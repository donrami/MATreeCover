# Low-Zoom Simplification Contract — Performance Fixes (spec 014)

Applies to FR-004, FR-005, FR-006, US2, SC-001, SC-006.

## Flags

The Makefile `pmtiles-buildings` target gains two flags:

```text
-S 10 --simplify-only-low-zooms
```

Semantics (tippecanoe 2.80.0): `-S 10` multiplies the simplification tolerance by 10. `--simplify-only-low-zooms` keeps the maximum zoom (18) untouched. All other flags stay unchanged, including `--drop-densest-as-needed`.

## Why this is safe

- Feature presence is controlled by drop-densest-as-needed. It is unchanged, so the same buildings appear at every zoom.
- Only vertex density changes below z18. At city scale (z10-z12) the deviation is sub-pixel.
- Building properties (value, has_value) pass through tippecanoe untouched.

## Parity gates (all must pass)

1. Feature-count parity: for every tile at z10-z13, the feature count in the rebuilt archive equals the count in the current archive. Implemented with the pmtiles Python library (project dependency, v3+).
2. Property parity: sample tile features at z10-z13. value and has_value match the current archive.
3. Screenshot parity: render the initial view and fixed cameras at z10, z12, z14, z16, z18 with the current and rebuilt archives. Pixel difference below the SC-005 image-sanity threshold. No missing, added, or degenerate buildings.
4. Image sanity: the repo's SC-005 image sanity suite passes.
5. No value drift: the source geojson is untouched, only re-tiled. City mean and per-building values cannot change. Verify with the existing recalculation test.

## Tuning loop

Target: TBT under 1.5 s on the Lighthouse mobile profile (SC-001).

1. Build with -S 10. Run the parity gates and the Lighthouse mobile profile.
2. If parity fails, lower the scale (10 to 5) and repeat. The parity gates are the hard constraint.
3. If TBT still exceeds 1.5 s at the highest passing scale, extend the initial-view optimization (see plan) and re-measure. Report honestly if the target needs adjustment.

## Rollback

The workspace keeps the current and rebuilt archives. The Makefile rebuild is the only mutation. A failed gate rolls back to the current archive by re-running the build with the original flags.
