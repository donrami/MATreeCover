---
description: "Task list for Popup Comparative Context"
---

# Tasks: Popup Comparative Context

**Input**: Design documents `/specs/013-popup-comparative-context/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, contracts/ (popup-content.md, rank-quartile.md), quickstart.md
**Tests**: Requested by spec.md SC-003 (automated rank/quartile cross-check via `tests/acceptance/test_rank.py`), plan.md (`tests/acceptance/test_style.py` static CSS/DOM assertions; `tests/frontend/smoke_us7.md` manual checklist), quickstart.md S5 (test_style.py green). Write story tests FIRST, fail before implementation.
**Organization**: Tasks grouped by user story, each independently implementable and testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: run in parallel (different files, no dependencies)
- **[Story]**: user story task belongs (US1, US2, US3)
- File paths included in descriptions

## Path Conventions

Static web frontend, no build tool, no backend. Files touched in this feature:

- `src/site/main.js` — EDIT: pure helpers (`computeDistrictRankings`, `quartileBand`, `classifyDelta`, `formatDelta`, `cityStats`), `loadDistrictRankings()`, reworked `buildingPopupHtml(props, lngLat)` + `districtPopupHtml(props)`. Click handlers/arbitration logic UNTOUCHED (FR-015)
- `src/site/style.css` — EDIT: popup hierarchy styles, badge/delta colors, footnote, mobile max-height/overflow (FR-016)
- `src/site/style.json` — **UNTOUCHED** (layers, palette, metadata verbatim — out of scope)
- `src/site/index.html` — **UNTOUCHED** (popups are JS-rendered)
- `tests/acceptance/test_rank.py` — NEW (SC-003: Python reference + node-VM cross-check)
- `tests/acceptance/test_style.py` — EDIT: static popup CSS assertions (FR-013, FR-016)
- `tests/frontend/smoke_us7.md` — NEW manual checklist (US1/US2/US3)
- `validation/perf-budget.json` — re-measure interaction latency (quickstart S5)
- `dist/` — regenerated via `make publish` (dist/main.js is a plain copy of src/site/main.js; required before the SC-003 JS cross-check passes)

**Shared contracts (read before implementing, all three stories)**: every metric derives from data already in the published bundle — district features in `dist/stadtteile.geojson` (`code`, `name`, `n_buildings`, `mean_value`, `share_lt30`; 38/38 means present) and `style.json` `metadata.city_stats.mean_value_pct = 22.2`. Formatting helpers already exist: `formatPercent` (dot decimal), `formatInteger` (thin-space thousands), `escapeHtml`, `UNAVAILABLE = '\u2013'`. German copy only, dot-decimal convention kept, "pp" deltas, minus sign U+2212 in deltas, "±" for neutral, no em/en dashes in new prose (hyphens only in compounds). Every color-coded fact also carries its text label (FR-013). `districtRankings` must come from the full 38-district set, never viewport-limited `querySourceFeatures` results (R-1).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm a clean, green baseline and feature branch before any popup rework so regressions are attributable (SC-008).

- [X] T001 Create and switch to branch `013-popup-comparative-context` (currently on `main`; note the modified `validation/event.log.jsonl` and untracked `specs/013-popup-comparative-context/` must come along); record baseline file sizes of `src/site/main.js` and `src/site/style.css` (pre-change baseline)
- [X] T002 Verify prerequisites (node >= 20 — v22.22.1 present; `verification/stadtteile.geojson` has 38 districts; `dist/stadtteile.geojson` has 38 features with 38/38 `mean_value`; `dist/style.json` `metadata.city_stats.mean_value_pct = 22.2`) and run the baseline acceptance suite (`.venv/bin/python -m pytest tests/`) plus `make check-public`; confirm both green and note the result before editing

**Checkpoint**: Baseline green on the feature branch; edits now proceed against a known-good state.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared pure helpers and popup CSS structure that BOTH popups depend on — delta classification/formatting (FR-003/FR-004/FR-008), city-stat access (FR-014), and the shared popup hierarchy/badge/delta color CSS (FR-013, R-12). No user story can start before this.

### Implementation — Foundational

- [X] T003 Add pure top-level helpers in `src/site/main.js` (no map/DOM access, node-VM loadable): `classifyDelta(delta)` returning `'above' | 'below' | 'neutral'` per the 0.1 pp band (`delta > 0.1` ⇒ above, `delta < -0.1` ⇒ below, `|delta| <= 0.1` ⇒ neutral, FR wording normative over Edge Cases wording) and `formatDelta(delta, cls)` rendering `±0.0 pp` for neutral (derived from the classification, so word and number never contradict), otherwise sign + magnitude rounded to 1 decimal half-up on the magnitude (`Math.abs(delta).toFixed(1)`) + ` pp`, plus sign `+`, minus sign U+2212 (`−2.3 pp`); plus the R-4 assessment-word map (building vs district: "über/unter dem Stadtteil-Durchschnitt" / "auf Stadtteil-Niveau"; building vs city and district vs city: "über/unter dem Stadtdurchschnitt" / "auf Stadtniveau")
- [X] T004 Add `cityStats()` in `src/site/main.js` returning `map.getStyle().metadata.city_stats.mean_value_pct` (number) or `null` when missing (R-5) — same source as `renderCityPanel()`, so popups and the "Mannheim im Überblick" panel can never contradict (FR-014)
- [X] T005 [P] Add shared popup content CSS in `src/site/style.css`: hierarchy block classes per FR-013 (header / headline / badge / context / footnote), badge base (pill with text label — never color-only, FR-013), delta color classes following R-12 palette semantics (positive/good → cool cyan family `#1db6ff`/`#39c2ff`, negative/bad → `#ffd524` warm, neutral gets no color), footnote "Was bedeutet das?" block base

**Checkpoint**: Shared helpers + popup structure CSS ready; all three stories can now proceed.

---

## Phase 3: User Story 1 — Building Value in Context (Priority: P1) 🎯 MVP

**Goal**: A building click immediately shows the tree-share value, whether it is above/below the district and city averages with signed deltas in pp, and whether it reaches the 30 % adequate-shading threshold — no mental arithmetic (FR-001..FR-006).

**Independent Test**: On the published bundle, click ten buildings in different districts. For each, read the value line and both comparison lines; verify the assessment words and deltas by cross-checking against the district mean and the city average 22.2 %.

### Tests User Story 1 (write FIRST, fail before implementation)

- [X] T006 [P] [US1] Extend `tests/acceptance/test_style.py` with static CSS assertions for the building popup: `.popup-badge` classes for "erreicht" (cool cyan family per R-12) and "verfehlt" (warm) both with text labels; footnote block present; hierarchy classes in FR-013 order. Run to confirm the assertions fail before the implementation exists

### Implementation User Story 1

- [X] T007 [US1] Rework `buildingPopupHtml(props, lngLat)` in `src/site/main.js` and delete `buildingDistrictHtml(lngLat)` (merge its district lookup into the single renderer, per R-6): district name header (FR-002, via `districtAt(lngLat)`); headline label "Baumanteil im 60-m-Umkreis" + value (FR-001, `value_str` + `%`, dot-decimal) or the `UNAVAILABLE` en-dash marker when `has_value === false` (FR-006, never a fabricated value); badge "erreicht" when `Number(value_str) >= 30` else "verfehlt", only when a value exists (FR-005; exactly 30.0 counts as erreicht); district comparison line "Durchschnitt im Stadtteil" with mean + signed delta + assessment word (FR-003); city comparison line "Stadtdurchschnitt" with `mean_value_pct` + signed delta + word (FR-004, only when value exists AND `cityStats()` is non-null); when `has_value === false` keep the plain district line "Durchschnitt im Stadtteil" with mean (FR-006) and skip badge/deltas/city line; footnote per R-8: "Was bedeutet das?" + "Der Baumanteil im 60-m-Umkreis ist der Anteil der Baumkronen an der Fläche im Umkreis von 60 m um das Gebäude. Ab 30 % gilt die Beschattung als ausreichend." (FR-012)
- [X] T008 [US1] Update the building click handler in `wireBuildingsInteractions()` in `src/site/main.js` to the single call `.setHTML(buildingPopupHtml(feature.properties || {}, event.lngLat))` (remove the old `+ buildingDistrictHtml(event.lngLat)` concatenation); leave popup instance creation, `closeOnClick: false`, close button, tooltip, hover cursor, and click arbitration untouched (FR-015)
- [X] T009 [P] [US1] Add building popup CSS in `src/site/style.css`: header + headline hierarchy prominence, badge colors (erreicht = cool cyan, verfehlt = warm per R-12) with text labels, delta line colors, footnote block styling for the building popup
- [X] T010 [US1] Verify all US1 acceptance scenarios (spec.md US1-S1..S6) against `contracts/popup-content.md`: a neutral building (|Δ| <= 0.1 pp) shows "auf …-Niveau" with "±0.0 pp" and no color; a building at exactly 30.0 % shows "erreicht"; a building without a value shows the en-dash marker with district lines and no deltas; word and sign never contradict

**Checkpoint**: US1 complete — building popup shows value + both comparisons + threshold badge, independently testable.

---

## Phase 4: User Story 2 — District Standing Among All Districts (Priority: P1)

**Goal**: A district click shows where the district stands — mean tree share, above/below the city average with signed delta, rank "Platz X von 38", and quartile band — while keeping the existing building-count and below-30 % lines (FR-007..FR-011).

**Independent Test**: On the published bundle, click ten districts. Verify each shown rank matches an independent computation of the 38-district ordering by mean tree share and the quartile label matches the rank band (reference table in `contracts/rank-quartile.md`).

### Tests User Story 2 (write FIRST, fail before implementation)

- [X] T011 [P] [US2] Write `tests/acceptance/test_rank.py` per R-10/SC-003: (1) Python reference — recompute ranks/quartiles from `dist/stadtteile.geojson` with the R-2 algorithm, assert ranks are exactly 1..38 unique, band bounds hold (1-10 / 11-19 / 20-28 / 29-38), and tied means order alphabetically (Friedrichsfeld before Neckarau at 21.5; Neckarstadt-Nordost before Seckenheim at 19.5); (2) node-VM JS cross-check — load `dist/main.js` in a node VM (stubs: `window.maplibregl`/`window.pmtiles` no-op classes, `document.getElementById` → null, `window.matchMedia` → `{matches: false}`, `console`), call the top-level `computeDistrictRankings` from the VM global with the same features, and assert all 38 ranks + quartiles match the Python reference; skip when node or `dist/main.js` is missing (existing dist-fixture pattern). The JS part fails until T013 exists AND `make publish` refreshes `dist/main.js` — that failure is expected at this point
- [X] T012 [P] [US2] Extend `tests/acceptance/test_style.py` with static CSS assertions for the district popup: quartile badge classes for all four bands ("oberstes Viertel", "oberes Mittelfeld", "unteres Mittelfeld", "unterstes Viertel") with their R-12 colors and text labels; rank line class. Run to confirm the assertions fail before the implementation exists

### Implementation User Story 2

- [X] T013 [US2] Add pure top-level helpers in `src/site/main.js` (no map/DOM access): `quartileBand(rank, n)` implementing the R-2 band formula (`q1 = ceil(n/4)`, `q2 = q3 = floor(n/4)`, remainder to the last band; bands 1..q1 "oberstes Viertel", q1+1..q1+q2 "oberes Mittelfeld", q1+q2+1..q1+q2+q3 "unteres Mittelfeld", rest "unterstes Viertel"; n = 38 → 10/9/9/10) and `computeDistrictRankings(districtFeatures)` returning a `Map` keyed by district `code` with `{ rank, quartile }`: filter `mean_value != null`, sort by `mean_value` descending then `name` ascending (FR-009; JS `<` string ordering matches Python code-point ordering for all 38 names — the reproducibility contract), assign distinct sequential ranks 1..n, fewer than two valid means ⇒ return null (rank/quartile hidden everywhere)
- [X] T014 [US2] Add `loadDistrictRankings()` in `src/site/main.js`: `fetch('stadtteile.geojson')` once at map load (same URL the style's `stadtteile` source loads, so the browser serves it from cache — no new network transfer, R-1), compute via `computeDistrictRankings` and store in a module-level `districtRankings` variable; on fetch failure set it to `null` (defensive degradation); expose `computeDistrictRankings` on `window.__districtRankings` as a debug handle (consistent with the `window.__map` / `window.__renderCityPanel` pattern); call `loadDistrictRankings()` from `onMapLoad()`
- [X] T015 [US2] Rework `districtPopupHtml(props)` in `src/site/main.js` per R-7: district name header + headline label "Baumanteil im Durchschnitt" with mean value (FR-007; "keine Daten" when `mean_value == null`, FR-011); quartile badge when ranked (FR-010, looked up by feature property `code`); rank line "Platz {rank} von {n}" (FR-009, rank 1 = highest mean); city comparison line "Stadtdurchschnitt" with `mean_value_pct` + signed delta + word (FR-008, hidden when `cityStats()` is null per FR-014); existing "Gebäude" (formatInteger thin-space thousands) and "Anteil unter 30 %" (formatPercent) lines kept (FR-007); footnote per R-8: "Was bedeutet das?" + "Der Baumanteil im Durchschnitt ist der mittlere Baumanteil im 60-m-Umkreis aller Gebäude in diesem Stadtteil." (FR-012). Degradation: `mean_value == null` → name + building count only, mean marked "keine Daten", rank/quartile/city hidden; `districtRankings` null (fetch failed) → rank + quartile badge hidden, city line unaffected; content order strictly per FR-013 (header → headline → badge → context lines → footnote)
- [X] T016 [P] [US2] Add district popup CSS in `src/site/style.css`: quartile badge colors per R-12 (oberstes Viertel = cool cyan family, oberes Mittelfeld = `#39c2ff`, unteres Mittelfeld = `#e6854a`, unterstes Viertel = `#ffd524`) all with text labels, rank line styling
- [X] T017 [US2] Verify all US2 acceptance scenarios (spec.md US2-S1..S6) against `contracts/rank-quartile.md`: Lindenhof = Platz 13 / oberes Mittelfeld, Niederfeld = Platz 1 / oberstes Viertel, Innenstadt = Platz 38 / unterstes Viertel; city-line delta cross-checked by hand (Lindenhof +4.0 pp, Innenstadt −12.6 pp); a district at exactly the city average shows "auf Stadtniveau"

**Checkpoint**: US2 complete — district popup shows mean, rank, quartile, city comparison, independently testable.

---

## Phase 5: User Story 3 — Understand Numbers (Priority: P2)

**Goal**: A visitor unsure what "Baumanteil im 60-m-Umkreis" or the 30 % threshold means gets a one-line plain-German explanation inside the popup, a consistent visual hierarchy, and fully visible/scrollable content on mobile — without leaving the map (FR-012, FR-013, FR-016).

**Independent Test**: On the published bundle, open both popup types; verify the footnote explains the headline metric (and the 30 % threshold on the building popup), the content follows the FR-013 hierarchy, and everything is readable and unclipped at a 360 px viewport width.

### Tests User Story 3 (write FIRST, fail before implementation)

- [X] T018 [P] [US3] Extend `tests/acceptance/test_style.py` with FR-016/FR-013 assertions: both popup content boxes have `max-height` (viewport-proportional, e.g. `min(70vh, 420px)`) with `overflow-y: auto` and `max-width: min(240px, calc(100vw - 24px))` so no line is clipped at 360 px (SC-006); hierarchy classes present in FR-013 order. Run to confirm the assertions fail before the implementation exists

### Implementation User Story 3

- [X] T019 [US3] Add mobile-fit + readability CSS in `src/site/style.css`: both popup content boxes get `max-height: min(70vh, 420px)` + `overflow-y: auto` and `max-width: min(240px, calc(100vw - 24px))` (R-9, FR-016/SC-006 — MapLibre's existing anchor edge-flip keeps the popup in view); footnote typography and hierarchy spacing so the "Was bedeutet das?" block reads clearly on desktop and mobile (FR-012/FR-013)
- [X] T020 [US3] Verify US3 acceptance scenarios (spec.md US3-S1..S3): both popups show the footnote in one plain-German sentence with the 30 % explanation on the building popup; visual order is name header → headline → badge → context → footnote; at 360 px both popup types render with every line visible or reachable by scrolling inside the popup (3 representative districts/buildings each — one top quartile, one middle, one bottom); run the SC-007 comprehension spot check (5 people, >= 4 correct restatements of what "60-m-Umkreis" measures)

**Checkpoint**: US3 complete — numbers explainable, hierarchy consistent, mobile fit holds.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Manual verification, performance, copy gates, publish, and final acceptance across all stories.

- [X] T021 [P] Create `tests/frontend/smoke_us7.md` manual checklist per `quickstart.md` covering US1-US3 and edge cases: 10 buildings with value/both deltas/badge/footnote (S2), 10 districts with rank/quartile/city line vs the S1 reference table (S3), footnote + hierarchy + 360 px scroll (S4), 20 mixed building/district/empty-space clicks with at most one popup open, en-dash marker for value-less buildings, close button + German close tooltip (S5), plus a note that district clicks add zero network requests (stadtteile.geojson is browser-cached)
- [X] T022 [P] Add the copy gate to `tests/acceptance/test_style.py`: assert zero em-dashes and zero en-dashes in all new German popup copy strings (R-3/feature 012 convention) and that delta strings use U+2212 minus (e.g. "−2.3 pp"); leave the `UNAVAILABLE` en-dash constant unchanged
- [X] T023 Run `make publish` to refresh `dist/` (main.js is a plain copy of src/site/main.js — required for the SC-003 JS cross-check); run the full acceptance suite (`.venv/bin/python -m pytest tests/`) including the new `tests/acceptance/test_rank.py` node-VM cross-check; run `make check-public`; confirm all green
- [X] T024 Re-measure interaction latency per `validation/perf-budget.json` (quickstart S5): rank computed once at load (O(n log n), n = 38) and O(1) lookups per popup render; confirm the 2 s interaction budget holds with no first-usable-map regression; record the measurement in `validation/` per the existing process
- [X] T025 Run quickstart S1-S5 end to end on the published bundle (S1 pytest cross-check; S2 ten buildings; S3 ten districts; S4 footnote/hierarchy/360 px + comprehension; S5 arbitration + perf); log completed runs to `validation/event.log.jsonl` (project convention, smoke-us7 rows)
- [X] T026 Update `CHANGELOG.md` with the feature 013 entry; commit the work in OR-004 slices via `make commit-slice MSG="..."` and the validation milestone via `make commit-milestone MSG="..."` (Makefile discipline)

**Checkpoint**: Feature complete — all automated checks green, manual checklist passes, performance gate holds.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. BLOCKS all user stories (shared helpers/CSS).
- **User Stories (Phase 3+)**: Depend on Foundational completion. US1 → US2 → US3 in priority order (US1 and US2 are both P1; US3 is P2). US2's rank helpers are US2-only; US1 does not wait on US2.
- **Polish (Final Phase)**: Depends on all three user stories complete. T023 (publish + suite) precedes T024 (perf) and T025 (quickstart runs) because the SC-003 JS cross-check and manual checks run against the refreshed `dist/`.

### User Story Dependencies

- **User Story 1 (P1)**: starts after Foundational. No dependency on other stories.
- **User Story 2 (P1)**: starts after Foundational. Shares `classifyDelta`/`formatDelta`/`cityStats` and the popup structure CSS but is independently testable (rank/quartile vs the reference table).
- **User Story 3 (P2)**: starts after Foundational. Adds footnote/mobile CSS on top of the US1/US2 renderers; independently testable (footnote readability + 360 px fit).

### Within Each User Story

- Tests (T006, T011, T012, T018) MUST be written FIRST and fail before the corresponding implementation.
- JS helpers before renderer rework; renderer before handler wiring; CSS per story before its acceptance verification.
- Story complete and independently verified before moving to the next priority.

### Parallel Opportunities

- Setup: T001, T002 run in parallel (independent checks).
- Foundational: T005 (style.css) runs in parallel with T003/T004 (main.js).
- US1: T006 (test_style.py) runs in parallel with T007 (main.js) and T009 (style.css).
- US2: T011 (test_rank.py) and T012 (test_style.py) and T016 (style.css) run in parallel; the main.js tasks T013/T014/T015 are sequential (same file).
- US3: T018 (test_style.py) runs in parallel with T019 (style.css).
- Polish: T021 (smoke_us7.md) and T022 (test_style.py) run in parallel; T023 (publish + suite) must precede T024 and T025.

### Parallel Caveat

All JS edits land in `src/site/main.js` (one file, no build tool) — main.js tasks within and across stories are sequential; parallelism comes from the different-file tasks (style.css, test files, smoke checklist). Do not staff two implementers on main.js at once.

---

## Parallel Example: User Story 2

```bash
# Launch the US2 test files and CSS together (different files):
Task: "Write tests/acceptance/test_rank.py (Python reference + node-VM cross-check)"
Task: "Extend tests/acceptance/test_style.py with district popup quartile-badge assertions"
Task: "Add district popup CSS in src/site/style.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (green baseline on the feature branch).
2. Complete Phase 2: Foundational (CRITICAL — shared delta/city helpers + popup structure CSS block all stories).
3. Complete Phase 3: User Story 1 (building popup value + both comparisons + 30 % badge + footnote).
4. **STOP VALIDATE**: Test User Story 1 independently per its Independent Test (10 buildings).
5. Deploy/demo if ready.

### Incremental Delivery

1. Setup + Foundational → shared helpers ready.
2. Add User Story 1 → test independently → deploy/demo (MVP).
3. Add User Story 2 (district rank/quartile) → test independently → deploy/demo.
4. Add User Story 3 (footnote/mobile fit) → test independently → deploy/demo.
5. Polish: publish, full suite, quickstart S1-S5, perf gate, changelog.
6. Each story adds value without breaking the previous stories (FR-015 arbitration preserved).

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. Once Foundational is done: one implementer owns `src/site/main.js` (US1 → US2 → US3 JS, sequential); CSS and test-file tasks can be picked up in parallel by others.
3. Stories integrate independently on the shared helpers and popup structure.

---

## Notes

- [P] tasks edit different files and have no interdependencies; same-file tasks are sequential.
- [US1]/[US2]/[US3] labels map tasks to their spec user story for traceability.
- Every user story is independently completable and testable.
- Tests (T006, T011, T012, T018) are written FIRST and must fail before implementation.
- `src/site/style.json`, `src/site/index.html`, and the data pipeline are deliberately UNTOUCHED; never edit them (out-of-scope boundary FR-015).
- `dist/main.js` must be refreshed via `make publish` before the SC-003 node-VM cross-check can pass — the cross-check tests the shipped function, not a re-implementation (R-10).
- German copy only, dot-decimal kept, "pp" deltas, U+2212 minus, "±" neutral, no em/en dashes in new prose (feature 012 convention); `UNAVAILABLE` en-dash constant unchanged.
- Avoid: vague tasks, same-file parallel conflicts, cross-story dependencies that break independence.
