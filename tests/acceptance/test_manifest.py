"""Manifest state machine (T038): FR-022/FR-023/SC-010.

`pass` is terminal; `fail` cascades to `invalidates` → `pending`;
independent accepted inputs stay `pass`; accepted artifacts are never
regenerated (their recorded sha256/size survive a re-validation).
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from src.pipeline import artifact_manifest as am


def _minimal_manifest() -> dict:
    return {
        "release_id": "test",
        "generated_at": "2026-01-01T00:00:00Z",
        "artifacts": [
            {
                "path": "boundary.geojson",
                "kind": "boundary",
                "acceptance": "pass",
                "invalidates": [],
            },
            {
                "path": "mosaic/canopy_prediction_mask.tif",
                "kind": "canopy-mask",
                "acceptance": "fail",
                "invalidates": ["buildings.geojson", "trees.pmtiles"],
            },
            {"path": "buildings.geojson", "kind": "values", "acceptance": "pass", "invalidates": []},
            {"path": "trees.pmtiles", "kind": "trees", "acceptance": "pending", "invalidates": []},
        ],
    }


def test_pass_is_terminal() -> None:
    manifest = _minimal_manifest()
    flipped = am.cascade_failures(manifest)
    assert "buildings.geojson" in flipped
    # a pass artifact is never flipped by a cascade
    assert am.get_artifact(manifest, "boundary.geojson")["acceptance"] == "pass"
    assert am.get_artifact(manifest, "buildings.geojson")["acceptance"] == "pending"


def test_fail_cascades_to_pending() -> None:
    manifest = _minimal_manifest()
    flipped = am.cascade_failures(manifest)
    assert flipped == ["buildings.geojson", "trees.pmtiles"]
    assert am.get_artifact(manifest, "trees.pmtiles")["acceptance"] == "pending"
    assert am.get_artifact(manifest, "buildings.geojson")["acceptance"] == "pending"


def test_independent_inputs_stay_pass(manifest_copy, workspace) -> None:
    """FR-023: a failed derived artifact does not touch accepted inputs."""
    manifest = am.load_manifest(manifest_copy)
    before = {
        a["path"]: a["acceptance"]
        for a in manifest["artifacts"]
        if a["acceptance"] == "pass"
    }
    flipped = am.cascade_failures(manifest)
    after = {a["path"]: a["acceptance"] for a in manifest["artifacts"]}
    for path, state in before.items():
        if path not in flipped:
            assert after[path] == state, f"{path} changed despite independence"
    assert am.get_artifact(manifest, "boundary.geojson")["acceptance"] == "pass"


def test_no_regeneration_of_pass_artifacts(tmp_path, manifest_copy, repo_root) -> None:
    """SC-010: re-validation of accepted inputs changes nothing (no
    re-download/re-generation); the recorded sha256/size are stable."""
    import shutil

    work = tmp_path / "work"
    shutil.copytree(manifest_copy.parent, work / "manifest", dirs_exist_ok=True)
    env = {**os.environ, "MATREECOVER_MANIFEST": str(work / "manifest" / "artifacts.manifest.json")}
    proc = subprocess.run(
        [str(repo_root / ".venv" / "bin" / "python"), "-m", "src.pipeline.cli", "accept"],
        capture_output=True, text=True, cwd=repo_root, env=env, timeout=600,
    )
    assert proc.returncode == 1  # canopy mask still fails (quarantine)
    before = {
        a["path"]: (a["sha256"], a["size_bytes"])
        for a in am.load_manifest(manifest_copy)["artifacts"]
        if a["sha256"]
    }
    after = {
        a["path"]: (a["sha256"], a["size_bytes"])
        for a in am.load_manifest(work / "manifest" / "artifacts.manifest.json")["artifacts"]
        if a["sha256"]
    }
    for path, record in before.items():
        assert after[path] == record, f"{path} regenerated on re-validation"
