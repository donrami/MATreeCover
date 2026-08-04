"""Buildings acceptance (T033/T057): source/crs/count assertions (SC-003),
no outside, synthetic, or duplicate buildings (FR-004).

SC-003 accounting: the raw LGL inventory holds 93,024 rows; exactly 2 of
them are duplicate-id rows (`b-62e14c8638d8`, `b-c0aa13bc722a`, each
listed twice — the same footprint recorded twice). FR-004 de-duplicates
by stable id, so the published set carries 93,022 features.
"""

from __future__ import annotations

import json

from src.pipeline import buildings

EXPECTED_COUNT = 93024  # SC-003 / 2026.01/meta.json (raw inventory)
EXPECTED_DEDUPED_COUNT = 93022  # FR-004: 2 duplicate-id rows dropped
EXPECTED_DUPLICATE_ROWS = 2


def _buildings_artifact(repo_root) -> dict:
    manifest = json.loads((repo_root / "artifacts.manifest.json").read_text(encoding="utf-8"))
    return next(a for a in manifest["artifacts"] if a["kind"] == "buildings")


def test_source_recorded(workspace, repo_root) -> None:
    artifact = _buildings_artifact(repo_root)
    assert artifact["source"] == "LGL ALKIS Hausumringe"
    assert artifact["license"] == "dl-de/by-2-0"
    assert artifact["feature_count"] == EXPECTED_COUNT


def test_raw_feature_count(workspace) -> None:
    import pyogrio

    info = pyogrio.read_info(str(workspace / "tables" / "buildings.geojson"))
    assert info["features"] == EXPECTED_COUNT  # SC-003
    assert info["crs"] == "EPSG:25832"


def test_crs_and_count(workspace) -> None:
    loaded = buildings.load_buildings(workspace / "tables/buildings.geojson")
    # SC-003: 93,024 raw rows minus the 2 duplicate-id rows dropped by
    # FR-004's de-duplication on the stable id.
    assert len(loaded) == EXPECTED_DEDUPED_COUNT


def test_duplicate_ids_dropped(workspace) -> None:
    """FR-004/SC-003: exactly the 2 duplicate-id rows are dropped, nothing
    else."""
    import numpy as np
    import pyogrio
    from collections import Counter

    result = pyogrio.raw.read(str(workspace / "tables" / "buildings.geojson"))
    meta = result[0]
    wkb = None
    columns = None
    for item in result[1:]:
        if isinstance(item, np.ndarray) and item.ndim == 1 and len(item) > 0 and isinstance(item[0], (bytes, bytearray)):
            wkb = item
        elif isinstance(item, list) and item and isinstance(item[0], np.ndarray):
            columns = item
    names = list(meta.get("fields", []))
    id_idx = names.index("id")
    raw = [str(columns[id_idx][i]) for i in range(len(wkb))]
    counts = Counter(raw)
    dup_rows = sum(v - 1 for v in counts.values() if v > 1)
    assert dup_rows == EXPECTED_DUPLICATE_ROWS  # 2 duplicate-id rows
    loaded = buildings.load_buildings(workspace / "tables/buildings.geojson")
    assert len(loaded) == len(raw) - dup_rows  # only duplicates dropped


def test_published_feature_count(workspace) -> None:
    """SC-003: the published buildings layer (values output) carries
    93,022 features — the deduped inventory count."""
    import pyogrio

    info = pyogrio.read_info(str(workspace / "buildings.geojson"))
    assert info["features"] == EXPECTED_DEDUPED_COUNT


def test_no_duplicate_ids(workspace) -> None:
    loaded = buildings.load_buildings(workspace / "tables/buildings.geojson")
    ids = [b["id"] for b in loaded]
    assert len(ids) == len(set(ids))  # FR-004


def test_no_synthetic_geometry(workspace) -> None:
    loaded = buildings.load_buildings(workspace / "tables/buildings.geojson")
    for b in loaded:
        assert not b["geometry"].is_empty
        assert b["geometry"].geom_type in ("Polygon", "MultiPolygon")


def test_no_outside_buildings(workspace, buffered_geometry) -> None:
    loaded = buildings.load_buildings(workspace / "tables/buildings.geojson")
    selected = buildings.select_in_buffer(loaded, buffered_geometry)
    # every accepted footprint intersects the analysis boundary (FR-004)
    assert len(selected) == len(loaded)


def test_clip_buildings_output(tmp_path, workspace, buffered_geometry) -> None:
    out = tmp_path / "buildings_clipped.geojson"
    count = buildings.clip_buildings(
        workspace / "tables/buildings.geojson", out, buffered_geometry
    )
    assert count == len(buildings.load_buildings(workspace / "tables/buildings.geojson"))
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["type"] == "FeatureCollection"
    for feature in data["features"]:
        assert feature["properties"]["in_boundary"] is True
