# Data Model: Heatwave Map Insights

Feature 011 derived-data entities. All values are computed at publish
time from the accepted dataset; the client performs no computation of
statistics (FR-010). Reference numbers recomputed 2026-08-06 from
`data/archive/workspace/buildings.geojson` (accepted).

## Entities

### Building (unchanged)

Existing published entity (`buildings.geojson`, EPSG:4326, 93,022
features, schema in `contracts/pmtiles-sources.md` of feature 001).
Feature 011 adds **no** per-building attribute: the heat-exposure class
was removed from scope on 2026-08-06 (clarification Option B), so the
building schema is exactly the pre-feature schema (`id`, `value`,
`value_str`, `has_value`, `completeness`, `in_boundary`).

Validation:
- The published `buildings.geojson` carries no `heat_class` attribute
  (regression check: feature-011 pipeline revert).

### District (Stadtteil)

38 official GDI-MA districts, published as `dist/stadtteile.geojson`
(EPSG:4326, reprojected from `verification/stadtteile.geojson`
EPSG:25832 by publish.py). Properties:

| Field | Type | Rule |
|-------|------|------|
| `code` | string, 3 digits | unchanged ("011") |
| `name` | string | unchanged ("Innenstadt") |
| `id_name` | string | unchanged ("011 Innenstadt") |
| `n_buildings` | int | NEW. Buildings whose centroid lies in the district (reference: all 93,022 assigned) |
| `mean_value` | float, 1 decimal or null | NEW. Mean tree-cover value over buildings with a value; null if none |
| `share_lt30` | float, 1 decimal | NEW. Percent of valued buildings below the 30 % guideline |

Relationships: District 1—N Building (centroid containment);
District M—1 CityStats (aggregation).

Validation:
- Exactly 38 features, EPSG:4326, no duplicate `code`.
- Statistics MUST be consistent with the accepted building values:
  independent recomputation within 0.5 pp (mean) / 1 pp (share) for
  all districts (SC-002, `tests/acceptance/test_districts.py`).

### CityStats

Precomputed aggregates shipped in published style.json
`metadata.city_stats` (read by the overview panel; no extra request):

| Field | Type | Reference value |
|-------|------|-----------------|
| `mean_value_pct` | float, 1 decimal | 22.2 |
| `share_gte30_pct` | float, 1 decimal | 24.1 |
| `tree_count` | int | 153524 |

Validation:
- Values MUST match recomputation from the accepted dataset within
  0.5 pp / 1 pp / 1 % (SC-003).
- `share_gte30_pct` MUST be consistent with the sum of district
  `share_lt30` (weighted by `n_buildings`): 100 - weighted share.

## Derived-Data Flow (publish time)

```text
buildings.geojson (unchanged by feature 011)
                     │
publish.py ──────────┼────────────────────────────────────────────┐
  · read workspace buildings.geojson + trees_polygons.geojson     │
  · transform verification/stadtteile.geojson 25832 → 4326        │
  · centroid-in-polygon join: district stats per building          │
  · aggregate city stats + tree count                             │
  · write dist/stadtteile.geojson (stats on properties)           │
  · patch dist/style.json: metadata.city_stats, sources+=stadtteile│
  · write dist/manifest.json (new artifact entries)               │
  └───────────────────────────────────────────────────────────────┘
```

Client state (not persisted, session-only): one open popup at a time
(building or district). No new localStorage keys.

## State Transitions

- Popup lifecycle: building click opens the building popup (closes the
  district popup); district click with no building hit opens the
  district popup (closes the building popup); click on empty space
  closes both.
- No-value buildings: popup shows the en dash; no district mean line
  when the lookup misses or the district has no valued buildings
  ("keine Daten").
