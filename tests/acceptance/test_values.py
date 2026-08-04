"""Values output contract (T036): FR-008/FR-009.

`value` in [0,100] or null; `value_str` with two decimals; `has_value`
consistent; unavailable buildings never look like zero.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from src.pipeline import values

GSD = 0.2
RADIUS_M = 2.0
MASK_PX = 200


def _make_mask(path: Path) -> None:
    rng = np.random.default_rng(3)
    mask = np.zeros((MASK_PX, MASK_PX), dtype=np.uint8)
    yy, xx = np.ogrid[:MASK_PX, :MASK_PX]
    mask[(xx - 60) ** 2 + (yy - 60) ** 2 <= 25**2] = 1
    mask[rng.random((MASK_PX, MASK_PX)) < 0.05] = 1
    with rasterio.open(
        path, "w", driver="GTiff", height=MASK_PX, width=MASK_PX, count=1,
        dtype="uint8", crs="EPSG:25832", transform=from_origin(0.0, MASK_PX * GSD, GSD, GSD),
    ) as dst:
        dst.write(mask, 1)


def _compute(tmp_path: Path):
    mask_path = tmp_path / "mask.tif"
    _make_mask(mask_path)
    radius_px = values.radius_px(RADIUS_M, GSD)
    margin = radius_px + 2
    buildings = [
        {"id": f"b-{i}", "geometry": box((10 + 3 * i) * GSD, (10 + 3 * i) * GSD, (15 + 3 * i) * GSD, (15 + 3 * i) * GSD)}
        for i in range(20)
    ]
    buildings.append({"id": "b-edge", "geometry": box(0, 0, 5 * GSD, 5 * GSD)})  # incomplete disc
    out_path = tmp_path / "buildings.geojson"
    boundary = box(-100, -100, MASK_PX * GSD + 100, MASK_PX * GSD + 100)
    features = values.compute_building_values(
        mask_path, buildings, out_path, boundary, radius_m=RADIUS_M, gsd_m=GSD
    )
    return features


def test_value_range(tmp_path) -> None:
    for feature in _compute(tmp_path):
        value = feature["properties"]["value"]
        if value is not None:
            assert 0.0 <= value <= 100.0  # FR-008


def test_value_str_two_decimals(tmp_path) -> None:
    for feature in _compute(tmp_path):
        props = feature["properties"]
        if props["value"] is not None:
            assert props["value_str"] == f"{props['value']:.2f}"  # FR-008


def test_has_value_consistency(tmp_path) -> None:
    for feature in _compute(tmp_path):
        props = feature["properties"]
        assert props["has_value"] == (props["value"] is not None)  # FR-009


def test_unavailable_never_zero(tmp_path) -> None:
    features = _compute(tmp_path)
    edge = next(f for f in features if f["id"] == "b-edge")
    props = edge["properties"]
    assert props["value"] is None
    assert props["value_str"] == "\u2013"  # en dash, not "0.00"


def test_output_is_4326(tmp_path) -> None:
    import json

    out = tmp_path / "buildings.geojson"
    _make_mask(tmp_path / "mask.tif")
    data = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
    # recompute to also produce the output file
    radius_px = values.radius_px(RADIUS_M, GSD)
    buildings = [
        {"id": "b-1", "geometry": box(10 * GSD, 10 * GSD, 15 * GSD, 15 * GSD)}
    ]
    boundary = box(-100, -100, MASK_PX * GSD + 100, MASK_PX * GSD + 100)
    values.compute_building_values(
        tmp_path / "mask.tif", buildings, out, boundary, radius_m=RADIUS_M, gsd_m=GSD
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "EPSG:4326" in data["crs"]["properties"]["name"]


def test_chunk_edge_buildings_not_nulled(tmp_path) -> None:
    """R-006: buildings on a 1000-px chunk border keep full coverage.

    Regression: coverage was measured against the chunk window edge, so
    every building within one radius of a chunk boundary was nulled
    (60%+ of the city). Buildings are attributed to the chunk holding
    their centroid and coverage is measured against the data extent.
    """
    mask_path = tmp_path / "mask.tif"
    px = 300
    rng = np.random.default_rng(5)
    mask = np.zeros((px, px), dtype=np.uint8)
    yy, xx = np.ogrid[:px, :px]
    mask[(xx - 150) ** 2 + (yy - 150) ** 2 <= 120**2] = 1
    mask[rng.random((px, px)) < 0.1] = 1
    with rasterio.open(
        mask_path, "w", driver="GTiff", height=px, width=px, count=1,
        dtype="uint8", crs="EPSG:25832",
        transform=from_origin(0.0, px * GSD, GSD, GSD),
    ) as dst:
        dst.write(mask, 1)
    # buildings straddling the chunk grid lines at 100 px and 200 px
    # (centroids strictly inside their chunks: 101, 201, 150)
    buildings = [
        {"id": "b-edge1", "geometry": box(98 * GSD, 98 * GSD, 104 * GSD, 104 * GSD)},
        {"id": "b-edge2", "geometry": box(198 * GSD, 198 * GSD, 204 * GSD, 204 * GSD)},
        {"id": "b-mid", "geometry": box(147 * GSD, 147 * GSD, 153 * GSD, 153 * GSD)},
    ]
    out = tmp_path / "buildings.geojson"
    boundary = box(-10 * GSD, -10 * GSD, (px + 10) * GSD, (px + 10) * GSD)
    features = values.compute_building_values(
        mask_path, buildings, out, boundary, radius_m=RADIUS_M, gsd_m=GSD, chunk_px=100
    )
    assert len(features) == 3
    for f in features:
        assert f["properties"]["has_value"] is True, f["id"]  # FR-008/FR-009
        assert f["properties"]["value"] is not None
