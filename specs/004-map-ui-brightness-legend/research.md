# Phase 0 Research

**Branch**: `004-map-ui-brightness-legend` | **Date**: 2026-08-04
**Inputs**: `spec.md` (+ clarifications), `plan.md` technical context,
`src/site/index.html`, `src/site/style.css`, `src/site/main.js`,
`src/site/style.json`, `src/pipeline/publish.py`,
`tests/frontend/smoke_us1.md`, 003 research/contracts.

This feature is a frontend-only presentation change. Every unknown is
resolved against the vendored MapLibre source, the shipped style
document, and the static bundle that publish produces. No data
changes, no pipeline changes (spec FR-015, plan Constitution Check).

## R-001 — Brightness slider mechanism: runtime raster-brightness paint

**Decision**: Drive the existing MapLibre raster paint property at
runtime: `map.setPaintProperty('basemap', 'raster-brightness-max', v)`
with `v ∈ [0.05, 1.0]`, default `0.65`. The slider element is a
native `<input type="range" min="5" max="100" value="65">`; the
value maps identity to brightness (`v = value / 100`), so the
default position (65) reproduces today's published appearance and no
value-mapping function is needed.

**Rationale**: The vendored raster shader (MapLibre GL JS 5.7.1)
applies `out = brightness_min + (brightness_max - brightness_min) * in`
with defaults min 0, max 1 (verified verbatim in 003 research
R-001). `raster-brightness-max` is a standard paint property, so it
supports runtime updates via `setPaintProperty` — the same mechanism
003 set statically, now user-controlled. With `min = 0` fixed:
`out = max * in`, a uniform multiplicative transform of the raster
only; layers above the basemap (mask, buildings, trees) are not
processed by the raster shader (FR-004). Live updates on the `input`
event give continuous dimming with zero network cost (FR-005,
SC-007). Range bounds: 1.0 restores the original un-darkened
basemap; 0.05 is "almost black" while keeping buildings distinct.

**Alternatives considered**:
- *CSS `filter: brightness()` on the map canvas*: affects buildings,
  trees, and popups too — violates FR-004; rejected (same reason 003
  rejected it).
- *Overlay div with black fill + opacity*: an extra layer above the
  basemap, violating the fixed layer order and adding a z-order
  surface; the native paint property is the same effect with less
  machinery.
- *Restyle/re-tile the basemap per value*: network/data change; out
  of scope (SC-007).
- *localStorage persistence*: explicitly out of scope (FR-007,
  clarification session 2026-08-04).

## R-002 — Slider semantics, accessibility, and CSP constraints

**Decision**: Native `<input type="range">` with `aria-label`,
German visible label "Helligkeit", and `addEventListener` wiring in
`main.js`. No inline event handlers.

**Rationale**: Native range inputs give keyboard arrow-key operation,
touch dragging, and automatic `aria-valuenow`/`aria-valuemin`/
`aria-valuemax` for free (FR-006, edge cases "touch devices" and
"keyboard users"). The page CSP is `script-src 'self'` (verified in
`index.html`), which forbids inline JS handlers — all wiring goes
through `main.js` listeners. The slider sits inside its own
interactive element, so dragging it does not pan the map (the map's
drag listeners fire on canvas pointer events; the slider consumes
its own pointer events). `touch-action` needs no override; the
smoke checklist verifies no pan-while-dragging.

**Alternatives considered**: *Custom-drawn slider (div + drag
handlers)*: reinvents keyboard/touch/ARIA support; rejected.

## R-003 — UI placement rework: root cause and fix

**Decision**: Move the tools card (`#controls`: Bäume toggle +
brightness slider) from the top-right corner to the left column,
directly below the legend card. The top-right corner is then
occupied by MapLibre's NavigationControl alone. Attribution stays
bottom-right; the popup stays transient (FR-017).

**Rationale**: The overlap is structural, verified in
`src/site/style.css`: `#controls` is `position: absolute;
top: 12px; right: 12px` — the same corner MapLibre mounts its
NavigationControl into (`.maplibregl-ctrl-top-right`, default
`margin: 10px`), with no offset between the two, so the Bäume
button and the zoom/compass buttons occupy overlapping rectangles at
typical widths. Any top-right position for our card is fragile
because the navigation control's height varies (zoom buttons +
compass) — the fix that cannot drift is to stop sharing the corner. The left
column (legend above, tools below) is a standard map-UI pattern;
the legend card is `top: 12px; left: 12px` with `max-width: 220px`,
leaving a clear vertical stack. On ≤480 px the existing media query
already relocates `#controls` to `bottom: 76px; right: 12px` (above
the legend strip) and collapses the legend to a bottom strip — the
rework keeps that behavior, now for a card containing Bäume + slider
(FR-008, edge case "narrow screens").

**Alternatives considered**:
- *Nudge `#controls` lower with a fixed top offset*: still shares the
  corner; the navigation control's height is not fixed (compass +
  zoom), so a fixed offset cannot guarantee disjointness at all
  widths — this is the current bug's mechanism; rejected.
- *Merge Bäume into the legend card*: reduces element count but mixes
  data-explanation and map-operation UI; rejected in favor of
  keeping the tools card distinct (spec clarification: slider is a
  standalone control).
- *Move the navigation control to a different corner*: changes
  MapLibre control mounting (`map.addControl` position) and fights
  the library's own layout; the tools card move is the smaller
  change.

## R-004 — Gradient legend: markup, stops, ticks, and accessibility

**Decision**: Replace the discrete swatch `<ol class="legend-stops">`
with a continuous gradient bar:
- The bar is a `linear-gradient` using the eight frozen palette
  stops positioned at their value fractions: `0 → #ffd524`,
  `12 → #e6854a`, `24 → #a97e65`, `24.08 → #0674aa`,
  `32 → #1db6ff`, `40 → #39c2ff`, `48 → #56ceff`, `80 → #6ad4ff`,
  with `#6ad4ff` held constant from 80 to 100 (values above 80 keep
  the final reference color — the palette's existing cap).
- Tick labels `0`, `15`, `30`, `50`, `100` are real text elements
  positioned at `left: 0%, 15%, 30%, 50%, 100%` — value-proportional
  (FR-012), matching the reference project's presentation.
- Screen-reader semantics (FR-018): the gradient element carries
  `role="img"` + an `aria-label` describing the scale, and the
  existing five-value list is kept in a visually-hidden form so
  assistive technology reads the values as text (the current legend
  is a semantic list; the rework must not regress it).

**Rationale**: The palette stops and the cap at 80 are documented in
`src/site/style.json` (`buildings-fill` interpolate stops) and
frozen by 003's data model (E-002). Positioning stops at their value
fractions makes the bar a true value axis, so a building's color can
be matched to a point on the bar (US3 acceptance 3). The tick values
0/15/30/50/100 are the existing legend's labels (verified in
`index.html`) and the reference project's labels; keeping them
preserves continuity for current visitors. CSP `style-src
'unsafe-inline'` permits inline gradient styles; the visually-hidden
list is the established `.sr-only` pattern (no new mechanism).

**Alternatives considered**:
- *Perceptual (Lab) interpolation*: technically smoother color
  transitions, but the frozen palette stops are the product's
  colors; linear interpolation between them is what the reference
  project shows and what visitors expect. Deferred to plan level;
  rejected as unnecessary deviation (spec edge case "no unintended
  color" is satisfied: every gradient pixel is a convex combination
  of adjacent palette stops).
- *Gradient without tick labels*: loses the value axis; FR-012
  requires the labels.
- *`<canvas>`-drawn gradient*: a JS dependency for what CSS
  `linear-gradient` does natively; rejected.

## R-005 — Overlap verification matrix (SC-003, FR-008, FR-009)

**Decision**: Extend the smoke-checklist convention with
`tests/frontend/smoke_us4.md`, whose core check measures the
bounding boxes of the five static UI elements (legend, tools card,
navigation control, attribution, and the popup when open) via
`getBoundingClientRect` and asserts pairwise disjointness at a
viewport matrix of 5 widths (320, 480, 768, 1280, 1920 px) × 3 zoom
levels (default view, one zoomed in, one zoomed out). Optional
recorded evidence under `validation/brightness-slider/overlap.json`.

**Rationale**: The project has no browser test harness (documented
convention: manual smoke checklists — 003 quickstart); the matrix is
scriptable in the browser console in minutes, deterministic, and
maps 1:1 to SC-003 ("at least 5 widths and 3 zoom levels, 100% of
element pairs have zero overlapping clickable areas"). SC-004 (Bäume
clickable at the former overlap point) is a click-through check at
the old overlap rectangle.

**Alternatives considered**: *CI screenshot test*: no such harness
exists; manual checklist + recorded measurements is the established
pattern. *Synthetic layout assertions in pytest*: the DOM is
browser-rendered; pytest cannot measure it.

## R-006 — Luminance measurement (SC-001)

**Decision**: Reuse 003's screenshot-luminance method (`numpy` +
`rasterio`, both in `.venv`) on the published bundle: capture the
same fixed basemap-only viewport at slider minimum (0.05), default
(0.65), and maximum (1.0); assert min < 10% of default and max
restores the original un-darkened luminance (equal to the 003
pre-change bundle's measurement within tolerance).

**Rationale**: The transform is exactly linear (`out = max * in`
with min 0), so the ratios are predictable: 0.05 / 0.65 ≈ 0.077
(7.7% < 10% ✓); 1.0 / 0.65 ≈ 1.54 relative to the darkened default
and ≈ 1.0 relative to the original light basemap. Measured on a
basemap-only region (river/park, or with `buildings-fill` hidden) to
exclude the building overlay. Recorded under
`validation/brightness-slider/luminance.json`.

## R-007 — No-network / no-data proof (SC-007, FR-015)

**Decision**: Verify via `git diff` scope and the network tab that
the change is confined to the three static files and adds no
requests.

**Rationale**: `publish.py` copies `STATIC_FILES =
("index.html", "style.css", "main.js", "style.json",
"attribution.html")` verbatim from `src/site/` to `dist/` and
patches only `style.json` camera metadata and quarantine (verified in
`src/pipeline/publish.py`). The feature modifies the first three
files only; the raster paint update re-renders already-loaded tiles —
no tile requests, no new assets. The gradient is CSS; the slider is
HTML+JS.

## R-008 — Contract interplay with 003

**Decision**: 003's `base-map-style.md` contract fixed
`raster-brightness-max` in `[0.6, 0.7]` as a constant. 004
supersedes the *runtime* clause: the static default stays `0.65`
(in 003's window, so a no-JS/no-slider load renders identically),
while the user-adjustable runtime range is `[0.05, 1.0]`. The other
003 invariants (grayscale, same tiles, layer order, palette frozen,
mask untouched) are unaffected and carried forward.

**Rationale**: The 003 contract is a historical artifact of its
feature; 004's contracts (this feature's `contracts/`) state the
current contract and explicitly note the supersession so the two
don't read as contradictory. The static style document keeps 0.65,
which preserves SC-003 of 003 (default = darkened) and FR-003 of 004
(default reproduces today's appearance) simultaneously.

## R-009 — Regression surface (SC-006)

**Decision**: Touch only the pieces the spec requires: the legend
markup in `index.html`, layout rules in `style.css`, and a new
`wireBrightnessSlider()` function in `main.js` invoked from
`onMapLoad`. The existing `wireBuildingsInteractions`,
`wireTreesToggle`, `wireErrorHandling`, popup behavior, camera
logic, and layer order are untouched.

**Rationale**: Layer order and all non-basemap layers are
byte-identical; the raster paint update cannot reach them (R-001).
The published smoke checklists `smoke_us2.md` (popup) and
`smoke_us3.md` (tree toggle) cover the interaction surface and are
unchanged; `smoke_us1.md` gains the new brightness + legend checks
(extending 003's darkness section, which already asserts the
default-appearance baseline this feature's slider default must
match).
