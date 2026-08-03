#!/usr/bin/env python3
"""OR-005 governance check (`make check-or005`).

Asserts:
1. No `*.tif`, `*.pmtiles`, or `*.geojson` larger than 50 MiB is tracked in git.
2. Every file larger than 50 MiB under the mannheim workspace is recorded in
   `artifacts.manifest.json` with path, size_bytes, sha256, and source.

Exit 0 on compliance, 1 otherwise.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

THRESHOLD = 50 * 1024 * 1024  # 50 MiB
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "artifacts.manifest.json"


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.splitlines() if line]


def violations_tracked(tracked: list[str]) -> list[str]:
    bad: list[str] = []
    for rel in tracked:
        if rel.endswith((".tif", ".pmtiles")):
            bad.append(rel)
            continue
        if rel.endswith(".geojson"):
            size = (ROOT / rel).stat().st_size
            if size > THRESHOLD:
                bad.append(f"{rel} ({size} bytes)")
    return bad


def workspace_large_files(workspace: Path) -> list[Path]:
    large: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(workspace):
        if any(part.startswith(".") for part in Path(dirpath).relative_to(workspace).parts):
            continue
        for name in filenames:
            p = Path(dirpath) / name
            try:
                if p.stat().st_size > THRESHOLD:
                    large.append(p)
            except OSError:
                continue
    return large


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not MANIFEST.exists():
        print("FAIL: artifacts.manifest.json missing at repo root")
        return 1
    manifest = json.loads(MANIFEST.read_text())
    artifacts = manifest.get("artifacts", [])
    by_path = {a["path"]: a for a in artifacts}

    fail = 0

    tracked = tracked_files()
    bad_tracked = violations_tracked(tracked)
    if bad_tracked:
        fail = 1
        print("FAIL: large data files tracked in git:")
        for b in bad_tracked:
            print(f"  {b}")
    else:
        print("OK: no *.tif / *.pmtiles / >50 MiB *.geojson tracked in git")

    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    scan_failed = False
    if workspace is not None and workspace.is_dir():
        for p in workspace_large_files(workspace):
            rel = p.relative_to(workspace).as_posix()
            entry = by_path.get(rel)
            if entry is None:
                scan_failed = True
                fail = 1
                print(f"FAIL: {rel} (>50 MiB) not recorded in artifacts.manifest.json")
                continue
            missing = [k for k in ("path", "size_bytes", "sha256", "source") if not entry.get(k)]
            if missing:
                scan_failed = True
                fail = 1
                print(f"FAIL: {rel} missing manifest fields: {', '.join(missing)}")
                continue
            if entry["size_bytes"] != p.stat().st_size:
                print(f"WARN: {rel} size changed (manifest {entry['size_bytes']}, disk {p.stat().st_size})")
        if not scan_failed:
            print("OK: every >50 MiB workspace file recorded in manifest (path, size, sha256, source)")
    else:
        print("SKIP: workspace scan (workspace arg missing or not a directory)")

    if fail:
        print("OR-005 CHECK FAILED")
        return 1
    print("OR-005 CHECK OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
