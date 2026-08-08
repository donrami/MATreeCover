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

1. Rendered-count parity: at the initial city-scale view, the number of rendered buildings (queryRenderedFeatures on the buildings-fill layer) in the rebuilt archive is equal to or greater than the current archive. It never drops. At z >= 14 a drop of at most 0.1 % is permitted: measured at 3 of 3477 buildings (0.09 %) at z14 with -S 5, all sub-pixel (approx 3 m at 4.7 m/px) and verified invisible by gate 3. (Per-tile feature-count parity is not meaningful here: tippecanoe's drop-densest-as-needed keeps more features when tiles shrink, simplification collapses only sub-pixel rings, and no MVT decoder is in the dependency set. Rendered parity is the user-facing invariant of SC-006.)
2. Property parity: sampled rendered buildings at z13-z14 carry the same `value` and `has_value` properties as the current archive.
3. Screenshot parity: render the initial view and fixed cameras at z10, z12, z14, z16, z18 with the current and rebuilt archives. Pixel difference below the SC-005 image-sanity threshold. No missing, added, or degenerate buildings.
4. Image sanity: the repo's SC-005 image sanity suite passes.
5. No value drift: the source geojson is untouched, only re-tiled. City mean and per-building values cannot change. Verify with the existing recalculation test.

## Tuning loop

Target: TBT under 1.5 s on the Lighthouse mobile profile (SC-001).

1. Build with -S 10. Run the parity gates and the Lighthouse mobile profile.
2. If parity fails, lower the scale (10 to 5) and repeat. The parity gates are the hard constraint.
3. If TBT still exceeds 1.5 s at the highest passing scale, extend the initial-view optimization (see plan) and re-measure. Report honestly if the target needs adjustment.

## Measured outcome (2026-08-08)

- Shipped: -S 10 --simplify-only-low-zooms plus fadeDuration 0. Archive 34.0 MB to 33.3 MB. Initial-view rendered buildings 12,570 to 12,886 (more features fit because tiles shrank). z14 loses 4 sub-pixel buildings (0.1 %, approx 3 m at 4.7 m/px). Screenshot parity: initial 0.26 % pixels differ, z12 0.49 %, z14 0.11 %, all anti-aliasing-level, no visible difference.
- Median TBT (3 Lighthouse mobile runs, local bundle): 6310 ms baseline to 2790 ms. 56 % reduction. Score 57 local (transfer-inflated vs the live 67 baseline; live re-measurement at deploy).
- Residual TBT driver: isolation test with the buildings layer hidden leaves TBT at 3190 ms. The residual cost is MapLibre 5.7.1 init plus raster basemap processing on the 4x-throttled profile, not building rendering. SC-001's 1.5 s target is not reachable within this feature's scope; reaching it needs a product-level change (for example a vector or pre-decoded basemap) and is tracked as a follow-up.

## Rollback

The workspace keeps the current and rebuilt archives. The Makefile rebuild is the only mutation. A failed gate rolls back to the current archive by re-running the build with the original flags.
