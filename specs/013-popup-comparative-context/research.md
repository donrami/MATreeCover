# Research: Popup Comparative Context

Phase 0 output for `specs/013-popup-comparative-context`. All decisions are grounded in the
published bundle (`dist-assets/` mirrors `dist/`), the source (`src/site/main.js`,
`src/site/style.css`), and the verified reference computation below. No pipeline, data, or
publish-time changes are made; every metric derives from data already in the bundle.

## Verified input facts (evidence)

- `dist/stadtteile.geojson`: 38 features; properties `code`, `id_name`, `name`,
  `mean_value` (1 decimal, 38/38 present), `n_buildings`, `share_lt30`. Source
  `stadtteile` already in `style.json` with layer `stadtteile-fill` (transparent, queryable).
- `style.json` `metadata.city_stats`: `mean_value_pct: 22.2`, `share_gte30_pct: 24.1`,
  `tree_count: 153524` (verified in `dist-assets/style.json`; consumed today by
  `renderCityPanel()` via `map.getStyle().metadata.city_stats`).
- `verification/stadtteile.geojson`: 38 districts, geometry only (`code`, `id_name`,
  `name`) — the SC-003 cross-check asset.
- Current popup renderers in `src/site/main.js`: `buildingPopupHtml(props)` (value line
  only), `buildingDistrictHtml(lngLat)` (district name + mean via `districtAt()`
  = `querySourceFeatures('stadtteile')` + `pointInPolygon`), `districtPopupHtml(props)`
  (4 lines). Handlers/arbitration per feature 011: building click wins over district,
  empty-space closes; one popup instance per type (`closeOnClick: false`).
- Formatting helpers already present: `formatPercent` (dot decimal), `formatInteger`
  (thin-space thousands), `escapeHtml`, `UNAVAILABLE = '\u2013'` (en dash).
- `dist/main.js` is a plain copy of `src/site/main.js` (no build tool) and its functions
  are top-level declarations — loadable in a node VM with minimal stubs.
- Node v22.22.1 available in the environment (verified) — the SC-003 JS cross-check can
  run without a browser.

## R-1 Full 38-district set for rank computation

**Decision**: At map load, `fetch('stadtteile.geojson')` once (the same URL the style's
`stadtteile` source already loads, so the browser serves it from cache — no new network
transfer) and compute a module-level `districtRankings` map (`code` → `{rank, quartile}`).
On fetch failure, set `districtRankings = null`; district popup then hides rank/quartile
lines (defensive degradation, spec Edge Cases).

**Rationale**: Rank/quartile need all 38 districts. `map.querySourceFeatures('stadtteile')`
returns only viewport-intersecting features, so at high zoom it is incomplete. A one-time
fetch of the already-cached bundle file is deterministic, uses only public APIs, and adds
no data beyond what the bundle already contains.

**Alternatives considered**:
- `map.getSource('stadtteile').serialize().data` — zero fetch, but the vendored 5.7.1
  bundle is minified and `GeoJSONSource.serialize()`'s return shape is not documented;
  rejected as fragile.
- Union of `querySourceFeatures` calls across zooms — complex, racy, still not guaranteed
  complete; rejected.

## R-2 Rank and quartile algorithm

**Decision**:
1. Filter districts with `mean_value != null`.
2. Sort by `mean_value` descending, then `name` ascending (FR-009 tie-break). Comparison
   order must be identical in JS and Python: JS `<` on strings compares UTF-16 code units,
   Python compares code points — identical for all 38 names (all BMP, umlauts are single
   code points). Documented as the reproducibility contract.
3. Assign sequential ranks 1..N (ties get distinct ranks — e.g. Friedrichsfeld and
   Neckarau at 21.5 rank 20 and 21, alphabetical).
4. Quartile band from rank and N (FR-010, proportional for N != 38 per Assumptions):
   `q1 = ceil(N/4)`, `q2 = floor(N/4)`, `q3 = floor(N/4)`, remainder to the last band.
   Bands: 1..q1 "oberstes Viertel", q1+1..q1+q2 "oberes Mittelfeld",
   q1+q2+1..q1+q2+q3 "unteres Mittelfeld", rest "unterstes Viertel".
   For N = 38: 10/9/9/10 → 1-10, 11-19, 20-28, 29-38 (matches FR-010).
5. Fewer than two valid district means → no rankings at all (rank/quartile hidden,
   spec Edge Cases).

**Rationale**: Deterministic and reproducible; matches FR-009/FR-010 and the spec's
"distinct sequential ranks" edge case exactly.

**Alternatives considered**: percentile-based bands from mean values — rejected, spec fixes
rank-based bands; competition ranking (shared ranks) — rejected, spec demands distinct
sequential ranks.

## R-3 Delta classification and formatting

**Decision**:
- Delta = building value (from `value_str`, 2 decimals) − reference mean (1 decimal), or
  district mean − city mean. Computed on raw numbers.
- Classification per FR-003/FR-004/FR-008: `delta > +0.1` → "über", `delta < −0.1` →
  "unter", `|delta| <= 0.1` → "auf …-Niveau". The FR wording (`<= 0.1`) is normative over
  the Edge Cases wording (`< 0.1`).
- Display: neutral → `±0.0 pp`; otherwise sign + magnitude rounded to 1 decimal with
  half-up on the magnitude (`Math.abs(delta).toFixed(1)`), minus sign U+2212 ("−2.3 pp"),
  plus sign "+". Display is derived from the *classification* (neutral always shows
  `±0.0 pp`), so word and number can never contradict (a raw +0.10 delta shows
  "auf …-Niveau" + "±0.0 pp", never "+0.1 pp").
- Dot-decimal kept: the acceptance scenarios' "−2,3 pp"/"±0,0 pp" commas are artifacts;
  Assumptions and US1-S1's "dot-decimal per convention" are normative (no German-comma
  reform).

**Rationale**: One rule set for all three comparison kinds (FR-003, FR-004, FR-008);
prevents misleading signs from rounding; consistent with the existing dot-decimal
formatting.

**Alternatives considered**: rounding first, then classifying the rounded delta —
rejected, can mislabel |raw delta| = 0.05 → "±0.0 pp" as "über" if rounding went up.

## R-4 Assessment words and popup hierarchy (FR-013)

**Decision**: Fixed German copy per comparison kind:

| Kind | über | unter | neutral |
|------|------|-------|---------|
| Building vs district | über dem Stadtteil-Durchschnitt | unter dem Stadtteil-Durchschnitt | auf Stadtteil-Niveau |
| Building vs city | über dem Stadtdurchschnitt | unter dem Stadtdurchschnitt | auf Stadtniveau |
| District vs city | über dem Stadtdurchschnitt | unter dem Stadtdurchschnitt | auf Stadtniveau |

Hierarchy (both popups): name header → headline value → badge → context lines (comparisons,
then existing stats) → footnote. Badge = 30 % status on building popup (FR-005), quartile
band on district popup (FR-010). Every colored element carries its text label (FR-013).

**Rationale**: Exact words per spec; hierarchy is the spec's In-Scope list; consistent
across both popups.

## R-5 City stats access and degradation (FR-014)

**Decision**: `cityStats()` reads `map.getStyle().metadata.city_stats` at render time and
returns `mean_value_pct` (number) or `null` — same source as `renderCityPanel()`, so popups
and the "Mannheim im Überblick" panel can never contradict (Assumptions). When `null`,
all city-comparison lines are hidden in both popups. District rank/quartile are computed
from `stadtteile.geojson` (not city stats), so they still render — satisfying FR-014's
"rank/quartile still render" even with stale city metadata.

**Rationale**: One reference for city average; independent data paths for city lines and
district rankings match FR-014 exactly.

## R-6 Building popup restructure

**Decision**: Merge `buildingPopupHtml(props)` + `buildingDistrictHtml(lngLat)` into a
single `buildingPopupHtml(props, lngLat)` that renders: district name header (FR-002);
headline label "Baumanteil im 60-m-Umkreis" + value (FR-001, unavailable marker when
`has_value === false`, never a fabricated value — FR-006); badge "erreicht"/"verfehlt"
only when a value exists, threshold `value >= 30` counts as erreicht (FR-005, edge case);
comparison lines district (FR-003) and city (FR-004) with average, signed delta, assessment
word — only when a value exists (FR-006: no deltas without value; district context lines
still render); footnote (FR-012). The building click handler changes from
`buildingPopupHtml(p) + buildingDistrictHtml(lngLat)` to the single call; arbitration,
close button, tooltip, hover cursor untouched (FR-015).

**Rationale**: One renderer, one source of truth for the popup body; keeps the existing
district lookup (`districtAt`) and unavailable-marker semantics.

## R-7 District popup restructure

**Decision**: `districtPopupHtml(props)` gains: name header (existing), mean headline
("keine Daten" when `mean_value == null` — FR-011), quartile badge when ranked, rank line
"Platz X von 38" (FR-009), city comparison line with average + signed delta + word
(FR-008), then existing "Gebäude" and "Anteil unter 30 %" lines (FR-007). District without
mean: name + building count only, mean marked unavailable, rank/quartile/city hidden
(FR-011). Rankings looked up by feature property `code` (present on all 38 features,
verified).

**Rationale**: Spec-mandated content set; `code` is the stable key.

## R-8 Footnote copy (FR-012)

**Decision**: Both popups end with a "Was bedeutet das?" block. Building popup:
"Der Baumanteil im 60-m-Umkreis ist der Anteil der Baumkronen an der Fläche im Umkreis von
60 m um das Gebäude. Ab 30 % gilt die Beschattung als ausreichend." District popup:
"Der Baumanteil im Durchschnitt ist der mittlere Baumanteil im 60-m-Umkreis aller Gebäude
in diesem Stadtteil." One plain-German sentence per metric; 30 % explanation only on the
building popup (FR-012); "ausreichende Beschattung" matches the existing panel copy
(Assumptions); no em/en dashes, hyphens only in compounds (feature 012 FR-011 convention).

**Rationale**: Plain-German, one sentence, matches existing app wording for the threshold.

## R-9 Mobile fit (FR-016/SC-006)

**Decision**: Both popup content boxes get `max-height` (viewport-proportional, e.g.
`min(70vh, 420px)`) + `overflow-y: auto`, and a width clamp (`max-width: min(240px,
calc(100vw - 24px))`) so the taller content scrolls inside the popup on 360 px viewports
and no line is clipped. MapLibre's existing anchor/edge-flip keeps the popup in view.

**Rationale**: Content is substantially taller than today; scroll-within-popup satisfies
"visible or scrollable" without layout changes to the map.

## R-10 SC-003 automated cross-check

**Decision**: New `tests/acceptance/test_rank.py`:
1. Python reference: ranks/quartiles from `dist/stadtteile.geojson` per R-2; asserts
   ranks 1..38 unique, band bounds 1-10/11-19/20-28/29-38, tie-break order
   (Friedrichsfeld before Neckarau at 21.5; Neckarstadt-Nordost before Seckenheim at 19.5).
2. JS cross-check: load `dist/main.js` in a node VM (stubs: `window.maplibregl`/
   `window.pmtiles` no-op classes, `document.getElementById` → null, `matchMedia`,
   `console`), call the top-level `computeDistrictRankings(districtFeatures)` from the VM
   global, and compare all 38 ranks + quartiles against the Python reference. Skips when
   node or `dist/main.js` is missing (existing dist-fixture pattern).

**Rationale**: SC-003 demands 100 % automated match of the *shown* values; the VM harness
exercises the real shipped function. Pure top-level helpers (no map/DOM access) make this
possible without a browser. Node v22 is present (verified).

**Alternatives considered**: browser automation for the cross-check — heavy, flaky in CI;
rejected. Testing a re-implemented JS copy — tests a different function than ships;
rejected. Regex-extracting the function from main.js — brittle; rejected.

## R-11 Rounding rule

**Decision**: Deltas: magnitude rounded to 1 decimal, half-up on the magnitude
(`Math.abs(delta).toFixed(1)`) before sign prefixing. Building values and means are
displayed as published (no reform, R-3). Rank/quartile involve integers only (no rounding).

**Rationale**: Half-up on magnitude is the closest to the existing `formatPercent` 1-decimal
convention and avoids negative-zero artifacts.

## R-12 Colors (FR-013)

**Decision**: New CSS variables on the existing dark theme, following the published
palette semantics (low tree share = warm, high = cool): "good/erreicht/oberstes Viertel" →
cool cyan family (`#1db6ff`/`#39c2ff`), "unteres Mittelfeld" → `#e6854a`, "bad/verfehlt/
unterstes Viertel" → `#ffd524`. Every colored badge/assessment line carries its German text
label (FR-013). Neutral "auf …-Niveau" gets no color.

**Rationale**: Reuses the app's existing color language (palette stops 0/12/30 use
`#ffd524`/`#e6854a`/`#0674aa`); color is reinforcement only, never the sole encoding.

## Open questions

None. All spec ambiguities resolved above (delta comma artifacts, 0.1 pp band wording,
full-set access).
