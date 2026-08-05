"""Mannheim workspace root resolution.

All artifact paths in `artifacts.manifest.json` are relative to this root.
Overridable via the `MANNHEIM_WORKSPACE` environment variable.
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_WORKSPACE = Path(__file__).resolve().parent.parent.parent / "data/archive/workspace"


def workspace_root() -> Path:
    return Path(os.environ.get("MANNHEIM_WORKSPACE", str(DEFAULT_WORKSPACE)))
