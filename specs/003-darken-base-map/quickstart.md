# Quickstart — Darken Base Map

**Branch**: `003-darken-base-map` | **Date**: 2026-08-04

End-to-end validation guide for the base-map darkening. Every
scenario is a pass/fail check against the spec's user stories,
acceptance scenarios, and success criteria SC-001..SC-005. The style
contract is `contracts/base-map-style.md`; the entities are in
`data-model.md`; the design rationale is in `research.md`.

## Prerequisites

- The published bundle from the prior feature (`dist/`, buildings
  layer + values accepted, per `artifacts.manifest.json`).
- The venv with `numpy` and `rasterio` (already present; used only
  for the luminance measurement in Scenario 1).
- A Range-capable static server (PMTiles requires HTTP Range;
  `python -m http.server` does not support it — use nginx or
  equivalent).
- A modern desktop browser with WebGL 2.

## Setup

```text
git checkout 003-darken-base-map
make publish        # regenerates dist/ from src/ (copies style.json, patches camera + quarantine)
```

Serve the published bundle:

```text
nginx -c /tmp/nginx-dist.conf   # root .../dist; Range enabled
```

Keep the pre-change bundle reachable for the before/after comparison
in Scenario 1 (e.g. `git stash` + `make publish` into a separate
copy, or `git show HEAD:src/site/style.json` to inspect the diff).

## Scenario 1 — Luminance drop (SC-001, FR-001)

**Maps to**: user story 1, acceptance scenario 1, contract
invariant "Verification · Luminance".

1. Open the OLD bundle in a fixed-size window (e.g. 1280×800).
2. Set the same camera in both bundles: zoom to a basemap-only area
   with no buildings (e.g. the Rhine or a park), or hide the
   `buildings-fill` layer via the devtools console:
   ```js
   map.setLayoutProperty('buildings-fill', 'visibility', 'none')
   ```
3. Screenshot the viewport (devtools screenshot or OS capture) →
   `old.png`. Repeat identically on the NEW bundle → `new.png`.
4. Compute mean luminance of both images:
   ```py
   import numpy as np, rasterio
   def mean_lum(path):
       with rasterio.open(path) as ds:
           rgb = ds.read([1,2,3]).astype(np.float64) / 255.0
       return (0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2]).mean()
   old_l, new_l = mean_lum('old.png'), mean_lum('new.png')
   assert new_l <= 0.70 * old_l, (old_l, new_l)
   ```
5. **Pass criteria**:
   - The new mean luminance is ≤ 70% of the old (≥30% drop).
   - Expected ≈ 0.65 × old (35% drop) with `raster-brightness-max: 0.65`
     (research R-001); allow measurement tolerance, gate at 30%.
   - The map is visibly darker by eye (FR-001).

## Scenario 2 — Palette distinguishability (SC-002, FR-004, FR-007)

**Maps to**: user story 1, acceptance scenarios 2–3, edge case
"lightest palette color" and "gray no-value buildings".

1. Open the NEW bundle at the default view.
2. **Pass criteria** (visual inspection at default zoom):
   - The lightest palette color (yellow `#ffd524`, 0% tree cover)
     is clearly visible against the darkened background.
   - The dark blue stop (`#0674aa`) is distinguishable from the
     background by hue, not only lightness.
   - The light blue high-value colors (`#39c2ff`..`#6ad4ff`) remain
     bright and clearly visible.
   - Gray "no value" buildings (`#b8b8b8` at 0.8 opacity, lightened
     during implementation for FR-007) are visible and do not merge
     into the background (FR-007).
   - Neighboring buildings with different values show an
     easily-perceived color difference.
3. (Optional, scripted) composited ΔE check: for each palette stop
   `c` at its opacity `a` over the measured background `bg`,
   `ΔE(c_over_bg, bg) ≥ 20`. The palette stops are listed in
   `data-model.md` E-002; measurement method in `research.md` R-007.

## Scenario 3 — Label legibility (SC-003, FR-005)

**Maps to**: user story 2, acceptance scenarios 1–2.

1. Open the NEW bundle. Zoom to a downtown area (street names and
   district labels visible).
2. Read ten street or district labels at that zoom.
3. **Pass criteria**:
   - All ten sampled labels are legible against the darkened
     background (SC-003).
   - Panning across the city: no area renders with unreadably
     low-contrast labels.
4. Repeat at one zoomed-in and one zoomed-out level to confirm the
   darkening does not break legibility at other zooms (FR-005).

## Scenario 4 — Grayscale, overlays, and interaction regression
(FR-002, FR-006, FR-008, FR-009, SC-004)

**Maps to**: user story 3, all edge cases.

1. Open the NEW bundle.
2. **Pass criteria**:
   - The base map is grayscale: no hue or tint anywhere on the base
     map (FR-002). Compare against the OLD bundle screenshot if
     unsure.
   - Toggle the `Bäume` layer on: tree polygons (`#39C43D`) are
     clearly visible over the darkened background (FR-006).
   - Click buildings: the compact value popup opens exactly as
     before (FR-009). Click empty space: popup closes. Hover a
     building: pointer cursor.
   - Zoom in and out: darkening applies at every zoom (FR-008).
3. Run the published smoke checklists:
   ```text
   # manual: tests/frontend/smoke_us1.md (extended with this feature's checks)
   # manual: tests/frontend/smoke_us2.md (popup behavior unchanged)
   # manual: tests/frontend/smoke_us3.md (tree toggle unchanged)
   ```

## Scenario 5 — No network or data change (SC-005, FR-010)

**Maps to**: spec assumption "same tiles, same data".

1. Inspect the style diff:
   ```text
   git diff HEAD -- src/site/style.json
   ```
2. **Pass criteria**:
   - The diff touches ONLY the `basemap` layer's `paint` block
     (adding `raster-brightness-max`). No source URL, tileSize,
     attribution, layer order, or other layer changes.
   - In the browser network tab, the new bundle requests the same
     basemap.de tile URLs as the old bundle.
   - `make publish` output includes the same artifacts; the
     `manifest.json` in `dist/` is unchanged apart from
     regeneration metadata (FR-010: no data change).

## What to do when a scenario fails

- Scenario 1 failure (drop < 30%): the brightness value is too
  light. Raise the darkening (lower `raster-brightness-max` within
  the contract window `[0.6, 0.7]`), re-publish, re-measure.
- Scenario 3 failure: labels illegible at 0.65. Trade off against
  SC-001: nudge `raster-brightness-max` up (toward 0.7) until both
  gates pass; the contract window is the tuning range.
- Scenario 4 failure: contract violation of layer order, palette, or
  interactions — stop and fix; do not tune brightness to mask it.
- Scenario 5 failure: the change went beyond the paint block;
  revert the extra edits. The feature is JSON-only by design
  (FR-010).
- Do not commit the implementation until Scenario 1 and Scenario 3
  both pass; they cover the two measurable gates the spec names
  (SC-001, SC-003).
