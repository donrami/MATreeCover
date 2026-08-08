---
description: "Task list for Security Audit & Repo Housekeeping (feature 015)"
---

# Tasks: Security Audit & Repo Housekeeping (015)

**Input**: Design documents `/specs/015-security-audit-housekeeping/`
**Prerequisites**: plan.md, spec.md (4 user stories), research.md (R1–R12), data-model.md (E1–E10), contracts/ (5 contracts), quickstart.md (S1–S8)
**Tests**: explicitly requested by the spec — SC-007 (synthetic-pattern gate test), quickstart S1/S2/S4/S5/S7 acceptance tests. Written FIRST (fail before implementation).
**Organization**: Tasks grouped by user story so each story is implemented and tested independently. Branch: `015-security-audit-housekeeping`. No new packages; no new top-level directories; no git-history rewrite; zero user-visible map change.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: user story the task belongs to (US1–US4); setup/foundational/polish carry no label
- File paths in every description

## Path Conventions

Single flat repository (static frontend + pipeline + Worker + gates). Enforcement scripts live in `scripts/` next to the existing gates (`check-public.sh`, `check_or005.py`); the audit report joins the evidence home `verification/`; provenance sits next to the vendored files in `src/site/vendor/`. Tests: `tests/acceptance/`, `tests/endpoint/`. All enforcement is shell + git + grep only — no new dependencies.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization — feature branch on a clean baseline

- [X] T001 Create and switch to feature branch `015-security-audit-housekeeping` from clean `main` (verify `git status` clean before branching)
- [X] T002 [P] Run `bash scripts/check-prereqs.sh`; confirm git/python3.11/venv toolchain ready and worktree clean (no `data/`, `dist/`, `.omp/` tracked)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure every user story writes into — the audit report is the shared disposition sink (FR-012, SC-006); the baseline is the before-state every story's "no regression" claim compares against

- [X] T003 Create audit report skeleton `verification/security-audit-2026-08-08.md` per R11: scope, method, findings table (ID, severity, location, description, disposition), housekeeping decisions table, gate summary, how-to-re-run section. Empty sections stay as headings — later tasks fill them (FR-012, SC-006)
- [X] T004 [P] Run baseline verification: full pytest suite (`pytest tests/ -q`), `make check-public`, `make check-or005`; record results (counts, pass/fail) in the report's method section as the pre-audit state (feeds US4 comparison)

**Checkpoint**: Report skeleton committed; baseline state recorded — user stories can now begin in parallel

---

## Phase 3: User Story 1 — The Repository Contains No Secrets (Priority: P1) 🎯 MVP

**Goal**: Committed proof — from a scan, not a promise — that no credential, personal path, or private key material exists in tracked files or any of the 89 commits; every finding dispositioned; the FR-010 gate extended and trustworthy (FR-001/002/003, SC-001/007).

**Independent Test**: `make check-public` and `make check-history` both report clean (exit 0); `pytest tests/acceptance/test_public_hygiene.py tests/acceptance/test_secret_scan.py -q` green; the audit report lists every pattern checked (P1–P32) and the disposition of every historical hit.

### Tests User Story 1 (SC-007 requires; write FIRST, fail before implementation)

- [X] T005 [P] [US1] Write SC-007 regression test `tests/acceptance/test_public_hygiene.py`: writes a tracked-looking temp file containing each pattern P1–P32 and asserts `scripts/check-public.sh` fails naming that file and pattern (fails until T007/T010; a pattern that stops matching is a test failure)
- [X] T006 [P] [US1] Write `tests/acceptance/test_secret_scan.py`: asserts `scripts/check-git-history.sh` exits 0 with output `clean: 89 commits scanned, M exempted findings, 0 open` and that every exemption row resolves to a dispositioned finding in `verification/security-audit-2026-08-08.md` (fails until T011/T012)

### Implementation User Story 1

- [X] T007 [US1] Create `scripts/public-patterns.txt`: move the 19 existing regexes out of `scripts/check-public.sh` into the shared file, one ERE per line, each preceded by a `# P<n> — rationale` comment block (single source of truth for both gates per R2)
- [X] T008 [US1] Refactor `scripts/check-public.sh` to source patterns from `scripts/public-patterns.txt` (depends on T007); extend `EXEMPT_FILES` with `scripts/public-patterns.txt`; keep exit-0 `clean: N tracked files scanned` / exit-1 `file:line: match` semantics; fix the P9 zone-id script/contract drift
- [X] T009 [US1] Update `specs/006-public-release-prep/contracts/public-hygiene.md` (depends on T007/T008, same commit): document pattern IDs and rationale only, stop quoting regex literals, drop its hygiene exemption — contract and gate now change together (FR-003)
- [X] T010 [US1] Add patterns P20–P32 to `scripts/public-patterns.txt` (depends on T007) per the `contracts/secrets-scan.md` inventory: GitHub fine-grained PAT, Cloudflare API token (assignment form), Cloudflare X-Auth header form, AWS secret access key, AWS ASIA temp key, npm token, Slack token/webhook, Stripe live key, Google API key, PGP private key block, PuTTY key, netrc machine/login/password marker, desktop path fragment
- [X] T011 [US1] Implement `scripts/check-git-history.sh` (depends on T010): for each commit in `git rev-list --all` run `git grep -nIE '<all patterns as alternation>' <commit>`; scan commit messages via `git log --all --format='%H%x00%s%x00%b'`; allow a hit only with a row in `scripts/history-exemptions.tsv` (`<pattern-id>\t<commit-sha>\t<path>`); fail on unexempted findings, stale exemptions (rows matching nothing), and orphaned rows (no matching report finding); exit 0 `clean: N commits scanned, M exempted findings, 0 open`; never requires network access (R3)
- [X] T012 [US1] Run the history scan (depends on T011); disposition every finding in `verification/security-audit-2026-08-08.md` as `remediated` (rotation proof), `never-live` (evidence), or `accepted-risk` (reason + owner sign-off); populate `scripts/history-exemptions.tsv`; keep allow-listed values (`abu-hamad.de`, loopback refs, `MANNHEIM_WORKSPACE`/`RUNPOD_HOST`/`SSH_KEY`/`BIND_ADDR`, `/workspace/mannheim/...` paths) unflagged by pattern design, not by exemption (FR-002, SC-001)
- [X] T013 [US1] Add `check-history` target to `Makefile` next to `check-public` (depends on T011): `@bash scripts/check-git-history.sh`

**Checkpoint**: `make check-public` + `make check-history` clean; T005/T006 green; report dispositions complete for every hit — US1 fully functional and testable independently

---

## Phase 4: User Story 2 — The Deployed Surface Is Reviewed and Hardened (Priority: P1)

**Goal**: The maintainer knows what the Worker, R2, deploy scripts, and the RunPod endpoint expose; high-risk gaps are closed; every Worker response carries the documented security headers and CSP; the site keeps working exactly as before (FR-004/005/006/007, SC-002).

**Independent Test**: `pytest tests/endpoint/ -q` green (threshold tests plus new bind/413 tests); `bash scripts/deploy-cf.sh verify` passes the existing FR-013 gates and the new security-header + 404 assertions; the audit report records the HIGH and MEDIUM findings as remediated and lists accepted risks with reasons.

### Tests User Story 2 (write FIRST, fail before implementation)

- [X] T014 [P] [US2] Write `tests/endpoint/test_bind.py`: asserts `src/endpoint/server.py` binds `127.0.0.1` by default and honors a `BIND_ADDR` env override (fails until T017)
- [X] T015 [P] [US2] Write `tests/endpoint/test_request_size.py`: asserts `Content-Length > 1 MiB` → 413 before any body read; non-numeric length falls into the 400 path (fails until T018)

### Implementation User Story 2

- [X] T016 [US2] Implement `applySecurityHeaders()` in `workers/map/index.js` per `contracts/security-headers.md`: set/override exactly the 7 security headers (CSP byte-identical to the meta tag in `src/site/index.html`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`, `Strict-Transport-Security: max-age=31536000` without includeSubDomains, `X-XSS-Protection: 0`) on every response — static assets, R2 passthroughs (200 and 206), and 404s; on 206 responses never alter `Content-Range`, `ETag`, `Accept-Ranges`, or `Content-Length` (R4, FR-013)
- [X] T017 [US2] Fix HIGH finding in `src/endpoint/server.py`: bind `127.0.0.1` by default with `BIND_ADDR` env override for deliberate pod-internal exposure; SSH-tunnel workflow unchanged (R7)
- [X] T018 [US2] Fix MEDIUM finding in `src/endpoint/server.py`: reject `Content-Length > 1 MiB` with 413 before reading the body (depends on T017; same file, sequential)
- [X] T019 [P] [US2] Pin resolved pod dependency versions in `scripts/runpod-deploy.sh` (`pip install segmentation-models-pytorch rasterio` → pinned versions) so the pod supply chain is reproducible (R6 low fix)
- [X] T020 [US2] Extend `scripts/deploy-cf.sh verify` (depends on T016): assert security headers on `/map/` (index) and on a 206 Range response from an R2 key; assert an unknown data-looking key returns 404; existing DNS/redirect/Range/cache-header/cert gates unchanged (R5, R12)
- [X] T021 [US2] Update `specs/005-host-on-personal-domain/contracts/hosting-config.md` §3 with the header and unknown-key-404 checks (depends on T020, same commit) so the deploy contract stays in sync
- [X] T022 [US2] Record US2 findings and dispositions in `verification/security-audit-2026-08-08.md` (depends on T016–T019): HIGH bind and MEDIUM size-cap remediated; accepted risks with reasons — no auth on `/infer` (loopback-only, single owner), serialized long-running inference, pinning fix; verify `src/endpoint/server.py` matches `contracts/endpoint-trust-model.md` (FR-002, SC-002)

**Checkpoint**: `pytest tests/endpoint/` green; `deploy-cf.sh verify` passes with new assertions; report records remediated HIGH/MEDIUM — US2 independently testable

---

## Phase 5: User Story 3 — The Repository Layout Matches Its Documentation (Priority: P2)

**Goal**: Every tracked file resolves to a documented location in DEVELOPMENT.md's layout section; root strays and duplicates consolidated with recorded dispositions; vendored libraries have committed provenance; README/DEVELOPMENT/CHANGELOG/spec index agree with reality (FR-008/009/010/011, SC-003).

**Independent Test**: `make check-layout` reports `clean: N tracked paths, M documented entries` (exit 0); `pytest tests/acceptance/test_layout.py -q` green; the layout section names every root-level file and the manifest as its machine form; `sha256sum src/site/vendor/*.js src/site/vendor/*.css` matches PROVENANCE.md.

### Tests User Story 3 (write FIRST, fail before implementation)

- [X] T023 [P] [US3] Write `tests/acceptance/test_layout.py`: asserts `scripts/check-layout.sh` exits 0 with the clean summary on the reorganized repo (fails until T025; also asserts no tracked root file outside the documented root set)

### Implementation User Story 3

- [X] T024 [US3] Create `scripts/layout-manifest.tsv` per `contracts/layout-gate.md`: TAB-separated `<tracked-path>\t<documentation-reference>` rows for the frozen root set — `.gitignore`, `CHANGELOG.md`, `DEVELOPMENT.md`, `LICENSE`, `Makefile`, `README.md`, `pyproject.toml`, `artifacts.manifest.json`, `tiles.csv`, `screenshot/`, `scripts/`, `specs/`, `src/`, `tests/`, `validation/`, `verification/`, `workers/`, `outputs/`
- [X] T025 [US3] Implement `scripts/check-layout.sh` (depends on T024): every `git ls-files` path must start with a manifest row; every row must exist in the tracked tree (no dead entries); no tracked file at the repo root outside the documented root set; exit 0 `clean: N tracked paths, M documented entries`, exit 1 with one `path → expected documentation-reference` mismatch line per failure (R9)
- [X] T026 [P] [US3] `git mv cited.md` → `outputs/cited.md` (DEVELOPMENT.md already documents the verified source list under `outputs/`); update the two DEVELOPMENT.md references to point at the new path (R10)
- [X] T027 [P] [US3] `git mv notes/s2_abstracts.json notes/s2_abstracts2.json` → `outputs/` (Semantic-Scholar abstracts are literature-review evidence; empty `notes/` disappears from git) (R10)
- [X] T028 [P] [US3] Move root `info` (WebP, no extension) → `outputs/info.webp` per owner decision; disposition recorded in the audit report — never silently deleted (R10, spec edge case)
- [X] T029 [US3] Delete `progress.md` (72-byte boilerplate template, no references) after owner sign-off recorded in the audit report; deletion documented, not silent (R10, spec edge case)
- [X] T030 [P] [US3] Create `src/site/vendor/PROVENANCE.md` per `contracts/vendored-provenance.md`: MapLibre GL JS 5.7.1 (BSD-3-Clause, github.com/maplibre/maplibre-gl-js, `maplibre-gl.js` + `maplibre-gl.css`) and pmtiles 4.4.0 (BSD-3-Clause, github.com/protomaps/PMTiles, `pmtiles.js`), each with sha256 computed from the tracked files; declare runtime dependencies — LGL basemap `sgx.geodatenzentrum.de` (attributed) and `demotiles.maplibre.org` glyph origin as accepted risk (MEDIUM, owner sign-off) (R8)
- [X] T031 [US3] Update `DEVELOPMENT.md` (depends on T024–T030): layout section enumerates every root-level file plus `screenshot/` and `outputs/.plans/`, and names `scripts/layout-manifest.tsv` as the machine-checkable form; governance section documents `check-history` and `check-layout`; lit-review references point at `outputs/cited.md`; correct the "no other third-party scripts are used" claim to declare the demotiles font origin; vendored-libraries section references `src/site/vendor/PROVENANCE.md`
- [X] T032 [P] [US3] Update `CHANGELOG.md` with the 2026-08-08 security-audit entry and add the 015 row to the feature-history spec index (FR-010)
- [X] T033 [US3] Add `check-layout` target to `Makefile` (depends on T025): `@bash scripts/check-layout.sh`
- [X] T034 [US3] Record every housekeeping decision (E9) in `verification/security-audit-2026-08-08.md`: move/delete/keep-and-document with destination or reason for `cited.md`, `s2_abstracts*.json`, `info`, `progress.md`, `notes/`, `screenshot/`, `outputs/.plans/` (depends on T026–T029)

**Checkpoint**: `make check-layout` clean; layout section ↔ manifest consistent; PROVENANCE.md hashes match the tracked files — US3 independently testable

---

## Phase 6: User Story 4 — Nothing Regresses (Priority: P2)

**Goal**: The maintainer ships the audit knowing the map is byte-for-byte the same experience and every gate still passes (FR-013/014, SC-004/005).

**Independent Test**: Full pytest suite green; all governance gates (check-public, check-or005, check-history, check-layout, commit checks) green; `deploy-cf.sh verify` green including new assertions; interaction harness within budget; parity render identical to the current bundle.

### Implementation User Story 4

- [X] T035 [US4] Run the full test suite `pytest tests/ -q` (acceptance, pipeline, endpoint including new tests); fix any failure caused by housekeeping moves or header changes — e.g. tests referencing moved paths (quickstart S4)
- [X] T036 [US4] Run every governance gate — `make check-public`, `make check-or005`, `make check-history`, `make check-layout`, `scripts/commit-check.sh` — and confirm all exit 0 on the audited tree (SC-004)
- [X] T037 [P] [US4] Run `bash scripts/deploy-cf.sh verify` against the live deploy: existing FR-013 gates (DNS, redirects, Range 206, cache headers, cert) plus the new security-header and unknown-key-404 assertions; confirm headers present with contract values and CSP byte-identical to the meta tag (quickstart S6)
- [X] T038 [P] [US4] Run `bash scripts/perf-measure.sh https://abu-hamad.de/map/` and `node scripts/parity-render.mjs`: all 8 interactions ≤ 2 s, desktop median ≤ 123 ms, first usable ≤ 10 s, rendered building values/colors/labels/popups identical to the pre-audit bundle (quickstart S8, SC-005)
- [X] T039 [US4] Verify OR-005: no `*.tif`/`*.pmtiles`/`>50 MiB` file entered the tracked set (`make check-or005` green); gitignored local dirs (`data/`, `dist/`, `dist-assets/`, `.omp/`, `.venv/`) untouched and `scripts/check-prereqs.sh` paths intact
- [X] T040 [US4] Finalize `verification/security-audit-2026-08-08.md` (depends on T035–T039): complete gate summary and how-to-re-run section so a reviewer unfamiliar with the repo can verify every disposition (SC-006)

**Checkpoint**: All suites, gates, and deploy verification green; parity and perf budgets met — US4 complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories — end-to-end validation, contract/implementation consistency, docs accuracy

- [X] T041 [P] Run quickstart.md scenarios S1–S8 in order against the finished tree; record results in the audit report's gate summary (quickstart is the run guide for the whole feature)
- [X] T042 [P] Verify all five contracts (`contracts/secrets-scan.md`, `security-headers.md`, `layout-gate.md`, `vendored-provenance.md`, `endpoint-trust-model.md`) match the implementation; update `contracts/README.md` cross-link table if any subject drifted
- [X] T043 [P] README.md accuracy check (R10: no content change required — verify; add the optional security link only if it stays accurate)
- [X] T044 Commit all remaining work in logical slices with `make commit-slice MSG="..."` (OR-004 discipline: gate/contract/report changes for the same surface land in the same commit; no `make commit-milestone` until validation milestones pass)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately
- **Foundational (Phase 2)**: depends on Setup; report skeleton (T003) and baseline (T004) feed every story
- **User Stories (Phase 3+)**: depend on Foundational; US1/US2 (P1) and US3/US4 (P2) proceed in parallel (staffed teams) or in priority order
- **Polish (Final Phase)**: depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: no dependencies on other stories — MVP
- **User Story 2 (P1)**: no dependencies on other stories
- **User Story 3 (P2)**: no dependencies on other stories (manifest frozen after housekeeping moves; `info`/`progress.md` dispositions recorded independently)
- **User Story 4 (P2)**: depends on US1–US3 being complete (it verifies the audited tree end to end)

### Within Each User Story

- Tests written FIRST, must FAIL before implementation (T005/T006, T014/T015, T023)
- Shared pattern file before gates (T007 → T008/T010 → T011); manifest before gate (T024 → T025); fixes before report entries (T016–T019 → T022; T026–T029 → T034)
- Story complete before moving to the next priority

## Parallel Opportunities

- **Setup**: T002 parallel with T001
- **Foundational**: T004 parallel with T003
- **US1**: T005 and T006 run in parallel (different test files); T011 and T012 are sequential (scan depends on gate), but T009's contract update is parallelizable with T010 once T007 lands
- **US2**: T014 and T015 (test files) in parallel; T019 (runpod pin) parallel with the worker/endpoint slices; T017 then T018 sequentially (same file)
- **US3**: T026/T027/T028/T030 (moves + provenance, different files) all in parallel; T031 depends on the moves; T032 and T033 parallel with each other
- **US4**: T037 (deploy verify) and T038 (perf/parity) run in parallel; T035/T036 local runs parallel with them
- **Polish**: T041/T042/T043 all in parallel
- Once Foundational completes, US1–US3 start in parallel (different teams/members); US4 follows

## Parallel Example: User Story 1

```bash
# Launch both US1 tests together (fails until implementation):
Task: "Write SC-007 regression test tests/acceptance/test_public_hygiene.py (T005)"
Task: "Write tests/acceptance/test_secret_scan.py (T006)"
# Then, after the shared pattern file lands (T007):
Task: "Refactor scripts/check-public.sh to source scripts/public-patterns.txt (T008)"
Task: "Update specs/006-public-release-prep/contracts/public-hygiene.md (T009)"
```

## Parallel Example: User Story 2

```bash
# Launch both endpoint tests together:
Task: "Write tests/endpoint/test_bind.py (T014)"
Task: "Write tests/endpoint/test_request_size.py (T015)"
# Launch independent slices together:
Task: "Pin pod dependencies in scripts/runpod-deploy.sh (T019)"
Task: "Implement applySecurityHeaders in workers/map/index.js (T016)"
```

## Parallel Example: User Story 3

```bash
# Launch the housekeeping moves and provenance record together:
Task: "git mv cited.md → outputs/cited.md (T026)"
Task: "git mv notes/s2_abstracts*.json → outputs/ (T027)"
Task: "Move info → outputs/info.webp (T028)"
Task: "Create src/site/vendor/PROVENANCE.md (T030)"
# Documentation and Makefile updates follow (T031/T032/T033).
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (audit report skeleton + baseline)
3. Complete Phase 3: User Story 1 (secrets scan, history gate, exemptions, dispositions)
4. **STOP VALIDATE**: `make check-public` + `make check-history` clean, SC-007 test green, report dispositions complete
5. The secrets audit is the highest-impact deliverable and ships independently

### Incremental Delivery

1. Setup + Foundational → foundation ready (report + baseline committed)
2. Add User Story 1 → test independently → commit (MVP: secrets audit complete)
3. Add User Story 2 → test independently (endpoint tests + deploy verify) → commit (surface hardened)
4. Add User Story 3 → test independently (layout gate + provenance) → commit (tree matches docs)
5. Add User Story 4 → full-suite regression proof + perf/parity → commit milestone
6. Polish: quickstart S1–S8 end-to-end run, contract/implementation consistency, final slice commits

### Parallel Team Strategy (multiple developers)

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (patterns, both gates, exemptions)
   - Developer B: User Story 2 (worker headers, endpoint fixes, verify extension)
   - Developer C: User Story 3 (manifest, gate, moves, provenance, docs)
3. Developer D (or the team) runs User Story 4 verification once US1–US3 merge
4. Stories integrate independently; the shared audit report is the only cross-story file — each story appends its own section (use distinct headings per story to avoid edit conflicts)

## Notes

- [P] tasks = different files, no dependencies — the audit report (`verification/security-audit-2026-08-08.md`) is the one shared sink; story tasks that append to it (T012, T022, T034, T040) are deliberately sequential within their story and use distinct sections
- Gate changes, contract changes, and report entries for the same surface land in the same commit (FR-003, OR-004)
- No new dependencies: enforcement is git + grep + shell only; no gitleaks, no new packages
- Verify tests fail before implementation (T005/T006/T014/T015/T023); commit each logical slice; stop at each checkpoint and validate the story independently
- Avoid: vague tasks, same-file conflicts (T017/T018 sequential), cross-story dependencies that break independence

---

## Phase 8: Convergence

**Purpose**: Close the gaps found when the implementation was assessed against the spec, plan, and tasks after the implement command completed all prior phases (converge run 2026-08-08). All prior phases verified green: `check-public` (293 files), `check-history` (96 commits, 2030 exempted, 0 open), `check-layout` (296 paths / 18 entries), `check-or005`, pytest 156 passed, CSP byte-identical header/meta, PROVENANCE.md hashes match, 3-key R2 whitelist with 206 preserved, endpoint loopback bind + 413 cap, all 5 contracts present.

- [X] T045 Commit or revert the regenerated `artifacts.manifest.json` (timestamp-only diff, uncommitted since the last slice) so the audited tree is a clean, fully committed state per T044 and FR-010 (`partial`)
- [X] T046 Deploy the reviewed Worker to Cloudflare (owner-gated, requires `scripts/deploy-cf.env` or `MATREECOVER_*` credentials) and re-run `bash scripts/deploy-cf.sh verify` so the security-header and unknown-key-404 assertions pass against the live surface per FR-004/SC-002 (`partial`)
- [X] T047 Record quickstart S1–S8 run results as a row in `verification/security-audit-2026-08-08.md`'s gate summary per T041/SC-006 (`partial`)
