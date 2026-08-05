# Contract: Verify Ratings

Scope: the inspection criteria the owner applies and the
`verification/ratings.jsonl` schema. Requirements: FR-002, FR-008;
success criteria SC-002, SC-008. See [../data-model.md](../data-model.md)
and [verify-sample.md](verify-sample.md).

## Rating criteria

For each rendered patch (`verification/patches/<patch_id>.png`), the
owner compares the mask overlay against the true-color imagery and
assigns exactly one rating:

| Rating | Meaning | Decide this when |
|--------|---------|-------------------|
| `correct` | The detected canopy matches the visible tree canopy | Detected areas are trees; missed canopy is negligible or within shadow/occlusion that a human also cannot resolve |
| `over` | Over-detection dominates | The mask flags substantial areas that are clearly not tree canopy (e.g. roofs, shadows, dark fields, water, cars) |
| `under` | Under-detection dominates | The mask misses substantial visible tree canopy (e.g. bright or low-contrast trees, single trees on grassland) |

Rules:

- The rating describes the **dominant** failure if both over- and
  under-detection occur; the `note` documents what was seen.
- A patch with neither substantial failure is `correct`, even if
  imperfect in detail.
- `no-imagery` patches (degeneracy `no-imagery`) are **not rated**; they
  are excluded from rating counts and disclosed in the report instead
  (FR-008). `empty-mask` and `full-mask` patches are rated normally:
  they are legitimate detection outcomes to judge.
- The owner re-inspects every 10th patch (by patch_id order) after
  completing the first pass. Divergent re-ratings are resolved to one
  final rating; the divergence itself is recorded in the report
  (FR-008), not erased.

## `verification/ratings.jsonl` schema

One JSON object per line, UTF-8, one record per rated patch:

```json
{
  "patch_id": "p001",
  "district_code": "030",
  "district_name": "Neckarstadt-West",
  "value_band": "0-10",
  "rating": "correct",
  "note": "Two large trees match the overlay; small shadow gap at the south edge.",
  "ts": "2026-08-06T18:30:00+00:00"
}
```

| Field | Rule |
|-------|------|
| patch_id | Must exist in `sample.jsonl`; exactly one rating per patch |
| district_code / district_name / value_band | Copied verbatim from the sample record |
| rating | Exactly `correct`, `over`, or `under` |
| note | Free text; may be empty |
| ts | ISO 8601 with timezone |

## Invariants (tested)

- Every non-`no-imagery` sample patch has exactly one rating before
  `verify-report` runs (report generation fails validation otherwise).
- Rating values are exactly the three documented categories.
- No rating exists for a patch with degeneracy `no-imagery`.
- `verify-report` refuses to run on an invalid ratings file (schema
  error, missing patch, unknown rating → exit 1).
