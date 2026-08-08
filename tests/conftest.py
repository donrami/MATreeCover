"""Shared fixtures for the acceptance/pipeline suites.

All tests are read-only against the mannheim workspace and the repo
manifest; state-machine tests operate on copies in tmp dirs.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKSPACE = REPO_ROOT / "data/archive/workspace"


def dist_path(rel: str) -> Path:
    """Resolve a dist-relative file through the hashed-asset map (feature 014).

    Falls back to the un-hashed name when dist/manifest.json is missing or
    predates hashing, so older dist fixtures keep working.
    """
    manifest = REPO_ROOT / "dist" / "manifest.json"
    if manifest.exists():
        try:
            import json

            hashed = json.loads(manifest.read_text(encoding="utf-8")).get("hashed_assets", {})
            if rel in hashed:
                return REPO_ROOT / "dist" / hashed[rel]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    return REPO_ROOT / "dist" / rel


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def workspace() -> Path:
    ws = Path(os.environ.get("MANNHEIM_WORKSPACE", str(DEFAULT_WORKSPACE)))
    if not (ws / "boundary.geojson").exists():
        pytest.skip(f"mannheim workspace not available at {ws}")
    return ws


@pytest.fixture(scope="session")
def boundary_geometry(workspace):
    import json

    from shapely.geometry import shape

    data = json.loads((workspace / "boundary.geojson").read_text(encoding="utf-8"))
    return shape(data["features"][0]["geometry"])


@pytest.fixture(scope="session")
def buffered_geometry(boundary_geometry):
    return boundary_geometry.buffer(60.0)


@pytest.fixture()
def manifest_copy(tmp_path, repo_root):
    """A working copy of artifacts.manifest.json for state-machine tests."""
    src = repo_root / "artifacts.manifest.json"
    dst = tmp_path / "artifacts.manifest.json"
    shutil.copy(src, dst)
    return dst
