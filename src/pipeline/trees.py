"""Detected tree areas (E-004, R-007, FR-007/FR-015).

Polygonizes the accepted canopy mask with `rasterio.features.shapes`,
clips to the official boundary (never publishes halo geometry), assigns
stable ids `tree-<n>`, and writes an EPSG:4326 GeoJSON for tippecanoe.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pyproj
import rasterio
from rasterio.features import shapes
from shapely.geometry import mapping, shape
from shapely.ops import transform

from . import io

GSD_M = 0.2
OUT_CRS = "EPSG:4326"
SOURCE = "accepted_canopy_mask"


def polygonize_canopy(
    mask_path: Path | str,
    out_path: Path | str,
    boundary_geometry: Any,
) -> list[dict[str, Any]]:
    """Extract canopy polygons from the binary mask, clipped to the official
    boundary, reprojected to EPSG:4326. Returns the feature list.
    """
    transformer = pyproj.Transformer.from_crs("EPSG:25832", OUT_CRS, always_xy=True)
    features: list[dict[str, Any]] = []
    n = 0
    with rasterio.open(str(mask_path)) as src:
        crs = src.crs.to_string() if src.crs else None
        if crs != "EPSG:25832":
            raise ValueError(f"mask crs {crs!r} != EPSG:25832")
        mask = src.read(1)
        for geom, value in shapes(mask, mask=(mask > 0), transform=src.transform):
            if value == 0:
                continue
            polygon = shape(geom)
            clipped = polygon.intersection(boundary_geometry)
            if clipped.is_empty:
                continue
            n += 1
            canopy_pixels = int(round(polygon.area / (GSD_M * GSD_M)))
            geom4326 = transform(transformer.transform, clipped)
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
