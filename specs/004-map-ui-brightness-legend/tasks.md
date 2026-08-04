# Tasks: Map UI, Brightness Slider & Gradient Legend

**Input**: Design documents from `/specs/004-map-ui-brightness-legend/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test harness exists in this project (documented convention: manual smoke checklists). The smoke-checklist extension tasks below are required verification work from plan.md/quickstart.md, not optional tests.

**Organization**: Tasks are grouped by user story. Stories US1 and US2 both modify `src/site/index.html` and `src/site/style.css` (the slider lives inside the tools card US2 relocates), so stories run as sequential slices; [P] is only used within a story for file-disjoint work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Static frontend: `src/site/` (index.html, style.css, main.js) at repository root
- Verification: `tests/frontend/` smoke checklists, `validation/brightness-slider/` measurement records

---

## Phase 1: Setup

**Purpose**: Verify the environment and the pre-change baseline before any modification

- [X] T001 Checkout branch `004-map-ui-brightness-legend` and verify tooling: `.venv` has `numpy` + `rasterio` (luminance measurement), a Range-capable static server is available (nginx or equivalent) — per quickstart prerequisites

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the regression baseline every story must preserve (SC-006)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Publish the unmodified baseline (`make publish`), serve `dist/`, and run the existing smoke checklists `tests/frontend/smoke_us1.md`, `smoke_us2.md`, `smoke_us3.md` to confirm all pass before any change

**Checkpoint**: Foundation ready — the pre-change bundle is green; user story implementation can begin

---

## Phase 3: User Story 1 - Brightness Slider (Priority: P1) 🎯 MVP

**Goal**: A permanently visible "Helligkeit" slider that adjusts the raster base map's brightness live from near-black (value 5 → `raster-brightness-max` 0.05) up to the original un-darkened basemap (value 100 → 1.0), defaulting to today's appearance (value 65 → 0.65), session-only (FR-001..FR-007, FR-016).

**Independent Test**: quickstart Scenario 1 (slider exists at 65, default = today's look, live dim/brighten, no pan interference, reload resets) and Scenario 2 (luminance gates: min < 10% of default, max restores original).

### Implementation for User Story 1

- [X] T003 [US1] Add the brightness control to `src/site/index.html` inside `#controls`: a visible "Helligkeit" label and `<input type="range" id="brightness-slider" min="5" max="100" value="65" aria-label="Helligkeit der Karte">` (identity-mapped, research R-001/R-002)
- [X] T004 [P] [US1] Add dark-theme slider styles in `src/site/style.css` (range input styling matching the panel theme; no positioning changes yet — the tools-card move is US2)
- [X] T005 [P] [US1] Implement `wireBrightnessSlider()` in `src/site/main.js`: `input` listener calls `map.setPaintProperty('basemap', 'raster-brightness-max', value / 100)`; invoke it from `onMapLoad` next to the existing `wireTreesToggle()` call; guard on element existence like `wireTreesToggle` does
- [X] T006 [P] [US1] Extend `tests/frontend/smoke_us1.md` with a brightness section: default value 65 reproduces today's map (FR-003), live dimming leaves buildings/trees unchanged (FR-004), dragging does not pan the map, reload resets the value (FR-007), slider visible at desktop and 360 px (FR-016)
- [X] T007 [US1] Measure and record the luminance gates per quickstart Scenario 2 (screenshots at values 65 / 5 / 100, `numpy` + `rasterio` mean-luminance check) into `validation/brightness-slider/luminance.json`

**Checkpoint**: User Story 1 fully functional — the brightness slider works standalone with all luminance gates passing

---

## Phase 4: User Story 2 - Clean, Non-Overlapping Controls (Priority: P1)

**Goal**: The tools card (Bäume + brightness slider) moves out of the top-right corner into the left column below the legend card; no two static UI elements overlap at any width ≥320 px and any zoom (FR-008, FR-009, FR-017).

**Independent Test**: quickstart Scenario 3 (5-width × 3-zoom `getBoundingClientRect` overlap matrix, pairwise disjoint) and Scenario 4 (Bäume click-through at the former overlap point).

### Implementation for User Story 2

- [X] T008 [US2] Move `#controls` from `top: 12px; right: 12px` to the left column below `#legend` in `src/site/style.css` (desktop rules: same `left: 12px` column, top = legend bottom + gap; keep `z-index: 10`; remove the top-right placement) — the structural fix for the Bäume/zoom overlap (research R-003)
- [X] T009 [US2] Adjust the `≤480px` media-query rules in `src/site/style.css`: the tools card stacks above the legend strip (`bottom: 76px; right: 12px` anchor kept) without covering the zoom control, legend strip, or attribution slot; legend keeps collapsing to the bottom strip
- [X] T010 [P] [US2] Create `tests/frontend/smoke_us4.md`: overlap-matrix checklist (widths 320/480/768/1280/1920 × 3 zoom levels, pairwise-disjoint `getBoundingClientRect` assertion per quickstart Scenario 3), Bäume click-through at the former overlap rectangle (SC-004), and popup transient/dismissible check (FR-017)
- [X] T011 [US2] Run the overlap matrix on the published bundle and record results into `validation/brightness-slider/overlap.json` (quickstart Scenario 3 pass criteria)

**Checkpoint**: User Stories 1 AND 2 functional — no overlaps at any tested viewport, Bäume fully clickable

---

## Phase 5: User Story 3 - Gradient Legend Bar (Priority: P2)

**Goal**: The legend's discrete color swatches become one continuous gradient bar spanning the frozen palette stops at value-proportional positions, with tick labels 0 / 15 / 30 / 50 / 100 and screen-reader text preserved (FR-010..FR-013, FR-018).

**Independent Test**: quickstart Scenario 5 (continuous bar, no gaps, five tick labels visible at proportional positions at desktop and ≤480 px, values exposed as text to assistive tech).

### Implementation for User Story 3

- [X] T012 [US3] Replace the legend swatch `<ol class="legend-stops">` in `src/site/index.html` with the gradient-bar markup: bar with the eight palette stops at value fractions (`0 → #ffd524`, `12 → #e6854a`, `24 → #a97e65`, `24.08 → #0674aa`, `32 → #1db6ff`, `40 → #39c2ff`, `48 → #56ceff`, `80 → #6ad4ff`, capped to 100), tick labels `0/15/30/50/100` at `left: 0%/15%/30%/50%/100%`, `role="img"` + `aria-label`, and a visually hidden value list for screen readers (research R-004; contract `contracts/legend-gradient.md`); keep the card title, description, and "Prozent" unit unchanged (FR-013)
- [X] T013 [P] [US3] Add gradient-bar, tick-label, and `.sr-only` styles in `src/site/style.css` (continuous `linear-gradient`, tick positions value-proportional, labels never clipped — including the ≤480 px legend strip)
- [X] T014 [P] [US3] Extend `tests/frontend/smoke_us1.md` with gradient legend checks: one continuous bar (FR-010/FR-011), five tick labels at proportional positions (FR-012), accessible text present (FR-018), all labels visible in the narrow strip (SC-005)

**Checkpoint**: All user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation and delivery discipline

- [X] T015 Run quickstart Scenarios 1–6 end-to-end on the published bundle and fix any failures (Scenario 2 luminance gates, Scenario 3 overlap matrix, Scenario 5 legend checks are the blocking gates — do not ship until they pass)
- [X] T016 [P] Run all four smoke checklists (`tests/frontend/smoke_us1.md` extended, `smoke_us2.md`, `smoke_us3.md` unchanged, `smoke_us4.md` new) and confirm green
- [X] T017 Commit per OR-004: `make commit-slice` after each story slice (US1, US2, US3) and `make commit-milestone` after the final validation pass, with the commit-check script passing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (regression baseline must be green first)
- **User Stories (Phase 3+)**: Depend on Foundational; run sequentially because all three stories edit shared files in `src/site/` (index.html, style.css) and `tests/frontend/smoke_us1.md`
- **Polish (Final Phase)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational. No dependency on US2/US3.
- **User Story 2 (P1)**: Can start after Foundational AND after US1 — the tools card US2 relocates contains the US1 slider. Sequenced after US1 to avoid same-file conflicts in `src/site/style.css`.
- **User Story 3 (P2)**: Can start after Foundational; edits `#legend` markup in `src/site/index.html` and appends to `smoke_us1.md` — sequenced after US2 to keep story slices clean.

### Within Each User Story

- Markup first (the element the JS/CSS bind to), then [P] file-disjoint work, then measurement/verification
- Story complete (checkpoint) before moving to the next priority

### Parallel Opportunities

- T004, T005, T006 are file-disjoint (style.css / main.js / smoke_us1.md) and can run in parallel after T003
- T010 is file-disjoint from T008/T009 (smoke_us4.md vs style.css) and can run in parallel
- T013, T014 are file-disjoint (style.css / smoke_us1.md) and can run in parallel after T012
- Cross-story parallelism is NOT safe: all stories touch `src/site/index.html` and `src/site/style.css`

---

## Parallel Example: User Story 1

```bash
# After T003 (slider markup in index.html) lands, launch together:
Task: "T004 Style the brightness slider in src/site/style.css"
Task: "T005 Wire wireBrightnessSlider() in src/site/main.js"
Task: "T006 Extend tests/frontend/smoke_us1.md with brightness checks"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (baseline green)
3. Complete Phase 3: User Story 1 (brightness slider)
4. **STOP and VALIDATE**: quickstart Scenarios 1–2 + `make commit-slice`
5. Deploy/demo if ready — the slider alone delivers the editorial-style use case

### Incremental Delivery

1. Setup + Foundational → baseline established
2. User Story 1 → slider works → commit slice (MVP!)
3. User Story 2 → no overlaps anywhere → commit slice
4. User Story 3 → gradient legend → commit slice
5. Polish: full quickstart + all smoke checklists → `make commit-milestone`
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Within each story, the [P]-marked tasks are split across developers
3. Stories themselves are sequenced (shared files): US1 → US2 → US3
4. Stories complete and integrate in order

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable (its checkpoint)
- The palette (`src/site/style.json` buildings-fill) is FROZEN — no task may change it (spec FR-003, 003 contract)
- The popup/hover/toggle behavior is untouched except for the slider wiring addition in `main.js` (FR-014)
- Avoid: vague tasks, same-file parallel work, cross-story dependencies that break slice independence
- Commit after each task or logical group (OR-004)
