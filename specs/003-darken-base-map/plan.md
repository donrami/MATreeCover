# Implementation Plan: Darken Base Map

**Branch**: `003-darken-base-map` | **Date**: 2026-08-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-darken-base-map/spec.md`

## Summary

Darken the grayscale base map so building tree-cover colors are
easier to distinguish. The change is a single JSON edit: add
`"paint": { "raster-brightness-max": 0.65 }` to the `basemap` raster
layer in `src/site/style.json`. MapLibre GL JS 5.7.1 (vendored)
applies `out = mix(raster-brightness-min, raster-brightness-max, in)`
in the raster shader, so with min 0 and max 0.65 every base-map pixel
scales by 0.65: a 35% mean-luminance drop (SC-001 gate: ≥30%),
grayscale preserved, labels scale proportionally, zero network or
data change, all zoom levels. `publish.py` copies `style.json`
verbatim apart from camera metadata and acceptance quarantine, so the
edit flows into `dist/` unchanged.

## Technical Context

**Language/Version**: JSON style document (MapLibre GL style spec v8);
frontend is static JS/HTML/CSS, no build tool.

**Primary Dependencies**: MapLibre GL JS 5.7.1 (vendored at
`src/site/vendor/maplibre-gl.js`) — raster paint properties
`raster-brightness-min`/`raster-brightness-max`, verified present in
the vendored source (research R-001). basemap.de grayscale raster
tiles. No new dependencies.

**Storage**: N/A — no data involved; the feature is a style-document
change only (FR-010).

**Testing**: Manual smoke checklists (`tests/frontend/smoke_us1.md`
extended with darkness checks, `smoke_us2.md`, `smoke_us3.md`);
pixel-luminance measurement with `numpy` + `rasterio` (already in
`.venv`, no new dependency); existing pytest suites untouched (no
data change). Verification guide: `quickstart.md` (Scenarios 1–5).

**Target Platform**: Modern browser with WebGL 2 (unchanged from the
existing bundle).

**Project Type**: Static web map (frontend).

**Performance Goals**: No change. The darkening is a per-pixel shader
operation already in the render path; no extra requests, no added
paint cost (SC-005).

**Constraints**: Mean base-map luminance drop ≥30% (SC-001);
10/10 sampled labels legible at a downtown zoom (SC-003); every
palette color distinguishable from the new background (SC-002);
grayscale preserved (FR-002); palette, tree layer, popup, hover, and
toggle unchanged (FR-003/FR-006/FR-009); same tile URLs and data
(SC-005, FR-010).

**Scale/Scope**: One paint property on one layer; applies at every
zoom; Mannheim map only.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No constitution file exists, so there are no constitution-derived gates. The de-facto
gates are the spec's own constraints, evaluated as follows:

- **FR-010 / SC-005 (no data, no network change)**: PASS — the
  approach is a client-side shader property; tile URLs and data
  untouched (research R-001, R-002).
- **SC-003 (label legibility)**: PASS — multiplicative scaling
  preserves relative contrast; verified empirically via quickstart
  Scenario 3.
- **SC-001 (≥30% luminance drop)**: PASS by construction — 0.65
  scaling gives a 35% drop (research R-001); measured in quickstart
  Scenario 1.
- **OR-004 (one commit per accepted spec/plan/slice)**: PASS — plan
  commits as a single artifact via `make commit-plan`.

Post-design re-check: no new gates introduced. The design adds no
files to the source tree (single existing-file edit) and no
dependencies, so complexity and governance constraints remain
unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/003-darken-base-map/
├── plan.md              # This file (plan command output)
├── research.md          # Phase 0 output — mechanism, measurement, alternatives
├── data-model.md        # Phase 1 output — style-document entities and invariants
├── quickstart.md        # Phase 1 output — Scenarios 1–5 validation guide
├── contracts/           # Phase 1 output
│   ├── README.md
│   └── base-map-style.md
└── tasks.md             # Phase 2 output (tasks command output)
```

### Source Code (repository root)

```text
src/
└── site/
    └── style.json       # THE change: basemap layer gains paint.raster-brightness-max (0.65)

tests/
└── frontend/
    ├── smoke_us1.md     # extended during implementation with darkness + legibility checks
    ├── smoke_us2.md     # unchanged (popup regression surface)
    └── smoke_us3.md     # unchanged (tree toggle regression surface)

validation/              # optional: record the before/after luminance numbers
```

No new source files are created. The deliverable is one edit to an
existing file plus documentation.

**Structure Decision**: Single existing style document
(`src/site/style.json`); no new modules, no build changes. The
publish pipeline (`src/pipeline/publish.py`) already carries
`style.json` from `src/site/` to `dist/` and patches only camera
metadata and acceptance quarantine, neither of which touches the
`basemap` layer paint (research R-002).

## Complexity Tracking

No Constitution Check violations; this table is intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
