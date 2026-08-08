# Vendored Library Provenance (FR-008, feature 015)

This record states which third-party runtime code ships with the map,
where it came from, and under which license, so a reviewer can verify
the supply chain without trusting a claim. Contract:
`specs/015-security-audit-housekeeping/contracts/vendored-provenance.md`.

## maplibre-gl 5.7.1

- License: BSD-3-Clause
- Source: https://github.com/maplibre/maplibre-gl-js
- Vendored files:
  - `src/site/vendor/maplibre-gl.js` — sha256 `aa49ba072cb2d4621c365e501867cbc0ffead0d4a42dd79cb8f182525082451a`
  - `src/site/vendor/maplibre-gl.css` — sha256 `43c1d886b5fdf0aac4e7135bd6f84b823d9f48283a648012665f9be52c01389f`

## pmtiles 4.4.0

- License: BSD-3-Clause
- Source: https://github.com/protomaps/PMTiles
- Vendored file:
  - `src/site/vendor/pmtiles.js` — sha256 `4aa8f046955d77116fc1c9bb71bc49d174654342af8f1284aa34c625c71fd676`

The hashes are computed from the tracked files; they are evidence, not
a pin. Updating a vendored library updates this record in the same
commit (update rule in the contract).

## Declared runtime dependencies

The map at runtime also fetches from two external origins; FR-008
forbids undeclared runtime dependencies, so both are declared here:

| Origin | Use | Status |
|--------|-----|--------|
| `sgx.geodatenzentrum.de` | LGL basemap raster tiles (`wmts_basemapde_web_raster_grau`, dl-de/by-2-0, attributed in `src/site/style.json`) | Declared, documented, required by the CSP |
| `demotiles.maplibre.org` | Glyph/font PBFs via the `glyphs` URL in `src/site/style.json` | Declared; accepted risk (medium, owner sign-off 2026-08-08): MapLibre's public demo CDN — GET-only requests, no data leaves the page, CSP restricts to fonts. Vendoring the glyphs is a possible follow-up but would change the bundle and require a render-parity check; out of scope for this audit |

No other runtime dependency is introduced by this repository.
