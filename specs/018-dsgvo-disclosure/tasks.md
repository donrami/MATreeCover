---
description: "Tasks for feature 018"
---

# Tasks: DSGVO Disclosure

**Input**: `/specs/018-dsgvo-disclosure/` design documents.
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.
**Tests**: NO new tests.
**Organization**: Each user story ships as an MVP increment.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: parallel-safe. Different files.
- **[Story]**: user story tag (`US1` through `US5`).
- Description names the file path.

## Path Conventions

Single project. Repo root. No new directories.

## Phase 1: Setup

**Purpose**: Confirm worktree and design docs.

- [x] T001 Verify branch `research/dsgvo-cookies-conformity` and clean status. Confirm six spec files exist.

**Checkpoint**: docs present. Worktree clean.

## Phase 2: Foundational

**Purpose**: Lock the template and references. Read-only.

- [x] T002 [P] Read `src/site/impressum.html`. Lock as the byte template.
- [x] T003 [P] Read `src/site/sitemap.xml`. Capture the entry pattern.
- [x] T004 [P] Read `src/site/vendor/PROVENANCE.md`. Capture the MapLibre host.

**Checkpoint**: template locked. US1 can start.

## Phase 3: User Story 1 (Priority: P1) 🎯 MVP

**Goal**: Visitor sees "Datenschutzerklärung" in the footer beside "Impressum". Click takes them to `/datenschutz`. Page has 9 FR-002 blocks. No scripts. No new hosts.

**Independent Test**: `grep -c '<section>' src/site/datenschutz.html` returns 9. Two `class="legal-link"` siblings exist in `index.html`. New sitemap row is present. CSP `<meta>` is byte-identical.

### Implementation for User Story 1

- [x] T005 [P] [US1] Create `src/site/datenschutz.html`. Mirror `impressum.html`. Add 9 `<section>` blocks in FR-002 order. The nine blocks:

  1. Verantwortlicher
  2. Datenschutzbeauftragter
  3. Zwecke und Rechtsgrundlagen
  4. Empfänger und Drittländertransfer
  5. Speicherdauer
  6. Betroffenenrechte
  7. Cookies und localStorage
  8. Keine automatisierten Entscheidungen
  9. Stand (Last update 2026-08-10)

  Covers FR-001, FR-002, FR-003, FR-012, FR-013.

- [x] T006 [US1] Add the new sibling link in `src/site/index.html` after the Impressum link. One whitespace. No wrapper. No dot. No icon. Covers FR-004, FR-005.

- [x] T007 [P] [US1] Add `<url>` row to `src/site/sitemap.xml`. Loc and lastmod set. Covers FR-008.

**Checkpoint**: page live. Footer link visible. Sitemap updated.

## Phase 4: User Story 2 (Priority: P1) 🎯 MVP

**Goal**: Impressum privacy section is one sentence plus a link to the new page. No more "no active collection" claim.

**Independent Test**: `grep -A1 'id="datenschutz"' src/site/impressum.html` shows one sentence. Old paragraph is gone.

### Implementation for User Story 2

- [x] T008 [P] [US2] Replace the Impressum Datenschutz section plus its `<p>` with one new `<p>` in `src/site/impressum.html`. The new text reads "Mehr Informationen zum Datenschutz finden Sie in der Datenschutzerklärung." Link points to `./datenschutz`. Covers FR-007.

**Checkpoint**: Impressum has one sentence.

## Phase 5: User Story 3 (Priority: P2)

**Goal**: Story-modal flow keeps working. TDDDG exemption is documented. No behavior change.

**Independent Test**: `grep -A5 'TDDDG\|§ 25' specs/007-first-visit-story/contracts/dismissal-state.md` shows the paragraph. Dismiss and reload still hides the modal. `localStorage` has one key.

### Implementation for User Story 3

- [x] T009 [P] [US3] Append a 3–5 sentence paragraph to `specs/007-first-visit-story/contracts/dismissal-state.md`. Document the § 25(2) Nr. 2 TDDDG exemption. Cover three points. The write happens only on explicit dismissal. Without the key, dismissal cannot survive reloads. No privacy-friendly alternative exists. The key is strictly necessary. Covers FR-010.

**Checkpoint**: doc-only update. No behavior change.

## Phase 6: User Story 4 (Priority: P2)

**Goal**: Ko-fi link does not leak referrer. The outbound link is honest about being sponsored.

**Independent Test**: `grep 'kofi' src/site/index.html | grep -oE 'rel="[^"]+"'` returns the new `rel`. New tab has `window.opener === null`.

### Implementation for User Story 4

- [x] T010 [US4] Update the Ko-fi anchor's `rel` in `src/site/index.html` to `"noopener noreferrer nofollow sponsored"`. Leave `href`, `target`, `class`, and the `<img>` unchanged. Covers FR-006. Depends on T006.

**Checkpoint**: one attribute changed.

## Phase 7: User Story 5 (Priority: P3)

**Goal**: README does not claim zero egress. It names Cloudflare, BKG, and Ko-fi. It links to the new page.

**Independent Test**: `grep -i 'datenschutz\|datenschutzerklärung' README.md` returns one sentence. No "nothing leaves" claim remains.

### Implementation for User Story 5

- [x] T011 [P] [US5] Replace the README privacy claim with wording that names Cloudflare, BKG, and Ko-fi as HTTP recipients. Link to `https://abu-hamad.de/map/datenschutz`. Covers FR-011.

**Checkpoint**: README updated.

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Run all gates. Prove no drift.

- [x] T012 [P] Run quickstart scenarios S2 through S12. Confirm each check from `quickstart.md`.

- [x] T013 [P] Run `make check-layout`, `make check-public`, `make check-history`, `make check-or005`, and `.venv/bin/python -m pytest tests/ -q`. All green. Covers SC-004.

- [x] T014 [P] Run `bash scripts/deploy-cf.sh verify` if access exists. New route returns 200. Headers match the index. Covers FR-014, SC-006.

- [x] T015 [P] Append a `## 2026-08-10 — DSGVO disclosure (018)` entry to `CHANGELOG.md`. Cover page, Impressum pointer, Ko-fi `rel`, README softening, and TDDDG paragraph.

**Checkpoint**: deployable. Gates green. Manifest updated.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no deps. First.
- **Foundational (Phase 2)**: depends on Phase 1.
- **User Story 1 (Phase 3, P1)**: depends on Phase 2.
- **User Story 2 (Phase 4, P1)**: depends on Phase 2. Different file. Parallel with US1.
- **User Story 3 (Phase 5, P2)**: depends on Phase 2. Doc-only. Parallel with US1.
- **User Story 4 (Phase 6, P2)**: depends on T006. Same file. Runs after US1.
- **User Story 5 (Phase 7, P3)**: depends on Phase 2. Different file. Fully parallel.
- **Polish (Phase 8)**: depends on all stories.

### Within Each User Story

- No tests written (research R10).
- US1: T005 and T007 are different files. They run in parallel. T006 gates US4.
- US2: one file, one task.
- US3: doc-only, one task.
- US4: one attribute. Depends on T006.
- US5: one file, one task.

### Parallel Opportunities

- T002, T003, T004 run in parallel.
- T005 and T007 run in parallel. T006 runs alongside them.
- T008, T009, T011 run in parallel after US1.
- T012, T013, T014, T015 run in parallel.

## Parallel Example: User Story 1

```bash
# Three parallel tasks for US1.
Task: "Create src/site/datenschutz.html with 9 FR-002 blocks."
Task: "Add the new sibling link to src/site/index.html."
Task: "Add the new row to src/site/sitemap.xml."
```

```bash
# US2, US3, US5 in parallel after US1 lands.
Task: "Replace the Impressum Datenschutz section with one sentence."
Task: "Append the TDDDG paragraph to spec 007 dismissal-state.md."
Task: "Soften the README privacy claim and link the new page."
```

```bash
# US4 last. One attribute change.
Task: "Update the Ko-fi rel attribute in src/site/index.html."
```

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Setup.
2. Complete Foundational.
3. Complete US1.
4. Complete US2.
5. **STOP and VALIDATE**. Load `/datenschutz`. Read both legal pages. Run all gates.
6. Deploy. The site is DSGVO-conform on Art. 13.

### Incremental Delivery

1. Setup + Foundational.
2. Add US1. Page reachable.
3. Add US2. Impressum aligned. MVP done.
4. Add US3. TDDDG documented.
5. Add US4. Ko-fi hardened.
6. Add US5. README aligned.
7. Polish. Gates green.

### Suggested Team Allocation

- Engineer A: US1 and US2.
- Engineer B: US3 from Phase 2 onward.
- Engineer C: US4 after US1. US5 in parallel.

## Notes

- [P] tasks touch different files.
- [Story] maps to user story for traceability.
- Each story ends with a Checkpoint.
- No new tests added. Full suite must pass.
- No CSP, header, Worker, pipeline, or storage change beyond listed edits.
- The deploy artifact comes from the existing copy step.
- Avoid: wrappers, dots, new CSS, new scripts, new hosts, new storage keys, or test edits.
