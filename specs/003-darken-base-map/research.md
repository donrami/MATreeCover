# Phase 0 Research

**Branch**: `003-darken-base-map` | **Date**: 2026-08-04
**Inputs**: `spec.md`, `src/site/style.json`, `src/pipeline/publish.py`,
vendored `src/site/vendor/maplibre-gl.js` (MapLibre GL JS 5.7.1),
`tests/frontend/smoke_us1.md`.

This feature is a frontend-only visual change. Every unknown is
resolved against the vendored MapLibre source and the style document
that ship in the published bundle — the bundle is the source of
truth, not upstream library docs. No data changes, no pipeline
changes (spec FR-010).

## R-001 — Darkening mechanism: MapLibre raster brightness paint

**Decision**: Add `"paint": { "raster-brightness-max": 0.65 }` to the
`basemap` raster layer in `src/site/style.json`. Target value window
`[0.6, 0.7]`; `0.65` is the default, giving a 35% luminance drop.

**Rationale**: Verbatim from the vendored raster fragment shader
(`src/site/vendor/maplibre-gl.js`, MapLibre 5.7.1):

```glsl
vec3 u_high_vec = vec3(u_brightness_low,  u_brightness_low,  u_brightness_low);
vec3 u_low_vec  = vec3(u_brightness_high, u_brightness_high, u_brightness_high);
fragColor = vec4(mix(u_high_vec, u_low_vec, rgb) * color.a, color.a);
```

with `u_brightness_low = paint["raster-brightness-min"]` (default `0`)
and `u_brightness_high = paint["raster-brightness-max"]` (default `1`).
So the effective transform is:

```
out = brightness_min + (brightness_max - brightness_min) * in
```

With `min = 0` (default) and `max = 0.65`, `out = 0.65 * in` — a
uniform multiplicative darkening of every base-map pixel. Mean
luminance therefore scales by exactly 0.65: a 35% drop, above the
spec's SC-001 gate (≥30%). The current `basemap` layer in
`src/site/style.json` has no `paint` block at all, so today it
renders at full brightness (identity transform).

**Alternatives considered**:
- *Dark fill overlay layer above the basemap*: mathematically
  equivalent (a black overlay at opacity α multiplies by `1-α`), but
  adds a layer and z-order surface; the native raster paint property
  is the same effect with less machinery.
- *Swap tile set to a dark basemap.de variant*: violates the spec
  assumption "the base map source and tile set remain unchanged" and
  SC-005 (no network change); also depends on an external style
  offering.
- *Server-side tile reprocessing*: pipeline/data change; out of
  scope (FR-010).
- *CSS filter on the canvas element*: affects the whole canvas
  including buildings and popups; rejected.

## R-002 — Where the change lives: style.json is the only surface

**Decision**: Single JSON edit in `src/site/style.json` (the
`basemap` layer). No `main.js`, no CSS, no pipeline code.

**Rationale**: `grep` of `src/site/main.js` finds no reference to the
`basemap` layer or `outside-mask` — the frontend code never touches
the base map. `publish.py` copies `STATIC_FILES` including
`style.json` from `src/site/` into `dist/`, then patches only
(a) `metadata.mannheim_bbox` (initial camera, FR-002) and
(b) quarantines sources/layers whose data is not accepted (FR-021/
FR-023). Neither patch touches the `basemap` layer's paint, so the
edit survives publish verbatim.

**Alternatives considered**: *Editing `dist/style.json` directly*:
regenerated on every `make publish`; wrong surface.

## R-003 — Label legibility under multiplicative darkening

**Decision**: Keep labels inside the raster tiles; do not restyle or
re-add labels. Verify legibility empirically (SC-003, 10/10 labels).

**Rationale**: basemap.de grayscale raster tiles bake street and
district labels into the image; there is no separate label layer to
restyle. Under `out = 0.65 * in`, label contrast scales
proportionally: a typical dark-label/light-background pair with a
WCAG contrast ratio of ~8:1 stays at ~6.8:1 at `max = 0.65` — still
above AA (4.5:1). Legibility is preserved by construction, but the
spec gates it on observation, so quickstart Scenario 3 samples ten
labels at a downtown zoom.

**Alternatives considered**: *Replacing the raster with a vector
style + separate label layer*: changes the base map provider and tile
set; rejected per R-001.

## R-004 — Luminance measurement (SC-001 verification)

**Decision**: Compare screenshots of the same viewport (same center,
zoom, and window size) of the old and new bundles; compute mean
luminance of a fixed basemap-only region with `numpy` + `rasterio`
(both already in `.venv`; rasterio reads PNG via GDAL — no new
dependency). Assert the new mean is ≤ 0.70 × the old mean (≥30% drop).

**Rationale**: The venv ships `numpy` and `rasterio` (verified in
site-packages); no PIL. A fixed region with no buildings (river/park
area) isolates the basemap from the 75%-opacity building overlay.
Because the transform is exactly linear (`0.65 × in`), the measured
drop should land at 35% ± measurement tolerance; the gate is 30%.

**Alternatives considered**: *Browser devtools pixel sampling*:
manual, not reproducible. *CI screenshot test*: no such harness
exists for this project; frontend verification is manual smoke
checklists (documented convention).

## R-005 — Boundary mask unaffected

**Decision**: No change needed to the `outside-mask` layer.

**Rationale**: `outside-mask` is a black fill layer rendered above the
basemap (layer order: `basemap`, `outside-mask`, `buildings-fill`,
`buildings-line`, `trees-fill`). The area outside Mannheim is
`#000000` regardless of basemap brightness; darkening only changes
the in-boundary background behind the buildings.

## R-006 — Color-vision safety preserved

**Decision**: Grayscale in, grayscale out.

**Rationale**: The transform `out = 0.65 * in` scales all three RGB
channels identically, so hue and saturation of the grayscale raster
are untouched (only lightness changes). No new hue competes with the
building palette (spec FR-002, edge case "visitors with
color-vision deficiency"). The building palette and tree layer sit in
separate layers above and are not processed by the raster shader.

## R-007 — Distinguishability measurement (SC-002 verification)

**Decision**: Verify every palette color composited over the new
background differs from the background alone by a perceptual color
distance (ΔE) ≥ 20, and by hue where luminance alone is ambiguous.

**Rationale**: The palette's dark blue stop (`#0674aa`) is close to
the darkened gray background in luminance but clearly separated by
hue; strict WCAG luminance contrast would falsely fail it. ΔE ≥ 20 is
a strongly perceptible difference, appropriate for a
color-discrimination map. Palette colors are rendered at
`fill-opacity` 0.75 (values) / 0.4 (unavailable), so the measurement
composites each color over the darkened background at its opacity.

## R-008 — Regression surface (SC-004)

**Decision**: The change touches exactly one layer's paint; all
interactions and overlays are on layers above and are untouched.

**Rationale**: Layer order and all other layers are byte-identical
after the edit (verified by reading `style.json` in full). The
published smoke checklists (`tests/frontend/smoke_us1.md` color map,
`smoke_us2.md` popup, `smoke_us3.md` tree toggle) cover the
interaction surface; US1's "Base map is dark" check remains true (the
outside area is the black mask, unchanged).
