"""Canopy model contract (FR-024/FR-025, OR-003).

The local pipeline never invokes the model: `REQUIRES_RUNPOD = True`.
Inference with the existing `deepLabV3plus-resnet34` weights runs only on
owner-supplied RunPod capacity via `runpod-infer`, which refuses with
exit 2 when `MANNHEIM_RUNPOD_ENDPOINT` is unset (STOP_MESSAGE). There is
no local inference code path at all, so no local-GPU exit code is defined
(`contracts/cli.md` lists only reachable codes 0-3).
"""

from __future__ import annotations

REQUIRES_RUNPOD = True
MODEL_ID = "deepLabV3plus-resnet34"
STOP_MESSAGE = "STOP — request RunPod capacity"
