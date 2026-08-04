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
make bootstrap        # venv + deps + acceptance suite (all green)
```

## Pipeline subcommands

```text
python -m src.pipeline.cli accept       # re-validate artifacts.manifest.json (FR-021)
python -m src.pipeline.cli values       # per-building 60 m values from the accepted mask
python -m src.pipeline.cli trees        # polygonize the mask to trees_polygons.geojson
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
```

`dist/` is a plain static bundle (index.html, style.json, PMTiles,
boundary mask, attribution). The PMTiles layers need HTTP byte
serving (Range requests). `python -m http.server` does not support
Range; use nginx or another Range-capable host:

```text
nginx -c /tmp/nginx-dist.conf   # server { root .../dist; }
```

The bundle is ~171 MB on disk (buildings.pmtiles 33 MB, trees.pmtiles
77 MB, buildings.geojson 54 MB, vendored libs ~1 MB). SC-008 is a time
budget, not a byte budget: PMTiles are range-requested, so a first
paint fetches only the viewport tiles — measured 434 KB of the
buildings archive on a throttled 25 Mbps / 50 ms link. First usable
map measured at 2.5 s (budget 10 s); popup, zoom, and toggle
interactions measured at 80–211 ms (budget 2 s). Record:
`validation/perf-budget.json`.

There is no application server, no database, and no analytics (FR-001).

## Canopy-mask inference on RunPod (FR-024/FR-025)

The canopy mask is produced on owner-supplied RunPod capacity; the
local pipeline never runs the model (OR-003). The endpoint contract:
`POST {"model": "deepLabV3plus-resnet34", "inputs": [...]}` returns the
mask as GeoTIFF bytes. `src/endpoint/server.py` implements it —
banded tiled inference replicating the CityTreeCover reference
(DeepLabV3+ ResNet34, 1024 px patches, 64 px overlap, ImageNet
normalization, sigmoid threshold 0.5, max-confidence seams).

Prereqs on the pod: the imagery tiles under `mosaic/extract/` and the
weights `models/best_deeplabv3plus.pth` (from the CityTreeCover repo,
MIT). Then:

```text
bash scripts/runpod-deploy.sh [host] [port] [ssh_key]   # install + start
ssh -p 40092 -i ~/.ssh/id_ed25519 -N -L 8000:localhost:8000 root@HOST
MANNHEIM_RUNPOD_ENDPOINT=http://127.0.0.1:8000/infer \
  python -m src.pipeline.cli runpod-infer
```

`runpod-infer` writes `mosaic/canopy_prediction_mask.tif` and the
accompanying JSON into the workspace. With the mask accepted, the
remaining pipeline runs locally:

```text
python -m src.pipeline.cli values   # per-building 60 m values
python -m src.pipeline.cli trees    # trees_polygons.geojson (EPSG:4326)
make pmtiles-buildings pmtiles-trees
python -m src.pipeline.cli accept && python -m src.pipeline.cli publish
```

The acceptance suite, value recalc, image sanity, and smoke checklists
run green with the accepted mask.

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
