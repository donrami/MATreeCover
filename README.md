# Mannheim Tree-Cover Parity (Baumfläche)

A static, German-language, dark-themed web map of Mannheim. Every
building is colored by its mean tree-cover percentage within a 60 m
radius. A `Bäume` toggle shows the optional detected-tree layer. The map
reproduces the [CityTreeCover](https://github.com/jcscaptures/CityTreeCover)
presentation for Mannheim. It reuses the accepted artifacts of the prior
`mannheim` workspace.

**License**: The application code is MIT. It preserves the reference
CityTreeCover MIT notice. Map data (LGL, basemap.de) is used under
`dl-de/by-2-0`. See `src/site/attribution.html`.

## What is in this repository

- `src/pipeline/` - offline Python data pipeline (CLI, no server).
- `src/site/` - the static frontend (MapLibre GL + PMTiles, no build tool).
- `tests/` - acceptance suite (FR-021 per artifact), value recalculation
  (SC-004), image sanity (SC-005), RSS/GPU gate (OR-001/OR-003), and
  manual smoke checklists (quickstart Scenarios 1-3).
- `artifacts.manifest.json` - the single source of truth for every
  pipeline artifact (source, extent, resolution, completeness, lineage,
  acceptance state).
- `tiles.csv` - index of the accepted DOP20 imagery tiles.

Files above 50 MiB are recorded in the manifest. They are never committed
(OR-005).

## Prerequisites

- Linux x86_64, Python 3.11.
- `tippecanoe` >= 2.x on `$PATH`.
- The mannheim workspace at
  `/home/mainuser/Desktop/mannheim/workspace/mannheim` (read-only is
  sufficient). Override with `MANNHEIM_WORKSPACE`.
- A modern browser with WebGL 2 for the frontend.

## Setup

```text
make check-prereqs
make bootstrap        # venv + deps + acceptance suite (canopy-mask fail expected)
```

## Pipeline subcommands

```text
python -m src.pipeline.cli accept       # re-validate artifacts.manifest.json (FR-021)
python -m src.pipeline.cli values       # per-building 60 m values from the accepted mask
python -m src.pipeline.cli publish      # emit the static dist/ bundle
python -m src.pipeline.cli runpod-infer # gated; needs MANNHEIM_RUNPOD_ENDPOINT
```

Every invocation runs under the `/usr/bin/time -v` wrapper. Peak RSS is
logged to `validation/event.log.jsonl`. A run above 12 GiB aborts with
exit code 3 (OR-001).

Exit codes: 0 success, 1 acceptance/input failure, 2 RunPod gate,
3 RSS over 12 GiB, 4 local GPU attempted.## Publish + static hosting

```text
make publish
python -m http.server -d dist
```

`dist/` is a plain static bundle (index.html, style.json, PMTiles,
boundary mask, attribution). Any static host can serve it. There is no
application server, no database, and no analytics (FR-001).

## Quarantine state (expected)

The prior canopy mask (`mosaic/canopy_prediction_mask.tif`) fails
acceptance (0.48% completeness < 0.95). Per FR-023 its dependents
(`buildings.geojson` values, `trees.pmtiles`) stay `pending` until an
owner-approved RunPod inference (FR-024/FR-025) produces a replacement
mask. While quarantined, `publish` emits the structural bundle without
the buildings and trees layers. The acceptance suite, value recalc,
image sanity, and smoke checklists all run green.

## Tests

```text
.venv/bin/python -m pytest tests/            # full suite
.venv/bin/python -m pytest tests/acceptance  # FR-021 per artifact
.venv/bin/python -m pytest tests/pipeline    # SC-004, SC-005, OR-001/003
```

Manual browser checklists: `tests/frontend/smoke_us1.md` (color map),
`smoke_us2.md` (popup), `smoke_us3.md` (tree toggle).

## Governance

- OR-004: one commit per accepted spec, plan, slice, or milestone. Use
  `make commit-spec|commit-plan|commit-slice|commit-milestone MSG="..."`.
- OR-005: `make check-or005` asserts no `*.tif`, `*.pmtiles`, or
  > 50 MiB `*.geojson` is tracked in git. It also asserts that every
  > 50 MiB workspace file is recorded in the manifest.

## Vendored frontend libraries

- MapLibre GL JS 5.7.1 (`src/site/vendor/maplibre-gl.js`, 3-Clause BSD).
- pmtiles 4.4.0 (`src/site/vendor/pmtiles.js`, BSD-3-Clause).

No build tool and no other third-party scripts are used.
