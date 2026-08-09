# SEO Assessment & Improvement (feature 016)

Date: 2026-08-09.
Scope: search-engine and link-sharing visibility of the live map site
`https://abu-hamad.de/map/` and its two info pages.
Map lock: the map itself is unchanged. Values, colors, labels, popups, and
interactions stay locked (FR-012).
Method: fetch raw HTML of every page. Record title, meta description,
canonical, Open Graph, JSON-LD, and visible text. Verify crawler files and
the governance gates. Verification is server-side only (FR-001/FR-011).
Source docs: `specs/016-seo-improvement/` (spec.md, plan.md, research.md,
data-model.md, contracts/).

## Current state (pre-change evidence, fetched 2026-08-09)

Live fetches via `curl` on 2026-08-09:

| Page | HTTP | Title | Meta description | Canonical | OG/Twitter | JSON-LD |
|------|------|-------|------------------|-----------|------------|---------|
| `https://abu-hamad.de/map/` | 200 | `Baumfläche` (10 chars) | missing | missing | none | none |
| `https://abu-hamad.de/map/impressum` | 200 | `Impressum – Mannheim Baumfläche` | missing | missing | none | none |
| `https://abu-hamad.de/map/attribution` | 200 | `Datenquellen – Mannheim Baumfläche` | missing | missing | none | none |

Crawler files and preview image:

| Resource | HTTP |
|----------|------|
| `https://abu-hamad.de/map/robots.txt` | 404 (not deployed) |
| `https://abu-hamad.de/map/sitemap.xml` | 404 (not deployed) |
| `https://abu-hamad.de/map/og-image.png` | 404 (not deployed) |

Redirect behavior (existing Worker, unchanged). `/map/index.html` returns
307 to `/map/`. `www.abu-hamad.de/map/` returns 301 to the apex. Verified
2026-08-09.

Visible text in the raw HTML of the map page defines what a non-JS crawler
reads. It contains the page heading "Baumfläche" and the legend. The legend
reads "Durchschnittlicher Baumanteil im 60-m-Umkreis", scale 0 to 100,
"Prozent". It also contains the legend note with the attribution link
and the legal link.
All informative prose lives inside the `hidden` first-visit story dialog.
That prose covers the project story, the SPIEGEL source, the CityTreeCover
reference, and the GitHub link. A non-JS crawler sees none of it.
Measured baseline: 26 visible words on the map page. Zero percent of the
informative text sits outside hidden containers.

The governance gates passed pre-change on 2026-08-09 (branch
`016-seo-improvement`, commit `91ced8b`).

| Gate | Status |
|------|--------|
| `make check-public` | clean (315 files) |
| `make check-layout` | clean (318 paths, 18 documented) |
| `make check-or005` | OK |
| `make check-git-history` | clean (105 commits, 0 open) |
| acceptance suite | 102 passed, 1 infra-flagged (exemption bookkeeping, resolved) |

## Post-change state (committed bundle, 2026-08-09)

The published bundle is identical to the source tree after `make publish`.
All checks below ran against `dist/` served on 127.0.0.1:8088.

| Page | Title | Meta description | Canonical | OG/Twitter | JSON-LD |
|------|-------|------------------|-----------|------------|---------|
| `index.html` | `Baumfläche Mannheim: Baumanteil je Gebäude im 60-m-Umkreis` (58 chars) | 156 chars, German | `https://abu-hamad.de/map/` | full 10-tag set | WebSite + Organization |
| `impressum.html` | `Impressum – Mannheim Baumfläche` (kept) | 148 chars, German | `https://abu-hamad.de/map/impressum` | none | none |
| `attribution.html` | `Datenquellen – Mannheim Baumfläche` (kept) | 146 chars, German | `https://abu-hamad.de/map/attribution` | none | none |

Crawler files and preview image:

| Resource | State |
|----------|-------|
| `/map/robots.txt` | 200 `text/plain`, `User-agent: *`, exactly three data-file `Disallow:` lines, no HTML disallow |
| `/map/sitemap.xml` | 200 XML, exactly the three canonical URLs, no `lastmod`, no data files or hashed assets |
| `/map/og-image.png` | PNG 1200×630, 211775 bytes (under 1 MB), visual render of the current map (Mannheim, current colors/labels) |

Visible content: the `#about` section (story, method, data sources, accuracy
disclaimer) sits below the map in page flow, outside hidden containers. The
distinctive SPIEGEL sentence occurs exactly once in the document. The
first-visit story modal holds no story copy; it shows over the map with
section (dismissal returns to the map view, persistence unchanged).

## Findings

Every finding carries a severity (high / medium / low) and a disposition
(`fixed` / `documented` / `owner-side`). The post-change pass completes the
evidence column.

| # | Finding | Severity | Disposition |
|---|---------|----------|-------------|
| F-01 | Map page title is the bare 10-char "Baumfläche" | high | fixed |
| F-02 | No meta description on any of the three pages | high | fixed |
| F-03 | No canonical tag on any of the three pages | high | fixed |
| F-04 | No Open Graph or Twitter Card tags, no preview image | high | fixed |
| F-05 | All informative text hidden in the `hidden` story dialog | high | fixed |
| F-06 | No structured data (JSON-LD) | medium | fixed |
| F-07 | No `/map/robots.txt`, no `/map/sitemap.xml` | medium | fixed |
| F-08 | Root-domain `robots.txt` (blog origin) lacks the `Sitemap:` line and data-file disallows | low | owner-side |
| F-09 | No JSON-LD `Dataset` record | low | documented |
| F-10 | No AI-bot HTML restrictions at the map path | low | documented |
| F-11 | Plain-HTTP requests to the canonical URL form served 200 by the worker (no scheme redirect; zone-level Always Use HTTPS not enabled) | high | fixed |

## Research summary

Scoped web research R-001 to R-009 with decisions D1 to D10 is documented
in `specs/016-seo-improvement/research.md`. The source list lives there.
Key decisions applied in this feature:

- D1/D2: informative content lives in the raw HTML, outside hidden
  containers. AI crawlers are treated as non-JS clients.
- D3: JSON-LD declares `WebSite` and `Organization` only. No `FAQPage`,
  `LocalBusiness`, or `Speakable`. Those rich-result types are dead or
  inapplicable. No `SearchAction`. The sitelinks search box was removed
  2024-11-21.
- D4: full OG set plus `twitter:card=summary_large_image`. The `og:image`
  is PNG with 1200 by 630 px (1.91:1). It stays under 1 MB with an
  absolute URL and declared dimensions.
- D5: the zone-level AI-bot split (Cloudflare Managed Content) is already
  enforced. The map-path `robots.txt` does not duplicate it.
- D6: CWV budgets stay unchanged. LCP 2.5 s, INP 200 ms, CLS 0.1 at p75.
  All 8 interactions at or under 2 s (feature 014 SC-008); the latency
  harness probes 5 of them via CDP (zoom in/out, trees toggle, popup,
  surface toggle), the remaining interactions are code-unchanged
  (FR-012). Desktop median at or under 123 ms.
  First usable at or under 10 s.
- D7: impressum and attribution keep their descriptive titles. Only
  descriptions and canonicals are added.
- D8: verification is server-side only. Search Console and Bing Webmaster
  use DNS-record or file-based verification. Zero client-side tracking.
- D9: the preview image is a committed static asset. It is generated via
  `scripts/parity-render.mjs` export mode from the current map rendering.
- D10: JSON-LD ships as an inline data block. The CSP stays unchanged.
  `script-src 'self'` does not apply to `application/ld+json` data blocks.
  That rule follows the HTML spec, section 4.12.1.

## Verification

Every check below reproduces on the committed tree and on the deployed
site (quickstart Q8). The acceptance suite enforces the machine-checkable
rules; the other commands give the observed outputs. Deployment record:
`validation/deploy-20260809-134930.json` (version
`bc57cc98-bbce-4b77-8329-c8ed61a4b616`); initial deploy record
`validation/deploy-20260809-131358.json` (version `33a5e699`).

```text
make publish
.venv/bin/python -m pytest tests/acceptance/test_seo_metadata.py -q
```

Expected: `17 passed`. The suite asserts titles (30 to 60 chars, never the
bare "Baumfläche"), descriptions (100 to 160 chars, pairwise distinct),
canonicals, the ten OG/Twitter properties, the og:image file (PNG,
1200×630, under 1 MB), the >= 80 % visible-word share, the single story
copy, the JSON-LD types, and the robots/sitemap rules.

Image and files (served from dist):

```text
file dist/og-image.png     # PNG image data, 1200 x 630
file dist/robots.txt       # ASCII text
curl -sI /map/robots.txt   # 200, text/plain
curl -sI /map/sitemap.xml  # 200, XML content type
```

Full regression pass on 2026-08-09:

```text
.venv/bin/python -m pytest tests/ -q          # 173 passed
make check-public                              # clean (315 files)
make check-layout                              # clean (318 paths, 18 documented)
make check-or005                               # OK
bash scripts/perf-measure.sh <url>             # first usable 376 ms (budget 10 s)
                                               # 5 probed CDP interactions, median 13 to 14 ms
                                               # (budget 2 s, 123 ms; 8-interaction set per SC-008)
node scripts/parity-render.mjs --archive <pmtiles> --out <dir>
                                               # property samples OK at all zooms
                                               # initial rendered count 12886 (unchanged)
```

One documented artifact: the now-scrollable page shows a vertical
scrollbar, which narrows the parity viewport by 15 px. Rendered counts at
z14/z16 drift accordingly (3473 to 3426, 185 to 172). Building values,
colors, labels, and popups are identical (property samples pass at every
zoom; style.json and popup code unchanged).

Post-deploy live verification (2026-08-09, version
`bc57cc98-bbce-4b77-8329-c8ed61a4b616` live; earlier versions
`33a5e699` and `95a7966b` superseded):

```text
curl -s https://abu-hamad.de/map/              # title 58 chars, meta description 156 chars,
                                               # canonical https://abu-hamad.de/map/, full
                                               # OG + twitter:card set, JSON-LD WebSite +
                                               # Organization (parses; no SearchAction;
                                               # no FAQPage/LocalBusiness/Speakable)
curl -sI /map/robots.txt                       # 200, text/plain, nosniff
curl -sI /map/sitemap.xml                      # 200, application/xml, nosniff
curl -sI /map/og-image.png                     # 200, image/png, 211775 bytes, 1200x630
curl -s -D - http://abu-hamad.de/map/           # 301 -> https://abu-hamad.de/map/ (single hop,
                                               # worker scheme redirect, SC-002; also for
                                               # /map/impressum and /map/robots.txt)
bash scripts/perf-measure.sh https://abu-hamad.de/map/
                                               # cold LCP 444 ms, TTFB 138 ms, CLS 0
                                               # (budgets: LCP 2.5 s, CLS 0.1 @ p75)
                                               # 5 probed CDP interactions, medians 13-14 ms
node scripts/smoke-verify.mjs https://abu-hamad.de/map/
                                               # popups, trees toggle, story-modal dismissal,
                                               # consoleErrors: []
# browser, fresh profile: first visit shows the story modal over the
# map (no scrolling, scrollY unchanged) with an attribution-page link;
# dismiss removes it and persists; reload does not re-show; the story
# phrase occurs exactly once in the DOM
```

The Google Rich Results Test runs against the deployed URL in a browser
and is owner-side manual (quickstart Q5): expected zero errors. The
machine-checkable JSON-LD evidence above (parse, types, absence of
forbidden types) is enforced by the acceptance suite.

## Quickstart Q1–Q8 validation results (2026-08-09)

Run end to end per `specs/016-seo-improvement/quickstart.md` on the
deployed site (`https://abu-hamad.de/map/`, version
`33a5e699-dd4c-4f1f-8bfb-32d7ff826618`).

| Scenario | Result | Evidence |
|----------|--------|----------|
| Q1 on-page metadata | PASS | `17 passed` in `test_seo_metadata.py`; live fetch: title 58 chars, description 156 chars, canonical + unique descriptions on all three pages; legal-page titles kept |
| Q2 link previews | PASS | Ten OG/Twitter properties in raw HTML; `og-image.png` 200 `image/png`, 1200×630, 211,775 B; sharing previews verified by tag set (manual share check owner-side) |
| Q3 crawler files | PASS | `robots.txt` 200 `text/plain` with exactly three data-file `Disallow:` lines, no HTML disallow; `sitemap.xml` 200 XML, exactly three canonical URLs, no `lastmod`; root-coordination lines documented owner-side below |
| Q4 visible content | PASS | 7 matches of SPIEGEL/CityTreeCover/Datenquellen in raw HTML; `-k visible` tests green (≥ 80 % visible words, single story copy, self-contained) |
| Q5 structured data + CSP | PASS | JSON-LD parses; WebSite + Organization; no SearchAction; no FAQPage/LocalBusiness/Speakable; CSP meta byte-identical; Rich Results Test manual step documented above |
| Q6 story modal | PASS | Browser (fresh profile): first visit shows modal over the map, no scroll (scrollY unchanged), attribution link opens new tab; dismiss persists; reload does not re-show; story phrase once in DOM; `smoke-verify.mjs` consoleErrors empty |
| Q7 nothing regresses | PASS | Gates green (check-public/check-layout/check-or005); full suite 173 passed; live perf: cold LCP 444 ms, CLS 0, 5 probed interactions median 13–14 ms (budgets 2 s / 123 ms); parity: 12886 initial, property samples OK |
| Q8 report reproducible | PASS | Every check in this report's Verification section re-run against the deployed site; stated results reproduce |

## Root coordination (owner-side, FR-010)

The domain root belongs to the blog origin (E-004). The authoritative
`/robots.txt` is the blog's file. It is not deployed from this repo.
The owner should add one line to the blog-origin root `robots.txt`:

```text
Sitemap: https://abu-hamad.de/map/sitemap.xml
```

Optionally duplicate the three data-file disallows:

```text
Disallow: /map/buildings.pmtiles
Disallow: /map/trees.pmtiles
Disallow: /map/buildings.geojson
```

The map-path `robots.txt` deployed by this repo is informational. Crawlers
read the authoritative directives from the domain root. Cloudflare caches
`robots.txt` by default. The edge TTL is 120 minutes for 200 responses
without `cache-control` (research D5). After a root-file edit the owner
must purge the cached copy or wait out the TTL. Sitemaps are not cached by
default. AI-bot rules already exist at the root and stay.

## Tradeoffs

Disallowing the three data files for all user agents may reduce
AI-assistant citations of the underlying data. The HTML pages stay
accessible to all bots (FR-008). Default recorded: data files blocked,
HTML accessible.

The map-path `robots.txt` is not authoritative on its own. Its value comes from the root coordination above.

## Measurement (server-side only, FR-001/FR-011)

Traffic and crawl evidence comes from Cloudflare logs. Those logs already
exist. No code change is needed. Crawl statistics come from the verified
Search Console and Bing Webmaster properties.

Property verification is server-side only. Search Console supports a DNS
TXT record or file upload. Bing Webmaster Tools supports the same. No HTML
tag, no client-side script, and no analytics anywhere.

Recommended properties: `https://abu-hamad.de/` (domain property) or
`https://abu-hamad.de/map/` (URL-prefix property) in Search Console. Bing
Webmaster can import the domain from Search Console or verify via DNS.
