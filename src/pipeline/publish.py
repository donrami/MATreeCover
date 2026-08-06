"""Static bundle publisher (T020, `contracts/static-bundle.md`, FR-007).

Refuses to run when a required (input) artifact is `pending`/`fail`;
quarantined derived layers (buildings values, trees) are excluded from the
bundle and recorded as such in `dist/manifest.json`. Streams inputs, never
loads a full raster (OR-002). Writes the PublishedMap record (E-007).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pyproj
from shapely.geometry import shape
from shapely.ops import transform

from . import artifact_manifest as manifest_mod
from . import io, workspace as ws

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
STATIC_FILES = ("index.html", "style.css", "main.js", "style.json", "attribution.html", "impressum.html")


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
    }
    (dist_dir / "manifest.json").write_text(json.dumps(public, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # PublishedMap record (E-007)
    record = {
        "release_id": manifest.get("release_id", "2026.01"),
        "generated_at": public["generated_at"],
        "index_html": "index.html",
        "style": "style.json",
        "buildings": included.get(DERIVED_BUILDINGS),
        "trees": included.get(DERIVED_TREES),
        "boundary": "boundary.geojson",
        "boundary_bbox": boundary_out["bbox4326"],
        "stadtteile": DERIVED_STADTTEILE,
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
