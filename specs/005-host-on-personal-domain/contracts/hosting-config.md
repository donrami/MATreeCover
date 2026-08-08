# Hosting Configuration Contract (Cloudflare)

**Branch**: `005-host-on-personal-domain` | **Date**: 2026-08-04
**Source**: `spec.md` FR-001/FR-002/FR-003/FR-005/FR-007, research
R-001/R-002/R-003/R-007/R-008. **Entity**: E-004/E-005.

This contract fixes the Cloudflare-side configuration of the map
path: the Worker and routes, the R2 objects, the DNS records, and
the TLS mode. It must hold at every release.

## 1. Worker and routes

- One Worker `matreecover-map`, plain JS, no build step.
- Routes (exactly these four, all to the same Worker — no sibling
  route-pattern conflicts, R-005):
  `abu-hamad.de/map`, `abu-hamad.de/map/*`,
  `www.abu-hamad.de/map`, `www.abu-hamad.de/map/*`.
- Worker behavior:
  - `/map` → 301 to `/map/`; `www.abu-hamad.de/map*` → 301 to
    `https://abu-hamad.de/map/` (single canonical redirect,
    FR-003, R-004/R-009).
  - `/map/*` small files → served from assets (dist/).
  - `/map/buildings.pmtiles`, `/map/trees.pmtiles`,
    `/map/buildings.geojson` → R2 binding range passthrough
    (`env.DATA.get(key, { range })`, forward 206 + Content-Range).
  - Any other path (including the root) → not matched by routes;
    falls through to the blog origin (never handled by the
    Worker).
- `wrangler.toml`: `assets.directory = ../../dist`, R2 binding
  `DATA → matreecover-data`, the four routes, pinned wrangler
  ≥ 3.98.0 (subdirectory asset serving).

**Invariants**:

- The canonical URL is `https://abu-hamad.de/map/`; every map
  request lands there via at most one 301 (FR-001, FR-003).
- The Worker never serves paths outside `/map/` — the root and all
  other paths belong to the blog origin (E-004).
- Only one Worker is attached to the `/map*` patterns (route
  specificity caveat, R-005).

## 2. R2 objects (bucket `matreecover-data`)

| Key | Content-Type | Cache-Control |
|---|---|---|
| `buildings.pmtiles` | `application/vnd.pmtiles` | `no-store, no-transform` |
| `trees.pmtiles` | `application/vnd.pmtiles` | `no-store, no-transform` |
| `buildings.geojson` | `application/geo+json` | `no-cache` |

- Uploaded with `wrangler r2 object put --content-type …
  --cache-control …`; single PUT per object (all < 5 GiB — no
  multipart).
- `no-transform` on the `.pmtiles` objects keeps `Content-Length`
  intact so edge behavior never breaks 206 slicing (R-007).
- `no-store` on the `.pmtiles` objects: pmtiles.js only sends
  `cache: "no-store"` on Windows Chrome (its `chromeWindowsNoCache`
  workaround); on other platforms the browser cache is used for
  range requests, and Chrome's range cache is keyed by URL only —
  it can serve a cached 206 for the WRONG byte range, silently
  corrupting tiles (verified live 2026-08-05). Server-side
  `no-store` disables browser caching of range responses for all
  clients. Range responses are small (viewport tiles only), so
  repeat visits re-fetch ranges — within SC-004 headroom.
- `no-cache` on `buildings.geojson` (fetched whole, not
  range-served): revalidate with ETag; never `no-store` there
  (would force re-downloading the 54 MB payload every visit and
  break SC-004 for repeat visitors), never `max-age` on
  non-hashed names (stale after deploy).

**Invariants**:

- Range requests return 206 with a correct `Content-Range` (FR-007,
  R-003) — verified live in the FR-013 gate.
- Data files change only via atomic per-object PUT; an interrupted
  PUT leaves the previous object live (FR-010).

## 3. DNS records (zone `abu-hamad.de`, free plan)

| Name | Type | Value | Proxy |
|---|---|---|---|
| `abu-hamad.de` | A | `<owner-host-ip>` (IPv4, blog, <hosting-provider>) | proxied (orange, after zone Active) |
| `abu-hamad.de` | AAAA | `<owner-host-ip>` (IPv6) | proxied (orange, after zone Active) |
| `www` | CNAME | `abu-hamad.de` | proxied (orange, after zone Active) |
| `ftp` | A | `<owner-host-ip>` (IPv4) | DNS-only |
| `autoconfig` | CNAME | `<mail-provider-cname>` | DNS-only (email client autoconfig) |
| `autodiscover` | CNAME | `<mail-provider-cname>` | DNS-only (email client autodiscover) |
| `abu-hamad.de` | MX | 10 `<mail-provider-mx-1>`; 20 `<mail-provider-mx-2>` | DNS-only |
| `abu-hamad.de` | TXT | `v=spf1 include:<mail-provider-spf> ~all` | DNS-only |
| `titan1_*` (DKIM) | TXT | `v=DKIM1; k=rsa; p=…` (Titan DKIM, per scan import) | DNS-only |
| `_dmarc` | TXT | none today — optional hardening only, not part of this feature | DNS-only if added |

All values verified against the live zone 2026-08-05 (`dig`; DKIM selector name per the Cloudflare scan).

- A records MUST be proxied for the `/map*` routes to work (routes
  run on proxied traffic, R-008). Migration order: grey → zone
  Active + Universal SSL Active → orange → SSL mode **Full
  (strict)** (<hosting-provider>'s Let's Encrypt satisfies the origin-CA
  requirement; Flexible causes redirect loops, R-008).
- Email records stay DNS-only (Cloudflare does not proxy MX/SMTP).

**Invariants**:

- The map path is served over HTTPS with Universal SSL (apex + www)
  — no mixed content (FR-002/FR-003, R-013).
- Email and blog records are identical to the pre-migration
  <hosting-provider> zone (FR-014, R-008).

## 4. Verification surface

The FR-013 gate checks, against the live site: `/map` → 301 →
`/map/`; `/map/` 200; `Cache-Control` present (no-cache/revalidate);
`buildings.pmtiles` Range → 206 + Content-Range; `www` map path →
canonical; certificate valid for both hostnames. Exact commands in
`quickstart.md` Scenario 6.

Feature 015 additions (contracts/security-headers.md is the reference):

- Security headers present on `/map/` and on a 206 Range response from
  an R2 key: `Content-Security-Policy` (byte-identical to the meta tag
  in `src/site/index.html`), `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Strict-Transport-Security` (no
  `includeSubDomains`/`preload`), `Referrer-Policy`,
  `Permissions-Policy`, `X-XSS-Protection: 0`.
- An unknown data-looking key under `/map/` answers 404 (only the three
  declared R2 keys are reachable; Range 206 passthrough unchanged).
- The R2 bucket public-access setting stays OFF (manual dashboard check,
  quickstart S6); access exists only through the Worker binding.
