# Contract: Base Map Style (Darkened)

**Feature**: Darken Base Map | **Branch**: `003-darken-base-map`
**Source of truth**: `src/site/style.json` (copied to `dist/style.json`
by `publish.py`, which patches only `metadata.mannheim_bbox` and
quarantines non-accepted sources/layers).

## Purpose

The base map must stay the same grayscale basemap.de raster as today,
rendered darker so building tree-cover colors are easier to
distinguish. This contract fixes the layer's stable properties so the
darkening cannot silently become a style swap, a hue shift, or a
data change.

## Layer contract

The `basemap` layer MUST satisfy all of the following after this
feature ships:

| Property | Required value |
|---|---|
| `id` | `"basemap"` |
| `type` | `"raster"` |
| `source` | `"basemap"` (raster tile set `de_basemapde_web_raster_grau`, same tile URLs) |
| `paint.raster-brightness-min` | `0` (default; may be omitted) |
| `paint.raster-brightness-max` | in `[0.6, 0.7]`; target `0.65` |
| `layout.visibility` | `"visible"` |
| `attribution` | `© basemap.de / LGL` (via source) |

## Invariants

1. **Grayscale preserved (FR-002).** The brightness transform scales
   all RGB channels identically. The layer must never gain a hue
   filter, saturation change, or colored overlay.
2. **Same tiles, same network (SC-005).** The source URLs and
   `tileSize` must not change. The darkening is a client-side render
   transform only.
3. **All zoom levels (FR-008).** `raster-brightness-max` is a
   constant, not zoom-dependent.
4. **Layer order fixed.** `basemap` stays below `outside-mask`,
   `buildings-fill`, `buildings-line`, `trees-fill`. No layer added
   above the basemap to achieve the darkening.
5. **Palette untouched (FR-003).** No stop, opacity, or outline value
   in `buildings-fill`/`buildings-line` changes.
6. **Unavailable buildings visible (FR-007).** The gray
   `#444444`/0.4 fill must remain distinguishable from the darkened
   background.
7. **Darkening only inside the boundary.** The `outside-mask` fill
   stays `#000000`; the area outside Mannheim is not affected.

## Verification

- Luminance: mean luminance of a fixed basemap-only region in the new
  bundle ≤ 0.70 × the same region in the old bundle (SC-001; see
  quickstart Scenario 1).
- Distinguishability: each palette color composited at its opacity
  over the darkened background differs from the background alone by
  ΔE ≥ 20 (SC-002; quickstart Scenario 2).
- Legibility: 10/10 sampled street/district labels legible at a
  downtown zoom (SC-003; quickstart Scenario 3).
- No regression: smoke checklists `smoke_us1.md` (extended),
  `smoke_us2.md`, `smoke_us3.md` pass (SC-004).
