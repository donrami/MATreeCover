"""Canopy model contract (FR-024/FR-025, OR-003).

The local pipeline never runs the model: `REQUIRES_RUNPOD = True`.
Inference uses the existing `deepLabV3plus-resnet34` weights only and
runs on owner-supplied RunPod capacity. Any local attempt to invoke the
model raises `LocalGPUError` (CLI exit code 4).
"""

from __future__ import annotations

REQUIRES_RUNPOD = True
MODEL_ID = "deepLabV3plus-resnet34"

STOP_MESSAGE = "STOP — request RunPod capacity"


class LocalGPUError(RuntimeError):
    """OR-003 violation: a local GPU/model invocation was attempted."""


def refuse_local_inference() -> None:
    raise LocalGPUError(
        f"local inference refused: canopy.py REQUIRES_RUNPOD=true (OR-003). "
        f"{STOP_MESSAGE}"
    )
