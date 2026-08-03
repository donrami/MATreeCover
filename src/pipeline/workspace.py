"""Mannheim workspace root resolution.

All artifact paths in `artifacts.manifest.json` are relative to this root.
Overridable via the `MANNHEIM_WORKSPACE` environment variable.
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_WORKSPACE = Path("/home/mainuser/Desktop/mannheim/workspace/mannheim")


def workspace_root() -> Path:
    return Path(os.environ.get("MANNHEIM_WORKSPACE", str(DEFAULT_WORKSPACE)))
