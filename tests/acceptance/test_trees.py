"""Trees acceptance (T037): in-boundary only (FR-007), source lineage
`accepted_canopy_mask` (E-004), stable ids `tree-<n>`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box, shape

from src.pipeline import trees

GSD = 0.2
MASK_PX = 200
# realistic UTM zone 32N eastings/northings (Mannheim area): reprojection
# 25832 -> 4326 is only valid inside the zone
ORIGIN_X = 460000.0
ORIGIN_Y = 5480000.0 + MASK_PX * GSD


def _make_mask(path: Path) -> None:
    mask = np.zeros((MASK_PX, MASK_PX), dtype=np.uint8)
    yy, xx = np.ogrid[:MASK_PX, :MASK_PX]
    mask[(xx - 100) ** 2 + (yy - 100) ** 2 <= 40**2] = 1
    with rasterio.open(
        path, "w", driver="GTiff", height=MASK_PX, width=MASK_PX, count=1,
        dtype="uint8", crs="EPSG:25832",
        transform=from_origin(ORIGIN_X, ORIGIN_Y, GSD, GSD),
    ) as dst:
        dst.write(mask, 1)


def _boundary_4326() -> object:
    import pyproj
    from shapely.ops import transform as shp_transform

    boundary = box(ORIGIN_X + 10, ORIGIN_Y - 40 + 10, ORIGIN_X + 45, ORIGIN_Y - 40 + 45)
    transformer = pyproj.Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)
    return shp_transform(transformer.transform, boundary)


def test_polygonize_in_boundary_only(tmp_path) -> None:
    mask_path = tmp_path / "mask.tif"
    _make_mask(mask_path)
    # boundary cuts the canopy blob (center ~(ORIGIN+20 m), radius 8 m)
    boundary = box(ORIGIN_X + 10, ORIGIN_Y - 40 + 10, ORIGIN_X + 45, ORIGIN_Y - 40 + 45)
    out = tmp_path / "trees.geojson"
    features = trees.polygonize_canopy(mask_path, out, boundary)
    assert len(features) > 0
    boundary4326 = _boundary_4326()
    for feature in features:
        geom = shape(feature["geometry"])
        assert boundary4326.covers(geom)  # FR-007: no halo leakage


def test_stable_ids_and_source(tmp_path) -> None:
    mask_path = tmp_path / "mask.tif"
    _make_mask(mask_path)
    boundary = box(ORIGIN_X, ORIGIN_Y - 40, ORIGIN_X + MASK_PX * GSD, ORIGIN_Y)
    out = tmp_path / "trees.geojson"
    features = trees.polygonize_canopy(mask_path, out, boundary)
    ids = [f["properties"]["id"] for f in features]
    assert ids == [f"tree-{i + 1}" for i in range(len(features))]  # E-004
    for feature in features:
        assert feature["properties"]["source"] == "accepted_canopy_mask"
        assert feature["properties"]["canopy_pixel_count"] > 0


def test_output_4326(tmp_path) -> None:
    import json

    mask_path = tmp_path / "mask.tif"
    _make_mask(mask_path)
    boundary = box(ORIGIN_X, ORIGIN_Y - 40, ORIGIN_X + MASK_PX * GSD, ORIGIN_Y)
    out = tmp_path / "trees.geojson"
    trees.polygonize_canopy(mask_path, out, boundary)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "EPSG:4326" in data["crs"]["properties"]["name"]
