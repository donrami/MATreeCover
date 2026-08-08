# Contract: Static Bundle

The published `dist/` directory. Any static web host can serve it;
the maintainer may also run `python -m http.server -d dist` for a
local preview.

## Layout

```text
dist/
├── index.html
├── style.css
├── main.js
├── vendor/
│   ├── maplibre-gl.js
│   └── pmtiles.js
├── style.json
├── buildings.pmtiles
├── trees.pmtiles
├── boundary.geojson
├── manifest.json            # subset of artifacts.manifest.json, public-safe
└── attribution.html         # LGL + basemap.de + CityTreeCover
```

## `index.html`

- `<title>Baumfläche</title>` (FR-013).
- One `<div id="map">` fills the viewport; one
  `<aside id="legend">` (FR-012); one `<button id="baeume">`
  labelled `Bäume` (FR-013); one `<div id="attribution">`.
- Loads `style.css`, then ESM imports `main.js`.
- No analytics, no telemetry, no service worker, no
  application server.

## `style.css`

- Dark theme: page background `#0e0e0e`, map background `#000`,
  text `#fff`, subtle gray `#888` for outlines.
- `@media (max-width: 480px)`: legend collapses to a bottom
  strip, controls stack vertically. Preserves the reference
  arrangement on narrow screens (FR-018).

## `main.js`

- ESM module. Imports `maplibre-gl` and `pmtiles` from `vendor/`.
- Registers the `pmtiles` protocol with MapLibre so the
  client can range-read PMTiles without a tile server.
- Adds the `NavigationControl` with `showCompass: true` (FR-017).
- Loads the boundary mask layer (FR-003) and the buildings
  PMTiles (FR-004/FR-005/FR-008/FR-009/FR-010/FR-011).
- Loads the trees PMTiles (FR-015), `visibility: 'none'` on
  start; toggles `visibility` only on `Bäume` click (FR-016).
- Building `mousemove` sets `canvas.style.cursor = 'pointer'`
  (FR-014). `click` opens a MapLibre `Popup` with the
  building's `value_str` (FR-008/FR-014).
- Failed tree-PMTiles load is wrapped in a `try/catch` so the
  buildings still render (FR-020).

## `style.json`

- MapLibre `style` object. Sources: `pmtiles://buildings.pmtiles`,
  `pmtiles://trees.pmtiles`, `geojson://boundary.geojson` (the
  mask). Layers: `outside-mask`, `buildings-fill`,
  `buildings-line`, `trees-fill`.
- The `outside-mask` is a `fill` layer over the whole world with
  a hole punched by the official Mannheim boundary, rendered
  with `fill-color: #000` and `fill-opacity: 1` (FR-003).
- `buildings-fill` uses the reference palette interpolation
  (FR-010/FR-011) keyed on `value`. Features with
  `has_value == false` get `fill-color: #444` and
  `fill-opacity: 0.4` (FR-009).
- `buildings-line` is `line-color: #555`, `line-width: 0.5`
  (FR-010).
- `trees-fill` is `fill-color: #39C43D`, `fill-opacity: 0.75`
  (FR-015).

## `attribution.html`

- Required providers, hyperlinked:
  - LGL (Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0)
  - basemap.de
  - CityTreeCover (MIT)
- Links to the project's own source code on GitHub
  (https://github.com/donrami/MATreeCover).
- Reachable from the map's `AttributionControl` (FR-019).

## Size budget

- The whole bundle must remain under 50 MiB so the host can
  serve it from a single static directory without LFS. PMTiles
  are the dominant cost; the maintainer verifies their size
  before `publish` and records each in `manifest.json`.

## Browser support

- Latest two versions of Chrome, Firefox, Safari, and Edge.
- ES modules required.
- WebGL 2 required.
- Mobile width down to 360 px (FR-018/FR-004 acceptance
  scenario 4).
