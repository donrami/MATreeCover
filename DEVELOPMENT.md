# Development

This document is for people who want to build, test, or deploy the map.
For an introduction to the map itself, see the [README](README.md).

## What is in this repository

This section is the human form of the layout; the machine form is
`scripts/layout-manifest.tsv`, enforced by `make check-layout`.

Root-level files:

- `README.md` — user-facing description and live-map link.
- `LICENSE` — MIT license.
- `DEVELOPMENT.md` — this file: architecture, commands, governance.
- `CHANGELOG.md` — release log.
- `Makefile` — the command surface (`make bootstrap`, `make publish`, `make check-*`).
- `pyproject.toml` — Python package metadata and dev dependencies.
- `.gitignore` — exclusions for local and harness directories.
- `artifacts.manifest.json` — the single source of truth for every
  pipeline artifact (source, extent, resolution, completeness, lineage,
  acceptance state).
- `tiles.csv` — index of the accepted DOP20 imagery tiles.
- `screenshot/` — `map.png`, the README screenshot.

Directories:

- `src/pipeline/` — offline Python data pipeline (CLI, no server).
- `src/site/` — the static frontend (MapLibre GL + PMTiles, no build tool).
- `src/endpoint/` — the RunPod HTTP endpoint that runs the canopy-model
  inference on the pod (`server.py`); never executed locally (OR-003).
- `workers/map/` — the Cloudflare Worker that serves the map from a
  static-assets binding plus R2 data files.
- `scripts/` — deploy (`deploy-cf.sh`, `runpod-deploy.sh`), governance
  gates (`check-public.sh`, `check-git-history.sh`, `check-layout.sh`,
  `check_or005.py`, `commit-check.sh`, `next-tag.sh`, `check-prereqs.sh`),
  the shared secret patterns (`public-patterns.txt`), the history
  exemption ledger (`history-exemptions.tsv`), the layout manifest
  (`layout-manifest.tsv`), and the performance harness (`perf-measure.sh`,
  `perf-probe.mjs`, `parity-render.mjs`, `smoke-verify.mjs`).
- `specs/` — one directory per feature (001–015): spec, plan, research,
  tasks, quickstart, data model, and contracts. The feature history is
  summarized below; the spec directories are the primary record.
- `tests/` — pytest suites (acceptance, pipeline, endpoint) plus manual
  browser smoke checklists (`tests/frontend/`).
- `verification/` — evidence for how well the tree-detection model works
  on Mannheim imagery (features 008/009): the reproducible 100-patch
  sample, per-patch ratings, the German findings report, the
  calibration value deltas, and the committed security audit report
  (`security-audit-2026-08-08.md`, feature 015).
- `validation/` — machine records: `event.log.jsonl` (per-run RSS/exit
  codes), perf budgets and live measurements, `published-map.json`.
- `outputs/` — the tree-canopy-30-heat literature review artifacts
  (draft, research brief, provenance, reviewer/verifier reports, cooling
  chart); `cited.md` is the verified source list; the Semantic-Scholar
  abstract pulls (`s2_abstracts*.json`) and the info image live here
  too. Internal planning drafts stay in `outputs/.plans/`.

Files above 50 MiB are recorded in the manifest. They are never committed
(OR-005).

## Feature history (development log)

The project went live incrementally; every feature has its own spec
directory under `specs/` with the full record. Short version:

| # | Date (2026) | Feature | What shipped |
|---|-------------|---------|--------------|
| 001 | 08-03/04 | Mannheim tree-cover parity | Replicate CityTreeCover for Mannheim: dark map, buildings colored by mean 60 m tree-cover, Bäume toggle, German UI, static bundle. Reused the archived workspace; canopy mask unblocked via one owner-supplied RunPod inference. |
| 002 | 08-04 | Fix building popup | Popup interaction fixed; maplibre-gl.css vendored (controls were unstyled). |
| 003 | 08-04 | Darken base map | Basemap raster darkened (`raster-brightness-max 0.65`). |
| 004 | 08-04 | Map UI rework | Brightness slider, left-column tools card, gradient legend, low-brightness basemap inversion (FR-019) capped at 0.65. |
| 005 | 08-05 | Host on personal domain | Cloudflare Worker serving `https://abu-hamad.de/map/`; large data files in R2 with Range/206 passthrough; DNS + email/blog continuity gates. |
| 006 | 08-05 | Public release prep | User README, MIT LICENSE, `make check-public` hygiene gate (FR-010), sanitization of personal paths, `dist-assets/` staging. |
| 007 | 08-05 | First-visit story modal | Story modal explaining the 30 % shade guideline and the reference project, with source-repository link (T015). |
| 008 | 08-05 | Verify tree detection | Structured visual inspection of 100 sampled patches (38 Stadtteile × 3 value bands, seed `20260805`): 59 % correct, 39 % over-detection, 2 % under. Report in `verification/report.md`. |
| 009 | 08-05/06 | Calibrate canopy threshold | Sigmoid threshold parameterized end-to-end; candidate masks at 0.6/0.65 re-verified and value-deltas quantified. Decision: keep published 0.5 values; no re-release. See “Model tuning” below. |
| 010 | 08-06 | Accuracy disclaimer | German accuracy note on the attribution page + legend link; no district specifics; map data unchanged. |
| 011 | 08-06 | Heatwave map insights | Clickable districts with statistics popups, city-overview card (“Mannheim im Überblick”); Hitzebelastung view reverted (Option B scope); city stats derived at publish time. |
| 012 | 08-06 | Mobile-first native UX | Bottom-sheet surfaces, thumb-reachable tool buttons, desktop panel, 30 %-scale mockups, German tooltips, native-feeling motion. |
| 013 | 08-07 | Popup comparative context | Building popup: headline value, 30 % badge, district/city comparison with signed pp deltas; district popup: rank “Platz X von 38”, quartile band, city comparison. Rank computed client-side once. |
| 014 | 08-08 | Performance fixes | PMTiles edge/browser caching, content-hashed immutable assets, no cross-fade init, low-zoom geometry simplification, inlined styles, preload/preconnect, favicon; committed perf harness; mobile attribution alignment fix. |
| 015 | 08-08 | Security audit & housekeeping | Full-history secrets scan (`make check-history`) plus extended public-hygiene gate (P1–P32, shared pattern file); security headers + CSP on every Worker response; endpoint loopback bind + 1 MiB size cap; vendored-library provenance record; layout gate (`make check-layout`) and housekeeping moves into `outputs/`; committed audit report in `verification/security-audit-2026-08-08.md`. |

There is also a heatwave-context literature review (not a numbered
feature): the 30 % guideline evidence base lives in `outputs/` and
`outputs/cited.md` (39 items, URLs verified, reviewer/verifier passes clean).

## Architecture in one paragraph

DOP20 aerial imagery (20 cm GSD, LGL, dl-de/by-2-0) is cut into tiles in
the archived workspace. On owner-supplied RunPod capacity, a DeepLabV3+
ResNet34 segmentation model (see next section) classifies tree canopy
into a binary mask (`mosaic/canopy_prediction_mask.tif`, EPSG:25832).
The local pipeline then: (1) computes per-building 60 m-radius mean
tree-cover values (`values`), (2) polygonizes the mask into tree areas
(`trees`), (3) tiles both into PMTiles with tippecanoe, (4) validates
every artifact against `artifacts.manifest.json` (`accept`), and
(5) clips everything to the official boundary and emits the static
`dist/` bundle (`publish`). A Cloudflare Worker serves the bundle from
`dist-assets/` and streams the large PMTiles from R2 with 206 range
support. There is no application server, no database, and no analytics
(FR-001).

## The tree-detection model (DeepLabV3+ ResNet34)

The canopy mask is produced by a model the project **reuses, never
retrains** (FR-024/FR-025): DeepLabV3+ with a ResNet34 encoder via
`segmentation-models-pytorch`, trained by Jakob Schultz on Erlangen
aerial imagery for the reference project
[CityTreeCover](https://github.com/jcscaptures/CityTreeCover) (MIT).

**Weights.** The original checkpoint, used unchanged for every inference
run in this project:

- Reference project weights: <https://github.com/jcscaptures/CityTreeCover/blob/main/best_deeplabv3plus.pth>
- On the pod: `/workspace/mannheim/models/best_deeplabv3plus.pth`
  (staged by `scripts/runpod-deploy.sh`; the script refuses to start
  without it).
- Local archived copy (gitignored, never redistributed):
  `data/archive/mannheim-project/models/best_deeplabv3plus.pth`.

The file is a plain PyTorch state dict (not a `.tar`). Loading is
`torch.load(path, map_location=...)` with no wrapper. The pod installs
`segmentation-models-pytorch` and builds the same architecture from
`MODEL_ID = "deepLabV3plus-resnet34"` in `src/endpoint/server.py`.

**Inference recipe** (parity with the reference; constants in
`src/endpoint/server.py`):

- Patches: 1024 × 1024 px with 64 px overlap (the overlap is discarded
  except for a max-confidence seam policy between overlapping bands).
- Normalization: ImageNet per-channel `(x/255 − mean) / std` with
  `mean = (0.485, 0.456, 0.406)`, `std = (0.229, 0.224, 0.225)`.
- Binarization: sigmoid output compared against a threshold. Default
  `0.5`, overridable per request (see tuning below).
- Ground sampling distance: 0.2 m (matches the DOP20 tiles).
- Output: binary canopy mask GeoTIFF + a metadata JSON that records
  model id, threshold, coverage, and tile info. The metadata is the
  trust boundary: a mask without complete metadata is never accepted
  (FR-008 of feature 009).

**Transfer caveat.** The model was trained on Erlangen imagery, and the
model author reports that his own cross-city transfer test
(Erlangen-trained weights on Bamberg DOP20) was significantly worse:
lower contrast, different sun angle, few training data. The Mannheim
verification (feature 008) therefore measured the transfer here instead
of assuming it.

### Model tuning: verification and threshold calibration

This project did **not** retrain or fine-tune the model. The tuning axis
was the **sigmoid decision threshold**, calibrated against a structured
visual inspection. Full record: `verification/report.md` (German),
`specs/008-verify-tree-detection/`, `specs/009-calibrate-canopy-threshold/`.

**Baseline (feature 008, 2026-08-05).** 100 patches sampled
reproducibly (seed `20260805`; stratified by 38 Stadtteile × value
bands `[0,10)`, `[10,30)`, `[30,100]`; proportional to building counts
with a floor of 1 per district). Each patch was rendered as a
1024 px window with the production mask overlaid and rated
`correct` / `over` / `under`. Result at threshold 0.5: **59 % correct,
39 % over-detection, 2 % under-detection**. The over-detection
concentrated on roofs, lawns, fields, and railway ballast, inflating
per-building values in the affected districts (Sandhofen, Feudenheim
flagged; dense districts clean).

**Candidates (feature 009, 2026-08-05).** The threshold was made
configurable end to end with no behavior change at the default.
`POST /infer` accepts an optional `"threshold"` field
(`_parse_threshold` in `server.py`). The CLI gained
`runpod-infer --threshold <t> --out <workspace-relative path>`, and the
metadata records the threshold used. Two candidate masks were produced
from the **same weights and tiles** (one RunPod session each, RTX 3090,
~12 314 patches per run): `mosaic/canopy_prediction_mask_t060.tif` and
`mosaic/canopy_prediction_mask_t065.tif`, plus their metadata JSONs.
The 100 patches were re-rated per candidate with the same criteria.

Results:

| Measure | 0.5 (published) | 0.6 | 0.65 |
|---|---|---|---|
| Previously `correct` patches still correct | — | 82.9 % | 75.8 % |
| Previously `over` patches now improved | — | 80.6 % | 72.8 % |
| Mean per-building value delta vs published | — | −3.90 pp | −5.53 pp |
| Buildings moving > 0.5 pp | — | 98.0 % | 98.6 % |
| City mean tree cover | 22.22 % | 18.33 % | 16.69 % |

An independent visual pass over the five strongest losses in previously
correct patches found that **70–85 % of the area removed at 0.6 is real
tree canopy**; the additional 0.65 step removes mostly crown edges. Both
candidates therefore trade false positives for real trees, at a cost of
shifting almost every building value.

**Decision (owner, 2026-08-05, recorded in `verification/report.md`):**
keep the published 0.5-threshold values; do not adopt either candidate;
do not re-release the data. The chosen remedy is a general accuracy
disclaimer on the site (feature 010). Values are model-based estimates
from aerial imagery, tree detection is imperfect, and no district-level
numbers are published.

**Related bug found during calibration:** a pre-existing `values.py`
float-noise issue (fftconvolve) had left 109 buildings without a value
in the published file. The pipeline code was fixed (`values.py`,
regression test in `tests/pipeline/test_values_recalc.py`); the
published map was deliberately not changed.

**How to reproduce a candidate mask:**

```text
# on the pod: endpoint already accepts "threshold"; stage weights + tiles
bash scripts/runpod-deploy.sh <host> [port] [ssh_key]
ssh -p <port> -i <ssh_key> -N -L 8000:localhost:8000 <host>
MANNHEIM_RUNPOD_ENDPOINT=http://127.0.0.1:8000/infer \
  python -m src.pipeline.cli runpod-infer --threshold 0.6 \
  --out mosaic/canopy_prediction_mask_t060.tif
python -m src.pipeline.cli verify-render --mask mosaic/canopy_prediction_mask_t060.tif \
  --patches-dir verification/patches_t060 --sample-out verification/sample_t060.jsonl
python -m src.pipeline.cli verify-value-delta --mask mosaic/canopy_prediction_mask_t060.tif
# then rate the PNGs into verification/ratings_t060.jsonl (contracts/verify-ratings.md)
```

**What was explicitly out of scope (and still is):** retraining,
fine-tuning, or replacing the model; thresholds outside 0.5–0.7;
more than two candidates; any change to the published map without a
recorded release decision.

## Prerequisites

- Linux x86_64, Python 3.11.
- `tippecanoe` >= 2.x on `$PATH`.
- The mannheim workspace at `data/archive/workspace` (an archived mirror
  of the original workspace; read-only is sufficient). The archive is
  gitignored and not redistributed; point `MANNHEIM_WORKSPACE` at your
  own workspace if you have one.
- A modern browser with WebGL 2 for the frontend.
- For the perf harness (feature 014): `node` and a Chromium build
  (`CHROME_PATH`, default `/usr/bin/chromium`).
- For deploys: `npx wrangler` (Cloudflare Workers CLI) and `curl`.

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
                                        #   --threshold 0.6  (default 0.5)
                                        #   --out mosaic/canopy_prediction_mask_t060.tif
python -m src.pipeline.cli verify-sample    # reproducible 100-patch inspection sample (feature 008)
python -m src.pipeline.cli verify-render    # review PNGs with canopy-mask overlay, degeneracy flags
                                            #   --mask <workspace mask>  (default: published mask)
python -m src.pipeline.cli verify-report    # German findings report from ratings + notes
python -m src.pipeline.cli verify-value-delta  # candidate-vs-published per-building values (feature 009)
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

**Caching (feature 014).** Repeat visits are cheap by design:

- `buildings.pmtiles` / `trees.pmtiles`: `public, max-age=86400,
  stale-while-revalidate=604800, no-transform` (R2 object metadata;
  `deploy-cf.sh verify` asserts it). Browser and edge both cache; a
  second visit transfers only genuinely new ranges.
- Hashed static assets (`main-<hash>.js`, `style-<hash>.css`,
  `vendor/*-<hash>.js`, boundary/stadtteile GeoJSON): `immutable`
  caching via the Worker; new deploys get new hashes, so old caches are
  never stale.
- `index.html` (and other un-hashed files): `public, max-age=0,
  must-revalidate`. The document always revalidates, so the newest
  bundle is picked up on the next visit.
- `buildings.geojson`: `no-cache` (R2, unchanged).

The bundle is ~172 MB on disk (buildings.pmtiles 33 MB, trees.pmtiles
80 MB, buildings.geojson 56 MB, vendored libs ~1 MB). SC-008 is a time
budget, not a byte budget: PMTiles are range-requested, so a first
paint fetches only the viewport tiles: measured ~453 KB of the
buildings archive on a throttled 25 Mbps / 50 ms link (plus ~16 KB of
trees ranges). Last measured (feature 013/014 bundle, 2026-08-08): first usable map
1.39 s (budget 10 s). All 8 interactions (popup, zoom, tree toggle,
district click, panel, surface toggle) settle in 0–123 ms (budget 2 s).
Lighthouse mobile TBT dropped from 6310 ms to 2790 ms (−56 %) after the
014 fixes. Records: `validation/perf-budget.json` (canonical),
`validation/live-perf.json`, `validation/baseline-014.json`, audit in
`validation/perf-audit-2026-08-08.md`.

**Perf harness.** `scripts/perf-measure.sh <url>` drives headless
Chromium (`perf-probe.mjs`) for cold/warm load + interaction timing and
optionally runs Lighthouse; `parity-render.mjs` renders PMTiles zoom
levels to PNGs for visual parity checks, and `smoke-verify.mjs` drives
the smoke scenarios headlessly. These are committed so any future
change can be measured against the same method.

There is no application server, no database, and no analytics (FR-001).

## Verification of detection quality (feature 008)

Structured visual inspection of the reused canopy model on Mannheim
imagery: evidence for how well the published tree layer detects trees.
Read-only over the workspace; never runs the model (OR-003). Details in
`specs/008-verify-tree-detection/`; artifacts in `verification/`. The
calibration follow-up (features 009/010) is documented in the “Model
tuning” section above and in `specs/009-calibrate-canopy-threshold/`.

```text
python -m src.pipeline.cli verify-sample   # verification/sample.jsonl (seed 20260805, 38 Stadtteile x 3 bands)
python -m src.pipeline.cli verify-render   # verification/patches/*.png (gitignored) + degeneracy in sample
# owner rates each PNG into verification/ratings.jsonl (contracts/verify-ratings.md)
python -m src.pipeline.cli verify-report   # verification/report.md from ratings + notes.md
```

District boundaries: official GDI-MA Stadtteile (38, dl-de/by-2-0),
committed at `verification/stadtteile.geojson` (attribution in
`verification/README.md`).

## Canopy-mask inference on RunPod (FR-024/FR-025)

The canopy mask is produced on owner-supplied RunPod capacity; the
local pipeline never runs the model (OR-003). The endpoint contract:
`POST {"model": "deepLabV3plus-resnet34", "inputs": [...]}` returns the
mask as GeoTIFF bytes; an optional `"threshold"` field (default 0.5)
selects the sigmoid cutoff. `src/endpoint/server.py` implements it:
banded tiled inference replicating the CityTreeCover reference
(DeepLabV3+ ResNet34, 1024 px patches, 64 px overlap, ImageNet
normalization, sigmoid threshold, max-confidence seams). See “The
tree-detection model” for weights and tuning details.

Prereqs on the pod: the imagery tiles under `mosaic/extract/` and the
weights `models/best_deeplabv3plus.pth` (from the CityTreeCover repo,
MIT — original file:
<https://github.com/jcscaptures/CityTreeCover/blob/main/best_deeplabv3plus.pth>).
Then:

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
.venv/bin/python -m pytest tests/acceptance  # FR-021 per artifact, style, values, districts,
                                             # popup render + rank (013), threshold (010)
.venv/bin/python -m pytest tests/pipeline    # SC-004/SC-005 value recalc, publish hashing (014),
                                             # verify sample/render, image sanity, RSS gate
.venv/bin/python -m pytest tests/endpoint    # inference threshold parameterization (009)
```

Manual browser checklists (per feature, all in `tests/frontend/`):
`smoke_us1.md` (color map), `smoke_us2.md` (popup), `smoke_us3.md`
(tree toggle), `smoke_us4.md` (UI placement/no overlap), `smoke_us5.md`
(first-visit story modal), `smoke_us6.md` (heatwave insights, feature
011), `smoke_us7.md` (popup comparative context, feature 013),
`smoke_mobile.md` (mobile-first UX, feature 012). The headless
equivalent of the smoke checks is `scripts/smoke-verify.mjs`.

## Governance

- OR-004: one commit per accepted spec, plan, slice, or milestone. Use
  `make commit-spec|commit-plan|commit-slice|commit-milestone MSG="..."`.
- OR-005: `make check-or005` asserts no `*.tif`, `*.pmtiles`, or
  > 50 MiB `*.geojson` is tracked in git. It also asserts that every
  > 50 MiB workspace file is recorded in the manifest.
- FR-010/FR-003 (feature 015): `make check-public` scans tracked files
  for personal paths, credentials, and internal tooling references
  against the shared pattern file `scripts/public-patterns.txt`
  (P1–P32, one source of truth for both gates). It must stay clean —
  it is the gate for making the repository public. The gate grew with
  the repo and has caught real leaks before (harness paths, absolute
  render paths) — keep it green. Adding a pattern is a contract
  change: update the pattern file and the contract together.
- FR-001/FR-002 (feature 015): `make check-history` scans the full git
  history (trees and commit messages) with the same pattern set;
  historical findings are allowed only via dispositioned exemption
  rows in `scripts/history-exemptions.tsv`, each resolving to a
  finding in `verification/security-audit-2026-08-08.md`. History is
  never rewritten; the gate enforces forward prevention.
- FR-009/FR-011 (feature 015): `make check-layout` asserts the tracked
  tree matches `scripts/layout-manifest.tsv` (the machine form of the
  layout section above); moving a file requires updating the manifest
  and the section together.

## Vendored frontend libraries

- MapLibre GL JS 5.7.1 (`src/site/vendor/maplibre-gl.js`, 3-Clause BSD).
- pmtiles 4.4.0 (`src/site/vendor/pmtiles.js`, BSD-3-Clause).

Committed provenance (version, license, source URL, sha256 of the
vendored files, and the declared runtime dependencies) lives in
`src/site/vendor/PROVENANCE.md` (FR-008, feature 015). Updating a
vendored library updates the record in the same commit.

Runtime dependencies: besides the vendored files, the map fetches the
LGL basemap tiles (`sgx.geodatenzentrum.de`, attributed) and the glyph
font origin `demotiles.maplibre.org` (MapLibre's public demo CDN,
accepted risk — GET-only, no data leaves the page, CSP-restricted to
fonts; see PROVENANCE.md). No build tool and no other third-party
scripts are used.
