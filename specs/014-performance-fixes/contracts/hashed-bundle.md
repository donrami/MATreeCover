# Hashed Bundle Contract — Performance Fixes (spec 014)

Applies to FR-002, FR-003, FR-007, FR-008, FR-009, FR-010, US3.

## Hashed files

Hash = sha256 of file bytes, first 12 hex chars. Name = `<stem>-<hash>.<ext>`.

| Source file | Hashed name example |
|---|---|
| src/site/main.js | main-3f2a9c1b8d04.js |
| src/site/style.css | style-7c1e5a2b9f03.css |
| src/site/style.json | style-9d4b6c2e1a05.json |
| src/site/vendor/maplibre-gl.js | vendor/maplibre-gl-5a8f2d4c7b01.js |
| src/site/vendor/maplibre-gl.css | vendor/maplibre-gl-2e6b9a3d8c02.css |
| src/site/vendor/pmtiles.js | vendor/pmtiles-8c3a5f1b7d09.js |
| stadtteile.geojson (publish-derived) | stadtteile-4b1d7c2e9f06.geojson |
| boundary.geojson (publish-derived) | boundary-6e2a8c4d1b07.geojson |

Un-hashed: index.html, favicon.svg, attribution.html, impressum.html.

## Reference rewrites (publish time)

| File | Rewrite |
|---|---|
| index.html | script srcs to hashed names. Inline style.css and maplibre-gl.css into one `<style>` block. Add preload of vendor/maplibre-gl-<hash>.js, preconnect to https://sgx.geodatenzentrum.de, favicon link. |
| main.js | `STYLE_URL` constant to the hashed style.json. fetch URLs for stadtteile.geojson and boundary.geojson to hashed names. |
| style.json | `data` URLs for the boundary and stadtteile sources to hashed names. |

The rewrite is a deterministic string replacement in publish.py. Each replaced string occurs exactly once in the source files. The implementation asserts this. The publish fails if a pattern is missing or occurs twice.

## index.html head after publish

```html
<link rel="preconnect" href="https://sgx.geodatenzentrum.de">
<link rel="preload" href="vendor/maplibre-gl-<hash>.js" as="script">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<style>...inline style.css + maplibre-gl.css...</style>
```

CSP note: the inline style is allowed by the existing `style-src 'unsafe-inline'`. Preconnect and preload targets are allowed by the existing connect-src and script-src 'self'.

## Determinism and idempotence

- Identical inputs produce identical hashed names.
- Running publish twice yields the same bundle.
- The dist/manifest.json record gains a `hashed_assets` map (source name to hashed name) for verification and the deploy log.

## Verification

- Every reference in index.html, main.js, and style.json resolves to a file in dist/.
- No un-hashed copy of a hashed file is referenced by the bundle.
- The smoke test page still loads the map (scripts referenced by hashed names work).
