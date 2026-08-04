# Implementation Plan: Mannheim Tree-Cover Parity

**Branch**: `001-replicate-mannheim-tree-cover` | **Date**: 2026-08-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/home/mainuser/Desktop/MATreeCover/specs/001-replicate-mannheim-tree-cover/spec.md`

**Source of truth**: The committed spec (`spec.md`) is authoritative. The
unfilled `.specify/memory/constitution.md` template is treated as having no
binding constraints; the binding constraints are the spec's functional
requirements (FR-001..FR-025) and operational constraints (OR-001..OR-005).
The mannheim workspace `/home/mainuser/Desktop/mannheim/workspace/mannheim` is
the reuse source per FR-021..FR-023.

- **Published map**: any static web server. No application server, no database, per the out-of-scope list.

Deliver a single static, German-language, dark-themed web map that renders
Mannheim buildings colored by their mean 60 m-radius tree-cover percentage,
with a `Bäume` toggle for the optional detected-tree layer. The published map
combines the official Mannheim boundary, the LGL ALKIS building set, an
accepted canopy mask, derived per-building values, and detected tree areas.
Every published artifact either passes an explicit acceptance check against
FR-021 or is regenerated once. The prior canopy result fails acceptance
(0.48% canopy pixels) and its downstream dependents are quarantined until
owner-approved RunPod inference produces a replacement. **Status update
(T053/T054)**: the owner-approved RunPod inference ran and the replacement
canopy mask passes acceptance (completeness 1.0); `values`, `trees`, and
`buildings.pmtiles` are accepted and the full bundle is published to
`dist/`. The quarantine described below is the historical baseline state.

## Technical Context

**Language/Version**: Python 3.11 (data pipeline, reuses the existing
mannheim workspace tooling); vanilla HTML + ESM JavaScript (frontend, no
- Published map: desktop and mobile browsers with German locale and ESM support. No application server or database.

**Primary Dependencies**:
- **Data pipeline** (Python): `rasterio`, `numpy`, `scipy.signal.fftconvolve`,
  `shapely`, `pyproj`, `fiona`/`pyogrio`, `pmtiles` (Python writer), `click`
  for the CLI. Reuses the libraries already exercised in
  `2026.01/meta.json` (`scipy.signal.fftconvolve`, 60 m / 300 px circular
  kernel, chunked 1000 px tiles).
- **Frontend** (JS, ESM from CDN): `maplibre-gl` (MapLibre GL JS, MIT) for
  rendering; `pmtiles` (MIT) for direct PMTiles reading; no build tool, no
  framework. Reuses CityTreeCover's MapLibre + PMTiles presentation pattern
  since the spec mandates the same dark map, legend, popup, and `Bäume` toggle.
- **Inference** (paused): existing model `deepLabV3plus-resnet34` weights
  retained from the mannheim workspace. No new training, no new labels
  (FR-024). RunPod execution only after the owner supplies capacity
  (FR-025 / OR-003).

**Storage**: File-based, no database. All published assets are static
files served over plain HTTP.
- Repository: code, contracts, manifests, small metadata JSON, the
  generated boundary clip, and a `tiles.csv` index. No raster, no PMTiles,
  no large GeoJSON committed (OR-005).
- Out-of-repo (workspace or release bundle): PMTiles, GeoJSON, rasters,
  and any other file > 50 MiB. Each excluded file is recorded in
  `artifacts.manifest.json` (path, size, sha256, source, acceptance state)
  per OR-005.

**Testing**:
- **Data acceptance** (Python, `pytest`): each candidate artifact gets a
  per-`FR-021` check — source attribution, extent vs. boundary, GSD / CRS
  for rasters, completeness (no gaps inside the buffered boundary),
  lineage (input hash referenced), and acceptance state.
- **Value recalculation** (Python, `pytest`): for 100 sampled buildings
  (SC-004), recompute the 60 m mean independently and assert agreement
  within one percentage point.
- **Image sanity** (Python, `pytest`): 20 image crops, threshold score
  ≥ 17/20 distinguish canopy from roofs/roads/water (SC-005).
- **Frontend smoke** (manual + browser, no test framework): load
  `index.html` against a local server, drive a scripted
  `playwright`-style run for the 4 user stories (color map, popup, tree
  toggle, mobile width). Automated browser tests are out of scope per
  spec ("static German presentation" — no analytics, no telemetry).
- **Performance** (manual): measure local pipeline peak RSS with
  `/usr/bin/time -v` (SC-009).

**Target Platform**:
- Local development and pipeline: Linux x86_64, 12 GiB RSS cap (OR-001).
  No GPU ever (OR-003).
- Published map: desktop and mobile browsers, German locale, ESM
  support. Static hosting (any static web server); no application
  server, no database (per out-of-scope: "User accounts,
  authentication, editing, analytics, databases, or application
  servers").

**Project Type**: Web application — frontend (static site) + offline
data-pipeline (CLI). No backend service.

**Performance Goals**:
- Time to first usable map ≤ 10 s on a 25 Mbps / 50 ms link (SC-008).
- ≥ 95% of interactions complete within 2 s (SC-008).
- Local pipeline jobs peak resident set ≤ 12 GiB (SC-009 / OR-001).
- No GPU job ever on the local machine (SC-009 / OR-003).

**Bundle-size budget (T053 reconciliation)**: SC-008 is a time budget,
not a byte budget. The `dist/` bundle is ~162 MB on disk
(`buildings.geojson` 54 MB, `buildings.pmtiles` 33 MB,
`trees.pmtiles` 78 MB, vendored libs ~1 MB), which exceeds the 50 MiB
figure that OR-005 applies to *git governance* (files > 50 MiB never
committed). The served payload is far smaller because the two vector
layers are PMTiles archives: the browser issues HTTP Range requests and
fetches only the header/directory plus the viewport's z10–13 tiles —
measured ~33 KB at first paint on a 25 Mbps / 50 ms link
(`validation/perf-budget.json`). The bundle is therefore not trimmed;
the range-request rationale is the budget compliance.

**Constraints**:
- 12 GiB RSS cap on every local job (OR-001).
- No loading a complete city raster or vector into memory (OR-002).
  Each job is chunked (1000 px tiles, matching
  `2026.01/meta.json`'s pipeline), streams inputs, and writes outputs
  incrementally.
- Static hosting via any static web server. No application server, no database, per the out-of-scope list.
  (OR-005).
- One commit per accepted specification, plan, implementation slice,
  and validation milestone (OR-004).
- No Label Studio, no new labels, no training, no fine-tuning (FR-024).
- Mannheim-only publication; no halo geometry, buildings, trees, or
  values outside the official boundary may appear (FR-007).
- Strict CityTreeCover parity for visible scope, palette, legend,
  popup, `Bäume` toggle, attribution.

**Scale/Scope**:
- 1 city, 1 release (no historical comparison).
- 93,024 building footprints (LGL ALKIS, per `2026.01/meta.json`).
- Imagery: `2026.01/meta.json` declares 460 tiles (full LGL DOP20 set for
  the region); the accepted workspace extract holds the 302 tiles
  intersecting the buffered boundary (1000 m × 1000 m, 0.2 m GSD).
  `tiles.csv` indexes the accepted 302 (T055).
- 1 static published map; desktop + mobile widths (FR-018).
- One 60 m-radius mean per building (FR-005); one flat-green tree
  layer (FR-015); one legend (FR-012); one `Bäume` button (FR-013).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution file is the unfilled template; no project-level
principles are ratified. The binding constitution is therefore the spec's
own requirements and operational constraints, which are reproduced
verbatim below as the gate.

### FR gates (must pass with documented evidence)

| ID | Requirement (paraphrased) | Plan evidence |
|---|---|---|
| FR-001 | Public map, no accounts | Static site, no auth, no DB. |
| FR-002 | Initial view = full boundary, north up | MapLibre `fitBounds` on the official boundary bbox with minimal padding; `bearing = 0`. |
| FR-003 | Obscure base map outside Mannheim | Mask layer in MapLibre with `fill-color: rgba(0,0,0,1)` covering everything outside the official boundary polygon; rendered above the base map. |
| FR-004 | Buildings = accepted official inventory only | `tables/buildings.geojson` is the LGL ALKIS Hausumringe source (per meta.json). Pipeline: assert source, clip to buffered boundary, drop duplicates, no synthetic buildings. |
| FR-005 | Value = mean 60 m-radius tree-cover % across footprint | `scipy.signal.fftconvolve` with a 300 px circular kernel (60 m / 0.2 m GSD) over the binary canopy mask, chunked 1000 px tiles (matches meta.json `neighbourhood` block). |
| FR-006 | 60 m exterior halo permitted, no wider | Pipeline reads imagery tiles intersected by `boundary ∪ boundary.buffer(60 m)` only; halo is never published. |
| FR-007 | Published map contains no halo geometry | All published layers (buildings, trees, mask) are clipped to the official boundary; halo computation stays in the pipeline's intermediate files, never copied into the static bundle. |
| FR-008 | Valid values 0–100%, 2 decimal places | Pipeline output formatted as a string with two decimals; values outside [0, 100] rejected as failures. |
- There is no application server, no database, and no API. The "backend" runs once on the maintainer's machine to produce static artifacts that the frontend loads.
| FR-010 | Reference palette, 75% opacity, thin gray outlines | Palette encoded as a MapLibre `interpolate` expression with the exact stops in the spec; `fill-opacity: 0.75`; line layer is `line-color: #555`, `line-width: 0.5`. |
| FR-011 | Interpolate between stops; ≥80% stays at last color | `interpolate` expression with `linear` interpolation; the final color is the value at the 80% stop — MapLibre clamps at the last stop by default. |
| FR-012 | Legend with German description and labels `0`, `15`, `30`, `50`, `100` | Legend is a static DOM control; labels are hard-coded German strings. |
| FR-013 | Title `Baumfläche`; only `Bäume` data toggle | `<title>Baumfläche</title>`; one toggle button labelled `Bäume`. |
| FR-014 | Hover pointer; compact popup on click | `mousemove` sets `cursor: pointer`; `click` opens a MapLibre `Popup` with the formatted value. |
| FR-015 | Tree layer starts hidden, flat `#39C43D` 75% | Layer `visibility: 'none'` on load; `fill-color: '#39C43D'`, `fill-opacity: 0.75`. |
| FR-016 | Tree toggle preserves center, zoom, bearing, pitch | Toggle only flips `setLayoutProperty('visibility', ...)`. |
| FR-017 | Zoom in/out + north-reset controls | MapLibre `NavigationControl` with `showCompass: true`. |
| FR-018 | Layout works at 360 px width | CSS uses `clamp()` and media queries; legend/controls collapse to a bottom strip on narrow viewports. |
| FR-019 | Required attributions reachable | `AttributionControl` lists LGL `dl-de/by-2-0`, basemap.de, and CityTreeCover MIT. |
| FR-020 | A failed optional layer does not block another | Tree layer is loaded with its own try/catch in the bootstrap; buildings render regardless. |
| FR-021 | Validate each candidate (source, extent, resolution, completeness, lineage) | `pytest` suite `tests/acceptance/` runs the five checks for every artifact in `artifacts.manifest.json`. |
| FR-022 | Reuse every accepted candidate | Pipeline reads accepted artifacts; no regeneration of accepted inputs. |
| FR-023 | Failed derived artifacts invalidate dependents only | Acceptance state propagates: a failed `canopy_mask` invalidates `building_values` and `tree_areas`; independent accepted inputs (boundary, buildings) stay reusable. |
| FR-024 | No Label Studio, no new labels, no training, no fine-tuning | Plan contains zero training steps. The only inference is `model.predict()` on existing weights. |
| FR-025 | Replacement inference on existing weights; only after RunPod capacity | Plan explicitly gates inference on owner-supplied RunPod; local never runs the model. |

### OR gates (operational)

| ID | Constraint | Plan evidence |
|---|---|---|
| OR-001 | Local peak RSS ≤ 12 GiB | Pipeline chunks by 1000 px tiles; rasters streamed via `rasterio` windowed reads; vector I/O via `pyogrio` (not `geopandas` full-read); building-value pass uses `fftconvolve` per chunk. CI runs `/usr/bin/time -v` and fails on RSS > 12 GiB. |
| OR-002 | No full-city raster/vector in memory | Tiles and chunks; never a full mosaic in RAM. |
| OR-003 | Stop and request RunPod when GPU/limit needed | `tasks.md` marks the inference step with `requires_runpod: true`; the local pipeline refuses to invoke the model and prints a `STOP` message. |
| OR-004 | One commit per spec/plan/slice/milestone | The repo enforces this with a top-level `Makefile` target `commit-spec`, `commit-plan`, `commit-slice`, `commit-milestone` that takes a single message and refuses unstaged changes. |
| OR-005 | Files > 50 MiB excluded; recorded in manifest | `.gitignore` excludes `*.tif`, `*.pmtiles`, `*.geojson > 50 MiB`, `mosaic/canopy_prediction_mask.tif` (222 MiB — the failed one — stays out entirely); `artifacts.manifest.json` records path, size, sha256, source, acceptance state for every excluded file. |

**Gate result**: PASS. Every FR has a concrete plan element; every OR is
either enforced by tooling or documented as a milestone gate. No
violation requires justification; `Complexity Tracking` stays empty.

### Post-design re-check

Re-evaluated after `research.md`, `data-model.md`, `contracts/*`, and
`quickstart.md` were generated. Each gate is honored by at least one
design artifact:

- **FR-004 / FR-007** — `E-003 BuildingFootprint.in_boundary` and
  `publish.py` clip step guarantee no outside-Mannheim geometry ships.
- **FR-005** — `R-001` and `E-005 BuildingValue.method` lock the metric
  to `scipy.signal.fftconvolve` with a 60 m / 300 px kernel, matching
  `2026.01/meta.json`.
- **FR-008 / FR-009** — `E-003.value_str` and `E-004.has_value` plus the
  MapLibre `case` expression in `map-style.md` cover both branches.
- **FR-010 / FR-011 / FR-015** — `map-style.md` lists every palette
  stop verbatim from the spec; the 75% opacity is set in the same
  block.
- **FR-021 / FR-022 / FR-023** — `contracts/manifest.md` defines the
  five FR-021 checks, the `pass` / `fail` / `pending` state machine,
  and the cascading `invalidates` list.
- **FR-024 / FR-025 / OR-003** — `cli.md` `runpod-infer` subcommand is
  gated on `MANNHEIM_RUNPOD_ENDPOINT`; the local machine never runs
  the model.
- **OR-001 / OR-002** — `R-006` and `quickstart.md` Scenario 4 keep the
  pipeline chunked at 1000 px tiles and the per-subcommand RSS gate
  at 12 GiB.
- **OR-004** — `R-013` defines the `Makefile` commit targets.
- **OR-005** — `R-012` plus `.gitignore` rules plus
  `contracts/manifest.md` keep large files out of git while recording
  them in the manifest.

**Gate result after design**: PASS. No new violations. `Complexity
Tracking` stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-replicate-mannheim-tree-cover/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks, not here)
```

### Source Code (repository root)

```text
src/pipeline/                # Offline Python data pipeline (CLI)
├── __init__.py
├── cli.py                   # click entrypoint
├── acceptance.py            # FR-021 checks (source, extent, GSD/CRS, completeness, lineage)
├── artifact_manifest.py     # read/write artifacts.manifest.json
├── boundary.py              # load + buffer official boundary
├── buildings.py             # clip + dedupe + provenance
├── canopy.py                # placeholder contract; real work runs on RunPod
├── values.py                # 60 m fftconvolve, chunked 1000 px tiles
├── trees.py                 # polygonize canopy mask → tree areas
├── publish.py               # clip to boundary; emit static bundle
└── io.py                    # windowed raster reads; PMTiles + GeoJSON writers

src/site/                    # Static frontend
├── index.html               # <title>Baumfläche</title>; bootstrap
├── style.css                # dark theme, mobile-responsive
├── main.js                  # MapLibre bootstrap, layers, popup, Bäume toggle
└── vendor/                  # maplibre-gl.js, pmtiles.js (ESM, vendored)

tests/
├── acceptance/              # FR-021 per-artifact tests
│   ├── test_boundary.py
│   ├── test_buildings.py
│   ├── test_imagery.py
│   ├── test_canopy.py
│   ├── test_values.py
│   └── test_trees.py
├── pipeline/                # value recalculation, image sanity
│   ├── test_values_recalc.py
│   ├── test_image_sanity.py
│   └── test_rss.py          # /usr/bin/time -v wrapper, fails on >12 GiB
└── frontend/                # manual smoke checklist (executed by quickstart.md)

artifacts.manifest.json      # path, size, sha256, source, acceptance state (OR-005)
tiles.csv                    # 302-row tile index of the accepted extract, verified against manifest tile_count (T055)
Makefile                     # commit-spec, commit-plan, commit-slice, commit-milestone
.gitignore                   # *.tif, *.pmtiles, *.geojson > 50 MiB
```

**Structure Decision**: Option 2 (web application) — `src/pipeline/` is
the offline data backend (CLI, no server), `src/site/` is the static
frontend, `tests/` covers both. There is no application server, no
database, and no API; the "backend" runs once on the maintainer's
machine to produce static artifacts that the frontend loads.

## Complexity Tracking

No constitution violations. Table intentionally empty.
