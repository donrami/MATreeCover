"""Read/write `artifacts.manifest.json` per `contracts/manifest.md`.

The manifest is the single source of truth for what the pipeline reads,
what it reuses, and what it invalidates. Acceptance states:

    pending ──► pass ──► pass            (pass is terminal)
             └─► fail ──► fail ──► cascades to `invalidates` → pending

The pipeline is the only writer. `accept` re-validates every artifact and
refreshes the manifest; a `fail` cascades to its `invalidates` list.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "artifacts.manifest.json"

STATES = ("pass", "fail", "pending")


def manifest_path() -> Path:
    """Manifest location; overridable for tests via MATREECOVER_MANIFEST."""
    return Path(os.environ.get("MATREECOVER_MANIFEST", str(MANIFEST_PATH)))


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    path = path or manifest_path()
    if not path.exists():
        raise FileNotFoundError(
            f"artifacts.manifest.json missing at {path}; run the seed step first"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(manifest: dict[str, Any], path: Path | None = None) -> None:
    path = path or manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_artifact(manifest: dict[str, Any], path: str) -> dict[str, Any] | None:
    for artifact in manifest.get("artifacts", []):
        if artifact.get("path") == path:
            return artifact
    return None


def upsert_artifact(manifest: dict[str, Any], artifact: dict[str, Any]) -> None:
    """Insert or replace an artifact record (matched by path)."""
    artifacts = manifest.setdefault("artifacts", [])
    for i, existing in enumerate(artifacts):
        if existing.get("path") == artifact.get("path"):
            artifacts[i] = artifact
            return
    artifacts.append(artifact)


def cascade_failures(manifest: dict[str, Any]) -> list[str]:
    """FR-023: a `fail` artifact flips every entry in its `invalidates` list
    to `pending` (unless the dependent is already `fail`).

    Returns the paths flipped so callers can report them.
    """
    flipped: list[str] = []
    for artifact in manifest.get("artifacts", []):
        if artifact.get("acceptance") != "fail":
            continue
        for dep_path in artifact.get("invalidates", []):
            dep = get_artifact(manifest, dep_path)
            if dep is not None and dep.get("acceptance") != "fail":
                dep["acceptance"] = "pending"
                dep["checks"] = {k: "pending" for k in ("source", "extent", "resolution", "completeness", "lineage")}
                flipped.append(dep_path)
    return flipped


def any_failed(manifest: dict[str, Any]) -> bool:
    return any(a.get("acceptance") == "fail" for a in manifest.get("artifacts", []))


def required_ready(manifest: dict[str, Any], required: list[str]) -> list[tuple[str, str]]:
    """Return [(path, acceptance)] for required artifacts that are not `pass`."""
    blocked: list[tuple[str, str]] = []
    for path in required:
        artifact = get_artifact(manifest, path)
        if artifact is None:
            blocked.append((path, "missing"))
        elif artifact.get("acceptance") != "pass":
            blocked.append((path, artifact.get("acceptance", "unknown")))
    return blocked


def summary_lines(manifest: dict[str, Any]) -> list[str]:
    lines = [f"release {manifest.get('release_id', '?')}"]
    for artifact in manifest.get("artifacts", []):
        lines.append(
            f"  {artifact.get('acceptance', '?'):7s} {artifact.get('path')}"
        )
    return lines
