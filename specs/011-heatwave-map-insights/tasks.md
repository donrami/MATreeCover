---
description: "Task list for Heatwave Map Insights implementation (2026-08-06 scope clarification, Option B)"
---
# Tasks: Heatwave Map Insights

**Input**: Design documents `specs/011-heatwave-map-insights/`
**Prerequisites**: plan.md (required), spec.md (required user stories), research.md, data-model.md, contracts/
**Tests**: Included per plan R-7 and spec SC-002..SC-009 (repo convention: acceptance pytest defends data/style contracts; manual smoke checklists defend browser behavior; SC-008 gates on all suites green). Not strict TDD; smoke checklist sections are written within each story phase as the acceptance record.
**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: run in parallel (different files, no dependencies)
- **[Story]**: user story the task belongs to (US2..US4; US1 was removed from scope on 2026-08-06)
- File paths included in every description
- Path conventions: single project — `src/`, `tests/`, repo root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify the environment the pipeline and frontend work depend on

- [X] T001 Verify prerequisites: run `bash scripts/check-prereqs.sh` (python 3.11, tippecanoe >= 2, workspace readable at `data/archive/workspace`); confirm a clean worktree for the OR-004 slice commits (`make commit-slice`)

**Checkpoint**: Environment verified; all later phases assume these prereqs hold.

## Phase 2: Foundational - Heat-View Revert + Data Regeneration (Blocking Prerequisites)

**Purpose**: The Hitzebelastung heat-exposure view was removed from scope on 2026-08-06 (clarification Option B). The code already shipped with it must be reverted to the pre-feature contract (research R-1) and the pipeline re-run so the surviving district/city derivations are regenerated from the reverted building values (FR-007). Nothing user-facing is re-validated until this phase completes.

**⚠️ Blocks US2..US4 - the revert touches every file the stories re-verify**

### Revert: pipeline (R-1)

- [X] T002 Remove the `heat_class(value)` function and the `heat_class` output attribute from `compute_building_values` in `src/pipeline/values.py` (restore the pre-feature building schema: `id`, `value`, `value_str`, `has_value`, `completeness`, `in_boundary`; contract `contracts/district-stats.md`)
- [X] T003 [P] Delete `tests/pipeline/test_heat_class.py`
- [X] T004 [P] Remove the heat-class consistency test (band rule for all valued buildings, `None` iff `has_value` false) from `tests/acceptance/test_values.py` (SC-001 is dropped with the view)
- [X] T005 Regenerate `data/archive/workspace/buildings.geojson` via `make values` (idempotent; RSS ~2.8 GiB < 12 GiB OR-001 gate); verify no `heat_class` attribute remains in the output
- [X] T006 Rebuild `dist/buildings.pmtiles` via `make pmtiles-buildings` (RSS ~6.1 GiB < gate); record the regenerated file size from `dist/buildings.pmtiles` (expected 34023835) for T012

### Revert: frontend (R-1)

- [X] T007 Remove `CLASS_LABEL`, the heat paint-expression constants (`HEAT_FILL_COLOR`), `wireHeatViewToggle` (paint-swap + restore), the legend-block swap and the popup class line from the building popup assembly in `src/site/main.js`
- [X] T008 [P] Remove the "Hitzebelastung" button from `#controls` and the class legend block (swatch rows + "Richtwert 30 %" line) from `#legend` in `src/site/index.html`
- [X] T009 [P] Remove the class legend and toggle `.active` styles from `src/site/style.css` (including the 480 px flex-row collapse handling)
- [X] T010 [P] Remove the class-thresholds sentence from the "Genauigkeit der Baumwerte" section in `src/site/attribution.html` and the Hitzebelastung bullet from `README.md` (R-1 copy trim; FR-011 dash rule)

### Revert: perf budget and deploy gate

- [X] T011 [P] Remove the `heat_toggle_on` / `heat_toggle_off` keys from `interaction_latency_ms` in `validation/perf-budget.json` (SC-006)
- [X] T012 Revert the `cmd_verify` buildings.pmtiles size literal in `scripts/deploy-cf.sh` (`content-range: bytes 0-1023/<size>`; read the size recorded in T006, expected 34023835)

### Data regeneration and regression gate

- [X] T013 Run `make accept` (manifest gate incl. the `stadtteile.geojson` derived-artifact entry in `artifacts.manifest.json`, kind `stadtteile`, source "Stadt Mannheim, GDI-MA", license dl-de/by-2-0, lineage [verification/stadtteile.geojson, buildings.geojson])
- [X] T014 Run `make publish`; verify S1 expectations from `quickstart.md`: `dist/stadtteile.geojson` (38 features, EPSG:4326, `n_buildings` / `mean_value` / `share_lt30` on every feature), `metadata.city_stats` = `{"mean_value_pct": 22.2, "share_gte30_pct": 24.1, "tree_count": 153524}`, `dist/buildings.geojson` carries no `heat_class`, `dist/manifest.json` lists the new artifact, `available_sources` includes `'stadtteile'` (style quarantine keeps the source)
- [X] T015 Regression checkpoint: `.venv/bin/python -m pytest tests/acceptance tests/pipeline -q` all green (incl. `tests/acceptance/test_districts.py` SC-002/SC-003 and the updated `tests/acceptance/test_style.py`), no `tests/pipeline/test_heat_class.py` exists, `make check-public` clean (SC-008)

**Checkpoint**: Foundation ready - heat view fully reverted, derived data regenerated from reverted values, acceptance green. User story re-validation can start in parallel.

## Phase 3: User Story 2 - Neighborhood Comparison via Stadtteile (Priority: P2)

**Goal**: All 38 Stadtteile are clickable (transparent `stadtteile-fill` layer) and open a popup with derived statistics (building count, mean tree cover, share below 30 %); click arbitration reworked so building/district/empty-space clicks never double-popup. Implemented in the earlier pass; this phase re-verifies it against the reverted bundle and fixes regressions (FR-006, FR-007, FR-009, FR-013).

**Independent Test**: Serve `dist/`, click all 38 Stadtteile and verify the popup appears with statistics matching an independent recomputation for at least 5 sampled districts (Innenstadt mean ~9.6 %, share ~98.2 %; Niederfeld mean ~34.5 %); empty-space click closes both popups.

### Tests User Story 2

- [X] T016 [US2] Update `tests/acceptance/test_style.py`: `EXPECTED_LAYERS` gains `stadtteile-fill` pinned between `outside-mask` and `buildings-fill`; source assertions gain `stadtteile` (contract update, SC-004/SC-008)
- [X] T017 [P] [US2] Rewrite the US2 sections of `tests/frontend/smoke_us6.md` (district popup content: name, Gebäude, Baumanteil im Durchschnitt, Anteil unter 30 %; Innenstadt vs Niederfeld direction; click arbitration incl. empty-space close and district-click-replaces-building-popup; keyboard reachability and closable popups per FR-013; remove the heat-view scenarios S3.1-3.2/S3.7 from the old checklist)

### Implementation User Story 2

- [X] T018 [US2] Verify the `stadtteile` GeoJSON source (`stadtteile.geojson`) and `stadtteile-fill` layer (transparent fill-opacity 0, no stroke, between `outside-mask` and `buildings-fill`) are present in `src/site/style.json` after the revert (research R-3/R-4); fix if disturbed
- [X] T019 [US2] Verify the map-level click arbitration in `src/site/main.js` per `contracts/district-stats.md`: building hit (`queryRenderedFeatures` on `buildings-fill`) wins and closes the district popup; else district hit (`stadtteile-fill`) opens the district popup (own `maplibregl.Popup`, own className, offset 8, closable) with German labels and dot-decimal/thin-space formatting ("3 383", "9.6 %", "98.2 %"); else both popups close; "keine Daten" for null `mean_value`
- [X] T020 [P] [US2] Verify district popup styles in `src/site/style.css` (own className, max-width, wraps, never overflows the viewport on narrow screens; sufficient contrast on the dark background per FR-013)

**Checkpoint**: US2 fully functional and testable independently.

## Phase 4: User Story 3 - City Overview Panel (Priority: P3)

**Goal**: A `#city-panel` card in the left stack shows derived city stats (mean 22.2 %, share >= 30 % 24.1 %, 153 524 tree areas) read from `metadata.city_stats`; hides itself if metadata is missing (FR-008, FR-010). Implemented in the earlier pass; this phase re-verifies it against the reverted bundle and fixes regressions.

**Independent Test**: Serve `dist/`, read the panel, verify the three numbers match quickstart S1 values (within 0.5 pp mean / 1 pp shares / 1 % tree count, SC-003) and the district-stats consistency invariant (`share_gte30_pct` == `100 - sum(n_buildings * share_lt30) / sum(n_buildings)`, within 0.1 pp).

### Tests User Story 3

- [X] T021 [US3] Add the `#city-panel` presence assertion to `tests/acceptance/test_style.py` (sequential with T016: same file)
- [X] T022 [P] [US3] Rewrite the US3 section of `tests/frontend/smoke_us6.md` (panel values match data: 22.2 %, 24.1 %, 153 524; narrow-screen readability; panel included in the overlap matrix at 320/480/768/1280/1920 px per the 004 technique)

### Implementation User Story 3

- [X] T023 [P] [US3] Verify the `#city-panel` card (empty container) exists in `#left-stack` below `#legend` in `src/site/index.html` after the revert (German copy rendered by main.js, none hardcoded in HTML; contract `contracts/city-overview.md`)
- [X] T024 [P] [US3] Verify city panel styles in `src/site/style.css` (compact card, no overlap with existing cards, 480 px bottom-strip behavior with `column-reverse`, no horizontal overflow per FR-013)
- [X] T025 [US3] Verify the panel renders from `map.getStyle().metadata.city_stats` in `src/site/main.js` at map load (no fetch; labels "Mannheim im Überblick", "Durchschnittlicher Baumanteil im 60-m-Umkreis", "Gebäude mit ausreichender Beschattung (30 %)", "Anzahl der erkannten Baumflächen"; dot decimals, thin-space thousands separator; panel hides itself when `metadata.city_stats` is missing)

**Checkpoint**: US3 fully functional and testable independently.

## Phase 5: User Story 4 - Building Popup with District Context (Priority: P4)

**Goal**: The building popup gains district name + district mean via `querySourceFeatures('stadtteile')` at the clicked point; buildings outside all districts show no district line; null district mean shows "keine Daten" (FR-009). Implemented in the earlier pass; this phase re-verifies it against the reverted bundle.

**Independent Test**: Serve `dist/`, click buildings in at least three different Stadtteile and verify the popup shows the correct district name and district mean; the district mean equals the district popup's value (same property, same formatting).

### Tests User Story 4

- [X] T026 [P] [US4] Rewrite the US4 section of `tests/frontend/smoke_us6.md` (district line correct in 3 districts; building outside all districts shows value without a district line; "keine Daten" fallback path)

### Implementation User Story 4

- [X] T027 [US4] Verify the district lookup and the two popup lines ("Stadtteil", "Durchschnitt im Stadtteil") in the building popup assembly in `src/site/main.js` (no fetch; lookup via `map.querySourceFeatures('stadtteile')`; no district line when the lookup misses; "keine Daten" when `mean_value` is null; district mean formatting identical to the district popup; the existing en-dash UNAVAILABLE constant stays untouched)

**Checkpoint**: US4 fully functional; all stories independently testable.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Release hygiene and regression across all stories (FR-014, SC-004..SC-009)

- [X] T028 [P] Verify `src/site/attribution.html`: new h2 "Stadtteile" after "Gebäude und Stadtgrenze" crediting "Stadt Mannheim, GDI-MA, dl-de/by-2-0 (Daten verändert)"; a new paragraph in the "Genauigkeit der Baumwerte" section explaining the district and city statistics are computed from the published building values (same estimation uncertainty) with the metric caveat (the 30 % reference is the site's 60-m framing; the supporting 3-30-300 evidence is neighborhood canopy cover, a related but distinct metric, per research R-8); no class-thresholds sentence remains (FR-014, SC-009; `contracts/publish-bundle.md` §Attribution)
- [X] T029 Update `README.md`: remove the Hitzebelastung bullet (R-1 trim) and document the surviving user-facing features (clickable Stadtteile with statistics, city overview panel, building popup district context) with dash-free copy (FR-011)
- [X] T030 [P] Re-measure performance per `validation/perf-budget.json` method (CDP throttled 25 Mbps / 50 ms, cold cache, Chromium headless 1280x800): `interaction_latency_ms` keeps `district_click` and `panel_render`, each under the 2000 ms budget; `first_usable_ms` under 10000 ms (stadtteile.geojson adds ~373 KB to first paint; ~7.5 s headroom vs the 2482 ms baseline); record results in `validation/perf-budget.json` (SC-006)
- [X] T031 [P] Add the cross-cutting smoke sections to `tests/frontend/smoke_us6.md`: zero new network requests (DevTools shows only the 11 known requests, SC-007), no new localStorage keys beyond `matreecover.story-dismissed`, default view renders exactly as published with no Hitzebelastung button (SC-004), Bäume toggle and brightness slider still work (FR-012), overlap matrix at 320/480/768/1280/1920 px incl. `#city-panel` (FR-013)
- [X] T032 Final regression: full pytest suite (`tests/acceptance`, `tests/pipeline`), smoke checklists us1-us6 (log rows to `validation/event.log.jsonl` per project convention), `make check-public`, `make check-or005` (SC-008)
- [X] T033 Run `quickstart.md` S1-S5 end to end; S5 deploy steps are owner-gated (stop before `npx wrangler deploy` if not releasing); verify `dist-assets/attribution.html` stays in sync with the GDI-MA credit and the derivation note (FR-014)

**Checkpoint**: Feature complete, regression-clean, release-ready.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies, start immediately
- **Foundational (Phase 2)**: depends on Setup; **blocks US2..US4** (revert touches every file the stories re-verify; derived data must be regenerated from reverted values)
- **User Stories (Phase 3-5)**: depend on Foundational completion; run in priority order (P2 → P3 → P4), or in parallel once T015 passes
- **Polish (Phase 6)**: depends on all stories complete (T032/T033 last)

### User Story Dependencies

- **US2 (P2)**: Foundational only; no story dependencies
- **US3 (P3)**: Foundational only; no story dependencies
- **US4 (P4)**: Foundational + US2's `stadtteile` source in style.json (`querySourceFeatures('stadtteile')` needs it)
- US2 and US3 both edit `tests/acceptance/test_style.py` (T016 before T021) and `src/site/main.js` / `src/site/index.html` (sequence T019 before T025 and T023 to keep single-implementer-per-file); US4's T027 follows US2's T019 in `main.js`

### Within Each Story

- Contract/test maintenance before UI verification (US2: T016/T017 before T018-T020; US3: T021/T022 before T023-T025)
- Smoke checklist section written within the story phase as its acceptance record
- Story complete before moving to the next priority

## Parallel Opportunities

- Foundational: T003/T004 (test deletions) parallel; T007/T008/T009/T010/T011 (main.js, index.html, style.css, attribution/README, perf) parallel; T002 → T005 → T006 → T012 sequential (data + deploy gate); T013/T014/T015 after T005/T006
- US2: T016 + T017 parallel with T018-T020; T020 (style.css) parallel with T018/T019
- US3: T023 + T024 (index.html, style.css) parallel; T025 after; T022 parallel with all
- US4: T026 parallel with T027
- Polish: T028, T029, T030, T031 parallel (different files); T032/T033 last
- Cross-story: US2, US3, US4 can be staffed in parallel after T015 (different files per story); sequence US2 → US3 → US4 on the shared `main.js` / `test_style.py`

## Parallel Example: Foundational revert

```bash
# Launch together (different files):
#   T003  delete tests/pipeline/test_heat_class.py
#   T004  remove heat-class test from tests/acceptance/test_values.py
#   T007  remove heat-view code from src/site/main.js
#   T008  remove Hitzebelastung button + class legend from src/site/index.html
#   T009  remove class legend/toggle styles from src/site/style.css
#   T010  trim attribution.html + README.md copy
#   T011  remove heat_toggle_* keys from validation/perf-budget.json
# Then sequentially:
#   T002  values.py revert  ->  T005  make values  ->  T006  make pmtiles-buildings  ->  T012  deploy-cf.sh literal
```

## Parallel Example: User Story 2

```bash
# Launch together (different files):
#   T016  test_style.py EXPECTED_LAYERS + stadtteile source assertions
#   T017  smoke_us6.md US2 sections
#   T020  district popup styles in src/site/style.css
# Then sequentially in the layer + main.js:
#   T018  stadtteile source + stadtteile-fill layer in src/site/style.json
#   T019  click arbitration + district popup in src/site/main.js
```

## Implementation Strategy

### MVP First (Foundational Revert + US2 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T015, CRITICAL - blocks all stories; the revert is the only genuinely new code work in this plan)
3. Complete Phase 3: User Story 2 (T016-T020)
4. **STOP VALIDATE**: smoke_us6.md US2 sections; default view regression (smoke us1..us5); SC-004 / SC-007 checks
5. Deploy/demo if ready (release flow in `contracts/publish-bundle.md`, owner-gated)

### Incremental Delivery

1. Setup + Foundational → foundation ready (heat view gone, derived data consistent with reverted values)
2. Add US2 → re-validate independently → deploy/demo (MVP)
3. Add US3 → re-validate independently → deploy/demo
4. Add US4 → re-validate independently → deploy/demo
5. Each story adds value without breaking previous stories (SC-004 regression gate at each step)

### Parallel Team Strategy

1. Team completes Setup + Foundational together (T001-T015)
2. After T015: one developer per story (US2, US3 in parallel; US4 after US2's style.json source lands, or same developer as US2)
3. Polish (T028-T031) by any remaining capacity; T032/T033 gated on everything else

## Notes

- Commits follow OR-004: one commit per slice/milestone via `make commit-slice` / `make commit-milestone MSG="..."` (clean worktree required); the revert is one slice, each re-validated story is a slice
- RSS gates: `values` ~2.8 GiB, `pmtiles-buildings` ~6.1 GiB, both under the 12 GiB OR-001 abort
- German copy rule (FR-011): no em/en dashes in any new user-facing copy, hyphens only inside compounds; the popup's existing en-dash UNAVAILABLE constant is untouched; percentages use dot decimals ("22.2 %"), thousands use thin space ("153 524")
- Do not touch: `buildings-fill` palette in `src/site/style.json` (published contract, SC-004), the Bäume toggle, the brightness slider, the story modal, the disclaimer, the `matreecover.story-dismissed` localStorage key
- Default view must render byte-identical to the published map (SC-004) - verify at every story checkpoint
- `stadtteile.geojson` (373 KB) and style.json ride the Worker-assets path (<= 25 MiB); pmtiles stay on R2; deploy flow needs no structural changes beyond the T012 size literal
