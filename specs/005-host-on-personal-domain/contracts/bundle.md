# Deployment Bundle Contract

**Branch**: `005-host-on-personal-domain` | **Date**: 2026-08-04
**Source**: `spec.md` FR-004/FR-005, SC-007, `src/pipeline/publish.py`,
`validation/perf-budget.json`, research R-002/R-003/R-006.
**Entity**: E-002 (DeploymentBundle).

This contract fixes what the deploy transfers, how it is split
between Cloudflare assets and R2, and how its identity is proven —
so the live site is byte-identical to the local `make publish`
output (FR-004, SC-007).

## 1. Bundle contents and the 25 MiB split

| File | Size | Destination |
|---|---|---|
| `index.html` | 1.5 KB | Worker static assets (dist/) |
| `style.css` | 4.7 KB | Worker static assets |
| `main.js` | 7.4 KB | Worker static assets |
| `style.json` | 3.2 KB | Worker static assets |
| `attribution.html` | 1.0 KB | Worker static assets |
| `vendor/maplibre-gl.js` | 918 KB | Worker static assets |
| `vendor/maplibre-gl.css` | 68 KB | Worker static assets |
| `vendor/pmtiles.js` | 19 KB | Worker static assets |
| `boundary.geojson` | 75 KB | Worker static assets |
| `manifest.json` | 2 KB | Worker static assets |
| `buildings.geojson` | 54 MB | R2 object `buildings.geojson` |
| `buildings.pmtiles` | 33 MB | R2 object `buildings.pmtiles` |
| `trees.pmtiles` | 77 MB | R2 object `trees.pmtiles` |

Total on disk ≈ 171 MB (perf record: 171,062,607 bytes). The split
boundary is the Cloudflare asset limit of 25 MiB per file
(research R-002): everything smaller is served as a Worker static
asset (free, unlimited requests); the three larger files are R2
objects streamed by the Worker with native Range/206 support
(R-003). URLs are untouched — all files keep their relative names
under `/map/`, so the bundle is never rewritten (SC-007).

## 2. Identity

- Identity manifest: sorted file list, per-file `sha256`, file
  count, total bytes — computed by `deploy-cf.sh` from `dist/`.
- Verified against the R2 objects BEFORE activation
  (`wrangler r2 object get` + sha256, or checksum read-back) and
  against the live URLs AFTER the deploy (research R-006):
  checksums catch truncated large files (the realistic failure
  mode for a 77 MB `.pmtiles` over a flaky connection) that
  file-count and size checks miss.

**Invariants**:

- The live release's files match the local manifest byte-for-byte
  (SC-007); a mismatch aborts the deploy before activation.
- No file is modified after verification (verify before activation,
  prune after success).
- Data URLs are never patched — the bundle is transferred exactly
  as `make publish` emitted it (R-003).

## 3. Data layers (FR-005)

- `buildings.pmtiles` and `trees.pmtiles` must load at all zoom
  levels on the live site; they are served by the Worker from R2
  with HTTP Range support (206 verified — `hosting-config.md` §2,
  research R-003). The FR-013 gate checks one Range request; the
  quickstart Scenario 2 exercises pan/zoom/popup/toggle at deep
  zoom against the live URL.

## 4. Non-goals

- No bundle file names change; no hashed filenames are introduced
  (the cache contract compensates via revalidation —
  `hosting-config.md` §2).
- No build step on Cloudflare; the bundle is pre-built by
  `make publish` and transferred byte-identically.
