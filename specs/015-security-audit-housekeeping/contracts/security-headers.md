# Contract: Security Headers and Content Security Policy

Target: `workers/map/index.js`, `src/site/index.html`, `scripts/deploy-cf.sh` (`verify`), `specs/005-host-on-personal-domain/contracts/hosting-config.md` (§3). Requirement sources: FR-004, FR-005, FR-013; US2.

## Purpose

Every response served by the Cloudflare Worker — static assets, R2 data passthroughs (200 and 206), and 404s — carries the documented security headers and content security policy. The policy is reviewed, committed, and verified at deploy time. The map keeps working exactly as before (FR-013).

## Security headers

Applied by `applySecurityHeaders(headers)` to every Worker response. The helper sets or overrides only the keys below and touches nothing else.

| Header | Value | Notes |
|--------|-------|-------|
| `Content-Security-Policy` | identical to the CSP meta tag (below) | header + meta both apply; keeping them identical prevents accidental tightening |
| `X-Content-Type-Options` | `nosniff` | all responses |
| `X-Frame-Options` | `DENY` | the page is never embedded |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | HTTPS-only site; cross-origin tile requests keep origin-only referrer |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()` | additive privacy defaults |
| `Strict-Transport-Security` | `max-age=31536000` | deliberately no `includeSubDomains` / `preload`: the apex host also serves the owner's blog and email subdomains; HSTS must stay scoped to the map host |
| `X-XSS-Protection` | `0` | legacy filter is deprecated; `0` disables its interference |

Reference implementation pattern: Cloudflare's documented Workers example ([set security headers](https://developers.cloudflare.com/workers/examples/security-headers)), adapted so headers apply to all responses, not only HTML.

## Content security policy

Source of truth: the `<meta http-equiv="Content-Security-Policy">` tag in `src/site/index.html`. The Worker header mirrors it byte-for-byte. Policy:

```text
default-src 'self'; img-src 'self' data: https://sgx.geodatenzentrum.de https://storage.ko-fi.com;
style-src 'self' 'unsafe-inline'; script-src 'self';
connect-src 'self' https://sgx.geodatenzentrum.de;
worker-src 'self' blob:; font-src 'self' https://demotiles.maplibre.org
```

Required allowlist (any tightening that removes these breaks the map — spec edge case):

| Directive | Origin | Why |
|-----------|--------|-----|
| `img-src` / `connect-src` | `sgx.geodatenzentrum.de` | LGL basemap raster tiles |
| `img-src` | `storage.ko-fi.com` | Ko-fi donation button image (feature 017) |
| `worker-src` | `blob:` | MapLibre/PMTiles worker instantiation |
| `style-src` | `'unsafe-inline'` | feature-014 inlined styles |
| `font-src` | `demotiles.maplibre.org` | glyphs URL in `src/site/style.json` (accepted risk, see vendored-provenance.md) |
| `img-src` / `worker-src` | `data:` / `blob:` | sprite/canvas/worker paths used by the frontend |

Changing the policy is a contract change: update this contract, the meta tag, and the Worker header together, and re-run the live-map verification (quickstart S6) before deploy.

## R2 data surface (FR-005)

- The Worker serves exactly three data keys: `buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson` (`DATA_KEYS`). Nothing else answers from R2.
- Range passthrough is preserved: 206, `Content-Range`, `ETag`, `Accept-Ranges`, `Content-Length` pass through untouched. Security headers are additive on those responses and must not alter them.
- The R2 bucket's public-access setting must stay OFF; access exists only through the Worker binding. This is checked manually in quickstart S6 (dashboard state is not in the repo).
- `deploy-cf.sh verify` asserts: the three keys answer 206 on Range requests; a request for an unknown data-looking key returns 404; security headers are present on the index response and on a 206 response.

## Regression constraints

- No change to map values, colors, labels, popups, or interactions (FR-013).
- No change to caching semantics: hashed assets stay `immutable`, HTML stays revalidating, PMTiles keep their R2 metadata cache headers (feature 014). The existing `verify` cache-header gate stays green.
- Header changes are verified against the live deploy before being declared complete (quickstart S6).
