"""SC-004 value recalculation (T023).

Sample 100 random buildings on a synthetic binary canopy mask, compute the
60 m-disc mean with the pipeline (`values.compute_building_values`,
fftconvolve-based) and independently with a direct per-pixel disc summation,
and assert they agree within one percentage point for every building.

The accepted canopy mask is quarantined (FR-021), so the test runs on a
controlled synthetic mask with full kernel coverage (interior buildings).
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from src.pipeline import values

GSD = 0.2
RADIUS_M = 2.0
RADIUS_PX = values.radius_px(RADIUS_M, GSD)
MASK_PX = 300  # 60 m x 60 m area
N_BUILDINGS = 100
BUILDING_PX = 5


def _make_mask(path: Path, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    mask = np.zeros((MASK_PX, MASK_PX), dtype=np.uint8)
    # three canopy blobs with tree-ish shapes
    for cx, cy, r in ((70, 70, 25), (180, 90, 30), (230, 210, 22)):
        yy, xx = np.ogrid[:MASK_PX, :MASK_PX]
        blob = (xx - cx) ** 2 + (yy - cy) ** 2 <= r**2
        mask[blob] = 1
    # sprinkle noise canopy so values are not trivially 0/100
    noise = rng.random((MASK_PX, MASK_PX)) < 0.03
    mask[noise] = 1
    transform = from_origin(0.0, MASK_PX * GSD, GSD, GSD)
    with rasterio.open(
        path, "w", driver="GTiff", height=MASK_PX, width=MASK_PX, count=1,
        dtype="uint8", crs="EPSG:25832", transform=transform,
    ) as dst:
        dst.write(mask, 1)
    return mask


def _make_buildings(seed: int = 11) -> list[dict]:
    """100 axis-aligned 5 px squares, each at least `RADIUS_PX` px from the
    mask edge so its whole disc is inside the data (coverage == 1.0)."""
    rng = random.Random(seed)
    margin = RADIUS_PX + 2
    buildings = []
    ids = set()
    while len(buildings) < N_BUILDINGS:
        x0 = rng.randint(margin, MASK_PX - margin - BUILDING_PX)
        y0 = rng.randint(margin, MASK_PX - margin - BUILDING_PX)
        x0 = x0 - (x0 % 2)  # align to even pixels for exact rasterization
        y0 = y0 - (y0 % 2)
        bid = f"b-{x0}-{y0}"
        if bid in ids:
            continue
        ids.add(bid)
        geom = box(x0 * GSD, y0 * GSD, (x0 + BUILDING_PX) * GSD, (y0 + BUILDING_PX) * GSD)
        buildings.append({"id": bid, "geometry": geom})
    return buildings


def _independent_value(mask: np.ndarray, building: dict, radius_px: int) -> float:
    """Direct per-pixel disc summation (no FFT) — the independent method.

    Raster convention is north-up: row 0 is the top (y = MASK_PX * GSD).
    """
    minx, miny, maxx, maxy = building["geometry"].bounds
    x0 = int(round(minx / GSD))
    x1 = int(round(maxx / GSD))
    row_top = MASK_PX - int(round(maxy / GSD))
    row_bot = MASK_PX - int(round(miny / GSD))
    offs = [
        (dx, dy)
        for dy in range(-radius_px, radius_px + 1)
        for dx in range(-radius_px, radius_px + 1)
        if dx * dx + dy * dy <= radius_px * radius_px
    ]
    disc_size = len(offs)
    pixel_values = []
    for row in range(row_top, row_bot):
        for col in range(x0, x1):
            s = 0
            for dx, dy in offs:
                s += int(mask[row + dy, col + dx])  # int(): avoid uint8 wrap
            pixel_values.append(s / disc_size)
    return float(np.mean(pixel_values)) * 100.0


def test_values_recalculation_within_one_point(tmp_path: Path) -> None:
    mask_path = tmp_path / "mask.tif"
    mask = _make_mask(mask_path)
    buildings = _make_buildings()

    out_path = tmp_path / "buildings.geojson"
    boundary = box(-100, -100, MASK_PX * GSD + 100, MASK_PX * GSD + 100)  # no clip
    features = values.compute_building_values(
        mask_path, buildings, out_path, boundary,
        radius_m=RADIUS_M, gsd_m=GSD,
    )

    assert len(features) == N_BUILDINGS
    for feature, building in zip(features, buildings):
        pipeline_value = feature["properties"]["value"]
        assert pipeline_value is not None
        independent = _independent_value(mask, building, RADIUS_PX)
        assert (
            abs(pipeline_value - independent) <= 1.0
        ), f"{building['id']}: pipeline {pipeline_value:.2f} vs independent {independent:.2f}"
        assert 0.0 <= pipeline_value <= 100.0
        assert feature["properties"]["value_str"] == f"{pipeline_value:.2f}"
        assert feature["properties"]["has_value"] is True


def test_edge_building_is_null_when_disc_incomplete(tmp_path: Path) -> None:
    """FR-009: a building whose 60 m disc extends beyond the mask gets an
    unavailable value (null), never a false zero."""
    mask_path = tmp_path / "mask.tif"
    mask = _make_mask(mask_path)
    # building flush against the mask corner: disc mostly outside the data
    edge_building = {"id": "b-edge", "geometry": box(0, 0, BUILDING_PX * GSD, BUILDING_PX * GSD)}
    out_path = tmp_path / "buildings_edge.geojson"
    boundary = box(-100, -100, MASK_PX * GSD + 100, MASK_PX * GSD + 100)
    features = values.compute_building_values(
        mask_path, [edge_building], out_path, boundary,
        radius_m=RADIUS_M, gsd_m=GSD,
    )
    assert len(features) == 1
    props = features[0]["properties"]
    assert props["value"] is None
    assert props["has_value"] is False
    assert props["value_str"] == "\u2013"
    assert props["completeness"] < 0.95


def test_treeless_building_gets_zero_not_null(tmp_path: Path) -> None:
    """A building in a treeless area gets value 0.0, never None from
    fftconvolve float residue (R-006). Regression for the pre-existing
    noise-sign bug found during 009 calibration."""
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    mask_path = tmp_path / "mask_bare.tif"
    mask = np.zeros((MASK_PX, MASK_PX), dtype=np.uint8)  # no trees at all
    transform = from_origin(0.0, MASK_PX * GSD, GSD, GSD)
    with rasterio.open(
        mask_path, "w", driver="GTiff", height=MASK_PX, width=MASK_PX, count=1,
        dtype="uint8", crs="EPSG:25832", transform=transform,
    ) as dst:
        dst.write(mask, 1)
    # interior building, disc fully inside the mask
    building = {"id": "b-bare", "geometry": box(250 * GSD, 250 * GSD, 260 * GSD, 260 * GSD)}
    out_path = tmp_path / "buildings_bare.geojson"
    boundary = box(-100, -100, MASK_PX * GSD + 100, MASK_PX * GSD + 100)
    features = values.compute_building_values(
        mask_path, [building], out_path, boundary,
        radius_m=RADIUS_M, gsd_m=GSD,
    )
    props = features[0]["properties"]
    assert props["has_value"] is True
    assert props["value"] == 0.0
    assert props["completeness"] >= 0.95
