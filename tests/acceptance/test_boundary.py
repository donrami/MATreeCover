"""Boundary acceptance (T032): the five FR-021 checks on E-001.

Source LGL `dl-de/by-2-0`, extent vs boundary, resolution n/a,
completeness 1.0, lineage recorded.
"""

from __future__ import annotations

import json


def _boundary_artifact(repo_root) -> dict:
    manifest = json.loads((repo_root / "artifacts.manifest.json").read_text(encoding="utf-8"))
    return next(a for a in manifest["artifacts"] if a["kind"] == "boundary")


def test_source_lgl(workspace, repo_root) -> None:
    artifact = _boundary_artifact(repo_root)
    assert "LGL" in artifact["source"]
    assert artifact["license"] == "dl-de/by-2-0"


def test_extent_matches_boundary(workspace, repo_root) -> None:
    from src.pipeline import acceptance

    artifact = _boundary_artifact(repo_root)
    check = acceptance.check_extent(artifact, workspace)
    assert check.status == "ok", check.detail


def test_resolution_na(workspace, repo_root) -> None:
    from src.pipeline import acceptance

    artifact = _boundary_artifact(repo_root)
    check = acceptance.check_resolution(artifact, workspace)
    assert check.status == "ok" and artifact["resolution"] == "n/a"


def test_completeness_1(workspace, repo_root) -> None:
    from src.pipeline import acceptance

    artifact = _boundary_artifact(repo_root)
    assert artifact["completeness"] == 1.0
    check = acceptance.check_completeness(artifact, workspace)
    assert check.status == "ok"


def test_lineage_recorded(workspace, repo_root) -> None:
    from src.pipeline import acceptance

    artifact = _boundary_artifact(repo_root)
    check = acceptance.check_lineage(artifact, workspace)
    assert check.status == "ok"


def test_all_five_checks_pass(workspace, repo_root) -> None:
    from src.pipeline import acceptance

    artifact = _boundary_artifact(repo_root)
    results = acceptance.run_checks(artifact, workspace)
    assert {r.criterion: r.status for r in results} == {
        "source": "ok",
        "extent": "ok",
        "resolution": "ok",
        "completeness": "ok",
        "lineage": "ok",
    }


def test_load_boundary_geometry(workspace) -> None:
    from src.pipeline import boundary

    loaded = boundary.load_boundary(workspace / "boundary.geojson")
    assert loaded["crs"] == "EPSG:25832"
    assert loaded["area_m2"] > 0
    assert len(loaded["bbox"]) == 4
    assert loaded["bbox"][0] < loaded["bbox"][2]
    assert loaded["bbox"][1] < loaded["bbox"][3]
