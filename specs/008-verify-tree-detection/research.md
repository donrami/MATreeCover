# Research: Verify Tree Detection Quality

Research date: 2026-08-05. All decisions are codebase-grounded (read of
`src/pipeline/cli.py`, `values.py`, `workspace.py`, `tests/conftest.py`,
DEVELOPMENT.md, the archived workspace layout, `tiles.csv`, the canopy
mask metadata) plus one external lookup (Mannheim district boundary
sources, verified against the city's open-data services on 2026-08-05).
The spec's clarifications (Q1 visual inspection, Q2 repo-only, Q3 no
gating) were resolved before planning; no NEEDS CLARIFICATION remained.
The single genuine unknown — where official Stadtteil boundaries come
from — is resolved in R-2.

## R-1 Verification as pipeline subcommands, not a separate tool

**Decision**: Implement the verification as three new subcommands of the
existing `tree-cover` CLI (`src/pipeline/cli.py`): `verify-sample`,
`verify-render`, `verify-report`, backed by a new module
`src/pipeline/verify.py`. They run under the existing wrapper (RSS gate
OR-001, event log to `validation/event.log.jsonl`, exit codes), exactly
like `accept`, `values`, `trees`, `publish`, `runpod_infer`.

**Rationale**:
- The pipeline is the established home for workspace-data work: it owns
  workspace resolution (`MANNHEIM_WORKSPACE`), the RSS gate, and the
  event log. A separate script would duplicate that machinery or bypass
  the gate (OR-001 violation risk).
- All inputs are existing pipeline artifacts: DOP20 tiles in
  `mosaic/extract/`, the canopy mask `mosaic/canopy_prediction_mask.tif`
  (EPSG:25832, 0.2 m GSD, metadata JSON confirming model/settings), and
  `tables/buildings.geojson` (EPSG:25832, per-building `value` in %).
- The wrapper's event log gives the verification its own auditable trail
  (sample/render/report runs recorded with RSS and exit codes), matching
  how every other pipeline step is documented.
- No new dependencies: rasterio windows, numpy compositing, shapely
  point-in-polygon, pyproj transforms, click — all already in
  `pyproject.toml`.

**Alternatives considered**:
- A standalone `scripts/verify-*.py` set: rejected — bypasses the
  wrapper's RSS gate and event log, and the repo convention is that
  pipeline data work lives in the CLI.
- A new package: rejected — one module plus three registrations is the
  established pattern; a package is over-structure.

## R-2 District boundaries: official GDI-MA Stadtteile, dl-de/by-2-0

**Decision**: Use the official Mannheim Stadtteil boundary layer from the
city's geodata infrastructure (GDI-MA), license dl-de/by-2-0 — the same
license family as the LGL data already credited in the README. The layer
is downloaded once at implementation time, reprojected to EPSG:25832,
and committed as a small GeoJSON at `verification/stadtteile.geojson`
with the attribution recorded in `verification/README.md` and the
report. If the WFS is unreachable, the download procedure falls back to
the GDI-MA OGC service list and GeoNetwork catalog (both published by
the city).

**Rationale**:
- The spec requires per-district stratification and findings across "all
  districts with buildings" (FR-003/FR-004). Mannheim is administratively
  divided into 38 official Stadtteile (statistical codes 011–174, the
  city's own classification); the Reddit discussion that motivated this
  feature speaks in Stadtteil terms, so the official Stadtteil layer is
  the right unit.
- The repo has no district data today (verified: no Stadtteil geometry
  anywhere in `src/` or the workspace — only the city boundary
  `boundary.geojson`), so this is a new, small, one-time input.
- License fit: the repo already ships LGL data under dl-de/by-2-0 with
  attribution in README/attribution; GDI-MA open data uses the same
  license (verified on the Mannheim open-data portal metadata, e.g. the
  Stadtteil statistical datasets carry `license: dl-de-by 2.0`). One
  license family, one attribution pattern.
- Committed GeoJSON keeps the verification reproducible and offline: no
  runtime dependency on a city web service, and the file is small
  (city-district boundaries, well under 50 MiB — OR-005 clean).

**Alternatives considered**:
- OpenStreetMap Stadtteil relations via Overpass: rejected — ODbL
  attribution and share-alike obligations on a public repository are
  friction the official dl-de/by-2-0 source avoids; the official layer is
  also the one the city itself uses for Stadtteil statistics.
- Approximate districts (grid cells, quadrants): rejected — FR-003
  requires findings per district, and the whole point (per the Reddit
  discussion) is real district differences; an approximation would
  mislead.
- GADM admin boundaries: rejected — GADM has no Stadtteil level for
  Mannheim.

**Discovery procedure (implementation step, exact endpoint not pinned
today)**: enumerate the GDI-MA WFS/WMS service list at
`https://www.gis-mannheim.de/mannheim/mod_ogc/index.php`, locate the
Stadtteile/Stadtbezirke feature type, fetch as GeoJSON (EPSG:25832 or
transform via pyproj), verify 38 features with names and 3-digit
Stadtteil codes, record source URL + license + download date in
`verification/README.md`. Fallback: search the GeoNetwork catalog at
`service.gis-mannheim.de` for "Stadtteile". Direct WFS endpoint guesses
(`geodaten.gis-mannheim.de/geoserver/…`) did not resolve on 2026-08-05;
the service list is the canonical entry point.

## R-3 Sample design: 100 patches, district × value-band stratification

**Decision**: Fixed sample of 100 patch centers. Strata: 38 official Stadtteile ×
3 building-value bands `[0,10)`, `[10,30)`, `[30,100]` % (matching the
map's legend semantics and the reference project's 10/30 thresholds).
Allocation: district share proportional to the district's building count,
with a floor of 1 patch per district that has buildings (all 38 do),
remainder by largest remainder; within a district, patches split across
the district's non-empty value bands proportionally to band building
counts. Patch centers are drawn uniformly at random from the centroids
of the buildings in the stratum, with a fixed seed (default
`20260805`) recorded in the sample file. Points outside the imagery
extent are resampled deterministically (seed continues); the resample is
recorded.

**Rationale**:
- FR-004: "cover all districts with buildings, in proportion to their
  share of the city" — proportional allocation by building count is the
  direct reading; the floor of 1 keeps every district present with at
  least a minimal signal (small districts are then flagged as
  inconclusive per the edge cases, not silently dropped).
- Value bands: the published values are right-skewed with a long tail
  (verified directly from the derived `buildings.geojson` on 2026-08-05:
  mean 22.2 %, median 20.8 %, 16.2 % of buildings < 10 %, 24.1 % >= 30 %,
  p99 58.6 %; an earlier claim of a 2.2 % mean, taken from the reference
  workspace's archive `statistic.json`, does not describe this pipeline's
  published values and is retracted here). The 30-100 band holds only a
  quarter of buildings, so an unstratified sample would under-represent
  the high-value tail where the district extremes (Reddit thread) live;
  the bands guarantee coverage there. Fixed bands beat quantiles: stable
  across runs, 10/30 match the legend the map already shows.
- Building centroids as the sampling frame: buildings are the map's unit
  of analysis, the centroid lands the patch in the building's actual
  surroundings, and `tables/buildings.geojson` already carries both
  geometry and `value`.
- Fixed seed + deterministic algorithm make the sample reproducible
  (FR-004, SC-002): re-running `verify-sample` with the same seed
  produces a byte-identical sample file.

**Alternatives considered**:
- Uniform random points over the city area: rejected — area weighting
  would under-represent dense districts and, unlike building centroids,
  would often land patches on fields/harbor/forest with no building
  context.
- Pure random sample, no stratification: rejected — would under-represent
  the high-value tail (mean 22.2 %, only a quarter of buildings at or
  above 30 %).
- Post-stratification weighting instead of allocation: rejected —
  allocation guarantees per-district presence up front, which is what the
  report needs.

## R-4 Patch rendering: 1024-px windows, windowed reads, mask overlay

**Decision**: Each patch is a 1024×1024-px review window (204.8 m at
0.2 m GSD) centered on the sampled building centroid, EPSG:25832.
`verify-render` reads the overlapping DOP20 tile(s) via rasterio windows
(never full tiles), and composites the binary canopy mask at 50 % alpha
in a distinct color over the RGB imagery, writing one PNG per patch to
`verification/patches/` (gitignored). Patch file name embeds the sample
row id. Degenerate patches (no imagery coverage, or empty/full mask
within the window) are still rendered and flagged in the sample record —
never silently excluded (FR-008).

**Rationale**:
- The 1024-px size matches the inference patch size used to produce the
  mask (spec's motivating discussion: 1024 px patches, 64 px overlap),
  so a window shows exactly the model's native decision context.
- Windowed reads keep RSS orders of magnitude below the OR-001 12 GiB
  gate: a full 2-km tile at 20 cm is ~10k×10k px (~300 MB/band as
  uint8); a window is ~1 MB/band. No full-tile load ever happens.
- The mask is the direct source of the published tree layer (the `trees`
  subcommand polygonizes exactly this mask into `trees_polygons.geojson`
  → `trees.pmtiles`), so reviewing the mask overlay IS reviewing the
  published Bäume layer (FR-001: "exactly as used for the published
  map").
- 50 % alpha overlay on true-color imagery is the standard, legible way
  to compare detection against reality; no external viewer needed.
- PNGs are review aids, not evidence artifacts: gitignoring them (OR-005)
  keeps the repo small while sample/ratings/report (the evidence) are
  committed.

**Alternatives considered**:
- Side-by-side imagery/mask pairs: rejected — overlay is what the map's
  Bäume toggle shows; reviewers should judge the same visual the
  visitors see.
- Full-resolution mosaics per district: rejected — huge, unnecessary;
  windows are the review unit.
- Web-based viewer (e.g., local MapLibre page over PMTiles): rejected —
  the Bäume toggle on the live map already provides this; the offline PNG
  set is simpler, deterministic, and works without serving infrastructure.

## R-5 Ratings and report: JSONL schema, 3 categories, generated report

**Decision**: Ratings live in `verification/ratings.jsonl`, one JSON
object per patch: `{patch_id, district_code, district_name, value_band,
rating, note, ts}` with `rating ∈ {correct, over, under}` (documented
criteria in `contracts/verify-ratings.md`). `verify-report` reads
ratings + the owner-written `verification/notes.md` (comparison with the
model author's cross-city warning, limitations writeup) and generates
`verification/report.md`: sample summary, overall rating counts, a
per-district table (n, rating distribution, value-trust assessment
trustworthy/overstated/understated where the distribution supports it),
flagging districts where fewer than half of the patches are rated
`correct`, and the mandatory disclosure list. A re-inspection subset
(10 patches) is part of the procedure; divergence is documented in the
report (FR-008).

**Rationale**:
- JSONL is the repo's existing record format (validation event log is
  JSONL) and is diff-friendly for a human-edited ratings file.
- Exactly three rating values, as the spec mandates (FR-002); the note
  field carries nuance. No invented "mixed" category.
- Report generation from the ratings file makes the report reproducible
  and prevents hand-edited number drift; the qualitative sections
  (comparison, limitations) come from the owner's notes file, which is
  the honest place for judgment (SC-003: report documents its own
  limitations).
- The 50 % flagging rule is a simple, documented, defensible threshold
  (FR-003: districts whose detection quality differs from the overall
  level are flagged); the overall level is the city-wide share of
  `correct` ratings, so the rule compares like with like.
- Re-inspection of a fixed subset (every 10th patch, documented) is the
  concrete reproducibility check for a manual process (spec edge case;
  FR-008).

**Alternatives considered**:
- Free-form text report only: rejected — no per-district structure, not
  reproducible, violates FR-003.
- Rating scale with severity levels: rejected — spec fixes three
  categories; more categories would need justification the spec does not
  give.

## R-6 Verification artifacts and repo hygiene

**Decision**: All verification outputs live in a new top-level
`verification/` directory (mirroring the existing `validation/`
convention): committed files `README.md`, `stadtteile.geojson`,
`sample.jsonl`, `ratings.jsonl`, `notes.md`, `report.md`; gitignored
`patches/`. `.gitignore` gains `verification/patches/`.

**Rationale**:
- The workspace is an archived, read-only mirror (DEVELOPMENT.md:
  "read-only is sufficient"); writing verification outputs there would
  mutate the archive and fight its purpose.
- `verification/` mirrors `validation/` (events) — a reader immediately
  sees the pairing; the report is the durable evidence, the event log is
  the audit trail.
- OR-005: committed files are all small; the only bulky artifacts (PNGs)
  are gitignored.
- FR-010 (`make check-public`): report and notes are written to be
  public-safe; no personal paths, credentials, or internal tooling
  references (accepted via the existing scan in acceptance).

**Alternatives considered**:
- `validation/` reuse: rejected — that directory is the pipeline's event
  log; mixing artifacts in would blur the audit trail.
- Workspace subdirectory: rejected — archive is read-only.
