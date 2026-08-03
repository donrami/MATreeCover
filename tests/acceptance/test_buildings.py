"""Buildings acceptance (T033): source/crs/count assertions (SC-003),
no outside, synthetic, or duplicate buildings (FR-004).
"""

from __future__ import annotations

import json

from src.pipeline import buildings

EXPECTED_COUNT = 93024  # SC-003 / 2026.01/meta.json (raw inventory)


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
    assert len(loaded) <= EXPECTED_COUNT
    assert len(loaded) >= EXPECTED_COUNT - 5  # only duplicate ids are dropped


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
