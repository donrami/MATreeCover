---
description: "Task list: Fix Building Popup Interaction"
---

# Tasks: Fix Building Popup Interaction

**Branch**: `main`

**Input**: Design documents in `specs/002-fix-building-popup/`. Required: `plan.md`, `spec.md`. Supporting: `research.md`, `data-model.md`, `contracts/popup-interaction.md`, `quickstart.md`.

**Prerequisites**: The published bundle from the prior feature (`dist/`, buildings layer and values accepted per `artifacts.manifest.json`). A Range-capable static server for `dist/`. `python -m http.server` has no Range support. Use nginx or equivalent. No new dependencies. No data changes. No pipeline changes.

**Tech stack**: Vanilla ESM JavaScript with no build tool. The convention is `src/site/main.js`. MapLibre GL JS 5.7.1 and pmtiles are already vendored in `src/site/vendor/`. The vendored bundle is the source of truth for library behavior, not the upstream docs.

**Tests**: Manual plus browser only, per plan.md and research R-010. The test artifact is the extended smoke checklist `tests/frontend/smoke_us2.md`. The six quickstart scenarios run against the published bundle. No unit tests: no framework exists, and adding one is out of scope. No pipeline tests: there are no pipeline changes.

**Constraints**: Frontend behavior only. No change to published data or acceptance state (operational constraint OP-001). One commit per slice via `make commit-slice` (`Makefile`). It runs `git add -A` and refuses unstaged changes.

## Format

- `[ID] [P?] [Story] Description with file path`
- `[P]`: run in parallel. Different files, no dependencies on incomplete tasks.
- `[Story]`: maps the task to US1. Setup, Foundational, and Polish carry no label.

## Path Conventions

- The only edited source file is `src/site/main.js`, the `wireBuildingsInteractions()` function.
- The extended test artifact is `tests/frontend/smoke_us2.md`.
- The published bundle is `dist/` (gitignored, never edited). Re-copy `src/site/main.js` into `dist/` when the served bundle predates the fix.
- Commit machinery: the `commit-slice` target in `Makefile`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verification environment for the browser-only acceptance runs.

- [X] T001 [P] Confirm the verification environment per `quickstart.md` Setup. Be on branch `main`. Confirm `make commit-slice` is available (`Makefile`). Serve `dist/` with a Range-capable static server (nginx or equivalent). Open the served URL in a clean browser.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No tasks. There are no blocking prerequisites. The fix lives in `wireBuildingsInteractions()` in `src/site/main.js`. The vendored MapLibre 5.7.1 bundle, the `style.json` `buildings-fill` layer, PMTiles sources, hover handlers, `Bäume` toggle, and error handling come from the prior feature. They stay in place. Implementation can begin after Setup.

---

## Phase 3: User Story 1: Select Any Building Value (Priority: P1) 🎯 MVP

**Goal**: Clicking any building always shows its tree-cover value in a compact popup. At most one popup is open at any moment. Clicking empty map space dismisses it. Buildings without a valid value show the unavailable marker `–`, never `0.00%`.

**Independent Test**: On the served published bundle, click ten distinct buildings in a row. Every click shows the clicked building's value with two decimals. `document.querySelectorAll('.maplibregl-popup').length` never exceeds `1`. No building click ever closes the popup (SC-001, quickstart.md Scenario 1). Then click empty space. The popup closes (SC-003).

### Tests User Story 1 (write FIRST, fail before implementation)

⚠️ **NOTE: Write the failing checklist FIRST, before implementation**

- [X] T002 [P] [US1] Extend `tests/frontend/smoke_us2.md` with this feature's checks per `quickstart.md` Scenarios 1–6. Cover replace-not-close, single popup count, empty-space close, close-button close, and re-open after close (FR-011). Cover the `–` marker never showing `0.00%`, touch-tap parity, tree-overlay click, and viewport-edge popup. The new checks MUST fail on the current published bundle. A second building click closes the popup there. Verify that failure before implementation starts.

### Implementation User Story 1

- [X] T003 [US1] Create one module-level popup instance in `src/site/main.js`. Use `new maplibregl.Popup({ closeButton: true, offset: 8, className: 'building-popup', closeOnClick: false })` at module scope, outside `wireBuildingsInteractions()`. No code path may construct a second instance (SC-001).

- [X] T004 [US1] Rewrite the `buildings-fill` click handler in `src/site/main.js` to update the single instance. Call `setLngLat(event.lngLat)` plus `setHTML(...)` from `has_value` / `value_str`. Keep the label `Baumanteil im 60-m-Umkreis`. Show the en dash `–` when `has_value === false`, never `0.00%`. Call `addTo(map)` when the popup is closed, so it re-attaches (FR-002/FR-003/FR-007/FR-011). Keep `closeButton: true` for the built-in close (FR-004, R-002/R-009).

- [X] T005 [US1] Add a map-level close handler in `src/site/main.js`. Use `map.on('click', ...)` with `queryRenderedFeatures(event.point, { layers: ['buildings-fill'] })`. Call `popup.remove()` when the result is empty. Boundary mask and outside-Mannheim clicks then close the popup. Building clicks never do (FR-003, R-003).

- [X] T006 [US1] Verify no regression in `src/site/main.js`. The hover pointer handlers (`mousemove`/`mouseleave` on `buildings-fill`), `wireTreesToggle`, and `wireErrorHandling` are untouched. No per-click `new maplibregl.Popup(...)` remains anywhere (FR-008/FR-010, R-007/R-008).

**Checkpoint**: US1 complete and independently testable. Re-copy `src/site/main.js` into `dist/` when the served bundle predates the fix. Run Scenario 1 and Scenario 3 before any commit. Both MUST pass (gates SC-001, SC-003).

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation and the operational-constraint commit.

- [X] T007 Run `quickstart.md` Scenarios 1–6 end-to-end against the served `dist/` bundle. Re-copy `src/site/main.js` into `dist/` first when the bundle predates the fix. Record pass/fail per scenario. Update the Result section of `tests/frontend/smoke_us2.md` (SC-001..SC-005). Scenarios 4–6 cover the close button, click-through, touch parity, tree overlay, and viewport edge.
      NOTE: PASSED on the served bundle (nginx, 127.0.0.1:8088). Maintainer confirmed all scenarios after the CSS fix (commit 810bd6f, vendored maplibre-gl.css 5.7.1). Scenarios 1 and 3 (gates SC-001, SC-003) pass; checklist Result ticked in `tests/frontend/smoke_us2.md`.

- [X] T008 Create the slice commit via `make commit-slice` (`Makefile`). It requires a `MSG=...` argument and runs `git add -A`. Confirm `git status` shows only the intended files first. The commit must contain exactly `src/site/main.js` and `tests/frontend/smoke_us2.md`. No data, manifest, or other published-content changes (operational constraint OP-001).
      NOTE: committed as c9b9065 (Slice-02). The slice contains exactly `src/site/main.js` and `tests/frontend/smoke_us2.md`. The spec dir (`specs/002-fix-building-popup/`) was committed earlier as 4e9ae7c (Spec-01). `dist/main.js` was re-copied from `src/site/main.js` but is gitignored, so it is not in the slice commit (OP-001).

**Checkpoint**: All scenarios green. Extended smoke checklist recorded. Slice committed on `main`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Start immediately.
- **Foundational (Phase 2)**: No tasks. Nothing blocks.
- **User Story 1 (Phase 3)**: Depends on Setup (serving environment). It is the only story and the MVP.
- **Polish (Phase 4)**: Depends on US1 complete and scenario-verified.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Setup only. It has no cross-story dependencies.

### Within User Story 1

- Write the failing checklist (T002) before implementation. It runs in parallel with it (different file).
- T003 → T004 → T005 are strictly sequential. They edit the same file. Each rewrites a region of `wireBuildingsInteractions()` in `src/site/main.js`.
- T006 (regression verification) runs after T003–T005.
- Smoke-check the story (Scenarios 1 and 3) before the Polish phase.

### Parallel Opportunities

- **Setup**: T001 alone.
- **US1**: T002 (smoke checklist) runs in parallel with T003–T005 (implementation). The implementation tasks T003–T005 edit one file, so they are sequential.
- **Polish**: T007 then T008, strictly sequential.

## Parallel Example: User Story 1

```bash
# Launch the failing checklist and the implementation start together:
Task: "Extend tests/frontend/smoke_us2.md with this feature's checks per quickstart.md Scenarios 1-6 (T002)"
Task: "Create one module-level popup instance in src/site/main.js (T003)"
# T004 and T005 follow T003 in the same file. Do NOT parallelize same-file edits.
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1: Setup (serving environment).
2. Write the failing checks (T002) into `tests/frontend/smoke_us2.md`. Verify they fail on the current bundle. A second building click closes the popup there.
3. Implement in order: single persistent popup instance (T003), replace-not-close layer handler (T004), empty-space close handler (T005), regression verification (T006).
4. **STOP VALIDATE**: serve `dist/` (re-copy `src/site/main.js` when needed). Run `quickstart.md` Scenario 1 (ten-building sequence, single popup) and Scenario 3 (empty-space close ×10, re-open). Both must pass.
5. Run all six quickstart scenarios. Update the smoke checklist Result. Commit via `make commit-slice`.

### Incremental Delivery

1. Setup plus failing checklist → evidence that the defect is captured.
2. User Story 1 → Scenarios 1 and 3 green → demo.
3. Remaining scenarios (4–6) → regression evidence → slice commit.

### Parallel Team Strategy

Single story, single edited file. One implementer for T003–T005. A second person can write the checklist (T002) in parallel. Nothing else runs concurrently.

---

## Notes

- `[P]` tasks = different files, no dependencies.
- `[Story]` label maps each task to its user story for traceability.
- The user story is independently completable and testable.
- Verify the new checklist fails before implementing (T002 first).
- Commit the implementation slice only after Scenario 1 and Scenario 3 pass.
- Avoid: same-file parallel edits (`src/site/main.js`), data/pipeline changes (OP-001), per-click popup instances (SC-001).
