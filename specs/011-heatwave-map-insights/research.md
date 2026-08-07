# Research: Heatwave Map Insights

Research date: 2026-08-06 (updated after the 2026-08-06 clarification
that removed the Hitzebelastung view). Decisions are codebase-grounded
(read of `src/pipeline/{values,publish,cli,verify}.py`, `src/site/
{style.json,main.js,index.html,style.css,attribution.html}`, Makefile,
`scripts/deploy-cf.sh`, `tests/acceptance/*`, `tests/pipeline/*`,
`tests/frontend/*`, `validation/perf-budget.json`) plus a live
recomputation of the derived statistics from the accepted dataset
(93,022 buildings, 56 of them without a value; 38 official Stadtteile).
The spec is self-contained: no external data sources (spec Out of
Scope), so there are no external unknowns.

## Scope change (2026-08-06 clarification, Option B)

The originally planned "Hitzebelastung" heat-exposure view (per-building
exposure classes, view toggle, class legend, popup class line) was
**removed from scope**: it re-encodes the same per-building `value`
with no new information and adds a second toggle that risks confusing
users. The 30 % guideline stays visible as the existing legend tick and
through the district and city statistics. This research documents the
surviving design and the revert surface for the code that was already
shipped with the heat view.

## R-1 Heat-exposure view: removed, and the shipped code reverted

**Decision**: No exposure-class view. Remove every trace of it from the
codebase: `values.py` loses the `heat_class` function and output
attribute (buildings.geojson regenerates to its pre-feature state),
`main.js` loses `CLASS_LABEL`, `HEAT_FILL_COLOR`, the paint-swap toggle
and the popup class line, `index.html` loses the "Hitzebelastung"
button and the class legend block, `style.css` loses the class legend
and toggle styles, `tests/pipeline/test_heat_class.py` is deleted, the
heat-class assertions in `tests/acceptance/test_values.py` and
`tests/acceptance/test_style.py` are removed, the README and
attribution copy is trimmed, `validation/perf-budget.json` drops the
heat-toggle interaction keys, and `scripts/deploy-cf.sh` reverts its
buildings.pmtiles size literal to the regenerated size.

**Rationale**:
- The class view derives from the same `value` attribute as the default
  view; it contains no new information (spec clarification 2026-08-06).
- The 30 % guideline is already a labeled tick (30) on the default
  legend; the guideline story is carried by the district popup
  ("Anteil unter 30 %") and the city panel ("Gebäude mit ausreichender
  Beschattung (30 %)").
- Keeping the code would leave a dead feature and its test surface in
  the bundle; reverting is cheaper than maintaining it.

**Alternatives considered**:
- Keep the view (Option A): rejected by the owner; the encoding fix it
  offered (class colors matching the README's red/orange/green wording)
  is cosmetic, not functional.
- Recolor the default map with the class palette and drop the toggle
  (Option C): rejected, it changes the published `buildings-fill`
  palette, which the default-view contract pins verbatim (SC-004).

## R-2 District statistics: joined at publish time, shipped on the district features

**Decision**: publish.py derives `dist/stadtteile.geojson` from the
committed `verification/stadtteile.geojson` (official GDI-MA, 38
features, EPSG:25832), reprojected to EPSG:4326 with the existing
pyproj transform machinery (same code path as `dist/boundary.geojson`),
with one statistics block per district property:

- `n_buildings`: count of buildings whose centroid lies in the
  district (reference run: all 93,022 assigned)
- `mean_value`: mean tree-cover value, 1 decimal, over buildings with
  a value (null if a district has no valued buildings)
- `share_lt30`: percent of valued buildings below the 30 % guideline,
  1 decimal

Reference values (recomputed 2026-08-06): range 9.6 % (Innenstadt,
98.2 % below guideline) to 34.5 % (Niederfeld); the full 38-row table
is reproducible from the accepted `buildings.geojson`.

**Rationale**:
- FR-010 / SC-007 forbid new network requests; district stats on the
  district feature properties ride on the one `stadtteile.geojson`
  request that the district layer needs anyway.
- Centroid-in-polygon assignment is the same method used in the
  verification workflow; it is deterministic and reproducible
  (SC-002: independent recomputation within 0.5 pp / 1 pp).
- 373 KB fits the ≤25 MiB Worker-asset path: zero deploy-script changes
  beyond the pmtiles size literal (deploy-cf.sh picks new files up via
  rsync).

**Alternatives considered**:
- A separate `dist/stats.json` fetched by the client: rejected, it is
  a new network request.
- District stats computed client-side from building tiles: rejected,
  buildings are range-requested per viewport, so city-wide stats would
  be wrong and non-deterministic.

## R-3 District layer: plain GeoJSON source, one transparent fill layer

**Decision**: style.json gains a `stadtteile` GeoJSON source
(`stadtteile.geojson`) and one layer `stadtteile-fill` (transparent
fill, no stroke, placed between `outside-mask` and `buildings-fill`),
interactive via a layer-filtered click handler. publish.py's
`available_sources` set gains `'stadtteile'` so the source survives the
style.json quarantine rewrite. The map-level click handler is reworked:
a click hits the district when no building is hit, opening the district
popup and closing the building popup; a click on empty space closes
both.

**Rationale**:
- MapLibre queries features of `visible` layers regardless of paint
  opacity, so a fully transparent fill provides hit-testing without
  changing the render (SC-004: default appearance unchanged).
- Below `buildings-fill`, building clicks keep priority; the district
  is the fallback for clicks between buildings.
- The 38 GDI-MA districts are already committed and used by verify.py;
  no new data acquisition.

**Alternatives considered**:
- A `stadtteile.pmtiles` via tippecanoe: rejected, unnecessary for a
  373 KB layer; the plain GeoJSON source matches the existing
  `boundary` source pattern.
- District click via `map.on('click', 'stadtteile-fill')` plus keeping
  the old close handler: rejected, the old handler would close the
  district popup immediately (it removes the building popup on any
  click without a building).

## R-4 City overview: style.json metadata, same patch point as mannheim_bbox

**Decision**: publish.py writes `metadata.city_stats` into the
published style.json (same patch point as the existing
`metadata.mannheim_bbox`):

- `mean_value_pct`: 22.2 (city mean, 1 decimal)
- `share_gte30_pct`: 24.1 (percent of valued buildings at or above the
  30 % guideline, 1 decimal)
- `tree_count`: 153524 (feature count of the accepted
  `trees_polygons.geojson`)

The overview panel reads the values from `map.getStyle().metadata` and
renders static German text.

**Rationale**:
- style.json is already fetched by every visitor; zero new requests
  (FR-010 / SC-007).
- The metadata patch point exists and is exercised (mannheim_bbox).
- Reference numbers were recomputed from the accepted dataset on
  2026-08-06 (mean 22.2 %, 24.1 % at or above 30 %, 153,524 tree
  areas).

**Alternatives considered**:
- Hardcoded numbers in index.html: rejected, two sources of truth and
  no publish-time derivation.
- A separate stats file: rejected (new request, see R-2).

## R-5 Popup enrichment: district lookup from the already-loaded source

**Decision**: The building popup gains two lines when the building
lies in a district: district name and district mean. Lookup via
`map.querySourceFeatures('stadtteile')` at the clicked coordinate (no
fetch). Buildings outside all districts (none in the current data,
handled defensively) and buildings without a value keep the existing
fallbacks.

**Rationale**: FR-009 wants the context; the district source is loaded
for R-3 anyway, so the enrichment costs zero requests and reuses the
R-2 statistics. Consistency: the district mean shown in the building
popup equals the value in the district popup (same property).

## R-6 Attribution and copy: credit and derivation note

**Decision**: attribution.html gains (1) a new h2 "Stadtteile" section
after "Gebäude und Stadtgrenze" crediting "Stadt Mannheim, GDI-MA,
dl-de/by-2-0" (the attribution already used in verification/README.md),
and (2) a derivation note next to the "Genauigkeit der Baumwerte"
section explaining that the district and city statistics are computed
from the published building values and therefore carry the same
estimation uncertainty as the values themselves. All new copy is
German with no em-dashes or en-dashes (feature 007 convention; the
popup's existing en-dash UNAVAILABLE constant is untouched).

**Rationale**: FR-014 is a scope requirement; the attribution page is
the established home (feature 010 added the accuracy disclaimer
there). The 30 % guideline referenced by the district and city
statistics follows the site's own framing ("30 % des 60-m-Umkreises",
per the story modal and SPIEGEL/CityTreeCover presentation); the
supporting evidence (3-30-300 rule) states neighborhood canopy cover,
a related but distinct metric, so the note keeps the two distinct
(see R-8).

**Alternatives considered**: putting the derivation note in the legend:
rejected, the legend stays compact; the attribution page is linked
from the legend note.

## R-7 Test and verification surface

**Decision**: Extend the existing suites rather than add new
frameworks: `tests/acceptance/test_districts.py` checks the published
stadtteile layer (38 features, EPSG:4326, stats present and consistent
with the accepted building values, SC-002, and the city-stats
invariant SC-003); `tests/acceptance/test_style.py` pins the
`stadtteile-fill` layer position and the `#city-panel` presence; a new
manual checklist `tests/frontend/smoke_us6.md` covers the district
popup, city panel, popup enrichment, a11y, and no-overlap (project
convention: manual smoke checklists logged into
validation/event.log.jsonl). The heat-class tests
(`tests/pipeline/test_heat_class.py`, the SC-001 assertions in
`test_values.py`, the class-legend assertions in `test_style.py`) are
removed with the revert (R-1). Perf re-measurement keeps
`interaction_latency_ms` with `district_click` and `panel_render`
(SC-006; method from validation/perf-budget.json: CDP throttled
25 Mbps / 50 ms, cold cache, 2 000 ms budget).

**Rationale**: the repo's pyramid is acceptance pytest for data and
style contracts plus manual smoke checklists for browser behavior; the
feature's data derivations (district stats, city stats) are exactly
the kind of contract the acceptance suite defends, and the new
interactions are exactly the kind the smoke checklists cover. SC-008
(existing suites green, check-public clean) is the regression gate.

**Alternatives considered**: browser automation for the smoke checks:
rejected, the project convention is manual checklists (no Playwright
etc. in the bundle contract).

## R-8 Literature grounding for the 30 % guideline (external, non-blocking)

Status note: an automated literature-search pass was attempted but is not
operational in this environment (no search backend configured). The
findings below come from built-in web search with cited sources, not
an automated consensus review. Primary sources not yet read in full;
claims marked
accordingly.

**Decision**: keep the 30 % anchor used by the district and city
statistics; add the metric-caveat sentence to the attribution note
(see publish-bundle.md). The evidence supports the guideline's
direction but is metric-distinct from the site's 60-m-buffer value,
and the site must not present them as identical.

**Findings**:

- The canonical guideline is the 3-30-300 rule (Konijnendijk 2022,
  J. Forestry Research): 3 trees visible from every home, 30 % canopy
  cover as a minimum at neighborhood level, 300 m to green space.
  `link.springer.com/article/10.1007/s11676-022-01523-z`
- Heatwave-specific support: a Europe-wide study (Barboza et al.)
  found 30 % canopy coverage associated with about one-third lower
  mortality during heatwaves. Reported via secondary sources
  (Arboriculture & Urban Forestry 50(3):241 and Nature Communications,
  Croeser et al. 2024, doi 10.1038/s41467-024-53402-2); primary paper
  not yet verified. [INFERENCE on exact effect size]
- Caveat: the 3-30-300 30 % figure is neighborhood canopy cover
  (area-based). The site's metric is tree cover in the 60-m
  surroundings of a building (buffer-based, building-weighted). The
  two are related but not identical; the site's story modal already
  frames the guideline as "30 % des 60-m-Umkreises". The attribution
  note keeps the metrics distinct.

**Impact on design**: none for R-2..R-7.
