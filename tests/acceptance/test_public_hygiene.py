"""Public-hygiene gate self-test (SC-007, feature 015).

Every pattern in `scripts/public-patterns.txt` must make
`scripts/check-public.sh` fail with the probe file and the matching text
named. A pattern that stops matching (or a new pattern without a sample)
fails this test.

The probe file is built from runtime concatenations on purpose: the
forbidden literals must never appear verbatim in this tracked source file,
or the gate would flag the test itself. The gate scans `git ls-files`,
so the probe is added to the index with intent-to-add and removed again
in a finally block.
"""

from __future__ import annotations

import re
import subprocess
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GATE = "scripts/check-public.sh"
PATTERN_FILE = REPO_ROOT / "scripts" / "public-patterns.txt"

# Runtime-built samples, one per pattern id. Keep in sync with
# scripts/public-patterns.txt (the coverage assertion below enforces it).
SAMPLES = {
    "P1": "/home/" + "alice" + "/",
    "P2": "/Users/" + "alice" + "/",
    "P3": "~/" + ".ssh/",
    "P4": "id_" + "ed25519",
    "P5": "-----BEGIN " + "OPENSSH " + "PRIVATE KEY-----",
    "P6": "ghp_" + "a" * 20,
    "P7": "sk-" + "a" * 20,
    "P8": "AKIA" + "0" * 16,
    "P9": 'zone_id = "' + "a" * 32 + '"',
    "P10": "speck" + "it",
    "P11": ".spec-" + "workflow",
    "P12": ".spec" + "ify",
    "P13": "root@" + "example.com",
    "P14": "open" + "code",
    "P15": "local:" + "//",
    "P16": "alpha_" + "search",
    "P17": "fetch_" + "content",
    "P18": "web_" + "search",
    "P19": "sub" + "agent",
    "P20": "github_pat_" + "a" * 22,
    "P21": "CLOUDFLARE_API_TOKEN = \"" + "A" * 40 + "\"",
    "P22": "X-Auth-" + "Email: " + "me@example.com",
    "P23": "aws_secret_access_key = \"" + "A" * 40 + "\"",
    "P24": "ASIA" + "0" * 16,
    "P25": "npm_" + "a" * 30,
    "P26": "xoxb-" + "a" * 12 + "-" + "b" * 12 + "-" + "c" * 24,
    "P27": "sk_live_" + "a" * 24,
    "P28": "AIza" + "a" * 35,
    "P29": "-----BEGIN PGP " + "PRIVATE KEY BLOCK-----",
    "P30": "PuTTY-" + "User-Key-File",
    "P31": "machine github.com " + "login owner " + "password secret",
    "P32": "Desktop" + "/notes",
}


def _pattern_ids() -> list[str]:
    """Pattern ids declared in the shared pattern file (P1, P2, ...)."""
    text = PATTERN_FILE.read_text(encoding="utf-8")
    return re.findall(r"^# (P\d+) ", text, flags=re.MULTILINE)


def test_every_pattern_has_a_sample() -> None:
    """SC-007 self-maintenance: the gate covers exactly the patterns that
    have samples, so a new pattern without a sample is a test failure."""
    declared = set(_pattern_ids())
    assert declared == set(SAMPLES), (
        f"pattern/sample mismatch: declared={sorted(declared - set(SAMPLES))} "
        f"samples-only={sorted(set(SAMPLES) - declared)}"
    )


def _probe_path() -> Path:
    return REPO_ROOT / f"hygiene_probe_{uuid.uuid4().hex[:8]}.txt"


def test_gate_catches_every_pattern() -> None:
    """A tracked-looking file containing each pattern must fail the gate
    with the file and every matching text named (SC-007, quickstart S1)."""
    probe = _probe_path()
    probe.write_text("\n".join(SAMPLES.values()) + "\n", encoding="utf-8")
    try:
        subprocess.run(
            ["git", "add", "-N", str(probe)],
            check=True, capture_output=True, text=True, cwd=REPO_ROOT,
        )
        proc = subprocess.run(
            ["bash", GATE], capture_output=True, text=True, cwd=REPO_ROOT, timeout=120, check=False,
        )
        assert proc.returncode != 0, "gate did not fail on synthetic patterns"
        assert "FAIL" in proc.stdout, f"no FAIL summary:\n{proc.stdout}"
        assert probe.name in proc.stdout, f"probe file not named:\n{proc.stdout}"
        for pattern_id, sample in SAMPLES.items():
            assert sample in proc.stdout, (
                f"{pattern_id}: matching text not named\n---\n{proc.stdout}"
            )
    finally:
        subprocess.run(
            ["git", "rm", "--cached", "--force", "--quiet", str(probe)],
            capture_output=True, text=True, cwd=REPO_ROOT, check=False,
        )
        probe.unlink(missing_ok=True)
