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


def _make_chunked_mask(path: Path, chunk_px: int = 400) -> np.ndarray:
    """A mask spanning many chunks: blobs crossing seams, one interior
    blob, and a diagonal corner-touching pair split across a seam."""
    size = 3 * chunk_px
    mask = np.zeros((size, size), dtype=np.uint8)
    yy, xx = np.ogrid[:size, :size]
    # blob crossing the chunk-corner at (chunk_px, chunk_px)
    mask[(xx - chunk_px) ** 2 + (yy - chunk_px) ** 2 <= (chunk_px // 2) ** 2] = 1
    # blob crossing the vertical and horizontal seams
    mask[(xx - 2 * chunk_px) ** 2 + (yy - 2 * chunk_px) ** 2 <= (3 * chunk_px // 4) ** 2] = 1
    # blob entirely inside one chunk
    mask[(xx - size + chunk_px // 2) ** 2 + (yy - chunk_px // 2) ** 2 <= (chunk_px // 4) ** 2] = 1
    # diagonal pair (4-connectivity: two components) straddling a seam
    mask[chunk_px - 1, chunk_px + 1] = 1
    mask[chunk_px, chunk_px + 2] = 1
    with rasterio.open(
        path, "w", driver="GTiff", height=size, width=size, count=1,
        dtype="uint8", crs="EPSG:25832",
        transform=from_origin(ORIGIN_X, ORIGIN_Y, GSD, GSD),
    ) as dst:
        dst.write(mask, 1)
    return mask


def test_chunked_matches_full_read_components(tmp_path) -> None:
    """OR-002: chunked polygonization must reproduce the full-read result
    — one feature per 4-connected canopy component (independent reference:
    scipy.ndimage.label), exact pixel totals, no seam splits or corner
    merges."""
    from scipy import ndimage

    chunk_px = 400
    mask_path = tmp_path / "chunked_mask.tif"
    mask = _make_chunked_mask(mask_path, chunk_px)
    structure = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=int)  # 4-connectivity
    _, ncomp = ndimage.label(mask > 0, structure=structure)

    size = mask.shape[0]
    boundary = box(ORIGIN_X, ORIGIN_Y - size * GSD, ORIGIN_X + size * GSD, ORIGIN_Y)
    out = tmp_path / "trees_chunked.geojson"
    features = trees.polygonize_canopy(mask_path, out, boundary, chunk_px=chunk_px)

    assert len(features) == ncomp
    total_pixels = int((mask > 0).sum())
    assert sum(f["properties"]["canopy_pixel_count"] for f in features) == total_pixels
    ids = [f["properties"]["id"] for f in features]
    assert ids == [f"tree-{i + 1}" for i in range(len(features))]  # E-004


def test_chunked_deterministic(tmp_path) -> None:
    """Same input, same window order, same GEOS ops: byte-identical
    output on a re-run (reproducible derived artifact)."""
    chunk_px = 400
    mask_path = tmp_path / "chunked_mask.tif"
    _make_chunked_mask(mask_path, chunk_px)
    size = 3 * chunk_px
    boundary = box(ORIGIN_X, ORIGIN_Y - size * GSD, ORIGIN_X + size * GSD, ORIGIN_Y)
    out1 = tmp_path / "trees_1.geojson"
    out2 = tmp_path / "trees_2.geojson"
    features1 = trees.polygonize_canopy(mask_path, out1, boundary, chunk_px=chunk_px)
    features2 = trees.polygonize_canopy(mask_path, out2, boundary, chunk_px=chunk_px)
    assert features1 == features2
    assert out1.read_bytes() == out2.read_bytes()
