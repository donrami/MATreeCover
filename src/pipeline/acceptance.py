"""FR-021 acceptance checks (`contracts/manifest.md`).

Five criteria per artifact: source, extent, resolution, completeness,
lineage. Deterministic and idempotent; metadata-only reads, never full
rasters (OR-002). `accept` is the only writer of manifest records.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shapely.geometry import shape

CRITERIA = ("source", "extent", "resolution", "completeness", "lineage")
COMPLETENESS_MIN = 0.95  # matches meta.json coverage_ratio_min
RESOLUTION_RASTER = "0.2 m"
RESOLUTION_NA = "n/a"

_boundary_cache: dict[str, Any] = {}


@dataclass(frozen=True)
class Check:
    criterion: str
    status: str  # "ok" | "fail"
    detail: str


def _boundary(workspace: Path) -> dict[str, Any]:
    key = str(workspace)
    if key not in _boundary_cache:
        data = json.loads((workspace / "boundary.geojson").read_text(encoding="utf-8"))
        features = data.get("features", [])
        if len(features) != 1:
            raise ValueError("boundary.geojson: expected exactly one feature")
        geom = shape(features[0]["geometry"])
        _boundary_cache[key] = {
            "geometry": geom,
            "bbox": [float(v) for v in geom.bounds],
            "buffered_bbox": [float(v) for v in geom.buffer(60.0).bounds],
        }
    return _boundary_cache[key]


def _extent_bbox(artifact: dict[str, Any]) -> list[float] | None:
    extent = artifact.get("extent")
    if isinstance(extent, dict) and extent.get("type") == "Polygon":
        # contract example stores a GeoJSON polygon; take its bbox
        try:
            g = shape(extent)
            return [float(v) for v in g.bounds]
        except Exception:
            return None
    if isinstance(extent, list) and len(extent) == 4:
        return [float(v) for v in extent]
    return None


def _intersects(a: list[float], b: list[float]) -> bool:
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def check_source(artifact: dict[str, Any], workspace: Path) -> Check:
    source = artifact.get("source")
    ok = bool(source) and bool(artifact.get("license"))
    return Check("source", "ok" if ok else "fail", f"source={source!r}")


def check_extent(artifact: dict[str, Any], workspace: Path) -> Check:
    boundary = _boundary(workspace)
    bbox = _extent_bbox(artifact)
    if bbox is None:
        return Check("extent", "fail", "no extent recorded")
    if artifact.get("kind") == "boundary":
        target = boundary["bbox"]
        within = all(
            abs(a - b) < 1.0 for a, b in zip(bbox, target)
        )
        return Check("extent", "ok" if within else "fail", "bbox matches boundary")
    ok = _intersects(bbox, boundary["buffered_bbox"])
    return Check("extent", "ok" if ok else "fail", "intersects buffered boundary")


def check_resolution(artifact: dict[str, Any], workspace: Path) -> Check:
    kind = artifact.get("kind", "")
    expected = RESOLUTION_RASTER if kind in ("imagery", "canopy-mask") else RESOLUTION_NA
    recorded = artifact.get("resolution")
    ok = recorded == expected
    return Check("resolution", "ok" if ok else "fail", f"{recorded!r} expected {expected!r}")


def check_completeness(artifact: dict[str, Any], workspace: Path) -> Check:
    value = artifact.get("completeness")
    if not isinstance(value, (int, float)) or value < 0 or value > 1:
        return Check("completeness", "fail", f"completeness={value!r} out of range")
    ok = value >= COMPLETENESS_MIN
    return Check(
        "completeness",
        "ok" if ok else "fail",
        f"{value:.4f} {'>=' if ok else '<'} {COMPLETENESS_MIN}",
    )


def check_lineage(artifact: dict[str, Any], workspace: Path) -> Check:
    lineage = artifact.get("lineage", {})
    inputs = lineage.get("inputs") if isinstance(lineage, dict) else None
    ok = isinstance(inputs, list) and len(inputs) > 0
    return Check("lineage", "ok" if ok else "fail", f"inputs={inputs!r}")


def run_checks(artifact: dict[str, Any], workspace: Path) -> list[Check]:
    return [
        check_source(artifact, workspace),
        check_extent(artifact, workspace),
        check_resolution(artifact, workspace),
        check_completeness(artifact, workspace),
        check_lineage(artifact, workspace),
    ]
