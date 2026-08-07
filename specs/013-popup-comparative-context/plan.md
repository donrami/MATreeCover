# Implementation Plan: Popup Comparative Context

**Branch**: `013-popup-comparative-context` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/013-popup-comparative-context/spec.md`

## Summary

Make the building and district popups instantly informative: a visitor sees **what** the
number is, **how good or bad it is** relative to the district and the whole city, and — for
districts — **where the district stands** among all 38 Mannheim districts. Pure client-side
presentation change in `src/site/main.js` + `style.css`: no pipeline, data, layer, or
interaction-model changes (FR-015, out-of-scope boundary).

- Building popup: value headline, 30 % badge ("erreicht"/"verfehlt"), district-average
  comparison and city-average comparison each with signed delta (pp) + assessment word,
  footnote (FR-001..FR-006, FR-012).
- District popup: name header, mean headline, rank "Platz X von 38" (FR-009), quartile band
  badge (FR-010), city-average comparison with signed delta (FR-008), existing Gebäude +
  Anteil unter 30 % lines kept (FR-007), footnote (FR-012).
- Rank/quartile computed client-side from the 38 district features already in the published
  bundle, fetched once from the cached `stadtteile.geojson` (no new network transfer).
- All comparative metrics derive from data already in the bundle: district `mean_value`/
  `n_buildings`/`share_lt30`, style-metadata `city_stats.mean_value_pct` (same reference as
  the "Mannheim im Überblick" panel).
- SC-003 (100 % rank/quartile cross-check) automated via a new pytest that runs the real
  `dist/main.js` rank function in a node VM against a Python reference computation.

## Technical Context

**Language/Version**: JavaScript (ES2021+, no build tool, classic `<script>` tags, vendored
MapLibre GL JS 5.7.1 + pmtiles 4.4.0 in `src/site/vendor/`); tests in Python 3.11+ (pytest).

**Primary Dependencies**: MapLibre GL JS 5.7.1 (popups, `querySourceFeatures`,
`getStyle`); no new third-party dependencies (existing project constraint — static bundle,
CSP `script-src 'self'`).

**Storage**: N/A. No server, no database. Rank table computed at runtime from the
already-loaded `stadtteile.geojson` (browser-cached fetch, once); popup state is the
existing MapLibre popup instances (session-only).

**Testing**: pytest (existing suite in `tests/`); new `tests/acceptance/test_rank.py`
(reference rank/quartile computation + node-VM cross-check of the real JS function,
SC-003); extended frontend smoke checklist `tests/frontend/smoke_us7.md` (US1/US2/US3
independent tests, SC-001/002/004/005/006/007); static CSS assertions extended in
`tests/acceptance/test_style.py`. `make check-public` stays clean.

**Target Platform**: Static web bundle served at `https://abu-hamad.de/map/` by the
Cloudflare Worker; desktop and mobile browsers (>= 360 px viewport width, FR-016/SC-006).

**Project Type**: Static web frontend (MapLibre GL map). No backend; source is `src/site/`.

**Performance Goals**: No new interactions; rank computed once at map load (parse of the
already-fetched 373 KB GeoJSON, O(n log n) sort, n = 38) and O(1) lookups per popup render.
Existing 2 s interaction budget (baseline 80-211 ms) must hold; re-measured in quickstart S5.

**Constraints**:
- No pipeline, data, publish-time, style.json (layers/palette), or interaction/arbitration
  changes (out of scope; FR-015). Only `src/site/main.js` (popup content + pure helpers)
  and `src/site/style.css` (popup hierarchy, badge, footnote, mobile scroll) are edited.
- German copy only; dot-decimal convention kept (no German-comma reform); "pp" for deltas;
  0.1 pp neutral band; no em/en dashes in new prose (hyphens only in compounds); minus sign
  U+2212 in deltas, "±" for neutral (R-3).
- Rank/quartile must come from the full 38-district set, not the viewport-limited
  `querySourceFeatures` result (R-1). Deterministic tie-break: mean desc, then name
  ascending; distinct sequential ranks (FR-009).
- Every color-coded fact also carries a text label (FR-013); colors follow the existing
  palette semantics (low tree share = warm, high = cool) (R-12).
- Degradation: building without value (FR-006), district without mean (FR-011), missing
  city stats (FR-014, rank/quartile still render), fewer than two valid district means
  (rank/quartile hidden).
- Verification asset `verification/stadtteile.geojson` (38 districts, geometry only)
  exists for the SC-003 cross-check; published stats live in `dist/stadtteile.geojson`.

**Scale/Scope**: 38 districts, ~93k buildings; single-page static bundle; popup content
change confined to two popup renderers and one load-time computation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No constitution file exists in the repository, so no constitution gates
are defined. The project's standing governance gates (documented in README/DEVELOPMENT.md and
enforced by the Makefile) are adopted as the applicable constitution, as in plans 011/012:

| Gate | Source | Status |
|------|--------|--------|
| One commit per accepted spec/plan/slice/milestone (OR-004) | DEVELOPMENT.md | PASS |
| No `*.tif`/`*.pmtiles`/>50 MiB `*.geojson` tracked (OR-005) | DEVELOPMENT.md | PASS (untouched) |
| Public-release scan clean: no personal paths/credentials (`make check-public`) | DEVELOPMENT.md / Makefile | PASS (must re-verify) |
| Existing acceptance suites green (`make accept`) | DEVELOPMENT.md / Makefile | PASS (must re-run) |
| Performance budget holds: interactions <= 2 s, no first-usable-map regression | `validation/perf-budget.json` | PASS by design (must re-measure, S5) |
| Interaction/arbitration model unchanged (FR-015, features 002/011) | spec | PASS — only popup content changes |
| No pipeline/data/layer/palette changes (out-of-scope boundary) | spec | PASS — edits confined to main.js + style.css |
| German copy, dot-decimal, no color-only encoding (FR-013/FR-017) | spec | PASS by design |
| Popup fits/scrolls at 360 px (FR-016/SC-006) | spec | PASS by design (max-height + overflow, S4) |
| Rank/quartile 100 % match automated cross-check (SC-003) | spec | PASS — new pytest + node VM harness |

No violations; no complexity justification table required.

**Post-design re-check (after Phase 1)**: all gates still hold. The design edits only
`main.js` + `style.css` (G6, G7), fixes the German copy and color-with-text rule in
`contracts/popup-content.md` (G8), specifies scroll-within-popup for 360 px (G9), and
provides the automated node-VM cross-check in `tests/acceptance/test_rank.py` (G10).
No new files > 50 MiB, no personal paths, no perf-sensitive new interaction.

## Project Structure

### Documentation (this feature)

```text
specs/013-popup-comparative-context/
├── spec.md              # feature specification (clarify command output)
├── plan.md              # This file (plan command output)
├── research.md          # Phase 0 output: R-1..R-12 decisions
├── data-model.md        # Phase 1 output: Building Footprint, District, City Statistics, popup state
├── quickstart.md        # Phase 1 output: S1..S5 runnable validation
├── contracts/           # Phase 1 output
│   ├── README.md
│   ├── popup-content.md # popup hierarchy, exact German copy, delta rules, degradation
│   └── rank-quartile.md # rank/quartile algorithm, band formula, reference table, SC-003 harness
└── tasks.md             # Phase 2 output (tasks command - NOT created here)
```

### Source Code (repository root)

```text
src/site/                 # static frontend, no build tool
├── main.js               # EDIT: pure helpers (rank/quartile/delta/assessment), loadDistrictRankings(),
│                         #       reworked buildingPopupHtml + districtPopupHtml, cityStats(); handlers
│                         #       and arbitration UNTOUCHED (FR-015)
├── style.css             # EDIT: popup hierarchy styles (header/headline/badge/context/footnote),
│                         #       delta colors (palette semantics), max-height/overflow scroll (FR-016),
│                         #       width clamp for 360 px viewports
├── index.html            # UNTOUCHED (popups are JS-rendered)
├── style.json            # UNTOUCHED (layers, palette, metadata verbatim — out of scope)
├── attribution.html      # UNTOUCHED
└── impressum.html        # UNTOUCHED

tests/
├── acceptance/
│   ├── test_rank.py      # NEW: reference rank/quartile from dist/stadtteile.geojson (FR-009/FR-010)
│   │                     #       + node VM cross-check of dist/main.js rank function (SC-003)
│   └── test_style.py     # EDIT: static CSS assertions — popup hierarchy classes, badge colors with
│                         #       text labels, mobile max-height/overflow (FR-013/FR-016)
└── frontend/
    └── smoke_us7.md      # NEW: US1/US2/US3 manual checklist on the published bundle
                          #       (10 buildings, 10 districts, arbitration, 360 px, footnote)
```

**Structure Decision**: The feature is confined to the existing static frontend, mirroring
plans 011/012. `src/site/main.js` gains pure, top-level helper functions
(`computeDistrictRankings`, `quartileBand`, `classifyDelta`, `formatDelta`) that are
deliberately free of map/DOM access so the node VM test can load the published bundle and
exercise them directly (SC-003). `style.json`, `index.html`, pipeline, and the popup click
handlers/arbitration are untouched. One new pytest file and one new smoke checklist follow
the existing test layout.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No Constitution Check violations; table intentionally empty.
