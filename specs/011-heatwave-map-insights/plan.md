# Implementation Plan: Heatwave Map Insights

**Branch**: `011-heatwave-map-insights` | **Date**: 2026-08-06
(re-planned after the scope clarification) | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification `specs/011-heatwave-map-insights/spec.md`
(updated 2026-08-06 by the clarify step, Option B)

## Summary

Three data-derived additions to the static Mannheim tree-cover map,
answering the heatwave question the map's story modal poses (the 30 %
shade guideline from the SPIEGEL report): clickable Stadtteile with
derived statistics, a city overview panel, and a district line in the
building popup. Everything is precomputed at publish time from the
accepted dataset and shipped inside already-fetched resources — zero
new network requests beyond the one stadtteile.geojson source
(FR-010, SC-007):

- District statistics ride on the new `dist/stadtteile.geojson` layer
  (official GDI-MA districts, reprojected 25832 → 4326, centroid-in-
  polygon join at publish time; R-2/R-3).
- City statistics live in `style.json` `metadata.city_stats`, patched
  by publish.py like the existing `mannheim_bbox` (R-4).
- The building popup gains district name + district mean via
  `querySourceFeatures('stadtteile')` (R-5).

The originally planned "Hitzebelastung" heat-exposure view (exposure
classes, view toggle, class legend, popup class line) was **removed
from scope on 2026-08-06**: it re-encodes the same per-building values
with no new information and adds a second toggle that risks confusing
users. Because the heat view was already implemented and shipped
during the earlier pass, this plan's first workstream **reverts every
trace of it** (values.py `heat_class`, the frontend toggle/legend/
class popup, its tests, README and attribution copy, perf keys, the
pmtiles size literal), and the second workstream **completes and
re-validates the surviving US2-US4 scope** (already implemented and
verified; re-verified after the revert).

Reference numbers recomputed from the accepted data on 2026-08-06:
city mean 22.2 %, 24.1 % of buildings at or above the 30 % guideline,
district range 9.6 % (Innenstadt, 98.2 % below guideline) to 34.5 %
(Niederfeld), 153,524 detected tree areas.

## Technical Context

**Language/Version**: Python 3.11 (pipeline), vanilla JS (frontend,
no build tool); Node 22 for measurement scripts. Pipeline runs via
`make` / `.venv/bin/python -m src.pipeline.cli`.

**Target Platform**: Modern browser WebGL 2; viewport widths ≥320 px;
served as static Worker assets + R2 (unchanged deploy).

**Project Type**: Static web map with an offline Python data pipeline.

**Performance Goals**: Unchanged budgets: first usable map ≤10 000 ms
(baseline 2482 ms; stadtteile.geojson adds ~373 KB to first paint),
interactions ≤2000 ms (baseline 80-341 ms). New interactions
(`district_click`, `panel_render`) measured into
`interaction_latency_ms` (SC-006).

**Constraints**:
- FR-010 / SC-007: zero new network requests beyond the one
  stadtteile.geojson source; all derived data in already-fetched
  resources (stadtteile source, style.json metadata). CSP
  `script-src 'self'`; no inline scripts.
- publish.py style quarantine: `available_sources` must gain
  `'stadtteile'` or the new source is stripped from dist/style.json.
- `tests/acceptance/test_style.py` asserts the exact layer order and
  the verbatim buildings palette in `src/site/style.json`; the
  palette stays untouched (SC-004), `EXPECTED_LAYERS` gains the one
  `stadtteile-fill` layer.
- OR-005: no `*.pmtiles` or >50 MiB `*.geojson` tracked;
  stadtteile.geojson is 373 KB (fine).
- FR-011: German copy, no em/en dashes, hyphens only in compounds.
- SC-004: default view unchanged — no new view, no new toggle, the
  published palette stays verbatim.
- Deploy: stadtteile.geojson (373 KB) and style.json metadata ride the
  ≤25 MiB Worker-asset path; pmtiles keep the R2 path. The `cmd_verify`
  size literal in deploy-cf.sh is reverted to the regenerated
  buildings.pmtiles size (expected 34023835).

## Gates

Repo gates (README/Makefile/DEVELOPMENT.md, OR-004/005/006/007) plus
the approved feature spec, re-evaluated after the scope change:

| Gate | Source | Status |
|------|--------|--------|
| G1 OR-004: one commit per accepted spec/plan/slice/milestone | README "Governance", Makefile `commit-*` | PASS - plan lands via `make commit-plan`; the revert + re-validation land as slices via `make commit-slice` |
| G2 OR-005: no `*.tif`, `*.pmtiles`, >50 MiB `*.geojson` tracked | `scripts/check_or005.py` | PASS - new data is 373 KB stadtteile geojson (derived, in dist/ which is not tracked); buildings files revert to pre-feature state |
| G3 FR-010 / SC-007: no new network requests beyond the one source | Feature spec | PASS by design - stats ride on stadtteile.geojson source and style.json metadata; no fetch added |
| G4 FR-012 / SC-004: existing behavior unchanged | Feature spec | PASS by design - no new view or toggle; district layer is a transparent fill below buildings; default legend untouched |
| G5 SC-008: existing suites green + check-public clean | Feature spec + DEVELOPMENT.md | PASS by design - contract changes (EXPECTED_LAYERS, city panel) are deliberate test updates; heat-class tests removed with the revert |
| G6 SC-006: perf budgets hold | Feature spec + perf-budget.json | PASS by design - 373 KB new source with 7.5 s first-paint headroom; interactions are paint/query ops within the 2 s budget; re-measured in quickstart S4 |
| G7 FR-013: accessibility of new popups/panel | Feature spec | PASS by design - popups have close buttons and wrap without viewport overflow; panel is plain text with sufficient contrast |

No gate violations; no unjustified complexity.

**Post-design re-check (after the scope change)**: all gates still
hold. The revert adds one derived-attribute removal, the stadtteile
source (373 KB), one transparent layer, and one metadata block; the
pmtiles size literal is the only deploy change.

## Project Structure

```text
specs/011-heatwave-map-insights/
├── spec.md            # file (specify command output; US1 removed)
├── plan.md            # file (this document)
├── research.md        # Phase 0 output: R-1..R-8 decisions
├── data-model.md      # Phase 1 output: District stats, CityStats
├── quickstart.md      # Phase 1 output: S1..S5 runnable validation
├── contracts/         # Phase 1 output
│   ├── README.md
│   ├── district-stats.md      # layer, derivation, popups, click arbitration
│   ├── city-overview.md       # metadata schema, panel content and placement
│   └── publish-bundle.md      # pipeline, manifest, attribution, release
│   (heat-exposure-view.md deleted with the scope change)
└── tasks.md           # Phase 2 output (tasks command - NOT created here)
```

### Source Code (repository root)

```text
src/
├── pipeline/
│   ├── values.py      # EDIT: REVERT heat_class() fn + output attribute (R-1)
│   └── publish.py     # EDIT: stadtteile transform + join + stats,
│                      #       metadata.city_stats, available_sources,
│                      #       REQUIRED_INPUTS, record (controls minus toggle)
└── site/
    ├── style.json     # EDIT: stadtteile source + stadtteile-fill layer
    ├── main.js        # EDIT: district popup + click arbitration, city panel
    │                  #       render, popup enrichment; REMOVE CLASS_LABEL /
    │                  #       HEAT_FILL_COLOR / wireHeatViewToggle /
    │                  #       refreshBuildingPopup / class line
    ├── index.html     # EDIT: #city-panel card; REMOVE Hitzebelastung button
    │                  #       and class legend block
    ├── style.css      # EDIT: district popup + city panel styles;
    │                  #       REMOVE class legend / toggle styles
    └── attribution.html  # EDIT: GDI-MA Stadtteile credit + statistics
                          #       derivation note; REMOVE class thresholds copy
artifacts.manifest.json # EDIT: stadtteile.geojson derived artifact entry
tests/
├── acceptance/
│   ├── test_style.py      # EDIT: EXPECTED_LAYERS + city-panel assertions;
│   │                      #       REMOVE class-legend assertions
│   ├── test_values.py     # EDIT: REMOVE heat-class consistency test
│   └── test_districts.py  # NEW: 38 districts, 4326, stats (SC-002),
│                          #      city stats (SC-003)
├── pipeline/
│   └── test_heat_class.py # DELETE with the revert
└── frontend/
    └── smoke_us6.md       # NEW/EDIT: districts, panel, popup context,
                           #      a11y, no-network; REMOVE heat-view scenarios
validation/
└── perf-budget.json   # EDIT: remove heat_toggle_* keys (SC-006)
```

**Structure Decision**: the existing flat single-project layout is
preserved. publish.py is the single place where derived statistics are
computed and written into the bundle. The district layer ships as a
plain GeoJSON source (matching the existing `boundary` pattern) rather
than a tippecanoe tile set, because 373 KB does not justify a tile
set and the source must carry the statistics properties anyway. The
revert is a plain deletion slice: no new abstractions, no migration,
no compatibility shims.

## Complexity Tracking

> **Fill ONLY Constitution Check violations must be justified** No
> Constitution Check violations; table intentionally empty. (The
> constitution file is absent from this repo; the governing gates are
> the README/Makefile governance rules listed above.)

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |
