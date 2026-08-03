# Contract: MapLibre Style

The MapLibre style object that `main.js` loads. Defined as JSON;
the maintainer can edit it without touching code.

## Top-level

```json
{
  "version": 8,
  "name": "Mannheim Tree Cover",
  "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
  "sprite": "",
  "sources": { … },
  "layers":  [ … ]
}
```

No `glyphs` are required by the published layers, but MapLibre
expects the field. The demotiles URL is used for the published
build; the maintainer can switch to a self-hosted font if a
licence is needed.

## Sources

```json
{
  "sources": {
    "basemap":   { "type": "raster", "tiles": ["…basemap.de…"], "tileSize": 256, "attribution": "© basemap.de / LGL" },
    "buildings": { "type": "vector", "url": "pmtiles://buildings.pmtiles", "attribution": "Datenquelle: LGL, dl-de/by-2-0" },
    "trees":     { "type": "vector", "url": "pmtiles://trees.pmtiles", "attribution": "Datenquelle: LGL, dl-de/by-2-0" },
    "boundary":  { "type": "geojson", "data": "boundary.geojson" }
  }
}
```

The buildings and trees PMTiles are referenced by relative path;
`pmtiles://` is a MapLibre protocol registered in `main.js`.

## Layers (bottom → top)

1. **`basemap`** — base raster from basemap.de dark style.
2. **`outside-mask`** — a `fill` layer over the world
   (`fill-color: #000`, `fill-opacity: 1`) with a hole punched
   by the official Mannheim boundary, so any base map area
   outside Mannheim is obscured (FR-003).
3. **`buildings-fill`** — `fill` layer keyed on `value`:

   ```text
   fill-color: interpolate(
     ['linear'], ['get', 'value'],
     0,    '#ffd524',
     12,   '#e6854a',
     24,   '#a97e65',
     24.08,'#0674aa',
     32,   '#1db6ff',
     40,   '#39c2ff',
     48,   '#56ceff',
     80,   '#6ad4ff'
   )
   ```

   `fill-opacity: 0.75` (FR-010). Features with
   `has_value == false` use `case` to fall through to
   `#444` at `0.4` opacity (FR-009).
4. **`buildings-line`** — `line` layer; `line-color: #555`,
   `line-width: 0.5` (FR-010).
5. **`trees-fill`** — `fill` layer; `fill-color: #39C43D`,
   `fill-opacity: 0.75` (FR-015).
   `layout.visibility: 'none'` on load (FR-015).

## Camera

Initial camera is set in `main.js` to fit
`E-001.bbox` (MannheimBoundary) with `padding: 24`,
`bearing: 0`, `pitch: 0`, `duration: 0` (FR-002).

## Validation hooks

- `tests/acceptance/test_style.py` loads `style.json` with the
  MapLibre style parser and asserts the five layers, the
  palette stops, and the legend labels.
- The style object must round-trip through `JSON.parse` and
  `JSON.stringify` without loss.
