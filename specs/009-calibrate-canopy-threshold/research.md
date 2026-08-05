# Research: Calibrate Canopy Detection Threshold

Research date: 2026-08-05. Decisions are codebase-grounded (read of
`src/endpoint/server.py`, `src/pipeline/cli.py`, `verify.py`, 008
contracts and report) plus the 008 verification evidence. No external
unknowns: the calibration path, candidates, acceptance rules, and
release handling were decided with the owner before planning.

## R-1 Threshold parameterization: payload override, default 0.5

**Decision**: `src/endpoint/server.py` reads an optional `threshold`
field from the inference request payload; absent → `THRESHOLD = 0.5`
unchanged. The threshold is applied at the sigmoid comparison
(`server.py:256`, `probs > threshold`), recorded in the mask metadata
(`server.py:272`, already writes `"threshold": THRESHOLD`).

**Rationale**:
- Backward compatible: the 008 pod flow sends `{"model", "inputs"}`
  without threshold → identical behavior, identical masks.
- Metadata already records the threshold — the trust boundary (FR-008)
  works without schema changes.
- The threshold is a per-run decision, not a deployment config: a
  request field is the smallest surface.

**Alternatives considered**:
- Env var: rejected — the endpoint is deployed via `runpod-deploy.sh`
  once; per-request control avoids redeploys between candidates.
- CLI-side post-processing of probabilities: rejected — the endpoint
  returns the already-thresholded mask; the pod-side threshold is the
  only place the decision can be made without re-serving scores.

## R-2 Two candidates: 0.6 and 0.65, same run cost

**Decision**: Exactly two candidate masks at sigmoid thresholds 0.6 and
0.65, from the same weights and tiles, via the existing gated
`runpod-infer` flow with a new `--threshold` option and a `--out` path
so two masks can coexist in the workspace
(`mosaic/canopy_prediction_mask_t060.tif`, `_t065.tif`).

**Rationale**:
- Evidence (008): false positives (roofs, lawns, ballast) are
  low-confidence; real crowns score high — 0.6/0.65 sit where the FP
  mass is expected to drop without touching true positives. 0.7 stays
  in reserve (spec: adjust only with owner approval).
- Two candidates bracket the decision; one candidate would give no
  gradient to judge sensitivity.
- `runpod-infer` already streams the mask from the endpoint; only the
  output path and the payload gain options.

**Alternatives considered**:
- Score-threshold sweep locally: rejected — the endpoint returns only
  the thresholded mask, not per-pixel scores; a sweep would need
  endpoint changes to serve probabilities (bigger surface).
- Single candidate 0.6: rejected — no sensitivity evidence.

## R-3 Re-verification: same 100 patches, per-candidate ratings

**Decision**: `verify.render_patches` gains a mask-path parameter
(default: the current `mosaic/canopy_prediction_mask.tif`); the owner
re-rates the same 100 patches per candidate using the 008 criteria and
schema. Acceptance per FR-004: over share < 39 % and ≥ 90 % of the 59
previously correct patches remain correct.

**Rationale**:
- The sample is reproducible (seed 20260805) and already rated at 0.5:
  re-rendering the same centers with a different mask is the direct
  before/after comparison — no new sampling bias.
- The correct-retention rule is the guard against the Bamberg failure
  mode (aggressive thresholding kills low-contrast real crowns).
- Ratings go into the 008 schema (`verification/ratings_t060.jsonl`,
  `ratings_t065.jsonl`) so the report machinery is reused.

## R-4 Value delta: reuse `values`, compare per building

**Decision**: New `verify-value-delta` subcommand: run
`values.compute_building_values` on each candidate mask (same boundary
and 60-m rule), load the published `buildings.geojson` values, and emit
`verification/value-delta_t060.md` / `_t065.md`: per-building deltas,
share of buildings changing value, per-district movement, city mean
shift. The report (008) gains a calibration section with the decision.

**Rationale**:
- `values` already implements the exact published rule (fftconvolve
  60-m disc, boundary clipping) — reusing it guarantees the comparison
  isolates the mask change, nothing else.
- The delta summary is the decision input (FR-006): the owner sees how
  many buildings move, where, and whether district rankings change.

**Alternatives considered**:
- A separate reimplementation of the 60-m rule: rejected — divergent
  numerics would muddy the comparison.
- Delta-only statistics without per-building artifacts: rejected —
  the per-building file is the reproducible evidence.

## R-5 Release: existing path only, no site changes

**Decision**: A release = `trees` → pmtiles → `accept` → `publish` →
`scripts/deploy-cf.sh`, exactly as documented in DEVELOPMENT.md. No
site code, style, or legend changes (FR-007). The published map stays
live until the decision is executed.

**Rationale**:
- The 008 feature already proved the zero-change discipline; the
  release path is documented and exercised (deploy scripts, FR-013
  gates).
- FR-007 is a scope boundary: calibration must not become a frontend
  change.

## R-6 Metadata as trust boundary

**Decision**: A candidate mask is accepted only if its companion
metadata JSON records the expected threshold and full coverage
(FR-008). The `runpod-infer` flow already writes the metadata JSON;
`verify-value-delta` verifies it before computing.

**Rationale**: the whole comparison depends on which threshold produced
the mask; a mislabeled mask would silently corrupt the evidence.
