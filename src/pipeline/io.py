"""Low-level IO helpers (OR-002). Raster work is windowed in `values.py`;
this module holds the shared file-level utilities.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_geojson(features: Iterable[dict[str, Any]], path: Path | str, crs_name: str = "EPSG:25832") -> None:
    """Streaming FeatureCollection writer (one feature per line, still valid JSON)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write('{\n  "type": "FeatureCollection",\n  "crs": {\n    "type": "name",\n'
                f'    "properties": {{ "name": "urn:ogc:def:crs:{crs_name}" }}\n  }},\n'
                '  "features": [\n')
        for i, feature in enumerate(features):
            sep = ",\n" if i else ""
            f.write(sep + json.dumps(feature, ensure_ascii=False))
        f.write("\n  ]\n}\n")
