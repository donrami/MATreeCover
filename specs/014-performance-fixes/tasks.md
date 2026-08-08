# Tasks: Performance Fixes

**Input**: Design documents `/specs/014-performance-fixes/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md
**Tests**: Test and verification artifacts are in-scope deliverables where the contracts or repo gates require them (parity script, publish rewrite assertions, perf harness, image sanity, deploy gates).
**Organization**: Tasks grouped by user story. Each story is independently implementable and testable.
**Format**: `[ID] [P?] [Story] Description with file path`

## Path Conventions

- Frontend sources: `src/site/`
- Pipeline (publish, hashing): `src/pipeline/`
- Worker: `workers/map/`
- Deploy: `scripts/deploy-cf.sh`, `Makefile`
- Tests and tooling: `tests/`, `scripts/`
- Evidence: `validation/`

---

## Phase 1: Setup (Baseline)

**Purpose**: Capture the before-state so every later measurement has a comparison.

- [ ] T001 Capture baseline measurements on the current published bundle (Lighthouse 13.4.1 mobile + desktop, warm-visit same-origin transfer, 8 interaction latencies) into `validation/baseline-014.json` using the audit method from `validation/perf-audit-2026-08-08.md`

**Checkpoint**: Baseline recorded. Current mobile score 67, TBT 6310 ms, LCP 2459 ms.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared mechanics that every user story needs. Must complete before any story starts.

- [ ] T002 [P] Add the reusable perf harness `scripts/perf-measure.sh` (headless Chromium + CDP: cold load LCP/CLS/TTFB, warm-visit transfer, interaction latency probe; optional Lighthouse invocation; method per `validation/perf-budget.json` and `quickstart.md` S2-S4)
- [ ] T003 [P] Implement the publish hashing engine in `src/pipeline/publish.py` per `contracts/hashed-bundle.md`: sha256-12 hashed renames for main.js, style.css, style.json, vendor/maplibre-gl.js, vendor/maplibre-gl.css, vendor/pmtiles.js, stadtteile.geojson, boundary.geojson; deterministic reference rewrites (STYLE_URL and fetch URLs in main.js, source data URLs in style.json); single-occurrence assertions; `hashed_assets` map in `dist/manifest.json`; unit tests in `tests/test_publish_hashing.py`

**Checkpoint**: Foundation ready. Hashing is deterministic and idempotent. Stories can start in parallel.

---

## Phase 3: User Story 1 — Repeat Visits Load Fast (Priority: P1)

**Goal**: Cached range responses and immutable assets cut the repeat-visit transfer from ~900 KB to under 100 KB same-origin.

**Independent Test**: Warm-load via `scripts/perf-measure.sh`. Second navigation transfers under 100 KB same-origin. Hashed asset responses carry `public, max-age=31536000, immutable`. index.html keeps `max-age=0`.

- [ ] T004 [P] [US1] Add the hashed-filename Cache-Control rule to `workers/map/index.js` (ASSETS branch; regex `-[0-9a-f]{12}\.(js|css|json|geojson|svg)$` → `public, max-age=31536000, immutable`; all other responses unchanged) per `contracts/cache-headers.md`
- [ ] T005 [P] [US1] Change the R2 upload metadata in `scripts/deploy-cf.sh` (lines 91-92): buildings.pmtiles and trees.pmtiles from `no-store, no-transform` to `public, max-age=86400, stale-while-revalidate=604800, no-transform`; add a cache-control presence check to the verify gate per `contracts/cache-headers.md`
- [ ] T006 [US1] Verify warm-visit caching locally via nginx + `scripts/perf-measure.sh` (depends on T002, T003, T004): second-load same-origin transfer under 100 KB; pmtiles ranges served from browser cache; hashed asset headers immutable

**Checkpoint**: US1 complete. Repeat-visit transfer budget met locally.

---

## Phase 4: User Story 2 — Low-End Phones Can Use the Map (Priority: P1)

**Goal**: Main-thread blocking drops so the mobile lab profile meets TBT < 1.5 s and LCP < 2.0 s, with identical values and no missing buildings.

**Independent Test**: Lighthouse 13.4.1 mobile on the rebuilt bundle (median of 3). TBT < 1.5 s, LCP < 2.0 s. Parity gates pass: feature count and properties per tile identical to the current archive, screenshot parity at z10-z18.

- [ ] T007 [P] [US2] Add `fadeDuration: 0` to the Map constructor in `src/site/main.js` (the options object in `init()`)
- [ ] T008 [P] [US2] Add `-S 10 --simplify-only-low-zooms` to the `pmtiles-buildings` target in `Makefile` per `contracts/low-zoom-simplification.md`
- [ ] T009 [US2] Rebuild the archive: `make pmtiles-buildings` (depends on T008; writes `data/archive/workspace/buildings.pmtiles`)
- [ ] T010 [P] [US2] Add the parity check script `tests/parity_check.py` (feature-count and property parity per tile at z10-z13 against the current archive, using the pmtiles Python library) and run it after T009
- [ ] T011 [P] [US2] Render before/after screenshots at z10, z12, z14, z16, z18 (initial view + fixed cameras) with the current and rebuilt archives; diff below the SC-005 threshold with no missing, added, or degenerate buildings
- [ ] T012 [US2] Run Lighthouse 13.4.1 mobile on the rebuilt bundle (depends on T009, T010): TBT < 1.5 s, LCP < 2.0 s (SC-001). If parity gates fail, lower the scale to 5 and repeat. If TBT exceeds the target at the highest passing scale, extend the initial-view optimization and re-measure per `contracts/low-zoom-simplification.md`
- [ ] T013 [US2] Run the SC-005 image sanity suite and the value recalculation check (source geojson untouched; city mean and per-building values unchanged)

**Checkpoint**: US2 complete. Mobile metrics meet SC-001 with parity gates green.

---

## Phase 5: User Story 3 — First Load Starts Faster (Priority: P2)

**Goal**: The map library download starts earlier, the basemap connection is pre-warmed, no stylesheet blocks first paint, and the favicon 404 disappears.

**Independent Test**: Request-waterfall inspection on a cold load. maplibre-gl.js download starts before the end-of-body script tag. The sgx connection is pre-warmed. No render-blocking stylesheet request. favicon.svg returns 200.

- [ ] T014 [P] [US3] Add a small self-hosted `favicon.svg` to `src/site/`
- [ ] T015 [US3] Add the critical-path transforms to the publish step in `src/pipeline/publish.py` (depends on T003; same file, sequential): inline style.css and vendor/maplibre-gl.css into a `<style>` block, add `<link rel="preload" href="vendor/maplibre-gl-<hash>.js" as="script">`, `<link rel="preconnect" href="https://sgx.geodatenzentrum.de">`, and the favicon link per `contracts/hashed-bundle.md`; extend `tests/test_publish_hashing.py`
- [ ] T016 [US3] Verify the cold-load waterfall via nginx + `scripts/perf-measure.sh` (depends on T015): preload starts the library fetch early, preconnect used, zero render-blocking stylesheet requests, favicon 200, FCP not regressed vs baseline

**Checkpoint**: US3 complete. Critical path verified.

---

## Phase 6: User Story 4 — Deploys Stay Safe (Priority: P2)

**Goal**: Every existing gate passes and the published site matches the measured bundle.

**Independent Test**: Full suite green, all 8 interactions within the 2 s budget, deploy gates pass, live headers match the directive table.

- [ ] T017 [US4] Run the full regression suite: `.venv/bin/python -m pytest tests/`, `bash scripts/check-public.sh` (FR-010), `make check-or005` (OR-005)
- [ ] T018 [US4] Re-measure interaction latencies with `scripts/perf-measure.sh` (depends on T002): all 8 interactions within the 2 s budget, desktop median at or below 123 ms (SC-005)
- [ ] T019 [US4] Deploy and verify per `quickstart.md` S7 (depends on all prior stories): `prepare-assets`, `upload-data`, `wrangler deploy`, `scripts/deploy-cf.sh verify`; live checks — hashed asset immutable headers, index.html `max-age=0`, repeated range request cf-cache-status (HIT expected; if MISS record it and apply the browser-only SC-004 fallback), favicon 200
- [ ] T020 [US4] Update `validation/perf-budget.json` and `validation/live-perf.json` with the new measurements in the existing record format

**Checkpoint**: US4 complete. Published site verified.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Wrap-up that touches multiple stories.

- [ ] T021 [P] Update `CHANGELOG.md` for feature 014
- [ ] T022 Run `quickstart.md` S1-S7 end-to-end as the final acceptance gate
- [ ] T023 Commit per OR-004: `make commit-slice` after each story checkpoint, `make commit-milestone` after the final validation, `make commit-spec|commit-plan` already done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Run first.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all stories.
- **US1 (Phase 3)**: Depends on T002, T003 (harness + publish for the warm-load test).
- **US2 (Phase 4)**: Depends on T002 (Lighthouse measurement). Does not touch publish.py or the worker.
- **US3 (Phase 5)**: Depends on T003 (same file publish.py, sequential). T014 runs parallel to T015.
- **US4 (Phase 6)**: Depends on all stories.
- **Polish (Phase 7)**: Depends on all stories.

### User Story Dependencies

- **US1**: Independent of US2 and US3 file sets (worker + deploy script vs main.js/Makefile vs publish.py).
- **US2**: Independent of US1 and US3. Its only shared dependency is the harness (T002).
- **US3**: Shares publish.py with the foundational hashing engine (T003), which must land first. T014 (favicon) is independent.
- **US4**: Integration phase. Nothing else can verify the deployed site.

### Within Each User Story

- US1: T004 and T005 in parallel, then T006.
- US2: T007 and T008 in parallel. T009 after T008. T010 and T011 in parallel after T009. T012 after T010. T013 after T012.
- US3: T014 and T015 in parallel. T016 after T015.
- US4: T017 and T018 in parallel. T019 after both. T020 after T019.

### Parallel Opportunities

- T002 and T003 run in parallel (foundational, different files).
- US1, US2, and US3 run in parallel after foundational (different files, except T015 which follows T003).
- T004 ∥ T005, T007 ∥ T008, T010 ∥ T011, T014 ∥ T015, T017 ∥ T018.

### Parallel Example: US2

```text
# Launch together:
Task: "Add fadeDuration: 0 to the Map constructor in src/site/main.js"
Task: "Add -S 10 --simplify-only-low-zooms to the pmtiles-buildings target in Makefile"
# After the rebuild:
Task: "Add the parity check script tests/parity_check.py and run it"
Task: "Render before/after screenshots at z10-z18 and diff"
# Then:
Task: "Run Lighthouse 13.4.1 mobile on the rebuilt bundle"
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1 (baseline) and Phase 2 (foundational).
2. Complete US1 (caching). Validate warm-load transfer under 100 KB.
3. Complete US2 (main-thread). Validate TBT under 1.5 s.
4. **STOP VALIDATE**: run quickstart S1-S6, then deploy.
5. US3 and US4 follow in the same increment or the next one.

Rationale: US1 and US2 are both P1 and carry the audit's two critical findings. US1 is a one-line-class change with immediate repeat-visit value. US2 is the score driver. US3 is cheap and low-risk; US4 is the safety net around the deploy.

### Incremental Delivery

1. Baseline + foundation (harness, hashing).
2. US1: caching live. Repeat visits drop to under 100 KB.
3. US2: mobile score 67 to 85+, TBT under 1.5 s, parity gates green.
4. US3: first-load critical path.
5. US4: regression suite, deploy, edge verification, records update.

### Notes

- Run `make publish` and serve via nginx (127.0.0.1:8088) after each story that changes publish.py or src/site/.
- The geometry rebuild (T009) mutates only gitignored paths. It never touches `src/` or tracked data.
- The parity gates are the hard constraint on the simplification scale. Never trade visual parity for TBT.
- Record the edge-cache finding honestly (T019). If cf-cache-status stays MISS, apply the documented SC-004 fallback and note it in the records.
- Commit at every checkpoint (OR-004). Do not mix slices in one commit.
