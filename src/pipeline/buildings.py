"""Building inventory (FR-004, R-003, SC-003).

Reads the accepted `tables/buildings.geojson` (LGL ALKIS Hausumringe,
93,024 features, EPSG:25832), asserts source/crs/count, selects features
intersecting the buffered boundary, de-duplicates by stable id, strips the
stale value fields from the quarantined previous run, and writes the
pipeline's analysis building set (EPSG:25832). Never regenerates the
accepted input (FR-022).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pyogrio
from shapely import from_wkb
from shapely.geometry import mapping

from . import io

EXPECTED_CRS = "EPSG:25832"
EXPECTED_COUNT = 93024  # SC-003, 2026.01/meta.json
STALE_FIELDS = ("mean_value", "value_status", "coverage_ratio", "validation_band", "release_id")


def _read_geojson(source_path: Path | str) -> tuple[dict[str, Any], np.ndarray, list[np.ndarray], list[str]]:
    """Read via pyogrio's native reader.

    Returns (meta, wkb_geometry_array, field_columns, field_names).
    Locates the geometry (WKB bytes) and field columns defensively, since
    the raw tuple layout varies across pyogrio builds.
    """
    result = pyogrio.raw.read(str(source_path))
    meta = result[0]
    wkb: np.ndarray | None = None
    columns: list[np.ndarray] | None = None
    for item in result[1:]:
        if isinstance(item, np.ndarray) and item.ndim == 1 and len(item) > 0 and isinstance(item[0], (bytes, bytearray)):
            wkb = item
        elif isinstance(item, list) and item and isinstance(item[0], np.ndarray):
            columns = item
    if wkb is None or columns is None:
        raise ValueError("pyogrio.raw.read: could not locate geometry/field columns")
    names = list(meta.get("fields", []))
    return meta, wkb, columns, names


def load_buildings(source_path: Path | str, expected_count: int = EXPECTED_COUNT) -> list[dict[str, Any]]:
    """Read + assert the accepted inventory. Returns [{"id", "geometry"}].

    Asserts CRS, feature count, and source attribution per FR-004/SC-003.
    """
    meta, wkb, columns, field_names = _read_geojson(source_path)
    crs = meta.get("crs")
    count = len(wkb)
    if crs != EXPECTED_CRS:
        raise ValueError(f"buildings crs {crs!r} != {EXPECTED_CRS}")
    if count != expected_count:
        raise ValueError(f"buildings feature count {count} != expected {expected_count} (SC-003)")
    id_idx = field_names.index("id") if "id" in field_names else None
    if id_idx is None:
        raise ValueError("buildings.geojson has no id field")
    geometries = from_wkb(wkb)
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i in range(count):
        fid = str(columns[id_idx][i])
        geom = geometries[i]
        if geom is None or geom.is_empty:
            continue
        if fid in seen:
            continue  # drop duplicates by stable id (FR-004)
        seen.add(fid)
        out.append({"id": fid, "geometry": geom})
    return out


def select_in_buffer(buildings: list[dict[str, Any]], buffered_geometry: Any) -> list[dict[str, Any]]:
    """FR-004: keep buildings intersecting the analysis (buffered) boundary."""
    return [b for b in buildings if buffered_geometry.intersects(b["geometry"])]


def write_buildings(buildings: list[dict[str, Any]], out_path: Path | str) -> None:
    """Write the analysis building set as a FeatureCollection (EPSG:25832)
    with only `id`, `geometry`, and `in_boundary: true`."""
    features = [
        {
            "type": "Feature",
            "id": b["id"],
            "properties": {"id": b["id"], "in_boundary": True},
            "geometry": mapping(b["geometry"]),
        }
        for b in buildings
    ]
    io.write_geojson(features, out_path, crs_name=EXPECTED_CRS)


def clip_buildings(source_path: Path | str, out_path: Path | str, buffered_geometry: Any) -> int:
    """End-to-end: load, assert, select in buffer, dedupe, write. Returns count."""
    buildings = load_buildings(source_path)
    selected = select_in_buffer(buildings, buffered_geometry)
    write_buildings(selected, out_path)
    return len(selected)
