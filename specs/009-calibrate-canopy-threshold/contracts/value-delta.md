# Contract: Value Delta

Scope: the per-building value comparison between a candidate mask and
the published values. Requirements: FR-005, FR-006; success criteria
SC-004, SC-005. See [../data-model.md](../data-model.md).

## Inputs

- Candidate mask + accepted metadata (see [candidate-mask.md](candidate-mask.md)).
- Published values: `buildings.geojson` in the workspace (derived,
  EPSG:4326, `value` property) — the same file the map shows.
- City boundary and the 60-m rule exactly as the `values` subcommand
  implements them (fftconvolve disc mean, boundary completeness gate).

## Computation

- Run the existing value computation on the candidate mask (same
  buildings, same boundary, same rule).
- Join per building_id; `delta = value_candidate - value_published`.
- Every building with a published value appears exactly once.

## Output (`verification/value-delta_t0XX.md`)

- Header: candidate mask path, threshold, generated_at, seed/sample ref.
- City-level: mean delta, mean |delta|, share of buildings with
  |delta| > 0.5 percentage points, city mean value before/after.
- District-level table: district | n buildings | mean delta | share
  moved | published mean | candidate mean.
- District-ranking change: Spearman correlation of district means
  (published vs candidate).
- Full per-building table (`verification/value-delta_t0XX.csv`).

## Trust checks

- The metadata threshold MUST equal the requested threshold (else abort).
- Candidate value coverage MUST equal published value coverage (same
  set of buildings with values); mismatch → abort with a message.
- The mask extent MUST match the published mask extent (else abort).

## Decision input (FR-006)

The owner reads the delta summaries for both candidates together with
the re-verification ratings and records the release decision in
`verification/report.md`: candidate published / keep published /
investigate, with date and the decisive numbers.
