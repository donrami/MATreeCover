# Research: SEO Assessment & Improvement (feature 016)

Phase 0 output. Augments the scoped research embedded in `spec.md` (R-001…R-009) with a deep-research pass (multi-agent, citation-tracked) plus direct verification against the live site. Every decision below resolves a spec question with rationale and evidence.

## Provenance

- **Deep-research brief** (4 parallel researcher agents → lead synthesis → verifier citation pass, 128 URLs reachability-checked on 2026-08-09): `outputs/.drafts/german-interactive-map-seo-cited.md` (41.6 KB). Researcher notes: `outputs/.drafts/german-interactive-map-seo-research-t1..t4.md`; pre-citation draft: `outputs/.drafts/german-interactive-map-seo-draft.md`. Plan: `outputs/.plans/german-interactive-map-seo.md`.
- **Reviewer pass**: the pipeline's reviewer step stalled (no output after 16 min) and the pipeline was stopped; the reviewer checklist was executed inline (below, "Reviewer pass notes") with spot-checks of every load-bearing claim against primary sources.
- **Live-site verification** (2026-08-09, direct HTTP checks): see D1.

## D1 — Live-site state (verified, not assumed)

Direct `curl` evidence on 2026-08-09, supersedes the spec's "no robots/sitemap" baseline with detail:

- `https://abu-hamad.de/map/` → 200, `text/html`, `cf-cache-status: HIT`, `cache-control: public, max-age=0, must-revalidate` (Workers static-asset caching; HTML is edge-cached with revalidation — no staleness risk for crawlers). All security headers present (CSP, HSTS, X-Frame-Options, Referrer-Policy, Permissions-Policy).
- `https://www.abu-hamad.de/map/` → 301 → apex; `https://abu-hamad.de/map` → 301 → `/map/`; `https://abu-hamad.de/map/index.html` → **307 → root** (Cloudflare Workers assets redirect the literal `index.html` path; **no duplicate-content path exists** — the spec's SC-002 concern via `/map/index.html` is already handled; canonical tag remains best practice as the standard signal).
- `<title>Baumfläche</title>` live; no meta description, no canonical tag, no OG/Twitter tags, no JSON-LD in the served HTML.
- `https://abu-hamad.de/map/robots.txt` → **404**; `/map/sitemap.xml` → **404** (as spec'd).
- **Root `robots.txt` (blog origin, zone level) already carries Cloudflare Managed Content**: `User-agent: *` + `Content-Signal: search=yes,ai-train=no,use=reference` (EU DSM Directive 2019/790 framing), and explicit disallows for `Amazonbot`, `Applebot-Extended`, `Bytespider`, `CCBot`, `ClaudeBot`, `CloudflareBrowserRenderingCrawler`, `Google-Extended`, `GPTBot`, `meta-externalagent`, `ia_archiver`. **The zone already implements the deep research's recommended AI-bot split policy (D5): training bots blocked, search/retrieval bots (Googlebot, OAI-SearchBot, PerplexityBot, Claude-SearchBot) not blocked.** No `Sitemap:` line present.
- `impressum` → 200; content already cites **"§ 5 DDG"** (Digitale-Dienste-Gesetz, in force 2024-05-14 — the TMG reference the deep research warns about is already fixed on this site). `attribution` → 200.

## D2 — Indexability: static text first, map as progressive enhancement (FR-006)

- **Decision**: the visible-content requirement (FR-006) is the single highest-value change. Evidence: Google's rendering pipeline (crawl → render → index) queues JS rendering and "not all bots can run JavaScript" (Google JS SEO basics, updated 2026-03-04); canvas/WebGL map output is pixels with no DOM text or links; Googlebot "doesn't interact with anything when it crawls" (SEJ, 2020). Bing renders JS (evergreen Edge since 2019) but its own guidance still recommends static/prerendered HTML. DuckDuckGo classic results are largely Bing-sourced; its own index is rolling out. AI crawlers (GPTBot etc. and AI search: OAI-SearchBot, PerplexityBot) are not documented to execute JS — raw-HTML text is the only guaranteed-readable content.
- **Rationale**: only Google and Bing are documented to render JS; static HTML is the intersection that serves every consumer including non-JS AI crawlers.
- **Alternatives considered**: SSR/prerendering the page (rejected for this feature — out of scope per spec; with static fallback content, prerendering is an optimization, not a correctness requirement); `<noscript>` duplicate (rejected — official guidance is old and mixed (2018–2019), not reliable as primary carrier); prerender.io/Browser Run (documented options; unnecessary while static text carries the content).
- **Spec interaction**: FR-006 and SC-004/SC-010 stand. The story/method/sources text must be visible initial HTML, not hidden.

## D3 — Structured data: WebSite + Organization primary; Dataset is for Dataset Search (FR-007)

- **Decision**: ship JSON-LD `WebSite` (name + url + alternateName; **no SearchAction** — sitelinks search box was removed 2024-11-21) and `Organization` (logo ≥ 112×112, crawlable). Add `Dataset` only because this site genuinely publishes data (`buildings.geojson` etc.) — **but verify scope**: Google states Dataset markup feeds **Dataset Search**, not Google Search rich results (official clarification; docs verified 2026-08-09: "easier to find in the Dataset Search tool"; required: name, description 50–5000 chars; recommended: creator, license, sameAs, identifier, distribution, spatialCoverage). Rich Results Test is still Google's validity checker (not retired); site names validate only in the Schema Markup Validator.
- **Do NOT add**: `FAQPage` (rich results dead — restricted 2023-08, removed from results 2026-05-07); `LocalBusiness` (this is an informational map, not a service-area business); `Speakable` (BETA, not relevant); `BreadcrumbList` (desktop-only since 2025-01; 3-page site gains nothing).
- **Format**: JSON-LD in the initial HTML head; CSP `script-src 'self'` does not block non-executed `application/ld+json` script elements (verify in browser as acceptance anyway).
- **Spec interaction**: FR-007 reworded — "WebSite and Dataset markup… valid per the Rich Results Test" → WebSite + Organization for Google Search appearance; Dataset for dataset discovery; all validated; visible-content alignment.

## D4 — Link previews: OG + Twitter full set, PNG/JPG image (FR-005)

- **Decision**: full Open Graph set: `og:title`, `og:type=website`, `og:url`, `og:image`, `og:description`, `og:site_name`, **`og:locale=de_DE`** (default is en_US), `og:image:width/height/alt`. Twitter: `twitter:card=summary_large_image` is **required and has no OG fallback**; other fields fall back to `og:*`.
- **Image**: 1200×630 (1.91:1), **PNG or JPG** (WebP is inconsistently decoded by scrapers), absolute HTTPS URL, `< 1 MB`, declared dimensions (renders on first scrape). Facebook min 600×315. Static, build-time generated from the current map render (repo already has rendering/parity tooling); regenerate whenever the map changes (spec edge case).
- **Verification**: the old Twitter Card Validator was removed (2022) — test by pasting into Tweet Composer (card cache ~7 days); WhatsApp/Telegram/Discord/LinkedIn read OG directly.
- **Cloudflare caveats**: email obfuscation rewrites visible emails to `/cdn-cgi/l/email-protection` links (soft-404s for crawlers) — keep contact emails out of visible body text or exempt; Bot Fight Mode can challenge social scrapers — social crawlers must not be challenged (zone setting; owner-side, documented).

## D5 — AI-crawler policy: already handled at the zone (FR-008)

- **Decision**: the zone root `robots.txt` (verified D1) already implements the recommended split policy — training bots (`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `Applebot-Extended`, `Meta-ExternalAgent`, `Bytespider`, `Amazonbot`) blocked; search/retrieval bots (`OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot`, `Googlebot`) allowed, plus `Content-Signal: search=yes,ai-train=no,use=reference`. **No AI-bot work is needed in this feature** beyond documenting the existing posture in the assessment report.
- **Rationale**: split policy is the vendor-doc-backed consensus: blocking training crawlers does not affect Google/Bing rankings (Google-Extended only controls Gemini training/grounding, not Search or AI Overviews); blocking search bots removes the page from AI-search answers.
- **Caveats to record**: robots.txt is preference not enforcement (RFC 9309; Google enforces 500 KiB cap); Perplexity has a documented stealth-crawling incident (2025-08, Cloudflare de-listed it); Bytespider compliance widely doubted; user-triggered bots (ChatGPT-User, Perplexity-User) may ignore robots.txt by design.
- **Spec interaction**: FR-008 narrows to the map-path file: disallow the three data files for `*` (general crawlers have `Allow: /` today — pmtiles/geojson contain no HTML and waste crawl budget), keep the HTML pages allowed. Coordination item in FR-010 changes from "AI-bot rules" to just the `Sitemap:` line + optional data-file disallows at root.

## D6 — robots.txt/sitemap mechanics (FR-008/009)

- **Map-path robots.txt**: crawlers only read `/robots.txt` at the host root (blog origin), so the map-path file is informational + for direct submission; the authoritative disallow lives at the root. Cloudflare **caches robots.txt by default** (120-min edge TTL when no cache-control) — robots.txt changes require a purge or bypass rule; sitemap `.xml` is **not** cached by default (fine).
- **Sitemap**: limits 50,000 URLs / 50 MB, gzip allowed; `Sitemap:` directive is top-level, absolute, not user-agent-scoped; supported by Google/Bing/CCBot; submission is "a hint, not a guarantee" — pair with Search Console submission (FR-011). Three URLs only; omit `<lastmod>` or generate from publish timestamp (staleness edge case).
- **HTML caching**: Cloudflare CDN does not cache HTML by default; this Worker's assets binding already edge-caches with revalidation (`cf-cache-status: HIT`, verified D1). CWV-wise: thresholds unchanged 2026 (LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 @ p75); INP replaced FID 2024-03-12; CWV is the only page-experience aspect Google documents as directly used in ranking, weight is small; TTFB is not a ranking factor (caching is a perf play). No action beyond keeping existing budgets (SC-008).

## D7 — E-E-A-T / YMYL (FR-006, FR-010)

- **Decision**: heat-protection content is health/safety-adjacent (YMYL-ish, raters' inference): strengthen trust signals via the visible text — author byline, method explanation, citations to official sources (DWD Hitzewarnung, LGL data license already attributed), accuracy disclaimer (feature 010), links to Impressum + Datenschutz. Impressum duty is § 5 DDG (since 2024-05-14) — **live page already compliant** (D1); it is a legal requirement and a trust signal, not a confirmed ranking factor.
- **Spec interaction**: FR-006's visible-content section explicitly includes author/method/sources/disclaimer (already spec'd); D7 confirms this is E-E-A-T-correct, no scope change.

## D8 — German local keywords (context, not scope)

- The deep research's keyword data targets heat-protection **services** (window films, blinds — commercial local-business intent). This site is an informational city map; the relevant query space is informational ("Mannheim Baumkarte", "Baumfläche Mannheim", "Hitzeschutz Mannheim Bäume"). Takeaways that apply: city+keyword combos are standard German practice; avoid thin doorway pages; seasonality — heat interest peaks in summer, content should be current before the season. **No keyword-targeting work is in scope** (spec Out Scope).

## Reviewer pass notes

Executed inline after the pipeline's reviewer step stalled (16 min, no output; pipeline stopped, no FATAL findings were pending). Spot-checks of load-bearing claims against primary sources, all PASS:

| Claim | Check | Result |
|-------|-------|--------|
| Dataset markup feeds Dataset Search, not Google Search rich results | developers.google.com/search/docs/appearance/structured-data/dataset (fetched 2026-08-09) | PASS — "easier to find in the Dataset Search tool"; JSON-LD preferred; RRT for validation |
| Cloudflare caches robots.txt by default, not HTML/JSON | developers.cloudflare.com/cache/concepts/default-cache-behavior/ (fetched 2026-08-09) | PASS — "The Cloudflare CDN does not cache HTML or JSON by default. Additionally, by default Cloudflare caches a website's robots.txt." Edge TTL 120 m for 200/206/301 without cache-control |
| CWV thresholds LCP 2.5 s / INP 200 ms / CLS 0.1 @ p75 | developers.google.com/search/docs/appearance/core-web-vitals + web.dev vitals (verified in scoped pass R-005) | PASS |
| Sitelinks search box removed 2024-11-21 | Google blog "Farewell, Sitelinks Search Box" (2024-10) | PASS |
| FAQ rich results ended 2026-05-07 | SEJ + Google changelog (2026) | PASS (secondary, consistent) |
| § 5 DDG since 2024-05-14 | gesetze-im-internet.de/ddg/__5.html; live impressum already cites § 5 DDG (D1) | PASS |
| og:image 1200×630 PNG/JPG < 1 MB, og:locale de_DE | ogp.me spec + Facebook sharing best practices (scoped pass R-008) | PASS |
| INP replaced FID 2024-03-12 | web.dev blog | PASS |

Known-weak evidence carried with labels (already in the brief's Caveats): QRG is PDF-only (YMYL claims via secondary quotes); DuckDuckGo own-index JS rendering (secondary); AI-crawler JS execution is an industry inference (no vendor statement); keyword volumes are third-party estimates; Bing guidelines full text client-rendered (snippets only). No FATAL or MAJOR issues found; the brief's own caveats section covers every blocked/unverified item.

## Open questions

| Question | Status |
|----------|--------|
| Do OAI-SearchBot / PerplexityBot execute JS? | No official docs — static HTML is the safe assumption (D2). |
| DuckDuckGo own-index share of traffic | Rolling out; unknown (D2). |
| CWV threshold changes | None documented as of 2026-08 (D6). |
| Impressum as ranking factor | No official statement; legal requirement + trust signal (D7). |
