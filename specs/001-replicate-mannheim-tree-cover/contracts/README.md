# Contracts

The plan exposes a small surface. Each contract is a single file in
this directory.

| File | Surface | Audience |
|---|---|---|
| `cli.md` | The `tree-cover` Python CLI. | Maintainer. |
| `static-bundle.md` | The `dist/` directory served by any static host. | Frontend browser; static host operator. |
| `map-style.md` | The MapLibre style object. | Frontend browser. |
| `manifest.md` | The `artifacts.manifest.json` schema. | Pipeline acceptance tests. |
| `pmtiles-sources.md` | The PMTiles data contract. | Frontend browser. |

All contracts are derived from the spec; no behavior is added that
the spec does not require. The contracts are versioned together
with the `release_id` recorded in `artifacts.manifest.json`.
