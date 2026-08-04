---
description: "Task list: Mannheim Tree-Cover Parity"
---

# Tasks: Mannheim Tree-Cover Parity

**Branch**: `001-replicate-mannheim-tree-cover`

**Input**: Design documents in `specs/001-replicate-mannheim-tree-cover/`: `plan.md` (required), `spec.md` (required, user stories with priorities), `research.md`, `data-model.md`, `contracts/` (`cli.md`, `manifest.md`, `map-style.md`, `pmtiles-sources.md`, `static-bundle.md`, `README.md`), `quickstart.md`.

**Prerequisites**: Python 3.11, `tippecanoe` ≥ 2.x on `$PATH`, the mannheim workspace at `/home/mainuser/Desktop/mannheim/workspace/mannheim` (read-only).

**Tests**: Requested. The spec's "User Scenarios & Testing" section is mandatory and `plan.md` defines the suites: `tests/acceptance/*` (per-FR-021 checks), `tests/pipeline/test_values_recalc.py` (SC-004), `tests/pipeline/test_image_sanity.py` (SC-005), `tests/pipeline/test_rss.py` (OR-001/SC-009), and `tests/frontend/` smoke checklists (quickstart Scenarios 1–3). All tests are written FIRST and must FAIL before implementation of their story.

**Organization**: Tasks are grouped by user story so each story is independently implementable and testable. One commit per slice/milestone via `make commit-slice` / `make commit-milestone` (OR-004).

## Format

- `[ID] [P?] [Story] Description with file path`
- `[P]`: run in parallel (different files, no dependencies on incomplete tasks)
- `[Story]`: user story the task belongs to (US1..US4). Setup, Foundational, and Polish carry no label.

## Path Conventions

- Repo root: `src/pipeline/` (offline data CLI), `src/site/` (static frontend), `tests/` (`acceptance/`, `pipeline/`, `frontend/`), `Makefile`, `.gitignore`, `artifacts.manifest.json`, `tiles.csv`.
- Published output lands in `dist/` (gitignored, OR-005).
- Rasters, PMTiles, and GeoJSON > 50 MiB never enter git; they are recorded in `artifacts.manifest.json` (OR-005).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [X] T001 Create project structure per `plan.md`: `src/pipeline/` (with `__init__.py`), `src/site/`, `src/site/vendor/`, `tests/acceptance/`, `tests/pipeline/`, `tests/frontend/`, `validation/`, `dist/` at repo root
- [X] T002 Initialize Python 3.11 project in `pyproject.toml` (deps: rasterio, numpy, scipy, shapely, pyproj, pyogrio, pmtiles, click; dev: pytest) and add `make bootstrap` target (create venv, install deps, ensure branch `001-replicate-mannheim-tree-cover`, run the acceptance suite once)
- [X] T003 [P] Create `.gitignore` per OR-005/R-012 (exclude `*.tif`, `*.pmtiles`, `*.geojson` > 50 MiB, `dist/`, `.venv/`, `__pycache__/`)
- [X] T004 [P] Create Makefile commit targets per R-013/OR-004 in `Makefile` (`commit-spec`, `commit-plan`, `commit-slice`, `commit-milestone`: add expected files only, refuse unstaged changes, append `Spec-NN:` / `Plan-NN:` / `Slice-NN:` / `Milestone-NN:` tag)
- [X] T005 [P] Vendor pinned ESM builds `maplibre-gl.js` and `pmtiles.js` into `src/site/vendor/` (no build tool, no framework; record versions in repo README)
- [X] T006 [P] Add `make check-prereqs` target (Python 3.11, `tippecanoe` ≥ 2.x on PATH, mannheim workspace readable)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story starts.

- [X] T007 Create CLI skeleton in `src/pipeline/cli.py` (click entrypoint; subcommands `accept`, `publish`, `values`, `runpod-infer`; exit codes per `contracts/cli.md`: 0 success, 1 acceptance/input failure, 2 RunPod gate, 3 RSS > 12 GiB, 4 GPU attempted)
- [X] T008 Implement common subcommand behavior in `src/pipeline/cli.py` (per-invocation row in `validation/event.log.jsonl` with ts, subcommand, rss_peak_bytes, gpu_used, exit_code, inputs; `/usr/bin/time -v` RSS wrapper exits 3 on > 12 GiB; input acceptance short-circuit on `pending`/`fail` (OR-001/OR-002)
- [X] T009 [P] Implement `artifact_manifest.py` in `src/pipeline/artifact_manifest.py` (read/write `artifacts.manifest.json` per `contracts/manifest.md`: path, size_bytes, sha256, source, license, extent, resolution, completeness, lineage, acceptance, checks, invalidates; pass/fail/pending state machine; `fail` cascades to `invalidates`)
- [X] T010 [P] Implement `io.py` in `src/pipeline/io.py` (windowed raster reads via rasterio, GeoJSON writer, PMTiles writer; never loads a full city raster (OR-002)
- [X] T011 [P] Implement `boundary.py` in `src/pipeline/boundary.py` (load official boundary E-001: bbox + area, EPSG:25832; derive buffered boundary E-002 = boundary ∪ 60 m exterior, marked analysis-only, never published (FR-006/FR-007)

**Checkpoint**: Foundation ready. User story implementation can begin in parallel.

---

## Phase 3: User Story 1: View Mannheim Color Map (Priority: P1) 🎯 MVP

**Goal**: A public static dark map that opens with the full Mannheim boundary, obscures everything outside it, and colors every Mannheim building with the reference palette, plus legend, navigation controls, attribution, and a 360 px-compatible layout.

**Independent Test**: `python -m http.server -d dist`, open a clean browser. Verify: initial view fits the boundary with minimal padding, north up; base map outside the boundary is black; buildings use the reference palette at 75% opacity with thin gray outlines; legend labels `0`, `15`, `30`, `50`, `100`; zoom/north controls work; attribution lists LGL (`dl-de/by-2-0`), basemap.de, CityTreeCover; reload at 360 px keeps legend and controls usable (quickstart.md Scenario 1).

### Tests User Story 1 (write FIRST, fail before implementation)

⚠️ **NOTE: Write tests FIRST, FAIL before implementation**

- [X] T012 [P] [US1] Write style contract test in `tests/acceptance/test_style.py` (load `src/site/style.json` with a MapLibre style parser; assert the five layers, verbatim palette stops 0/12/24/24.08/32/40/48/80, legend labels, JSON round-trip (per `contracts/map-style.md`)
- [X] T013 [P] [US1] Write US1 frontend smoke checklist in `tests/frontend/smoke_us1.md` (quickstart Scenario 1 pass criteria: title `Baumfläche`, boundary fitBounds, dark outside-mask, palette/outlines, controls, attribution, 360 px layout)

### Implementation User Story 1

- [X] T014 [P] [US1] Create `index.html` in `src/site/index.html` (`<title>Baumfläche</title>`; `#map` fills viewport; `#legend` with German description and labels `0`, `15`, `30`, `50`, `100`; `#baeume` button labelled `Bäume`; `#attribution`; loads `style.css` then ESM `main.js` (FR-012/FR-013)
- [X] T015 [P] [US1] Create `style.css` in `src/site/style.css` (dark theme: page `#0e0e0e`, map `#000`, text `#fff`, outlines `#888`; `@media (max-width: 480px)` collapses legend to a bottom strip and stacks controls (FR-018)
- [X] T016 [P] [US1] Create `style.json` in `src/site/style.json` per `contracts/map-style.md` (sources: basemap.de raster, `pmtiles://buildings.pmtiles`, `pmtiles://trees.pmtiles`, boundary geojson; layers bottom→top: basemap, outside-mask `#000` opacity 1, buildings-fill `interpolate(linear, ['get','value'], 0 '#ffd524', 12 '#e6854a', 24 '#a97e65', 24.08 '#0674aa', 32 '#1db6ff', 40 '#39c2ff', 48 '#56ceff', 80 '#6ad4ff')` opacity 0.75 with `case` fallback `#444`/0.4 for `has_value == false`, buildings-line `#555` width 0.5, trees-fill `#39C43D` opacity 0.75 `visibility: 'none'` (FR-003/FR-009/FR-010/FR-011/FR-015)
- [X] T017 [US1] Implement `buildings.py` in `src/pipeline/buildings.py` (assert source `LGL ALKIS Hausumringe`, CRS EPSG:25832, feature_count 93024; clip to buffered boundary; drop duplicates by stable id; emit only `in_boundary == true` (FR-004/SC-003; reads the accepted `tables/buildings.geojson`, never regenerates it (FR-022)
- [X] T018 [US1] Implement `values.py` in `src/pipeline/values.py` (per-building value = mean canopy fraction in a 60 m disc: `scipy.signal.fftconvolve` with a 300 px circular kernel over the binary canopy mask, chunked 1000 px tiles with reflective padding, footprint rasterized to the mask grid; `value` in [0,100] or `null`; `value_str` two decimals; `has_value`; `completeness` (FR-005/FR-008/FR-009/OR-002, R-001/R-006; depends on T017)
- [X] T019 [US1] Add `pmtiles-buildings` target to `Makefile` (tippecanoe recipe per `contracts/pmtiles-sources.md`: `--name buildings --layer buildings --minimum-zoom 12 --maximum-zoom 18 --base-zoom 14 --drop-densest-as-needed --extend-zooms-if-still-dropping --read-parallel --output=buildings.pmtiles buildings.geojson`)
- [X] T020 [US1] Implement `publish.py` in `src/pipeline/publish.py` (refuse if any required artifact is `pending`/`fail`; clip every accepted layer to the official boundary (FR-007; emit `dist/` bundle per `contracts/static-bundle.md`: index.html, style.css, main.js, vendor/, style.json, PMTiles, boundary.geojson, public manifest.json, attribution.html; stream inputs, never a full raster (OR-002; write the PublishedMap record)
- [X] T021 [US1] Implement `main.js` bootstrap in `src/site/main.js` (ESM; register the `pmtiles` protocol; `fitBounds` on the boundary bbox with `padding: 24, bearing: 0, pitch: 0, duration: 0`; add `NavigationControl` with `showCompass: true`; load outside-mask + buildings layers (FR-001/FR-002/FR-003/FR-017; depends on T016)
- [X] T022 [US1] Create `attribution.html` in `src/site/attribution.html` and wire the `AttributionControl` in `main.js` (LGL `Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0`, basemap.de, CityTreeCover MIT (FR-019; depends on T021)

**Checkpoint**: US1 complete. Run `make publish`, then `tests/frontend/smoke_us1.md`. Full-color rendering additionally requires an accepted canopy mask (see US4 / RunPod gate). The quarantine of the failed prior mask is the intended FR-021/FR-023 behavior, not a defect.

---

## Phase 4: User Story 2: Inspect a Building Value (Priority: P2)

**Goal**: Hovering a building shows a selection pointer; clicking opens a compact popup with the two-decimal value; buildings without a valid value are identified as unavailable, never as zero.

**Independent Test**: Click known low/middle/high buildings from the accepted data; popup values match with two decimal places; click an unavailable building. The popup reads `–` and the fill is the gray unavailable color; `pytest tests/pipeline/test_values_recalc.py` passes 100/100 within 1 percentage point (SC-004) (quickstart.md Scenario 2).

### Tests User Story 2 (write FIRST, fail before implementation)

⚠️ **NOTE: Write tests FIRST, FAIL before implementation**

- [X] T023 [P] [US2] Write value recalculation test in `tests/pipeline/test_values_recalc.py` (sample 100 random buildings, recompute the 60 m mean independently, assert ≤ 1 percentage point disagreement (SC-004)
- [X] T024 [P] [US2] Write US2 frontend smoke checklist in `tests/frontend/smoke_us2.md` (pointer cursor on hover; popup shows two decimals; unavailable popup reads `–`; quickstart Scenario 2 pass criteria)

### Implementation User Story 2

- [X] T025 [US2] Implement building popup in `src/site/main.js` (`click` on buildings-fill opens a compact MapLibre `Popup` with the feature's `value_str`; a null `value_str` shows `–` (FR-008/FR-009/FR-014)
- [X] T026 [US2] Implement hover pointer in `src/site/main.js` (`mousemove` over buildings-fill sets `canvas.style.cursor = 'pointer'` (FR-014; depends on T025, same file)

**Checkpoint**: US2 complete and independently testable.

---

## Phase 5: User Story 3: Toggle Detected Tree Cover (Priority: P3)

**Goal**: A `Bäume` button toggles the detected tree layer. It starts hidden, renders flat `#39C43D` at 75% opacity when active, never moves the camera, and a failed tree load never blocks the buildings layer.

**Independent Test**: On load the tree layer is hidden. Click `Bäume`. Flat green areas appear at 75% opacity. The camera (`map.getCenter()`, `map.getZoom()`, `map.getBearing()`, `map.getPitch()`) stays unchanged. Click again. The layer disappears and the camera stays unchanged. `pytest tests/pipeline/test_image_sanity.py` passes ≥ 17/20 crops (SC-005) (quickstart.md Scenario 3).

### Tests User Story 3 (write FIRST, fail before implementation)

⚠️ **NOTE: Write tests FIRST, FAIL before implementation**

- [X] T027 [P] [US3] Write image sanity test in `tests/pipeline/test_image_sanity.py` (20 distributed crops of the accepted canopy mask; ≥ 17/20 distinguish canopy from roofs/roads/water (SC-005)
- [X] T028 [P] [US3] Write US3 frontend smoke checklist in `tests/frontend/smoke_us3.md` (hidden on load; flat green `#39C43D` on toggle; camera unchanged; quickstart Scenario 3 pass criteria)

### Implementation User Story 3

- [X] T029 [US3] Implement `trees.py` in `src/pipeline/trees.py` (polygonize the accepted canopy mask with `rasterio.features.shapes`; clip to the official boundary (FR-007; stable ids `tree-<n>`; `canopy_pixel_count`; `source: accepted_canopy_mask` (E-004; depends on T011)
- [X] T030 [US3] Add `pmtiles-trees` target to `Makefile` (tippecanoe recipe per `contracts/pmtiles-sources.md`: `--name trees --layer trees --minimum-zoom 12 --maximum-zoom 18 --base-zoom 14 --drop-densest-as-needed --extend-zooms-if-still-dropping --read-parallel --output=trees.pmtiles canopy_polygons.geojson`)
- [X] T031 [US3] Implement `Bäume` toggle in `src/site/main.js` (trees-fill `visibility: 'none'` on load; click flips `setLayoutProperty('visibility', ...)` only (camera untouched, FR-016); wrap the trees PMTiles load in try/catch, console warning on failure, buildings keep rendering (FR-020; depends on T016 style.json)

**Checkpoint**: US3 complete and independently testable.

---

## Phase 6: User Story 4: Reuse Prior Work Safely (Priority: P4)

**Goal**: Every candidate artifact passes the five FR-021 checks before reuse; accepted artifacts are reused (never re-downloaded or regenerated); a failed derived artifact invalidates only its dependents; GPU work pauses and requests RunPod; large files stay out of git and are recorded in the manifest.

**Independent Test**: `python -m src.pipeline.cli accept`. The manifest reports per-artifact `pass`/`fail`/`pending`; the canopy mask is `fail` (0.48% completeness) and cascades to `buildings.geojson` + `trees.pmtiles` `pending`; accepted inputs (boundary, buildings, imagery) stay `pass` with zero repeat downloads; `runpod-infer` exits 2 with `STOP — request RunPod capacity` when `MANNHEIM_RUNPOD_ENDPOINT` is unset; `git status` shows no `*.tif` / `*.pmtiles` / large `*.geojson` (quickstart.md Scenario 4).

### Tests User Story 4 (write FIRST, fail before implementation)

⚠️ **NOTE: Write tests FIRST, FAIL before implementation**

- [X] T032 [P] [US4] Write boundary acceptance test in `tests/acceptance/test_boundary.py` (five FR-021 checks: source LGL `dl-de/by-2-0`, extent vs boundary, resolution n/a, completeness 1.0, lineage recorded)
- [X] T033 [P] [US4] Write buildings acceptance test in `tests/acceptance/test_buildings.py` (source/crs/count assertions; feature count exactly 93,024 (SC-003; no outside, synthetic, or duplicate buildings (FR-004)
- [X] T034 [P] [US4] Write imagery acceptance test in `tests/acceptance/test_imagery.py` (460 tiles from `mosaic/extract/dop20rgb_*.tif`; sidecar asserts `Bodenpixelgroesse == 0.2` and CRS 25832; completeness inside the buffered boundary ≥ 0.95 (R-002)
- [X] T035 [P] [US4] Write canopy acceptance test in `tests/acceptance/test_canopy.py` (completeness 0.48 < 0.95 threshold → `fail`; `invalidates: ["buildings.geojson", "trees.pmtiles"]`; asserts the baseline failure state per spec evidence)
- [X] T036 [P] [US4] Write values acceptance test in `tests/acceptance/test_values.py` (value in [0,100] or null; value_str two decimals; has_value consistency (FR-008/FR-009)
- [X] T037 [P] [US4] Write trees acceptance test in `tests/acceptance/test_trees.py` (in-boundary only (FR-007; source `accepted_canopy_mask` lineage)
- [X] T038 [P] [US4] Write manifest state-machine test in `tests/acceptance/test_manifest.py` (`pass` terminal; `fail` cascades to `invalidates` → `pending`; independent accepted inputs stay `pass`; no re-generation of `pass` artifacts (FR-022/FR-023/SC-010)
- [X] T039 [P] [US4] Write RSS/GPU gate test in `tests/pipeline/test_rss.py` (`/usr/bin/time -v` per subcommand; peak RSS ≤ 12 GiB; `gpu_used` false; local `runpod-infer` without endpoint exits 2 (OR-001/OR-003/SC-009)

### Implementation User Story 4

- [X] T040 [P] [US4] Implement `acceptance.py` in `src/pipeline/acceptance.py` (five FR-021 checks: source attribution, extent vs boundary, resolution/GSD, completeness ≥ 0.95, lineage input-hash; deterministic and idempotent; metadata-only reads, never full rasters (OR-002)
- [X] T041 [US4] Implement `accept` subcommand in `src/pipeline/cli.py` (re-validate every artifact in `artifacts.manifest.json`, refresh the manifest, print per-artifact `pass`/`fail`/`pending`, exit 0 if all pass-able artifacts pass else 1; the gate before every `publish`; depends on T040)
- [X] T042 [US4] Create `canopy.py` in `src/pipeline/canopy.py` (contract module with `requires_runpod: true` marker; the local pipeline refuses to invoke the model (OR-003); existing `deepLabV3plus-resnet34` weights only, no new labels, no training (FR-024)
- [X] T043 [US4] Implement `runpod-infer` subcommand in `src/pipeline/cli.py` (writes `canopy_mask.tif` + `canopy_mask.json`; refuses unless `MANNHEIM_RUNPOD_ENDPOINT` is set, prints `STOP — request RunPod capacity`, exits 2 (FR-025/OR-003; depends on T042)
- [X] T044 [P] [US4] Create seed `artifacts.manifest.json` at repo root from the mannheim workspace inventory (boundary/imagery/buildings `pass` with checks ok; canopy-mask `fail` with completeness 0.48 and `invalidates: ["buildings.geojson", "trees.pmtiles"]`; every > 50 MiB file recorded with path, size, sha256, source (OR-005; per `contracts/manifest.md` example)
- [X] T045 [P] [US4] Create `tiles.csv` at repo root (460-row tile index derived from `mosaic/extract/`, verified against the `2026.01/meta.json` tile count)
- [X] T046 [P] [US4] Add `make check-or005` target to `Makefile` (assert no `*.tif` / `*.pmtiles` / `*.geojson` > 50 MiB tracked in git; assert every excluded file has path, size, sha256, and source in the manifest (OR-005)

**Checkpoint**: US4 complete. Acceptance suite green, manifest reflects the quarantine, RunPod gate verified.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [X] T047 Run `quickstart.md` end-to-end (Scenarios 1–4), record results in `validation/event.log.jsonl`, and fix any failures found
- [X] T048 [P] Write repo `README.md` (setup via `make bootstrap`, pipeline subcommands, publish + static hosting, tippecanoe requirements; preserve the reference CityTreeCover MIT notice per spec Dependencies)
- [X] T049 Code cleanup: extract shared validation/IO helpers, remove duplication across `src/pipeline/` modules; re-run the acceptance suite
- [X] T050 Verify the performance budget: `dist/` < 50 MiB; initial map usable ≤ 10 s on a 25 Mbps / 50 ms link; ≥ 95% of interactions ≤ 2 s (SC-008); PMTiles sizes recorded in the manifest
- [X] T051 [P] Verify the published bundle carries no secrets, analytics, or telemetry and no third-party scripts beyond the vendored libs (FR-001 out-of-scope compliance); add a CSP `meta` tag to `index.html` if not present
- [X] T052 Create the final milestone commit via `make commit-milestone` (OR-004)

**Checkpoint**: All user stories complete, quickstart green, milestone committed.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Start immediately
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories
- **User Stories (Phases 3–6)**: Depend on Foundational. Proceed in parallel (if staffed) or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational only. No cross-story dependencies.
- **User Story 2 (P2)**: Depends on US1 (buildings layer + `value_str` fields from `values.py`)
- **User Story 3 (P3)**: Depends on US1 (`style.json` trees-fill layer, `main.js` bootstrap); real-data render additionally needs an accepted canopy mask (US4)
- **User Story 4 (P4)**: Depends on Foundational only. Independent of US1–US3. Its `accept` gate and RunPod output unblock real publication.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Contract/model files before services; services before publish/bootstrap
- Story complete and smoke-checked before the next priority begins

### Parallel Opportunities

- **Setup**: T003, T004, T005, T006 run in parallel
- **Foundational**: T009, T010, T011 run in parallel (after T007 → T008)
- **US1**: tests T012 + T013 parallel; assets T014, T015, T016, T017 parallel; then T018 → T019 → T020 → T021 → T022 sequential
- **US2**: tests T023 + T024 parallel
- **US3**: tests T027 + T028 parallel; T029 → T030 sequential; T031 after US1 `style.json`
- **US4**: tests T032..T039 all parallel (8-way); T040 → T041 sequential; T042 → T043 sequential; T044, T045, T046 parallel
- **Polish**: T048, T051 parallel

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together:
Task: "Write style contract test in tests/acceptance/test_style.py"
Task: "Write US1 frontend smoke checklist in tests/frontend/smoke_us1.md"
# Launch all US1 asset/model files together:
Task: "Create index.html in src/site/index.html"
Task: "Create style.css in src/site/style.css"
Task: "Create style.json in src/site/style.json"
Task: "Implement buildings.py in src/pipeline/buildings.py"
```

## Parallel Example: User Story 4

```bash
# Launch all US4 tests together:
Task: "Write boundary acceptance test in tests/acceptance/test_boundary.py"
Task: "Write buildings acceptance test in tests/acceptance/test_buildings.py"
Task: "Write imagery acceptance test in tests/acceptance/test_imagery.py"
Task: "Write canopy acceptance test in tests/acceptance/test_canopy.py"
Task: "Write values acceptance test in tests/acceptance/test_values.py"
Task: "Write trees acceptance test in tests/acceptance/test_trees.py"
Task: "Write manifest state-machine test in tests/acceptance/test_manifest.py"
Task: "Write RSS/GPU gate test in tests/pipeline/test_rss.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL: blocks all stories)
3. Complete Phase 3: User Story 1 (style contract test fails → assets → buildings → values → PMTiles → publish → frontend bootstrap → attribution)
4. **STOP VALIDATE**: `make publish`, serve `dist/`, run `tests/frontend/smoke_us1.md`
5. **Data gate note**: full-color publication additionally requires an accepted canopy mask. The prior mask fails (0.48% completeness), so its dependents stay `pending` until the owner-approved RunPod inference (T042/T043) produces a replacement. This quarantine is the intended FR-021/FR-023 behavior, not a defect. The pipeline code, acceptance suite, and smoke checklists are fully deliverable and testable now.

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. User Story 1 → test independently → demo (subject to the canopy gate)
3. User Story 2 → popup + recalculation test → demo
4. User Story 3 → tree toggle + image sanity → demo
5. User Story 4 → acceptance machinery + RunPod gate. Once the RunPod output is accepted, run `values` and `publish` for the full published map

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Once Foundational is done: Developer A (US1) and Developer B (US4) start immediately; US2 and US3 follow US1
3. Stories integrate independently. Run `make commit-slice` after each

---

## Notes

- `[P]` tasks = different files, no dependencies
- `[Story]` label maps each task to its user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit each logical group (OR-004)
- Stop at every checkpoint and validate the story independently
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence

---

## Phase 8: Convergence

**Purpose**: Close gaps found by the convergence assessment between the spec/plan/tasks and the implemented codebase.

- [X] T053 Verify and record the SC-008 performance budget: serve `dist/` on a throttled 25 Mbps / 50 ms link and measure time-to-first-usable-map and interaction latency; reconcile the 162 MB dist bundle (trees.pmtiles 76 MB, buildings.geojson 54 MB, buildings.pmtiles 32 MB) with the plan's < 50 MiB budget by documenting the PMTiles range-request rationale or trimming the bundle; record PMTiles sizes including `buildings.pmtiles` in the manifest per SC-008, plan: T050 (partial)
- [X] T054 Refresh `quickstart.md` Scenario 4 and the quarantine notes in `tests/frontend/smoke_us1.md`, `smoke_us2.md`, `smoke_us3.md` to describe the unblocked acceptance state (canopy mask `pass`, buildings and trees published to `dist/`) instead of the lifted quarantine per plan: quickstart Scenario 4, T047 (partial)
- [X] T055 Add an automated test asserting `tiles.csv` indexes every `mosaic/extract/` tile with correct grid coordinates and matches the manifest `tile_count`; reconcile the plan's 460-tile reference with the accepted 302-tile extract per T045 (partial)

**Convergence record (T053-T055)**: SC-008 measured on a throttled 25 Mbps / 50 ms link (nginx + CDP): first usable map 2.5 s (budget 10 s), interactions 80-211 ms (budget 2 s), record in `validation/perf-budget.json`. Gap found and fixed: MapLibre does not render vector sources below `minzoom`, so `--minimum-zoom 12` left the FR-002 initial fitBounds view (z10.9) without buildings; both PMTiles regenerated at `--minimum-zoom 10` (contract `pmtiles-sources.md` updated). 460-vs-302 tile discrepancy reconciled (meta.json declares the full 460-tile LGL set; the accepted extract holds the 302 tiles intersecting the buffered boundary; `tiles.csv` indexes the 302, asserted by `tests/acceptance/test_tiles_csv.py`). Quarantine notes in `quickstart.md` and the smoke checklists refreshed to the unblocked state (canopy mask `pass`, buildings + trees published in `dist/`).
