# Research: SEO Assessment & Improvement (feature 016)

Phase 0 output. Resolves every NEEDS CLARIFICATION in the Technical Context. Sources: scoped web research R-001…R-008 (recorded in spec.md) plus a deep-research pass (4 parallel researcher agents, 128 sources, verifier-citation pass — the underlying evidence table is reproduced in §4). Decisions D1–D8 use the format Decision / Rationale / Alternatives considered.

## Summary

The highest-impact, cheapest wins are static-HTML metadata and content visibility: a descriptive German title + meta description + canonical on every page, Open Graph/Twitter Card tags with a 1200×630 preview image, moving the informative text out of the `hidden` story dialog into a visible section, JSON-LD structured data, and two crawler-facing files (`robots.txt`, `sitemap.xml`). No decision requires a new dependency, a build step, a JS change, or a CSP change.

## Decision Log

### D1 — Content that matters lives in raw HTML

**Decision**: The map page's informative text (story, method, sources, accuracy disclaimer) becomes visible in the initial HTML response, outside hidden containers and without JavaScript execution. All metadata (title, description, canonical, OG) is static markup in the head.

**Rationale**: Static HTML in the initial response is the only content guaranteed readable by every engine and AI crawler. Only Google and Bing are documented to render JavaScript; OAI-SearchBot, PerplexityBot, ClaudeBot and peers have no documented JS rendering, so static HTML is the safe assumption (D2). Static pages index faster and more reliably (R-001).

**Alternatives considered**: (a) Server-side rendering via the Worker — rejected: no application server, Worker serves a static bundle by design (FR-001, feature 005), and the content is static anyway. (b) Keeping text hidden and relying on Google's JS rendering — rejected: excludes non-JS crawlers and AI bots, and hidden content is contextually devalued (R-003).

### D2 — AI crawler behavior is treated as non-JS

**Decision**: All copy that must reach AI assistants and non-JS crawlers lives in raw HTML. No claim is made about any bot's JS support; the safe assumption governs.

**Rationale**: No official documentation states that OAI-SearchBot or PerplexityBot execute JavaScript. DuckDuckGo's own-index share is still rolling out and unknown. The conservative baseline costs nothing and covers every crawler.

**Alternatives considered**: (a) Assuming Google-style rendering everywhere — rejected: unverifiable, excludes real non-JS clients. (b) Blocking AI bots from HTML — rejected: the zone policy (research D5) already splits AI bots from data files; HTML stays accessible to all bots per FR-008.

### D3 — Structured data: WebSite + Organization, no dead rich-result types

**Decision**: Inline JSON-LD declares `WebSite` (name, url, alternateName; no `SearchAction` — sitelinks search box removed 2024-11-21) and `Organization`, aligned to visible content only. A `Dataset` record MAY be added (it feeds Dataset Search, not Google Search rich results). `FAQPage`, `LocalBusiness`, and `Speakable` MUST NOT be added.

**Rationale**: FAQ rich results ended 2026-05-07; the sitelinks search box was removed 2024-11-21. Marking up dead features adds noise and risk for zero rich-result value. `Dataset` is optional because it serves Dataset Search discovery, which is real but marginal for this site.

**Alternatives considered**: (a) `FAQPage` for the FAQ-like story content — rejected: feature is dead. (b) `LocalBusiness`/`Speakable` — rejected: inapplicable or deprecated surface. (c) No structured data at all — rejected: WebSite/Organization is cheap, zero-risk, and improves entity understanding.

### D4 — Open Graph / Twitter Card: full set, PNG/JPG image

**Decision**: The map page carries the full OG set — `og:title`, `og:description`, `og:type`, `og:url`, `og:site_name`, `og:locale=de_DE`, `og:image`, `og:image:width`, `og:image:height` — plus `twitter:card=summary_large_image`. The preview image is PNG or JPG, 1200×630 (1.91:1), under 1 MB, with declared dimensions.

**Rationale**: WebP is inconsistently decoded by scrapers; PNG/JPG is the safe format. `twitter:card` is required — there is no OG fallback for X/Twitter cards. Declared dimensions prevent layout jank in scrapers. `og:locale=de_DE` matches the German content.

**Alternatives considered**: (a) WebP image — rejected: inconsistent scraper decode (research R-008). (b) Dynamic image endpoint — rejected: the site is a static bundle (FR-001); a committed, generated image is deterministic and cacheable. (c) Omitting `twitter:card` — rejected: X would fall back to a bare link card.

### D5 — Crawler files: map-path robots.txt + sitemap.xml; zone policy documented, not duplicated

**Decision**: `/map/robots.txt` returns 200 `text/plain` and disallows the three data files (`buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson`) for ALL user agents, including GPTBot, ClaudeBot, PerplexityBot, CCBot. It does not block HTML pages and does not repeat the zone-level AI-bot split (already enforced via Cloudflare Managed Content — spec assumption, verified 2026-08-09). `/map/sitemap.xml` returns 200 XML and lists exactly the three canonical URLs. The root-domain `robots.txt` (blog origin) additions — the `Sitemap:` line and optionally the data-file disallows — are documented in the assessment report as owner-side actions (FR-010), not deployed from this repo.

**Rationale**: Crawlers and AI bots only honor `/robots.txt` at the domain root; the map-path file is informational and for direct submission. Cloudflare caches `robots.txt` by default (120-min edge TTL for 200 responses without cache-control) but not `.xml` sitemaps — a fact the owner-side purge rule must account for. The three data files contain no HTML, so disallowing them loses no indexing value and protects crawl budget.

**Alternatives considered**: (a) Deploying a root `robots.txt` from this repo — rejected: the root belongs to the blog origin (E-004); overriding it would break the blog's own policy. (b) Putting `Sitemap:` in the map-path file only — rejected: crawlers read `Sitemap:` from the domain root; the map-path file is not authoritative. (c) Blocking AI bots from HTML — rejected: FR-008 requires HTML stay accessible; the tradeoff (fewer AI citations) is recorded in the report instead.

### D6 — CWV budgets stay authoritative and unchanged

**Decision**: The feature 014 budgets remain: LCP 2.5 s, INP 200 ms, CLS 0.1 (p75), plus the repo's own interaction budgets (8 interactions ≤ 2 s, desktop median ≤ 123 ms, first usable ≤ 10 s). SEO work adds only static text and head tags.

**Rationale**: The scoped research confirms current CWV thresholds (R-005); no threshold change is documented as of 2026-08. Static additions cannot regress interaction latency; the perf harness proves it. INP replaced FID on 2024-03-12, so INP is the metric the harness reports.

**Alternatives considered**: (a) Optimizing the visible section into a lazy-load — rejected: defeats the purpose (content must be in initial HTML). (b) Adding preload hints for the preview image — rejected: the image is only needed on link preview; it must not compete with map-critical resources.

### D7 — Impressum and transparency are E-E-A-T signals

**Decision**: Keep the existing descriptive titles on `impressum`/`attribution`; add unique German meta descriptions and canonical tags. The accuracy disclaimer (feature 010) and data-source transparency stay visible. § 5 DDG has been in force since 2024-05-14 and the impressum already cites it.

**Rationale**: Health/safety-adjacent content (heat protection) is held to a higher quality bar; transparency about data, method, sources, and accuracy is a documented E-E-A-T signal (R-009). There is no official statement that an impressum is itself a ranking factor, but it is a legal requirement and trust signal.

**Alternatives considered**: (a) Noindexing the legal pages — rejected: they carry the transparency signals and are already linked. (b) Rewriting the existing titles — rejected: they are already descriptive and match the spec's FR-003 "keep existing titles".

### D8 — Verification is server-side only

**Decision**: Search Console and Bing Webmaster properties are verified server-side (DNS record or file upload). Zero client-side tracking is added anywhere (FR-001).

**Rationale**: The site has no analytics by design. Server-side verification works without any page change and adds no privacy surface.

**Alternatives considered**: (a) Analytics/beacon to measure SEO traffic — rejected: explicitly out of scope (FR-001/FR-011). (b) Relying on Cloudflare logs for traffic evidence — acceptable, already available, no code needed; noted in the assessment report as the measurement method.

### D9 — Preview image is a committed static asset

**Decision**: `og-image.png` (1200×630) is generated from the current map rendering via the committed parity/rendering tooling (`scripts/parity-render.mjs` gains an export mode), committed in `src/site/`, copied by `publish.py` like other STATIC_FILES, and served unhashed from the map path. When the map rendering changes (colors, data version, labels), the image MUST be regenerated and recommitted in the same change.

**Rationale**: A committed image is deterministic, versioned, and reviewable; freshness is enforced by contract + quickstart check (visual match with the current bundle, same tooling as the parity gate). "Static image, not a dynamic endpoint" is the spec's assumption.

**Alternatives considered**: (a) Generating at publish time in `publish.py` — rejected: adds node/Chromium to the Python publish pipeline and makes publish nondeterministic (headless render timing). (b) Unversioned URL (`/og-image.png` overwritten in R2) — rejected: loses reviewability and the git record.

### D10 — JSON-LD is CSP-compatible without changing the policy

**Decision**: JSON-LD ships as an inline `<script type="application/ld+json">` block in `<head>`. The CSP meta tag is not touched. Verification: the page loads in a browser under the locked CSP and the Rich Results Test reports zero errors.

**Rationale**: Per the HTML spec (§4.12.1), a script element whose type is not a JavaScript MIME type is a data block — it is not executed, and `script-src 'self'` does not apply to it. Browsers and Google's validator treat `application/ld+json` this way.

**Alternatives considered**: (a) External JSON-LD file loaded via `src` — rejected: extra request, no CSP benefit (data blocks are already exempt), and the site's CSP/`connect-src` posture is unchanged. (b) Altering CSP to allow `'unsafe-inline'` for scripts — rejected: would weaken the locked policy (feature 015).

## Scoped research notes (R-001 … R-009, from spec)

- **R-001 (JS rendering)**: Google renders and indexes JavaScript, but static-HTML pages index faster, more reliably, and are readable by AI crawlers that cannot execute JS. 2026 de-facto best practice: keep content that matters in raw HTML.
- **R-002 (titles/descriptions)**: Title tags ~50–60 characters (~600 px, truncation ≈ 525–535 px); meta descriptions ~120–160 characters. Vague or mixed-intent pages get titles/descriptions rewritten by Google.
- **R-003 (hidden content)**: Google can index `display:none`/`hidden` content, but hiding material contextually devalues it; content behind interaction is not treated like visible content.
- **R-004 (robots.txt/sitemap)**: Both are static text files; the `Sitemap:` directive belongs in the domain-root robots.txt; sitemaps must not list data files or hashed assets.
- **R-005 (CWV)**: LCP 2.5 s / INP 200 ms / CLS 0.1 at p75; INP replaced FID (2024-03-12).
- **R-008 (OG images)**: 1200×630 (1.91:1), declared dimensions, `og:locale=de_DE`; PNG/JPG preferred over WebP.
- **R-009 (YMYL/E-E-A-T)**: Health/safety-adjacent content (heat protection) is held to a higher quality bar; transparency about data, method, sources, and accuracy is an E-E-A-T signal.

## Verifier-citation evidence table (deep-research pass, 2026-08-09)

Every claim below was checked against the cited source; Result is the verifier verdict.

| Claim | Check | Result |
|-------|-------|--------|
| Dataset markup feeds Dataset Search, not Google Search rich results | developers.google.com/search/docs/appearance/structured-data/dataset | PASS — "easier to find in the Dataset Search tool"; JSON-LD preferred; Rich Results Test for validation |
| Cloudflare caches robots.txt by default, not HTML/JSON | developers.cloudflare.com/cache/concepts/default-cache-behavior/ | PASS — "The Cloudflare CDN does not cache HTML or JSON by default. Additionally, by default Cloudflare caches a website's robots.txt." Edge TTL 120 m for 200/206/301 without cache-control |
| CWV thresholds LCP 2.5 s / INP 200 ms / CLS 0.1 @ p75 | developers.google.com/search/docs/appearance/core-web-vitals + web.dev vitals (R-005) | PASS |
| Sitelinks search box removed 2024-11-21 | Google blog "Farewell, Sitelinks Search Box" (2024-10) | PASS |
| FAQ rich results ended 2026-05-07 | SEJ + Google changelog (2026) | PASS (secondary, consistent) |
| § 5 DDG since 2024-05-14 | gesetze-im-internet.de/ddg/__5.html; live impressum already cites § 5 DDG | PASS |
| og:image 1200×630 PNG/JPG < 1 MB, og:locale de_DE | ogp.me spec + Facebook sharing best practices (R-008) | PASS |
| INP replaced FID 2024-03-12 | web.dev blog | PASS |
| OAI-SearchBot / PerplexityBot execute JS? | No official docs — static HTML is the safe assumption (D2) | OPEN → resolved by D2 |
| DuckDuckGo own-index share of traffic | Rolling out; unknown (D2) | OPEN → resolved by D2 |
| CWV threshold changes | None documented as of 2026-08 (D6) | OPEN → resolved by D6 |
| Impressum as ranking factor | No official statement; legal requirement + trust signal (D7) | OPEN → resolved by D7 |

All NEEDS CLARIFICATION resolved. No open questions remain.
