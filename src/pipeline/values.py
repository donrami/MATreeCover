"""Per-building 60 m tree-cover values (FR-005, R-001/R-006).

The value of a building is the mean canopy fraction inside a circular
60 m radius, evaluated at every pixel of the footprint, then the mean of
those pixel values. Implementation: `scipy.signal.fftconvolve` with a
300 px circular kernel over the binary canopy mask, chunked 1000 px
tiles with reflective padding (matches `2026.01/meta.json`
`neighbourhood`). Never loads a full city raster (OR-002).

Output: `buildings.geojson` in EPSG:4326, clipped to the official
boundary, with `value`, `value_str`, `has_value`, `completeness`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pyproj
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window
from scipy.signal import fftconvolve
from shapely.geometry import box, mapping
from shapely.ops import transform
from shapely.strtree import STRtree

from . import io

RADIUS_M = 60.0
GSD_M = 0.2  # ground sampling distance, 2026.01/meta.json
COMPLETENESS_MIN = 0.95
CHUNK_PX = 1000
OUT_CRS = "EPSG:4326"
UNAVAILABLE = "\u2013"  # en dash, FR-009


def radius_px(radius_m: float = RADIUS_M, gsd_m: float = GSD_M) -> int:
    return round(radius_m / gsd_m)


def circular_kernel(radius: int) -> np.ndarray:
    yy, xx = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    return (xx * xx + yy * yy <= radius * radius).astype(np.float64)


def _local_fraction_chunk(chunk: np.ndarray, kernel: np.ndarray, radius: int) -> np.ndarray:
    """Local canopy fraction for one chunk (R-006).

    Reflect-pads the chunk so the convolution at interior pixels is
    exact; the halo is real imagery, so the chunk border is not treated
    as the world edge.
    """
    pad = radius
    mode = "reflect" if min(chunk.shape) > pad else "edge"
    ksum = kernel.sum()
    padded = np.pad(chunk, pad, mode=mode)
    return fftconvolve(padded, kernel, mode="valid") / ksum


_tile_boxes_cache: dict[str, list[Any] | None] = {}


def _tile_boxes(extract_dir: Path) -> list[Any] | None:
    """Footprint boxes of the accepted imagery tiles (data extent).

    Coverage is measured against these footprints, never against chunk
    window edges (R-006: the chunk halo is real data). Returns None when
    no extract directory exists — callers then treat all pixels as valid
    (tests use synthetic masks).
    """
    key = str(extract_dir)
    if key in _tile_boxes_cache:
        return _tile_boxes_cache[key]
    boxes: list[Any] = []
    if extract_dir.is_dir():
        for t in sorted(extract_dir.glob("dop20rgb_*.tif")):
            try:
                with rasterio.open(t) as s:
                    tr = s.transform
                    boxes.append(box(tr.c, tr.f + tr.e * s.height, tr.c + tr.a * s.width, tr.f))
            except Exception:
                continue
    _tile_boxes_cache[key] = boxes or None
    return _tile_boxes_cache[key]


def _coverage_chunk(
    tile_boxes: list[Any] | None,
    kernel: np.ndarray,
    radius: int,
    chunk_px: int,
    row: int,
    col: int,
    canvas_transform: Any,
    canvas_shape: tuple[int, int],
    window_shape: tuple[int, int],
    window_offset: tuple[int, int],
) -> np.ndarray:
    """Fraction of each pixel's 60 m disc inside the imagery data extent.

    Returns an array of ``window_shape`` aligned with the mask read
    window (which is clamped at the canvas border). Validity is
    rasterized over the window plus one extra radius of truth, so a
    pixel's disc is evaluated against the real data extent; zero beyond
    the canvas means no data (FR-009: incomplete discs null the
    building).
    """
    if tile_boxes is None:
        # no extract directory (synthetic tests): the data extent is the
        # mask canvas itself, so buildings whose disc crosses the canvas
        # edge get incomplete coverage (FR-009)
        full = chunk_px + 4 * radius
        valid_full = np.zeros((full, full), dtype=np.float64)
        er0, ec0 = row - 2 * radius, col - 2 * radius
        vr0, vr1 = max(0, er0), min(canvas_shape[0], er0 + full)
        vc0, vc1 = max(0, ec0), min(canvas_shape[1], ec0 + full)
        if vr0 < vr1 and vc0 < vc1:
            valid_full[vr0 - er0 : vr1 - er0, vc0 - ec0 : vc1 - ec0] = 1.0
        cov = fftconvolve(valid_full, kernel, mode="valid") / kernel.sum()
        dr, dc = window_offset
        return cov[dr : dr + window_shape[0], dc : dc + window_shape[1]]
    full = chunk_px + 4 * radius
    valid_full = np.zeros((full, full), dtype=np.float64)
    er0, ec0 = row - 2 * radius, col - 2 * radius
    vr0, vr1 = max(0, er0), min(canvas_shape[0], er0 + full)
    vc0, vc1 = max(0, ec0), min(canvas_shape[1], ec0 + full)
    if vr0 < vr1 and vc0 < vc1:
        sub_shape = (vr1 - vr0, vc1 - vc0)
        sub_transform = canvas_transform * rasterio.Affine.translation(vc0, vr0)
        sub_bounds = rasterio.transform.array_bounds(*sub_shape, sub_transform)
        sub_box = box(*sub_bounds)
        boxes = [tb for tb in tile_boxes if tb.intersects(sub_box)]
        if boxes:
            valid_full[vr0 - er0 : vr1 - er0, vc0 - ec0 : vc1 - ec0] = rasterize(
                [(tb, 1) for tb in boxes],
                out_shape=sub_shape,
                transform=sub_transform,
                fill=0,
                dtype=np.uint8,
                all_touched=True,
            )
    cov = fftconvolve(valid_full, kernel, mode="valid") / kernel.sum()
    dr, dc = window_offset
    return cov[dr : dr + window_shape[0], dc : dc + window_shape[1]]


def compute_building_values(
    mask_path: Path | str,
    buildings: Iterable[dict[str, Any]],
    out_path: Path | str,
    boundary_geometry: Any,
    radius_m: float = RADIUS_M,
    gsd_m: float = GSD_M,
    chunk_px: int = CHUNK_PX,
) -> list[dict[str, Any]]:
    """Compute per-building values from a binary canopy mask.

    `buildings`: iterable of {"id": str, "geometry": shapely (EPSG:25832)}.
    Writes a FeatureCollection in EPSG:4326 clipped to `boundary_geometry`
    (official boundary, FR-007). Returns the output feature list.
    """
    radius = radius_px(radius_m, gsd_m)
    kernel = circular_kernel(radius)

    buildings = list(buildings)
    tree = STRtree([b["geometry"] for b in buildings])
    centroids = [b["geometry"].centroid for b in buildings]

    # accumulate per building: [sum_frac, count_px, sum_coverage]
    acc: dict[int, list[float]] = {i: [0.0, 0.0, 0.0] for i in range(len(buildings))}

    with rasterio.open(str(mask_path)) as src:
        crs = src.crs.to_string() if src.crs else None
        if crs != "EPSG:25832":
            raise ValueError(f"mask crs {crs!r} != EPSG:25832")
        transform_ = src.transform
        width, height = src.width, src.height
        tile_boxes = _tile_boxes(Path(str(mask_path)).parent / "extract")

        for row in range(0, height, chunk_px):
            for col in range(0, width, chunk_px):
                r0, c0 = max(0, row - radius), max(0, col - radius)
                r1 = min(height, row + chunk_px + radius)
                c1 = min(width, col + chunk_px + radius)
                chunk_transform = transform_ * rasterio.Affine.translation(c0, r0)
                window_bounds = rasterio.transform.array_bounds(r1 - r0, c1 - c0, chunk_transform)
                window_bbox = box(*window_bounds)
                chunk_bbox = box(
                    *rasterio.transform.array_bounds(
                        chunk_px, chunk_px, transform_ * rasterio.Affine.translation(col, row)
                    )
                )
                # each building is attributed to the single chunk holding its
                # centroid, so footprint pixels are never double-counted and
                # chunk borders cannot degrade completeness (R-006 overlap)
                hits = [
                    i
                    for i in tree.query(window_bbox)
                    if centroids[i].within(chunk_bbox)
                ]
                if not hits:
                    continue  # no buildings in this window (OR-002)
                chunk = src.read(1, window=Window.from_slices((r0, r1), (c0, c1))).astype(np.float64)
                chunk = np.where(chunk > 0, 1.0, 0.0)

                frac = _local_fraction_chunk(chunk, kernel, radius)
                coverage = _coverage_chunk(
                    tile_boxes, kernel, radius, chunk_px, row, col, transform_, (height, width),
                    (r1 - r0, c1 - c0), (r0 - (row - radius), c0 - (col - radius)),
                )

                # One labeled rasterization per chunk instead of one per
                # building: pixel sums accumulate via bincount, so the
                # dense core is O(window) per chunk, not O(buildings).
                labels = rasterize(
                    [(buildings[i]["geometry"], i + 1) for i in hits],
                    out_shape=chunk.shape,
                    transform=chunk_transform,
                    fill=0,
                    dtype=np.int32,
                    all_touched=False,
                )
                mask = labels > 0
                if not mask.any():
                    continue
                flat = labels[mask].ravel()
                counts = np.bincount(flat, minlength=len(buildings) + 1)
                fsums = np.bincount(flat, weights=frac[mask].ravel(), minlength=len(buildings) + 1)
                csums = np.bincount(flat, weights=coverage[mask].ravel(), minlength=len(buildings) + 1)
                for i in hits:
                    acc[i][0] += float(fsums[i + 1])
                    acc[i][1] += float(counts[i + 1])
                    acc[i][2] += float(csums[i + 1])

    # assemble output features (clip to official boundary, reproject to 4326)
    transformer = pyproj.Transformer.from_crs("EPSG:25832", OUT_CRS, always_xy=True)
    features: list[dict[str, Any]] = []
    for i, b in enumerate(buildings):
        s, px, cov = acc[i]
        completeness = (cov / px) if px else 0.0
        if px == 0 or completeness < COMPLETENESS_MIN:
            value = None
        else:
            value = float(s / px * 100.0)
            if value < 0 or value > 100:
                value = None
        geom = b["geometry"].intersection(boundary_geometry)
        if geom.is_empty:
            continue
        geom4326 = transform(transformer.transform, geom)
        features.append(
            {
                "type": "Feature",
                "id": b["id"],
                "properties": {
                    "id": b["id"],
                    "value": value,
                    "value_str": f"{value:.2f}" if value is not None else UNAVAILABLE,
                    "has_value": value is not None,
                    "completeness": round(completeness, 6),
                    "in_boundary": True,
                },
                "geometry": mapping(geom4326),
            }
        )

    io.write_geojson(features, out_path, crs_name=OUT_CRS)
    return features
