"""Static bundle publisher (T020, `contracts/static-bundle.md`, FR-007).

Refuses to run when a required (input) artifact is `pending`/`fail`;
quarantined derived layers (buildings values, trees) are excluded from the
bundle and recorded as such in `dist/manifest.json`. Streams inputs, never
loads a full raster (OR-002). Writes the PublishedMap record (E-007).
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

import pyproj
from shapely.geometry import shape
from shapely.ops import transform

from . import artifact_manifest as manifest_mod
from . import workspace as ws

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SITE_DIR = REPO_ROOT / "src" / "site"
DIST_DIR = REPO_ROOT / "dist"
REQUIRED_INPUTS = [
    "boundary.geojson",
    "tables/buildings.geojson",
    "mosaic/extract/dop20rgb_*.tif",  # imagery aggregate
    "verification/stadtteile.geojson",  # feature 011 district input (repo file)
]
DERIVED_BUILDINGS = "buildings.geojson"  # workspace-relative, values-joined
DERIVED_TREES = "trees.pmtiles"
DERIVED_STADTTEILE = "stadtteile.geojson"  # dist-relative, publish-derived
STATIC_FILES = ("index.html", "style.css", "main.js", "style.json", "favicon.svg", "attribution.html", "impressum.html")

# Assets that get content-hashed filenames at publish time (feature 014,
# contracts/hashed-bundle.md). Value: (dist-relative hashed stem, suffix).
HASHED_ASSETS: dict[str, tuple[str, str]] = {
    "main.js": ("main", ".js"),
    "style.css": ("style", ".css"),
    "style.json": ("style", ".json"),
    "vendor/maplibre-gl.js": ("vendor/maplibre-gl", ".js"),
    "vendor/maplibre-gl.css": ("vendor/maplibre-gl", ".css"),
    "vendor/pmtiles.js": ("vendor/pmtiles", ".js"),
    "boundary.geojson": ("boundary", ".geojson"),
    "stadtteile.geojson": ("stadtteile", ".geojson"),
}


def _sha12(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def _rewrite_once(path: Path, old: str, new: str, what: str) -> None:
    """Replace a pattern that must occur exactly once (feature 014)."""
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise PublishError(f"publish refused: {path.name} {what} pattern {old!r} occurs {count} times")
    path.write_text(text.replace(old, new), encoding="utf-8")


def _hash_static_assets(dist_dir: Path) -> dict[str, str]:
    """Rename hashed assets and rewrite all references (feature 014).

    Deterministic: identical inputs produce identical hashed names.
    Returns a map of original dist-relative name -> hashed name.
    """
    hashed: dict[str, str] = {}
    for rel, (stem, suffix) in HASHED_ASSETS.items():
        src = dist_dir / rel
        if not src.exists():
            raise PublishError(f"publish refused: hashed asset missing: {src}")
        new_rel = f"{stem}-{_sha12(src)}{suffix}"
        src.rename(dist_dir / new_rel)
        hashed[rel] = new_rel

    # main.js: style URL + data fetches (contracts/hashed-bundle.md)
    main_js = dist_dir / hashed["main.js"]
    _rewrite_once(main_js, "const STYLE_URL = 'style.json'", f"const STYLE_URL = '{hashed['style.json']}'", "STYLE_URL")
    _rewrite_once(main_js, "fetch('stadtteile.geojson')", f"fetch('{hashed['stadtteile.geojson']}')", "stadtteile fetch")
    _rewrite_once(main_js, "fetch('boundary.geojson')", f"fetch('{hashed['boundary.geojson']}')", "boundary fetch")

    # style.json: source data URLs (JSON-safe rewrite)
    style_path = dist_dir / hashed["style.json"]
    style = json.loads(style_path.read_text(encoding="utf-8"))
    sources = style.get("sources", {})
    for source_key, rel in (("boundary", "boundary.geojson"), ("stadtteile", "stadtteile.geojson")):
        src_data = sources.get(source_key, {}).get("data")
        if src_data != rel:
            raise PublishError(f"publish refused: style.json {source_key} source data {src_data!r} != {rel!r}")
        sources[source_key]["data"] = hashed[rel]
    style_path.write_text(json.dumps(style, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # index.html: script srcs and stylesheet hrefs (contracts/hashed-bundle.md)
    index_path = dist_dir / "index.html"
    for rel, attr in (
        ("vendor/maplibre-gl.js", 'src="vendor/maplibre-gl.js"'),
        ("vendor/pmtiles.js", 'src="vendor/pmtiles.js"'),
        ("main.js", 'src="main.js"'),
    ):
        _rewrite_once(index_path, attr, attr.replace(rel, hashed[rel]), "index.html reference")

    # critical path (feature 014, FR-007 to FR-010): inline the two
    # stylesheets (no render-blocking stylesheet requests), preload the map
    # library, preconnect to the basemap origin, add the favicon link.
    html = index_path.read_text(encoding="utf-8")
    stylesheet_links = re.findall(r'<link rel="stylesheet"[^>]*>', html)
    if len(stylesheet_links) != 2:
        raise PublishError(f"publish refused: expected 2 stylesheet links in index.html, found {len(stylesheet_links)}")
    inline_css = "\n".join(f"/* {rel} */\n" + (dist_dir / hashed[rel]).read_text(encoding="utf-8") for rel in ("vendor/maplibre-gl.css", "style.css"))
    html = html.replace("<head>", (
        "<head>\n"
        f'  <link rel="preconnect" href="https://sgx.geodatenzentrum.de">\n'
        f'  <link rel="preload" href="{hashed["vendor/maplibre-gl.js"]}" as="script">\n'
        '  <link rel="icon" type="image/svg+xml" href="favicon.svg">\n'
        f"  <style>\n{inline_css}\n  </style>"
    ))
    for link in stylesheet_links:
        html = html.replace(link, "", 1)
    index_path.write_text(html, encoding="utf-8")

    # every rewritten reference must resolve
    for rel, new_rel in hashed.items():
        if not (dist_dir / new_rel).exists():
            raise PublishError(f"publish refused: hashed target missing after rewrite: {new_rel}")

    # drop stale hashed files from previous publishes (feature 014): they
    # would otherwise accumulate in dist/ and ship with the assets deploy.
    current = set(hashed.values())
    for path in dist_dir.rglob("*-[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].*"):
        rel = path.relative_to(dist_dir).as_posix()
        if rel not in current:
            path.unlink()
    return hashed


class PublishError(RuntimeError):
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code


def _boundary_wgs84(workspace: Path) -> dict[str, Any]:
    """Official boundary reprojected to EPSG:4326, as a world polygon with
    the city as a hole (FR-003: obscure everything outside Mannheim).

    Also returns the city's 4326 bbox so the initial camera can fit it.
    """
    data = json.loads((workspace / "boundary.geojson").read_text(encoding="utf-8"))
    features = data.get("features", [])
    if len(features) != 1:
        raise PublishError("boundary.geojson: expected exactly one feature")
    geom = shape(features[0]["geometry"])
    transformer = pyproj.Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)
    geom4326 = transform(transformer.transform, geom)
    bbox4326 = [float(v) for v in geom4326.bounds]

    def ring(coords: Any) -> list[list[float]]:
        return [[float(x), float(y)] for x, y in coords]

    if geom4326.geom_type == "Polygon":
        holes = [ring(geom4326.exterior.coords)]
    elif geom4326.geom_type == "MultiPolygon":
        holes = [ring(p.exterior.coords) for p in geom4326.geoms]
    else:
        raise PublishError(f"boundary geometry type {geom4326.geom_type} not supported")

    world_outer = [[-180.0, -85.06], [180.0, -85.06], [180.0, 85.06], [-180.0, 85.06], [-180.0, -85.06]]
    mask_polygon = {
        "type": "Feature",
        "properties": {"id": "mannheim-boundary-mask", "bbox4326": bbox4326},
        "geometry": {"type": "Polygon", "coordinates": [world_outer] + holes},
    }
    return {"feature": mask_polygon, "bbox4326": bbox4326}


def _derive_stadtteile(workspace: Path, out_path: Path) -> dict[str, Any]:
    """Official districts reprojected to EPSG:4326 with per-district
    statistics joined from the accepted building values (feature 011,
    R-3/R-5, `contracts/district-stats.md`, `contracts/city-overview.md`).

    Joins by building centroid containment (same method as the
    verification workflow), so the result is deterministic. Writes
    `dist/stadtteile.geojson` and returns the city stats derived from
    the same join plus the accepted tree polygon count.
    """
    from shapely.geometry import mapping, shape
    from shapely.strtree import STRtree

    data = json.loads((REPO_ROOT / "verification" / "stadtteile.geojson").read_text(encoding="utf-8"))
    features = data.get("features", [])
    if len(features) != 38:
        raise PublishError(f"verification/stadtteile.geojson: expected 38 features, got {len(features)}")
    transformer = pyproj.Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)

    districts: list[dict[str, Any]] = []
    for feature in features:
        props = feature.get("properties", {})
        districts.append(
            {
                "code": props.get("code"),
                "name": props.get("name"),
                "id_name": props.get("id_name"),
                "geometry": transform(transformer.transform, shape(feature["geometry"])),
                "n_buildings": 0,
                "value_sum": 0.0,
                "value_count": 0,
                "below_30": 0,
            }
        )

    buildings = json.loads((workspace / "buildings.geojson").read_text(encoding="utf-8"))
    centroids: list[tuple[Any, float | None, bool]] = []
    for feature in buildings.get("features", []):
        props = feature.get("properties", {})
        geom = shape(feature["geometry"])
        centroids.append((geom.centroid, props.get("value"), props.get("has_value") is True))
    tree = STRtree([c for c, _, _ in centroids])

    for district in districts:
        for i in tree.query(district["geometry"]):
            point, value, has_value = centroids[i]
            if not district["geometry"].contains(point):
                continue
            district["n_buildings"] += 1
            if has_value and value is not None:
                district["value_sum"] += value
                district["value_count"] += 1
                if value < 30:
                    district["below_30"] += 1

    total_buildings = 0
    total_value_sum = 0.0
    total_value_count = 0
    total_below_30 = 0
    out_features: list[dict[str, Any]] = []
    for district in districts:
        vc = district["value_count"]
        # standard half-up rounding at the 2nd decimal (district-stats.md)
        mean_value = round(district["value_sum"] / vc, 1) if vc else None
        share_lt30 = round(100.0 * district["below_30"] / vc, 1) if vc else 0.0
        props = {k: district[k] for k in ("code", "name", "id_name")}
        props.update({"n_buildings": district["n_buildings"], "mean_value": mean_value, "share_lt30": share_lt30})
        out_features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": mapping(district["geometry"]),
            }
        )
        total_buildings += district["n_buildings"]
        total_value_sum += district["value_sum"]
        total_value_count += vc
        total_below_30 += district["below_30"]

    collection = {
        "type": "FeatureCollection",
        "name": "mannheim-stadtteile",
        "features": out_features,
    }
    out_path.write_text(json.dumps(collection, ensure_ascii=False), encoding="utf-8")

    # city stats from the same join (city-overview.md); tree count is the
    # accepted trees_polygons.geojson feature count (R-5). pyogrio.read_info
    # is metadata-only, so the 871 MB file is never loaded (OR-002).
    mean_value_pct = round(total_value_sum / total_value_count, 1) if total_value_count else 0.0
    share_gte30_pct = round(100.0 * (total_value_count - total_below_30) / total_value_count, 1) if total_value_count else 0.0
    trees_path = workspace / "trees_polygons.geojson"
    if not trees_path.exists():
        raise PublishError(f"missing accepted input: {trees_path}")
    import pyogrio

    tree_count = pyogrio.read_info(str(trees_path))["features"]
    return {
        "mean_value_pct": mean_value_pct,
        "share_gte30_pct": share_gte30_pct,
        "tree_count": int(tree_count),
    }


def publish(workspace: Path | None = None, dist_dir: Path = DIST_DIR) -> dict[str, Any]:
    workspace = workspace or ws.workspace_root()
    manifest = manifest_mod.load_manifest()

    # workspace inputs gate on the manifest; repo-relative inputs
    # (verification/) gate on file presence (feature 011, T009)
    workspace_inputs = [p for p in REQUIRED_INPUTS if not p.startswith("verification/")]
    blocked = manifest_mod.required_ready(manifest, workspace_inputs)
    if blocked:
        raise PublishError(f"publish refused: required artifact not accepted: {blocked}")
    for repo_input in (p for p in REQUIRED_INPUTS if p.startswith("verification/")):
        if not (REPO_ROOT / repo_input).exists():
            raise PublishError(f"publish refused: missing input file: {REPO_ROOT / repo_input}")

    dist_dir.mkdir(parents=True, exist_ok=True)

    # static assets
    for name in STATIC_FILES:
        src = SITE_DIR / name
        if not src.exists():
            raise PublishError(f"missing static asset: {src}")
        shutil.copy(src, dist_dir / name)
    shutil.copytree(SITE_DIR / "vendor", dist_dir / "vendor", dirs_exist_ok=True)

    # boundary: world-with-hole polygon for the outside-mask (FR-003),
    # plus the city bbox the frontend uses for the initial camera (FR-002)
    boundary_out = _boundary_wgs84(workspace)
    boundary_collection = {
        "type": "FeatureCollection",
        "name": "mannheim-boundary-mask",
        "features": [boundary_out["feature"]],
    }
    (dist_dir / "boundary.geojson").write_text(json.dumps(boundary_collection), encoding="utf-8")

    # derived layers: include only accepted ones (FR-021/FR-023 quarantine)
    included: dict[str, str] = {}
    excluded: dict[str, str] = {}
    for derived_path, dist_name, extra in (
        (DERIVED_BUILDINGS, "buildings.geojson", "buildings.pmtiles"),
        (DERIVED_TREES, "trees.pmtiles", None),
    ):
        artifact = manifest_mod.get_artifact(manifest, derived_path)
        acceptance = artifact.get("acceptance") if artifact else "missing"
        if acceptance == "pass":
            src = workspace / derived_path
            if src.exists():
                shutil.copy(src, dist_dir / dist_name)
                included[derived_path] = dist_name
                if extra and (workspace / extra).exists():
                    shutil.copy(workspace / extra, dist_dir / extra)
            else:
                excluded[derived_path] = "pass but file missing"
        else:
            excluded[derived_path] = acceptance

    # stadtteile: 38 official districts reprojected to 4326 with the
    # publish-time statistics join (feature 011, R-3); city_stats from the
    # same join plus the accepted tree count (R-5)
    city_stats = _derive_stadtteile(workspace, dist_dir / DERIVED_STADTTEILE)
    # manifest gate: the derived-artifact entry is workspace-relative
    # (artifacts.manifest.json), so mirror the file for `make accept` to
    # hash and accept it (feature 011, FR-021)
    shutil.copy(dist_dir / DERIVED_STADTTEILE, workspace / DERIVED_STADTTEILE)

    # initial camera target (FR-002) + city overview stats (FR-008):
    # patch dist/style.json metadata
    style_path = dist_dir / "style.json"
    style = json.loads(style_path.read_text(encoding="utf-8"))
    style.setdefault("metadata", {})["mannheim_bbox"] = boundary_out["bbox4326"]
    style.setdefault("metadata", {})["city_stats"] = city_stats

    # quarantine: drop sources/layers whose data is not accepted, so the
    # published bundle only references published artifacts (FR-021/FR-023).
    # MapLibre's `load` event waits for every source; referencing a missing
    # pmtiles file would stall it (FR-020 handled at the source level here).
    available_sources = {"basemap", "boundary", "stadtteile"}
    if included.get(DERIVED_BUILDINGS):
        available_sources.add("buildings")
    if included.get(DERIVED_TREES):
        available_sources.add("trees")
    style["sources"] = {k: v for k, v in style["sources"].items() if k in available_sources}
    style["layers"] = [layer for layer in style["layers"] if layer.get("source") in available_sources]
    style_path.write_text(json.dumps(style, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # feature 014: content-hash static assets and rewrite references
    # (contracts/hashed-bundle.md). Runs after all files are final so the
    # hashes cover the patched style.json and derived geojsons.
    hashed_assets = _hash_static_assets(dist_dir)

    # public manifest (subset of artifacts.manifest.json)
    public = {
        "release_id": manifest.get("release_id"),
        "generated_at": manifest.get("generated_at"),
        "artifacts": [
            {k: a.get(k) for k in ("path", "size_bytes", "sha256", "source", "license", "acceptance")}
            for a in manifest.get("artifacts", [])
            if a.get("kind") != "large-file"
        ],
        "excluded_from_bundle": excluded,
        "hashed_assets": hashed_assets,
    }
    (dist_dir / "manifest.json").write_text(json.dumps(public, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # PublishedMap record (E-007)
    record = {
        "release_id": manifest.get("release_id", "2026.01"),
        "generated_at": public["generated_at"],
        "index_html": "index.html",
        "style": hashed_assets.get("style.json", "style.json"),
        "buildings": included.get(DERIVED_BUILDINGS),
        "trees": included.get(DERIVED_TREES),
        "boundary": hashed_assets.get("boundary.geojson", "boundary.geojson"),
        "boundary_bbox": boundary_out["bbox4326"],
        "stadtteile": hashed_assets.get("stadtteile.geojson", DERIVED_STADTTEILE),
        "hashed_assets": hashed_assets,
        "legend": {"labels": ["0", "15", "30", "50", "100"]},
        "controls": ["zoom-in", "zoom-out", "compass", "baeume-toggle"],
        "attribution": [
            "Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0",
            "basemap.de",
            "CityTreeCover (MIT)",
            "Stadt Mannheim, GDI-MA, dl-de/by-2-0 (Daten verändert)",
        ],
    }
    validation_dir = REPO_ROOT / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    (validation_dir / "published-map.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record
