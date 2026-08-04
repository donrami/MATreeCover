# Quickstart — Map UI, Brightness Slider & Gradient Legend

**Branch**: `004-map-ui-brightness-legend` | **Date**: 2026-08-04

End-to-end validation guide. Every scenario is a pass/fail check
against the spec's user stories, acceptance scenarios, and success
criteria SC-001..SC-007. Contracts: `contracts/base-map-brightness.md`,
`contracts/ui-layout.md`, `contracts/legend-gradient.md`; entities in
`data-model.md`; design rationale in `research.md`.

## Prerequisites

- The published bundle from the prior feature (`dist/`, 003
  darkening shipped: `style.json` has `raster-brightness-max: 0.65`).
- The venv with `numpy` and `rasterio` (used only for the luminance
  measurement in Scenario 2).
- A Range-capable static server (PMTiles requires HTTP Range; use
  nginx or equivalent, not `python -m http.server`).
- A modern desktop browser with WebGL 2; browser devtools.

## Setup

```text
git checkout 004-map-ui-brightness-legend
make publish        # regenerates dist/ from src/ (static files copied verbatim)
```

Serve the published bundle:

```text
nginx -c /tmp/nginx-dist.conf   # root .../dist; Range enabled
```

## Scenario 1 — Slider exists, defaults to today, dims live (FR-001,
FR-002, FR-003, FR-005, FR-016)

**Maps to**: user story 1, acceptance scenarios 1, 3, 6.

1. Open the bundle. Confirm the tools card below the legend contains
   the Bäume button and a "Helligkeit" slider at value 65.
2. **Pass criteria**:
   - On load, before touching the slider, the map looks identical to
     the pre-feature published map (FR-003; the slider default 65 ==
     `raster-brightness-max 0.65`, contract invariant 6).
   - Drag the slider down: the base map dims continuously with no
     jumps; buildings and trees keep their colors (FR-002, FR-004).
   - Drag back up past 65: the map brightens continuously toward the
     original un-darkened basemap (clarification Q1; FR-002).
   - Drag below 25: the base map transitions gradually into the
     inverted (photo-negative) look; at 5, streets and labels render
     lighter than the near-black background, never brighter than the
     0.65 cap, and remain legible (clarifications Q3/Q4; FR-019;
     verified per-pixel in Scenario 2).
   - The slider is a visible standalone control at desktop and at a
     360 px viewport (FR-016).
   - Dragging the slider does not pan or zoom the map; panning after
     release does not reset the slider (FR-006).
3. Reload the page at a non-default slider value: the slider and the
   map return to the default (FR-007, contract invariant 4).

## Scenario 2 — Luminance and inversion gates (SC-001, SC-008)

**Maps to**: success criteria SC-001 and SC-008.

1. Open the bundle in a fixed-size window (e.g. 1280×800). Hide the
   building overlay to isolate the basemap:
   ```js
   map.setLayoutProperty('buildings-fill', 'visibility', 'none')
   ```
2. Set the slider to default (65), screenshot → `def.png`; minimum
   (5), screenshot → `min.png`; maximum (100), screenshot →
   `max.png`. Keep the camera fixed.
3. Background gate (SC-001): luminance is linear light, and the
   raster shader multiplies in linear space — decode the
   sRGB-encoded screenshots first, and measure the background with a
   feature-free sub-region (park or Rhine) or the 10th-percentile
   luminance of the central crop (features are excluded: at minimum
   they invert and are intentionally brighter):
   ```py
   import numpy as np, rasterio
   def srgb_to_linear(c):
       c = c.astype(np.float64)
       return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
   def bg_lum(path):
       with rasterio.open(path) as ds:
           rgb = ds.read([1,2,3]).astype(np.float64) / 255.0
       lin = srgb_to_linear(rgb)
       lum = (0.2126*lin[0] + 0.7152*lin[1] + 0.0722*lin[2]).flatten()
       return np.percentile(lum, 10)          # background, not features
   d, m, x = bg_lum('def.png'), bg_lum('min.png'), bg_lum('max.png')
   assert m <= 0.10 * d, (d, m)          # min background < 10% of default
   assert abs(x - (d / 0.65)) <= 0.05 * (d / 0.65), (d, x)  # max restores original
   ```
   Per-pixel fallback (robust to encoding gamma): median of per-pixel
   background ratios min/default ≤ 0.10; measured 2026-08-04: 0.090
   before inversion was added (re-record at implementation).
4. Inversion gate (SC-008): at minimum the base map inverts — pixels
   that were dark at maximum (streets, labels) must become lighter
   than the pixels that were bright (background):
   ```py
   def lum_arr(path):
       with rasterio.open(path) as ds:
           rgb = ds.read([1,2,3]).astype(np.float64) / 255.0
       lin = srgb_to_linear(rgb)
       return (0.2126*lin[0] + 0.7152*lin[1] + 0.0722*lin[2]).flatten()
   a_max, a_min = lum_arr('max.png'), lum_arr('min.png')
   dark = a_max < np.percentile(a_max, 25)       # features at max
   assert np.mean(a_min[dark]) > np.mean(a_min[~dark]), 'features must invert lighter'
   assert a_min[dark].max() <= 0.65, 'inverted features must stay within the 0.65 cap (SC-008)'
   ```
5. **Pass criteria**:
   - `min` background ≤ 10% of `def` background (expected ≈ 7.7%:
     0.05/0.65).
   - `max` luminance ≈ `def / 0.65` (restores the pre-003 light
     basemap; contract invariant 5).
   - At minimum, streets and labels render lighter than the
     background, never exceeding the 0.65 cap (per-pixel luminance
     ≤ 0.65), and are legible by eye (SC-008); the map stays
     grayscale (FR-019).
   - By eye at minimum: map background is almost black, buildings
     still clearly visible when the overlay is back on (SC-002).
   - The transition between normal dimming and the inverted look is
     gradual across the low end of the slider range (no sudden
     switch; spec edge case).
   - Record results under `validation/brightness-slider/luminance.json`.

## Scenario 3 — Overlap matrix (SC-003, FR-008)

**Maps to**: user story 2, acceptance scenarios 1–3, 5.

1. Open the bundle. Run this console snippet at each matrix cell
   (widths 320, 480, 768, 1280, 1920 px × 3 zoom levels: default
   view, one zoomed in, one zoomed out):
   ```js
   const ids = ['legend', 'controls', 'attribution'];
   const nav = document.querySelector('.maplibregl-ctrl-top-right');
   const rects = [...ids.map(id => document.getElementById(id)), nav]
     .filter(Boolean)
     .map(el => { const r = el.getBoundingClientRect();
       return { id: el.id || 'nav', l: r.left, t: r.top, r: r.right, b: r.bottom }; });
   const overlap = (a, b) => a.l < b.r && a.r > b.l && a.t < b.b && a.b > b.t;
   const pairs = [];
   for (let i = 0; i < rects.length; i++)
     for (let j = i + 1; j < rects.length; j++)
       if (overlap(rects[i], rects[j])) pairs.push([rects[i].id, rects[j].id]);
   console.log(pairs); // expect []
   ```
2. **Pass criteria**:
   - `pairs` is empty at all 15 matrix cells (SC-003).
   - At each cell, all four elements are visually reachable; the
     narrow layouts (320, 480) show the legend strip and the tools
     card stacked without covering the zoom control or attribution
     (FR-008, `contracts/ui-layout.md` invariant 2).
3. Record the matrix under `validation/brightness-slider/overlap.json`.

## Scenario 4 — Bäume clickable at the former overlap point (SC-004,
FR-009)

**Maps to**: user story 2, acceptance scenario 4.

1. Open the bundle at 1280 px. Click the location where the Bäume
   button overlapped the zoom control before this feature (top-right
   corner, below the zoom buttons).
2. **Pass criteria**:
   - The click toggles the Bäume layer (button gains the green
     active state and the tree layer appears); the click is never
     swallowed by another element (SC-004).
   - The zoom controls remain fully clickable in their own corner.

## Scenario 5 — Gradient legend (SC-005, FR-010..FR-013, FR-018)

**Maps to**: user story 3, all acceptance scenarios.

1. Open the bundle.
2. **Pass criteria**:
   - The legend shows one continuous gradient bar — no visible
     segment boundaries between colors (FR-010/FR-011).
   - Tick labels `0`, `15`, `30`, `50`, `100` are visible at
     proportional positions along the bar (left to right; FR-012).
   - A building's color matches a point on the bar (e.g. a yellow
     building at the left end, a light-blue one at the right end).
   - Title "Baumfläche", description, and unit "Prozent" remain
     (FR-013).
   - Narrow viewport (360 px): the bottom-strip legend shows the
     gradient with all five labels visible, no clipping (SC-005,
     US3 acceptance 4).
   - Screen reader / accessibility tree: the gradient element has an
     accessible name, and the values `0 15 30 50 100` plus the unit
     are exposed as text (FR-018).

## Scenario 6 — Regression and no-network (SC-006, SC-007, FR-014,
FR-015)

**Maps to**: user story 1 acceptance 4–5, spec Out of Scope.

1. Open the bundle.
2. **Pass criteria**:
   - Click buildings: the value popup opens with unchanged content;
     click empty space: it closes; hover: pointer cursor (FR-014).
   - Toggle Bäume on: tree polygons visible at full color over any
     slider position (edge case "very low brightness with trees").
   - Zoom in/out and north reset work (zoom control untouched).
   - Network tab: only the same basemap.de tiles and vendored libs
     load — no new requests at any slider position (SC-007).
   - `git diff HEAD --stat` touches only `src/site/index.html`,
     `src/site/style.css`, `src/site/main.js`, `tests/frontend/*`,
     and `specs/` (FR-015).
3. Run the published smoke checklists:
   ```text
   # manual: tests/frontend/smoke_us1.md (extended with this feature's checks)
   # manual: tests/frontend/smoke_us2.md (popup behavior unchanged)
   # manual: tests/frontend/smoke_us3.md (tree toggle unchanged)
   # manual: tests/frontend/smoke_us4.md (new: overlap matrix)
   ```

## What to do when a scenario fails

- Scenario 1/2 failure (no dimming, wrong default, or luminance
  gates): check the slider wiring — the `input` listener must call
  `setPaintProperty('basemap', 'raster-brightness-max', value/100)`;
  verify the default value is 65 and the static style value is 0.65.
  Do not tune the slider range to mask a wiring bug. An SC-008
  cap failure means `basemap-inverted` still paints `min: 1` — set
  it to `0.65` and re-measure; never raise the cap to pass.
- Scenario 3/4 failure (overlap or swallowed click): layout
  contract violation — stop and fix the placement per
  `contracts/ui-layout.md`; do not shrink the viewport matrix.
- Scenario 5 failure (gradient wrong or labels clipped): check the
  stops and tick positions against `contracts/legend-gradient.md`;
  the palette is frozen — never change stops to fix a rendering
  issue.
- Scenario 6 failure (regression or new requests): revert the extra
  change; the feature is confined to the three static files by
  design (FR-015).
- Do not commit the implementation until Scenarios 2, 3, and 5
  pass; they cover the three measurable gates (SC-001, SC-003,
  SC-005).
