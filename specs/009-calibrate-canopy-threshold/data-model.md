# Data Model: Calibrate Canopy Detection Threshold

Date: 2026-08-05. Entities and validation for the calibration feature;
requirements map to [spec.md](spec.md) and the 008 data model (sample,
ratings, report are reused unchanged).

## Entities

### Candidate Mask

A binary canopy mask from the same model and tiles at a threshold ≠ 0.5.

| Field | Type | Notes |
|-------|------|-------|
| path | string | Workspace-relative, e.g. `mosaic/canopy_prediction_mask_t060.tif` |
| threshold | float | From the companion metadata JSON; MUST match the requested threshold (FR-008) |
| crs / gsd | EPSG:25832, 0.2 m | MUST match the published mask |
| coverage | full | MUST cover the same tiles as the published mask |

Validation: metadata JSON exists next to the mask, records
`threshold` = requested value; otherwise the mask is rejected.

### Re-Verification Ratings

Per-patch ratings per candidate, same schema as 008
(`contracts/verify-ratings.md`), stored as
`verification/ratings_t060.jsonl`, `verification/ratings_t065.jsonl`.
Fields: patch_id, district_code, district_name, value_band, rating,
note, ts. Validation: identical to 008 (one rating per patch, three
rating values, no rating for no-imagery patches).

### Value Delta

Per-building comparison between candidate values and published values.

| Field | Type | Notes |
|-------|------|-------|
| building_id | string | Join key with `buildings.geojson` |
| value_published | float | Published 60-m value (%) |
| value_candidate | float | Same rule, candidate mask |
| delta | float | candidate − published |
| district_code / name | string | For district aggregation |

Aggregates: share of buildings with |delta| > 0.5 pp, mean |delta|,
per-district mean delta, city mean shift, district ranking change
(Spearman correlation of district means).

Validation: every building with a published value appears exactly once;
delta = value_candidate − value_published (no other formula).

### Release Decision

Recorded in `verification/report.md` (008) as a calibration section:
chosen candidate (or "keep published"), the FR-004 numbers, the value
delta summary, and the owner's decision with date. No other state.

## State transitions

```text
pod inference (--threshold 0.6/0.65) ──▶ candidate masks + metadata
candidate mask ──verify-render (mask param)──▶ patches_t0XX/ + ratings_t0XX.jsonl
candidate mask + metadata ──verify-value-delta──▶ value-delta_t0XX.md
ratings + deltas ──owner──▶ release decision (report section)
decision = publish ──▶ trees → pmtiles → accept → publish → deploy (existing path)
```

- Candidate masks are immutable once metadata is written.
- Ratings and deltas are per-candidate and never mixed.
- The published map has no state in this model until a release decision
  is executed; the existing pipeline owns that transition.
