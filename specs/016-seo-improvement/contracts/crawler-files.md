# Contract: Crawler files (feature 016)

Requirement: FR-008/009/010 (US3, SC-006). Subject: `/map/robots.txt`, `/map/sitemap.xml`, and the documented root-domain coordination. Implementation: `src/site/robots.txt`, `src/site/sitemap.xml` (copied by `publish.py` `STATIC_FILES`). Enforcement: `tests/acceptance/test_seo_metadata.py`; live checks in quickstart Q3.

## robots.txt (`/map/robots.txt`)

- Content type `text/plain`, HTTP 200.
- Exactly three disallowed paths, map-path relative, for ALL user agents:

```text
User-agent: *
Disallow: /buildings.pmtiles
Disallow: /trees.pmtiles
Disallow: /buildings.geojson
```

- No HTML page is disallowed. The three indexable pages (`/map/`, `/map/impressum`, `/map/attribution`) and all other HTML stay allowed (FR-008).
- Optional informational line: `Sitemap: https://abu-hamad.de/map/sitemap.xml` (research R-004). It is informational only. Crawlers read the authoritative `Sitemap:` directive from the domain-root file, which is owner-side (see below).
- The zone-level AI-bot split (Cloudflare Managed Content, research D5) is documented in the assessment report. It is NOT duplicated in this file (FR-008).
- Cache note: Cloudflare caches `robots.txt` by default (120-min edge TTL for 200 responses without cache-control, research D5). A future fast change to the map-path file must account for that TTL.

## sitemap.xml (`/map/sitemap.xml`)

- Content type XML (`application/xml`), HTTP 200.
- Exactly three `<url>` entries, absolute, canonical (E1):

```text
https://abu-hamad.de/map/
https://abu-hamad.de/map/impressum
https://abu-hamad.de/map/attribution
```

- No `lastmod` (hand-written dates go stale between publishes; never claim a false date, spec edge case).
- No data files, no hashed assets, no `og-image.png` (SC-006).
- Cloudflare does not cache `.xml` sitemaps by default (research D5); no cache-related rule needed for it.

## Root-domain coordination (owner-side, FR-010)

The domain root belongs to the blog origin (E-004). The authoritative `/robots.txt` is the blog's file, not deployed from this repo. The assessment report documents the exact additions for the owner:

```text
Sitemap: https://abu-hamad.de/map/sitemap.xml
```

Optionally the three data-file disallows (same lines as above). Any root edit must account for the Cloudflare 120-min `robots.txt` edge cache (purge rule, research D5). AI-bot rules already exist at the root (research D1/D5) and stay.

## Rules

1. Both files are served from the map path with the security headers applied by the Worker (feature 015 `applySecurityHeaders` on all responses, unchanged).
2. Neither file is content-hashed (feature 014 contract applies only to `main.js`/`style.css`/`style.json`/`vendor/*`).
3. Both files are static text committed in `src/site/`. No generation step, no dynamic response (FR-001).
4. The map-path `robots.txt` does not repeat or contradict the zone-level AI-bot policy.

## Machine checks (acceptance test)

- `dist/robots.txt` parses as a robots file: three `Disallow:` lines match the exact data-file names, no `Disallow:` matches any HTML path, `User-agent: *` present.
- `dist/sitemap.xml` parses: exactly 3 `<loc>` values, each equal to one of the canonical URLs; no `<lastmod>`; no `.pmtiles`, `.geojson`, `og-image`, or hashed asset names.

## Live verification (quickstart Q3)

- Fetch `https://abu-hamad.de/map/robots.txt`: 200, `text/plain`, three data-file disallows.
- Fetch `https://abu-hamad.de/map/sitemap.xml`: 200, XML content type, exactly three canonical URLs.

## Regression notes

- Adding either file to `STATIC_FILES` is the only `publish.py` change needed; the Worker serves them from the assets binding like `index.html` (no Worker code change).
- The sitemap URL list is the single source for "exactly three pages". Adding a fourth page later is a contract change here plus the canonical tags.
