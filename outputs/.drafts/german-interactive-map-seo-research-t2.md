# Researcher Brief T2 — Schema.org structured data + Open Graph / Twitter Card previews

**Status:** All 7 questions covered. Research date: 2026-08-09. Notes only — not the final report.
**Site context:** German-language static site (static HTML, client-side rendered interactive tree-canopy map, Cloudflare).

---

## Evidence table

| # | Source | URL | Key claim | Type | Confidence |
|---|--------|-----|-----------|------|------------|
| 1 | Google — Farewell, Sitelinks Search Box (blog, 2024-10-21) | https://developers.google.com/search/blog/2024/10/sitelinks-search-box | Sitelinks search box removed globally from Nov 21, 2024; RRT no longer highlights it; SC report removed; markup harmless to keep; site names still use a WebSite variation | primary | high |
| 2 | Google — Site names in Google Search (docs, last updated 2025-12-10) | https://developers.google.com/search/docs/appearance/site-names | WebSite structured data (name+url required, alternateName recommended, homepage only) is the most important signal for site names; site names NOT supported in Rich Results Test | primary | high |
| 3 | Google — Dataset structured data (docs, last updated 2025-12-10) | https://developers.google.com/search/docs/appearance/structured-data/dataset | Dataset markup is consumed by Dataset Search (toolbox.google.com/datasetsearch), not Google Search; required: name, description (50–5000 chars); recommended: creator, license, sameAs, identifier, distribution | primary | high |
| 4 | Google — Search Central "What's new" changelog (Nov 5, 2025; May 8 + June 15, 2026 entries) | https://developers.google.com/search/updates | Nov 5, 2025: "Dataset structured data is only used by Dataset Search, and not Google Search"; May 8, 2026: FAQ rich results deprecated (stopped appearing May 7, 2026); June 15, 2026: FAQ docs removed; Jan 22, 2025: breadcrumbs now desktop-only | primary | high |
| 5 | Google — Changes to HowTo and FAQ rich results (blog, 2023-08-08) | https://developers.google.com/search/blog/2023/08/howto-faq-changes | Aug 2023: FAQ rich results restricted to "well-known, authoritative government and health websites" | primary | high |
| 6 | Google — Breadcrumb (BreadcrumbList) docs | https://developers.google.com/search/docs/appearance/structured-data/breadcrumb | BreadcrumbList still supported; ≥2 ListItems; item/name/position | primary | high |
| 7 | Google — Organization structured data (docs) | https://developers.google.com/search/docs/appearance/structured-data/organization | No required properties; influences knowledge panel + logo (min 112×112); use most specific subtype (e.g., LocalBusiness) | primary | high |
| 8 | Google — Local business (LocalBusiness) docs | https://developers.google.com/search/docs/appearance/structured-data/local-business | LocalBusiness → knowledge panel in Search/Maps; required: address, name; recommended: geo, openingHoursSpecification, telephone, url | primary | high |
| 9 | Google — Speakable structured data (BETA) | https://developers.google.com/search/docs/appearance/structured-data/speakable | Speakable is news-oriented (Google Assistant TTS), US/English only; not for general sites | primary | high |
| 10 | Google — Structured data markup that Google Search supports (gallery) | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | Article, LocalBusiness, Organization, Speakable listed; FAQPage no longer in gallery | primary | high |
| 11 | Google — Intro to structured data | https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data | JSON-LD recommended (easiest to maintain); JSON-LD/Microdata/RDFa all equally fine; JSON-LD in head or body; don't hide structured data from users | primary | high |
| 12 | Google — Schema Markup Testing Tool overview | https://developers.google.com/search/docs/appearance/structured-data | RRT for Google rich-result eligibility; Schema Markup Validator (validator.schema.org) for generic schema.org validation | primary | high |
| 13 | Google Search Console Help — Rich Results Test | https://support.google.com/webmasters/answer/7445569 | RRT still the official validation tool; supports JSON-LD, RDFa, Microdata | primary | high |
| 14 | Google — Here's an update on our efforts to simplify the search results page (2025-11-05) | https://developers.google.com/search/blog/2025/11/update-on-our-efforts | Google phasing out underused structured-data features; not the end of rich results | primary | high |
| 15 | ogp.me — Open Graph protocol spec | https://ogp.me/ | 4 required: og:title, og:type, og:image, og:url; optional: og:description, og:locale (default en_US), og:site_name, og:image:width/height/alt/type/secure_url | primary | high |
| 16 | Facebook — Sharing Best Practices | https://developers.facebook.com/docs/sharing/best-practices/ | og:image ≥1080px width recommended, min 600px; declare og:image:width/height | primary | high |
| 17 | Cloudflare — Email Address Obfuscation docs | https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/ | Enabled by default; injects email-decode.min.js (defer); emails NOT obfuscated in `<head>`, in attributes except `href` of `<a>` | primary | high |
| 18 | Cloudflare — Bot Fight Mode docs | https://developers.cloudflare.com/bots/get-started/bot-fight-mode/ | Bot Fight Mode cannot be bypassed via WAF rules/Skip; Super Bot Fight Mode supports Skip rules | primary | high |
| 19 | Cloudflare — /cdn-cgi/ endpoint docs | https://developers.cloudflare.com/fundamentals/reference/cdn-cgi-endpoint/ | /cdn-cgi/ endpoints (email-protection, challenge-platform, image) can cause crawler errors; recommend robots.txt `Disallow: /cdn-cgi/` (with Allow for /cdn-cgi/image/ if used) | primary | high |
| 20 | Cloudflare — vercel/og Pages plugin docs | https://developers.cloudflare.com/pages/functions/plugins/vercel-og/ | Official Cloudflare Pages plugin for dynamic OG images (Satori-based, 1200×630 default) | primary | high |
| 21 | kvnang/workers-og (GitHub) | https://github.com/kvnang/workers-og | workers-og: Satori-based OG image generator for Cloudflare Workers (HTML input via HTMLRewriter) | primary (code) | medium |
| 22 | Cloudflare Community — og:image:secure_url won't load (user report) | https://community.cloudflare.com/t/ogsecure-url-wont-load-an-image/297144 | User report: og:image fails in iMessage when Super Bot Fight Mode set to BLOCK; works when ALLOW | secondary (user report) | medium |
| 23 | Cloudflare Community — No preview image in Facebook/WhatsApp, Facebook bot blocked (user report) | https://community.cloudflare.com/t/no-preview-image-in-facebook-or-whatsapp-facebook-bot-blocked/708866 | User report: FB bot 403 in Sharing Debugger due to Cloudflare blocking; caching also delays updated previews | secondary (user report) | medium |
| 24 | SEJ — Google Drops FAQ Rich Results From Search | https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/ | FAQ rich results gone from Search (May 7, 2026); RRT support dropped June 2026; SC API Aug 2026 | secondary | high |
| 25 | link.boo — X (Twitter) link card not showing — 2026 fix | https://link.boo/guides/x-link-card-not-showing | Card Validator preview removed mid-2022, no replacement; use Tweet Composer; twitter:* tags unchanged (not x:*); twitter:card has no OG fallback; X falls back to og:* for other fields; ~7-day cache | secondary | medium |
| 26 | Stack Overflow — Twitter card images no longer generating (quoting Twitter dev community) | https://stackoverflow.com/questions/72889599/twitter-card-images-no-longer-generating-properly-from-wordpress-site-links | Official confirmation: Card Validator preview removed mid-2022; preview by pasting URL into Tweet composer | secondary | high |
| 27 | GoogleWatchBlog (DE) — Google entfernt die Suchleiste (2024-10-22) | https://www.googlewatchblog.de/2024/10/websuche-google-entfernt-die-suchleiste-aus-den-suchergebnissen-sitelinks-verliert-praktische-funktion/ | German coverage of sitelinks search box removal Nov 21, 2024 | secondary (DE) | high |
| 28 | metayer.de (DE) — SEO Suchfeld (searchaction) VERALTET | https://www.metayer.de/blog/seo/suchfeld-schema/ | German blog: SearchAction schema outdated since Nov 2024; claims Bing offers no schema support (unverified claim) | secondary (DE) | low-medium |
| 29 | ki-q.de (DE) — Google Structured Data Cleanup: Was jetzt wegfällt | https://ki-q.de/blog/news/google-structured-data-cleanup-2026/ | German summary: practice problem deprecated Jan 2026; Dataset = Dataset Search only; RRT support changes | secondary (DE) | medium |
| 30 | Jilles Soeters — Open Graph Images in Astro: Build-Time vs Runtime | https://jilles.me/og-images-astro-build-vs-runtime/ | OG image generation: build-time (Satori+resvg in CI) vs runtime Worker; PNG for compatibility; caching headers | secondary | medium |
| 31 | seotest.app — OG Image Size: 1200×630 (2026) | https://seotest.app/blog/og-image-size-format-best-practices | 1200×630 (1.91:1), <1 MB target, JPG/PNG (WebP unreliable), absolute HTTPS URL, og:image:width/height avoid first-scrape blank card | secondary | medium |
| 32 | ThatDevPro — Twitter Cards: canonical reference | https://www.thatdevpro.com/reference/html-twitter-cards/ | twitter:card summary_large_image; image specs 1200×628 / min 300×157, 5 MB; validator deprecated 2022; X cache ~7 days | secondary | medium |
| 33 | Vercel — satori (GitHub) | https://github.com/vercel/satori | Satori: HTML/CSS→SVG, used by @vercel/og and workers-og | primary (code) | high |
| 34 | X Developer Platform portal | https://developer.x.com/ | Fetch of cards docs URLs (developer.x.com/en/docs/x-for-websites/cards/…) redirects to portal — cards docs not directly retrievable | primary (blocked) | n/a |

---

## Key findings per question

### 1. WebSite / sitelinks search box — deprecated, but WebSite type still worth shipping
- Google removed the **sitelinks search box** globally on **Nov 21, 2024**; it no longer highlights the markup in the Rich Results Test and removed the Search Console report [1][27]. Keeping `SearchAction` markup is harmless but produces nothing in Google Search [1]. (Claim in German blog that Bing offers no SearchAction support is unverified [28] — treat as low confidence.)
- `WebSite` structured data **still matters**: it is the primary signal for the **site names** feature (`name` + `url` required, `alternateName` recommended; homepage only; not validated by RRT) [1][2]. No 2025–2026 changes beyond this; docs last updated 2025-12-10 [2].
- Bonus: Google uses `og:title` as a title-link source and `og:image` as a thumbnail source in Search/Discover (changelog Aug 2024 + March 2026) [4].
- **Verdict:** Add `WebSite` JSON-LD (name, url, alternateName, inLanguage "de-DE") on the homepage. Skip `SearchAction` unless the site has a real search endpoint and you want non-Google consumers; it is not a Google rich result anymore [1][14].

### 2. Dataset — no rich result; only Dataset Search
- Google clarified (Nov 5, 2025): **Dataset structured data is only used by Dataset Search, not Google Search** [4][14][29]. Dataset markup still feeds `toolbox.google.com/datasetsearch`; docs remain live (updated 2025-12-10) [3]. Required: `name`, `description` (50–5000 chars); recommended: `creator`, `license`, `sameAs`, `identifier`, `distribution`, `spatialCoverage` [3].
- **Verdict:** Optional. Only worthwhile if the site publishes downloadable data it wants discoverable in Dataset Search; it yields no Google SERP rich result [3][4].

### 3. Other types — what is realistic in 2026
- **Organization:** no required properties; used behind the scenes and for logo/knowledge-panel display (logo min 112×112 px, crawlable) [7]. Recommended on homepage.
- **LocalBusiness:** still yields knowledge-panel display in Search/Maps; requires `address` + `name`; use the most specific subtype; relevant only if the site operator is a service-area business in German cities — otherwise skip [8]. (Note: Google's local prominence depends on Business Profile claim; markup alone is not a local ranking lever [8].)
- **Speakable:** BETA, news-oriented (Google Assistant TTS), effectively English/US — **not relevant** for this site [9].
- **FAQ:** **dead.** Aug 2023 → restricted to authoritative gov/health [5]; **May 7, 2026** → no longer shown at all; FAQ docs removed June 15, 2026; RRT support dropped June 2026, SC API Aug 2026 [4][24]. Markup is harmless but has zero Google effect.
- **BreadcrumbList:** still supported; since **Jan 2025 breadcrumbs appear on desktop only** [4][6]. Requires ≥2 `ListItem`s [6].
- **Article:** still supported for news/blog content [10]; for map/neighborhood pages prefer plain `WebPage` [11].

### 4. JSON-LD vs microdata; validation status
- Google recommends **JSON-LD** (easiest to implement/maintain); all three formats are equally fine; JSON-LD may go in `<head>` or `<body>` and is readable even when injected by JS — but for a static site, ship it in the initial HTML [11].
- **Rich Results Test is NOT retired.** It remains Google's official eligibility checker (still referenced in current docs; German version live) [12][13]. What changed: deprecated types (sitelinks search box, FAQ, practice problem, etc.) were removed from it [1][4][24]. For generic schema.org validation use the **Schema Markup Validator** (validator.schema.org); site names are only testable there [2][12]. German-language search confirms no "RRT eingestellt" — only per-feature support removal [29].

### 5. Open Graph
- ogp.me spec: required `og:title`, `og:type`, `og:image`, `og:url`; optional `og:description`, `og:site_name`, **`og:locale` (default en_US → set `de_DE`)**, `og:image:width/height/alt/type/secure_url` [15].
- Image: **1200×630 px (1.91:1)**, <1 MB target, **JPG/PNG** (WebP inconsistently decoded by scrapers), absolute HTTPS URL, publicly fetchable; declare `og:image:width`/`height` so the full card renders on the first scrape [16][31]. Facebook min 600×315, recommends ≥1080 px width [16].
- **Dynamic OG images on static hosting:** Satori (HTML/JSX → SVG) + resvg (SVG → PNG) [33]. Cloudflare options: official **vercel-og Pages plugin** (middleware that auto-injects og:image) [20] or **workers-og** for Workers [21]. For a static site, build-time generation during CI is also viable (one PNG per page in `dist/`), producing 1200×630 PNGs [30].

### 6. X / Twitter cards
- Tag names are still **`twitter:*`, not `x:*`** [25]. **`twitter:card` is required** — it has no Open Graph fallback; other fields fall back to `og:*` [25][32]. Use `summary_large_image`; image ≥300×157, ~1200×628, ≤5 MB [32].
- The official **Card Validator preview was removed mid-2022**; no replacement. Preview by pasting the URL into **Tweet Composer**; cache ~7 days, no public purge (workarounds: cache-bust query param, repost) [25][26][32].
- Official X cards docs: the `developer.x.com/en/docs/x-for-websites/cards/…` URLs redirect to the developer portal (verified by fetch) — mark official spec page as **blocked/relocated** [34].

### 7. Cloudflare compatibility
- **Email obfuscation** (on by default) rewrites visible emails to `/cdn-cgi/l/email-protection` links; the decode script is now deferred; emails inside `<head>` and inside attributes (except `<a href>`) are **not** obfuscated — so JSON-LD contact info in the head is safe; the rewritten links 404 to crawlers (soft-404 noise) [17][19].
- **Bot Fight Mode** cannot be bypassed with WAF rules/Skip; **Super Bot Fight Mode** supports Skip rules [18]. Community reports link social preview failures (iMessage og:image, Facebook Sharing Debugger 403) to blocked/challenged bots [22][23] — ensure social crawlers aren't challenged/blocked.
- **/cdn-cgi/ endpoints:** recommended `robots.txt` `Disallow: /cdn-cgi/` (+ `Allow: /cdn-cgi/image/` if Images is used) [19].
- OG image generation on Cloudflare is officially supported (vercel-og plugin / workers-og) [20][21].

---

## Recommended markup recipe (what to add)

1. **Homepage JSON-LD (in static HTML head, one WebSite + one Organization block):**
   - `WebSite`: `@id` `#website`, `name`, `url`, `alternateName`, `inLanguage: "de-DE"`, `publisher: {"@id": "#organization"}`. No `SearchAction` (no Google value; only add if internal search exists, for non-Google consumers).
   - `Organization`: `@id` `#organization`, `name`, `url`, `logo` (≥112×112, crawlable), `sameAs`, optional `contactPoint` (emails safe in head per Cloudflare docs [17]).
2. **City/neighborhood pages:** `WebPage` (+ `isPartOf` → `#website`) and `BreadcrumbList` with ≥2 `ListItem`s (desktop-only result) [4][6].
3. **Dataset:** only if downloadable data is published — for Dataset Search discovery, not rich results [3].
4. **LocalBusiness:** only if the operator is a service-area business (name, address, geo, areaServed, openingHours) [8].
5. **Skip:** `FAQPage` (dead since May 2026) [4], `Speakable` (news/EN) [9], sitelinks `SearchAction` (deprecated) [1].
6. **Open Graph (every page):** `og:title`, `og:type=website`, `og:url`, `og:image` (1200×630 JPG/PNG, absolute HTTPS, <1 MB), `og:image:width`/`height`, `og:description`, `og:site_name`, `og:locale=de_DE` [15][31].
7. **Twitter:** `twitter:card=summary_large_image` + `twitter:image` (mirror og:image); all other fields rely on og:* fallback [25][32].
8. **OG images:** build-time generation (Satori+resvg in CI) or Cloudflare Worker at `/og/<slug>.png`; serve PNG [20][30][33].
9. **Cloudflare hygiene:** allow/never-block social crawlers (Super Bot Fight Mode Skip rules); keep email obfuscation scoped or off; `Disallow: /cdn-cgi/` in robots.txt (with Allow for images if used) [17][18][19].
10. **Validation:** Rich Results Test (eligibility) + Schema Markup Validator (generic validity) after deploy; monitor SC rich-results status report [12][13].

---

## Search queries used
1. "Google sitelinks searchbox schema.org WebSite structured data documentation 2025"
2. "Google dataset rich results deprecated 2023 2024 Dataset schema.org current status"
3. "Rich Results Test retired 2025 Google Search Console change"
4. "Open Graph image size recommendations 2026 og:image best practices"
5. "Twitter card validator deprecated 2025 X card preview changes"
6. "FAQ rich results restricted government health sites Google 2023 current"
7. "Speakable structured data Google rich result news organizations documentation"
8. "Google breadcrumb rich result BreadcrumbList structured data documentation 2025"
9. "Google Organization structured data LocalBusiness documentation knowledge panel"
10. "Cloudflare bot fight mode social media crawlers og image blocked email obfuscation"
11. "dynamic OG image static site generation Satori Cloudflare Workers og-image 2025"
12. "Google JSON-LD best practices structured data placement head sitewide"
13. "Rich Results Test eingestellt Google 2025 Schema Validierung" (DE)
14. "Google Dataset Search eingestellt 2025 status Dataset Markup" (DE)
15. "X Twitter Card Validator ersatz 2026 Preview Tweet Composer" (DE)
16. "schema.org WebSite sitelinks searchbox entfernt November 2024 deutsch" (DE)

## URLs fetched directly
- https://developers.google.com/search/blog/2024/10/sitelinks-search-box
- https://developers.google.com/search/docs/appearance/structured-data/dataset
- https://developers.google.com/search/blog/2023/08/howto-faq-changes
- https://developers.google.com/search/updates
- https://developers.google.com/search/docs/appearance/site-names
- https://ogp.me/
- https://developer.x.com/en/docs/x-for-websites/cards/overview (+ /abouts/cards-markup) → redirects to portal
- https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/

## Blocked / unverified items
- **X official Cards spec page:** `developer.x.com/en/docs/x-for-websites/cards/…` redirects to the developer portal (blocked). Tag set and card types verified via secondary sources only [25][26][32].
- **Bing SearchAction support** (claimed in [28]): unverified, low confidence — do not rely on it.
- **Cloudflare bot-blocking → preview failures:** only user reports found [22][23]; no official Cloudflare doc states social crawlers are exempted from Bot Fight Mode.
- **German-language official Google docs** for structured data: not fetched (English docs verified directly); German secondary sources [27][29] agree with English primary sources.
- No PDFs were fetched (method requirement). All URLs above are HTML pages.
- Date-sensitive claims (FAQ removal June/Aug 2026 RRT/API timeline) come from Google changelog [4] + SEJ [24]; exact API cut-off date not re-verified on an official page.

## Coverage status
- Q1 WebSite/sitelinks: done (primary sources).
- Q2 Dataset: done (primary + changelog).
- Q3 Organization/LocalBusiness/Speakable/FAQ/Breadcrumb/Article: done (primary docs).
- Q4 JSON-LD vs microdata + RRT status: done (primary docs; German search confirms).
- Q5 Open Graph incl. dynamic images: done (ogp.me, FB best practices, Cloudflare plugin docs).
- Q6 Twitter cards: done, with official X docs marked blocked.
- Q7 Cloudflare: done (official docs + user reports marked secondary).
