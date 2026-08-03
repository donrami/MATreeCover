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


def _local_fraction_chunk(chunk: np.ndarray, kernel: np.ndarray, radius: int) -> tuple[np.ndarray, np.ndarray]:
    """Local canopy fraction and local kernel-coverage fraction for one chunk.

    The fraction reflect-pads the chunk so the convolution at interior
    pixels is exact (R-006). The coverage array zero-pads instead, so
    pixels whose 60 m disc extends beyond the data get coverage < 1;
    buildings there are nulled (FR-009, missing imagery = unavailable).
    """
    pad = radius
    mode = "reflect" if min(chunk.shape) > pad else "edge"
    ksum = kernel.sum()
    padded = np.pad(chunk, pad, mode=mode)
    frac = fftconvolve(padded, kernel, mode="valid") / ksum
    coverage = fftconvolve(np.pad(np.ones_like(chunk, dtype=np.float64), pad, mode="constant"), kernel, mode="valid") / ksum
    return frac, coverage


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

    # accumulate per building: [sum_frac, count_px, sum_coverage]
    acc: dict[int, list[float]] = {i: [0.0, 0.0, 0.0] for i in range(len(buildings))}

    with rasterio.open(str(mask_path)) as src:
        crs = src.crs.to_string() if src.crs else None
        if crs != "EPSG:25832":
            raise ValueError(f"mask crs {crs!r} != EPSG:25832")
        transform_ = src.transform
        width, height = src.width, src.height

        for row in range(0, height, chunk_px):
            for col in range(0, width, chunk_px):
                r0, c0 = max(0, row - radius), max(0, col - radius)
                r1 = min(height, row + chunk_px + radius)
                c1 = min(width, col + chunk_px + radius)
                chunk = src.read(1, window=Window.from_slices((r0, r1), (c0, c1))).astype(np.float64)
                chunk = np.where(chunk > 0, 1.0, 0.0)

                frac, coverage = _local_fraction_chunk(chunk, kernel, radius)

                chunk_transform = transform_ * rasterio.Affine.translation(c0, r0)
                window_bounds = rasterio.transform.array_bounds(chunk.shape[0], chunk.shape[1], chunk_transform)
                bbox_geom = box(*window_bounds)
                for hit in tree.query(bbox_geom):
                    b = buildings[hit]
                    geom = b["geometry"]
                    if not geom.intersects(bbox_geom):
                        continue
                    mask_arr = rasterize(
                        [(geom, 1)],
                        out_shape=chunk.shape,
                        transform=chunk_transform,
                        fill=0,
                        dtype=np.uint8,
                        all_touched=False,
                    ).astype(bool)
                    px = mask_arr.sum()
                    if px == 0:
                        continue
                    acc[hit][0] += float((frac * mask_arr).sum())
                    acc[hit][1] += float(px)
                    acc[hit][2] += float((coverage * mask_arr).sum())

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
