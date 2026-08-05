---
description: "Task list for verify-tree-detection feature implementation"
---

# Tasks: Verify Tree Detection Quality

**Input**: Design documents `specs/008-verify-tree-detection/`
**Prerequisites**: plan.md (required), spec.md (required user stories), research.md, data-model.md, contracts/, quickstart.md
**Tests**: included — the plan's Testing section specifies pytest additions in `tests/pipeline/test_verify.py` (reproducibility, coverage, schema, report) and the quickstart scenarios depend on them. Write tests first, see them fail, then implement.
**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: run in parallel (different files, no dependencies)
- **[Story]**: user story the task belongs to (US1, US2, US3)
- File paths in every description
- Commit points per OR-004 (one commit per accepted slice) at each checkpoint

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization — verification artifact directory and the one external input.

- [ ] T001 Create `verification/` directory and `verification/README.md` (purpose, artifact list, attribution/license section for the district layer, link to `specs/008-verify-tree-detection/`)
- [ ] T002 Fetch Mannheim Stadtteil boundaries from the official GDI-MA service (discovery procedure in `research.md` R-2), reproject to EPSG:25832, verify 38 features with names and 3-digit codes, commit as `verification/stadtteile.geojson`, and record source URL, license (dl-de/by-2-0), and download date in `verification/README.md`
- [ ] T003 [P] Add `verification/patches/` to `.gitignore`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure in `src/pipeline/verify.py` — MUST complete before any user story.

- [ ] T004 Implement shared verification infrastructure in `src/pipeline/verify.py`: constants (`DEFAULT_SEED = 20260805`, value bands `0-10`/`10-30`/`30-100`, `PATCH_PX = 1024`, patch size 204.8 m, flag threshold 0.5, rating values `correct`/`over`/`under`), artifact paths (`verification/sample.jsonl`, `ratings.jsonl`, `notes.md`, `report.md`, `patches/`), workspace readers (DOP20 tiles from `mosaic/extract/` via `tiles.csv`, canopy mask `mosaic/canopy_prediction_mask.tif`, buildings frame from `tables/buildings.geojson` filtered on `has_value`), district loader for `verification/stadtteile.geojson`, and JSONL schema validators for sample and rating records (per `contracts/verify-sample.md` and `contracts/verify-ratings.md`)

**Checkpoint**: Foundation ready — user story implementation can begin. Commit per OR-004.

## Phase 3: User Story 1 - Owner Carries Out a Structured Visual Inspection (Priority: P1) 🎯 MVP

**Goal**: A documented, reproducible sample of 100 patch centers, stratified by district and value band, written to `verification/sample.jsonl` — the inspection's sampling frame.

**Independent Test**: `verify-sample` run twice with the same seed produces byte-identical `verification/sample.jsonl` (quickstart Scenario 1).

### Tests User Story 1 (fail first)

- [ ] T005 [P] [US1] Write reproducibility + coverage tests in `tests/pipeline/test_verify.py`: same seed + same workspace → byte-identical sample file; 100 records; every district with buildings present with ≥ 2 patches; band counts match the documented allocation (largest remainder); schema validity of every record (see `contracts/verify-sample.md` invariants)

### Implementation User Story 1

- [ ] T006 [US1] Implement `select_sample()` in `src/pipeline/verify.py`: sampling frame from buildings (`has_value`, EPSG:25832), district assignment via point-in-polygon against `verification/stadtteile.geojson`, district × band allocation (proportional to building count, floor 2 per district, largest remainder), seeded random draw from building centroids without replacement, coverage check against the imagery extent with deterministic `resampled` replacement, `degeneracy` placeholder field (depends on T004)
- [ ] T007 [US1] Add `verify-sample` subcommand to `src/pipeline/cli.py` (wrapped by the existing RSS-gated runner, event-logged, exit 0 on success / 1 on validation failure, writes `verification/sample.jsonl`)

**Checkpoint**: US1 fully functional and testable independently. Commit per OR-004.

## Phase 4: User Story 2 - Owner Sees Findings Per District (Priority: P1)

**Goal**: Render the 1024×1024-px review PNGs with the production canopy-mask overlay into `verification/patches/` so the owner can inspect and rate; degeneracy is detected and recorded.

**Independent Test**: `verify-render` produces one PNG per sample patch (minus `no-imagery`), each 1024×1024 px with the mask overlay visible, and updates `degeneracy` in `verification/sample.jsonl` (quickstart Scenario 2).

### Tests User Story 2 (fail first)

- [ ] T008 [P] [US2] Write rendering tests in `tests/pipeline/test_verify.py` using a small fixture workspace (tmp dir with synthetic DOP20 tiles + binary mask + buildings): PNG count matches sample, PNG dimensions 1024×1024, deterministic output for identical input, `degeneracy` classification (`no-imagery` / `empty-mask` / `full-mask` / `null`), and no full-tile reads (windowed reads only — assert via rasterio windowing on oversized fixture tiles)

### Implementation User Story 2

- [ ] T009 [US2] Implement `render_patches()` in `src/pipeline/verify.py`: for each sample patch, windowed rasterio read of the overlapping DOP20 tile(s), composite the binary canopy mask at 50 % alpha in a distinct color over the RGB imagery, write `verification/patches/<patch_id>.png`, classify and record degeneracy (no imagery coverage, empty mask, full mask), and persist the updated `degeneracy` field back into `verification/sample.jsonl` (depends on T004, T006)
- [ ] T010 [US2] Add `verify-render` subcommand to `src/pipeline/cli.py` (wrapped, event-logged, read-only over the workspace, exit 0/1)

**Checkpoint**: US2 complete — the inspection loop (sample → render) works. Commit per OR-004.

## Phase 5: User Story 3 - Owner Keeps the Findings in the Repository (Priority: P2)

**Goal**: The ratings file and the generated `verification/report.md` — the durable evidence in the repository. The published map/site stays untouched.

**Independent Test**: `verify-report` on a valid ratings file produces a complete report per `contracts/verify-report.md`; on an invalid ratings file it exits 1 (quickstart Scenario 4).

### Tests User Story 3 (fail first)

- [ ] T011 [P] [US3] Write report-generation tests in `tests/pipeline/test_verify.py` from fixture sample + ratings + notes: report contains method, overall counts, per-district table covering all 38 districts, flagged districts exactly those with correct share < 50 %, all five limitation classes non-empty, comparison section present; invalid ratings (missing patch, unknown rating, unrated patch) → exit 1 (per `contracts/verify-report.md` invariants)

### Implementation User Story 3

- [ ] T012 [US3] Implement `generate_report()` in `src/pipeline/verify.py`: validate ratings against sample (every non-`no-imagery` patch rated exactly once, rating ∈ {correct, over, under}), compute overall rating counts, build the per-district table (n, correct/over/under, assessment trustworthy/overstated/understated/inconclusive per n ≥ 5 rule, FLAGGED when correct share < 50 %), merge `verification/notes.md` verbatim for the comparison and limitations sections, emit all five disclosure classes (counts or explicit "none observed"), write `verification/report.md` in the German section structure of `contracts/verify-report.md` (depends on T004, T006)
- [ ] T013 [US3] Add `verify-report` subcommand to `src/pipeline/cli.py` (wrapped, event-logged, exit 0/1)
- [ ] T014 [US3] Create `verification/notes.md` template with the comparison section (model author's Erlangen→Bamberg warning vs. Mannheim findings, qualitative) and the limitations writeup section, matching the report contract's structure

**Checkpoint**: US3 complete — report generated; all three stories independently testable. Commit per OR-004.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Regression safety, documentation, and the actual verification run.

- [ ] T015 [P] Update `DEVELOPMENT.md` to document the three `verify-*` subcommands, the `verification/` directory, and the district layer attribution
- [ ] T016 [P] Run the full existing suite (`pytest tests/`) and the zero-change gate: `git status --porcelain` shows no diffs in `dist-assets/`, `src/site/`, `workers/`, or workspace files; `make check-public` stays clean (quickstart Scenario 5)
- [ ] T017 Execute the verification end to end and commit the evidence: `verify-sample` → `verify-render` → owner rates all patches into `verification/ratings.jsonl` (criteria in `contracts/verify-ratings.md`, re-inspect every 10th patch) → write `verification/notes.md` → `verify-report`; commit `sample.jsonl`, `ratings.jsonl`, `notes.md`, `report.md`
- [ ] T018 Run quickstart Scenarios 1–6 and record results in the report's validation notes

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately (T001→T002 sequential; T003 parallel)
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3+)**: depend on Foundational; executed sequentially in priority order (US1 → US2 → US3) because US2 renders US1's sample and US3 consumes both
- **Polish (Final Phase)**: depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: starts after Foundational; no story dependencies
- **User Story 2 (P1)**: renders the sample produced by US1; independently testable on a fixture workspace
- **User Story 3 (P2)**: consumes sample + ratings from US1/US2 plus the owner's notes; report generation is independently testable on fixtures

### Within Each User Story

- Tests written first and failing before implementation (T005, T008, T011)
- Shared infrastructure before story code (T004 before T006/T009/T012)
- Subcommand registration (T007, T010, T013) after the function it dispatches to

### Parallel Opportunities

- T003 (gitignore) runs parallel with T001/T002
- Story tests (T005, T008, T011) are [P] — separate fixtures, one shared test file (sequential within the file, but independently writable)
- T015/T016 are [P] in the polish phase
- The three story implementations (T006+T007, T009+T010, T012+T013+T014) are independent modules of `verify.py` + separate registrations in `cli.py`; cli.py edits are sequential to avoid same-file conflicts

## Parallel Example: User Story 1

```bash
# Test task (fail first, then implement):
Task: "Write reproducibility + coverage tests in tests/pipeline/test_verify.py"
# Implementation (after tests fail):
Task: "Implement select_sample() in src/pipeline/verify.py"
Task: "Add verify-sample subcommand to src/pipeline/cli.py"
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1: Setup (district layer + verification dir)
2. Complete Phase 2: Foundational (`verify.py` infrastructure)
3. Complete Phase 3: User Story 1 (reproducible sample)
4. **STOP VALIDATE**: re-run `verify-sample`, diff against the first run, run T005 tests
5. The practical MVP is US1 + US2 together: a sample is only evidence once patches exist to inspect; US3 turns the inspection into the report

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 (sample) → reproducible sampling proven
3. US2 (render) → inspection loop possible; owner can start reviewing PNGs
4. US3 (report) → durable evidence; verification complete and committed
5. Each story adds value without breaking the previous ones; the published map is never touched

## Notes

- [P] tasks = different files, no dependencies
- [Story] labels trace tasks to spec user stories
- Verification runs CPU-only, never touches the model (OR-003), never writes to the archived workspace (read-only), never writes to published artifacts (FR-005/FR-010)
- OR-005: `verification/patches/` stays gitignored; all committed files are small
- Commit at every checkpoint (OR-004): Setup, Foundation, US1, US2, US3, Polish
