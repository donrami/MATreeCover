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
]
DERIVED_BUILDINGS = "buildings.geojson"  # workspace-relative, values-joined
DERIVED_TREES = "trees.pmtiles"
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


def publish(workspace: Path | None = None, dist_dir: Path = DIST_DIR) -> dict[str, Any]:
    workspace = workspace or ws.workspace_root()
    manifest = manifest_mod.load_manifest()

    blocked = manifest_mod.required_ready(manifest, REQUIRED_INPUTS)
    if blocked:
        raise PublishError(f"publish refused: required artifact not accepted: {blocked}")

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

    # initial camera target (FR-002): patch dist/style.json metadata
    style_path = dist_dir / "style.json"
    style = json.loads(style_path.read_text(encoding="utf-8"))
    style.setdefault("metadata", {})["mannheim_bbox"] = boundary_out["bbox4326"]

    # quarantine: drop sources/layers whose data is not accepted, so the
    # published bundle only references published artifacts (FR-021/FR-023).
    # MapLibre's `load` event waits for every source; referencing a missing
    # pmtiles file would stall it (FR-020 handled at the source level here).
    available_sources = {"basemap", "boundary"}
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
        "legend": {"labels": ["0", "15", "30", "50", "100"]},
        "controls": ["zoom-in", "zoom-out", "compass", "baeume-toggle"],
        "attribution": [
            "Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0",
            "basemap.de",
            "CityTreeCover (MIT)",
        ],
    }
    validation_dir = REPO_ROOT / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    (validation_dir / "published-map.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record
