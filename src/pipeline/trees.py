"""Detected tree (E-004, R-007, FR-007/FR-015).

Polygonizes the accepted canopy mask with `rasterio.features.shapes`,
clips to the official boundary (never publishes halo geometry), assigns
stable ids `tree-<n>`, and writes EPSG:4326 GeoJSON for tippecanoe.

OR-002: the mask is never loaded whole. Reads are windowed — 1000 px
chunks with a 1 px overlap, matching `values.py` and
`2026.01/meta.json`. Each window is polygonized in pixel space, and
polygons touching the shared overlap strips are stitched (unioned) so a
canopy component that crosses a chunk seam yields exactly one feature —
the same result as polygonizing the full array, with bounded memory.
4-connectivity is preserved: pieces that merely touch at a corner are
never merged. Window order is fixed (row-major) and all GEOS operations
are deterministic, so the output is reproducible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pyproj
import rasterio
from rasterio import Affine
from rasterio.features import shapes
from rasterio.windows import Window
from shapely.geometry import mapping, shape
from shapely.ops import transform as shp_transform

from . import io

GSD_M = 0.2
OUT_CRS = "EPSG:4326"
SOURCE = "accepted_canopy_mask"
CHUNK_PX = 1000  # OR-002: chunked jobs (matches values.py / meta.json)


def _should_merge(a: Any, b: Any) -> bool:
    """True when the pieces share area (the 1 px overlap strip).

    `rasterio.features.shapes` uses 4-connectivity, so corner-touching
    components are distinct in the full-read reference; pieces that only
    touch at a point must therefore never be merged.
    """
    if not a.intersects(b):
        return False
    return not a.touches(b) or a.equals(b)


def _merge_with(poly: Any, pools: list[list[Any]]) -> Any:
    """Union ``poly`` with every open polygon it should merge with.

    Merged polygons are removed from the pools (they live on inside the
    result). Iterates to a fixpoint so a chain of overlapping pieces is
    fully combined. Deterministic: pools are ordered lists, window
    iteration is row-major.
    """
    changed = True
    while changed:
        changed = False
        for pool in pools:
            for other in list(pool):
                if _should_merge(poly, other):
                    poly = poly.union(other)
                    pool.remove(other)
                    changed = True
    return poly


def polygonize_canopy(
    mask_path: Path | str,
    out_path: Path | str,
    boundary_geometry: Any,
    chunk_px: int = CHUNK_PX,
) -> list[dict[str, Any]]:
    """Extract canopy polygons from a binary mask, clipped to the official
    boundary, reprojected to EPSG:4326. Returns the feature list.

    Windowed polygonization with 1 px overlap: a component crossing a
    window edge appears (overlapping) in both windows' reads, so the
    union of the two pieces reproduces the full component. Polygon
    coordinates are kept in exact integer pixel space for the seam tests
    and converted to EPSG:25832 only when a polygon is final.
    """
    transformer = pyproj.Transformer.from_crs("EPSG:25832", OUT_CRS, always_xy=True)
    features: list[dict[str, Any]] = []
    final_polys: list[Any] = []
    n = 0

    with rasterio.open(str(mask_path)) as src:
        crs = src.crs.to_string() if src.crs else None
        if crs != "EPSG:25832":
            raise ValueError(f"mask crs {crs!r} != EPSG:25832")
        height, width = src.height, src.width
        affine = src.transform

        # open_polys[(row, col)]: polygons from that window touching its
        # bottom/right overlap strip, still able to merge with a later
        # window. Bounded by the window frontier, flushed at the end.
        open_polys: dict[tuple[int, int], list[Any]] = {}

        for row in range(0, height, chunk_px):
            for col in range(0, width, chunk_px):
                r0, c0 = max(0, row - 1), max(0, col - 1)
                r1, c1 = min(height, row + chunk_px + 1), min(width, col + chunk_px + 1)
                data = src.read(1, window=Window.from_slices((r0, r1), (c0, c1)))
                if not data.any():
                    continue

                # 1 px overlap strips shared with the neighbours
                # (absolute pixel coords; exact integer comparisons).
                bottom_strip = row + chunk_px - 1
                right_strip = col + chunk_px - 1
                merge_pools: list[list[Any]] = []
                if row > 0:
                    merge_pools.append(open_polys.get((row - chunk_px, col), []))
                if col > 0:
                    merge_pools.append(open_polys.get((row, col - chunk_px), []))

                # translate read-local pixel coords to absolute pixels
                window_tf = Affine.translation(c0, r0)
                for geom, value in shapes(data, mask=(data > 0), transform=window_tf):
                    if value == 0:
                        continue
                    poly = _merge_with(shape(geom), merge_pools)
                    minc, minr, maxc, maxr = poly.bounds
                    if maxr >= bottom_strip or maxc >= right_strip:
                        open_polys.setdefault((row, col), []).append(poly)
                    else:
                        final_polys.append(poly)

        # windows after the last row/column have no consumers: flush
        for key in list(open_polys):
            final_polys.extend(open_polys.pop(key))

        def _to_crs(poly: Any) -> Any:
            return shp_transform(lambda x, y: tuple(affine * (x, y)), poly)

        for poly in final_polys:
            clipped = _to_crs(poly).intersection(boundary_geometry)
            if clipped.is_empty:
                continue
            n += 1
            canopy_pixels = int(round(clipped.area / (GSD_M * GSD_M)))
            geom4326 = shp_transform(transformer.transform, clipped)
            features.append(
                {
                    "type": "Feature",
                    "id": f"tree-{n}",
                    "properties": {
                        "id": f"tree-{n}",
                        "canopy_pixel_count": canopy_pixels,
                        "source": SOURCE,
                    },
                    "geometry": mapping(geom4326),
                }
            )

    io.write_geojson(features, out_path, crs_name=OUT_CRS)
    return features
