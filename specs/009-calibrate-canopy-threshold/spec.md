# Feature Specification: Calibrate Canopy Detection Threshold

**Feature Branch**: `009-calibrate-canopy-threshold`
**Created**: 2026-08-05
**Status**: Draft
**Input**: The verification (feature 008) found dominating over-detection in 39 % of the sampled patches — roofs, lawns, fields, and railway ballast detected as tree canopy — systematically inflating the per-building 60-m tree-cover values in the affected districts (Sandhofen, Feudenheim flagged; dense districts clean). Decision: calibration path — raise the detection threshold, re-verify on the same sample, quantify the value impact, and decide whether to re-release the map.

## Scope

### Goal

Reduce the false-positive canopy detection by calibrating the sigmoid threshold, with evidence that the fix works (over-detection drops, real trees are not lost) and a quantified statement of how much the published building values change.

### In Scope

- Make the detection threshold configurable end to end (inference request → mask metadata), keeping the current 0.5 behavior as the default.
- Two candidate masks at thresholds 0.6 and 0.65, produced from the same weights and tiles (one owner-supplied RunPod session each).
- Re-verification on the same reproducible 100-patch sample: overlaid review PNGs per candidate, ratings per candidate, with two acceptance rules — the previously over-rated patches improve, and the previously correct patches do not flip to under-detection.
- A per-building value comparison between each candidate mask and the published values, summarized per district.
- A recorded release decision (publish a candidate, or keep the published map), and — if released — a re-run of the existing publish/deploy path with no site-code changes.
- Verification report (008) updated with the calibration results.

### Out of Scope

- Retraining, fine-tuning, or replacing the model.
- Thresholds outside the 0.5–0.7 range or more than two candidates (adjust only if the evidence demands it, by owner decision).
- Changes to the site, the map style, the legend, or any frontend behavior.
- Changes to building data, district data, or the sample design.
- Any change to the published map without a recorded release decision.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Owner Produces Candidate Masks (Priority: P1)

The owner runs the existing inference on the pod twice — once per candidate threshold — and gets two masks whose metadata records the threshold used.

**Why priority**: Without the masks nothing downstream can happen; this is the only GPU step.

**Independent Test**: Two mask files exist with metadata naming thresholds 0.6 and 0.65; each is a full-coverage binary canopy mask in EPSG:25832 at 0.2 m.

**Acceptance Scenarios**:

1. **Given** the pod endpoint is reachable, **When** the owner requests inference at threshold 0.6, **Then** a complete mask is produced and its metadata records `threshold: 0.6`.
2. **Given** the pod endpoint is reachable, **When** the owner requests inference at threshold 0.65, **Then** a complete mask is produced and its metadata records `threshold: 0.65`.
3. **Given** the current 0.5 behavior, **When** the endpoint receives no threshold, **Then** it behaves exactly as before (threshold 0.5, metadata records 0.5).

### User Story 2 - Owner Re-Verifies Detection Quality (Priority: P1)

With each candidate mask, the owner re-renders the same 100 review patches and re-rates them. The evidence must show the over-detection dropped and the true detections survived.

**Why priority**: This is the whole point of calibrating — a threshold that only moves false positives is worthless; one that kills real crowns is worse than the status quo.

**Independent Test**: Ratings exist for both candidate masks on the same 100 patches; the over-rate is below the current 39 % and at least 90 % of the previously correct patches remain correct.

**Acceptance Scenarios**:

1. **Given** a candidate mask, **When** the owner re-renders the 100 patches, **Then** the patches are identical in location and size to the 008 sample (same seed, same centers).
2. **Given** a candidate mask, **When** the owner re-rates the patches, **Then** the share of `over` ratings is lower than the 008 baseline (39 %).
3. **Given** the previously correct patches, **When** the owner re-rates them at the candidate threshold, **Then** at least 90 % of them remain `correct` (no meaningful under-detection introduced).
4. **Given** the re-ratings, **When** the owner compares candidates, **Then** the better candidate is identifiable (highest correct share with the largest over-rate reduction).

### User Story 3 - Owner Quantifies the Value Impact and Decides (Priority: P2)

The owner computes per-building values from each candidate mask, compares them with the published values, and records a decision: publish a candidate, keep the map as-is, or investigate further.

**Why priority**: The map's message is per-building values and district differences; the calibration only matters if it changes them meaningfully, and the decision must be documented either way.

**Independent Test**: A value-delta summary exists for each candidate (per-building deltas, district summary, city mean), and the decision is recorded in the verification report.

**Acceptance Scenarios**:

1. **Given** a candidate mask, **When** the owner computes building values, **Then** every building that had a value gets a candidate value (same boundary and 60-m rule).
2. **Given** the candidate values, **When** the owner reviews the comparison, **Then** it reports per-building deltas, the share of buildings changing value, per-district movement, and the city mean shift.
3. **Given** the comparison, **When** the owner decides, **Then** the decision is recorded in the verification report with the evidence behind it (publish / keep / investigate).
4. **Given** a decision to publish, **When** the owner releases, **Then** the existing publish and deploy path is used and no site code changes.

### Edge Cases

- A candidate threshold eliminates so many false positives that whole districts become nearly tree-free — the value deltas must show whether this is correction or overcorrection (check against the imagery in re-verification).
- Under-detection regression: if a previously correct patch flips to `under`, the threshold is too aggressive for that patch type; the report records it.
- The pod run fails midway (endpoint timeout, disk): the incomplete mask is discarded, no partial artifact is accepted.
- A candidate mask produces no meaningful value change: the decision is "keep published values" with the evidence documented.
- Metadata missing/wrong threshold: the mask is not accepted for comparison (trust boundary).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The detection threshold MUST be configurable in the inference request, defaulting to 0.5 when not provided; the mask metadata MUST record the threshold used.
- **FR-002**: The owner MUST be able to produce a candidate mask for each chosen threshold from the same weights and tiles, without retraining.
- **FR-003**: Each candidate mask MUST be re-verified on the same 100-patch sample as feature 008 (same seed and centers), with per-candidate ratings.
- **FR-004**: A candidate MUST be considered an improvement only if the `over` share is below the 008 baseline (39 %) AND at least 90 % of the previously `correct` patches remain `correct`.
- **FR-005**: The value comparison MUST cover every building with a published value, report per-building deltas, the share of buildings changing value, per-district movement, and the city mean shift.
- **FR-006**: The release decision (publish a candidate / keep published values / investigate) MUST be recorded in the verification report with the evidence behind it.
- **FR-007**: A release MUST use the existing publish and deploy path; no site code, style, legend, or frontend changes.
- **FR-008**: A mask without complete metadata or full coverage MUST NOT be accepted for comparison.
- **FR-009**: The verification report (feature 008) MUST be updated with the calibration results: candidates, re-verification numbers, value deltas, and the decision.

### Key Entities *(include if feature involves data)*

- **Candidate Mask**: a binary canopy mask from the same model and tiles at a threshold other than 0.5; identified by its threshold in metadata; full coverage EPSG:25832 at 0.2 m.
- **Re-Verification Ratings**: per-patch ratings (correct / over / under) per candidate on the 008 sample, with the same schema.
- **Value Delta**: per-building difference between candidate values and published values, plus district and city aggregates.
- **Release Decision**: the recorded choice (publish / keep / investigate) with the evidence that led to it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Two candidate masks exist with metadata thresholds 0.6 and 0.65, full coverage, EPSG:25832, 0.2 m.
- **SC-002**: Re-verification ratings exist for both candidates on the same 100 patches as 008.
- **SC-003**: At least one candidate achieves an `over` share below 39 % with ≥ 90 % of the previously correct patches still correct (FR-004).
- **SC-004**: The value comparison covers 100 % of buildings with published values; the city mean shift and per-district movement are reported.
- **SC-005**: The release decision is recorded in the report; if a release happens, it uses the existing path and the site is byte-identical otherwise.
- **SC-006**: No regression: existing pytest suites stay green; no changes to site code, style, legend, or sample design.
- **SC-007**: The 008 report documents thresholds, before/after re-verification numbers, value deltas, and the decision.

## Assumptions

- Candidate thresholds 0.6 and 0.65, per the 008 evidence (false positives are low-confidence; real crowns score higher). Adjust only with owner approval.
- The pod session is owner-supplied and reused from 008 (RunPod, same deploy script and tunnel).
- Re-rating the full 100-patch sample per candidate is the verification standard; it is the same human step as 008.
- Release is not automatic: the owner decides after seeing the value deltas (consistent with Q3 of 008 — no gating).
- The published map stays live until a release decision is made and executed.
- If neither candidate meets FR-004, the decision is "keep published values" and the evidence is recorded.
- Values are computed with the existing 60-m fftconvolve rule; only the mask input changes.

## Dependencies Evidence

- Threshold currently hardcoded: `src/endpoint/server.py:41` (`THRESHOLD = 0.5`), recorded in mask metadata (`server.py:272`).
- Inference CLI: `runpod-infer` in `src/pipeline/cli.py` (gated, OR-003; writes `mosaic/canopy_prediction_mask.tif` + metadata JSON).
- Re-verification: feature 008 tooling — `verify-sample` (seed `20260805`), `verify-render` (currently reads the single mask path `mosaic/canopy_prediction_mask.tif`), ratings schema in `contracts/verify-ratings.md` (008).
- Values: `values` subcommand (`values.compute_building_values`, 60-m disc, EPSG:25832; derived `buildings.geojson` in EPSG:4326).
- Release: `make pmtiles-buildings pmtiles-trees`, `accept`, `publish`, `scripts/deploy-cf.sh` (documented in DEVELOPMENT.md); site code untouched (FR-007).
- 008 baseline for acceptance: over 39 %, correct 59 %, under 2 % (verification/report.md, committed).
