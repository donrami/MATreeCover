"""Official Mannheim boundary (E-001) and the pipeline-only buffered
boundary (E-002 = boundary ∪ 60 m exterior, FR-006/FR-007).

The buffered boundary exists only inside the pipeline and is marked
`analysis-only`; publish never copies it to `dist/`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shapely.geometry import shape

CRS = "EPSG:25832"
HALO_M = 60.0


def _parse_geojson(path: Path) -> tuple[list[Any], str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    crs_name = data.get("crs", {}).get("properties", {}).get("name", "")
    if "25832" not in crs_name:
        raise ValueError(f"{path}: expected EPSG:25832, found crs {crs_name!r}")
    features = data.get("features", [])
    return features, crs_name


def load_boundary(path: Path | str) -> dict[str, Any]:
    """Load the official boundary (E-001). Returns geometry, bbox, area, crs.

    Accepts a single-feature FeatureCollection (one Polygon/MultiPolygon).
    """
    features, crs_name = _parse_geojson(Path(path))
    if len(features) != 1:
        raise ValueError(f"{path}: expected exactly one boundary feature, got {len(features)}")
    geom = shape(features[0]["geometry"])
    if geom.is_empty:
        raise ValueError(f"{path}: boundary geometry is empty")
    minx, miny, maxx, maxy = geom.bounds
    return {
        "geometry": geom,
        "bbox": [minx, miny, maxx, maxy],
        "area_m2": float(geom.area),
        "crs": CRS,
        "source": "LGL",
    }


def load_buffered(boundary_path: Path | str, buffer_m: float = HALO_M) -> dict[str, Any]:
    """E-002: boundary ∪ buffer_m exterior. `purpose: "analysis-only"` marks it
    so publish never emits it (FR-007).
    """
    boundary = load_boundary(boundary_path)
    return {
        "geometry": boundary["geometry"].buffer(buffer_m),
        "crs": CRS,
        "purpose": "analysis-only",
        "buffer_m": buffer_m,
    }
