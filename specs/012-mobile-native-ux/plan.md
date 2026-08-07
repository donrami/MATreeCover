# Implementation Plan: Mobile-First Native UX

**Branch**: `012-mobile-native-ux` | **Date**: 2026-08-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/012-mobile-native-ux/spec.md`

## Summary

Rework the published Mannheim tree-cover map from a desktop-first, permanently-stacked
UI (legend + tools + city-overview cards that on a phone hide most of the map) into a
mobile-first, native-feeling experience on both phones and desktops. Pure presentation
rework: no new data, no new views, no new features (FR-010). MapLibre GL stays the map
engine; MapLibre controls stay in place.

One shared, collapsible **legend/summary surface** (`#surface`) replaces the static
`#left-stack` column. Its persistent **header** carries the legend title, the tools
(Bäume toggle + Helligkeit slider) and the expand/collapse control; its **body** carries
the full legend (desc, gradient, ticks, units, note) and the city-overview panel.

- **Mobile (< 768px):** the surface is a bottom sheet. Collapsed by default = a compact
  thumb-reachable header strip at the bottom; the map regains >= 80% of the viewport
  (SC-001). Tapping expand slides the body up (internal scroll), map stays dominant,
  `map.setPadding({ bottom: sheetHeight })` keeps building/district popups fully visible
  above the sheet (FR-006). Tools stay visible and operable while collapsed because they
  live in the always-present header (FR-004).
- **Desktop (>= 768px):** the identical `#surface` component sits top-left as a collapsible
  panel, expanded by default (matches current behaviour), collapsible so the map reclaims
  space (P3). Same header/body, same controls, same JS wiring as mobile (FR-008).

Design decisions are grounded in external UX/UI research (thumb-zone ergonomics, touch-target
consensus, native map bottom-sheet conventions, dynamic viewport units, reduced motion), not
inference alone. See [research.md](research.md). All motion is slide/scale via compositor-safe
`transform`/`opacity`, with `prefers-reduced-motion` making every transition instant (FR-008).
Safe-area insets and dynamic viewport units (`dvh`) prevent clipping and browser-chrome layout
jump (FR-007, SC-005). This is CSS/HTML/JS only: zero new network requests, no server, no new
dependencies, static bundle unchanged (FR-012).

## Technical Context

**Language/Version**: Vanilla JavaScript (ES2020, already used) + HTML5 + CSS3. No TypeScript.
MapLibre GL JS 5.7.1 (vendored), pmtiles 4.4.0 (vendored). Python 3.11 for the test suite.

**Primary Dependencies**: MapLibre GL JS 5.7.1 (`src/site/vendor/maplibre-gl.js`), pmtiles 4.4.0
(`src/site/vendor/pmtiles.js`). No new third-party dependencies, no build tool (existing project
constraint, FR-012, feature 001 static-bundle contract).

**Storage**: N/A. Session-only UI state (surface collapsed/expanded) in the DOM; nothing
persisted, no server, no database (FR-012).

**Testing**: pytest (existing suite in `tests/`). New static CSS/DOM assertions in
`tests/acceptance/test_style.py` (touch targets, reduced-motion query, surface markup) and a
manual browser checklist `tests/frontend/smoke_mobile.md` (visual/mobile verification, SC-001,
SC-004, SC-005, SC-010). `make check-public` stays clean (SC-008).

**Target Platform**: Static web bundle served at `https://abu-hamad.de/map/` by a Cloudflare
Worker; mobile browsers (320px+ phones, landscape phones) and desktop browsers (>= 768px).

**Project Type**: Static web frontend (MapLibre GL map). No backend; source is `src/site/`.

**Performance Goals**: All interactions within the existing 2 s interaction budget (baseline
80-211 ms; SC-006). Expand/collapse must be a compositor-only `transform`/`opacity` transition
(no layout jank). No regression in first usable map (no new blocking work, SC-013).

**Constraints**:
- Zero new network requests, no server, static bundle functional offline on first load
  (FR-012, SC-007). Pure CSS/HTML/JS rework of existing elements; no new `fetch`, no new sources.
- No new features: never add, remove, or rename any existing feature or control; Bäume,
  Helligkeit, first-visit story modal, city-overview, district popup, building popup,
  attribution, Impressum keep current behaviour (FR-010).
- CSP `script-src 'self'`; no inline scripts (existing index.html CSP).
- German copy only, no em-dashes, no en-dashes, hyphens only inside compounds (FR-011, feature
  007 convention). The existing `UNAVAILABLE` en-dash constant (FR-009) is unchanged.
- Touch targets >= 44x44 px with >= 8 px spacing on mobile (FR-003); WCAG AA contrast; keyboard
  operable; visible focus (FR-014).
- No `*.pmtiles` or > 50 MiB `*.geojson` tracked (OR-005) — this feature touches only
  `src/site/{index.html,main.js,style.css}` and tests, so OR-005 is unaffected.
- Existing acceptance suites stay green (SC-008); `make check-public` stays clean.

**Scale/Scope**: One static bundle, single map page. Changes confined to `src/site/`
(index.html DOM, main.js interaction wiring, style.css layout/theme) plus tests and
`validation/perf-budget.json` (extend `interaction_latency_ms` with `surface_toggle`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No constitution file exists in the repository, so no constitution gates
are defined. The project's standing governance gates (documented in README/DEVELOPMENT.md and
enforced by the Makefile) are adopted as the applicable constitution:

| Gate | Source | Status |
|------|--------|--------|
| One commit per accepted spec/plan/slice/milestone (OR-004) | DEVELOPMENT.md | PASS |
| No `*.tif`/`*.pmtiles`/>50 MiB `*.geojson` tracked (OR-005) | DEVELOPMENT.md | PASS (untouched) |
| Public-release scan clean: no personal paths/credentials/internal tooling (`make check-public`) | DEVELOPMENT.md / Makefile | PASS (must re-verify) |
| Existing acceptance suites green (SC-008) | DEVELOPMENT.md / Makefile | PASS (must re-run) |
| Performance budget holds: interactions <= 2 s, no first-usable-map regression (SC-006/SC-013) | `validation/perf-budget.json` | PASS (must re-measure) |
| Feature parity: no feature add/remove/rename (FR-010) | spec | PASS |
| Zero new network requests, static offline bundle (FR-012/SC-007) | spec | PASS |
| German copy, no em/en dashes (FR-011, feature 007) | spec | PASS |

No violations. No complexity justification table required.

## Project Structure

### Documentation (this feature)

```text
specs/012-mobile-native-ux/
├── plan.md              # This file (plan command output)
├── research.md          # Phase 0 output (plan command)
├── data-model.md        # Phase 1 output (plan command)
├── quickstart.md        # Phase 1 output (plan command)
├── contracts/           # Phase 1 output (plan command)
│   ├── README.md
│   ├── layout-ux.md
│   ├── surface-interaction.md
│   └── touch-a11y-copy.md
└── tasks.md             # Phase 2 output (tasks command - NOT created by the plan step)
```

### Source Code (repository root)

```text
src/site/                 # static frontend, no build tool
├── index.html            # DOM: #map, #surface (header/body), #attribution, .legal-link, story modal
├── main.js               # MapLibre init, popup/surface/setPadding wiring, controls
├── style.css             # theme + responsive layout (bottom sheet / panel), motion, touch targets
├── style.json            # map style (UNTOUCHED: palette, layers, metadata stay verbatim)
├── attribution.html
└── impressum.html

tests/
├── acceptance/
│   └── test_style.py     # EXTENDED: #surface markup, touch-target CSS, reduced-motion query
└── frontend/
    ├── smoke_us1.md      # existing, unchanged
    ├── smoke_us2.md      # existing, unchanged
    ├── smoke_us3.md      # existing, unchanged
    └── smoke_mobile.md   # NEW: mobile/desktop UX + parity manual checklist (US1-3, edge cases)

validation/
└── perf-budget.json      # re-measure; add surface_toggle to interaction_latency_ms
```

**Structure Decision**: The feature is confined to the existing static frontend. `src/site/`
already contains the map HTML, JS, and CSS; there is no backend, pipeline change, or new module
tree. The single-file structure is retained; only `index.html`, `main.js`, `style.css` are
edited, `tests/acceptance/test_style.py` is extended, `tests/frontend/smoke_mobile.md` is added,
and `validation/perf-budget.json` is re-measured. `src/site/style.json` (palette, layers,
metadata) is deliberately untouched to preserve the published default view (SC-004).

## Complexity Tracking

No constitution violations; table intentionally empty.
