# Quickstart

**Branch**: `001-replicate-mannheim-tree-cover` | **Date**: 2026-08-03

End-to-end validation guide. Every scenario in this document is a
pass/fail check against one or more spec items (FR-001..FR-025,
OR-001..OR-005, SC-001..SC-010).

## Prerequisites

- Linux x86_64 host.
- Python 3.11 with the dependencies listed in the plan's
  Technical Context.
- `tippecanoe` ≥ 2.x on `$PATH`.
- A modern browser for the frontend scenarios.
- The mannheim workspace at
  `/home/mainuser/Desktop/mannheim/workspace/mannheim`,
  read-only access sufficient.

## Setup

```text
make commit-plan
git checkout -b 001-replicate-mannheim-tree-cover  # if not already on the branch
make bootstrap    # creates a venv, installs deps, runs the acceptance suite once
```

`make bootstrap` finishes with either `OK — all pass` or
`FAIL — see artifacts.manifest.json`. Since the owner-approved
RunPod inference produced an accepted canopy mask
(completeness 1.0), the acceptance suite is fully green and
`publish` emits the complete bundle (buildings + trees PMTiles).

## Scenario 1 — User Story 1: view the Mannheim color map (P1)

Maps to FR-001..FR-004, FR-010/FR-011, FR-017, FR-019, SC-001,
SC-002, SC-008, SC-009.

1. Serve the published bundle with a Range-capable static server
   (PMTiles requires HTTP Range requests; `python -m http.server`
   does not support them, so use e.g. nginx):
   ```text
   nginx -c /tmp/nginx-dist.conf   # root .../dist; Range enabled by default
   ```
2. Open the served URL in a clean browser.
3. **Pass criteria**:
   - Title bar reads `Baumfläche` (FR-013).
   - The full Mannheim boundary fills the viewport with minimal
     padding; north is up (FR-002).
   - The base map is dark; everything outside the boundary is
     black (FR-003).
   - Each Mannheim building uses the reference palette at 75%
     opacity; outlines are thin and gray (FR-010).
   - Zoom in, zoom out, and north reset are visible and
     functional (FR-017).
   - The attribution control lists LGL (`dl-de/by-2-0`),
     basemap.de, and CityTreeCover (FR-019).
   - Reload at 360 px width; legend and controls remain usable
     (FR-018).
   - The build's RSS during `publish` is ≤ 12 GiB (verified
     separately with `/usr/bin/time -v`).

## Scenario 2 — User Story 2: read a building value (P2)

Maps to FR-008, FR-009, FR-014, SC-004, SC-006.

1. With the page from Scenario 1 still open, hover a building.
2. **Pass criteria**:
   - The pointer turns into a pointer cursor (FR-014).
   - Click the building. A compact popup opens and shows the
     value with two decimal places, e.g. `12.34%` (FR-008,
     FR-014).
   - Click a building marked as unavailable (no value). The
     popup reads `–` and the fill is the gray
     unavailable color (FR-009).
3. **Independent recalculation**:
   ```text
   pytest tests/pipeline/test_values_recalc.py
   ```
   - 100 random buildings are sampled. The independent
     recompute differs from the published value by ≤ 1
     percentage point in 100/100 cases (SC-004).
4. **Timed interaction**:
   - With a stopwatch: at least 9 of 10 test visitors
     read a value within 30 s (SC-006). Recorded as a
     manual note in `validation/event.log.jsonl`.

## Scenario 3 — User Story 3: toggle detected tree cover (P3)

Maps to FR-013, FR-015, FR-016, SC-005, SC-007.

1. With the page from Scenario 1 still open, click `Bäume`.
2. **Pass criteria**:
   - The tree areas appear in flat `#39C43D` at 75% opacity
     (FR-015).
   - The button label is `Bäume`; no other data-layer button
     exists (FR-013).
   - The camera does not move (FR-016). Verify by reading
     `map.getCenter()`, `map.getZoom()`, `map.getBearing()`,
     `map.getPitch()` before and after.
   - At least 9 of 10 test visitors toggle the layer within
     15 s (SC-007).
3. **Image sanity**:
   ```text
   pytest tests/pipeline/test_image_sanity.py
   ```
   - 20 image crops. At least 17/20 distinguish obvious
     canopy from roofs, roads, and water (SC-005).

## Scenario 4 — User Story 4: reuse prior work safely (P4)

Maps to FR-021, FR-022, FR-023, FR-024, FR-025, OR-001, OR-003,
OR-005, SC-009, SC-010.

1. **Acceptance pass**:
   ```text
   python -m src.pipeline.cli accept
   ```
   - `artifacts.manifest.json` reports per-artifact
     `pass` / `fail` / `pending` (FR-021).
2. **Zero repeat downloads or regenerations**:
   - For each accepted artifact, the pipeline reads it from
     its recorded path; no download or re-extraction occurs
     (FR-022, SC-010).
3. **Dependent invalidation (unblocked state)**:
   - The canopy mask is `pass` (completeness 1.0). The derived
     `values`, `trees_polygons.geojson`, `trees.pmtiles`, and
     `buildings.pmtiles` artifacts are `pass` and published to
     `dist/` (FR-023). A future `fail` on any derived artifact
     still flips only its dependents to `pending`.
4. **Resource gates**:
   - `pytest tests/pipeline/test_rss.py` measures peak RSS
     per subcommand; each ≤ 12 GiB (OR-001, SC-009).
   - The pipeline never invokes a GPU; the
     `runpod-infer` subcommand exits with code `2`
     unless `MANNHEIM_RUNPOD_ENDPOINT` is set (OR-003,
     FR-025).
5. **Large-file governance**:
   - `git status` shows no `*.tif` / `*.pmtiles` /
     large `*.geojson` files (OR-005).
   - The manifest records every excluded file's path,
     size, sha256, and source.

## What to do when an acceptance fails

- The acceptance gate (`accept` subcommand) is the source of
  truth. It re-validates every artifact and refreshes the
  manifest.
- A `fail` on a derived artifact (e.g. canopy mask) flips its
  dependents to `pending`. The pipeline does not auto-regenerate;
  the maintainer chooses to run `values` (depends on canopy) or
  `runpod-infer` (depends on RunPod) only after fixing the
  upstream cause.
- A `fail` on an input artifact (e.g. missing tile) requires a
  re-download, which the maintainer must approve per FR-025.
- A `fail` on the `pytest` test suite blocks the `publish`
  step. The maintainer must clear the failure before the
  next milestone commit (OR-004).
