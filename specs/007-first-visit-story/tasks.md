# Tasks: First-Visit Story Modal

**Input**: Design documents from `/specs/007-first-visit-story/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test harness exists in this project (documented convention: manual smoke checklists). The smoke-checklist tasks below (`tests/frontend/smoke_us5.md` creation and extensions, quickstart scenario runs, `validation/first-visit-story/` evidence) are implementation-phase verification work required by plan.md/quickstart.md, not optional tests.

**Organization**: Stories US1–US3 all touch shared files in `src/site/` (the modal markup, story copy, and links live in `src/site/index.html`; show/dismiss and persistence logic live in `src/site/main.js`), so stories run as sequential slices; [P] is only used within a story for file-disjoint work.

**Status**: Generated 2026-08-05 from plan/spec/contracts. Phases 1–2 must complete before any user story. T006 is a **merge gate**: the final story wording must be approved by the user before merge (spec clarification, FR-015) — it blocks shipping, not later implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Static frontend: `src/site/` (index.html, style.css, main.js) at repository root — edited in place, no new static asset (modal markup ships inside `index.html` per `STATIC_FILES` in `src/pipeline/publish.py`)
- Verification: `tests/frontend/` smoke checklists (new `smoke_us5.md`), `validation/first-visit-story/` evidence records (004 precedent: `validation/brightness-slider/`)
- Copy source of truth: `specs/007-first-visit-story/contracts/story-content.md`

---

## Phase 1: Setup

**Purpose**: Verify the environment and the pre-change baseline before any modification

- [ ] T001 Checkout branch `007-first-visit-story` and verify tooling per quickstart prerequisites: a Range-capable static server is available (nginx or equivalent — plain `python -m http.server` breaks the map's PMTiles range requests), a browser with WebGL 2 enabled is available, and `make publish` produces `dist/` from the unmodified tree

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the regression baseline every story must preserve (SC-005, FR-014)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Publish the unmodified baseline (`make publish`), serve `dist/`, and run the existing smoke checklists `tests/frontend/smoke_us1.md`, `smoke_us2.md`, `smoke_us3.md`, `smoke_us4.md` to confirm all pass before any change (FR-007/FR-014 regression surface, SC-005)

**Checkpoint**: Foundation ready — the pre-change bundle is green; user story implementation can begin

---

## Phase 3: User Story 1 - First-Time Visitor Reads Story (Priority: P1) 🎯 MVP

**Goal**: On first visit (no stored dismissal state), a short German story modal appears automatically over the loaded map: how the map came to be (SPIEGEL article → CityTreeCover reference project → this Mannheim replication), why tree cover matters in the June/July 2026 heatwave, and the map's central value (buildings colored by average tree cover in their 60-m surroundings, matching the legend text). The modal is dismissible via a visible close button or Escape, fully keyboard- and screen-reader-operable, never overlaps the existing UI, and closing it causes no layout shift (FR-001, FR-002, FR-003, FR-004, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-015).

**Independent Test**: quickstart Scenario 1 (modal appears automatically on first load over the fully rendered map) + Scenario 2 (all story elements and links present) + Scenario 5 (keyboard-only flow, screen-reader dialog announcement) + Scenario 6 (overlap matrix with the open modal rect, pairwise disjoint at 320/480/768/1280/1920 px).

### Implementation for User Story 1

- [ ] T003 [US1] Add the story-modal markup to `src/site/index.html` before the closing `</body>` (after the existing `#attribution` div), per the markup contract in `specs/007-first-visit-story/contracts/story-modal.md`: `div.story-backdrop#story-backdrop[hidden]` fixed overlay containing `div.story-modal#story-dialog[role="dialog"][aria-modal="true"][aria-labelledby="story-title"][tabindex="-1"]` with `h2#story-title` (German heading), `button#story-close[type="button"][aria-label="Schließen"]` showing a visible glyph, the story paragraphs and the two reference links per the normative copy in `specs/007-first-visit-story/contracts/story-content.md` (SPIEGEL article link with the article title as link text, CityTreeCover link naming the project; both `target="_blank" rel="noopener"` — FR-006); static markup only — no inline scripts (CSP `script-src 'self'`), no fetch (FR-011); markup exists only in `index.html`, never in `src/site/attribution.html` (FR-012, holds by construction — attribution.html includes no `main.js`)
- [ ] T004 [P] [US1] Add the modal layout to `src/site/style.css` per the placement contract in `specs/007-first-visit-story/contracts/story-modal.md`: `.story-backdrop { position: fixed; inset: 0; z-index: 30; }` (above `#left-stack`/`#attribution` at z-index 10 and the map controls); `.story-modal` in the viewport safe zone — desktop (>480 px): top margin 260 px (below the left column), centered horizontally, `max-width: 480px`, `max-height: calc(100vh - 284px)`; ≤480 px media query: top margin 60 px, `width: calc(100vw - 24px)`, `max-height: calc(100vh - 220px)`; `overflow-y: auto` (content scrolls inside the modal, never the page — nothing clips at text zoom, FR-010); close-button styling and panel theme matching `--panel-bg`/`--subtle`/`--text` variables; no change to any existing rule
- [ ] T005 [P] [US1] Implement the story-modal behavior in `src/site/main.js` as one self-contained module (no MapLibre API calls — FR-014): show at `init()` by removing the `hidden` attribute from `#story-backdrop` and moving focus to `#story-dialog` (screen reader announces the dialog name from `aria-labelledby` — FR-009); install a keydown listener while open — Escape closes, Tab/Shift+Tab trap focus inside the dialog cycling the close button and the two reference links (FR-008); close (close-button click or Escape) removes the backdrop from the DOM (map immediately interactive, no reflow or reload — FR-007), restores focus to the previously focused element (document body on page-load open), and tears down the listeners; show unconditionally in this story — the dismissal-state gate lands in US2 (T007); per the dismissal wiring in `contracts/story-modal.md` (backdrop click does NOT dismiss)
- [ ] T006 [US1] Submit the final story wording for user approval: present the German copy as implemented in `src/site/index.html` (normative draft in `specs/007-first-visit-story/contracts/story-content.md`; phrasing may be adjusted but every required element, both link targets, and the short-story length MUST be kept) and obtain the user's explicit final-wording approval; run the FR-015 mechanical gates on the modal text — zero em-dashes (—), zero en-dashes (–), hyphens only inside compounds (e.g. "60-m-Umkreis") — plus the human prose review (spec clarification: "implementer drafts copy; user reviews and approves final wording before merge"); **merge is BLOCKED until approved**

**Checkpoint**: User Story 1 fully functional — the modal appears on first visit with the complete German story, dismisses via close button and Escape, is keyboard/screen-reader operable, and the open modal is pairwise disjoint from all existing UI elements

---

## Phase 4: User Story 2 - Returning Visitor Is Not Shown Modal Again (Priority: P2)

**Goal**: Dismissal persists on-device: the modal never reappears on later visits or reloads in the same browser while the dismissal state exists, and clearing the site data restores first-visit behavior. When on-device storage is unavailable or blocked, the modal still appears and remains dismissible for the current visit (FR-005, FR-013, FR-011).

**Independent Test**: quickstart Scenario 3 (dismiss → reload → no modal; close tab, reopen → no modal; clear site data → modal appears again) + Scenario 4 (storage blocked → modal still appears and dismisses; only in-memory flag written; no console errors).

### Implementation for User Story 2

- [ ] T007 [US2] Implement dismissal persistence in `src/site/main.js` (extends the T005 show/dismiss wiring; depends on it): read the `localStorage` key `matreecover.story-dismissed` once at `init()` — key present ⇒ modal stays hidden; key absent or storage unavailable ⇒ modal shows; write the key with value `"1"` ONLY on explicit dismissal (close-button click or Escape), never on page load or on show (no measurement, no tracking — FR-011); wrap every `localStorage` access in `try/catch` and substitute a session-only in-memory boolean flag on any failure (FR-013: modal still appears and dismisses for the current visit, reappears on the next visit); per `specs/007-first-visit-story/contracts/dismissal-state.md` (no timestamp, counter, or version stored)
- [ ] T008 [P] [US2] Create `tests/frontend/smoke_us5.md` — the first-visit story modal checklist, following the `tests/frontend/smoke_us4.md` format (Goal, FR/SC mapping, Setup, Checks, Result) and covering quickstart scenarios 1–9: first-visit automatic appearance in German (FR-001, SC-001); all story elements and both working links (FR-002/FR-003/FR-006, SC-003); close-button and Escape dismissal with map immediately interactive and no layout shift — map container `getBoundingClientRect()` unchanged before/after close, no reload in the network panel (FR-004/FR-007, SC-004); persistence across reload and session + storage-cleared restore (FR-005, SC-002); storage-blocked fallback (FR-013); keyboard-only flow and screen-reader dialog announcement ("Wie diese Karte entstanden ist") (FR-008/FR-009, SC-006); overlap matrix with the open modal rect added to the 004 console script (`document.getElementById('story-dialog')`) at widths 320/480/768/1280/1920 px, pairwise disjoint (FR-010, SC-008); network panel shows zero new requests on open/close and the only storage write is `matreecover.story-dismissed` (FR-011, SC-007); attribution page never shows the modal (FR-012); post-dismissal re-run of `smoke_us1.md`–`smoke_us4.md` stays green (FR-014, SC-005)

**Checkpoint**: User Story 2 fully functional — the modal appears exactly once per browser, persists across reloads and sessions, and degrades gracefully when storage is blocked

---

## Phase 5: User Story 3 - Visitor Follows References (Priority: P2)

**Goal**: From the modal, the visitor opens the SPIEGEL article and the CityTreeCover project in new tabs; both links resolve to the expected pages and the map tab is never navigated away or altered (FR-006, SC-003).

**Independent Test**: quickstart Scenario 2 (activate each link → opens in a new tab resolving the expected page; return to the map tab → map unchanged and fully usable). No code change is needed for this story — the link markup ships in T003; these tasks verify and pin the behavior.

### Implementation for User Story 3

- [ ] T009 [P] [US3] Verify at merge time that both reference URLs from `specs/007-first-visit-story/contracts/story-content.md` resolve (HTTP 200): the SPIEGEL article URL (https://www.spiegel.de/wissenschaft/natur/hitze-in-europa-wie-gut-stadtbaeume-vor-extremer-waerme-schuetzen-a-9a0b26e5-f8ae-4fa5-a897-2f2b026f5226) and https://github.com/jcscaptures/CityTreeCover (both verified resolving on 2026-08-05 during research; re-check before merge per quickstart Scenario 2)
- [ ] T010 [P] [US3] Add the US3 link checks to `tests/frontend/smoke_us5.md`: both links in the modal carry `target="_blank" rel="noopener"` and the article title / project name as link text; activating each opens a new tab resolving the expected page (SPIEGEL article "Hitze in Europa: Wie gut Stadtbäume vor extremer Wärme schützen"; CityTreeCover at github.com/jcscaptures/CityTreeCover); returning to the map tab shows the map unchanged and fully usable (FR-006, SC-003)

**Checkpoint**: All user stories independently functional — the modal shows once per browser with the complete story, persists dismissal, and both references open correctly in new tabs

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation, evidence, and delivery discipline

- [ ] T011 Run quickstart scenarios 1–9 end-to-end on the published bundle (`make publish`, serve `dist/`) and fix any failures (blocking gates: Scenario 2 story + links, Scenario 3 persistence, Scenario 4 storage-blocked fallback, Scenario 5 keyboard/screen-reader, Scenario 6 overlap matrix, Scenario 7 network panel, Scenario 8 attribution page, Scenario 9 no-regression)
- [ ] T012 [P] Run all five smoke checklists (`tests/frontend/smoke_us1.md`–`smoke_us5.md`) and confirm green — `smoke_us1.md`–`smoke_us4.md` must be unchanged (regression surface, FR-014)
- [ ] T013 [P] Record validation evidence into `validation/first-visit-story/` (matching the 004 precedent `validation/brightness-slider/`): `overlap.json` (overlap matrix including the open modal rect at widths 320/480/768/1280/1920 px) and the network-panel observation of zero new requests and the single `matreecover.story-dismissed` storage write (FR-010/FR-011, quickstart scenarios 6–7)
- [ ] T014 Commit per OR-004: `make commit-slice` after each story slice (US1 incl. the approved story wording, US2, US3) and `make commit-milestone` after the final validation pass (T011–T013), with the commit-check script passing (clean worktree per slice)

**Checkpoint**: Feature complete — quickstart 1–9 green, all five smoke checklists green, evidence recorded under `validation/first-visit-story/`, story wording approved by the user, commits per OR-004

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (regression baseline must be green first)
- **User Stories (Phase 3+)**: Depend on Foundational; run sequentially because all three stories edit shared files in `src/site/` (`index.html`, `main.js`) and `tests/frontend/smoke_us5.md`
- **Polish (Final Phase)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational. No dependency on US2/US3.
- **User Story 2 (P2)**: Can start after Foundational AND after US1 — T007 (persistence) extends the T005 show/dismiss wiring in `src/site/main.js`. Sequenced after US1 to avoid same-file conflicts in `main.js`.
- **User Story 3 (P2)**: Can start after Foundational; T010 appends to `smoke_us5.md` (created in US2, T008) — sequenced after US2 to keep story slices clean.
- **T006 (story wording approval)**: Depends on T003 (copy implemented in `index.html`); runs as a gate — it blocks the merge (and the T014 milestone commit), not the implementation of US2/US3.

### Within Each User Story

- Markup first (the elements the CSS/JS bind to: T003), then [P] file-disjoint work (T004 style.css, T005 main.js), then the approval gate (T006)
- In US2: persistence wiring in `main.js` (T007) first, then the file-disjoint checklist creation (T008)
- In US3: link verification (T009) and checklist extension (T010) are file-disjoint and can run together
- Story complete (checkpoint) before moving to the next priority

### Parallel Opportunities

- T004, T005 are file-disjoint (style.css / main.js) and can run in parallel after T003
- T007 (main.js) and T008 (new file smoke_us5.md) are file-disjoint and can run in parallel after T005
- T009 (URL verification) and T010 (smoke_us5.md) are file-disjoint and can run in parallel
- T012, T013 are file-disjoint (smoke runs / evidence files) and can run in parallel after T011
- Cross-story parallelism is NOT safe: all stories touch `src/site/index.html` and `src/site/main.js`

---

## Parallel Example: User Story 1

```bash
# After T003 (modal markup in index.html) lands, launch together:
Task: "T004 Add the modal layout to src/site/style.css"
Task: "T005 Implement the story-modal module in src/site/main.js"
# Then the approval gate:
Task: "T006 Submit the final story wording for user approval"
```

## Parallel Example: User Story 2

```bash
# After T005 (show/dismiss wiring in main.js) lands, launch together:
Task: "T007 Implement dismissal persistence in src/site/main.js"
Task: "T008 Create tests/frontend/smoke_us5.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (baseline green)
3. Complete Phase 3: User Story 1 (modal markup → CSS/JS in parallel → wording approval)
4. **STOP and VALIDATE**: quickstart Scenarios 1, 2, 5, 6 + `make commit-slice` (wording approved first)
5. Deploy/demo if ready — the first-visit story alone delivers the feature

### Incremental Delivery

1. Setup + Foundational → baseline established
2. User Story 1 → modal appears with the complete story → wording approval → commit slice (MVP!)
3. User Story 2 → dismissal persists, storage-blocked fallback works → commit slice
4. User Story 3 → both references verified and pinned in the checklist → commit slice
5. Polish: quickstart 1–9 end-to-end, all five smoke checklists, `validation/first-visit-story/` evidence → `make commit-milestone`
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Within each story, the [P]-marked tasks are split across developers
3. Stories themselves are sequenced (shared files): US1 → US2 → US3
4. Stories complete and integrate in order; the user's wording approval (T006) is required before the milestone commit

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable (its checkpoint)
- `tests/frontend/smoke_us5.md` and `validation/first-visit-story/` are implementation-phase artifacts per plan.md — they are created and filled by tasks T008 and T013, not assumed to pre-exist
- The story copy in `specs/007-first-visit-story/contracts/story-content.md` is normative for content (required elements, link targets, facts); the implemented wording in `src/site/index.html` requires the user's final approval before merge (spec clarification, FR-015) — T006
- No new static asset: modal markup ships inside `src/site/index.html` (STATIC_FILES in `src/pipeline/publish.py`); `attribution.html` carries neither markup nor `main.js` (FR-012)
- The map data, style, palette, layers, popup, Bäume toggle, Helligkeit slider, and zoom controls are untouched (FR-014) — the modal module in `main.js` calls no MapLibre API
- The 004 overlap-matrix technique is extended with the open modal rect (`#story-dialog`) — same console script, one more element (quickstart Scenario 6; `contracts/story-modal.md` verification section)
- Avoid: vague tasks, same-file parallel work, cross-story dependencies that break slice independence
- Commit after each task or logical group (OR-004, `make commit-slice` / `make commit-milestone`)
