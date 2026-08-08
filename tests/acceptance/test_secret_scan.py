"""Full-history secret scan gate test (SC-001/SC-006, feature 015).

`scripts/check-git-history.sh` must run clean on this repository: every
historical finding has an exemption row, and every exemption row resolves
to a dispositioned finding in the committed audit report.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HISTORY_GATE = "scripts/check-git-history.sh"
EXEMPTIONS = REPO_ROOT / "scripts" / "history-exemptions.tsv"
REPORT = REPO_ROOT / "verification" / "security-audit-2026-08-08.md"


def test_history_gate_runs_clean() -> None:
    """FR-001/SC-001: the scan over all commits exits 0 with zero open
    findings and names the counts."""
    proc = subprocess.run(
        ["bash", HISTORY_GATE], capture_output=True, text=True, cwd=REPO_ROOT, timeout=300, check=False,
    )
    assert proc.returncode == 0, f"gate failed:\n{proc.stdout}\n{proc.stderr}"
    assert re.search(r"clean: \d+ commits scanned, \d+ exempted findings, 0 open", proc.stdout), (
        f"unexpected gate output:\n{proc.stdout}"
    )


def test_every_exemption_resolves_to_report_finding() -> None:
    """E3/SC-006: each exemption row's disposition reference exists in the
    committed audit report's findings table."""
    if not EXEMPTIONS.exists():
        pytest.fail("scripts/history-exemptions.tsv missing")
    report_text = REPORT.read_text(encoding="utf-8")
    rows = [
        line.split("\t")
        for line in EXEMPTIONS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert rows, "exemption ledger is empty"
    for row in rows:
        assert len(row) >= 4, f"malformed exemption row: {row!r}"
        pattern_id, commit, path, disposition_ref = row[0], row[1], row[2], row[3].strip()
        assert re.fullmatch(r"P\d+", pattern_id), f"bad pattern id: {pattern_id}"
        assert re.fullmatch(r"[0-9a-f]{7,40}", commit), f"bad commit: {commit}"
        assert path, f"empty path in row: {row!r}"
        assert re.fullmatch(r"F\d+", disposition_ref), (
            f"disposition ref must be a finding id: {disposition_ref}"
        )
        assert f"| {disposition_ref} |" in report_text, (
            f"exemption {disposition_ref} ({pattern_id} {commit} {path}) "
            f"has no dispositioned finding in the audit report"
        )
