"""Stadtteile acceptance (feature 011, T011).

The published district layer (`dist/stadtteile.geojson`) and the city
stats in `dist/style.json` metadata must match an independent
recomputation from the accepted building values: 38 official districts,
EPSG:4326, no duplicate codes, per-district statistics within 0.5 pp
(mean) / 1 pp (share below 30 %) of a centroid-containment
recomputation (SC-002), and city stats consistent with the district
shares (SC-003). The manifest entry carries the five acceptance
criteria for the new derived artifact (publish-bundle.md).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.conftest import dist_path

REPO_ROOT = Path(__file__).resolve().parents[2]
DIST_STADTTEILE = dist_path("stadtteile.geojson")
DIST_STYLE = dist_path("style.json")


@pytest.fixture(scope="session")
def dist_stadtteile() -> dict:
    if not DIST_STADTTEILE.exists():
        pytest.skip("dist/stadtteile.geojson missing (run make publish)")
    return json.loads(DIST_STADTTEILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def dist_style() -> dict:
    if not DIST_STYLE.exists():
        pytest.skip("dist/style.json missing (run make publish)")
    return json.loads(DIST_STYLE.read_text(encoding="utf-8"))


def _exterior_coords(geometry: dict):
    if geometry["type"] == "Polygon":
        yield from geometry["coordinates"][0]
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            yield from polygon[0]


def test_38_features_and_unique_codes(dist_stadtteile) -> None:
    features = dist_stadtteile["features"]
    assert len(features) == 38  # SC-002 / data-model.md
    codes = [f["properties"]["code"] for f in features]
    assert len(codes) == len(set(codes))  # no duplicate codes


def test_epsg4326_coordinates(dist_stadtteile) -> None:
    for feature in dist_stadtteile["features"]:
        for x, y in _exterior_coords(feature["geometry"]):
            assert -180.0 <= x <= 180.0, (feature["properties"]["code"], x, y)
            assert -90.0 <= y <= 90.0, (feature["properties"]["code"], x, y)


def test_stats_present_on_every_district(dist_stadtteile) -> None:
    for feature in dist_stadtteile["features"]:
        props = feature["properties"]
        assert isinstance(props["n_buildings"], int) and props["n_buildings"] > 0
        assert props["mean_value"] is None or 0.0 <= props["mean_value"] <= 100.0
        assert 0.0 <= props["share_lt30"] <= 100.0


def _independent_district_stats(workspace, dist_stadtteile):
    """Centroid-containment recomputation from the accepted building
    values, independent of publish.py (SC-002)."""
    from shapely.geometry import shape
    from shapely.strtree import STRtree

    buildings = json.loads((workspace / "buildings.geojson").read_text(encoding="utf-8"))
    centroids = []
    for feature in buildings["features"]:
        props = feature["properties"]
        centroids.append((shape(feature["geometry"]).centroid, props.get("value"), props.get("has_value") is True))
    tree = STRtree([c for c, _, _ in centroids])

    stats = {}
    for feature in dist_stadtteile["features"]:
        code = feature["properties"]["code"]
        polygon = shape(feature["geometry"])
        n_buildings = 0
        value_sum = 0.0
        value_count = 0
        below_30 = 0
        for i in tree.query(polygon):
            point, value, has_value = centroids[i]
            if not polygon.contains(point):
                continue
            n_buildings += 1
            if has_value and value is not None:
                value_sum += value
                value_count += 1
                if value < 30:
                    below_30 += 1
        stats[code] = {
            "n_buildings": n_buildings,
            "mean_value": round(value_sum / value_count, 1) if value_count else None,
            "share_lt30": round(100.0 * below_30 / value_count, 1) if value_count else 0.0,
        }
    return stats


def test_district_stats_match_independent_recomputation(workspace, dist_stadtteile) -> None:
    """SC-002: within 0.5 pp (mean) / 1 pp (share) for all 38 districts."""
    independent = _independent_district_stats(workspace, dist_stadtteile)
    for feature in dist_stadtteile["features"]:
        props = feature["properties"]
        code = props["code"]
        ref = independent[code]
        assert props["n_buildings"] == ref["n_buildings"], code
        if ref["mean_value"] is not None:
            assert abs(props["mean_value"] - ref["mean_value"]) <= 0.5, code
        assert abs(props["share_lt30"] - ref["share_lt30"]) <= 1.0, code


def test_city_stats_match_recomputation(workspace, dist_style, dist_stadtteile) -> None:
    """SC-003: city stats match a recomputation from the accepted dataset."""
    stats = dist_style["metadata"]["city_stats"]
    assert "mean_value_pct" in stats and "share_gte30_pct" in stats and "tree_count" in stats

    independent = _independent_district_stats(workspace, dist_stadtteile)
    total_n = sum(v["n_buildings"] for v in independent.values())
    # mean recomputed from the same independent join (value-weighted)
    buildings = json.loads((workspace / "buildings.geojson").read_text(encoding="utf-8"))
    values = [f["properties"]["value"] for f in buildings["features"] if f["properties"].get("has_value") and f["properties"].get("value") is not None]
    mean = sum(values) / len(values)
    assert abs(stats["mean_value_pct"] - round(mean, 1)) <= 0.5

    # share_gte30 consistent with the district shares, weighted by
    # n_buildings: 100 - weighted share_lt30 (SC-003 invariant)
    weighted_share_lt30 = sum(
        v["n_buildings"] * v["share_lt30"] for v in independent.values()
    ) / total_n
    assert abs(stats["share_gte30_pct"] - (100.0 - weighted_share_lt30)) <= 0.1

    import pyogrio

    tree_count = pyogrio.read_info(str(workspace / "trees_polygons.geojson"))["features"]
    assert abs(stats["tree_count"] - tree_count) / tree_count <= 0.01


def test_manifest_entry_acceptance_criteria(repo_root) -> None:
    """publish-bundle.md: the five checks on the stadtteile derived
    artifact record."""
    from src.pipeline import acceptance

    manifest = json.loads((repo_root / "artifacts.manifest.json").read_text(encoding="utf-8"))
    entry = next(a for a in manifest["artifacts"] if a["kind"] == "stadtteile")
    assert "GDI-MA" in entry["source"]
    assert entry["license"] == "dl-de/by-2-0"
    assert entry["resolution"] == "n/a"
    assert entry["completeness"] == 1.0
    assert entry["lineage"]["inputs"]  # non-empty lineage
    results = acceptance.run_checks(entry, repo_root / "data/archive/workspace")
    assert {r.criterion: r.status for r in results} == {
        "source": "ok",
        "extent": "ok",
        "resolution": "ok",
        "completeness": "ok",
        "lineage": "ok",
    }
