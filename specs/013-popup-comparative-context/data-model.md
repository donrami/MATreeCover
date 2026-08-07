# Data Model: Popup Comparative Context

Feature 013. The published data model is **unchanged** (out of scope: no pipeline, data,
or publish-time changes). This document describes the entities the popups read, the
comparative attributes computed at display time, and the popup state machine. Ground truth
for the published properties is `dist/stadtteile.geojson` and `style.json` metadata
(verified: 38 districts, `city_stats.mean_value_pct = 22.2`).

## Entities (read-only, published bundle)

### Building Footprint

Source: `buildings-fill` layer features (`dist/buildings.pmtiles`). Unchanged by 013.

| Field | Type | Meaning | Source |
|-------|------|---------|--------|
| `has_value` | boolean | whether a tree-share value exists | publish pipeline |
| `value_str` | string | tree share in 60 m radius, 2 decimals (e.g. `"12.34"`) | publish pipeline |

Rules:
- Value is shown only when `has_value === true`; otherwise the unavailable marker
  (en dash `–`, existing `UNAVAILABLE` constant) is shown. Never a fabricated value
  (FR-006).
- Building display value = `value_str + '%'` (dot-decimal convention, no reform).
- Threshold: `Number(value_str) >= 30` ⇒ "erreicht", else "verfehlt" (FR-005; exactly
  30.0 counts as erreicht).

### District (Stadtteil)

Source: `stadtteile` GeoJSON source (38 features). Properties from the publish pipeline:

| Field | Type | Meaning |
|-------|------|---------|
| `code` | string | stable district key (rank lookup key) |
| `id_name` | string | machine name |
| `name` | string | display name (e.g. "Lindenhof") |
| `n_buildings` | integer | building count (thin-space thousands separator on display) |
| `mean_value` | number \| null | mean tree share of the district's valued buildings, 1 decimal; `null` if no valued buildings |
| `share_lt30` | number | share of valued buildings below 30 %, 1 decimal |

Display-time (computed in `main.js`, never persisted — R-2):

| Attribute | Derivation |
|-----------|------------|
| `rank` | position in the 38-district ordering: sort by `mean_value` desc, then `name` asc; sequential ranks 1..N; ties get distinct ranks |
| `quartile` | band from rank and N: 1..ceil(N/4) "oberstes Viertel", next floor(N/4) "oberes Mittelfeld", next floor(N/4) "unteres Mittelfeld", remainder "unterstes Viertel"; N = 38 ⇒ 1-10 / 11-19 / 20-28 / 29-38 |
| `deltaVsCity` | `mean_value − city_stats.mean_value_pct` |

### City Statistics

Source: `style.json` → `metadata.city_stats` (same block consumed by `renderCityPanel`).

| Field | Type | Meaning |
|-------|------|---------|
| `mean_value_pct` | number | city-wide mean tree share, 1 decimal — the city-average reference in both popups |
| `share_gte30_pct` | number | share of buildings at/above 30 % (panel only, not used by popups) |
| `tree_count` | integer | detected tree areas (panel only, not used by popups) |

The popups use **only** `mean_value_pct`. City lines are hidden when it is missing
(stale bundle, FR-014).

## Derived display model

### Building popup (rendered by `buildingPopupHtml(props, lngLat)`)

| Block | Content | Condition |
|-------|---------|-----------|
| Header | district `name` | always (district lookup via `districtAt(lngLat)`) |
| Headline | label "Baumanteil im 60-m-Umkreis" + `value_str %` or `–` | always |
| Badge | "erreicht" / "verfehlt" | only when `has_value === true` |
| Context | district average line: mean + signed delta + word (FR-003) | only when `has_value === true` |
| Context | city average line: `mean_value_pct` + signed delta + word (FR-004) | only when `has_value === true` **and** city stats present |
| Context | district average plain line (existing "Durchschnitt im Stadtteil") | when `has_value === false` (FR-006: district context still shown) |
| Footnote | "Was bedeutet das?" + metric + 30 % explanation | always |

Delta semantics (R-3): `delta = Number(value_str) − reference`; classification
`> +0.1` ⇒ über, `< −0.1` ⇒ unter, `|delta| ≤ 0.1` ⇒ "auf …-Niveau"; display
"±0.0 pp" when neutral, else sign (U+2212 minus) + magnitude rounded 1 decimal + " pp".

### District popup (rendered by `districtPopupHtml(props)`)

| Block | Content | Condition |
|-------|---------|-----------|
| Header | district `name` | always |
| Headline | "Baumanteil im Durchschnitt" + `mean_value %` or "keine Daten" | always |
| Badge | quartile band label | `mean_value` valid **and** rankings available |
| Context | rank "Platz X von 38" | same as badge |
| Context | city line: `mean_value_pct` + signed delta + word (FR-008) | `mean_value` valid **and** city stats present |
| Context | "Gebäude" `n_buildings` | always (existing, FR-007) |
| Context | "Anteil unter 30 %" `share_lt30` | always (existing, FR-007) |
| Footnote | "Was bedeutet das?" + metric explanation | always |

Degradation matrix (FR-011, FR-014):

| Case | Hidden |
|------|--------|
| `mean_value == null` | rank, quartile badge, city line; mean shows "keine Daten" |
| city stats missing | both city comparison lines (rank/quartile unaffected) |
| rankings unavailable (fetch failed) | rank, quartile badge |
| fewer than two valid district means | all rank/quartile content |

## State machine: Selection Popup

Unchanged from features 002/011 (FR-015). One popup instance per type, page lifetime;
`closeOnClick: false`; `className` per type for styling.

```
IDLE ── building click ──► BUILDING_POPUP (district popup removed)
IDLE ── district click ──► DISTRICT_POPUP (building popup removed)
BUILDING_POPUP ── building click ──► BUILDING_POPUP (content replaced, same popup)
BUILDING_POPUP ── district click ──► DISTRICT_POPUP
BUILDING_POPUP ── empty-space click / close button ──► IDLE
DISTRICT_POPUP ── building click ──► BUILDING_POPUP
DISTRICT_POPUP ── district click ──► DISTRICT_POPUP (content replaced)
DISTRICT_POPUP ── empty-space click / close button ──► IDLE
```

Content refresh on click re-renders the body via the render functions above; the state
machine itself is untouched by 013.

## Validation rules (from requirements)

- Never display a fabricated value: `has_value === false` ⇒ marker, no deltas (FR-006).
- Delta classification thresholds: ±0.1 pp band inclusive (FR-003/FR-004/FR-008).
- Rank determinism: sort mean desc, name asc; distinct sequential ranks (FR-009).
- Quartile bounds: 1-10 / 11-19 / 20-28 / 29-38 for N = 38 (FR-010).
- Threshold: `>= 30` counts as erreicht.
- All copy German, dot-decimal, "pp" for deltas (FR-017, R-3).
