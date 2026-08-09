---
description: "Task list for Ko-fi Donation Button feature implementation"
---

Tasks: Ko-fi Donation Button

**Input**: Design documents `/specs/017-ko-fi-button/`
**Prerequisites**: plan.md (required), spec.md (required user stories), research.md (decisions R-1…R-9), data-model.md (entities), contracts/ (ko-fi-button.md, csp-image-host.md), quickstart.md (validation Q1–Q9)
**Tests**: tests are explicitly requested — the spec's SC-002 (automated click test, 100 % success), the contracts' "Machine checks (acceptance test)" sections, and plan.md's Testing section all mandate `tests/acceptance/test_ko_fi.py`. Write it FIRST, expect FAIL before implementation.
**Organization**: Tasks grouped by user story (US1…US4 from spec.md) for independent implementation and testing.
**Repository**: flat project at repo root — `src/site/` (static frontend), `workers/map/` (Cloudflare Worker), `tests/`, `scripts/`, `specs/`. No new packages, no manifest change, no new static files (research R-1, R-4).

## Format: `- [ ] [ID] [P?] [Story] Description with file path`

- **[P]**: run in parallel (different files, no dependencies)
- **[Story]**: user story task belongs to (US1…US4)
- Include file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and branch baseline.

- [ ] T001 Create and switch to feature branch `017-ko-fi-button` (repo is currently on `016-seo-improvement`; verify branch does not exist yet, then `git checkout -b 017-ko-fi-button`)
- [ ] T002 [P] Verify prerequisites per quickstart.md: `git`, `bash`, `python3.11`, `.venv` with dev extras (`make bootstrap`), `node`, Chromium at `CHROME_PATH` (default `/usr/bin/chromium`) — run `make check-prereqs` if available; record any gaps before implementation starts

**Checkpoint**: Branch created, toolchain verified — proceed to foundational work.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before ANY user story is implemented.

- [ ] T003 ⚠️ Apply the CSP image-host extension in lockstep across all three policy carriers — `img-src` gains exactly one origin (`https://storage.ko-fi.com`), every other directive stays byte-identical (contract: csp-image-host.md, FR-009, research R-2):

- `<meta http-equiv="Content-Security-Policy">` in `src/site/index.html` (line 6; source truth)
- `SECURITY_HEADERS["Content-Security-Policy"]` string in `workers/map/index.js` (line 44; must stay byte-identical to the meta tag)
- policy text block in `specs/015-security-audit-housekeeping/contracts/security-headers.md` (committed contract — policy changes are contract changes)

New `img-src` value: `img-src 'self' data: https://sgx.geodatenzentrum.de https://storage.ko-fi.com;`. `script-src`/`style-src`/`connect-src`/`worker-src`/`font-src`/`default-src` MUST stay byte-identical. Commit as ONE commit (contract lockstep rule). Do NOT add preconnect/preload hints, and do NOT touch the Ko-fi widget script.

**Checkpoint**: Foundation ready — `grep` all three carriers to confirm the identical policy string; user story implementation can now begin.

---

## Phase 3: User Story 1 — Desktop Visitors Find & Use Donation Button (Priority: P1) 🎯 MVP

**Goal**: A desktop visitor (≥ 768 px) sees a clearly identifiable Ko-fi donation button in the surface panel header (expanded and collapsed states) and can click it to open the owner's Ko-fi page in a new tab without leaving the map.

**Independent Test**: Load the published page at a desktop viewport (≥ 768 px), assert the button is visible in the header without scrolling, click it, assert a new tab opens `https://ko-fi.com/M4Q624RYOV` while the map page stays open (quickstart Q1/Q2; `node scripts/smoke-verify.mjs <url>` ko-fi scenario).

### Tests User Story 1 (REQUIRED by contract — write FIRST, FAIL before implementation)

⚠️ **NOTE: Write tests FIRST, FAIL before implementation**

- [ ] T004 [P] [US1] Write acceptance test module `tests/acceptance/test_ko_fi.py` asserting the contract machine checks from contracts/ko-fi-button.md, mirroring `tests/acceptance/test_seo_metadata.py` conventions: anchor `.ko-fi` exists with exact `href="https://ko-fi.com/M4Q624RYOV"`, `target="_blank"`, `rel="noopener"`; `<img>` has exact `src="https://storage.ko-fi.com/cdn/kofi3.png?v=6"`, `width="143"`, `height="36"`, and German alt mentioning "Ko-fi" and a donation/support word; CSP meta `img-src` contains `https://storage.ko-fi.com` while `script-src`/`connect-src`/`style-src` stay byte-identical to the locked values; Worker header CSP byte-identical to the meta; `.ko-fi` participates in the mobile touch-target rule group (44 px min CSS). Run it — markup assertions MUST fail (no `.ko-fi` in the page yet)

### Implementation User Story 1

- [ ] T005 [US1] Add the ko-fi anchor markup as a direct child of `.surface-header` in `src/site/index.html` (after `.surface-tools` closing tag, before `#surface-toggle` — DOM order title → tools → ko-fi → toggle so the chevron stays rightmost, research R-4): `<a class="ko-fi" href="https://ko-fi.com/M4Q624RYOV" target="_blank" rel="noopener"><img src="https://storage.ko-fi.com/cdn/kofi3.png?v=6" width="143" height="36" alt="Baumfläche auf Ko-fi unterstützen"></a>`. Exact attributes per data-model.md DonationLink/DonationButton — no `onerror`, no inline `style`, no extra attributes (FR-008, research R-5/R-6/R-8/R-9)
- [ ] T006 [P] [US1] Add desktop `.ko-fi` styles in `src/site/style.css` (non-media-query base rules): inline-flex link with the brand image rendered at natural size, `width: 143px; height: 36px` on the image, subtle vertical alignment to sit with header tools. Additive `.ko-fi` rules ONLY — do not modify any rule owned by features 012/014 (contract regression constraints)
- [ ] T007 [P] [US1] Add the ko-fi scenario to `scripts/smoke-verify.mjs`: load page, assert `.ko-fi` anchor is visible in the header (desktop viewport), click it, assert a new tab opens with the EXACT URL `https://ko-fi.com/M4Q624RYOV`, assert the map page is still open and interactive in the original tab
- [ ] T008 [P] [US1] Create manual smoke checklist `tests/frontend/smoke_ko_fi.md` covering US1–US4 checks plus the spec edge cases (CSP-blocked image, 36 px image vs 44 px touch target, 320 px header packing, safe-area insets, external-link safety, Ko-fi unavailability, language consistency) as a browser checklist

**Checkpoint**: `pytest tests/acceptance/test_ko_fi.py -q` green for markup/CSP/desktop-style assertions (touch-target assertions may still be red — they land in US2); `node scripts/smoke-verify.mjs <url>` ko-fi scenario passes at 768/1280/1920 px; manual quickstart Q1/Q2 pass. User Story 1 fully functional and testable independently — commit this slice (OR-004).

---

## Phase 4: User Story 2 — Mobile Visitors Find & Use Donation Button (Priority: P1)

**Goal**: A mobile visitor (< 768 px) sees the same button in the collapsed bottom-sheet header; its touch target is ≥ 44 × 44 px with ≥ 8 px spacing, the map stays dominant (≥ 80 % viewport height), and the button never overlaps or intercepts any existing control at widths ≥ 320 px.

**Independent Test**: Load the published page at a mobile viewport (e.g. 375 × 812), sheet collapsed — button visible in header, map ≥ 80 % viewport; inspect the button's computed box (`getBoundingClientRect()` ≥ 44 × 44); tapping opens Ko-fi in a new tab and the map still pans/zooms (quickstart Q3/Q4).

### Implementation User Story 2

- [ ] T009 [US2] Join `.ko-fi` to the existing feature-012 mobile touch-target rule group in `src/site/style.css` mobile block (the `#baeume, .surface-toggle, .brightness input[type=range]` → `min-width: 44px; min-height: 44px` group, ~line 478-487): add `.ko-fi` as a member so the hit area is ≥ 44 × 44 px while the 36 px-tall image visual is preserved via vertical padding (research R-3). Spacing ≥ 8 px comes from the existing flex `gap: 8px` — verify, do not add new gap rules. Nothing else in the mobile media query changes (contract regression constraints)
- [ ] T010 [US2] Add the ≤ 350 px header packing rules in `src/site/style.css` mobile block per research R-4: `order` overrides so row 1 is `[title, ko-fi, toggle]` and row 2 is `[tools]` (measured fit 295 ≤ 296 px at 320 px), keeping the header at ≤ 2 rows with no horizontal overflow; if browser measurement at 320 × 568 shows the collapsed header exceeds 20 % viewport height (≤ 113 px), the ≤ 350 px image-height fallback (32-34 px, hit area unchanged) MAY be applied per contracts/ko-fi-button.md

**Checkpoint**: quickstart Q3/Q4/Q5/Q8 pass — collapsed header ≤ 20 % viewport (map ≥ 80 %), touch target ≥ 44 × 44, ≥ 8 px spacing, no-overlap matrix empty at 320/375/768 px in both surface states, no horizontal overflow, safe-area content never clipped, clean resize across the 768 px breakpoint. User Story 2 independently testable — commit this slice.

---

## Phase 5: User Story 3 — Button Renders & Is Accessible (Priority: P2)

**Goal**: The button image renders correctly in the published bundle (never blocked, broken, or blank under the extended CSP), carries a German text alternative identifying it as a donation/support link, is reachable and operable by keyboard alone, and shows a visible focus indicator.

**Independent Test**: Load the published page, confirm the button image renders (no broken-image state, zero CSP violations in the console), inspect the accessible name, operate it keyboard-only (Tab to focus, Enter to activate, visible focus indicator) — quickstart Q6/Q7.

### Implementation User Story 3

- [ ] T011 [US3] Add `:focus-visible` and hover/active feedback styles for `.ko-fi` in `src/site/style.css` matching the existing control pattern (`.surface-toggle` uses `outline: 2px solid var(--subtle)`; research R-3/data-model states) so the button shows a visible focus indicator consistent with the rest of the header. CSS-only, no script
- [ ] T012 [US3] Run quickstart Q6–Q7 end to end and fix any failures: `pytest tests/acceptance/test_ko_fi.py -q -k csp` green (img-src extension present, locked directives byte-identical, Worker header CSP byte-identical to meta); browser console shows zero CSP violations and the Ko-fi image renders (no broken/blank state); Tab reaches the button with a visible focus indicator; Enter opens Ko-fi in a new tab; accessible name identifies a donation/support link in German ("Baumfläche auf Ko-fi unterstützen")

**Checkpoint**: quickstart Q6/Q7 pass; the full `test_ko_fi.py` module is now green (touch-target assertions from US2 included). User Story 3 independently testable — commit this slice.

---

## Phase 6: User Story 4 — Nothing Regresses (Priority: P2)

**Goal**: The maintainer ships the button knowing the map experience, layout invariants, security posture, and performance budgets are unchanged — the button is purely additive.

**Independent Test**: Full test suite green; all governance gates pass (layout/overlap gate, commit checks, public-hygiene checks); interaction-latency budgets hold; visual parity with the previous bundle — quickstart Q9.

### Implementation User Story 4

- [ ] T013 [P] [US4] Run governance gates and fix any failures: `make check-public && make check-layout && make check-or005 && make check-history` (quickstart Q9)
- [ ] T014 [P] [US4] Run the full pytest suite `.venv/bin/python -m pytest tests/ -q` — every pre-existing test passes alongside `test_ko_fi.py` (the CSP extension breaks no pinned assertion; research R-2)
- [ ] T015 [P] [US4] Run the perf harness `bash scripts/perf-measure.sh <url>` and verify budgets hold: 8 interactions ≤ 2 s, desktop interaction median ≤ 123 ms, first usable ≤ 10 s (feature 014 SC-008 budgets)
- [ ] T016 [P] [US4] Run visual parity `node scripts/parity-render.mjs --archive dist/buildings.pmtiles --out /tmp/parity-017` — building values, colors, labels, popups identical to the previous bundle
- [ ] T017 [US4] Run quickstart Q9 end to end, including the feature-015 live-map verification (S6) that csp-image-host.md requires before deploy, and manually exercise every control (map pan/zoom, Bäume toggle, brightness slider, surface toggle, popups, attribution, Impressum link, legend) — all behave exactly as before; the button is purely additive

**Checkpoint**: All gates green, budgets hold, parity identical, full suite passes. User Story 4 complete — commit this slice.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the whole feature.

- [ ] T018 [P] Add the release-log entry for the ko-fi button feature in `CHANGELOG.md` (feature number 017, summary of the change, CSP note)
- [ ] T019 Make the final commit(s) per OR-004 (one commit per accepted slice; implementation lands in slice commits), verify the worktree is clean and the branch `017-ko-fi-button` contains the full feature: markup, styles, CSP lockstep, acceptance test, smoke checklist, smoke-verify scenario, CHANGELOG entry

**Checkpoint**: Feature complete, committed, clean tree.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories (the button image cannot render until `img-src` allows `https://storage.ko-fi.com`)
- **User Stories (Phase 3+)**: depend on Foundational completion; proceed sequentially in priority order (US1 → US2 → US3 → US4) because the stories edit the same files (`src/site/index.html`, `src/site/style.css`)
- **Polish (Final Phase)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: starts after Foundational — no dependencies on other stories
- **User Story 2 (P1)**: requires US1 (the `.ko-fi` class and base styles must exist before mobile rules join the same `style.css` blocks)
- **User Story 3 (P2)**: requires US1/US2 (alt text and touch-target rules land there; US3 adds focus styles and verifies rendering/accessibility)
- **User Story 4 (P2)**: requires US1–US3 complete (regression validation covers the whole change)

### Within Each User Story

- Tests (US1: REQUIRED) MUST be written to FAIL before implementation
- Markup before styles; styles before verification
- Story complete before moving to the next priority

### Parallel Opportunities

- **Phase 1**: T002 runs parallel with T001
- **Phase 3**: T004, T006, T007, T008 run in parallel (different files: `tests/`, `src/site/style.css`, `scripts/`, `tests/frontend/`); T005 lands after T004 per test-first
- **Phase 4**: T009 and T010 are sequential (same file `src/site/style.css`)
- **Phase 6**: T013, T014, T015, T016 run in parallel (independent command suites); T017 after them
- **Phase 7**: T018 parallel with final review; T019 last

---

## Parallel Example: User Story 1

```bash
# Launch the write-first test, desktop styles, smoke scenario, and checklist together:
# Task: "Write acceptance test module tests/acceptance/test_ko_fi.py"
# Task: "Add desktop .ko-fi styles in src/site/style.css"
# Task: "Add ko-fi scenario to scripts/smoke-verify.mjs"
# Task: "Create manual smoke checklist tests/frontend/smoke_ko_fi.md"
# Then, once the test asserts failure:
# Task: "Add ko-fi anchor markup in src/site/index.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (branch + prerequisites)
2. Complete Phase 2: Foundational (CSP lockstep — CRITICAL, blocks all stories)
3. Complete Phase 3: User Story 1 (desktop markup, styles, smoke scenario, acceptance test)
4. **STOP VALIDATE**: quickstart Q1/Q2 + smoke-verify ko-fi scenario
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently (desktop) → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently (mobile touch target, 320 px floor, no-overlap matrix) → Deploy/Demo
4. Add User Story 3 → Test independently (rendering, keyboard, focus) → Deploy/Demo
5. Add User Story 4 → Full gates, perf, parity → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Once Foundational done: US1 phase tasks fan out (test/styles/smoke/checklist in parallel); US2/US3 follow sequentially on the same files
3. US4 gate runs fan out across the team (pytest / gates / perf / parity in parallel)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps the task to its user story for traceability
- The CSP lockstep (T003) is a single atomic commit — never split across three commits (contract: csp-image-host.md)
- Commit each logical slice (OR-004); stop at every checkpoint and validate the story independently
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence
- All file paths are repo-relative; `src/`, `tests/`, `scripts/`, `workers/` live at the repository root
