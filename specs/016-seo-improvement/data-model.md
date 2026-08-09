# Data Model: SEO Assessment & Improvement (feature 016)

Phase 1 output. Entities, fields, validation rules, and state transitions the feature's artifacts must satisfy. The feature touches metadata, crawler-facing files, content visibility, and structured data; the map's data values, colors, labels, popups, and interactions are locked (FR-012) and are NOT modeled here.

## Entities

### E1 — CanonicalUrl

One canonical URL per page. Contract: `contracts/on-page-metadata.md`; implementation: `<link rel="canonical">` in each HTML head.

| Field | Value | Rule |
|-------|-------|------|
| page | enum `map` / `impressum` / `attribution` | Exactly these three indexable pages (feature 005/015). |
| canonical_url | absolute URL | `https://abu-hamad.de/map/`, `https://abu-hamad.de/map/impressum`, `https://abu-hamad.de/map/attribution`. Trailing slash only on the map page (the canonical form; `/map/index.html` already 307-redirects, research D1). |
| redirects | set | `www` and no-trailing-slash variants 301 to canonical (existing Worker behavior); `/map/index.html` 307 (existing). |

Validation: every page's canonical tag equals exactly its canonical URL; the tag is present in raw HTML; SC-002 (each page resolves exactly one indexable URL).

### E2 — PageMetadata

Title and meta description per page (FR-002/003). Contract: `contracts/on-page-metadata.md`.

| Field | Type | Rule |
|-------|------|------|
| page | ref E1 | |
| title | string | German. Unique per page. Map page: 30–60 characters, descriptive, covers what the map shows and where (never the bare "Baumfläche"). Impressum/attribution: keep existing descriptive titles. |
| meta_description | string | German, 100–160 characters, unique per page, summarizes page content. None of the three pages may lack it or share one. |
| lang | const `de` | Already present on all three pages; unchanged. |

Validation (FR-002/003, SC-003): raw HTML contains a single `<title>` and a single `meta[name=description]` meeting the length rules; no page carries the bare title "Baumfläche"; descriptions are pairwise distinct. Exact copy is finalized in the tasks phase against these constraints (example candidates in the contract).

### E3 — LinkPreviewMetadata

Open Graph + Twitter Card fields on the map page only (FR-005). Contract: `contracts/link-preview.md`.

| Field | Rule |
|-------|------|
| og:title | German, descriptive, matches page title semantics (may equal title). |
| og:description | German, 100–160 chars. |
| og:type | `website`. |
| og:url | Canonical URL `https://abu-hamad.de/map/`. |
| og:site_name | Site name, e.g. "Baumfläche Mannheim". |
| og:locale | `de_DE` (research D4). |
| og:image | Absolute URL of E4, served from the map path. |
| og:image:width / :height | `1200` / `630` (declared; 1.91:1). |
| twitter:card | `summary_large_image` (required — no OG fallback, research D4). |

Validation: all fields present with correct values in raw HTML (SC-005); acceptance test parses the tags.

### E4 — OgImage

The link-preview image (FR-005, D9). File: `src/site/og-image.png` → `dist/og-image.png`.

| Field | Rule |
|-------|------|
| format | PNG or JPG (WebP inconsistently decoded, research D4). |
| dimensions | 1200×630 px, ratio 1.91:1. |
| size | < 1 MB. |
| served_from | Map path (unhashed — feature 014 hashed-bundle contract excludes it), HTTP 200. |
| content | Visual render of the current map (colors, data version, labels). Must not show a stale or wrong city. |
| generation | `scripts/parity-render.mjs` export mode (1200×630 viewport), committed in `src/site/` (D9). |

Invariant (freshness): any change to the map rendering (colors, data, labels) MUST regenerate and recommit `og-image.png` in the same change; mismatch is a correctness bug (spec edge case).

### E5 — RobotsTxt

Crawler policy at `/map/robots.txt` (FR-008). File: `src/site/robots.txt`.

| Field | Rule |
|-------|------|
| content_type | `text/plain`, HTTP 200. |
| disallowed | `buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson` (map-path relative) for ALL user agents (`User-agent: *`). |
| allowed | All HTML pages — no `Disallow:` on `/map/`, `/map/impressum`, `/map/attribution`, or any HTML path. |
| zone_policy | Zone-level AI-bot split (Cloudflare Managed Content, research D5) documented in the assessment report, NOT duplicated in this file. |
| sitemap_line | Optional informational `Sitemap:` line pointing to the absolute sitemap URL (research R-004). |

Validation (SC-006): file contains the three disallows; no HTML disallow; served 200 `text/plain`; acceptance test asserts the rules.

### E6 — SitemapXml

Page inventory at `/map/sitemap.xml` (FR-009). File: `src/site/sitemap.xml`.

| Field | Rule |
|-------|------|
| content_type | XML (`application/xml`), HTTP 200. |
| entries | Exactly three absolute URLs: `https://abu-hamad.de/map/`, `…/map/impressum`, `…/map/attribution`. |
| lastmod | Omit (hand-written `lastmod` goes stale between publishes; never claim a false date — spec edge case). |
| excluded | No data files, no hashed assets, no `og-image.png`. |

Validation (SC-006): parse yields exactly 3 `<url>` entries matching E1; no data file or hashed asset appears.

### E7 — JsonLdBlock

Structured data (FR-007, D3). Inline `<script type="application/ld+json">` in the map page head.

| Type | Fields | Rule |
|------|--------|------|
| WebSite | name, url, alternateName | REQUIRED. No `SearchAction` (sitelinks search box removed 2024-11-21). |
| Organization | name, url | REQUIRED. |
| Dataset | subject, coverage, license, sources | OPTIONAL (feeds Dataset Search, not Google Search rich results — D3). |
| FAQPage / LocalBusiness / Speakable | — | FORBIDDEN (D3). |

Validation: block parses as JSON; required types/fields present; forbidden types absent; aligned to visible content only (no facts that are not on the page); Rich Results Test zero errors; page loads under the locked CSP (JSON-LD is a data block, HTML spec §4.12.1 — D10).

### E8 — VisibleContentSection

Crawlable content on the map page (FR-006). Implementation: a visible `<section>` in `src/site/index.html`.

| Field | Rule |
|-------|------|
| content | Project story (SPIEGEL context, CityTreeCover reference, GitHub link), method (60-m radius, 30 % guideline), data sources, accuracy disclaimer (feature 010). |
| visibility | Superseded (owner decision 2026-08-09): the story lives in the hidden modal; no visible-section criterion applies. |
| single_copy | Story text exists in EXACTLY one DOM location — inside the modal (Clarifications 2026-08-09, final). |
| self_contained | Must not reference "the map above" (non-JS crawlers see no map); explains itself. |
| word_share | Superseded (owner decision 2026-08-09): SC-004 no longer applies. |

Validation: acceptance test extracts informative text, counts words inside vs outside hidden containers, asserts ≥ 80 % and exactly one occurrence of the story copy.

### E9 — StoryModalBehavior

Feature 007 preservation (Clarifications 2026-08-09).

| Field | Rule |
|-------|------|
| trigger | First visit opens the modal as today. |
| content_source | Modal holds the full story text itself (single copy). It shows over the map without scrolling; links open in new tabs. No second story text in the DOM. |
| dismiss_persistence | Unchanged (dismiss → no modal on later visits). |
| smoke | `tests/frontend/smoke_us5.md` updated to the new interaction; headless `scripts/smoke-verify.mjs` covers it. |

### E10 — AssessmentReport

Committed deliverable (FR-001). File: `verification/seo-assessment-2026-08-09.md`. Contract: `contracts/assessment-report.md`.

| Section | Contents |
|---------|----------|
| current_state | Evidence per page: fetched raw HTML state before changes (title, description, canonical, OG, JSON-LD, visible text) with dates. |
| findings | Each finding: severity (high/medium/low) and disposition (`fixed` / `documented` / `owner-side`). |
| research_summary | R-001…R-009 scoped research + D1–D10 decisions, source list. |
| verification | Reproducible before/after checks: exact commands, expected output (quickstart Q8 re-runs them). |
| root_coordination | Exact lines the owner must add to the blog-origin `robots.txt` (FR-010): `Sitemap:` line, optional data-file disallows; Cloudflare robots.txt 120-min edge TTL purge note (D5). |
| tradeoffs | AI-bot policy side effect: disallowing data files may reduce AI-assistant citations; recorded owner-visible tradeoff (default: data files blocked, HTML accessible). |
| measurement | Server-side only: Cloudflare logs + Search Console/Bing Webmaster verification (DNS/file-based, no client tracking — FR-001/011). |

Validation (SC-001): report exists; every finding has severity + disposition; every listed verification check reproduces (quickstart Q8).

### E11 — RootDomainCoordination

Owner-side actions, not deployed from this repo (FR-010, E-004). Recorded in E10.

| Item | Rule |
|------|------|
| `Sitemap:` line | `Sitemap: https://abu-hamad.de/map/sitemap.xml` added to the blog-origin root `robots.txt` by the owner. |
| data-file disallows | Optional: duplicate the three disallows at root level. |
| purge | Root file edit must account for Cloudflare's default 120-min `robots.txt` edge cache (D5). |

## State transitions

- **OgImage freshness** (E4): map rendering changes (colors/data/labels) → regenerate `og-image.png` via parity tooling → recommit in the same change. No regeneration on metadata-only changes.
- **Modal behavior** (E9): pre-feature (modal holds hidden copy) → post-feature (modal opens/scrolls to visible section; dismiss persistence unchanged). No further transitions; persistence key unchanged.
- **Sitemap staleness** (E6): no `lastmod` field, so no staleness transition exists by design.

## Validation rules consolidated from spec

- FR-002/003/SC-003: title 30–60, description 100–160, German, unique per page, never bare "Baumfläche".
- FR-004/SC-002: canonical tag per page equals its canonical URL; `/map/` and `/map/index.html` not duplicates (307 exists); www variants 301.
- FR-005/SC-005: full OG set + `twitter:card=summary_large_image`; `og:image` 1200×630, < 1 MB, 200, PNG/JPG.
- FR-006/SC-004/SC-010: informative text ≥ 80 % outside hidden containers; exactly one story copy in DOM; self-contained copy.
- FR-007/SC-007: JSON-LD WebSite + Organization (no SearchAction); Dataset optional; FAQPage/LocalBusiness/Speakable forbidden; zero RRT errors; CSP unchanged and page loads under it.
- FR-008/009/SC-006: robots.txt 200 `text/plain` with three data-file disallows for all user agents, HTML never blocked; sitemap 200 XML with exactly 3 canonical URLs, no data files/hashed assets; zone AI-bot policy documented, not duplicated.
- FR-010: root-domain lines documented in the report as owner-side actions.
- FR-001/011/SC-009: zero client-side tracking; verification server-side (DNS/file-based properties).
- FR-012/013/SC-008: map values, colors, labels, popups, interactions, caching semantics, security headers, hashed-bundle contract unchanged; all tests/gates pass; interaction budgets hold.
