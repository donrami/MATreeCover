---
description: "Task list for Mobile-First Native UX"
---

# Tasks: Mobile-First Native UX

**Input**: Design documents `/specs/012-mobile-native-ux/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, contracts/ (layout-ux.md, surface-interaction.md, touch-a11y-copy.md), quickstart.md
**Tests**: Requested by plan.md (extend `tests/acceptance/test_style.py` with static CSS/DOM assertions; add `tests/frontend/smoke_mobile.md`; SC-009 copy check). Write tests FIRST, fail before implementation.
**Organization**: Tasks grouped by user story, each independently implementable and testable.

## Path Conventions

Static web frontend, no build tool, no backend. Files edited in this feature:

- `src/site/index.html` — `#map`, `#surface` (header/body) restructure of `#left-stack`
- `src/site/style.css` — responsive layout (bottom sheet / panel), motion, touch targets
- `src/site/main.js` — `wireSurfaceToggle()`, `map.setPadding` wiring
- `src/site/style.json` — **UNTOUCHED** (SC-004: palette, layers, metadata verbatim)
- `tests/acceptance/test_style.py` — extended with static assertions
- `tests/frontend/smoke_mobile.md` — NEW manual checklist
- `validation/perf-budget.json` — re-measure; add `surface_toggle`

**Shared contracts (read before implementing, all three stories)**: one `#surface`
component (`position: fixed` bottom sheet < 768 px, `position: absolute` top-left panel >=
768 px); `.surface-header` always present holding legend title + Bäume (`#baeume`) +
Helligkeit (`#brightness-slider`) + expand/collapse toggle; `.surface-body` collapsible
holding full legend (desc, gradient, ticks, units, note) + `#city-panel`. Toggle is a native
`<button>` with `aria-expanded` + `aria-controls="surface-body"`, state class `is-collapsed`
on `#surface`. Motion = `transform`/`opacity`, instant under `prefers-reduced-motion: reduce`.
Zero new network requests, no new deps, no feature add/remove/rename (FR-010, FR-012).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm a clean, green baseline before any presentation rework so regressions are attributable (SC-008).

- [X] T001 Confirm branch `012-mobile-native-ux` is checked out and the working tree is clean; record the current `src/site/{index.html,main.js,style.css}` file sizes as a pre-change baseline
- [X] T002 Run the full acceptance suite (`.venv/bin/python -m pytest tests/`) and `make check-public`; confirm both are green (SC-008) and note the result as the baseline before editing

**Checkpoint**: Baseline green; changes now proceed against a known-good state.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the single shared `#surface` component (DOM, base CSS, toggle wiring) that ALL three user stories depend on. No story can start before this. Per FR-008 the same component set, controls, and JS wiring must serve both breakpoints.

### Implementation — Foundational

- [X] T003 [P] Restructure `src/site/index.html`: replace the static `#left-stack` column with a single `<div id="surface">` containing a persistent `.surface-header` (existing legend heading, `#baeume` toggle, `#brightness-slider`, and a new expand/collapse `<button>` with `aria-expanded` + `aria-controls="surface-body"`) and a `.surface-body` holding the full legend (desc, gradient bar, ticks, units, note) plus the existing `#city-panel` content. Keep `#map` full-bleed, the story modal, `#attribution`, and `.legal-link` untouched (FR-010)
- [X] T004 [P] Add base `#surface` CSS in `src/site/style.css`: panel styling from `--panel-bg`/`--subtle`/`--text`, `z-index: 20` (below the story modal at `z-index: 30`), header layout, styled toggle button; remove the now-obsolete `#left-stack` and `#controls` layout rules (their content moves into the surface header/body)
- [X] T005 Implement `wireSurfaceToggle()` in `src/site/main.js` and call it from `init()`/`onMapLoad()`: the toggle button flips the `is-collapsed` class on `#surface`, mirrors state on `aria-expanded`, and calls `map.setPadding({ bottom: sheetHeightPx })` on expand / `map.setPadding({ bottom: 0 })` on collapse (FR-006, FR-008). Native `<button>` gives keyboard Enter/Space for free (FR-014)

**Checkpoint**: Shared `#surface` component + toggle functional on any viewport; all three stories can now proceed.

---

## Phase 3: User Story 1 — Mobile Map Uses Every Pixel (Priority: P1) 🎯 MVP

**Goal**: On mobile (< 768 px) the map fills the screen; legend/city-overview content is collapsed by default behind a compact thumb-reachable header, expands with one tap to reveal the body without a reload, and collapses back so the map regains >= 80% of the viewport height (FR-001, SC-001).

**Independent Test**: Open the bundle in a narrow (mobile) viewport; verify the map fills the screen with the legend collapsed by default, expand/collapse works in one tap, and building taps still open popups fully visible above the surface while collapsed.

### Tests User Story 1 (write FIRST, fail before implementation)

- [X] T006 [US1] Extend `tests/acceptance/test_style.py` with static DOM/CSS assertions: `#surface` contains `.surface-header` and `.surface-body`; the mobile media query sets `#surface.is-collapsed` by default (FR-001); a `@media (prefers-reduced-motion: reduce)` block disables transitions (FR-008); `#map` stays `position: absolute; inset: 0` (map-dominant). Run to confirm the assertions fail before the implementation exists

### Implementation User Story 1

- [X] T007 [P] [US1] Add the mobile bottom-sheet geometry in `src/site/style.css`: replace the current `@media (max-width: 480px)` block with `@media (max-width: 767.98px)` (R-8 single 768 px breakpoint); `#surface` is `position: fixed; left/right/bottom: 0; width: 100%`, collapsed to header height by default; expanded body `max-height: min(55dvh, 100dvh - env(safe-area-inset-bottom))` with `overflow-y: auto` so it scrolls internally and never overflows the visible viewport; size with `dvh`/`svh` plus a `vh` fallback and pad fixed chrome with `env(safe-area-inset-*)` (FR-007, SC-005)
- [X] T008 [US1] Tune the collapsed strip in `src/site/style.css` so the collapsed surface chrome (header + safe-area padding) occupies no more than 20% of the viewport height, leaving the map >= 80% (SC-001); verify the collapsed surface does not intercept pan/pinch/tap gestures on the map area (US1 acceptance)
- [X] T009 [US1] Verify popup clearance end to end: with the surface expanded and collapsed, confirm building and district popups stay fully visible above the surface at several map positions, including a building tapped near the bottom (FR-006); rely on the foundation `map.setPadding` wiring and adjust sheet-height measurement if a popup is clipped

**Checkpoint**: US1 complete — mobile map is dominant, one-tap expand/collapse, popups clear, independently testable.

---

## Phase 4: User Story 2 — Native-Size, Thumb-Reachable Tools (Priority: P2)

**Goal**: On mobile every interactive control (Bäume, Helligkeit, expand/collapse toggle, zoom buttons, popup close) is at least 44x44 px with at least 8 px spacing, tools stay visible and operable while the legend is collapsed, and no control overlaps the zoom control (top-right) or attribution (bottom-right) (FR-003, FR-004, FR-005).

**Independent Test**: In a mobile viewport, measure every interactive control's touch target and spacing; confirm Bäume and Helligkeit are reachable one-handed in the lower half while the legend is collapsed and nothing overlaps zoom or attribution.

### Tests User Story 2 (write FIRST, fail before implementation)

- [X] T010 [US2] Extend `tests/acceptance/test_style.py` with touch-target assertions: inside the mobile media query `#baeume`, `#brightness-slider`, the surface toggle, MapLibre `.maplibregl-control-button` (zoom), and popup close buttons have `min-width`/`min-height >= 44px` and adjacent targets have `gap >= 8px` (FR-003). Run to confirm they fail before the CSS exists

### Implementation User Story 2

- [X] T011 [P] [US2] Add touch-target CSS overrides in `src/site/style.css` inside the mobile media query: `min-width`/`min-height: 44px` on `#baeume`, `#brightness-slider`, the surface toggle, MapLibre NavigationControl buttons (override the 29 px default, R-3), and popup close buttons; use `gap >= 8px` for spacing (FR-003)
- [X] T012 [US2] Confirm Bäume and Helligkeit remain visible and operable while the surface is collapsed (they live in the persistent `.surface-header`, FR-004); assert no-overlap per the layout-ux matrix: surface header/tools are disjoint from the zoom control (top-right), `#attribution` (bottom-right), and `.legal-link` (bottom-left) in both surface states (FR-005)
- [X] T013 [US2] Harden for very small phones (>= 320 px) and landscape phones: ensure the surface, tools, and controls never overflow the viewport and stay usable (edge case); adjust internal scroll cap and touch layout as needed

**Checkpoint**: US2 complete — all mobile controls native-size, thumb-reachable, non-overlapping.

---

## Phase 5: User Story 3 — Consistent, Space-Optimized Desktop (Priority: P3)

**Goal**: On desktop (>= 768 px) the identical `#surface` component renders as a collapsible panel top-left, expanded by default (matches current behaviour), collapsible so the map reclaims space, with every existing feature (story modal, district popup, building popup, attribution, Impressum, Bäume, Helligkeit) behaving exactly as before (FR-008, FR-010).

**Independent Test**: Open the bundle in a desktop viewport; confirm the surface matches the mobile component set (header/body, tools, controls), collapse it to reclaim map space with nothing clipped, and verify all existing interactions still behave.

### Tests User Story 3 (write FIRST, fail before implementation)

- [X] T014 [US3] Extend `tests/acceptance/test_style.py` with a desktop assertion: at >= 768 px `#surface` uses the same `.surface-header`/`.surface-body` component set and is expanded by default (no `is-collapsed` in the desktop default), guarding against a divergent desktop design (FR-008). Run to confirm it fails before the desktop CSS exists

### Implementation User Story 3

- [X] T015 [P] [US3] Add the desktop panel geometry in `src/site/style.css` for `@media (min-width: 768px)`: `#surface` is `position: absolute; top: 12px; left: 12px; z-index: 10` (same spot as the old `#left-stack`), expanded by default, collapsible with the body hidden when collapsed so the map reclaims the freed space with no content clipped; expanded body height is content-driven with an internal scroll cap
- [X] T016 [US3] Verify the 768 px breakpoint transitions cleanly in BOTH directions: resize a desktop window down across the breakpoint and back, confirming the surface swaps between panel and bottom-sheet geometry with no broken overlaps or content overflow (edge case)
- [X] T017 [US3] Run a full feature-parity check: Bäume toggle, Helligkeit slider, first-visit story modal, city-overview panel, building popup, district popup, attribution, and Impressum all keep their current behaviour exactly (FR-010); no feature added, removed, or renamed; `src/site/style.json` remains untouched (SC-004)

**Checkpoint**: US3 complete — desktop consistent with mobile, space-optimized, full parity.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Manual verification, performance, copy/accessibility gates, and final acceptance across all stories.

- [X] T018 [P] Create `tests/frontend/smoke_mobile.md` manual checklist covering US1-3 and edge cases per `quickstart.md`: mobile map-dominant, expand/collapse + popup visibility, native-size thumb tools, consistent desktop, very small/landscape phones, safe-area, breakpoint resize, address-bar layout shift, reduced-motion, large-text reflow
- [X] T019 [P] Re-measure performance and add `surface_toggle` to `interaction_latency_ms` in `validation/perf-budget.json` (SC-006); confirm the expand/collapse interaction is a compositor-only `transform`/`opacity` transition and completes within the 2 s budget with no first-usable-map regression
- [X] T020 [P] Add the SC-009 copy check: assert zero em-dashes and zero en-dashes in all new German copy strings (e.g. `Legende einblenden` / `Legende ausblenden`) in `tests/acceptance/test_style.py`; reuse existing legend/city-overview copy where possible (FR-011); leave the `UNAVAILABLE` en-dash constant unchanged
- [X] T021 Run the full acceptance suite (`.venv/bin/python -m pytest tests/`) and `make check-public`; confirm both are green (SC-008) and run the new `tests/frontend/smoke_mobile.md` checklist in a browser
- [X] T022 Final accessibility sweep (SC-010): confirm every control is keyboard-operable with a visible `:focus-visible` outline (extend the existing `.legal-link:focus-visible` pattern), all new surfaces meet WCAG AA contrast on the dark theme, and screen-reader labels (incl. `aria-expanded`/`aria-controls`) describe the surface and tools

**Checkpoint**: Feature complete — all automated checks green, manual checklist passes, parity and performance gates hold.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. BLOCKS all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational completion. US1 → US2 → US3 in priority order (each is independently testable; a later story can be staffed after the foundation without waiting on the previous story's full completion).
- **Polish (Final Phase)**: Depends on all three user stories complete.

### User Story Dependencies

- **User Story 1 (P1)**: starts after Foundational. No dependency on other stories.
- **User Story 2 (P2)**: starts after Foundational. Relies on US1's mobile media query block but is independently testable (touch targets + tools + no-overlap).
- **User Story 3 (P3)**: starts after Foundational. Shares the `#surface` component; independently testable (desktop panel + parity).

### Within Each User Story

- Tests (T006, T010, T014) MUST be written FIRST and fail before the corresponding implementation.
- HTML/CSS structure before JS wiring in the foundation; geometry before tuning/verification in each story.
- Story complete and independently verified before moving to the next priority.

### Parallel Opportunities

- Setup: T001, T002 run in parallel (independent checks).
- Foundational: T003 (index.html) and T004 (style.css) are different files and run in parallel.
- US1: T006 (test_style.py) and T007 (style.css) run in parallel (different files).
- US2: T010 (test_style.py) and T011 (style.css) run in parallel.
- US3: T014 (test_style.py) and T015 (style.css) run in parallel.
- Polish: T018, T019, T020 are independent files (smoke_mobile.md, perf-budget.json, test_style.py) and run in parallel.
- Once Foundational is done, US1/US2/US3 can be staffed in parallel by different developers (per the shared `#surface` component), then integrated.

---

## Parallel Example: User Story 1

```bash
# Launch the US1 test and geometry together (different files):
Task: "Extend tests/acceptance/test_style.py with surface/collapsed/reduced-motion assertions"
Task: "Add the mobile bottom-sheet geometry in src/site/style.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (green baseline).
2. Complete Phase 2: Foundational (CRITICAL — the shared `#surface` component blocks all stories).
3. Complete Phase 3: User Story 1 (mobile map-dominant, one-tap expand/collapse, popups clear).
4. **STOP VALIDATE**: Test User Story 1 independently per its Independent Test.
5. Deploy/demo the MVP (mobile-first map is the single biggest quality improvement).

### Incremental Delivery

1. Setup + Foundational → shared surface ready.
2. Add User Story 1 → test independently → deploy/demo (MVP).
3. Add User Story 2 (native-size thumb tools) → test independently → deploy/demo.
4. Add User Story 3 (consistent desktop) → test independently → deploy/demo.
5. Each story adds value without breaking the previous stories (FR-010 parity preserved).

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. Once Foundational is done: Developer A → US1, Developer B → US2, Developer C → US3.
3. Stories integrate independently on the shared `#surface` component.

---

## Notes

- [P] tasks edit different files and have no interdependencies; same-file tasks are sequential.
- [US1]/[US2]/[US3] labels map tasks to their spec user story for traceability.
- Every user story is independently completable and testable.
- Tests (T006/T010/T014) are written FIRST and must fail before implementation.
- Avoid: vague tasks, same-file parallel conflicts, cross-story dependencies that break independence.
- `src/site/style.json` and the data pipeline are deliberately UNTOUCHED (SC-004); never edit them.
- German copy only, no em/en dashes, hyphens inside compounds only (FR-011, SC-009).

---

## Phase 7: Convergence

**Purpose**: Close gaps surfaced in post-implementation review (user feedback on the
published UX). Append-only; completing these is the job of `/speckit.implement`.

- [X] T023 Relocate the mobile attribution (map data / copyright footer) to the top-left corner so it stays visible with the bottom sheet collapsed or expanded, and let its long text wrap to the next line when expanded, per FR-005 (partial) — file: `src/site/style.css`
- [X] T024 Relocate the Impressum link to the top-left corner under the attribution on mobile so it is always visible with the sheet in any state, per plan DDG § 5 / FR-005 (partial) — file: `src/site/style.css`
- [X] T025 Remove the bordered box (border / border-radius) from the surface expand-collapse toggle so it renders as a bare arrow on desktop, keeping a 44x44 px hit area and a visible `:focus-visible` outline, per FR-002 / FR-008 (partial) — file: `src/site/style.css`
- [X] T026 Verify the relocated attribution and Impressum links stay functional after the T023/T024 move: correct `href` (`attribution` / `impressum`), reachable target pages, clickable with adequate touch target, not clipped or covered by the surface or the story modal, per FR-005 / FR-010 (partial) — files: `src/site/style.css`, `src/site/main.js`, `attribution.html`, `impressum.html`
- [X] T027 Align the orange-to-blue color transition to the 30% mark in both the map color scale and the legend bar: move the `#0674aa` blue stop from 24.08% to 30% in the buildings-fill `fill-color` in `src/site/style.json` and mirror it in the `.legend-gradient-bar` gradient in `src/site/style.css`, then update `PALETTE_STOPS` in `tests/acceptance/test_style.py` to match, per user review / the 30% shade guideline (partial) — files: `src/site/style.json`, `src/site/style.css`, `tests/acceptance/test_style.py`

---

## Phase 8: Convergence

**Purpose**: Close the last gaps found on the second converge pass (post-review
state). Append-only; completing these is the job of `/speckit.implement`.

- [X] T028 Give the mobile buildings-failure message slot (`#attribution`, populated only when the buildings layer fails) a distinct top-left position below the MapLibre attribution control, with a narrower `max-width` so the failure text never overlaps the attribution control or the zoom column, per plan pmtiles-sources contract / FR-005 (partial) — file: `src/site/style.css`
- [X] T029 Update `tests/frontend/smoke_mobile.md` to the relocated mobile chrome (attribution and Impressum now top-left, not bottom-right / above the sheet) and add checks for the 30% scale-bar boundary and the bare-arrow expand toggle, per FR-005 / FR-008 (partial) — file: `tests/frontend/smoke_mobile.md`
