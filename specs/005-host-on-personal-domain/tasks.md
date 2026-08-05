# Tasks: Host on Personal Domain

**Input**: Design documents `/specs/005-host-on-personal-domain/`
**Prerequisites**: plan.md (required), spec.md (required user
stories), research.md, data-model.md, contracts/, quickstart.md
**Tests**: manual smoke checklists + quickstart scenarios (project
convention — the spec requests no automated test suite)
**Organization**: tasks grouped by user story; each story is
independently implementable and testable via its quickstart
scenario.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: run in parallel (different files, no dependencies)
- **[Story]**: user story the task belongs to (US1..US5) — only in
  user story phases
- Every task includes exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Cloudflare zone + tooling + bucket — the blocking
prerequisites for every user story.

- [X] T001 Create the Cloudflare zone and migrate DNS per
  `contracts/dns-https.md` §3: inventory the <hosting-provider> DNS Zone
  Editor (A `@`/`www`, MX, TXT SPF/DMARC/DKIM, any `mail` A),
  corroborate with `dig @1.1.1.1 abu-hamad.de {A,MX,TXT,NS}`,
  create the zone (free, full setup), reconcile records (blog A
  grey, email DNS-only), change nameservers at <registrar>, wait for
  zone Active + Universal SSL Active, flip blog A to proxied with
  SSL mode Full (strict). **Accept**: `dig abu-hamad.de NS`
  returns Cloudflare NS at two resolvers; the blog loads over
  HTTPS; quickstart Scenario 7 (FR-014 gate) passes.
- [X] T002 [P] Scaffold the Worker project:
  `workers/map/package.json` (devDependency wrangler pinned
  `>= 3.98.0` — required for subdirectory asset serving,
  research R-011) and `workers/map/wrangler.toml` skeleton: `name
  = "matreecover-map"`, `main = "index.js"`,
  `assets.directory = "../../dist"`, `r2_buckets` binding
  `DATA -> matreecover-data`, and the four routes
  `abu-hamad.de/map`, `abu-hamad.de/map/*`,
  `www.abu-hamad.de/map`, `www.abu-hamad.de/map/*` per
  `contracts/hosting-config.md` §1. **Accept**: `npx wrangler
  deploy --dry-run` succeeds from `workers/map/`.
- [X] T003 [P] Create the R2 bucket with `npx wrangler r2 bucket
  create matreecover-data` (free tier, `contracts/bundle.md` §1).
  **Accept**: `npx wrangler r2 bucket list` shows the bucket.

**Checkpoint**: zone Active, Worker project scaffolds, bucket
exists — story implementation can begin.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: shared plumbing both the Worker and the deploy script
need; MUST complete before any user story implementation.

- [X] T004 Implement the shared plumbing of `scripts/deploy-cf.sh`:
  `set -euo pipefail`, configuration block (WORKER_DIR=workers/map,
  BUCKET=matreecover-data, DIST=dist, ARCHIVE=dist-archive,
  wrangler via `npx wrangler`), timestamped logging, and the
  sha256 identity manifest generator (sorted file list, per-file
  sha256, total bytes, file count) plus the R2 free-tier storage
  check (data size vs 10 GB-month) per `contracts/deployment.md`
  §3.1-3.3. **Accept**: running the script with a real `dist/`
  prints a valid manifest and passes the storage check.
- [X] T005 [P] Authorize tooling and verify the zone state:
  `npx wrangler login` + `npx wrangler whoami`; confirm the
  `abu-hamad.de` zone shows Active and Universal SSL Active via
  `npx wrangler zones list`. **Accept**: `wrangler whoami`
  shows the account; zone Active.

**Checkpoint**: tooling authenticated, script plumbing proven —
user story implementation can begin in parallel.

## Phase 3: User Story 1 — Public Access at the Personal Domain (P1)

**Goal**: `https://abu-hamad.de/map/` renders the map for any
visitor; `/map` and `www` variants canonicalize; the blog root is
untouched. **Independent Test**: quickstart Scenario 1 (fresh
profile, German texts match local, `/map` 301, www 301, phone
viewport, byte-identity SC-007).

- [X] T006 [US1] Implement `workers/map/index.js` routing and
  asset serving: `/map` -> 301 `/map/`; `www.abu-hamad.de/map*`
  -> 301 `https://abu-hamad.de/map/`; `/map/*` small files served
  from the assets directory; non-`/map` paths fall through to the
  origin (never handled) per `contracts/hosting-config.md` §1.
  **Accept**: `npx wrangler dev` at `/map/` serves `index.html`
  with all relative asset refs (`style.css`, `vendor/*.js`,
  `main.js`) resolving under `/map/`; `/map` and the www variants
  redirect exactly once.
- [X] T007 [US1] Deploy the Worker with the four routes to the
  live zone (`npx wrangler deploy` from `workers/map/`); verify
  live per quickstart Scenario 1 + Scenario 6 redirect checks:
  `/map/` 200, `/map` 301, `www.abu-hamad.de/map/` 301 to the
  canonical, domain root still serves the blog; byte-identity of
  `index.html`, `style.css`, `main.js`, `style.json`,
  `attribution.html` vs `dist/` (SC-007). **Accept**: Scenario 1
  pass criteria all green.

**Checkpoint**: US1 fully functional and independently testable —
MVP reachable.

## Phase 4: User Story 2 — Fully Functional Interactive Map (P1)

**Goal**: all map data layers load on the live site at all zoom
levels via Range requests (FR-005, FR-007). **Independent Test**:
quickstart Scenario 2 (pan/zoom/popup/Bäume toggle at z16-z18,
206 in the network tab).

- [X] T008 [US2] Implement the R2 range passthrough in
  `workers/map/index.js` for `buildings.pmtiles`,
  `trees.pmtiles`, `buildings.geojson`: forward the client
  `Range` header to `env.DATA.get(key, { range })` and pass
  through R2's 206 + `Content-Range` (research R-003).
  **Accept**: a Range request via `npx wrangler dev` returns 206
  with a correct `Content-Range` for each of the three keys.
- [X] T009 [US2] Add the data upload step to
  `scripts/deploy-cf.sh`: `npx wrangler r2 object put` for the
  three data files with `--content-type application/vnd.pmtiles`
  (pmtiles) / `application/geo+json` (geojson) and
  `--cache-control "no-cache, no-transform"` (pmtiles) /
  `"no-cache"` (geojson) per `contracts/hosting-config.md` §2;
  then upload and verify live: 206 on `buildings.pmtiles` and
  `trees.pmtiles`, smoke checklists `smoke_us1.md`..`smoke_us4.md`
  against `https://abu-hamad.de/map/`. **Accept**: Scenario 2 pass
  criteria all green.

**Checkpoint**: US2 fully functional and independently testable.

## Phase 5: User Story 3 — Secure HTTPS Delivery (P2)

**Goal**: valid certificate, no warnings, no mixed content
(FR-002, FR-003, SC-003) plus the FR-013/FR-014 gates. **Independent
Test**: quickstart Scenarios 3, 6, 7.

- [X] T010 [US3] Add the FR-013 verification block to
  `scripts/deploy-cf.sh` (dig NS/A; `/map/` 200 + no-cache
  header; Range 206 on `buildings.pmtiles`; `/map`/www 301s;
  certificate validity + hostname coverage via `openssl
  s_client`) and the FR-014 block (blog HTTPS load; MX/TXT dig
  checks; email send/receive test instructions) per
  `contracts/dns-https.md` §5; write results into
  `validation/deploy-<ts>.json`. **Accept**: quickstart Scenarios
  3, 6, and 7 pass criteria all green; a failed gate aborts the
  script with a non-zero exit.

**Checkpoint**: US3 fully functional; gates block failed deploys.

## Phase 6: User Story 4 — Acceptable Performance (P2)

**Goal**: SC-004 budgets hold on the live path. **Independent
Test**: quickstart Scenario 4.

- [X] T011 [US4] Measure the live site under the published CDP
  throttle profile (25 Mbps / 50 ms, cold cache per run) against
  `https://abu-hamad.de/map/` and write `validation/live-perf.json`
  with the same schema as `validation/perf-budget.json`.
  **Accept**: first usable map <= 10 s, interactions <= 2 s;
  record written.

**Checkpoint**: US4 record exists and passes the budget.

## Phase 7: User Story 5 — Repeatable, Safe Updates (P3)

**Goal**: the documented procedure publishes updates safely; an
interrupted deploy leaves the previous version live; rollback
works (FR-009, FR-010, SC-005, SC-006). **Independent Test**:
quickstart Scenario 5.

- [X] T012 [US5] Verify rollback + interruption safety of
  `scripts/deploy-cf.sh`: kill an `r2 object put` mid-transfer
  and confirm the previous object's checksum and the live version
  are unchanged (PUT atomicity); run `npx wrangler rollback` and
  re-upload the previous release's objects from `dist-archive/`;
  confirm `/map/` serves the previous version. **Accept**:
  Scenario 5 pass criteria all green.
- [X] T013 [P] [US5] Update the README "Publish + static hosting"
  section to the Cloudflare procedure: `workers/map/` +
  `scripts/deploy-cf.sh`, canonical URL `/map/`, R2 data path,
  DNS migration pointer to `contracts/dns-https.md`; remove the
  obsolete <hosting-provider>/nginx-era guidance. **Accept**: README
  reflects the Cloudflare topology with no stale <hosting-provider>
  instructions.

**Checkpoint**: US5 fully functional; procedure repeatable.

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: full validation and cleanup across all stories.

- [ ] T014 Run the complete quickstart (Scenarios 1-7) against the
  live site; verify no leftover <hosting-provider>-era deployment artifacts
  (`scripts/deploy.sh` removed; no `.htaccess`/symlink references
  outside the explicit "obsolete" notes in docs); confirm `git
  status` shows only intended files. **Accept**: all seven
  scenarios pass; worktree contains only planned changes.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no code dependencies — start immediately;
  T001 is manual ops, T002/T003 run in parallel.
- **Foundational (Phase 2)**: depends on T002 (Worker scaffold);
  T004 depends on T003 (bucket exists) and a real `dist/` from
  `make publish`; T005 runs in parallel with T004.
- **User Stories (Phase 3+)**: US1 depends on T004/T005 + live
  zone (T001); US2 depends on T008 (Worker code) + T009 (script
  step, depends on T004); US3 depends on T010 (script block,
  depends on T004); US4 depends on a live deploy (after US1/US2);
  US5 depends on T009/T010 (script complete). Stories proceed
  sequentially in priority order (P1 -> P2 -> P3) since they share
  `workers/map/index.js` and `scripts/deploy-cf.sh`.

### Within Each User Story

- Core implementation before live verification; each story ends
  with its quickstart scenario(s) green before the next story
  starts.

### Parallel Opportunities

- T002 + T003 (Setup) — different files, no dependencies.
- T004 + T005 (Foundational) — script plumbing vs tooling auth.
- T012 + T013 (US5) — drill vs README, different files.
- Polish T014 runs last, alone.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (T001..T003) and Phase 2 (T004..T005).
2. Complete Phase 3 (US1: T006, T007).
3. **STOP VALIDATE**: quickstart Scenario 1 + Scenario 6 redirect
   checks; the map renders at `/map/` (basemap + boundary mask;
   buildings layer shows the existing "Gebäudedaten derzeit nicht
   verfügbar" fallback until US2 uploads the data).
4. Deploy/demo if ready, then continue to US2.

### Incremental Delivery

1. Setup + Foundational -> foundation ready.
2. US1 (map renders at /map/) -> MVP, independently verified.
3. US2 (data layers live) -> complete interactive map.
4. US3 (HTTPS + gates) -> secure, guarded deploys.
5. US4 (perf record) -> budget proven live.
6. US5 (updates + rollback) -> routine publishing.

### Commit Discipline (OR-004)

- One `make commit-slice MSG="..."` per logical slice, e.g.
  "slice: Cloudflare worker serving /map (US1)", "slice: R2 data
  path (US2)", "slice: deploy gates (US3)", "slice: perf record
  (US4)", "slice: deploy procedure + rollback (US5)".
- `commit-slice` sweeps `git add -A` (it will pick up `tasks.md`
  and `validation/event.log.jsonl` with the first slice).
- Final validation lands as `make commit-milestone MSG="..."`.

## Notes

- [P] tasks = different files, no dependencies.
- Each user story is independently completable and testable.
- Avoid vague tasks and same-file conflicts; verify each story at
  its checkpoint before moving on.
