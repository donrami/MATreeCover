# Tasks: Map UI, Brightness Slider & Gradient Legend

**Input**: Design documents from `/specs/004-map-ui-brightness-legend/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test harness exists in this project (documented convention: manual smoke checklists). The smoke-checklist extension tasks below are required verification work from plan.md/quickstart.md, not optional tests.

**Organization**: Tasks are grouped by user story. Stories US1 and US2 both modify `src/site/index.html` and `src/site/style.css` (the slider lives inside the tools card US2 relocates), so stories run as sequential slices; [P] is only used within a story for file-disjoint work.

**Status**: Phases 1–6 shipped in milestone slice `9a00fcd`. Phase 7 shipped the low-brightness inversion (FR-019) in commit `e2dbb65` with `raster-brightness-min: 1` (uncapped). Clarification Q4 capped inverted features at 0.65; Phase 8 shipped the cap correction (paint flipped to `min: 0.65`, smoke + evidence updated, visual smoke test approved by maintainer). Nothing remains open on this feature.

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

## Phase 7: Follow-up Slice — Low-Brightness Inversion (FR-019)

**Purpose**: When the slider drops below 25, the base map crossfades gradually into a photo-negative — a second raster layer `basemap-inverted` (same `basemap` source, `raster-brightness-min: 0.65` / `raster-brightness-max: 0`, so the shader computes `out = 0.65 × (1 - in)` — inverted features never exceed the 0.65 cap, clarification Q4) with opacity `s(v) = clamp((25 − v)/20, 0, 1)` — fully inverted at 5. Streets and labels render lighter gray on the near-black background and stay legible; the map stays grayscale; buildings, trees, and popup are unaffected (FR-019, SC-008, research R-010..R-012). NOTE: this slice shipped with `min: 1` (uncapped, `out = 1 - in`, features measured up to 0.72 linear); Phase 8 corrects the paint value and re-verifies the cap.

**Depends on**: User Story 1 (Phase 3) — the slider markup and `wireBrightnessSlider()` must exist. Standalone slice: no changes to `src/site/index.html` or `src/site/style.css`, so the shipped US2/US3 work is untouched.

**Independent Test**: quickstart Scenario 1 step 2 (drag below 25 → gradual transition, no sudden switch; at 5, streets/labels lighter than the near-black background and legible) and Scenario 2 step 4 (per-pixel inversion assertion: features-at-max pixels measure lighter than background-at-max pixels at minimum) plus the Scenario 2 background gate (p10 ratio ≈ 0.002, SC-001) and the cap assertion `a_min[dark].max() <= 0.65` (SC-008) — the cap is enforced and verified in Phase 8.

### Implementation — Inversion Slice (US1)

- [X] T018 [US1] Add the `basemap-inverted` raster layer to `src/site/style.json` between the `basemap` and `outside-mask` layers: `id: "basemap-inverted"`, `type: "raster"`, `source: "basemap"` (same tile set — no new requests, FR-015/SC-007), `layout: { "visibility": "none" }`, `paint: { "raster-brightness-min": 1, "raster-brightness-max": 0, "raster-opacity": 0 }` — per `contracts/base-map-brightness.md` § Low-brightness inversion layer and research R-010/R-011; no other layer, source, or palette change (shipped with `min: 1` — the 0.65 cap is applied by T023)
- [X] T019 [P] [US1] Extend the `apply` handler in `wireBrightnessSlider()` in `src/site/main.js` with the inversion mapping: `const s = Math.min(1, Math.max(0, (25 - Number(slider.value)) / 20))`; when `s > 0` set `basemap-inverted` `raster-opacity` to `s` and `layout.visibility` to `"visible"`, otherwise set opacity `0` and visibility `"none"`; guard on `map.getLayer('basemap-inverted')` like the existing basemap guard — per research R-011/R-012 (clamped in-range values, visibility `"none"` skips the wasted render pass at `s = 0`)
- [X] T020 [P] [US1] Extend `tests/frontend/smoke_us1.md` with the inversion checks: below 25 the basemap crossfades gradually into the photo-negative (no sudden switch); at 5, streets and labels render lighter gray than the near-black background and remain legible (FR-019, SC-008); the map stays grayscale with no hue shift; buildings, trees, popup, and zoom controls unaffected at any slider position; at slider ≥ 25 the rendering is identical to the pre-slice appearance (FR-003 regression)
- [X] T021 [US1] Publish and verify per quickstart Scenarios 1–2: `make publish`, serve `dist/` (Range-capable server), screenshot the fixed viewport with `buildings-fill` hidden at slider 65 / 5 / 100; assert `min` background luminance ≤ 10% of `def` (p10 ≈ 0.002 expected, SC-001), `max` ≈ `def / 0.65` (±5%, restores pre-003 basemap), and the inversion assertion `mean(min luminance of features-at-max pixels) > mean(min luminance of background-at-max pixels)` (SC-008); record results into `validation/brightness-slider/luminance.json`
- [X] T022 [US1] Commit the inversion slice per OR-004 with `make commit-slice` (single commit: `src/site/style.json` inverted layer, `src/site/main.js` mapping, `tests/frontend/smoke_us1.md` extension, `validation/brightness-slider/luminance.json` update), commit-check script passing

**Checkpoint**: Inversion slice delivered (uncapped) and Phase 8 cap correction shipped — FR-019 and SC-008 verified on the published bundle, inverted features never exceed the 0.65 cap; the feature is complete.

---

## Phase 8: Cap Correction Slice — Inverted Features Capped at 0.65 (FR-019, SC-008)

**Purpose**: Clarification Q4 caps the inverted features' brightness at 0.65 (the map's default-brightness reference). The shipped Phase 7 layer paints `raster-brightness-min: 1` (uncapped; features measured up to 0.72 linear — too bright). The fix flips the paint to `min: 0.65` so the shader computes `out = 0.65 × (1 - in)` — no inverted feature ever exceeds the cap while the near-black background is preserved — updates the smoke checks, and re-verifies SC-008 with the per-pixel cap assertion (quickstart Scenario 2).

**Depends on**: Phase 7 (shipped). Standalone slice: touches only `src/site/style.json` (one paint value), `tests/frontend/smoke_us1.md` (cap checks), and `validation/brightness-slider/`; no US2/US3 files are re-entered.

**Independent Test**: quickstart Scenario 2 step 4 cap assertion — `a_min[dark].max() <= 0.65` at minimum brightness (per-pixel feature luminance ≤ 0.65, SC-008); features still measure lighter than the background (legibility preserved); background gate p10 ≈ 0.002 unchanged (SC-001).

### Implementation — Cap Correction Slice (US1)

- [X] T023 [US1] Change the `basemap-inverted` layer's `paint.raster-brightness-min` in `src/site/style.json` from `1` to `0.65` (all other properties unchanged: `raster-brightness-max: 0`, `raster-opacity: 0`, `layout.visibility: "none"`) — per `contracts/base-map-brightness.md` § Low-brightness inversion layer and clarification Q4; the shader then computes `out = 0.65 × (1 - in)` so no inverted feature exceeds 0.65
- [X] T024 [P] [US1] Update the inversion checks in `tests/frontend/smoke_us1.md`: assert streets and labels never render brighter than the 0.65 cap at minimum brightness (per-pixel sRGB luminance ≤ 0.65; measured max 0.6275 sRGB) while remaining lighter than the near-black background and legible (FR-019, SC-008, clarification Q4)
- [X] T025 [US1] Publish (`make publish`) and re-verify on the served bundle: screenshots at slider 65 / 5 / 100 with `buildings-fill` hidden; cap assertion PASS (`max_features_at_min_srgb = 0.6275 ≤ 0.65`); record the updated results into `validation/brightness-slider/luminance.json`; maintainer eyeball smoke test on the published bundle approved the visual result
- [X] T026 [US1] Commit the cap-correction slice per OR-004 with `make commit-slice` (single commit: `src/site/style.json` paint flip + stale comment fix in `src/site/main.js`, `tests/frontend/smoke_us1.md` cap checks, `validation/brightness-slider/luminance.json` update, plus the accumulated doc updates from the clarify/plan/tasks phases), commit-check script passing

**Checkpoint**: The 0.65 cap is enforced and verified — inverted features never exceed the cap at any brightness; the feature is complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (regression baseline must be green first)
- **User Stories (Phase 3+)**: Depend on Foundational; run sequentially because all three stories edit shared files in `src/site/` (index.html, style.css) and `tests/frontend/smoke_us1.md`
- **Polish (Final Phase)**: Depends on all user stories
- **Inversion Slice (Phase 7)**: Depends on User Story 1 (Phase 3) — needs the slider markup and `wireBrightnessSlider()`; standalone follow-up that does not re-enter US2/US3 files
- **Cap Correction (Phase 8)**: Depends on Phase 7 (shipped) — flips the inverted layer's paint to `min: 0.65`; touches only `src/site/style.json`, `tests/frontend/smoke_us1.md`, `validation/brightness-slider/`

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational. No dependency on US2/US3.
- **User Story 2 (P1)**: Can start after Foundational AND after US1 — the tools card US2 relocates contains the US1 slider. Sequenced after US1 to avoid same-file conflicts in `src/site/style.css`.
- **User Story 3 (P2)**: Can start after Foundational; edits `#legend` markup in `src/site/index.html` and appends to `smoke_us1.md` — sequenced after US2 to keep story slices clean.
- **Inversion follow-up (Phase 7, US1)**: Depends on US1 completion (shipped). Touches `src/site/style.json`, `src/site/main.js`, `tests/frontend/smoke_us1.md` — files US2/US3 no longer alter — so it lands as one clean slice after the milestone.
- **Cap correction (Phase 8, US1)**: Depends on Phase 7 (shipped). Touches `src/site/style.json`, `tests/frontend/smoke_us1.md`, `validation/brightness-slider/` — no US2/US3 files.

### Within Each User Story

- Markup first (the element the JS/CSS bind to), then [P] file-disjoint work, then measurement/verification
- In the inversion slice: the style layer (T018) first — the JS mapping (T019) guards on it — then file-disjoint work (T020) and end-to-end verification (T021, T022)
- In the cap-correction slice: the paint flip (T023) first, then file-disjoint smoke cap checks (T024) and end-to-end verification/commit (T025, T026)
- Story complete (checkpoint) before moving to the next priority

### Parallel Opportunities

- T004, T005, T006 are file-disjoint (style.css / main.js / smoke_us1.md) and can run in parallel after T003
- T010 is file-disjoint from T008/T009 (smoke_us4.md vs style.css) and can run in parallel
- T013, T014 are file-disjoint (style.css / smoke_us1.md) and can run in parallel after T012
- T019 (main.js) and T020 (smoke_us1.md) are file-disjoint and can run in parallel after T018 (style.json layer) lands
- T023 (style.json paint flip) and T024 (smoke_us1.md cap checks) are file-disjoint and can run in parallel after the cap value lands
- Cross-story parallelism is NOT safe: all stories touch `src/site/index.html` and `src/site/style.css`

---

## Parallel Example: User Story 1

```bash
# After T003 (slider markup in index.html) lands, launch together:
Task: "T004 Style the brightness slider in src/site/style.css"
Task: "T005 Wire wireBrightnessSlider() in src/site/main.js"
Task: "T006 Extend tests/frontend/smoke_us1.md with brightness checks"
```

## Parallel Example: Inversion Slice (Phase 7)

```bash
# After T018 (basemap-inverted layer in style.json) lands, launch together:
Task: "T019 Extend the apply() mapping in src/site/main.js with inversion opacity/visibility"
Task: "T020 Extend tests/frontend/smoke_us1.md with inversion checks"
```

## Parallel Example: Cap Correction (Phase 8)

```bash
# After T023 (paint flip min 1 → 0.65 in style.json) lands, launch together:
Task: "T024 Add the 0.65 cap assertions to tests/frontend/smoke_us1.md"
# Then verification (T025) and commit (T026) run in sequence.
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

### Follow-up Slices (Inversion, FR-019 + Cap, Q4)

1. The milestone slice (`9a00fcd`) has shipped US1–US3 without the low-brightness inversion.
2. Phase 7 landed as one independent slice after the milestone: `style.json` inverted layer → slider mapping + smoke extension (parallel) → publish + quickstart Scenarios 1–2 gates → `make commit-slice` (commit `e2dbb65`).
3. Phase 8 shipped the cap correction: flip `basemap-inverted` paint `min` 1 → 0.65 → smoke cap checks (parallel) → publish + visual smoke test on the served bundle (maintainer eyeball approved) → `make commit-slice`.
4. Phase 8 is the final slice of this feature — nothing else remains open.

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
- The cap-correction slice (Phase 8) shipped the 0.65 cap — Phases 1–7 shipped earlier (milestone `9a00fcd`, inversion `e2dbb65`). The inverted layer reuses the `basemap` source (no new requests, FR-015/SC-007) and adds only in-range paint values; the corrected paint `min: 0.65` keeps every inverted feature within the 0.65 cap (MapLibre clamps out-of-range `raster-brightness-*`, research R-011). Phase 8 closes the chapter on clarification Q4.
- Avoid: vague tasks, same-file parallel work, cross-story dependencies that break slice independence
- Commit after each task or logical group (OR-004)
