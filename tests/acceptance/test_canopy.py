"""Canopy mask acceptance (T035): the quarantined baseline failure state.

Completeness 0.48 < 0.95 → `fail`; `invalidates` lists the two dependent
derived artifacts per FR-023.
"""

from __future__ import annotations

import json

from src.pipeline import acceptance


def _canopy_artifact(repo_root) -> dict:
    manifest = json.loads((repo_root / "artifacts.manifest.json").read_text(encoding="utf-8"))
    return next(a for a in manifest["artifacts"] if a["kind"] == "canopy-mask")


def test_baseline_failure_state(repo_root) -> None:
    artifact = _canopy_artifact(repo_root)
    assert artifact["acceptance"] == "fail"
    assert artifact["completeness"] == 0.48  # spec evidence


def test_completeness_below_threshold(workspace, repo_root) -> None:
    artifact = _canopy_artifact(repo_root)
    check = acceptance.check_completeness(artifact, workspace)
    assert check.status == "fail"  # 0.48 < 0.95
    assert artifact["checks"]["completeness"] == "fail"


def test_invalidates_dependents(repo_root) -> None:
    artifact = _canopy_artifact(repo_root)
    assert artifact["invalidates"] == ["buildings.geojson", "trees.pmtiles"]


def test_mask_file_recorded(workspace, repo_root) -> None:
    artifact = _canopy_artifact(repo_root)
    assert (workspace / artifact["path"]).exists()
    assert artifact["size_bytes"] > 50 * 1024 * 1024  # OR-005 record
    assert len(artifact["sha256"]) == 64


def test_resolution_recorded(workspace, repo_root) -> None:
    artifact = _canopy_artifact(repo_root)
    assert artifact["resolution"] == "0.2 m"
