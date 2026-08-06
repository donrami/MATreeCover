# Contract: Publish Bundle and Attribution

Feature 011, FR-010, FR-014, SC-002..SC-009. How the derived data
enters the static bundle without new requests, and how the site
credits it.

## Bundle Additions (new files ≤25 MiB Worker assets; pmtiles stays R2)

| File | Producer | Notes |
|------|----------|-------|
| `dist/stadtteile.geojson` | publish.py | 38 districts, EPSG:4326, stats on properties (district-stats.md) |
| `dist/style.json` | publish.py patch | + `metadata.city_stats` (city-overview.md), + `stadtteile` source |

`buildings.geojson` / `buildings.pmtiles` are **unchanged by feature
011**: the heat-exposure class attribute was removed from scope on
2026-08-06 (clarification Option B), and the shipped `heat_class`
pipeline addition is reverted with the same `make values` /
`make pmtiles-buildings` run.

`scripts/deploy-cf.sh`, `workers/map/wrangler.toml`, and
`workers/map/index.js` need no structural changes: stadtteile.geojson
(373 KB) and style.json ride the ASSETS path; the pmtiles keep their
R2 path. One literal in deploy-cf.sh must be updated back: `cmd_verify`
hard-codes the buildings.pmtiles size for the FR-013 Range gate
('content-range: bytes 0-1023/34524543'), and the revert returns that
file to its pre-feature size (expected 34023835). The release flow
below updates it.

## Pipeline Changes

1. `values.py`: revert to the pre-feature state — remove the
   `heat_class(value)` function and the output attribute. The
   buildings.geojson regenerates via the existing `make values` run
   (idempotent; RSS well under the 12 GiB gate) and returns to its
   pre-feature content.
2. `publish.py`:
   - transform `verification/stadtteile.geojson` (25832 → 4326) with
     the existing pyproj machinery;
   - centroid-in-polygon join of workspace `buildings.geojson` onto
     the districts; compute the three statistics per district;
   - compute city stats from the same join + `trees_polygons.geojson`
     feature count;
   - write `dist/stadtteile.geojson`;
   - patch `metadata.city_stats` and add the `stadtteile` source to
     `available_sources` (else the style quarantine strips it);
   - write `dist/manifest.json` (new artifact entries) and
     `validation/published-map.json` (attribution list gains the
     GDI-MA credit; the controls list drops the removed
     `hitzebelastung-toggle` entry).
3. `artifacts.manifest.json`: new derived artifact entry
   `stadtteile.geojson` (kind `stadtteile`, source "Stadt Mannheim,
   GDI-MA", license dl-de/by-2-0, lineage [verification/stadtteile
   .geojson, buildings.geojson]); acceptance via the existing
   `make accept` gate. Buildings.geojson keeps its pre-feature entry
   unchanged (its sha256/size revert with the regeneration).
4. `REQUIRED_INPUTS` in publish.py gains the repo file
   `verification/stadtteile.geojson` so publish gates on it.

## Acceptance Criteria for New Artifacts (FR-021, five checks)

`stadtteile.geojson` (derived): source contains "GDI-MA" +
"dl-de/by-2-0"; extent = the 38 district bounds; resolution "n/a";
completeness 1.0 (all 38 districts with stats); lineage non-empty.
Enforced in `tests/acceptance/test_districts.py`.

## Attribution Page (`src/site/attribution.html`, then deploy-synced to dist-assets)

1. New h2 "Stadtteile" after "Gebäude und Stadtgrenze":
   "Stadtteile: Stadt Mannheim, GDI-MA, dl-de/by-2-0
   (Daten verändert)" — same credit wording as
   `verification/README.md`.
2. New paragraph in the "Genauigkeit der Baumwerte" section (feature
   010 disclaimer area): the district and city statistics are computed
   from the published building values, so they carry the same
   estimation uncertainty as the values themselves. (The exposure-class
   thresholds sentence was removed with the heat view on 2026-08-06.)
3. Metric caveat in the same paragraph: the 30 % guideline referenced
   by the district and city statistics follows the site's own framing
   ("30 % des 60-m-Umkreises", per the story modal and
   SPIEGEL/CityTreeCover presentation). The supporting evidence
   (3-30-300 rule, Konijnendijk 2022; Barboza et al. heatwave
   mortality) states neighborhood canopy cover; the site's value is
   tree cover in the 60-m surroundings of a building, a related but
   distinct metric (research R-8). The note keeps the two distinct and
   does not claim the evidence applies 1:1 to the buffer metric.

The deployed copy in `dist-assets/attribution.html` stays in sync with
`src/site/attribution.html` (existing prepare-assets rsync handles it).

## Zero-Request Guarantee

Complete request list after this feature (unchanged from today, 11
requests): vendor libs (4), style.css, main.js, style.json (now with
metadata), boundary.geojson, basemap tiles, buildings.pmtiles
range requests, trees.pmtiles (only on toggle), attribution.html (only
on click). stadtteile.geojson is fetched once as a map source, the
same as boundary.geojson. No fonts, no sprite, no new analytics
(SC-007; verified by smoke checklists).

## Release Flow

```text
make values              # buildings.geojson reverts (no heat_class)
make pmtiles-buildings   # buildings.pmtiles back to pre-feature size
make accept              # manifest gate incl. stadtteile.geojson artifact
make publish             # dist/ bundle with stadtteile + metadata
bash scripts/deploy-cf.sh prepare-assets && upload-data
# update cmd_verify's hard-coded buildings.pmtiles size literal to the
# regenerated size (stat -c %s dist/buildings.pmtiles) before verify
npx wrangler deploy --config workers/map/wrangler.local.toml
bash scripts/deploy-cf.sh verify   # FR-013 gate with the updated size
```
