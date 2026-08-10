# Vendored Library Provenance (FR-008, feature 015)

This record states which third-party runtime code ships with the map,
where it came from, and under which license, so a reviewer can verify
the supply chain without trusting a claim. Contract:
`specs/015-security-audit-housekeeping/contracts/vendored-provenance.md`.

## maplibre-gl 5.7.1

- License: BSD-3-Clause
- Source: https://github.com/maplibre/maplibre-gl-js
  - `src/site/vendor/maplibre-gl.js` — sha256 `22bcaea5f73befb89cbe0dc9e896ad2463966b7bdf68e1af88b7226bc10e7afe` (locally patched; see Patch below)
  - `src/site/vendor/maplibre-gl.css` — sha256 `43c1d886b5fdf0aac4e7135bd6f84b823d9f48283a648012665f9be52c01389f`

### Patch: suppress Firefox WebGL warning on ImageBitmap uploads

The upstream `5.7.1` build emits the Firefox console warning
`WebGL warning: texImage: Alpha-premult and y-flip are deprecated for non-DOM-Element uploads`
once per ImageBitmap upload (PMTiles decode path). The warning fires because
`Texture.update()` calls `pixelStoreUnpackFlipY.set(false)` and
`pixelStoreUnpackPremultiplyAlpha.set(...)` before `texImage2D`/`texSubImage2D`,
even when the source is an ImageBitmap, where those flags are no-ops and
no longer needed (the ImageBitmap upload path always uses the GL defaults:
`premult=false`, `flipY=false`).

Local edit, single site in `class hl` `update()`:

```js
// before
o.bindTexture(o.TEXTURE_2D,this.texture),a.pixelStoreUnpackFlipY.set(!1),a.pixelStoreUnpack.set(1),a.pixelStoreUnpackPremultiplyAlpha.set(this.format===o.RGBA&&(!e||!1!==e.premultiply)),s)
// after
o.bindTexture(o.TEXTURE_2D,this.texture),Y(t)||(a.pixelStoreUnpackFlipY.set(!1),a.pixelStoreUnpack.set(1),a.pixelStoreUnpackPremultiplyAlpha.set(this.format===o.RGBA&&(!e||!1!==e.premultiply))),s)
```

`Y(t)` is the existing `ImageBitmap` predicate already used in the
`texImage2D` branch of the same function. When `t` is an ImageBitmap,
the three `set()` calls are skipped, the GL defaults are used, and the
upload proceeds silently. When `t` is a DOM element, behavior is
byte-identical to the upstream build.

Upstream fix tracked in maplibre-gl-js#2030 / PR #7128. This patch is a
strict superset shrink: identical rendering, fewer console warnings.
Upstream upgrade to a build that includes PR #7128 supersedes this edit.

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
