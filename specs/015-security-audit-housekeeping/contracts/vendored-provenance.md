# Contract: Vendored Library Provenance

Target: `src/site/vendor/PROVENANCE.md`. Requirement source: FR-008.

## Purpose

Record, in the repository, what third-party runtime code ships with the map, where it came from, and under what license — so a reviewer can verify the supply chain without trusting a claim.

## Record format

`src/site/vendor/PROVENANCE.md` contains one section per vendored library:

```text
## <name> <version>

- License: <SPDX identifier>
- Source: <upstream URL>
- Vendored file: <path in src/site/vendor/>
- sha256: <of the vendored file>
```

## Current record (verified during the audit)

| Library | Version | License | Source | Vendored files |
|---------|---------|---------|--------|----------------|
| MapLibre GL JS | 5.7.1 | BSD-3-Clause | https://github.com/maplibre/maplibre-gl-js | `maplibre-gl.js`, `maplibre-gl.css` |
| pmtiles | 4.4.0 | BSD-3-Clause | https://github.com/protomaps/PMTiles | `pmtiles.js` |

Hashes are computed from the tracked files at audit time and recorded; they are evidence, not a pin. Updating a vendored library updates the record in the same commit.

## Declared runtime dependencies

The map at runtime also fetches from two external origins. These are part of the provenance record because FR-008 forbids undeclared runtime dependencies:

| Origin | Use | Status |
|--------|-----|--------|
| `sgx.geodatenzentrum.de` | LGL basemap raster tiles (dl-de/by-2-0, attributed) | Declared, documented, required by CSP |
| `demotiles.maplibre.org` | Glyph/font PBFs via the `glyphs` URL in `src/site/style.json` | Declared; **accepted risk** (MEDIUM, owner sign-off): MapLibre's public demo CDN — GET-only requests, no data leaves the page, CSP restricts to fonts. Vendoring the glyphs is a possible follow-up but would change the bundle and require a render-parity check; out of scope for this audit. |

## Update rule

- Vendoring a new library, bumping a version, or changing a glyph origin is a contract change: update this contract and the DEVELOPMENT.md "Vendored frontend libraries" section in the same commit, and verify the map still renders (quickstart S6).
- The record must match the actual vendored files: the layout gate and the audit report's re-run section both reference it.

## Constraint

No undeclared runtime dependency may be introduced (FR-008). A dependency that appears in the bundle or in network behavior without a record entry is a finding.
