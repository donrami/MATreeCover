# Phase 0 Research

**Branch**: `001-replicate-mannheim-tree-cover` | **Date**: 2026-08-03
**Inputs**: `spec.md`, `2026.01/meta.json`, the mannheim workspace
inventory at `/home/mainuser/Desktop/mannheim/workspace/mannheim`.

This document records every technical decision the plan must commit to.
Each unknown from the spec or from the mannheim workspace is resolved
here, with rationale and rejected alternatives. No data is downloaded
and no inference runs during planning.

## R-001 — 60 m building-value metric

**Decision**: Compute the per-building value as the mean canopy
fraction inside a circular 60 m radius evaluated at every pixel of the
footprint, then take the mean of those pixel values. Implementation uses
`scipy.signal.fftconvolve` on a binary canopy mask with a 300 px circular
kernel (60 m / 0.2 m GSD), chunked 1000 px tiles, and rasterizes each
building footprint to the mask grid before sampling.

**Rationale**: Matches the reference implementation directly
(`2026.01/meta.json`'s `neighbourhood` block records
`scipy.signal.fftconvolve with circular kernel, chunked 1000 px tiles`
with `radius_m: 60.0` and `radius_px: 300`). This is the same
arithmetic as the deployed CityTreeCover for any city at 0.2 m GSD.

**Alternatives considered**:
- *Distance-weighted Gaussian kernel*: smoother but disagrees with
  the reference, violates FR-005 parity.
- *Exponential-decay mean*: not circular, biases values for long
  footprints, fails SC-004.
- *Pre-computed zonal statistics per polygon*: matches at the
  footprint level but requires the footprint to be inside a closed
  disc that may extend outside the buffered boundary. The 60 m halo
  (FR-006) is the only sanctioned way to include that exterior.

## R-002 — Imagery source and provenance

**Decision**: Reuse `mosaic/extract/dop20rgb_*.tif` (460 tiles, 0.2 m
GSD, EPSG:25832, 1000 m tiles, 2024 acquisition) from the mannheim
workspace. Each tile's CSV sidecar carries the official LGL
metadata (`Kachelname`, `Aktualitaet`, `Bodenpixelgroesse`, CRS,
origin). The pipeline ingests the sidecar and asserts
`Bodenpixelgroesse == 0.2` and `Koordinatenreferenzsystem_Lage == 25832`
on every tile.

**Rationale**: FR-021 requires the five-criterion validation. Sidecar
checks give source, extent, and resolution in one read. Reusing the
tiles avoids the 460-tile re-download.

**Alternatives considered**:
- *Re-downloading from the LGL open-data portal*: violates FR-022
  and OR-005 (each tile is ~12 MiB; 460 tiles is 5.5 GiB).
- *Switching to a different DOP product (DOP40, DOP60)*: lower
  resolution, fails the 60 m / 300 px kernel arithmetic without a
  recompute and changes lineage.

## R-003 — Building inventory and provenance

**Decision**: Reuse `tables/buildings.geojson` (LGL ALKIS
`Hausumringe`, 93,024 features, EPSG:25832). Pipeline asserts
`source == "LGL ALKIS Hausumringe"`, `crs == EPSG:25832`, and
`feature_count == 93024`. The pipeline clips to the buffered
boundary and de-duplicates by stable id.

**Rationale**: Direct match to the spec's evidence statement
("93,024 official building footprints") and to `meta.json`
(`buildings.feature_count: 93024`).

**Alternatives considered**:
- *OSM buildings*: not the official inventory, fails FR-004.
- *Re-downloading ALKIS*: violates FR-022.

## R-004 — Boundary, halo, and publication clip

**Decision**: Use `boundary.geojson` as the official boundary and
`boundary_buffered.geojson` (= boundary ∪ 60 m exterior) as the
analysis boundary. The published bundle clips all layers to the
official boundary, never the buffered one (FR-007).

**Rationale**: Matches FR-006 and FR-007. The buffered boundary
exists only to scope the imagery-read job.

**Alternatives considered**:
- *Tight clip without halo*: would yield 0% canopy for any
  boundary-touching building, failing SC-004 for those.
- *Publish the buffered boundary*: violates FR-007, leaks the halo
  into the visible map.

## R-005 — Canopy mask and the RunPod gate

**Decision**: The pipeline does not run the model locally. The
canopy mask is a derived artifact that fails FR-021 in the mannheim
workspace (0.48% canopy pixels — the healthy urban tree-cover
share is 5–15%). The pipeline ships a `canopy.py` module with a
`requires_runpod: true` marker. When the maintainer supplies a
RunPod endpoint, the job runs `model.predict()` on the existing
`deepLabV3plus-resnet34` weights (no retraining, FR-024/025) and
returns a 0.2 m binary mask in EPSG:25832.

**Rationale**: FR-024 forbids new training; FR-025 forbids local
inference; OR-003 forbids local GPU. The 0.48% failure is the
trigger to re-run on RunPod.

**Alternatives considered**:
- *Local CPU inference*: would exceed OR-001 (the 460-tile mosaic
  at 5000×5000 px is 222 MiB on disk and ~10 GiB in memory if not
  chunked). Even chunked, the model run is slow and produces
  suspect quality.
- *Use the failed mask anyway*: violates FR-021.
- *Train a fresh model*: violates FR-024.

## R-006 — 60 m value calculation: chunking strategy

**Decision**: For each buffered-boundary tile (1000 m × 1000 m
grid aligned to imagery), read the canopy mask chunk and the
imagery-derived halo, run `fftconvolve` on a 300 px circular kernel
inside the chunk with reflective padding at the chunk boundary
(matches the reference's `neighbourhood` method), write a
`pct.tif` chunk for that tile, then zonal-mean over the building
footprints intersecting the chunk. Final values are gathered
into a single GeoJSON file.

**Rationale**: Same arithmetic as `meta.json.neighbourhood`.
Reflective padding at the chunk border approximates the
infinite-plane convolution well enough that a 1000 px chunk
exposes at most the outermost 300 px of buildings to a small
boundary error, which the chunk's overlap with the next tile
absorbs.

**Alternatives considered**:
- *Single fftconvolve on the full mosaic*: violates OR-002.
- *Vector zonal stats only (no convolution)*: fails FR-005
  (the metric is the disc mean, not the polygon mean).

## R-007 — Tree areas and publication clip

**Decision**: Polygonize the accepted canopy mask with
`rasterio.features.shapes` to a GeoJSON file, clip to the official
boundary, convert to PMTiles via `tippecanoe`. The published
PMTiles contains only polygons inside the official boundary.

**Rationale**: Matches FR-015 (flat green tree layer) and FR-007
(no halo leakage). `tippecanoe` is the standard PMTiles generator
and the maintainer already has the toolchain to install it.

**Alternatives considered**:
- *Publish the raw canopy mask as a raster tile layer*: violates
  the "tree areas appear in flat green" presentation in FR-015
  and would require a custom style.

## R-008 — Static basemap

**Decision**: Use `basemap.de` dark style for the base map
(attribution: `Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0` for
the buildings, and `basemap.de` for the base). The map style
combines a MapLibre `NavigationControl` (zoom + north reset) with
custom layers for the boundary mask, buildings, and tree areas.

**Rationale**: `meta.json.links.basemap = "https://basemap.de"`.
The basemap's dark style is the closest match to the
StadtBegruenung reference's "dark appearance" and is the same
provider the reference uses.

**Alternatives considered**:
- *Mapbox dark style*: requires a token, violates FR-001
  (no accounts) and "no application servers".
- *Custom raster basemap*: would need a tile server, violates
  the out-of-scope "no application server" rule.

## R-009 — Buildings PMTiles

**Decision**: Generate `buildings.pmtiles` via `tippecanoe` from
the published buildings GeoJSON (post-clip, post-value-join).
Zoom range 12–18 matches the published-map zoom band. Each
feature carries `id`, `value` (string, two decimals, or `null` for
no-data), and `has_value` (boolean).

**Rationale**: PMTiles + MapLibre is the reference's delivery
format (`meta.json.links.buildings_pmtiles` references
`buildings.pmtiles` directly). PMTiles is single-file, HTTP-range
served, and needs no tile server.

**Alternatives considered**:
- *Serve buildings as a single GeoJSON file*: would be ~100 MiB
  pre-clip, exceeds OR-005.
- *MVT served from a server*: violates the no-server rule.

## R-010 — Frontend hosting

**Decision**: Plain static hosting. No application server, no
database, no analytics, no auth. The maintainer can drop the
`src/site/` directory plus the published `dist/` bundle onto any
static host (GitHub Pages, Netlify, or a one-line
`python -m http.server` for local preview).

**Rationale**: FR-001 and the explicit out-of-scope list.

**Alternatives considered**:
- *Single-page app with code-splitting*: not needed for one page
  with one map. The maintainer's static host can serve the whole
  bundle in a few hundred KiB.

## R-011 — Acceptance-state propagation

**Decision**: Each artifact carries an acceptance record in
`artifacts.manifest.json`:

```json
{
  "path": "…",
  "size_bytes": …,
  "sha256": "…",
  "source": "…",
  "acceptance": "pass|fail|pending",
  "checks": {
    "source": "ok|fail",
    "extent": "ok|fail",
    "resolution": "ok|fail",
    "completeness": "ok|fail",
    "lineage": "ok|fail"
  },
  "invalidates": ["…", "…"]
}
```

A failed acceptance on a derived artifact marks every dependent
as `pending`; independent accepted inputs stay `pass`. The
`pytest` acceptance suite is the only writer of these records.

**Rationale**: FR-021 requires five explicit checks. FR-023
requires dependent invalidation. The manifest is the single
source of truth that the pipeline reads before deciding to
reuse or regenerate.

**Alternatives considered**:
- *Implicit propagation via file mtime*: no auditable lineage.
- *Ad-hoc CLI flags*: no shared state, no way to verify reuse.

## R-012 — Large-file governance (OR-005)

**Decision**: `.gitignore` excludes `*.tif`, `*.pmtiles`, and
GeoJSON > 50 MiB. The failed `canopy_prediction_mask.tif`
(222 MiB) is never in the repo; its lineage is recorded in the
manifest. Published PMTiles and the official buildings GeoJSON
live in the release bundle, also out of repo. The repo holds
code, contracts, manifests, and small metadata only.

**Rationale**: Direct compliance with OR-005.

**Alternatives considered**:
- *Git LFS*: would push the 222 MiB mask into LFS, violates the
  spirit of OR-005 and still costs LFS bandwidth on every
  clone.
- *Commit anyway with a waiver*: requires the owner to approve
  per OR-005; the plan does not seek that approval.

## R-013 — Commit discipline (OR-004)

**Decision**: `Makefile` targets `commit-spec`, `commit-plan`,
`commit-slice`, `commit-milestone` each `git add` only their
expected files, refuse to commit if other changes are unstaged,
and append a trailing `Spec-NN:` / `Plan-NN:` / `Slice-NN:` /
`Milestone-NN:` tag for traceability.

**Rationale**: OR-004 explicitly requires one commit per
milestone with a single subject. The Makefile makes that
mechanical.

**Alternatives considered**:
- *Pre-commit hook*: harder to bypass when the maintainer
  *needs* to bundle fixes with a milestone commit.
- *Manual discipline*: has been the failure mode that this
  constraint is correcting.

## R-014 — Validation scenarios

**Decision**: `quickstart.md` documents four end-to-end checks
that exercise FR-001..FR-025, OR-001..OR-005, and SC-001..SC-010:
(a) the four user stories from the spec; (b) the 100-building
value recalculation (SC-004); (c) the 20-image canopy sanity
check (SC-005); (d) the local RSS / no-GPU gate (SC-009).

**Rationale**: SCs are the measurable contract. Each SC is a
quickstart scenario.

**Alternatives considered**:
- *End-to-end browser tests with Playwright*: out of scope
  (no analytics, no telemetry, no test framework). The
  quickstart is a manual + scripted run.
