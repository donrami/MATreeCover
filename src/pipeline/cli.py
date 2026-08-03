"""`tree-cover` CLI (`contracts/cli.md`).

One binary, several single-purpose subcommands. Each invocation runs as a
child process under `/usr/bin/time -v` so the wrapper can measure peak RSS
(exit 3 on > 12 GiB, OR-001), records a row in
`validation/event.log.jsonl`, and enforces the input acceptance gate
(pending/fail input short-circuits, OR-001/OR-002).

Exit codes: 0 success, 1 acceptance/input failure, 2 RunPod gate,
3 RSS > 12 GiB, 4 GPU attempted locally.
"""

from __future__ import annotations

import json
import os
import resource
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import click

from . import acceptance, artifact_manifest as manifest_mod, io, workspace as ws

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVENT_LOG = REPO_ROOT / "validation" / "event.log.jsonl"
RSS_LIMIT_BYTES = 12 * 1024**3  # OR-001
WRAPPER_ENV = "MATREECOVER_UNDER_WRAPPER"
INPUTS_ENV = "MATREECOVER_INPUTS_FILE"

EXIT_OK = 0
EXIT_ACCEPTANCE = 1
EXIT_RUNPOD_GATE = 2
EXIT_RSS = 3
EXIT_GPU = 4

CANOPY_MASK = "mosaic/canopy_prediction_mask.tif"
BUILDINGS_INPUT = "tables/buildings.geojson"
BOUNDARY_INPUT = "boundary.geojson"


class CliError(RuntimeError):
    def __init__(self, message: str, exit_code: int = EXIT_ACCEPTANCE):
        super().__init__(message)
        self.exit_code = exit_code


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _has_glob(path: str) -> bool:
    return "*" in path or "?" in path


def _gate(required: list[str], workspace: Path) -> None:
    """Input acceptance short-circuit (pending/fail input → exit 1)."""
    manifest = manifest_mod.load_manifest()
    blocked = manifest_mod.required_ready(manifest, required)
    if blocked:
        raise CliError(f"input acceptance gate: {blocked} (pending/fail input short-circuits)")
    inputs_file = os.environ.get(INPUTS_ENV)
    if inputs_file:
        Path(inputs_file).write_text(json.dumps(required), encoding="utf-8")


# --------------------------------------------------------------------------
# Subcommands
# --------------------------------------------------------------------------

@click.command()
def accept() -> int:
    """Re-validate every artifact in artifacts.manifest.json (FR-021)."""
    workspace = ws.workspace_root()
    manifest = manifest_mod.load_manifest()
    for artifact in manifest.get("artifacts", []):
        path = artifact["path"]
        if artifact.get("kind") == "large-file":
            # OR-005 inventory records: governance only, not pipeline artifacts
            continue
        if _has_glob(path):
            # aggregate entry (imagery): metadata checks only, no file hash
            checks = acceptance.run_checks(artifact, workspace)
            artifact["checks"] = {c.criterion: c.status for c in checks}
            artifact["acceptance"] = "pass" if all(c.status == "ok" for c in checks) else "fail"
            continue
        file = workspace / path
        if not file.exists():
            # derived artifact not generated yet (quarantine): stays pending
            if artifact.get("acceptance") != "fail":
                artifact["acceptance"] = "pending"
                artifact["checks"] = {k: "pending" for k in acceptance.CRITERIA}
            continue
        artifact["sha256"] = io.sha256_file(file)
        artifact["size_bytes"] = file.stat().st_size
        checks = acceptance.run_checks(artifact, workspace)
        artifact["checks"] = {c.criterion: c.status for c in checks}
        artifact["acceptance"] = "pass" if all(c.status == "ok" for c in checks) else "fail"
    flipped = manifest_mod.cascade_failures(manifest)
    manifest["generated_at"] = _utcnow()
    manifest_mod.save_manifest(manifest)

    shown = [a for a in manifest.get("artifacts", []) if a.get("kind") != "large-file"]
    for line in manifest_mod.summary_lines({"release_id": manifest.get("release_id"), "artifacts": shown}):
        click.echo(line)
    if flipped:
        click.echo(f"cascade: {', '.join(flipped)} -> pending (FR-023)")
    if manifest_mod.any_failed(manifest):
        click.echo("accept: FAIL — at least one artifact failed acceptance")
        return EXIT_ACCEPTANCE
    click.echo("accept: OK — all artifacts accepted")
    return EXIT_OK


@click.command()
def publish() -> int:
    """Clip accepted layers to the official boundary and emit dist/."""
    try:
        from .publish import publish as publish_bundle

        record = publish_bundle()
    except Exception as exc:  # publish.py raises PublishError(exit 1)
        raise CliError(f"publish refused: {exc}") from exc
    click.echo(f"published {record['release_id']} -> dist/ (buildings={record['buildings']}, trees={record['trees']})")
    return EXIT_OK


@click.command()
def values() -> int:
    """Compute per-building 60 m values from the accepted canopy mask (FR-005)."""
    from . import boundary as boundary_mod
    from . import buildings as buildings_mod
    from . import values as values_mod

    workspace = ws.workspace_root()
    _gate([CANOPY_MASK, BUILDINGS_INPUT], workspace)
    boundary = boundary_mod.load_boundary(workspace / BOUNDARY_INPUT)
    buffered = boundary_mod.load_buffered(workspace / BOUNDARY_INPUT)
    buildings = buildings_mod.load_buildings(workspace / BUILDINGS_INPUT)
    selected = buildings_mod.select_in_buffer(buildings, buffered["geometry"])
    click.echo(f"values: {len(selected)} buildings selected in buffered boundary")
    features = values_mod.compute_building_values(
        workspace / CANOPY_MASK,
        selected,
        workspace / "buildings.geojson",
        boundary["geometry"],
    )
    click.echo(f"values: wrote {len(features)} features to {workspace / 'buildings.geojson'}")
    return EXIT_OK


@click.command()
def runpod_infer() -> int:
    """Gated inference on existing weights via RunPod (FR-025/OR-003)."""
    from .canopy import MODEL_ID, STOP_MESSAGE

    endpoint = os.environ.get("MANNHEIM_RUNPOD_ENDPOINT", "").strip()
    if not endpoint:
        click.echo(STOP_MESSAGE, err=True)
        return EXIT_RUNPOD_GATE
    workspace = ws.workspace_root()
    _gate([BOUNDARY_INPUT], workspace)
    tiles = sorted(str(p.relative_to(workspace)) for p in (workspace / "mosaic" / "extract").glob("dop20rgb_*.tif"))
    payload = json.dumps({"model": MODEL_ID, "inputs": tiles}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            body = response.read()
    except Exception as exc:
        raise CliError(f"runpod-infer: endpoint request failed: {exc}") from exc
    mask_path = workspace / CANOPY_MASK
    mask_path.write_bytes(body)
    meta = {
        "model": MODEL_ID,
        "crs": "EPSG:25832",
        "ground_sampling_distance_m": 0.2,
        "generated_at": _utcnow(),
        "endpoint": endpoint,
    }
    (workspace / "mosaic" / "canopy_prediction_mask.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    click.echo(f"runpod-infer: wrote {mask_path} + canopy_prediction_mask.json")
    return EXIT_OK


# --------------------------------------------------------------------------
# Wrapper: RSS measurement, event log, exit-code pass-through
# --------------------------------------------------------------------------

def _parse_time_rss(stderr: str) -> int | None:
    for line in stderr.splitlines():
        if "Maximum resident set size" in line and "kbytes" in line:
            try:
                return int(line.split(":")[-1].strip())
            except ValueError:
                return None
    return None


def _time_supports_v(time_bin: str) -> bool:
    try:
        proc = subprocess.run([time_bin, "-v", "/bin/true"], capture_output=True, text=True, timeout=10)
        return "Maximum resident set size" in proc.stderr
    except Exception:
        return False


def _log_event(subcommand: str, rss_bytes: int, gpu_used: bool, exit_code: int, inputs: list[str]) -> None:
    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": _utcnow(),
        "subcommand": subcommand,
        "rss_peak_bytes": rss_bytes,
        "gpu_used": gpu_used,
        "exit_code": exit_code,
        "inputs": inputs,
    }
    with open(EVENT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _run_wrapped(argv: list[str]) -> int:
    subcommand = argv[0] if argv else "?"
    inputs_file = REPO_ROOT / "validation" / f".inputs.{os.getpid()}.json"
    time_report = REPO_ROOT / "validation" / f".time.{os.getpid()}.txt"
    env = dict(os.environ)
    env[WRAPPER_ENV] = "1"
    env[INPUTS_ENV] = str(inputs_file)

    time_bin = shutil.which("time")
    child = [sys.executable, "-m", "src.pipeline.cli", *argv]
    rss_bytes: int | None = None
    if time_bin and _time_supports_v(time_bin):
        proc = subprocess.run(
            [time_bin, "-v", "-o", str(time_report), *child],
            env=env, capture_output=True, text=True,
        )
        if time_report.exists():
            rss_kb = _parse_time_rss(time_report.read_text(encoding="utf-8"))
            if rss_kb is not None:
                rss_bytes = rss_kb * 1024
    else:
        proc = subprocess.run(child, env=env, capture_output=True, text=True)
        rss_bytes = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024

    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    time_report.unlink(missing_ok=True)

    if rss_bytes is None:
        rss_bytes = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024

    inputs: list[str] = []
    if inputs_file.exists():
        try:
            inputs = json.loads(inputs_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            inputs = []
        inputs_file.unlink(missing_ok=True)

    _log_event(subcommand, rss_bytes, False, proc.returncode, inputs)

    if rss_bytes > RSS_LIMIT_BYTES:
        click.echo(f"RSS exceeded 12 GiB ({rss_bytes / (1024**3):.2f} GiB) — aborting (OR-001)", err=True)
        return EXIT_RSS
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if os.environ.get(WRAPPER_ENV) == "1":
        return _dispatch(argv)
    return _run_wrapped(argv)


def _dispatch(argv: list[str]) -> int:
    try:
        result = cli.main(prog_name="tree-cover", args=argv, standalone_mode=False)
    except CliError as exc:
        click.echo(str(exc), err=True)
        return exc.exit_code
    except click.exceptions.ClickException as exc:
        exc.show()
        return exc.exit_code
    if isinstance(result, int):
        return result
    return EXIT_OK


@click.group()
def cli() -> None:
    """Mannheim tree-cover data pipeline."""


cli.add_command(accept)
cli.add_command(publish)
cli.add_command(values)
cli.add_command(runpod_infer)


if __name__ == "__main__":
    sys.exit(main())
