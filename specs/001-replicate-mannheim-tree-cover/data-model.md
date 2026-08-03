# Data Model

**Branch**: `001-replicate-mannheim-tree-cover` | **Date**: 2026-08-03
**Source**: `spec.md` § Key Entities, plus the entities implied by
FR-001..FR-025 and the mannheim workspace inventory.

This document enumerates every entity that appears in the published
map or in the supporting pipeline, with its fields, types, and
invariants. All values are derived from the spec; no fields are
invented.

## E-001 — MannheimBoundary

The official municipal polygon that defines display, publication,
and accepted building membership.

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | string | LGL | Stable id, e.g. `mannheim-boundary`. |
| `geometry` | `MultiPolygon` (EPSG:25832) | `boundary.geojson` | One feature, possibly multi-polygon for exclaves. |
| `crs` | `"EPSG:25832"` | meta | LGL standard. |
| `bbox` | `[west, south, east, north]` | derived | Initial-view `fitBounds` target (FR-002). |
| `area_m2` | float | derived | Used to verify `area > 0` and to size the analysis grid. |
| `source` | `"LGL"`, license `"dl-de/by-2-0"` | spec evidence | Required for FR-021 source check. |

**Invariants**:
- The buffered boundary is `boundary ∪ boundary.buffer(60 m)` and
  exists only inside the pipeline; never published (FR-007).
- The initial map view fits this bbox with minimal padding
  (FR-002).

## E-002 — BufferedBoundary (pipeline-only)

| Field | Type | Notes |
|---|---|---|
| `geometry` | `MultiPolygon` (EPSG:25832) | `boundary.buffer(60 m)` to scope the imagery read. |
| `crs` | `"EPSG:25832"` | — |
| `purpose` | `"analysis-only"` | Marked so publish never copies it to `dist/`. |

**Invariants**:
- Never appears in any published artifact (FR-007).
- Imagery tile selection is `tiles ∩ buffered_boundary`; the
  pipeline does not load tiles outside this set (OR-002).

## E-003 — BuildingFootprint

An accepted official building geometry with a stable identifier
and an optional building value.

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | string | LGL ALKIS | Stable identifier; used as the de-duplication key. |
| `geometry` | `Polygon` (EPSG:25832) | `tables/buildings.geojson` | Clipped to the official boundary. |
| `value` | float \| `null` | derived | Mean 60 m tree-cover %; `null` means unavailable (FR-009). |
| `value_str` | string | derived | `value` formatted with two decimals, or `"–"` for `null` (FR-008). |
| `has_value` | bool | derived | `true` iff a valid value was computed (FR-009). |
| `in_boundary` | bool | derived | `true` for buildings that survived the clip; `false` would have been dropped already. |

**Invariants**:
- 93,024 features in the accepted inventory (matches
  `2026.01/meta.json.buildings.feature_count`).
- No synthetic, no duplicate, no outside-Mannheim building
  (FR-004). Duplicates are dropped by `id`.
- The published PMTiles contains only `in_boundary == true`
  features.
- `value` is in `[0, 100]` or `null` (FR-008).
- `value_str` is the popup payload, with two decimal places when
  present (FR-008).

## E-004 — DetectedTreeArea

A classified canopy area from the accepted imagery and canopy
result.

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | string | derived | Stable id `tree-<n>` from polygonize order. |
| `geometry` | `Polygon` (EPSG:4326 in PMTiles) | `rasterio.features.shapes` on accepted canopy mask | Clipped to the official boundary. |
| `canopy_pixel_count` | int | derived | Area in 0.2 m pixels; sanity-checked for SC-005. |
| `source` | `"accepted_canopy_mask"` | derived | Lineage pointer. |

**Invariants**:
- The published tree layer renders only after the user activates
  the `Bäume` button (FR-015).
- Render style: flat `#39C43D` at 75% opacity (FR-015).
- Layer toggle does not change the camera (FR-016).

## E-005 — BuildingValue

The mean 60 m-radius tree-cover percentage across one building
footprint.

| Field | Type | Source | Notes |
|---|---|---|---|
| `building_id` | string | E-003 `id` | Foreign key. |
| `value` | float \| `null` | `scipy.signal.fftconvolve` | Mean over the rasterized footprint inside a 60 m disc. |
| `completeness` | float | derived | Fraction of the 60 m disc that had valid imagery; 1.0 is full coverage, <1.0 means halo contributed less. |
| `method` | `"scipy.signal.fftconvolve"`, `"radius_m": 60.0`, `"radius_px": 300` | `meta.json` | Lineage. |
| `chunk_id` | string | derived | Which 1000 px tile produced this value. |

**Invariants**:
- `value == null` iff `completeness < completeness_threshold` or
  the imagery read failed (FR-009).
- The recompute check (SC-004) is a 100-building random sample;
  ≤ 1 percentage point disagreement is the pass criterion.

## E-006 — ReusableArtifact

A prior input or result with known source, extent, resolution,
completeness, lineage, and acceptance state.

| Field | Type | Notes |
|---|---|---|
| `path` | string | Workspace-relative path. |
| `size_bytes` | int | For OR-005 governance. |
| `sha256` | string | Content hash. |
| `source` | string | Origin (LGL, run, derived). |
| `license` | string | `"dl-de/by-2-0"` for LGL data; MIT for derived code. |
| `extent` | bbox or polygon | Coverage area. |
| `resolution` | string | E.g. `"0.2 m"`, `"n/a"`. |
| `completeness` | float | Coverage fraction inside buffered boundary. |
| `lineage` | string | Hash of the upstream artifact(s). |
| `acceptance` | `"pass" \| "fail" \| "pending"` | FR-021 verdict. |
| `checks` | object | Per-criterion status from FR-021. |
| `invalidates` | list[string] | Downstream artifacts to mark `pending` if this fails (FR-023). |

**Invariants**:
- An artifact is reused only when `acceptance == "pass"`.
- A failed derived artifact flips dependents to `pending` without
  re-evaluating independent accepted inputs (FR-023).
- Files > 50 MiB are recorded here, never committed (OR-005).

## E-007 — PublishedMap

The one Mannheim release that combines accepted buildings,
values, tree areas, legend, and controls.

| Field | Type | Notes |
|---|---|---|
| `release_id` | string | `"2026.01"` carried forward, or a new id with a fresh manifest. |
| `index_html` | string | `<title>Baumfläche</title>`; loads the bundle. |
| `style` | string | Reference MapLibre style URL. |
| `buildings` | string | Path to `buildings.pmtiles` (out of repo). |
| `trees` | string | Path to `trees.pmtiles` (out of repo). |
| `boundary` | string | Path to `boundary.geojson` (out of repo if > 50 MiB). |
| `legend` | DOM control | Labels: `0`, `15`, `30`, `50`, `100` (FR-012). |
| `controls` | DOM control | `Bäume` toggle (FR-013), zoom in/out, north reset (FR-017). |
| `attribution` | DOM control | LGL, basemap.de, CityTreeCover (FR-019). |

**Invariants**:
- No halo geometry, no outside-Mannheim building, no value > 100,
  no value < 0 (FR-007/FR-008).
- Page title is exactly `Baumfläche` (FR-013).
- The tree layer starts hidden (FR-015).
- The initial camera fits `E-001.bbox` with `bearing = 0`
  (FR-002).
- A failed tree-layer load does not block the buildings
  (FR-020).

## E-008 — AcceptanceRun

A recorded `pytest` run for a release.

| Field | Type | Notes |
|---|---|---|
| `run_id` | string | ULID, derived. |
| `timestamp` | ISO 8601 | UTC. |
| `pytest_version` | string | — |
| `cases` | list | Each per-artifact test result. |
| `rss_peak_bytes` | int | From `/usr/bin/time -v`; ≤ 12 GiB. |
| `gpu_used` | bool | Must be `false` (OR-003). |
| `result` | `"pass" \| "fail"` | — |

**Invariants**:
- An acceptance run is the gate before publication; a `fail`
  blocks any `publish` step.

## Relationships

```
MannheimBoundary ─┬─ BufferedBoundary (pipeline-only, halo)
                  └─ BuildingFootprint (clipped, in_boundary=true)
                                  │
                                  └── BuildingValue (one per footprint)

DetectedTreeArea  ── derived from accepted canopy mask
                ── clipped to MannheimBoundary
                ── published as trees.pmtiles

ReusableArtifact  ── recorded for every input/derived artifact
                ── drives acceptance state propagation

PublishedMap      ── consumes BuildingFootprint + DetectedTreeArea
                ── emits index.html + style + static assets
                ── gated by AcceptanceRun
```

## Validation rules summary

| Rule | Source | Where checked |
|---|---|---|
| Source attribution present | FR-021 | `src/pipeline/acceptance.py` |
| Extent intersects boundary | FR-021 | `src/pipeline/acceptance.py` |
| Resolution matches spec | FR-021 | `src/pipeline/acceptance.py` |
| Completeness inside buffered boundary ≥ 0.95 | FR-021, `coverage_ratio_min` | `src/pipeline/acceptance.py` |
| Lineage (input hash) recorded | FR-021 | `artifacts.manifest.json` |
| Building count exactly 93,024 | SC-003 | `tests/acceptance/test_buildings.py` |
| Value range 0–100% or `null` | FR-008 | `src/pipeline/values.py` |
| Two-decimal popup formatting | FR-008 | `src/site/main.js` |
| `value == null` ⇒ popup shows `–` | FR-009 | `src/site/main.js` |
| Camera unchanged on tree toggle | FR-016 | `tests/frontend/` (manual) |
| RSS ≤ 12 GiB on every local run | OR-001, SC-009 | `tests/pipeline/test_rss.py` |
