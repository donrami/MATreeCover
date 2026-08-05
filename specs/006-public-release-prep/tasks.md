---
description: "Task list: Public Release Preparation"
---

# Tasks: Public Release Preparation

**Branch**: `006-public-release-prep`

**Input**: Design documents in `specs/006-public-release-prep/`: `plan.md` (required), `spec.md` (required, user stories with priorities), `research.md` (audit + license findings), `data-model.md` (entities), `contracts/` (`readme.md`, `public-hygiene.md`, `license.md`), `quickstart.md` (validation scenarios 1–8).

**Prerequisites**: Git checkout of the repository; `bash`, `git`. Quickstart scenarios 3, 6, 7 need network; scenario 8 needs the Python venv (`.venv`).

**Tests**: Not requested. The spec's success criteria are validated through `quickstart.md` scenarios, not new unit tests. The only test run is the existing pytest suite as a regression guard (quickstart Scenario 8) after the workspace-default changes.

**Organization**: Tasks are grouped by user story so each story is independently implementable and testable. One commit per slice/milestone via `make commit-slice` / `make commit-milestone` (OR-004). The hygiene gate (`make check-public`, contracts/public-hygiene.md) is the FR-010 enforcement instrument for every story.

## Format

- `[ID] [P?] [Story] Description with file path`
- `[P]`: run in parallel (different files, no dependencies on incomplete tasks)
- `[Story]`: user story the task belongs to (US1..US3). Setup, Foundational, and Polish carry no label.

## Path Conventions

- Repo root: `README.md` (rewrite), `DEVELOPMENT.md` (new), `LICENSE` (new), `Makefile` (edit), `.gitignore` (edit).
- Enforcement: `scripts/check-public.sh` (new), `make check-public`.
- Code hygiene: `src/pipeline/workspace.py`, `tests/conftest.py`, `scripts/check-prereqs.sh`, `scripts/runpod-deploy.sh`, `scripts/deploy-cf.sh`, `workers/map/wrangler.toml`.
- In-app credits: `src/site/attribution.html`.
- Provenance docs: `specs/001..005/` (sanitize only; never rewrite git history — spec A-4).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Branch and planning-artifact commit (OR-004).

- [X] T001 Create and switch to branch `006-public-release-prep`
- [X] T002 Commit planning artifacts (spec, plan, research, data-model, contracts/, quickstart) via `make commit-plan MSG="plan: public release preparation"` (OR-004)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The hygiene gate plus all code-level personal-path fixes. These MUST be complete before any user story: the gate is the FR-010 instrument every story must pass, and the workspace changes are what `DEVELOPMENT.md` (US1) documents truthfully.

- [X] T003 Create `scripts/check-public.sh` per `contracts/public-hygiene.md`: scan `git ls-files` for patterns P1–P13; exit 0 with `clean: N tracked files scanned` when no findings, exit 1 with `file:line: match` lines otherwise; no network access; every pattern commented with rationale
- [X] T004 Update `Makefile`: add `check-public` target (runs `scripts/check-public.sh`, in `.PHONY`); change `WORKSPACE ?=` default to relative `data/archive/workspace`; fix stale bootstrap branch guard `refs/heads/001-replicate-mannheim-tree-cover` → `main`
- [X] T005 [P] Change `DEFAULT_WORKSPACE` in `src/pipeline/workspace.py` to a repo-root-relative default (`Path(__file__).resolve().parent.parent.parent / "data/archive/workspace"`), keeping the `MANNHEIM_WORKSPACE` env override (research.md decision 1)
- [X] T006 [P] Change `DEFAULT_WORKSPACE` in `tests/conftest.py` to `REPO_ROOT / "data/archive/workspace"`, keeping the `MANNHEIM_WORKSPACE` env override
- [X] T007 [P] Change the workspace default in `scripts/check-prereqs.sh` to relative `data/archive/workspace` (keep `MANNHEIM_WORKSPACE` override)

**Checkpoint**: Foundation ready. `make check-public` runs and reports the remaining doc-level findings as a known backlog (cleared in US2). Code-level findings are gone.

---

## Phase 3: User Story 1 - A Visitor Understands the Map (Priority: P1) 🎯 MVP

**Goal**: A user-focused English `README.md` that explains what the map is, links the live map at `https://abu-hamad.de/map/`, explains how to read it, credits the reference project and data sources, states the MIT license backed by a `LICENSE` file, and points developers to `DEVELOPMENT.md`.

**Independent Test**: Quickstart scenarios 2, 4, 5, 6 pass; a first-time visitor can state what the map shows and how to read a building's color from the README alone (SC-001, SC-002, SC-004, SC-005, SC-006).

### Implementation User Story 1

- [X] T008 [P] [US1] Create `LICENSE` per `contracts/license.md` §1: standard MIT text, project copyright `Copyright (c) 2026 donrami` (confirm exact holder at commit time), preserved CityTreeCover notice (`Copyright (c) 2026 Jakob Schultz` + MIT permission text)
- [X] T009 [P] [US1] Rewrite `README.md` per `contracts/readme.md`: English, required structure (one-line pitch, live map link `https://abu-hamad.de/map/`, what-the-map-shows, how-to-read + tree toggle, data/methodology, credits per `contracts/license.md` §2–3, license section linking `./LICENSE`, developer link to `DEVELOPMENT.md`); no commands, code blocks, exit codes, or internal workflow references (FR-001..006, 008, 012)
- [X] T010 [US1] Create `DEVELOPMENT.md` (FR-009): migrate the dev content from the current README (prerequisites via `MANNHEIM_WORKSPACE`, setup, pipeline subcommands, publish/hosting, RunPod inference, tests, governance OR-004/005, vendored libraries) sanitized per FR-010 — no personal paths, no harness-internal workflow references
- [X] T011 [US1] Verify README against `contracts/readme.md` "Verification": `grep -F "https://abu-hamad.de/map/" README.md` matches; no fenced code blocks or `$ `/`make `/`python -m`/`bash `/`npx ` line starts in the README; license statement matches `LICENSE`; CityTreeCover and `dl-de/by-2-0` present

**Checkpoint**: US1 complete — README is self-contained for a visitor; quickstart scenarios 2, 4, 5, 6 pass.

---

## Phase 4: User Story 2 - The Owner Publishes the Repository Safely (Priority: P2)

**Goal**: Every tracked file is free of personal data (FR-010): specs/ paths sanitized, owner ops redacted, `zone_id` and RunPod defaults neutralized, internal harness references removed — verified by `make check-public` exiting 0.

**Independent Test**: Quickstart scenario 1 — `make check-public` exits 0 with `clean` (SC-003).

### Implementation User Story 2

- [X] T012 [P] [US2] Sanitize personal paths in `specs/001-replicate-mannheim-tree-cover/`: replace every absolute personal workspace path with the relative `data/archive/workspace` (or `MANNHEIM_WORKSPACE` wording) (files: spec.md, plan.md, quickstart.md, research.md, tasks.md)
- [X] T013 [P] [US2] Replace absolute input-spec path in `specs/002-fix-building-popup/plan.md` with a relative `specs/…/spec.md` reference
- [X] T014 [P] [US2] Remove harness-internal workflow references from all `specs/001..005` plan.md and `checklists/requirements.md` files and from 006's own planning docs, replacing with neutral wording
- [X] T015 [P] [US2] Redact owner ops details in `specs/005-host-on-personal-domain/` per `contracts/public-hygiene.md` manual item 1: hosting IPs (`191.96.56.91`, `2a02:4780:...`), DNS/MX/CNAME records, registrar names → placeholders; keep architecture and decisions
- [X] T016 [P] [US2] Replace real `zone_id` in `workers/map/wrangler.toml` with `<your-zone-id>` placeholder; add `workers/map/wrangler.local.toml` to `.gitignore`; document the `--config` local override in `DEVELOPMENT.md`
- [X] T017 [P] [US2] Parameterize owner-infra gates in `scripts/deploy-cf.sh` per `contracts/public-hygiene.md` manual item 2: apex/www host, MX/CNAME checks, blog HTTPS check behind variables with neutral defaults
- [X] T018 [P] [US2] Replace SSH key/port defaults in `scripts/runpod-deploy.sh` with env-var placeholders (`SSH_KEY`, port passed as argument), keeping the `MANNHEIM_WORKSPACE`-relative default
- [X] T019 [US2] Run `make check-public` and fix every remaining finding (including US1 outputs) until exit 0 with `clean` (SC-003, quickstart scenario 1)

**Checkpoint**: US2 complete — the gate is clean; the repository is publishable from a data-hygiene standpoint.

---

## Phase 5: User Story 3 - The Reference Project Author Finds Credit (Priority: P3)

**Goal**: Credits are consistent between the README and the in-app attribution panel; the basemap.de credit uses the official string; no regressions in the app or the test suite.

**Independent Test**: Quickstart scenarios 7 and 8 — attribution panel renders all providers (SC-007) and the pytest suite stays green.

### Implementation User Story 3

- [X] T020 [US3] Align `src/site/attribution.html` per `contracts/license.md` §4: replace bare `basemap.de` entry with `© GeoBasis-DE / BKG (Jahr des letzten Datenbezugs) dl-de/by-2-0` linked to `govdata.de/dl-de/by-2-0`; keep LGL and CityTreeCover lines unchanged; keep the panel German
- [X] T021 [US3] Run the regression suite: `.venv/bin/python -m pytest tests/ -q` — green, or workspace-dependent skips only (quickstart scenario 8)
- [X] T022 [US3] Verify attribution renders: open `https://abu-hamad.de/map/` (or local `dist/`), open the attribution panel, confirm LGL (`dl-de/by-2-0`), the official basemap.de string, and CityTreeCover (MIT) are listed and match the README credits (FR-011, SC-007)

**Checkpoint**: US3 complete — credits consistent in both places; suite green.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality pass across all stories.

- [X] T023 [P] Capture a map screenshot from the live deployment (`https://abu-hamad.de/map/`) and embed it in the README top half (recommended per `contracts/readme.md`)
- [X] T024 [P] Run the README link-resolution sweep (quickstart scenario 6) for all registry URLs and fix any dead links
- [X] T025 Run the full `quickstart.md` (scenarios 1–8) end to end and record results
- [X] T026 Run `make check-or005` (G2: no large data files tracked) — must stay green
- [X] T027 Final review: read `README.md` as a first-time visitor (SC-001); confirm no harness-internal or personal-path strings remain in tracked files (`git grep`); confirm working tree contains only intended changes; commit milestone via `make commit-milestone MSG="milestone: public release preparation"`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup. BLOCKS all user stories (gate + code hygiene must exist first).
- **User Stories (Phase 3+)**: depend on Foundational. US1 is the MVP and the primary deliverable. US2 and US3 depend on Foundational only; US3's consistency check (T022) needs US1's README.
- **Polish (Final Phase)**: depends on all user stories complete.

### User Story Dependencies

- **User Story 1 (P1)**: Foundational only. No dependencies on other stories — highest value, delivered first.
- **User Story 2 (P2)**: Foundational only. Independent of US1 in files; if run in parallel with US1, T019 (gate-clean finalize) runs last within US2 so it also covers US1's new files.
- **User Story 3 (P3)**: Foundational + US1 (credits consistency). Independently testable via scenario 7/8.

### Parallel Opportunities

- Foundational T005/T006/T007 are [P] — three different files.
- US1: T008 (LICENSE) and T009 (README) run in parallel; T010 (DEVELOPMENT.md) can also run alongside; T011 verifies after.
- US2: T012–T018 all run in parallel (12 different files/dirs); T019 is the serial gate-clean finalize.
- US1 and US2 can be staffed in parallel after Foundational.

## Parallel Example: User Story 1

```bash
# Launch US1 file-creating tasks together:
Task: "Create LICENSE per contracts/license.md"              # T008
Task: "Rewrite README.md per contracts/readme.md"            # T009
Task: "Create DEVELOPMENT.md with sanitized dev content"      # T010
# Then verify (T011) once all three exist.
```

## Parallel Example: User Story 2

```bash
# Launch all US2 scrub tasks together (each touches different files):
Task: "Sanitize specs/001 personal paths"      # T012
Task: "Fix specs/002 input-spec path"          # T013
Task: "Remove harness-internal references"     # T014
Task: "Redact specs/005 owner ops"             # T015
Task: "Placeholder zone_id + local override"   # T016
Task: "Parameterize deploy-cf.sh gates"        # T017
Task: "Env-var RunPod SSH defaults"            # T018
# Then run the gate (T019) and fix findings until clean.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (README + LICENSE + DEVELOPMENT.md)
4. **STOP VALIDATE**: quickstart scenarios 2, 4, 5, 6
5. The repository is already meaningfully public-ready (user-facing README, license, credits)

### Incremental Delivery

1. Setup + Foundational → foundation ready (gate exists)
2. Add User Story 1 → README/LICENCE/DEVELOPMENT.md → validate (MVP!)
3. Add User Story 2 → hygiene sweep → `make check-public` clean → publish-safe
4. Add User Story 3 → attribution alignment + regression green
5. Polish → full quickstart run, screenshot, final review → make public

### Parallel Team Strategy (multiple developers)

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: (after US1) User Story 3
3. Stories integrate independently; T019 and Polish re-verify the whole tree

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps the task to its user story for traceability.
- Every story is independently completable and testable via its quickstart scenarios.
- The hygiene gate (T003/T004) is the single source of truth for FR-010; never weaken it to make a task pass.
- Commit per logical group via `make commit-slice` (OR-004); stop at each checkpoint and validate the story independently.
- Avoid: vague tasks, same-file conflicts (each [P] group touches disjoint files), cross-story dependencies that break independence.
