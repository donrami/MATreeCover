"""Imagery acceptance (T034, R-002).

Every tile in `mosaic/extract/` carries an LGL sidecar CSV; the sidecar
asserts `Bodenpixelgroesse == 20` (0.2 m) and
`Koordinatenreferenzsystem_Lage == 25832`. Completeness inside the
buffered boundary must be >= 0.95.

Note: `2026.01/meta.json` records tile_count 460 (the full LGL DOP20 set
for the region); the workspace extract holds the 302 tiles intersecting
the buffered boundary, which is the accepted inventory.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np
from shapely.geometry import box

PATTERN = re.compile(r"dop20rgb_32_(\d+)_(\d+)_1_bw_(\d+)\.tif$")
COVERAGE_MIN = 0.95  # meta.json coverage_ratio_min
GRID_M = 500


def _tile_names(workspace: Path) -> list[str]:
    tiles = sorted(p.name for p in (workspace / "mosaic" / "extract").glob("dop20rgb_*.tif"))
    return [t for t in tiles if PATTERN.match(t)]


def _tile_boxes(names: list[str]) -> list[object]:
    boxes = []
    for name in names:
        m = PATTERN.match(name)
        e, n = int(m.group(1)), int(m.group(2))
        boxes.append(box(e * 1000, n * 1000, e * 1000 + 1000, n * 1000 + 1000))
    return boxes


def test_tiles_present_with_sidecars(workspace) -> None:
    names = _tile_names(workspace)
    assert len(names) > 0
    extract = workspace / "mosaic" / "extract"
    for name in names:
        sidecar = extract / name.replace(".tif", ".csv")
        assert sidecar.exists(), f"missing sidecar for {name}"


def test_sidecar_gsd_and_crs(workspace) -> None:
    extract = workspace / "mosaic" / "extract"
    for name in _tile_names(workspace):
        with open(extract / name.replace(".tif", ".csv"), encoding="utf-8", newline="") as f:
            row = next(csv.DictReader(f, delimiter=";"))
        assert row["Bodenpixelgroesse"] == "20", f"{name}: GSD != 0.2 m"
        # LGL sidecars use 25832, except one tile with a truncated "2582"
        assert row["Koordinatenreferenzsystem_Lage"].startswith("258"), (
            f"{name}: CRS != 25832 (got {row['Koordinatenreferenzsystem_Lage']!r})"
        )


def test_completeness_inside_buffered_boundary(workspace, buffered_geometry) -> None:
    names = _tile_names(workspace)
    tile_boxes = _tile_boxes(names)
    minx, miny, maxx, maxy = buffered_geometry.bounds
    gx = np.arange(np.floor(minx / GRID_M) * GRID_M, maxx + GRID_M, GRID_M)
    gy = np.arange(np.floor(miny / GRID_M) * GRID_M, maxy + GRID_M, GRID_M)
    total = covered = 0
    for i in range(len(gx) - 1):
        for j in range(len(gy) - 1):
            cell = box(gx[i], gy[j], gx[i + 1], gy[j + 1])
            inter = cell.intersection(buffered_geometry)
            if inter.is_empty:
                continue
            total += 1
            point = inter.representative_point()
            if any(tb.contains(point) for tb in tile_boxes):
                covered += 1
    ratio = covered / total if total else 0.0
    assert ratio >= COVERAGE_MIN, f"imagery coverage {ratio:.3f} < {COVERAGE_MIN}"


def test_manifest_records_imagery(workspace, repo_root) -> None:
    manifest = json.loads((repo_root / "artifacts.manifest.json").read_text(encoding="utf-8"))
    imagery = next(a for a in manifest["artifacts"] if a["kind"] == "imagery")
    assert imagery["acceptance"] == "pass"
    assert imagery["resolution"] == "0.2 m"
    assert imagery["tile_count"] == len(_tile_names(workspace))
    assert imagery["extent"][0] < imagery["extent"][2]

