"""Layout gate test (SC-003, feature 015).

`scripts/check-layout.sh` must run clean on the audited tree: every
tracked path resolves to a documented top-level entry, every manifest
row exists, and no undocumented root-level file remains.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LAYOUT_GATE = "scripts/check-layout.sh"
MANIFEST = REPO_ROOT / "scripts" / "layout-manifest.tsv"


def test_layout_gate_runs_clean() -> None:
    proc = subprocess.run(
        ["bash", LAYOUT_GATE], capture_output=True, text=True, cwd=REPO_ROOT, timeout=120, check=False,
    )
    assert proc.returncode == 0, f"layout gate failed:\n{proc.stdout}\n{proc.stderr}"
    assert re.search(r"clean: \d+ tracked paths, \d+ documented entries", proc.stdout), (
        f"unexpected gate output:\n{proc.stdout}"
    )


def test_manifest_rows_are_documented_top_level() -> None:
    """Every manifest row is a top-level tracked entry and vice versa."""
    rows = [
        line.split("\t")
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert rows, "layout manifest is empty"
    manifest_entries = {row[0].rstrip("/") for row in rows}
    tracked_top = {
        line.split("/", 1)[0]
        for line in subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, cwd=REPO_ROOT, check=True
        ).stdout.splitlines()
    }
    # after the housekeeping pass the manifest covers exactly the tracked top level
    assert manifest_entries == tracked_top, (
        f"manifest/tree mismatch: manifest-only={sorted(manifest_entries - tracked_top)} "
        f"tree-only={sorted(tracked_top - manifest_entries)}"
    )
