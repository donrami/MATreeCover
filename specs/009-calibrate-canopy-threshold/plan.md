# Implementation Plan: Calibrate Canopy Detection Threshold

**Branch**: `009-calibrate-canopy-threshold` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-calibrate-canopy-threshold/spec.md`

## Summary

The 008 verification found dominating over-detection in 39 % of sampled patches (roofs, lawns, fields, railway ballast detected as tree), inflating per-building 60-m values in the affected districts. This feature calibrates the detection threshold: make the threshold configurable end to end, produce two candidate masks (0.6, 0.65) from the same weights on the pod, re-verify on the same 100-patch sample, quantify the per-building value deltas, and record a release decision. No retraining, no frontend changes; a release reuses the existing publish/deploy path.

Local work is fully implementable now: endpoint threshold parameter, render mask-path parameter, a value-delta comparison subcommand, and `runpod-infer --threshold/--out` options — all with tests on synthetic masks. The pod runs (FR-002) are the only gate; everything after them (re-render, re-rate, deltas, decision) is local.

## Technical Context

**Language/Version**: Python ≥ 3.11 (pipeline + endpoint); no frontend change.

**Primary Dependencies**: None new. Existing: torch (endpoint, pod-side), rasterio, numpy, shapely, pyproj, click (pipeline).

**Storage**: Candidate masks in the workspace (`mosaic/canopy_prediction_mask_t060.tif`, `_t065.tif`) — gitignored via `*.tif` (OR-005). Ratings and delta summaries in `verification/`. The 008 sample is reused unchanged (`verification/sample.jsonl`, seed 20260805).

**Testing**: pytest additions in `tests/pipeline/test_verify.py` (mask-path param, delta computation) and a new `tests/endpoint/test_threshold.py` if an endpoint test dir exists — check. Synthetic masks like `test_values_recalc` uses.

**Target Platform**: Linux x86_64, Python 3.11; pod-side is the existing RunPod setup.

**Project Type**: Offline data pipeline (CLI) + one HTTP endpoint (pod-side inference).

**Performance Goals**: Thresholding adds no cost (per-pixel compare during inference). Value delta over ~93k buildings: seconds (fftconvolve-based, as in `values`).

**Constraints**:
- OR-003: no local GPU — the two candidate masks require the owner's RunPod session; local code must not run the model.
- OR-001: RSS ≤ 12 GiB on every pipeline invocation (windowed reads already respected).
- OR-005: masks are `*.tif`, already gitignored; nothing > 50 MiB enters git.
- FR-007: release uses the existing path only; site code byte-identical otherwise.
- FR-004: acceptance rules — over share < 39 % AND ≥ 90 % of previously correct patches stay correct.
- Default threshold 0.5 preserved (backward compatible endpoint + CLI).
- Metadata records the threshold; masks without it are rejected (FR-008).

**Scale/Scope**: 2 candidate masks; 100 re-verified patches per candidate; ~93k building values compared; 1 recorded decision.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No `constitution.md` exists — gates are repo governance (DEVELOPMENT.md) + spec:

| Gate | Requirement | Status (design) |
|------|-------------|-----------------|
| OR-001 | Peak RSS ≤ 12 GiB | PASS — windowed reads; delta computation matches `values` cost |
| OR-003 | No local GPU; inference only via owner RunPod | PASS — pod runs are the only GPU step, gated like 008 |
| OR-005 | No `*.tif`/`*.pmtiles`/>50 MiB tracked | PASS — masks gitignored; evidence files small |
| FR-010 | `make check-public` clean | PASS — no new public-surface content |
| FR-004 | Improvement only if over < 39 % AND correct-retention ≥ 90 % | PASS — enforced in re-verification acceptance |
| FR-007 | Release via existing path, no site changes | PASS — reuses `values/trees/pmtiles/accept/publish/deploy` |

## Project Structure

### Documentation (this feature)

```text
specs/009-calibrate-canopy-threshold/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── README.md
│   ├── candidate-mask.md
│   └── value-delta.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/endpoint/server.py    # THRESHOLD from request payload (default 0.5); metadata records it
src/pipeline/verify.py    # render_patches accepts a mask path parameter
src/pipeline/values.py    # unchanged (compute_building_values already takes the mask path)
src/pipeline/cli.py       # runpod-infer: --threshold + --out options; new verify-value-delta subcommand

tests/pipeline/test_verify.py   # + mask-path param test, value-delta test (synthetic masks)
tests/endpoint/                 # + threshold parameterization test (if the dir exists)
verification/                   # ratings t060/t065, value-delta summaries (evidence, committed)
```

**Structure Decision**: same single-package pattern as 008 — small, targeted parameter changes plus one new subcommand; no new packages.

## Complexity Tracking

No constitution violations. Four small, localized changes; no new abstractions.
