# Tasks: Ko-fi Donation Button — Footer Placement Revision

**Input**: Design documents `/specs/017-ko-fi-button/` (plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md)

**Prerequisites**: plan.md (required), spec.md (required user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: tests ARE part of this feature — the spec defines Independent Tests and acceptance scenarios for every user story, and the plan scopes updates to the existing acceptance module, smoke checklist, and headless smoke scenario. Test updates are the story verification tasks below.

**Organization**: Tasks grouped by user story for independent implementation and testing. NOTE: the placement relocation itself is a single atomic markup + CSS change shared by US1/US2/US3 (one DOM move, one CSS file) — it lives in the Foundational phase so no story phase edits the same file; story phases own their verification artifacts (acceptance module, smoke scripts, browser checks).

**Implementation state**: a header-based implementation already landed on this branch (markup in `.surface-header`, header-packing CSS, CSP extension in all 3 carriers, tests, smoke checklist, smoke scenario). These tasks RELOCATE the landed work to the surface footer per the clarified spec. The CSP extension and the design artifacts (`contracts/ko-fi-button.md`, `csp-image-host.md`, `quickstart.md`, `research.md`, `data-model.md`) are already updated in the plan phase — no tasks here touch them. `main.js` needs NO change (desktop expands by default; `syncPadding` measures `surface.offsetHeight`).

## Format: `- [ ] [ID] [P?] [Story] Description with file path`

- **[P]**: run in parallel (different files, no dependencies)
- **[Story]**: user story the task belongs to (US1, US2, US3, US4)
- Include file paths in descriptions

## Path Conventions

Single project: `src/`, `tests/`, `scripts/`, `workers/` at the repository root. All paths relative to the repo root.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the pre-relocation baseline is green so the move starts from a known state.

- [X] T001 Verify baseline: run `make publish` and the full suite (`.venv/bin/python -m pytest tests/ -q`) and confirm the current header implementation is green (CSP lockstep tests included); record the pass summary. No file changes.

**Checkpoint**: Baseline green — relocation may start.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The shared core — one atomic relocation serving US1/US2/US3. MUST complete before any user story verification is meaningful.

- [X] T002 [P] Move the `.ko-fi` anchor out of `.surface-header` into a new `<footer class="surface-footer">` as the LAST child of `.surface-body` (after `.surface-body-inner`) in `src/site/index.html`; set the image `alt="Unterstützen"` (accessible name, FR-006); restore the header DOM order to title → `.surface-tools` → `#surface-toggle` (chevron rightmost, feature 012). Keep `href`/`target="_blank"`/`rel="noopener"` and `src`/`width="143"`/`height="36"` exactly as landed.
- [X] T003 [P] Update `src/site/style.css`: add `.surface-footer` rules (direct child of `.surface-body`; `position: sticky; bottom: 0;` `display: flex; justify-content: center;` `padding: 8px 14px;` `background: var(--panel-bg);` `border-top: 1px solid var(--subtle);`); DELETE the obsolete header-packing rules — the `.ko-fi` order overrides in the `@media (max-width: 680px)` block and the `@media (max-width: 350px)` image-shrink block; KEEP the `.ko-fi` base rules (inline-flex, padding 4px 0, img 143×36), the `:hover`/`:focus-visible` outline rule, and `.ko-fi` membership in the mobile touch-target rule group (≥ 44 × 44 px, FR-004).

**Checkpoint**: Build (`make publish`) and browser check — expanded surface: button visible in the footer, centered, no scrolling needed; collapsed surface: button hidden (feature-012 body collapse). No JS change made or needed.

## Phase 3: User Story 1 — Desktop Visitors Find and Use the Donation Button (Priority: P1)

**Goal**: On desktop (≥ 768 px, panel expanded by default), the Ko-fi button is clearly visible in the surface footer without scrolling; it opens the Ko-fi page in a new tab; it is hidden when the panel is collapsed.

**Independent Test**: `pytest tests/acceptance/test_ko_fi.py -q` green (footer position + exact alt + deleted-rule absence + CSP lockstep); `node scripts/smoke-verify.mjs <url>` ko-fi scenario green at 768/1280/1920; manual checklist US1 section.

### Implementation User Story 1

- [X] T004 [P] [US1] Update `tests/acceptance/test_ko_fi.py` for the footer placement: assert the `.ko-fi` anchor sits inside `.surface-footer`; `.surface-footer` is the last child of `.surface-body`; no `.ko-fi` element remains inside `.surface-header`; the image `alt` is exactly `Unterstützen` (replace the donation-word-contains check with an exact-match check); assert the deleted header-packing rules are absent from `src/site/style.css` (no `.ko-fi { order:` rule, no `max-width: 350px` `.ko-fi img` height override); keep `.ko-fi` in the mobile touch-target rule group assertion; leave the CSP lockstep tests (`test_csp_*`, `test_worker_header_csp_byte_identical_to_meta`) byte-identical.
- [X] T005 [P] [US1] Update the ko-fi scenario in `scripts/smoke-verify.mjs`: rename the visibility check to footer (button rect fully inside the viewport at 768/1280/1920 with the panel expanded by default); add a collapsed-hidden assertion — click `#surface-toggle`, assert the `.ko-fi` rect has zero size, toggle back; keep the exact-URL new-tab click and `mapPageStillOpen` checks unchanged.
- [X] T006 [P] [US1] Rewrite `tests/frontend/smoke_ko_fi.md` for the footer placement: US1 section — footer visibility expanded (768/1280/1920), hidden when collapsed, click opens new tab, header row back to title → tools → chevron; US2 section — collapsed sheet has NO donation button, map ≥ 80 %, expanded sheet shows the footer button, touch target ≥ 44 × 44 px, ≥ 8 px spacing, 320 px floor (no image-shrink fallback), safe areas; US3 section — accessible name exactly "Unterstützen", focus indicator, image renders with zero CSP violations; edge-case section — collapsed-state visibility is the intended de-emphasis, 36-px-visual/44-px-hit-area, `rel="noopener"`, unavailability fallback, language consistency. (Single file, cross-story manual checklist — updated once here.)

**Checkpoint**: Acceptance tests and headless smoke green — US1 fully functional and testable independently.

## Phase 4: User Story 2 — Mobile Visitors Find and Use the Donation Button (Priority: P1)

**Goal**: On mobile (< 768 px, sheet collapsed by default), the collapsed sheet shows no donation chrome and the map occupies ≥ 80 % of the viewport; when expanded, the footer button is visible, its touch target is ≥ 44 × 44 px with ≥ 8 px spacing, and tapping it opens the Ko-fi page in a new tab.

**Independent Test**: Browser verification of quickstart Q3/Q4/Q5/Q8 (collapsed-hidden, map ≥ 80 %, touch target, spacing, no-overlap matrix, 320 px floor, safe areas); machine checks already covered by T004.

### Implementation User Story 2

- [X] T007 [US2] Verify the mobile behavior in a real browser per `specs/017-ko-fi-button/quickstart.md` Q3 (collapsed → no button, sheet chrome ≤ 20 % / map ≥ 80 %; expanded → footer visible), Q4 (`getBoundingClientRect()` of `.ko-fi` ≥ 44 × 44 px, image visually 36 px), Q5 (overlap matrix empty at 320/375/768/1280/1920 in the expanded state), Q8 (320 × 568: no overflow, sticky footer stays visible with the city panel open, notched-device safe-area clearance, 768 px resize transition); record results against `tests/frontend/smoke_ko_fi.md` US2 checkboxes.

**Checkpoint**: US2 acceptance scenarios pass — sheet collapsed has no button; expanded footer is touch-target compliant.

## Phase 5: User Story 3 — The Button Renders and Is Accessible (Priority: P2)

**Goal**: The button image renders (never blocked/broken/blank), its accessible name is exactly "Unterstützen", it is keyboard-operable with a visible focus indicator, and the external link is `rel="noopener"` safe.

**Independent Test**: Browser verification of quickstart Q6/Q7 (CSP console zero violations, image render, keyboard Tab + Enter, accessible name in the devtools accessibility panel); machine checks already covered by T004.

### Implementation User Story 3

- [X] T008 [US3] Verify accessibility and rendering per `specs/017-ko-fi-button/quickstart.md` Q6 (image renders, devtools console shows zero CSP violations) and Q7 (Tab reaches the button with a visible `:focus-visible` indicator, Enter opens the Ko-fi URL in a new tab, the accessible name is exactly "Unterstützen"); record results against `tests/frontend/smoke_ko_fi.md` US3 checkboxes.

**Checkpoint**: US3 acceptance scenarios pass.

## Phase 6: User Story 4 — Nothing Regresses (Priority: P2)

**Goal**: The map experience, layout invariants, security posture, and performance budgets are unchanged; the button is purely additive.

**Independent Test**: All governance gates green, full test suite green, perf budgets hold, parity render identical (quickstart Q9).

### Implementation User Story 4

- [X] T009 [P] [US4] Run the governance gates and full suite per `specs/017-ko-fi-button/quickstart.md` Q9: `make check-public && make check-layout && make check-or005 && make check-history` and `.venv/bin/python -m pytest tests/ -q`; confirm the CSP lockstep tests still pass unchanged (the image-host extension stays byte-identical in meta, Worker header, feature-015 contract).
- [X] T010 [P] [US4] Run the performance and parity verification per quickstart Q9: `bash scripts/perf-measure.sh <url>` (all 8 interactions ≤ 2 s, desktop median ≤ 123 ms, first usable ≤ 10 s) and `node scripts/parity-render.mjs --archive dist/buildings.pmtiles --out /tmp/parity-017` (building values, colors, labels, popups identical to the previous bundle).

**Checkpoint**: All gates and budgets green — zero regressions proven.

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final housekeeping across the feature.

- [X] T011 Add the release-log entry for the feature to `CHANGELOG.md` (footer placement revision, placement decision reference).
- [X] T012 Final consistency sweep: grep `src/site/` and `tests/` for stale header-placement references (`.ko-fi` inside `.surface-header`, "Baumfläche auf Ko-fi unterstützen" alt, `.ko-fi { order:` rules) and remove any leftovers; run `make publish` + `.venv/bin/python -m pytest tests/acceptance/test_ko_fi.py -q` once more as the final proof.

**Checkpoint**: Feature complete — clean tree, green tests, changelog recorded.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001) — BLOCKS all user stories (the markup + CSS relocation is the shared core).
- **User Stories (Phases 3–6)**: Depend on Foundational completion.
- **Polish (Phase 7)**: Depends on all user story phases.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational. Owns the acceptance module update (T004) and the headless smoke scenario (T005) — these machine checks also cover US2/US3 contract points (touch-target group, exact alt).
- **US2 (P1)**: Starts after Foundational; its browser verification (T007) depends on T004 being merged (machine checks referenced) but is independently executable against the built bundle.
- **US3 (P2)**: Starts after Foundational; verification (T008) independently executable against the built bundle.
- **US4 (P2)**: Depends on all stories complete (full-suite + gates run on the final tree).

### Within Each User Story

Implementation/verification before checkpoint; story complete before moving to the next priority.

### Parallel Opportunities

- Phase 2: T002 (index.html) and T003 (style.css) run in parallel — different files.
- Phase 3: T004 (test_ko_fi.py), T005 (smoke-verify.mjs), T006 (smoke_ko_fi.md) run in parallel — different files.
- Phase 6: T009 (gates) and T010 (perf/parity) run in parallel — independent harnesses.
- Different stories: US2 and US3 browser verification can run in parallel once Phase 2 is complete (T007 and T008 touch no files in conflict).

## Parallel Example: Foundational + US1

```bash
# Phase 2 (parallel):
Task: "T002 Move .ko-fi anchor into .surface-footer in src/site/index.html (alt=Unterstützen)"
Task: "T003 Update src/site/style.css — add .surface-footer rules, delete header-packing rules"
# Phase 3 (parallel, after Phase 2 checkpoint):
Task: "T004 Update tests/acceptance/test_ko_fi.py for footer placement"
Task: "T005 Update ko-fi scenario in scripts/smoke-verify.mjs"
Task: "T006 Rewrite tests/frontend/smoke_ko_fi.md for footer placement"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (baseline green).
2. Complete Phase 2: Foundational (CRITICAL — the relocation blocks every story).
3. Complete Phase 3: User Story 1 (acceptance tests + headless smoke + manual checklist).
4. **STOP VALIDATE**: US1 independently — `pytest test_ko_fi.py` + `smoke-verify.mjs` green at 768/1280/1920.
5. Deploy/demo if ready — note the button is already visible on mobile expanded too (the relocation is atomic), so the MVP ships most of US2/US3 behavior as a side effect.

### Incremental Delivery

1. Complete Setup + Foundational → foundation ready (button relocated to the footer, hidden when collapsed).
2. Add US1 verification → test independently → deploy/demo (MVP).
3. Add US2 verification → test independently.
4. Add US3 verification → test independently.
5. Add US4 → full gates + perf + parity → release.
6. Each story adds value without breaking previous stories.

### Parallel Team Strategy

1. Team completes Setup + Foundational together (T001 → T002 + T003).
2. Once Foundational is done: one developer runs T004/T005/T006 (US1 artifacts), another prepares the US2/US3 browser checks.
3. Stories integrate and are verified independently; US4 gates run on the final tree.

## Notes

- [P] tasks touch different files and have no dependencies.
- [Story] labels map tasks to the spec user stories for traceability.
- Commit in logical groups per OR-004 (plan commit via `make commit-plan`; implementation in slice commits).
- The design artifacts (`contracts/ko-fi-button.md`, `contracts/csp-image-host.md`, `quickstart.md`, `research.md`, `data-model.md`, `plan.md`) were regenerated in the plan phase and need no implementation edits — `contracts/csp-image-host.md` is unchanged because the CSP extension already landed and is placement-agnostic.
- `main.js` is intentionally untouched: desktop expand-by-default and `syncPadding` (measures `surface.offsetHeight`) already accommodate the footer.
- This file replaces the stale header-based `tasks.md` from the previous plan run.
