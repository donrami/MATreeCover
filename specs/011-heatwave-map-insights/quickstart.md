# Quickstart: Heatwave Map Insights

Runnable validation guide for feature 011. Contracts and data model
are linked, not duplicated. Prereqs: Linux x86_64, Python 3.11,
tippecanoe ≥ 2.x, the workspace at `data/archive/workspace`, and a
Range-capable server (nginx; `python -m http.server` does not serve
PMTiles ranges).

Scope note: the Hitzebelastung view was removed on 2026-08-06
(clarification Option B). `values.py` returns to its pre-feature state
(`buildings.geojson` carries no `heat_class`); the remaining feature is
the district layer with statistics, the city overview panel, and the
district context in the building popup.

## S1 - Reproduce the derived data (pipeline)

Proves the data derivations (FR-006..FR-008) end to end.

```text
make values              # buildings.geojson unchanged (no heat_class)
make pmtiles-buildings   # buildings.pmtiles at pre-feature size
make accept              # manifest gate incl. the stadtteile artifact
make publish             # dist/: stadtteile.geojson, style.json metadata
```

Expected:

- `dist/stadtteile.geojson`: 38 features, EPSG:4326, each with
  `n_buildings`, `mean_value`, `share_lt30`.
- `dist/style.json` `metadata.city_stats` = `{"mean_value_pct": 22.2,
  "share_gte30_pct": 24.1, "tree_count": 153524}`.
- `dist/buildings.geojson` carries no `heat_class` attribute
  (regression check for the revert).
- `dist/manifest.json` lists the new `stadtteile.geojson` artifact.

## S2 - Acceptance suite (data and style contracts)

```text
.venv/bin/python -m pytest tests/acceptance -q
.venv/bin/python -m pytest tests/pipeline -q
```

Expected: all green, including `test_districts.py` (38 districts,
stats within 0.5 pp / 1 pp of independent recomputation, SC-002) and
`test_style.py` (updated `EXPECTED_LAYERS` incl. `stadtteile-fill`,
`#city-panel` present, no class-legend assertions). `make check-public`
stays clean (SC-008). No `tests/pipeline/test_heat_class.py` exists.

## S3 - Manual smoke: districts, city panel, popup context (FR-006..FR-013)

Serve `dist/` with nginx on 127.0.0.1:8088 and work
`tests/frontend/smoke_us6.md`, covering:

1. Default view renders exactly as published; legend unchanged
   (SC-004); no Hitzebelastung button exists; Bäume toggle and
   brightness slider still work (FR-012).
2. District click: popup with name, count, mean, share below 30 %;
   Innenstadt mean ≈ 9.6 % and Niederfeld ≈ 34.5 % (FR-006/FR-007).
3. City panel shows 22.2 %, 24.1 %, 153 524 (FR-008).
4. Building popup shows district name + district mean (FR-009).
5. Click arbitration: empty space closes both popups; district click
   replaces building popup and vice versa.
6. Keyboard: popups reachable; close buttons operable (FR-013).
7. Zero new requests: DevTools network shows only the 11 known
   requests (SC-007); no localStorage keys beyond
   `matreecover.story-dismissed`.
8. Overlap matrix (004 technique) at 320/480/768/1280/1920 px incl.
   `#city-panel`: no overlaps (FR-013).
9. Existing smoke checklists us1..us5 still pass (SC-008).

Completed checklists are logged to `validation/event.log.jsonl` as
smoke-us6 rows (project convention).

## S4 - Performance re-measurement (SC-006)

Reuse the CDP method from `validation/perf-budget.json` (throttled
25 Mbps / 50 ms, cold cache, Chromium headless 1280x800):

- `interaction_latency_ms` keeps `district_click` and `panel_render`;
  each must stay under the 2000 ms budget.
- `first_usable_ms` must stay under 10000 ms (stadtteile.geojson adds
  ~373 KB to first paint; budget has 7.5 s headroom vs the 2482 ms
  baseline).
- Record into `validation/perf-budget.json` alongside the existing
  keys (the `heat_toggle_*` keys are removed with the revert).

## S5 - Release (publish-bundle.md contract)

```text
bash scripts/deploy-cf.sh prepare-assets && bash scripts/deploy-cf.sh upload-data
npx wrangler deploy --config workers/map/wrangler.local.toml
bash scripts/deploy-cf.sh verify && bash scripts/deploy-cf.sh verify-dns
```

Expected: FR-013 verify gate passes with the buildings.pmtiles size
literal updated back to the regenerated size (read from
`dist/buildings.pmtiles` after the revert; expected 34023835);
live site shows the clickable districts, the city panel, and the
popup context; `dist-assets/attribution.html` in sync with the
GDI-MA credit and the statistics derivation note (FR-014).
