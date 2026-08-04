---

description: "Task list for base-map darkening"
---

# Tasks: Darken Base Map

**Input**: Design documents from `/specs/003-darken-base-map/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/base-map-style.md, quickstart.md

**Tests**: No automated test tasks are included — the spec defines no automated test requirement. Verification is the manual/scripted quickstart scenarios (`quickstart.md` Scenarios 1–5) plus the published smoke checklists. The luminance measurement script (T003) is verification tooling, not a test suite.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. All three stories verify the same single edit (`src/site/style.json`); they are independent *checks*, with T009 (tuning) the only cross-story touchpoint.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/`, `tests/` at repository root; `scripts/` for tooling; `validation/` for measured records.

---

## Phase 1: Setup (Baseline)

**Purpose**: Capture the pre-change state so SC-001 (≥30% luminance drop) is measurable against the *current published bundle*, and confirm the working baseline.

- [X] T001 Create `validation/darken/` and capture the current bundle baseline: serve the existing `dist/` (unchanged) with a Range-capable server, open at the fixed viewport used in quickstart Scenario 1 (1280×800, buildings hidden via `map.setLayoutProperty('buildings-fill','visibility','none')` or a building-free area), screenshot to `validation/darken/old-baseline.png`
- [X] T002 [P] Confirm the pre-change state: `src/site/style.json` `basemap` layer has no `paint` block (renders at full brightness), and `make publish` succeeds on the unchanged tree

**Checkpoint**: Baseline captured — the old bundle is reproducible for before/after comparison.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The luminance measurement tool that US1's SC-001 gate and Polish's record task both depend on.

**⚠️ CRITICAL**: No user story verification can begin until this phase is complete.

- [X] T003 Write `scripts/measure_luminance.py`: reads one or two PNGs with `numpy` + `rasterio` (both already in `.venv`), prints mean relative luminance (0.2126 R + 0.7152 G + 0.0722 B), and with `--assert-ratio OLD NEW 0.70` exits nonzero unless `mean_new <= 0.70 * mean_old`

**Checkpoint**: Foundation ready — `python scripts/measure_luminance.py validation/darken/old-baseline.png` prints a luminance value.

---

## Phase 3: User Story 1 - Distinguish Building Colors on a Darker Map (Priority: P1) 🎯 MVP

**Goal**: The base map renders visibly darker; building tree-cover colors are clearly distinguishable against it.

**Independent Test**: quickstart Scenario 1 (mean luminance drop ≥30%, measured) + Scenario 2 (all palette colors and the gray unavailable fill distinguishable at default zoom).

### Implementation for User Story 1

- [X] T004 [US1] Add the darkening paint to the `basemap` layer in `src/site/style.json`: `"paint": { "raster-brightness-max": 0.65 }` (target within contract window [0.6, 0.7] per `contracts/base-map-style.md`); validate the file with `python -m json.tool`; no other layer or source changes
- [X] T005 [US1] Regenerate the bundle with `make publish`; confirm `dist/style.json` contains the paint block and that the basemap tile URLs, `tileSize`, attribution, and layer order are unchanged
- [X] T006 [US1] Capture `validation/darken/new-baseline.png` at the identical viewport as T001 and run `python scripts/measure_luminance.py --assert-ratio validation/darken/old-baseline.png validation/darken/new-baseline.png 0.70` (SC-001 gate; expected ratio ≈ 0.65)
- [X] T007 [P] [US1] Visual palette check per quickstart Scenario 2 at default zoom: yellow `#ffd524`, orange `#e6854a`, brown `#a97e65`, dark blue `#0674aa`, light blues `#1db6ff`/`#39c2ff`/`#56ceff`/`#6ad4ff`, and gray unavailable `#444444` are each clearly distinguishable from the darkened background (FR-004); neighboring different-value buildings show an easily perceived color difference

**Checkpoint**: At this point, User Story 1 is complete — the map is measurably darker and the palette is distinguishable (SC-001, SC-002).

---

## Phase 4: User Story 2 - Keep Map Context Readable (Priority: P2)

**Goal**: Street and district labels remain legible on the darkened map at all zooms.

**Independent Test**: quickstart Scenario 3 — 10/10 sampled labels legible at a downtown zoom, plus one zoomed-in and one zoomed-out level; no unreadable area while panning.

### Implementation for User Story 2

- [X] T008 [US2] Label legibility check per quickstart Scenario 3: zoom to a downtown area, read ten street/district labels, pan the city, and repeat at one zoomed-in and one zoomed-out level (SC-003, FR-005)
- [X] T009 [US2] If any label fails: tune `raster-brightness-max` in `src/site/style.json` within the contract window [0.6, 0.7] (nudge up toward 0.7), re-run `make publish`, re-capture and re-measure per T006, and repeat the T008 check until both SC-001 and SC-003 pass (depends on T004–T008)

**Checkpoint**: At this point, User Stories 1 AND 2 both pass — the map is darker and still navigable.

---

## Phase 5: User Story 3 - Overlay Layers Stay Visible (Priority: P2)

**Goal**: The tree layer and gray unavailable buildings stay clearly visible; all interactions behave unchanged.

**Independent Test**: quickstart Scenario 4 — trees visible when toggled on, unavailable buildings distinct, popup/hover/toggle behavior unchanged, smoke checklists pass.

### Implementation for User Story 3

- [X] T010 [P] [US3] Toggle the `Bäume` layer on and confirm tree polygons (`#39C43D` at 0.75) are clearly visible over the darkened background (FR-006)
- [X] T011 [P] [US3] Locate a building without a valid value and confirm its gray fill (`#444444` at 0.4) is visible and distinct from the darkened background, never merging into it (FR-007)
- [X] T012 [US3] Interaction regression per quickstart Scenario 4: building click opens the compact value popup, empty-space click closes it, hover shows the pointer cursor, zoom in/out keeps the darkening applied (FR-008, FR-009)
- [X] T013 [US3] Extend `tests/frontend/smoke_us1.md` with the darkness checks (base map darker than before; grayscale preserved — no hue; palette distinguishable; 10/10 labels legible at a downtown zoom), then run the published smoke checklists `smoke_us1.md` (extended), `smoke_us2.md`, `smoke_us3.md` (SC-004)

**Checkpoint**: All user stories complete — the darkened map delivers value without regressions.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Governance, evidence, and cleanup across all stories.

- [X] T014 [P] No-network-change check per quickstart Scenario 5: `git diff HEAD -- src/site/style.json` touches only the `basemap` layer `paint` block; browser network tab requests the same basemap.de tile URLs; `dist/manifest.json` artifacts unchanged (SC-005, FR-010)
- [X] T015 [P] Record the measured evidence in `validation/darken/luminance.json`: old/new mean luminance, ratio, and the final `raster-brightness-max` value used (project convention: `validation/` holds measured records)
- [X] T016 Run `make check-or005` (governance gate: no forbidden artifacts tracked; new PNG/JSON records in `validation/darken/` are small and allowed)
- [X] T017 Commit the slice per OR-004: `make commit-slice MSG="darken base map (raster-brightness-max 0.65)"` after T013 and T014 pass

**Checkpoint**: Feature complete, evidenced, and committed.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately. T001 MUST finish before T005 (the old baseline must be captured before `make publish` regenerates `dist/`).
- **Foundational (Phase 2)**: Depends on Setup completion — blocks all user-story verification.
- **User Stories (Phase 3+)**: All depend on Foundational completion.
  - US1 (P1) first: it performs the single source edit (T004).
  - US2 and US3 verify the same bundle and do not edit source except T009 (tuning, conditional). They can run after T005.
  - T009 (tuning) is the only cross-story touchpoint: it re-edits `src/site/style.json` and re-runs T006/T008.
- **Polish (Final Phase)**: Depends on US1–US3 completion.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — no dependencies on other stories.
- **User Story 2 (P2)**: Can start after Foundational and T005 — independently testable; T009 conditionally touches US1's edit.
- **User Story 3 (P2)**: Can start after Foundational and T005 — independently testable; no edits to US1's surface.

### Within Each User Story

- Edit first (T004), publish (T005), measure (T006), then visual checks (T007/T008/T010/T011).
- Manual checks before extending smoke checklists (T013 last in US3).
- Story complete before moving to next priority; T009 tuning only after T008 shows a failure.

### Parallel Opportunities

- T001 and T002 run in parallel (Setup).
- T007 runs in parallel with T006 (both depend only on T005; different surfaces — measurement vs visual).
- T010 and T011 run in parallel (US3, disjoint checks).
- T014, T015 run in parallel (Polish, disjoint files).
- US2's T008 and US3's T010/T011 can run in parallel once T005 is done (different checks, same bundle).

---

## Parallel Example: User Story 1

```bash
# After T005 (bundle regenerated), run measurement and visual check together:
Task: "T006 measure luminance drop (scripts/measure_luminance.py)"
Task: "T007 visual palette check at default zoom"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (baseline capture)
2. Complete Phase 2: Foundational (measurement tool)
3. Complete Phase 3: User Story 1 — the edit, publish, SC-001 gate, palette check
4. **STOP and VALIDATE**: quickstart Scenarios 1–2 pass (SC-001, SC-002)
5. Deploy/demo if ready — the map is darker with palette distinguishable

### Incremental Delivery

1. Setup + Foundational → baseline and tooling ready
2. User Story 1 → measurable darkness + palette check (MVP)
3. User Story 2 → label legibility verified; tune only if needed
4. User Story 3 → overlays + interaction regression + smoke checklists
5. Polish → network/diff evidence, luminance record, OR-005 gate, OR-004 commit

### Parallel Team Strategy

With multiple developers:

1. One captures the baseline (T001/T002) while another writes the measurement tool (T003)
2. US1 implementer does T004–T007
3. After T005, US2 (T008) and US3 (T010/T011) run in parallel
4. T013 (smoke extension) and Polish land after all checks pass

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to the specific user story for traceability
- T004 is the ONLY source edit; everything else verifies or documents it (FR-010: purely visual change)
- Tuning (T009) is bounded by the contract window [0.6, 0.7] in `contracts/base-map-style.md`
- Stop at each checkpoint to validate the story independently
- Avoid: editing any layer other than `basemap` paint, changing tile URLs, reordering layers, or touching `main.js`/`style.css`
