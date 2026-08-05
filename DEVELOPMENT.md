# Development

This document is for people who want to build, test, or deploy the map.
For an introduction to the map itself, see the [README](README.md).

## What is in this repository

- `src/pipeline/` — offline Python data pipeline (CLI, no server).
- `src/site/` — the static frontend (MapLibre GL + PMTiles, no build tool).
- `workers/map/` — the Cloudflare Worker that serves the map.
- `tests/` — acceptance suite (FR-021 per artifact), value recalculation
  (SC-004), image sanity (SC-005), RSS/GPU gate (OR-001/OR-003), and
  manual smoke checklists (quickstart Scenarios 1–3).
- `artifacts.manifest.json` — the single source of truth for every
  pipeline artifact (source, extent, resolution, completeness, lineage,
  acceptance state).
- `tiles.csv` — index of the accepted DOP20 imagery tiles.

Files above 50 MiB are recorded in the manifest. They are never committed
(OR-005).

## Prerequisites

- Linux x86_64, Python 3.11.
- `tippecanoe` >= 2.x on `$PATH`.
- The mannheim workspace at `data/archive/workspace` (an archived mirror
  of the original workspace; read-only is sufficient). The archive is
  gitignored and not redistributed; point `MANNHEIM_WORKSPACE` at your
  own workspace if you have one.
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
3 RSS over 12 GiB. No local GPU path exists (OR-003), so no GPU exit
code is defined.

## Publish + hosting

```text
make publish
```

`dist/` is a plain static bundle (index.html, style.json, PMTiles,
boundary mask, attribution) served at `https://abu-hamad.de/map/`
(canonical URL, trailing slash) by the Cloudflare Worker
(`workers/map/`) with the large data files (`buildings.pmtiles`,
`trees.pmtiles`, `buildings.geojson`) in an R2 bucket. Deploy with
`scripts/deploy-cf.sh`:

```text
bash scripts/deploy-cf.sh prepare-assets   # stage dist/ minus the >25 MiB data files
bash scripts/deploy-cf.sh upload-data      # r2 object put (atomic per object)
npx wrangler deploy --config workers/map/wrangler.toml  # atomic version switch
bash scripts/deploy-cf.sh verify           # FR-013 gate (DNS, redirects, Range 206, cert)
bash scripts/deploy-cf.sh verify-dns       # FR-014 gate (email/blog records)
```

The committed `workers/map/wrangler.toml` carries a `<your-zone-id>`
placeholder. To deploy, either substitute your Cloudflare zone id or keep
a gitignored local copy:

```text
cp workers/map/wrangler.toml workers/map/wrangler.local.toml
# edit wrangler.local.toml: replace <your-zone-id>
npx wrangler deploy --config workers/map/wrangler.local.toml
```

The FR-014 `verify-dns` gate checks the owner's email/blog DNS records.
Those values are not committed. Create `scripts/deploy-cf.env`
(gitignored) from the example in this section, or set the
`MATREECOVER_MX1`, `MATREECOVER_MX2`, `MATREECOVER_SPF_INCLUDE`,
`MATREECOVER_AUTOCONFIG_CNAME`, `MATREECOVER_AUTODISCOVER_CNAME`
environment variables. Without configuration the continuity checks are
skipped with a warning.

```text
# scripts/deploy-cf.env (gitignored)
MATREECOVER_MX1=mx1.example.net
MATREECOVER_MX2=mx2.example.net
MATREECOVER_SPF_INCLUDE=spf.example.net
MATREECOVER_AUTOCONFIG_CNAME=autoconfig.example.net
MATREECOVER_AUTODISCOVER_CNAME=autodiscover.example.net
```

The PMTiles layers need HTTP byte serving (Range requests); the
Worker streams them from R2 with 206 passthrough. The domain's DNS
runs on Cloudflare; the migration and the email/blog continuity checks
are documented in `specs/005-host-on-personal-domain/contracts/dns-https.md`.

The bundle is ~171 MB on disk (buildings.pmtiles 33 MB, trees.pmtiles
77 MB, buildings.geojson 54 MB, vendored libs ~1 MB). SC-008 is a time
budget, not a byte budget: PMTiles are range-requested, so a first
paint fetches only the viewport tiles — measured 434 KB of the
buildings archive on a throttled 25 Mbps / 50 ms link. First usable
map measured at 2.5 s (budget 10 s); popup, zoom, and toggle
interactions measured at 80–211 ms (budget 2 s). Record:
`validation/perf-budget.json`; the live re-measurement lands in
`validation/live-perf.json`.

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
bash scripts/runpod-deploy.sh <host> [port] [ssh_key]   # install + start
ssh -p <port> -i <ssh_key> -N -L 8000:localhost:8000 <host>
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
- FR-010: `make check-public` scans tracked files for personal paths,
  credentials, and internal tooling references. It must stay clean —
  it is the gate for making the repository public.

## Vendored frontend libraries

- MapLibre GL JS 5.7.1 (`src/site/vendor/maplibre-gl.js`, 3-Clause BSD).
- pmtiles 4.4.0 (`src/site/vendor/pmtiles.js`, BSD-3-Clause).

No build tool and no other third-party scripts are used.
