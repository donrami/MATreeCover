"""RSS/GPU gate (T039): OR-001/OR-003/SC-009.

Every CLI invocation runs under the `/usr/bin/time -v` wrapper, logs
peak RSS (<= 12 GiB) and `gpu_used: false`, and passes exit codes
through. `runpod-infer` without `MANNHEIM_RUNPOD_ENDPOINT` exits 2.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VENV_PY = REPO_ROOT / ".venv" / "bin" / "python"
EVENT_LOG = REPO_ROOT / "validation" / "event.log.jsonl"
RSS_LIMIT_BYTES = 12 * 1024**3


def _run_cli(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = {**os.environ, **(env or {})}
    return subprocess.run(
        [str(VENV_PY), "-m", "src.pipeline.cli", *args],
        capture_output=True, text=True, cwd=REPO_ROOT, env=full_env, timeout=600,
    )


def _last_event_row() -> dict:
    rows = [json.loads(line) for line in EVENT_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows, "event.log.jsonl is empty"
    return rows[-1]


def test_accept_peak_rss_under_12gib(tmp_path, manifest_copy) -> None:
    env = {"MATREECOVER_MANIFEST": str(manifest_copy)}
    proc = _run_cli("accept", env=env)
    assert proc.returncode == 0  # all artifacts accepted (unblocked)
    row = _last_event_row()
    assert row["subcommand"] == "accept"
    assert row["rss_peak_bytes"] <= RSS_LIMIT_BYTES  # OR-001
    assert row["gpu_used"] is False  # OR-003


def test_runpod_infer_exits_2_without_endpoint() -> None:
    env = {k: v for k, v in os.environ.items() if k != "MANNHEIM_RUNPOD_ENDPOINT"}
    proc = _run_cli("runpod-infer", env=env)
    assert proc.returncode == 2  # OR-003 / FR-025
    assert "STOP" in proc.stdout + proc.stderr


def test_values_gate_exits_1_on_fail_input(tmp_path, manifest_copy) -> None:
    """OR-001: a pending/fail required input short-circuits values."""
    import json as _json

    manifest = _json.loads(manifest_copy.read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        if artifact["kind"] == "canopy-mask":
            artifact["acceptance"] = "fail"
    manifest_copy.write_text(_json.dumps(manifest), encoding="utf-8")
    proc = _run_cli("values", env={"MATREECOVER_MANIFEST": str(manifest_copy)})
    assert proc.returncode == 1  # canopy mask fail short-circuits (OR-001)


def test_event_log_row_shape() -> None:
    _run_cli("accept", env={"MATREECOVER_MANIFEST": str(REPO_ROOT / "artifacts.manifest.json")})
    row = _last_event_row()
    for key in ("ts", "subcommand", "rss_peak_bytes", "gpu_used", "exit_code", "inputs"):
        assert key in row, f"event row missing {key}"


def test_stale_report_sweep() -> None:
    """T058: orphaned .time.*/.inputs.* reports from dead wrappers are
    removed on the next invocation; live wrappers' reports survive."""
    import os as _os

    from src.pipeline import cli as cli_mod

    dead = REPO_ROOT / "validation" / ".time.999999999.txt"  # pid cannot exist
    live = REPO_ROOT / "validation" / f".time.{_os.getpid()}.txt"
    dead.write_text("stale", encoding="utf-8")
    live.write_text("live", encoding="utf-8")
    try:
        cli_mod._sweep_stale_reports()
        assert not dead.exists(), "dead wrapper's report must be swept"
        assert live.exists(), "live wrapper's report must survive"
    finally:
        live.unlink(missing_ok=True)


def test_sigpipe_silent_death() -> None:
    """T058: with the default SIGPIPE disposition, a torn-down session
    (reader gone) kills the wrapper silently instead of surfacing a
    BrokenPipeError exit 1 that masquerades as an acceptance failure."""
    import signal

    proc = subprocess.Popen(
        [str(VENV_PY), "-m", "src.pipeline.cli", "accept"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=REPO_ROOT,
    )
    assert proc.stdout is not None
    proc.stdout.close()  # reader disappears before the wrapper writes
    rc = proc.wait(timeout=120)
    assert rc == -signal.SIGPIPE, f"expected SIGPIPE death, got rc={rc}"
