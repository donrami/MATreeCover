# Cache Headers Contract — Performance Fixes (spec 014)

Applies to FR-001, FR-002, FR-003, SC-003, SC-004.

## Directive table

| Resource | Cache-Control | Where set |
|---|---|---|
| Hashed assets (`*-[0-9a-f]{12}.(js|css|json|geojson|svg)`) | `public, max-age=31536000, immutable` | Worker (workers/map/index.js, ASSETS branch) |
| index.html, attribution.html, impressum.html, un-hashed files | `public, max-age=0, must-revalidate` | Workers static assets default (unchanged) |
| buildings.pmtiles, trees.pmtiles | `public, max-age=86400, stale-while-revalidate=604800, no-transform` | R2 object metadata (scripts/deploy-cf.sh upload-data) |
| buildings.geojson | `no-cache` | R2 object metadata (unchanged) |

## Worker rule

In the ASSETS branch, after `env.ASSETS.fetch(...)`:

1. Parse the filename from the request pathname.
2. If it matches `-[0-9a-f]{12}\.(js|css|json|geojson|svg)$`, replace the Cache-Control header on the response with the immutable value.
3. Return the response unchanged in all other cases.

The R2 branch is untouched. Content-Range, Accept-Ranges, and Content-Length behavior stays as-is.

## Upload metadata (scripts/deploy-cf.sh)

The upload loop entries for the two pmtiles objects change from `no-store, no-transform` to the values above. `no-transform` stays in every pmtiles directive. Cloudflare must never re-encode the archives, or the Range contract breaks.

## Verification

- Curl a range request twice from the same edge. Check `cf-cache-status`.
- If the second request is not HIT, edge caching of worker-generated 206 responses is not available on this zone. Browser caching still applies. Record the finding and adjust SC-004 per the spec's fallback.
- Curl a hashed asset. Check `cache-control: public, max-age=31536000, immutable` and the ETag.
- Curl index.html. Check `cache-control: public, max-age=0, must-revalidate`.
- Run `bash scripts/deploy-cf.sh verify`. All existing gates must pass, including the Range 206 check.

## Edge cases

- A browser may hold cached ranges up to the TTL while the archive is re-uploaded. Values are unchanged, so the map stays correct. Geometry converges on the next visit.
- A rollback deploy removes old hashed files. The HTML references only current hashes, so no mixed-version load occurs.
- stale-while-revalidate allows background refresh after 24 h. Browsers that support it never block on the archive.
