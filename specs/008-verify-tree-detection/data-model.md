# Data Model: Verify Tree Detection Quality

Date: 2026-08-05. Entities, fields, and validation rules for the
verification feature. Requirements map to the spec
([spec.md](spec.md), FR-001…FR-010) and the contracts
([contracts/](contracts/)).

## Entities

### Stadtteil (district)

The administrative district a patch belongs to. Source: official GDI-MA
Stadtteil boundaries, committed at `verification/stadtteile.geojson`
(see [research.md](research.md) R-2).

| Field | Type | Notes |
|-------|------|-------|
| code | string (3 digits) | Official Stadtteil code (010–174) |
| name | string | Official Stadtteil name |
| geometry | polygon, EPSG:25832 | Boundary; must tile the city without gaps |

Validation: 38 features; every patch center lies inside exactly one
district (point-in-polygon over the layer); districts with buildings
must be present in the sample (FR-004).

### Building

Sampling-frame unit. Source: `tables/buildings.geojson` in the workspace
(EPSG:25832, read-only).

| Field | Type | Notes |
|-------|------|-------|
| id | string | `b-…` (existing) |
| geometry | polygon, EPSG:25832 | Used only for the centroid |
| value | float 0–100 | 60-m tree-cover % (`value` property, existing) |
| has_value | bool | False → building excluded from the frame |

Validation: buildings with `has_value = False` are excluded from the
sampling frame; a centroid must fall inside its own district.

### Patch

One review window in the sample. Record in
`verification/sample.jsonl` (contract: [verify-sample.md](contracts/verify-sample.md)).

| Field | Type | Notes |
|-------|------|-------|
| patch_id | string | Stable id, e.g. `p001`…`p100` |
| seed | int | Fixed seed used for this run |
| district_code | string | Stratum 1 |
| district_name | string | Human-readable |
| value_band | string | `0-10` \| `10-30` \| `30-100` (Stratum 2) |
| center_easting | float | EPSG:25832, building centroid |
| center_northing | float | EPSG:25832 |
| building_id | string | The sampled building |
| resampled | bool | True if the original draw fell outside imagery |
| degeneracy | string \| null | `no-imagery` \| `empty-mask` \| `full-mask` \| null (FR-008) |

Validation: exactly 100 records; patch_ids unique; every district with
buildings present (≥ 2 records); band counts match the documented
allocation; re-running with the same seed reproduces the file
byte-identically (FR-004); points outside the imagery extent are flagged
`resampled` or `no-imagery`, never silently dropped.

### Rating

Owner's judgment for one patch. Record in
`verification/ratings.jsonl` (contract: [verify-ratings.md](contracts/verify-ratings.md)).

| Field | Type | Notes |
|-------|------|-------|
| patch_id | string | Must reference a sample record (FK) |
| district_code | string | Copied from the patch |
| district_name | string | Copied from the patch |
| value_band | string | Copied from the patch |
| rating | enum | `correct` \| `over` \| `under` (FR-002) |
| note | string | What was seen; free text |
| ts | datetime (ISO 8601) | When the rating was recorded |

Validation: one rating per patch_id; every patch in the sample has
exactly one rating before the report is generated; rating values are
exactly the three documented categories (FR-002); schema validated by
test before report generation.

### Verification Report

Generated deliverable at `verification/report.md` (contract:
[verify-report.md](contracts/verify-report.md)).

| Section | Content | Source |
|---------|---------|--------|
| Method | Sample size, seed, strata, criteria, date | Generated from sample + constants |
| Overall findings | Rating counts and shares city-wide | Generated from ratings |
| Per-district findings | n, rating distribution, trust assessment, flags | Generated from ratings |
| Comparison | Model author's cross-city warning vs. Mannheim findings | Owner notes (`verification/notes.md`) |
| Limitations | Degenerate patches, small samples, boundary areas, single-inspector uncertainty, re-inspection divergence | Owner notes + generated degeneracy summary (FR-008) |

Validation: every district with buildings appears in the district table
(FR-003); districts with < 50 % `correct` are flagged (contract rule);
no number in the report diverges from the ratings file (generated, not
hand-edited); disclosure list non-empty.

## State transitions

```text
sample.jsonl ──verify-render──▶ patches/*.png (gitignored)
sample.jsonl + patches ──owner inspects──▶ ratings.jsonl
ratings.jsonl + notes.md ──verify-report──▶ report.md
```

- `verify-sample` is idempotent for a fixed seed (regenerating the file
  must not change it).
- `verify-render` is idempotent (overwrites PNGs deterministically).
- `verify-report` fails validation (exit 1) if any sample patch is
  missing a rating.
- The published map/site has no state in this model — FR-005/FR-010
  forbid any write to published artifacts.
