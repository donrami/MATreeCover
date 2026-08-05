---
description: "Task list for calibrate-canopy-threshold feature implementation"
---

# Tasks: Calibrate Canopy Detection Threshold

**Input**: Design documents `specs/009-calibrate-canopy-threshold/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: included — the plan specifies pytest additions for the mask-path
parameter and the value-delta computation. Write tests first, see them fail.
**Organization**: tasks grouped by user story; the pod runs are the only
blocked step (OR-003) — everything local is implementable now.

## Phase 1: Local Implementation (no pod needed)

**Purpose**: parameterize the pipeline so candidate masks can flow through.

- [ ] T001 [P] Add `threshold` parameter to the inference request in `src/endpoint/server.py` (payload override, default 0.5 preserved; applied at the sigmoid comparison; recorded in mask metadata) + test in `tests/endpoint/test_threshold.py` (request without threshold behaves as before; with threshold uses it and metadata records it)
- [ ] T002 [P] Add mask-path parameter to `render_patches()` in `src/pipeline/verify.py` (default current mask path) + test: same sample rendered against two different synthetic masks produces different overlays
- [ ] T003 [P] Implement `verify-value-delta` in `src/pipeline/verify.py` + `cli.py`: accepts `--mask`, validates metadata (threshold, crs, gsd, extent vs published), computes values via the existing `values.compute_building_values`, joins per building, writes `verification/value-delta_t0XX.md` + `.csv` (per-contract aggregates) + tests on synthetic masks (coverage, delta formula, trust-check aborts)
- [ ] T004 [P] Add `--threshold` and `--out` options to `runpod_infer` in `src/pipeline/cli.py` (threshold → payload; out → mask + metadata paths, default current behavior)

**Checkpoint**: local tooling green (`pytest tests/`); commit slice.

## Phase 2: User Story 1 - Candidate Masks (Priority: P1) ⚠️ BLOCKED ON POD

**Goal**: two masks at 0.6 / 0.65 from the same weights and tiles.

- [ ] T005 [US1] Run pod inference at threshold 0.6 → `mosaic/canopy_prediction_mask_t060.tif` + metadata (owner pod, `runpod-infer --threshold 0.6 --out …`)
- [ ] T006 [US1] Run pod inference at threshold 0.65 → `mosaic/canopy_prediction_mask_t065.tif` + metadata

**Independent Test**: both masks exist with metadata thresholds 0.6/0.65, full coverage (quickstart Scenario 3).

## Phase 3: User Story 2 - Re-Verification (Priority: P1)

**Goal**: per-candidate ratings on the same 100 patches; FR-004 acceptance.

- [ ] T007 [US2] Re-render the 100 patches per candidate (`verify-render --mask …`, outputs to `verification/patches_t060/`, `_t065/`)
- [ ] T008 [US2] Owner rates `verification/ratings_t060.jsonl` and `ratings_t065.jsonl` (008 criteria; skeleton generated from the sample)
- [ ] T009 [US2] Evaluate FR-004: over share < 39 % and ≥ 90 % of the 59 previously correct patches still correct; record numbers per candidate

**Independent Test**: ratings exist per candidate; FR-004 holds for at least one (quickstart Scenario 4).

## Phase 4: User Story 3 - Value Impact and Decision (Priority: P2)

**Goal**: per-building deltas and a recorded release decision.

- [ ] T010 [US3] Run `verify-value-delta --mask …` for both candidates → `verification/value-delta_t060.md`, `_t065.md`
- [ ] T011 [US3] Owner records the release decision in `verification/report.md` (publish candidate / keep published / investigate) with the decisive numbers
- [ ] T012 [US3] If publishing: `trees` → pmtiles → `accept` → `publish` → `scripts/deploy-cf.sh` (existing path only)
- [ ] T013 Update the 008 report with the calibration section (candidates, re-verification, deltas, decision); run quickstart Scenarios 1–6; zero-change gate (`pytest tests/`, `make check-public`, no site diffs); commit milestone

**Independent Test**: delta summaries + decision recorded (quickstart Scenarios 5–6).

## Dependencies & Execution Order

- Phase 1: four parallelizable tasks (T001–T004), different files — then commit.
- Phase 2: depends on T004 + pod; **pod notification point**.
- Phase 3: depends on Phase 2 (masks).
- Phase 4: depends on Phase 3 (ratings) for the decision; deltas only need masks.
- T013 is the final validation + commit.

## Implementation Strategy

1. Local slice now: T001–T004 + tests → commit (incremental, testable without GPU).
2. Stop at the pod gate → owner spawns pod → T005/T006.
3. T007–T009 (re-verification, human rating), T010–T013 (deltas, decision, release).
4. Release only on an explicit owner decision (FR-006, no auto-release).
