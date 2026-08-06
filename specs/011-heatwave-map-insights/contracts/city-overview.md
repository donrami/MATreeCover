# Contract: City Overview Panel

Feature 011, FR-008, FR-010. A compact static card answering "how
heat-exposed is Mannheim as a whole".

## Data: `metadata.city_stats`

publish.py writes into the published `style.json` metadata (same patch
point as the existing `mannheim_bbox`):

```json
{
  "mannheim_bbox": [8.42, 49.40, 8.66, 49.58],
  "city_stats": {
    "mean_value_pct": 22.2,
    "share_gte30_pct": 24.1,
    "tree_count": 153524
  }
}
```

Derivation (publish time, from the accepted dataset):
- `mean_value_pct`: mean of `value` over buildings with a value,
  1 decimal (reference 22.2).
- `share_gte30_pct`: 100 × (valued buildings with `value >= 30` /
  valued buildings), 1 decimal (reference 24.1).
- `tree_count`: feature count of the accepted `trees_polygons.geojson`
  (reference 153524). Unit: detected tree areas (canopy polygons), NOT
  individual trees; the panel label states this ("Anzahl der erkannten
  Baumflächen").

Consistency invariant: `share_gte30_pct` MUST equal
`100 - sum(n_buildings_i * share_lt30_i)/sum(n_buildings_i)` over all
38 districts (within rounding, 0.1 pp) — the panel and the district
stats MUST tell the same story (FR-007).

## Panel

- New card `#city-panel` in `#left-stack`, below `#legend` (flex
  column, cards never overlap; verified by the 004 overlap-matrix
  technique extended to `#city-panel`).
- Content rendered by main.js from `map.getStyle().metadata.city_stats`
  at map load (no fetch, no hardcoded numbers in HTML — the panel is a
  view over publish-time data):

  ```
  <h2 class="panel-title">Mannheim im Überblick</h2>
  <p>Durchschnittlicher Baumanteil im 60-m-Umkreis: 22.2 %</p>
  <p>Gebäude mit ausreichender Beschattung (30 %): 24.1 %</p>
  <p>Anzahl der erkannten Baumflächen: 153 524</p>
  ```

- Formatting rules: percentages with one decimal and a dot (matches
  the existing `value_str` format); integers with a thin space as
  thousands separator ("153 524").
- If `metadata.city_stats` is missing (e.g. stale bundle), the panel
  hides itself rather than showing placeholders.
- The 30 % reference in the second line is the shade guideline the
  map's story modal cites ("30 % des 60-m-Umkreises"), the same
  guideline the district popup's "Anteil unter 30 %" line uses, so the
  two surfaces stay consistent.

## Responsive

- Desktop: third card in the left stack.
- ≤480 px: `#left-stack` becomes a bottom strip (column-reverse); the
  city panel renders as a compact card in that strip, no horizontal
  overflow (spec Edge Cases, FR-013).

## Copy

"Überblick", "Durchschnittlicher Baumanteil im 60-m-Umkreis",
"Gebäude mit ausreichender Beschattung (30 %)", "Erkannte
Baumflächen" — final German copy, no dashes (FR-011).
