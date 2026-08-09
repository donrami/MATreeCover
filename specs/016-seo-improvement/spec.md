# Feature Specification: SEO Assessment & Improvement

**Feature Branch**: `016-seo-improvement`
**Created**: 2026-08-09
**Status**: Draft
**Input**: User description: "we need to assess and improve SEO aspects of the site ... perform scoped web research"

## Scope

### Goal

Assess the search-engine and link-sharing visibility of the live map site (`https://abu-hamad.de/map/`) against current SEO practice, then close the highest-impact gaps. The map itself and its data values, colors, labels, popups, and interactions stay unchanged; the work is metadata, crawler-facing files, content visibility, and structured data. A committed assessment report documents the before/after state.

### Current State (evidence)

- Deployed surface (feature 005/015): static bundle served by a Cloudflare Worker at `https://abu-had.de/map/` (canonical), `www` and `/map` 301-redirect to it; `impressum` and `attribution` are the only other pages; domain root and all non-`/map/*` paths belong to the blog origin (E-004). No application server, no database, no analytics (FR-001).
- `src/site/index.html`: `<title>Baumfläche</title>` (10 characters, no location, no keyword — vague titles get rewritten by Google, research R-002); **no meta description**, **no canonical tag**, **no Open Graph or Twitter Card tags**, **no structured data**.
- `impressum.html` and `attribution.html` have descriptive titles ("Impressum – Mannheim Baumfläche", "Datenquellen – Mannheim Baumfläche") but no meta descriptions or canonical tags.
- The only informative text on the map page (project story, SPIEGEL source, CityTreeCover reference, GitHub link) lives inside a `hidden` story dialog (feature 007). It is present in the initial HTML (crawlable raw), but hidden content is contextually devalued and invisible to non-JS crawlers — the page renders with essentially zero visible text beyond the heading and legend (research R-003).
- `dist/` (verified listing) contains no `robots.txt` and no `sitemap.xml`. Live checks (2026-08-09, research.md D1): `/map/robots.txt` → 404, `/map/sitemap.xml` → 404. The three R2-served data files (`buildings.pmtiles` ~25+ MiB, `trees.pmtiles`, `buildings.geojson`) are reachable by any crawler (root robots has `Allow: /` for general user agents) with no data-file disallow (research R-004/R-006).
- Live checks (2026-08-09, research.md D1) also established: `/map/index.html` → 307 → root (no duplicate-content path exists); the zone root `robots.txt` already carries Cloudflare Managed Content with `Content-Signal: search=yes,ai-train=no,use=reference` and disallows AI training bots (`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `Applebot-Extended`, `Meta-ExternalAgent`, `Bytespider`, `Amazonbot`, `ia_archiver`) while leaving search/retrieval bots allowed — the AI-bot split policy is already implemented at the zone; the `impressum` page already cites § 5 DDG (in force 2024-05-14).
- The site already has: `lang="de"`, a semantic `h1`, CSP, accessibility labels, hashed immutable assets with preconnect/preload (feature 014), Core Web Vitals budgets (interaction median ≤ 123 ms desktop, all 8 interactions ≤ 2 s), and an accuracy disclaimer (feature 010).
- Publish pipeline (`src/pipeline/publish.py`) copies a fixed `STATIC_FILES` set into `dist/` and content-hashes only `main.js`, `style.css`, `style.json`; HTML is served with `public, max-age=0, must-revalidate` so crawlers always revalidate.

### Scoped Web Research (R-001 … R-008)

- **R-001 (JS rendering)**: Google can render and index JavaScript, but static-HTML pages are indexed faster, more reliably, and are readable by AI crawlers that cannot execute JS. De-facto best practice in 2026: keep the content that matters in the raw HTML. (seo-kreativ.de, thegrowthterminal.com, blog.rankinglens.com)
- **R-002 (titles/descriptions)**: Title tags ~50–60 characters (~600 px, truncation ≈ 525–535 px); meta descriptions ~120–160 characters. Vague or mixed-intent pages get titles/descriptions rewritten by Google. (scaler.com, lettercounter.org, wscubetech.com, seeklab.io)
- **R-003 (hidden content)**: Google can index `display:none`/`hidden` content, but the context and intent of hiding matter; visibility is a quality signal. Content behind interaction is not treated like visible content. (fennecseo.app, contentforest.com, webmasters.stackexchange.com)
- **R-004 (robots.txt/sitemap)**: `robots.txt` and `sitemap.xml` are static text files; the `Sitemap:` directive in robots.txt points crawlers at the XML. Cloudflare serves them as plain assets. (developers.cloudflare.com, cloudflare.com/learning, metricspot.com)
- **R-005 (Core Web Vitals)**: Official thresholds unchanged: LCP < 2.5 s, INP < 200 ms, CLS < 0.1. (developers.google.com/search/docs/appearance/core-web-vitals) — the site already operates inside these budgets.
- **R-006 (AI crawlers)**: Zones can manage `robots.txt` to direct AI-bot operators on content scraping; bot policy is a first-class concern in 2026. (developers.cloudflare.com/bots/additional-configurations/managed-robots-txt)
- **R-007 (structured data)**: JSON-LD with visible-content alignment; correct schema selection (WebSite, Dataset) and validation via Rich Results Test; pages with valid rich-result markup earn higher CTR. (netstager.ae, digitalapplied.com, technovapartners.com)
- **R-008 (Open Graph)**: `og:image` 1200×630 px (1.91:1) is the shared standard for Facebook, LinkedIn, X, Discord, Slack, WhatsApp, Telegram; required fields: `og:title`, `og:description`, `og:type`, `og:url`, `og:image`. (fastedit.net, featureimg.com, env.dev/guides/opengraph)
- **R-009 (YMYL/E-E-A-T)**: Health/safety-adjacent content (heat protection) is held to a higher quality bar; transparency about data, method, sources, and accuracy is an E-E-A-T signal. (searchengineland.com/guide/ymyl, theguidex.com)

A deep-research pass (4 parallel researcher agents, 128 sources, verifier-citation pass) augments the above; see `research.md` (D1–D8). Key added findings: static HTML in the initial response is the only content guaranteed readable by every engine and AI crawler (only Google and Bing are documented to render JS); `Dataset` markup feeds Dataset Search, not Google Search rich results; `FAQPage` rich results are dead (2026-05-07) and sitelinks search box was removed (2024-11-21) — neither should be added; `og:image` should be PNG/JPG (WebP inconsistently decoded), `< 1 MB`, with declared dimensions and `og:locale=de_DE`; `twitter:card` is required with no OG fallback; Cloudflare caches `robots.txt` by default (120-min edge TTL) but not `.xml` sitemaps; CWV thresholds are unchanged (LCP 2.5 s / INP 200 ms / CLS 0.1 @ p75) and HTML caching is a performance play, not a direct ranking factor.

### In Scope

- Committed SEO assessment report: current-state evidence, findings with severity, research summary, before/after verification.
- On-page metadata for all three pages: descriptive title, meta description, canonical tag.
- Link-sharing metadata on the map page: Open Graph + Twitter Card tags with a 1200×630 preview image.
- Crawler-visible content: the primary informative text (story, method, sources, accuracy disclaimer) visible without interaction in the initial HTML.
- Structured data (JSON-LD): WebSite and Dataset markup aligned with visible content.
- Crawler-facing files: `robots.txt` (data files disallowed for all user agents; zone-level AI-bot policy documented, not duplicated) and `sitemap.xml` (exactly the three canonical URLs) served from the map path.
- Server-side search-engine property verification (Search Console / Bing Webmaster), no client-side tracking.
- Root-domain coordination documented as an owner-side step (blog origin robots.txt `Sitemap:` line + AI-bot rules).
- Regression verification: existing test suites, all gates, CWV budgets, map parity.

### Out Scope

- Server-side rendering, prerendering, or static snapshots of the map canvas (the map is not indexable content; the page's text is).
- Analytics, tracking, consent banners (FR-001: no tracking — verification is server-side only).
- Keyword research or content strategy beyond the page's existing topics; paid search; link building; social accounts.
- Any change to the blog origin's files (root `robots.txt` edits are owner-side, documented but not deployed from this repo).
- Multi-language versions or `hreflang` (the site is German-only).
- Changes to map values, colors, labels, popups, interactions, caching semantics, or data files.

## Clarifications

### Session 2026-08-09

- Q: What happens to the first-visit story modal (feature 007) once the story text becomes visible on the page? → A: Final decision (2026-08-09): the modal holds the FULL story text again (feature 007 restored: title, story paragraphs, SPIEGEL/CityTreeCover/GitHub links, Methode, Datenquellen, Genauigkeit). There is no visible section under the map; the map is the only content on the page. The story exists in exactly one DOM location (inside the hidden modal). Owner explicitly accepts the SEO tradeoff: the story text is no longer visible in the initial page (research R-003: hidden content is indexed but contextually devalued).
- Q: An SEO tool reported that `http://abu-hamad.de/map/` returns 200 over plain HTTP instead of redirecting to HTTPS. How is this fixed? → A: Worker-level scheme redirect — `workers/map/index.js` gains an `http:` → `https://` 301 for every `/map*` request (placed after the `www` and `/map` rules so every redirect stays a single hop). This supersedes the earlier plan constraint of no worker change in this feature for the redirect case; deployed via the standard deploy flow, SC-002 extended to cover the scheme variant.
- Q: When the first-visit modal opens, what should happen to get the user to the story section? → A: No scrolling at all; the modal shows over the map and holds the full story text (restored feature 007 content). The auto-scroll-to-`#about` and the scroll-back-on-close are removed; the `#about` section itself is deleted (nothing under the map). Dismissal (close button / Escape) persists as before; links inside the modal open in new tabs.
- Q: The visible story section under the map and the short attribution-only modal are not wanted. What should the page look like? → A: Remove everything under the map — the map is the only content. Restore the old modal with the full story text (single DOM copy inside the modal). This supersedes the earlier visible-section decisions (FR-006 visibility requirement, SC-004, SC-010 are dropped for the story text).

## User Scenarios & Testing

### User Story 1 - Search Engines Understand the Map Page (Priority: P1)

A person searching for Mannheim tree-cover, Baumfläche, or heat-protection information finds the page and the search result shows a clear, descriptive title and summary — not "Baumfläche" with a blank snippet. The page's real content (what the map shows, how it was made, sources, accuracy limits) is readable by crawlers and by AI crawlers that do not execute JavaScript.

**Why priority**: Without descriptive metadata and crawlable text, the page has no search presence at all — every other improvement builds on this. The page currently has ~10 characters of title, no description, and zero visible body text.

**Independent Test**: Fetch the raw HTML of `https://abu-hamad.de/map/` and assert: descriptive title (30–60 chars), meta description (100–160 chars), canonical tag matching the canonical URL, and that the story text is present exactly once in the raw HTML, inside the hidden first-visit modal (final Clarifications 2026-08-09).

**Acceptance Scenarios**:
1. **Given** the map page, **When** its raw HTML is fetched, **Then** it contains a unique descriptive title of 30–60 characters and a meta description of 100–160 characters in German, neither of which is the current "Baumfläche".
2. **Given** the map page, **When** its raw HTML is fetched, **Then** it contains a canonical link tag pointing to `https://abu-hamad.de/map/`.
3. **Given** the map page, **When** its raw HTML is fetched without JavaScript execution, **Then** the story text (story, method, sources, disclaimer) is present exactly once in the raw HTML, inside the first-visit story modal (final Clarifications 2026-08-09; the earlier ≥ 80 % visible-word criterion is superseded).
4. **Given** the published bundle, **When** `/map/index.html` and `/map/` are fetched, **Then** both resolve to the same canonical URL and the canonical tag identifies exactly one URL per page.
5. **Given** `impressum` and `attribution` pages, **When** their raw HTML is fetched, **Then** each has a unique meta description and a canonical tag matching its canonical URL.

### User Story 2 - Link Previews Render Everywhere (Priority: P1)

The site spreads through links (SPIEGEL context, GitHub, social posts). When someone shares `https://abu-hamad.de/map/` on WhatsApp, Telegram, X, LinkedIn, or Discord, the share shows a title, a description, and a map preview image — not a bare URL or an empty card.

**Why priority**: The site has no advertising and relies on organic reach; link previews are the first impression for every shared link. This is the cheapest visible win (static tags + one image).

**Independent Test**: Run the raw page HTML through an Open Graph validator (or inspect the tags directly) and confirm `og:title`, `og:description`, `og:type`, `og:url`, `og:image`, `og:locale`, and `twitter:card` are present and that the `og:image` URL returns 200 with a 1200×630 image.

**Acceptance Scenarios**:
1. **Given** the map page HTML, **When** inspected for link-sharing tags, **Then** all required Open Graph and Twitter Card fields are present with correct values.
2. **Given** the `og:image` URL, **When** fetched, **Then** it returns 200, a 1.91:1 image of at least 1200×630 pixels, and a size under 1 MB.
3. **Given** the shared URL, **When** previewed on at least 3 of Facebook/LinkedIn/X/WhatsApp/Telegram/Discord/Slack, **Then** the preview shows title, description, and the map image.
4. **Given** the map page, **When** shared, **Then** the preview image visually matches the current map rendering (no stale or wrong city shown).

### User Story 3 - Crawlers and AI Bots Are Told What to Fetch (Priority: P2)

Crawlers and AI bots do not waste bandwidth and crawl budget downloading multi-megabyte geodata files that contain no HTML content, and they can find the site's real pages via a sitemap. The owner can prove, from committed files, what bots are allowed to fetch.

**Why priority**: The data files (one > 25 MiB) are served `no-store` from R2 and today any bot may download them repeatedly. Cheap to fix, protects infrastructure and crawl budget (R-004/R-006).

**Independent Test**: Fetch `/map/robots.txt` and `/map/sitemap.xml`, verify status 200, correct content types, that the sitemap lists exactly the three canonical URLs, and that robots rules disallow the three data files for all user agents including AI bots.

**Acceptance Scenarios**:
1. **Given** `/map/robots.txt`, **When** fetched, **Then** it returns 200 with `text/plain` and disallows `buildings.pmtiles`, `trees.pmtiles`, and `buildings.geojson` for all user agents, including GPTBot, ClaudeBot, PerplexityBot, and CCBot.
2. **Given** `/map/sitemap.xml`, **When** fetched, **Then** it returns 200 with XML content type and lists exactly the three canonical URLs (`/map/`, `/map/impressum`, `/map/attribution`).
3. **Given** the sitemap, **When** parsed, **Then** no data file and no hashed asset appears in it.
4. **Given** the assessment report, **When** reviewed, **Then** the root-domain `robots.txt` coordination (blog origin `Sitemap:` line and AI-bot rules) is documented with the exact lines the owner must add.

### User Story 4 - Nothing Regresses (Priority: P2)

The maintainer ships the SEO work knowing the map experience is byte-for-byte the same, every gate passes, and performance budgets hold.

**Why priority**: Every prior feature locked behavior (values, colors, labels, popups, caching) and budgets; SEO work must not silently break any of it.

**Independent Test**: Run the full pytest suite, all governance gates (`make check-public`, layout/OR-005 gates, commit checks), the interaction-latency harness, and a visual parity comparison of the published map.

**Acceptance Scenarios**:
1. **Given** the changed tree, **When** the full test suite runs, **Then** every existing test passes.
2. **Given** the changed tree, **When** governance gates run, **Then** `check-public`, the layout gate, and commit checks all pass; no new large file is tracked (OR-005 stays green).
3. **Given** the published site, **When** the interaction-latency harness runs, **Then** all 8 interactions stay within 2 s and the desktop median stays ≤ 123 ms.
4. **Given** the published map, **When** compared to the previous bundle, **Then** building values, colors, labels, popups, and interactions are identical.
5. **Given** the changed bundle, **When** security headers are checked on the new files (`robots.txt`, `sitemap.xml`, preview image), **Then** they carry the same security headers as all other Worker responses.

### User Story 5 - The Assessment Is Reproducible and Committed (Priority: P2)

Anyone — including the maintainer in six months — can read one committed report and learn what the SEO state was, what was changed, why, and how to re-verify it.

**Why priority**: The user asked for an *assessed* improvement, not a blind change. A committed report with before/after evidence makes the work auditable and repeatable.

**Independent Test**: Open the committed assessment report and reproduce each claim by re-running the documented checks (fetch page, inspect head, validate sitemap, validate structured data).

**Acceptance Scenarios**:
1. **Given** the assessment report, **When** reviewed, **Then** it documents the current state with evidence, each finding with severity and disposition (fixed / documented / owner-side), and the research sources used.
2. **Given** the report's verification section, **When** each listed check is re-run, **Then** the stated result reproduces.
3. **Given** the post-change site, **When** verified via search-engine property tools (Search Console/Bing), **Then** the properties are verified server-side without adding client-side tracking.

### Edge Cases

- **JSON-LD vs. strict CSP**: the page's CSP is locked (feature 015). Structured data must not be blocked or alter the CSP; verification must show the page loads and validators pass with the existing CSP.
- **Hidden vs. visible copy duplication**: resolved (Clarifications 2026-08-09, final) — single source. The story text exists in EXACTLY one DOM location: inside the first-visit story modal (feature 007 restored with full text). There is no visible section under the map.
- **Sitemap staleness**: a hand-written `lastmod` goes stale between publishes. Either omit `lastmod` or generate it from the publish timestamp; never claim a date that is not true.
- **Robots.txt scope limits**: crawlers only honor `/robots.txt` at the domain root, which belongs to the blog origin. The map-path file is informational and for direct submission; the authoritative root file requires owner coordination (documented, not deployed here). Cloudflare caches `robots.txt` by default (120-min edge TTL) — the owner-side root edit must be followed by a cache purge or bypass rule, and the plan must account for the same if the map-path file ever needs a fast change.
- **HTTP→HTTPS scheme redirect**: requests to the canonical URL form over plain HTTP (`http://abu-hamad.de/map/`, `/map/impressum`, `/map/attribution`, `/map/robots.txt`, `/map/sitemap.xml`, `/map/og-image.png`) were served 200 by the worker (no scheme check; zone-level Always Use HTTPS not enabled) — duplicate-content risk (Clarifications 2026-08-09). Fixed by a worker-level `http:` → `https://` 301; any future request that reaches the worker over HTTP is a regression.
- **Preview image freshness**: the `og:image` must reflect the current map (colors, data version). If the map rendering changes, the preview image must be regenerated; a mismatch is a correctness bug.
- **First-visit story modal (feature 007)**: restored (Clarifications 2026-08-09, final). The modal shows over the map without scrolling and holds the full story text (story, links, Methode, Datenquellen, Genauigkeit); it is the single DOM copy. Dismissal (close button / Escape) persists; modal links open in new tabs. Its smoke test (smoke_us5.md) covers the interaction.
- **AI-bot policy side effects**: disallowing AI bots may reduce AI-assistant citations of the page; this is an explicit owner-visible tradeoff recorded in the report (the default is to disallow the data files for all bots, not to block the HTML pages).
- **Non-JS crawlers and the map**: crawlers that cannot execute JavaScript see no map. The visible text section is the page's content for them; it must be self-contained and not reference "the map above" as the only explanation.
- **Hashtag/hash interplay**: new files (`robots.txt`, `sitemap.xml`, preview image) must not be content-hashed like `main.js`/`style.css` (feature 014), or their URLs break; the hashed-bundle contract is unchanged.
- **Search Console without analytics**: verification must not require client-side tags (FR-001). DNS or file-based verification is the mechanism; any analytics addition is out of scope.

## Requirements

### Functional Requirements

- **FR-001**: A committed SEO assessment report MUST document: current state with evidence, findings with severity and disposition, the scoped research and its sources, and reproducible before/after verification steps.
- **FR-002**: The map page MUST have a descriptive, unique title of 30–60 characters and a meta description of 100–160 characters, written in German, covering what the map shows and where.
- **FR-003**: The `impressum` and `attribution` pages MUST each have a unique meta description; their existing descriptive titles MUST be kept.
- **FR-004**: Every page MUST have a canonical link tag pointing to its single canonical URL (`https://abu-hamad.de/map/`, `/map/impressum`, `/map/attribution`). (The literal `/map/index.html` path already 307-redirects away — research.md D1 — so the canonical tag is the standard signal, not a duplicate fix.)
- **FR-005**: The map page MUST carry the full Open Graph set (`og:title`, `og:description`, `og:type`, `og:url`, `og:site_name`, `og:locale=de_DE`, `og:image`, declared `og:image:width/height`) and `twitter:card=summary_large_image` (required; no OG fallback) with an `og:image` of 1200×630 (1.91:1) in PNG or JPG format (WebP is inconsistently decoded by scrapers — research D4), served from the map path, returning 200, under 1 MB, and visually matching the current map.
- **FR-006**: the primary informative content (story, method, data sources, accuracy disclaimer) MUST exist in exactly one DOM location: the first-visit story modal (feature 007 content restored, Clarifications 2026-08-09 final). The modal shows over the map without scrolling. No duplicate story text anywhere (no visible section under the map). [Owner decision 2026-08-09: the earlier 'visible in initial HTML / ≥ 80 % outside hidden containers' requirement is DROPPED; the map page contains only the map and the modal.]
- **FR-007**: The map page MUST include valid JSON-LD structured data of type WebSite (name, url, alternateName; no SearchAction — sitelinks search box is gone) and Organization, aligned with content visible on the page, passing the Rich Results Test with zero errors. A Dataset record MAY be added for dataset discovery (it feeds Dataset Search, not Google Search rich results — research D3). FAQPage, LocalBusiness, and Speakable markup MUST NOT be added (research D3).
- **FR-008**: `/map/robots.txt` MUST be served with 200 and `text/plain`, disallowing the three data files (`buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson`) for all user agents, and MUST NOT block the HTML pages. AI-bot policy is already enforced at the zone root (research.md D1/D5) and MUST be documented as such, not duplicated.
- **FR-009**: `/map/sitemap.xml` MUST be served with 200 and XML content type, listing exactly the three canonical URLs, and MUST NOT list data files, hashed assets, or the preview image.
- **FR-010**: Root-domain coordination MUST be documented in the assessment report: the exact `Sitemap:` line for the blog origin's `robots.txt` (AI-bot rules already exist there — research.md D1), plus the optional data-file disallows, marked as owner-side actions not deployed by this repo.
- **FR-011**: Search-engine property verification (Search Console, Bing Webmaster) MUST be server-side (DNS or file-based) and MUST NOT add client-side tracking or analytics.
- **FR-012**: All existing behavior MUST remain unchanged: map values, colors, labels, popups, interactions, caching semantics, security headers, and the hashed-bundle contract (feature 014).
- **FR-013**: All existing tests and gates MUST pass after the change: pytest suites, `check-public`, layout/OR-005 gates, commit checks, CWV interaction budgets, and deploy verification.

### Key Entities

- **SEO assessment report**: committed document recording current-state evidence, findings (severity, disposition), research summary with sources, and reproducible verification steps.
- **Canonical URL map**: the three pages and their single canonical URLs; the basis for canonical tags, the sitemap, and duplicate-content checks.
- **Crawler-facing files**: `robots.txt` (bot policy incl. AI bots, data-file disallows) and `sitemap.xml` (canonical page inventory); served from the map path, security-header-protected.
- **Link-preview metadata**: Open Graph + Twitter Card fields and the 1200×630 preview image; the first impression for every shared link.
- **Structured data records**: WebSite and Dataset JSON-LD describing the page and the underlying data (subject, coverage, license, sources) — aligned with visible content only.
- **Visible content section**: the crawlable German text (story, method, sources, disclaimer) that is the page's content for search engines and non-JS crawlers.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Assessment report committed, documenting current state with evidence, every finding with severity and disposition, and research sources; each listed verification check reproduces.
- **SC-002**: Every page resolves to exactly one indexable URL: the canonical tag matches the canonical URL, `/map/` and `/map/index.html` do not present as duplicate content (the literal path already 307-redirects — research.md D1), and `www`/no-trailing-slash/plain-HTTP variants 301 to the `https://` canonical (worker scheme redirect, Clarifications 2026-08-09).
- **SC-003**: Map page has a title of 30–60 characters and a meta description of 100–160 characters; all three pages have unique metadata; no page has the bare title "Baumfläche".
- **SC-004**: Superseded by owner decision (Clarifications 2026-08-09, final): the story text lives in the hidden first-visit modal (single DOM copy), not in visible page content. No ≥ 80 % visible-word criterion applies.
- **SC-005**: Link previews on at least 3 of Facebook/LinkedIn/X/WhatsApp/Telegram/Discord/Slack show title, description, and image; `og:image` is 1200×630, returns 200, under 1 MB.
- **SC-006**: `/map/robots.txt` and `/map/sitemap.xml` return 200 with correct content types; the sitemap lists exactly 3 URLs; no data file or hashed asset appears in it; the data files are disallowed for all user agents; the zone-level AI-bot policy is documented in the assessment report (research.md D1/D5).
- **SC-007**: JSON-LD passes the Rich Results Test with zero errors; only content visible on the page is marked up.
- **SC-008**: Zero regressions: full test suite and all gates pass; all 8 interactions ≤ 2 s; desktop interaction median ≤ 123 ms; map values, colors, labels, popups identical to the current bundle.
- **SC-009**: Search-engine properties verified server-side with zero client-side tracking added (FR-001 preserved).
- **SC-010**: Superseded by owner decision (Clarifications 2026-08-09, final): the story text is no longer visible in the initial HTML. Non-JS crawlers receive the metadata, JSON-LD, and the modal's story text in the raw HTML (indexable, contextually hidden); the visible-content self-sufficiency criterion is dropped.

## Assumptions

- The domain-root `robots.txt` belongs to the blog origin (E-004) and already enforces the AI-bot split policy via Cloudflare Managed Content (verified 2026-08-09, research.md D1); this repo ships the map-path files and documents the remaining root-level addition (the `Sitemap:` line, optionally the data-file disallows) as owner-side actions.
- German is the only content language; no `hreflang` or multi-language work is needed.
- No client-side tracking may be added (FR-001); verification and measurement are server-side only.
- The `og:image` is generated from the current map rendering (the repo already has rendering/parity tooling) as a static image, not a dynamic endpoint.
- The map canvas is not indexable content; this feature improves the page's text and metadata, not the map's indexability.
- Core Web Vitals budgets from feature 014 remain authoritative; SEO changes must not regress them.
- The three data files contain no HTML content, so disallowing them in `robots.txt` loses no indexing value.
- Search-engine crawling of the site is currently unverified (no properties set up); the assessment's baseline is the fetched raw state, not historical analytics.
