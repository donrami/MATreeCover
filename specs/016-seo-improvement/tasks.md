# Tasks: SEO Assessment & Improvement (feature 016)

**Input**: Design documents `/specs/016-seo-improvement/`
**Prerequisites**: plan.md (required), spec.md (required user stories), research.md, data-model.md, contracts/, quickstart.md
**Tests**: Tests are plan-mandated deliverables, not optional. `tests/acceptance/test_seo_metadata.py` is listed in plan.md, and the contracts require every machine-checkable rule to be enforced by a committed acceptance test ("never by documentation alone"). Write each story's test task FIRST, before its implementation.
**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: run in parallel (different files, no dependencies)
- **[Story]**: user story the task belongs to (US1–US5)
- Include file paths in descriptions

## Path Conventions

- Static frontend: `src/site/` (HTML/CSS/JS, no build tool)
- Python pipeline: `src/pipeline/` (publish.py)
- Tests: `tests/acceptance/`, `tests/frontend/`
- Tooling: `scripts/` (parity-render.mjs, smoke-verify.mjs, gates)
- Evidence: `verification/`
- Worker: `workers/map/index.js` (NO change in this feature)
- No new top-level directories, no new dependencies (plan structure decision; `check-layout` manifest unchanged)

## Phase 1: Setup

**Purpose**: Project readiness; verify environment and baseline build

- [X] T001 Verify branch `016-seo-improvement` and clean worktree (`git branch --show-current`, `git status --porcelain`)
- [X] T002 [P] Bootstrap dev environment (`make bootstrap`); confirm `.venv/bin/python -m pytest`, `node`, `curl` available
- [X] T003 Confirm baseline publish works: `make publish` succeeds, `dist/` populated (pre-change state)

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Capture pre-change evidence BEFORE any source change; create the committed assessment report skeleton (FR-001)

- [X] T004 Capture pre-change evidence and create `verification/seo-assessment-2026-08-09.md`: fetch raw HTML of `https://abu-hamad.de/map/`, `/map/impressum`, `/map/attribution`; record title, meta description, canonical, OG tags, JSON-LD, visible text per page; note missing `robots.txt`/`sitemap.xml` (404 today); record gate status. Write the Current state section with fetch date 2026-08-09. MUST run before any `src/` change.

**Checkpoint**: Foundation ready — user story implementation can begin. US1/US2 are P1; US3–US5 are P2.

## Phase 3: User Story 1 — Search Engines Understand Map Page (Priority: P1) 🎯 MVP

**Goal**: Every page carries descriptive German metadata (map title 30–60 chars, meta description 100–160 chars, canonical tag); the map page's informative text is visible in raw HTML without JavaScript (FR-002/003/004/006).
**Independent Test**: Fetch raw HTML of all three pages; assert title/description/canonical per page, ≥ 80 % informative words outside hidden containers, story copy exactly once (quickstart Q1/Q4).

### Tests User Story 1 (plan-mandated)

- [X] T005 [P] [US1] Create `tests/acceptance/test_seo_metadata.py` with metadata + visible-content assertions: single title 30–60 chars (never bare "Baumfläche"), single meta description 100–160 chars, canonical tag per page matching its canonical URL, pairwise-distinct descriptions; visible section outside hidden containers, ≥ 80 % informative words visible, distinctive story phrase occurs exactly once, no "the map above" reference. Write FIRST — fail before implementation.

### Implementation User Story 1

- [X] T006 [US1] Add descriptive German title (30–60 chars), meta description (100–160 chars), `<link rel="canonical" href="https://abu-hamad.de/map/">` to `src/site/index.html`
- [X] T007 [P] [US1] Add unique German meta description (100–160 chars) and canonical `https://abu-hamad.de/map/impressum` to `src/site/impressum.html` (title "Impressum – Mannheim Baumfläche" kept, FR-003)
- [X] T008 [P] [US1] Add unique German meta description (100–160 chars) and canonical `https://abu-hamad.de/map/attribution` to `src/site/attribution.html` (title "Datenquellen – Mannheim Baumfläche" kept, FR-003)
- [X] T009 [US1] Add visible informative `<section>` to `src/site/index.html` (story incl. SPIEGEL context / CityTreeCover / GitHub link, method 60-m radius + 30 % guideline, data sources DOP20/GDI-MA, accuracy disclaimer): visible in initial HTML, self-contained, single DOM copy
- [X] T010 [US1] Update story modal in `src/site/main.js`: opens and scrolls to the visible section; remove the modal's hidden story copy; dismiss persistence unchanged (feature 007, Clarifications 2026-08-09)
- [X] T011 [US1] Update `tests/frontend/smoke_us5.md` to the new modal interaction (modal opens/scrolls to visible section; dismiss → no modal next visit)
- [X] T012 [US1] Verify: `make publish`; `pytest tests/acceptance/test_seo_metadata.py -q -k "metadata or visible"` green; raw `dist/index.html` self-sufficient for non-JS crawlers (quickstart Q4)

**Checkpoint**: User Story 1 fully functional and testable independently.

## Phase 4: User Story 2 — Link Previews Render Everywhere (Priority: P1)

**Goal**: Full Open Graph + Twitter Card set on the map page with a committed 1200×630 preview image that visually matches the current map (FR-005).
**Independent Test**: Inspect raw HTML for all ten OG/Twitter properties; fetch `og:image` URL → 200, PNG, 1200×630, < 1 MB (quickstart Q2).

### Tests User Story 2 (plan-mandated)

- [X] T013 [P] [US2] Add link-preview assertions to `tests/acceptance/test_seo_metadata.py`: all ten properties present with correct values (`og:locale=de_DE`, `og:type=website`, `og:url` = canonical, `og:image:width/height` = 1200/630, `twitter:card=summary_large_image`, exactly one `og:*` per property); `og:image` filename exists in `dist/`, PNG/JPG, exactly 1200×630 px, under 1 MB. Write FIRST — fail before implementation.

### Implementation User Story 2

- [X] T014 [US2] Add og:image export mode (1200×630 viewport render) to `scripts/parity-render.mjs` (reuse existing parity pipeline; no new dependencies)
- [X] T015 [US2] Generate `src/site/og-image.png` via the new export mode from the current map rendering: PNG 1200×630, < 1 MB; verify it visually matches the current map (no stale or wrong city); commit the asset (research D9)
- [X] T016 [P] [US2] Add full OG + Twitter Card tags to `<head>` of `src/site/index.html` (`og:title`, `og:description`, `og:type=website`, `og:url`, `og:site_name`, `og:locale=de_DE`, `og:image`, `og:image:width`, `og:image:height`, `twitter:card=summary_large_image`); absolute image URL
- [X] T017 [US2] Add `og-image.png` to `STATIC_FILES` in `src/pipeline/publish.py` (unhashed; hashed-bundle contract untouched)
- [X] T018 [US2] Verify: `make publish`; `pytest tests/acceptance/test_seo_metadata.py -q -k og` green; `file dist/og-image.png` shows 1200×630 PNG under 1 MB

**Checkpoint**: User Story 2 fully functional and testable independently.

## Phase 5: User Story 3 — Crawlers & AI Bots Told What to Fetch (Priority: P2)

**Goal**: `/map/robots.txt` disallows the three data files for all user agents; `/map/sitemap.xml` lists exactly the three canonical URLs; root-domain coordination documented (FR-008/009/010).
**Independent Test**: Fetch both files: robots 200 `text/plain` with exactly three data-file disallows and no HTML disallow; sitemap 200 XML with exactly three canonical URLs and no `lastmod` (quickstart Q3).

### Tests User Story 3 (plan-mandated)

- [X] T019 [P] [US3] Add crawler-file assertions to `tests/acceptance/test_seo_metadata.py`: `dist/robots.txt` has `User-agent: *` and exactly the three data-file `Disallow:` lines, no `Disallow:` matching any HTML path; `dist/sitemap.xml` parses to exactly 3 `<loc>` values equal to the canonical URLs, no `<lastmod>`, no data files / hashed assets / `og-image`. Write FIRST — fail before implementation.

### Implementation User Story 3

- [X] T020 [P] [US3] Create `src/site/robots.txt`: `User-agent: *`; `Disallow: /buildings.pmtiles`, `/trees.pmtiles`, `/buildings.geojson`; optional informational `Sitemap:` line; no HTML disallow; zone-level AI-bot policy NOT duplicated (research D5)
- [X] T021 [P] [US3] Create `src/site/sitemap.xml`: exactly `https://abu-hamad.de/map/`, `https://abu-hamad.de/map/impressum`, `https://abu-hamad.de/map/attribution`; no `lastmod` (staleness edge case)
- [X] T022 [US3] Add `robots.txt` + `sitemap.xml` to `STATIC_FILES` in `src/pipeline/publish.py` (unhashed; Worker serves from assets binding — no Worker code change)
- [X] T023 [US3] Verify: `make publish`; `pytest tests/acceptance/test_seo_metadata.py -q -k robots` green; both files in `dist/` with correct content types

**Checkpoint**: User Story 3 fully functional and testable independently.

## Phase 6: User Story 4 — Nothing Regresses (Priority: P2)

**Goal**: All existing tests, governance gates, performance budgets, and the map experience stay green/identical (FR-012/013).
**Independent Test**: Full pytest suite, governance gates, interaction-latency harness, parity comparison (quickstart Q7).

- [X] T024 [P] [US4] Run full suite `pytest tests/ -q` — every existing test passes
- [X] T025 [P] [US4] Run governance gates `make check-public`, `make check-layout`, `make check-or005` — all green; no new large tracked files (OR-005)
- [X] T026 [P] [US4] Run interaction-latency harness `scripts/perf-measure.sh` — all 8 interactions ≤ 2 s, desktop interaction median ≤ 123 ms, first usable ≤ 10 s
- [X] T027 [P] [US4] Run parity comparison `node scripts/parity-render.mjs --archive dist/buildings.pmtiles --out /tmp/parity-016` — building values, colors, labels, popups identical to previous bundle; `og-image.png` visually matches current render
- [X] T028 [P] [US4] Verify CSP meta tag and security headers byte-identical (`git diff`); hashed-bundle contract unchanged (only `main.js`/`style.css`/`style.json`/`vendor/*` hashed); no Worker code change

**Checkpoint**: User Story 4 green — zero regressions.

## Phase 7: User Story 5 — Assessment Reproducible & Committed (Priority: P2)

**Goal**: The committed report documents before/after state, every finding with severity + disposition, research sources, and reproducible verification (FR-001/011).
**Independent Test**: Open `verification/seo-assessment-2026-08-09.md`; re-run every check in its Verification section; stated results reproduce (quickstart Q8).

- [X] T029 [US5] Complete `verification/seo-assessment-2026-08-09.md`: post-change evidence (fetched HTML, og-image, robots, sitemap, JSON-LD); findings table with severity (high/medium/low) and disposition (`fixed` / `documented` / `owner-side`) for every finding; research summary R-001…R-009 + decisions D1–D10 + source list; root-coordination lines (exact `Sitemap:` line, optional data-file disallows, Cloudflare 120-min `robots.txt` purge note) marked owner-side; tradeoffs (AI-bot citation effect); measurement (server-side only)
- [X] T030 [US5] Verify report reproducibility: run every check listed in the report's Verification section (fetch page, inspect head, validate sitemap, validate structured data, og:image checks) — each stated result reproduces (SC-001)
- [X] T031 [US5] Document server-side property verification (Search Console + Bing Webmaster via DNS record or file upload, zero client-side tracking) as owner steps in the report's Measurement section (FR-011/SC-009)

**Checkpoint**: User Story 5 complete — audit trail reproducible.

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Changelog, full validation, commit discipline

- [X] T032 [P] Add feature 016 entry to `CHANGELOG.md`
- [X] T033 Run quickstart.md validation Q1–Q8 end to end; record results
- [X] T034 Commit the implementation slice per OR-004 (one commit per accepted slice; plan already committed via `make commit-plan`)
- [X] T035 Final gate pass on the committed tree: pytest, `check-public`, `check-layout`, `check-or005`

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately
- **Foundational (Phase 2)**: depends on Setup — BLOCKS all user stories (T004 captures pre-change evidence and MUST precede any `src/` edit)
- **User Stories (Phase 3+)**: depend on Foundational. US1/US2 (P1) first, US3–US5 (P2) after
- **Polish (Final Phase)**: depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: no story dependencies. MVP.
- **User Story 2 (P1)**: no story dependencies. T017 edits `src/pipeline/publish.py`; US3's T022 adds two more `STATIC_FILES` entries as a separate additive edit.
- **User Story 3 (P2)**: no story dependencies.
- **User Story 4 (P2)**: after US1–US3 — its regression evidence covers the changed tree.
- **User Story 5 (P2)**: after US1–US3 (report needs the after-state); US4 results feed the report's verification section.

### Within Each User Story

- Tests (plan-mandated) written FIRST, failing before implementation
- Implementation before verification
- Story complete before moving to the next priority

### Parallel Opportunities

- **Setup**: T002 parallel with T001; T003 after T002
- **US1**: T005 (test) parallel with implementation; T007 and T008 parallel (different files); T006 → T009 sequential (same file `index.html`); T010 after T009; T011 after T010; T012 last
- **US2**: T013 (test) parallel; T014 → T015 (image pipeline → asset); T016 parallel with T015; T017 after T015; T018 last
- **US3**: T019 (test) parallel; T020 and T021 parallel (different files); T022 after both; T023 last
- **US4**: T024–T028 all parallel (different scripts/files)
- **US5**: T029 → T030 → T031 sequential (same file)
- **Polish**: T032 parallel with T033; T034 after both; T035 last

## Parallel Example: User Story 1

```bash
# Launch tests + independent page edits together:
Task: "Create tests/acceptance/test_seo_metadata.py with metadata + visible-content assertions"
Task: "Add meta description + canonical to src/site/impressum.html"
Task: "Add meta description + canonical to src/site/attribution.html"
```

## Parallel Example: User Story 2

```bash
# Launch tests + image + tags together:
Task: "Add link-preview assertions to tests/acceptance/test_seo_metadata.py"
Task: "Generate src/site/og-image.png via scripts/parity-render.mjs export mode"
Task: "Add full OG + Twitter Card tags to src/site/index.html"
```

## Parallel Example: User Story 3

```bash
# Launch tests + both crawler files together:
Task: "Add crawler-file assertions to tests/acceptance/test_seo_metadata.py"
Task: "Create src/site/robots.txt"
Task: "Create src/site/sitemap.xml"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (T004 evidence capture — CRITICAL, before any change)
3. Complete Phase 3: User Story 1
4. **STOP VALIDATE**: run quickstart Q1/Q4 + pytest; test US1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → test independently → deploy (MVP: search-engine presence)
3. Add US2 → test independently → deploy (link previews; P1)
4. Add US3 → test independently → deploy (crawl budget)
5. US4 regression sweep → US5 report committed
6. Each story adds value without breaking previous stories

### Parallel Team Strategy (multiple developers)

1. Team completes Setup + Foundational together (T004 first)
2. Once Foundational done:
   - Developer A: User Story 1 (metadata + visible section)
   - Developer B: User Story 2 (OG tags + image)
   - Developer C: User Story 3 (crawler files)
3. US1 and US2 BOTH edit `src/site/index.html` — coordinate ownership of that file or run those two stories sequentially
4. Stories complete, then integrate and validate independently

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to a specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing (TDD within each story)
- Commit tasks in logical groups; stop at every checkpoint and validate the story independently
- Avoid: vague tasks, same-file conflicts, cross-story dependencies
- Story text must exist in EXACTLY one DOM location: T010 (removing the modal's hidden copy) is what keeps the single-source rule true (Clarifications 2026-08-09)
- `og:image.png` freshness invariant: any future map-rendering change MUST regenerate and recommit the image in the same change (data-model E4)
