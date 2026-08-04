# Implementation Plan: Map UI, Brightness Slider & Gradient Legend

**Branch**: `004-map-ui-brightness-legend` | **Date**: 2026-08-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-map-ui-brightness-legend/spec.md`

## Summary

Three UI changes to the static frontend (`src/site/`), all client-side:

1. **Brightness slider** — a native `<input type="range">` bound to
   MapLibre's `raster-brightness-max` raster paint property via
   `map.setPaintProperty('basemap', 'raster-brightness-max', v)`.
   Runtime range `[0.05, 1.0]` (near-black ↔ original un-darkened
   basemap), default `0.65` = today's published appearance (the 003
   darkening), session-only (FR-007), live updates on `input` events
   (FR-005). Slider value is percent, identity-mapped
   (`min=5, max=100, value=65`). Only the `basemap` layer is touched
   (FR-004); layers above it (mask, buildings, trees) are untouched
   by the raster shader.
2. **UI placement rework** — the overlap is caused by `#controls`
   (`position: absolute; top: 12px; right: 12px`) sharing the
   top-right corner with MapLibre's NavigationControl
   (`.maplibregl-ctrl-top-right`, no offset). Fix: move the tools
   card (Bäume toggle + brightness slider) into the left column
   below the legend card; the top-right corner is then occupied by
   the navigation control alone. Attribution stays bottom-right;
   popup stays transient/dismissible (FR-017). Responsive rules for
   ≤480 px keep the existing stacked layout overlap-free (FR-008).
3. **Gradient legend** — replace the discrete swatch `<ol>` with a
   continuous gradient bar built from the eight frozen palette stops
   positioned at their value fractions (0, 12, 24, 24.08, 32, 40,
   48, 80, capped 80→100), with tick labels 0 / 15 / 30 / 50 / 100
   at value-proportional positions (FR-010..FR-012). Screen-reader
   text is preserved via a visually-hidden semantic value list
   (FR-018).

No pipeline, data, palette, popup, or interaction changes. The
publish step copies `index.html`, `style.css`, `main.js` verbatim
(verified: `STATIC_FILES` in `src/pipeline/publish.py`), so edits in
`src/site/` flow into `dist/` unchanged. New files: none in
`src/`; `tests/frontend/smoke_us4.md` (overlap matrix) plus an
extended `smoke_us1.md`; optional measurement record under
`validation/brightness-slider/`.

## Technical Context

**Language/Version**: Vanilla HTML/CSS/JS (no build tool); MapLibre
GL style spec v8; vendored MapLibre GL JS 5.7.1
(`src/site/vendor/maplibre-gl.js`).

**Primary Dependencies**: MapLibre GL JS — runtime paint update via
`setPaintProperty` (`raster-brightness-max` is a standard raster
paint property; the vendored raster shader applies
`out = min + (max - min) * in`, verified in 003 research R-001). No
new dependencies.

**Storage**: N/A — slider state is in-memory only (FR-007); no
localStorage, no server state.

**Testing**: Manual smoke checklists (documented project convention):
`tests/frontend/smoke_us1.md` extended with brightness + legend
checks, new `tests/frontend/smoke_us4.md` for the overlap matrix,
`smoke_us2.md`/`smoke_us3.md` unchanged as regression surfaces.
Pixel-luminance measurement with `numpy` + `rasterio` (already in
`.venv`) for SC-001; `getBoundingClientRect` overlap matrix for
SC-003. Existing pytest suites untouched (no data change).

**Target Platform**: Modern browser with WebGL 2 (unchanged from the
existing bundle).

**Project Type**: Static web map (frontend).

**Performance Goals**: No change. A slider drag issues paint-property
updates that are shader-level re-renders of the existing raster —
no new requests, no added assets (SC-007). Live updates must not
stutter: one `setPaintProperty` per `input` event is well within
MapLibre's render budget for a single raster layer.

**Constraints**: CSP `script-src 'self'` forbids inline JS handlers —
slider wiring goes through `addEventListener` in `main.js`; CSP
`style-src 'unsafe-inline'` permits the inline gradient styles.
Minimum luminance gate: slider minimum (0.05) must measure < 10% of
default (0.65) background luminance; maximum (1.0) must restore the
original un-darkened luminance (SC-001). No two static UI elements
may overlap at ≥320 px width, all zooms (FR-008); Bäume fully
clickable (FR-009/SC-004). Gradient bar continuous with all five
tick labels visible at desktop and ≤480 px (FR-010..FR-012,
SC-005). No new network requests (FR-015, SC-007). Palette, tree
layer, popup, hover, toggle behavior unchanged (FR-014, SC-006).

**Scale/Scope**: Three static files in `src/site/`
(`index.html` markup, `style.css` layout, `main.js` wiring) + smoke
checklists. Applies at every zoom level; Mannheim map only.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No constitution file exists (`.specify/memory/constitution.md`
absent), so there are no constitution-derived gates. The de-facto
gates are the project's operating rules (Makefile) and the spec's own
constraints:

- **OR-004 (one commit per accepted spec/plan/slice; Makefile
  `commit-spec`/`commit-plan`/`commit-slice`)**: PASS — this plan is
  committed via `make commit-plan` as a single artifact; the
  implementation lands as slices via `make commit-slice`.
- **OR-005 (no `*.tif`/`*.pmtiles`/>50 MiB `.geojson` tracked)**: PASS
  — no new files of these types; no manifest change.
- **FR-015 / SC-007 (no data, no network change)**: PASS — the
  feature is pure client-side UI: paint-property updates, layout
  CSS, legend markup. `publish.py` copies the three static files
  verbatim (verified); tile URLs, data, and pipeline untouched.
- **SC-001 (luminance gates)**: PASS by construction — slider maps
  to `raster-brightness-max` ∈ [0.05, 1.0]; 0.05/0.65 ≈ 7.7% < 10%
  at minimum; 1.0 restores the original (research R-006).
- **SC-003/SC-004 (no overlap, Bäume clickable)**: PASS by design —
  tools card moves to the left column, top-right reserved for the
  navigation control (research R-003); verified via quickstart
  Scenario 3.
- **SC-005 (gradient legend with all tick labels)**: PASS by design —
  value-proportional tick positions on a continuous gradient
  (research R-004); verified via quickstart Scenario 5.
- **SC-006 (no regression)**: PASS — layers above the basemap and
  all interaction wiring are untouched; smoke_us2/us3 unchanged
  (research R-009).

Post-design re-check: no new gates introduced. The design adds one
smoke checklist and modifies three existing source files in place; no
new dependencies, no new projects, no governance surface changes.

## Project Structure

### Documentation (this feature)

```text
specs/004-map-ui-brightness-legend/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output — mechanism, placement, verification
├── data-model.md        # Phase 1 output — entities and invariants
├── quickstart.md        # Phase 1 output — Scenarios 1–6 validation guide
├── contracts/           # Phase 1 output
│   ├── README.md
│   ├── base-map-brightness.md
│   ├── ui-layout.md
│   └── legend-gradient.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── site/
    ├── index.html       # legend → gradient markup; #controls gains the slider
    ├── style.css        # tools card to left column; gradient styles; responsive rules
    └── main.js          # wireBrightnessSlider(): input → setPaintProperty

tests/
└── frontend/
    ├── smoke_us1.md     # extended: brightness slider + gradient legend checks
    ├── smoke_us4.md     # NEW: UI placement / overlap matrix (FR-008, SC-003/SC-004)
    ├── smoke_us2.md     # unchanged (popup regression surface)
    └── smoke_us3.md     # unchanged (tree toggle regression surface)

validation/
└── brightness-slider/   # optional: recorded luminance + overlap measurements
```

No new source files are created; three existing files are modified in
place.

**Structure Decision**: Single static frontend, no build step. All
changes stay inside `src/site/` (markup + CSS + JS) because the
feature is presentation-only (spec Out of Scope: no data, no
pipeline). The smoke-checklist convention is extended with one new
file because the overlap matrix is a new verification surface not
covered by the existing three checklists.

## Complexity Tracking

No Constitution Check violations; this table is intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
