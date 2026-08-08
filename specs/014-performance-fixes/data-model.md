# Data Model — Performance Fixes (spec 014)

## Entities

### StaticAssetBundle

The published frontend bundle. Files carry a content hash in the filename, except the HTML document.

| Field | Type | Notes |
|---|---|---|
| source_path | path | Path in src/site/ |
| sha256_prefix | str | First 12 hex chars of the file sha256 |
| hashed_name | str | `<stem>-<prefix>.<ext>` |
| rewrite_targets | list[str] | Files that reference this asset |

Relationships:

- index.html references main.js, style.json (via main.js), vendor files, favicon.svg.
- main.js references style.json, stadtteile.geojson, boundary.geojson.
- style.json references boundary.geojson and stadtteile.geojson as source data URLs.
- The HTML is the only always-revalidated entry point.

Invariants:

- Two publishes of identical sources produce identical hashed names.
- Every reference in the bundle resolves to an existing file in dist/.
- No reference points to a file outside the current publish.

### CachePolicy

Maps a path pattern to HTTP cache directives.

| Field | Type | Notes |
|---|---|---|
| pattern | regex | Matched against the worker request pathname |
| directives | str | Cache-Control value |

Policies:

1. Hashed assets: `public, max-age=31536000, immutable`. Pattern: filename contains `-[0-9a-f]{12}\.(js|css|json|geojson|svg)`.
2. HTML and un-hashed files: `public, max-age=0, must-revalidate` (the existing default, unchanged).
3. PMTiles archives: `public, max-age=86400, stale-while-revalidate=604800, no-transform` (R2 object metadata).

Invariants:

- index.html never matches the immutable pattern.
- The pmtiles pattern keeps `no-transform`.

### BuildingsArchive

The published buildings.pmtiles vector archive.

| Field | Type | Notes |
|---|---|---|
| source | geojson | data/archive/workspace/buildings.geojson (values-joined, unchanged) |
| minzoom | int | 10 (unchanged) |
| maxzoom | int | 18 (unchanged) |
| base_zoom | int | 14 (unchanged) |
| simplification | scale | New: `-S 10 --simplify-only-low-zooms`, tunable within parity gates |

Invariants:

- Feature count per tile is identical to the pre-change archive at every zoom.
- Feature properties (`value`, `has_value`) are identical to the pre-change archive.
- Only vertex density below z18 may change.
- No feature is dropped, added, or degenerated to zero area.

### R2ObjectMetadata

HTTP metadata on the R2 data objects.

| Object | cache-control |
|---|---|
| buildings.pmtiles | `public, max-age=86400, stale-while-revalidate=604800, no-transform` |
| trees.pmtiles | `public, max-age=86400, stale-while-revalidate=604800, no-transform` |
| buildings.geojson | `no-cache` (unchanged, out of scope) |

Invariant: the upload loop in deploy-cf.sh is the single place that sets this metadata.

### Favicon

Small self-hosted SVG icon (favicon.svg) in the bundle.

| Field | Type | Notes |
|---|---|---|
| file | svg | src/site/favicon.svg, copied by publish |
| reference | link tag | `<link rel="icon" type="image/svg+xml" href="favicon.svg">` |

Invariant: the file exists in dist/ before the reference is written.

## Validation rules (from spec FRs)

- FR-001: both pmtiles objects carry the caching directives, and Range 206 passthrough stays correct.
- FR-002: every hashed file is served with the immutable directive.
- FR-003: index.html keeps the revalidate directive.
- FR-005: buildings.pmtiles carries the simplification flags and passes the parity gates.
- FR-006: building values in the rebuilt archive match the current archive exactly.
- FR-010: favicon.svg exists in the bundle and returns 200.

## State transitions

CachePolicy has no runtime state. The worker applies it per request from the pathname.

BuildingsArchive has one transition: current archive to simplified archive. The transition is gated on feature-count parity, property parity, screenshot parity, and image sanity. A failed gate rolls back to the current archive. The workspace keeps both, and the Makefile rebuild is the only mutation.
