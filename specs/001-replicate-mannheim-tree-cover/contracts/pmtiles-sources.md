# Contract: PMTiles Sources

The published map reads two PMTiles files via the
`pmtiles://` MapLibre protocol registered in `main.js`.
Each file's tippecanoe recipe is the contract.

## `buildings.pmtiles`

```text
tippecanoe   --name buildings   --layer buildings   --minimum-zoom 10 --maximum-zoom 18   --base-zoom 14   --drop-densest-as-needed   --extend-zooms-if-still-dropping   --read-parallel   --output=buildings.pmtiles   buildings.geojson
```

The input `buildings.geojson` is the post-clip, post-value-join
file from `src/pipeline/values.py`. Every feature carries:

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable LGL id. |
| `value` | float \| `null` | Mean 60 m % (FR-005). |
| `value_str` | string | Two-decimal popup payload (FR-008). |
| `has_value` | bool | Distinguishes unavailable from 0 (FR-009). |
| `in_boundary` | true | Clip guard. |

## `trees.pmtiles`

```text
tippecanoe   --name trees   --layer trees   --minimum-zoom 10 --maximum-zoom 18   --base-zoom 14   --drop-densest-as-needed   --extend-zooms-if-still-dropping   --read-parallel   --output=trees.pmtiles   canopy_polygons.geojson
```

The input `canopy_polygons.geojson` is the polygonized, clipped
canopy mask.

## Both files

- Coordinate reference system: EPSG:4326 in the PMTiles header
  (MapLibre auto-detects and re-projects to web mercator).
- Zoom 10–18. The lower bound is required, not arbitrary: MapLibre GL
  does not request tiles below a vector source's `minzoom`, and the
  initial view fits the full boundary at ~z10.9 (FR-002). With a
  `minimum-zoom` of 12 the initial view would render no buildings and
  no trees. `--drop-densest-as-needed` keeps the z10–11 overview
  tiles within budget.
- The maintainer verifies file size before `publish`; files >
  50 MiB stay in the release bundle, not in git (OR-005).
- `tippecanoe` is the only generator. A replacement generator
  must produce byte-identical output for the same input, or
  the maintainer re-runs the acceptance suite to confirm.

## Failure handling

`main.js` wraps the PMTiles load in a `try/catch`. A failed
`trees` load prints a console warning and leaves the
`trees-fill` layer's `visibility` at `'none'`; the buildings
layer continues to render (FR-020). A failed `buildings` load
is unrecoverable and the page surfaces the failure in the
`#attribution` slot.
