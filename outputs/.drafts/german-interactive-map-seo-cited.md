# SEO Best Practices 2026 — German Interactive Map Website (Static HTML, Client-Side Rendering, Cloudflare)

- **Date:** 2026-08-09
- **Scope:** German-language static site (static HTML + client-side rendered interactive map, e.g., heat-protection/heat-warning content), hosted on Cloudflare, no analytics. This brief answers the 10 requested topic clusters with evidence, caveats, and open questions.
- **Status:** Cited & verified 2026-08-09. Every inline citation maps to the Sources section below; every source URL was reachability-checked on 2026-08-09 (see per-source notes).

---

## Executive Summary

1. **Ship all important text as static HTML in the initial response.** Google renders JS with evergreen Chromium and *can* index rendered content, but rendering is queued, can fail, and "not all bots can run JavaScript" [1][6]. Canvas/WebGL map tiles, marker popups, and fetch/XHR-only data are effectively invisible to crawlers [25][16]. The map should be progressive enhancement on top of static text (headings, descriptions, location lists with real `<a>` links).
2. **Google's official advice still favors server-side/pre-rendering** for speed and for non-JS bots [1]. If you prerender at all, Cloudflare's Browser Run Worker pattern or prerender.io are documented options [7][13]; with static fallback content, prerendering is an optimization, not a correctness requirement for Google.
3. **Schema.org: WebSite (site names) + Organization are worth shipping; Dataset only if you publish downloadable data** (it feeds Dataset Search, not Google Search rich results) [27][28][29]. FAQ rich results are dead (May 2026) [45]. Sitelinks search box was removed Nov 2024 [26]. Breadcrumbs are desktop-only since Jan 2025 [29].
4. **Open Graph: use the full required set incl. `og:locale=de_DE` and a 1200×630 PNG/JPG < 1 MB with declared dimensions** [39][40][130]. Twitter: `twitter:card` is still required (`summary_large_image`); the card type has no OG fallback [46][48]. The old Card Validator was removed in 2022 — test by pasting into Tweet Composer [47].
5. **AI crawlers: split policy — allow search/retrieval bots (OAI-SearchBot, PerplexityBot, Claude-SearchBot), block training bots (GPTBot, ClaudeBot, Google-Extended, CCBot, Applebot-Extended, Meta-ExternalAgent, Bytespider)** — unless you explicitly want your content in training sets [22][23][52][80][81]. Blocking AI training crawlers does not affect Google or Bing rankings [22][52][54]. Google-Extended only controls Gemini training/grounding, not Search or AI Overviews [12][54].
6. **robots.txt is preference, not enforcement** (RFC 9309, 500 KiB cap) [62][56]; noindex is not a robots.txt function [55]. Sitemap limits: 50,000 URLs / 50 MB per sitemap, gzip allowed [63]. Cloudflare caches robots.txt by default but **not** HTML or .xml by default — HTML caching needs a Cache Rule [65][66].
7. **Core Web Vitals thresholds are unchanged in 2026: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at the 75th percentile** [82][83]. INP replaced FID on March 12, 2024 [84]. CWV is the only page-experience aspect Google documents as directly used in ranking; weight is small ("not going to make your site's rankings jump up") [87][88][90]. HTML caching is not a ranking factor per se (Google doesn't use TTFB for ranking), but TTFB ≤ 0.8 s feeds LCP [91][92].
8. **Heat-protection content is health/safety-adjacent (YMYL): build E-E-A-T signals** — author bylines, About page, contact, citations to DWD/Umweltbundesamt [97][98][99][118]. **Impressum is now § 5 DDG** (Digitale-Dienste-Gesetz, since May 14, 2024 — citing TMG is outdated) [104][105][108]; it is a trust signal, not a confirmed ranking factor [109][110].
9. **Bing renders JS (evergreen Edge Chromium since 2019)** and historically recommends prerendering for JS-heavy sites [2][17]; **DuckDuckGo's classic results are largely Bing-sourced** [20], with its own index (with JS rendering) rolling out [21]. **AI search (AI Overviews, ChatGPT Search, Perplexity) largely consumes the standard index or fetches raw HTML** — static text is the safest path [6][12][22][24].
10. **German local SEO:** target patterns like "Hitzeschutzfolie Fenster", "Sonnenschutzfolie", "Hitzeschutz Fenster" + city combinations; heat-protection services (window films, blinds) are classic service-area businesses — Google Business Profile with service-area setup, NAP consistency, Bing Places [111][112][114][121][122][125]. Avoid thin doorway city pages [116]. Interest is seasonal (summer peak) — publish before the season [119][120].

---

## 1. Indexability of JS-rendered map content

### How Google handles JS in 2026
Google's current official guidance describes a three-phase pipeline — **crawl → render → index** — using an evergreen version of Chromium [1]. Rendering is queued: "The page may stay on this queue for a few seconds, but it can take longer than that"; Googlebot re-parses the rendered HTML for links and uses the rendered HTML for indexing [1]. The old "two-wave indexing" model is no longer how Google describes it [9][10].

Key consequences:
- JS-only text and links **are** indexable in principle, but only if rendering succeeds. If rendering fails, times out, or resources are blocked by robots.txt, JS-only content never reaches the index [1][5].
- Google explicitly warns: **"Google Search won't render JavaScript from blocked files or on blocked pages"** — never block your own JS/CSS in robots.txt [1][20].
- Google's recommendation remains: "server-side or pre-rendering is still a great idea because it makes your website faster for users and crawlers, and **not all bots can run JavaScript**" [1].
- The map site's map tiles, canvas/WebGL output, and content injected behind user interaction are **not indexable in practice**: canvas content is pixels without DOM text or links [25], and Googlebot "doesn't interact with anything when it crawls webpages" [16].

### Recommended architecture (evidence-based)
1. **Static HTML first**: H1/H2s, region/location descriptions, and a list of locations/regions as real `<a href>` links in the initial HTML. This is what Google indexes immediately, what Bing's prerender advice targets, and what non-JS AI crawlers can read [1][2][6][80].
2. **Map as progressive enhancement**: the interactive canvas/Leaflet/WebGL layer renders on top of that static content. Do not put primary text only inside the map.
3. **`<noscript>` is not a reliable content strategy.** Current Google JS SEO docs don't mention it; the last official statements are mixed and old (2018: Google "simply ignores or does not trust" noscript content for web text; 2019: Google does index noscript content) [14][15]. Treat it as a degraded fallback aid, never the primary carrier of important text. *(Dated evidence — flagged.)*
4. **Optional prerendering**: Cloudflare Browser Run (Worker + headless-Chrome binding, with caching recommended) [7] or prerender.io via a Cloudflare Worker [13] can serve rendered HTML to bots. With static fallback content this is a performance/extra-bot optimization, not required for Google.
5. **Keep the sitemap as the crawl entry-point list** — explicit URLs instead of relying on link discovery through JS [64].

## 2. Bing / DuckDuckGo / AI-search handling of JS content

- **Bing**: bingbot has used evergreen Microsoft Edge (Chromium) as its rendering engine since late 2019 [17][18]. Bing's own 2018 guidance says bingbot "is generally able to render JavaScript" but does not support all frameworks equally, and recommends serving prerendered static HTML to bingbot (explicitly noting this is not cloaking if done in good faith) [2]. Current Bing Webmaster Guidelines (2025 revision) emphasize crawl/discovery signals (sitemaps, IndexNow, lastmod) [11]. *(Full guidelines text could not be fetched — client-rendered page; verified via snippets. See Open Questions.)*
- **DuckDuckGo**: official help pages state traditional links/images results are "largely sourced from Bing" [20], so DDG classic results ≈ Bing's index and rendering. DDG is also building its own index with a reported two-pass JavaScript rendering pipeline (2026; secondary sources — podcast + trade press) [21].
- **Google AI Overviews / AI Mode**: officially, pages just need to be indexed and snippet-eligible in normal Google Search — "There are no additional technical requirements"; controls are `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex` [12]. So AI Overviews inherit Googlebot rendering. Google-Extended does **not** control AI Overviews; it only affects Gemini Apps/Vertex AI training and grounding [12][54].
- **ChatGPT Search (OpenAI)**: OAI-SearchBot "is used to surface websites in search results in ChatGPT's search features"; blocking it removes pages from ChatGPT search answers; GPTBot is training-only; ChatGPT-User is user-triggered and "robots.txt rules may not apply" [22]. ChatGPT Search also draws on third-party indexes, notably Bing (documented 2024 case: a site penalized in Bing disappeared from ChatGPT search) [24]. No OpenAI documentation states OAI-SearchBot executes JS — industry analyses infer AI crawlers mostly receive raw/unrendered HTML [6] *(inference)*.
- **Perplexity**: PerplexityBot indexes and cites pages (not used for training) and respects robots.txt; Perplexity-User ignores robots.txt "generally" [23]. Official docs are silent on JS execution [23].

**Bottom line:** only Google and Bing are documented to execute JS. Static HTML text is the only content guaranteed readable by every engine and AI crawler [1][2][6][80].

## 3. Schema.org structured data (WebSite, Dataset, and friends)

Verified 2026 state of Google-supported types relevant to this site:

| Type | Status in 2026 | Verdict |
|---|---|---|
| `WebSite` | Primary signal for **site names** in Search (name+url required, alternateName recommended, homepage only) [27]. **Sitelinks search box removed Nov 21, 2024** — SearchAction markup now produces nothing in Google [26]. | **Add** (no SearchAction). |
| `Dataset` | Only used by **Dataset Search**, not Google Search (official clarification Nov 5, 2025) [28][29]. Required: name, description (50–5000 chars); recommended: creator, license, sameAs, identifier, distribution, spatialCoverage [28]. | **Optional** — only if you publish downloadable data. |
| `Organization` | No required props; feeds logo/knowledge-panel display; logo ≥ 112×112 px and crawlable [32]. | **Add** on homepage. |
| `LocalBusiness` | Still supports knowledge-panel display in Search/Maps; requires name + address; use most specific subtype; only relevant if the operator is a service-area business (see §9) [33]. | Conditional. |
| `FAQPage` | **Dead**: restricted to authoritative gov/health sites Aug 2023; stopped showing May 7, 2026; docs removed June 2026 [30][38][45][29]. | **Skip** (harmless, zero effect). |
| `BreadcrumbList` | Still supported; **desktop-only since Jan 2025**; ≥ 2 ListItems [31][29]. | **Add** on subpages. |
| `Speakable` | BETA, news/English-oriented — not relevant [34]. | Skip. |
| `Article` | Still supported for blog/news content [35]. | Only for articles. |

- **Format:** JSON-LD is Google's recommendation (all formats equal; JSON-LD may live in head or body). For a static site, ship it in the initial HTML [36].
- **Validation:** the **Rich Results Test is not retired** — it remains Google's eligibility checker (deprecated types were simply removed from it); generic schema.org validity is checked with the Schema Markup Validator (validator.schema.org) [37][29]. Site names are only validated in the Schema Markup Validator, not RRT [27].

## 4. Open Graph / Twitter Card link previews

- **Open Graph (ogp.me spec):** required `og:title`, `og:type`, `og:image`, `og:url`; recommended `og:description`, `og:site_name`, `og:locale` (default en_US → set **`de_DE`**), `og:image:width`/`height`/`alt` [39].
- **Image:** 1200×630 px (1.91:1), < 1 MB target, **PNG/JPG** (WebP is inconsistently decoded by scrapers), absolute HTTPS URL; declare dimensions so the card renders on the first scrape [40][130]. Facebook: min 600×315, recommends ≥ 1080 px width [40].
- **Dynamic OG images on static hosting:** Satori (HTML/CSS → SVG) + resvg (SVG → PNG) [49]; Cloudflare offers the official **vercel-og Pages plugin** and the community **workers-og** for Workers [44][50]. Build-time generation in CI (one PNG per page) is the simplest static approach [44][49][50].
- **X/Twitter Cards:** tag names are still `twitter:*` (not `x:*`) [46]. **`twitter:card` is required and has no OG fallback**; other fields fall back to `og:*` [46][48]. Use `summary_large_image`; image ≈ 1200×628, ≥ 300×157, ≤ 5 MB [48]. The official Card Validator preview was removed in mid-2022 with no replacement — test by pasting the URL into Tweet Composer; the card cache is ~7 days [47][46]. *(Official X cards docs redirect to the developer portal — verified blocked.)*
- **Cloudflare compatibility:** email obfuscation (on by default) rewrites visible emails to `/cdn-cgi/l/email-protection` links (soft-404s for crawlers); emails in `<head>` and non-`href` attributes are not obfuscated — JSON-LD contact info in the head is safe [41]. Bot Fight Mode can block social scrapers (user reports of failed iMessage/Facebook previews); Super Bot Fight Mode supports Skip rules — make sure social crawlers are not challenged [42][43]. Recommended: `Disallow: /cdn-cgi/` in robots.txt (add `Allow: /cdn-cgi/image/` if you use Cloudflare Images) [43].

## 5. AI-crawler robots.txt policy

### Current crawler landscape (2026)
All major vendors split **training / search / user-triggered** agents [22][52][23]:

| Company | Training | Search/retrieval | User-triggered |
|---|---|---|---|
| OpenAI | `GPTBot` | `OAI-SearchBot` | `ChatGPT-User` (robots.txt "may not apply") [22] |
| Anthropic | `ClaudeBot` | `Claude-SearchBot` | `Claude-User` (all three honor robots.txt; Crawl-delay supported) [52] |
| Perplexity | — (PerplexityBot not used for training) | `PerplexityBot` (respects robots.txt) [23][53] | `Perplexity-User` ("generally ignores robots.txt") [23] |
| Google | `Google-Extended` (token only, no HTTP UA; Gemini Apps/Vertex AI) [54] | `Googlebot` (Search + AI Overviews) | `Google-Agent` [57] |
| Apple | `Applebot-Extended` (token; doesn't crawl) [58] | `Applebot` | — |
| Meta | `meta-externalagent` | — | `Meta-ExternalFetcher` ("may bypass robots.txt") [59] |
| Amazon | `Amazonbot` (may train models) | `Amzn-SearchBot` | `Amzn-User` [60] |
| Common Crawl | `CCBot` (checks robots.txt; no JS execution) [61] | — | — |
| ByteDance | `Bytespider` — **no reachable official docs; compliance widely doubted** [79][81] | — | — |

### Recommended posture (evidence + explicit inference)
- **Allow search/retrieval bots** (`OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot`) if you want to be citable in AI search answers — blocking them removes you from those answers per vendor docs [22][23][52].
- **Block training bots** (`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `Applebot-Extended`, `Meta-ExternalAgent`, `Bytespider`) if you don't want content in training sets [51][52][58][59][60]. This is the consensus recommendation of third-party 2026 guides [80][81] — **an inference from vendor docs + practitioner consensus, not a single official mandate**.
- **Google-Extended does not affect Google Search or rankings** ("does not impact a site's inclusion in Google Search nor is it used as a ranking signal") [54][35]. Blocking GPTBot/ClaudeBot likewise has no effect on Google/Bing rankings — they are not search crawlers [22][52] *(inference from official docs)*.
- **Compliance caveats:** robots.txt is voluntary preference, not enforcement [69]. Documented 2025 incident: Perplexity used undeclared/stealth crawlers (rotating UAs/IPs/ASNs) to bypass robots.txt and WAF blocks; Cloudflare de-listed it as a verified bot [75]. Bytespider has a long record of ignoring robots.txt [79][81]. User-triggered bots (ChatGPT-User, Perplexity-User) may ignore robots.txt by design [22][23].
- **Traffic context without analytics:** Cloudflare Radar 2025: AI bots (excl. Googlebot) averaged ~4.2% of HTML requests (Googlebot ~4.5%); GPTBot rose to ~30% of AI-crawler share by May 2025 [77][76]. Crawl-to-refer ratios (June 2025): Google ~14:1, OpenAI ~1,700:1, Anthropic ~73,000:1 — most AI crawling never results in referrals [78]. Cloudflare's AI Crawl Control (formerly AI Audit) provides per-crawler allow/block (WAF-enforced, 403/402), robots.txt violation tracking, "Enforce robots.txt rules", and a managed robots.txt module that prepends AI-crawler blocks [69][70][71][72][73][74].

## 6. robots.txt / sitemap.xml best practices

- **robots.txt (RFC 9309):** parsing limit ≥ 500 KiB (Google enforces 500 KiB) [62][56]; groups of User-agent + Allow/Disallow path rules; named groups override `User-agent: *`; most-specific match wins [56]. **robots.txt manages crawl traffic, not indexing** — disallowed pages can still be indexed via external links; use `noindex`/X-Robots-Tag for removal [55]. Snippets/limits are controlled by `nosnippet`/`data-nosnippet`/`max-snippet`, not robots.txt [12][55].
- **Sitemap directive:** top-level (not tied to a user-agent group), absolute URL, multiple allowed; supported by Google, Bing, CCBot [56][63][61].
- **Sitemap limits (sitemaps.org):** ≤ 50,000 URLs and ≤ 50 MB (52,428,800 bytes) per sitemap; gzip allowed; sitemap index ≤ 50,000 entries; `<lastmod>` optional [63]. Submission is a "hint, not a guarantee" [64].
- **Cloudflare specifics (verified):**
  - Cloudflare caches by file extension: **HTML and JSON are not cached by default**; robots.txt **is** cached by default; `.xml` (sitemap) is **not** cached [65][66][67].
  - Default edge TTLs (no Cache-Control/Expires): 200/206/301 → 120 min; 302/303 → 20 min; 404/410 → 3 min [65].
  - **Caching HTML on a static site requires a Cache Rule** ("Eligible for cache" + Edge TTL mode). Origin `Cache-Control: max-age=0/no-cache/private` still prevents caching unless Edge TTL override is set [66][67][68]. Minimum Edge TTL by plan: Free 2 h, Pro 1 h, Business/Enterprise 1 s [67].
  - On robots.txt policy changes, purge the robots.txt URL (default 120-min TTL) or set a bypass rule [65].

## 7. Core Web Vitals thresholds and HTML caching as ranking factors

- **Thresholds (unchanged through 2026, verified):** LCP good ≤ 2.5 s / poor > 4.0 s; INP good ≤ 200 ms / poor > 500 ms; CLS good ≤ 0.1 / poor > 0.25 — evaluated at the **75th percentile** of field loads, mobile and desktop separately [82][83]. **INP replaced FID on March 12, 2024** [84]. No threshold change is documented in any primary source found for 2025–2026 [82][83]. *(Analyst claims of "2026 INP methodology tightening / TTFB promoted in PSI" are unverified against primary sources; Chrome is standardizing soft-navigation measurement, which doesn't change thresholds [85].)*
- **Ranking-factor status:** Google documents CWV as "a set of metrics... This, along with other page experience aspects, aligns with what our core ranking systems seek to reward" [82]. After an April 2024 documentation clarification, **only CWV are directly used by ranking systems among page experience aspects** — HTTPS, mobile-friendliness, no intrusive interstitials do not directly help rankings [87][88]. Evaluated from **field data (CrUX), sitewide, 75th percentile** [82][86][89]. Weight is small: "it's not going to make your site's rankings jump up" [87][90].
- **HTML caching as a ranking factor:** Google has stated it does not use TTFB for ranking (2017) [91]; TTFB is a diagnostic, not a Core Web Vital [92]. But web.dev: "high TTFB values add time to the metrics that follow it"; good TTFB ≤ 0.8 s, poor > 1.8 s [92][93]. So **edge caching of HTML is a performance/UX and CWV play, not a direct ranking factor** *(mechanism inference from [91][92])*. It also improves crawl efficiency [8][96]. For a static site on Cloudflare, caching the HTML document at the edge (Cache Rule) removes the origin round-trip from TTFB → LCP [94][95].

## 8. E-E-A-T / YMYL for heat-protection content

- **YMYL classification:** Google's Quality Rater Guidelines define YMYL as content that can affect health, safety, financial stability, or well-being; the July 2022 revision frames "YMYL Health or Safety" in terms of potential harm to mental, physical, emotional health or safety [97][98]. Heat-protection/heat-warning content is health-and-safety adjacent: the DWD itself frames Hitzewarnungen as health protection for vulnerable groups (elderly, chronically ill, children) [118]. **Inference: raters would treat heat-advice pages as YMYL-ish.** *(QRG full text is PDF-only — exact current wording via secondary quotes + Sept 2025 QRG update coverage [97][127]; flagged blocked.)*
- **E-E-A-T signals:** Trust is "the most important member of the E-E-A-T family" [99]; raters look for who is responsible for the site and About/Contact info [100][127]. Practical signals for a small German site: author bylines, About page, real contact info, citations to official sources (DWD, Umweltbundesamt), HTTPS, Impressum, Datenschutzerklärung [101][102][103].
- **Impressum — legal status 2026:** the TMG was replaced by the **Digitale-Dienste-Gesetz (DDG), in force since May 14, 2024**; the Impressum duty is now **§ 5 DDG** [104][105][106][108]. Required items (§ 5(1)): name + full address; for entities: legal form, authorized representatives, share capital if stated; contact details enabling fast electronic contact **including email**; register/USt-IdNr/Wirtschafts-ID where held; supervisory/professional-chamber info where relevant [104]. Must be "leicht erkennbar und unmittelbar erreichbar" (linked from every page, ≤ 2 clicks) [104][107]. Datenschutzerklärung references should use **TDDDG** (renamed from TTDSG alongside the DDG) [105].
- **Is Impressum a ranking factor?** No Google statement confirms it; trust associations/memberships are not direct ranking factors [109][110]; German SEO practice treats it as a trust/E-E-A-T signal, not a direct factor [101][102]. **Position: required legally; a trust signal; not a confirmed ranking factor.**

## 9. German local SEO keywords

- **Keyword patterns (evidence is third-party estimates, not Google-official):** "hitzeschutzfolie für fenster" (difficulty 38, high competition), "sonnenschutzfolie fenster" (~1,900), "fenster hitzeschutz folie" (~1,900), "hitzeschutz fenster innen" (~100–710), "thermo plissee" (~2,400), "hitzeschutz haare" (~2,900 — different intent) [111][112][113]. Head term "Hitzeschutz" is **mixed intent** (films, blinds, hair care, tents) — only the window-film/blind/Jalousie segment is clearly local-business intent *(inference from keyword mix)* [112][113].
- **City+keyword combos** ("Hitzeschutz München") are standard German local-SEO practice [114][115]; real examples exist ("Sonnenschutzfolie & Hitzeschutzfolie in München und Umgebung", service areas "Raum Schwerte und Dortmund") [124][131]. **Avoid thin doorway city pages** — city landing pages need real local value or they can harm rankings [116][117].
- **Local signals without analytics:** Google Business Profile (incl. **service-area profiles** for Handwerker without a storefront — official support via Local Services Ads for household services in DE) [125][128]; NAP consistency across web + directories; Bing Places for Business (relaunched Oct 2025; relevant since DDG classic results are Bing-sourced and Bing Copilot cites web results) [121][122][123].
- **Seasonality:** heat-warning/heat-protection interest spikes in summer (longest DWD early heat-warning period: 12 days in June 2026) [119][120] — publish/refresh content before the season *(inference)*.
- **Local relevance in AI search:** German trade press notes content without regional reference is barely relevant for Handwerksbetriebe in AI/classic search [126].

## Caveats and disagreements

- **QRG exact wording:** the Quality Rater Guidelines are PDF-only; YMYL/E-E-A-T claims rely on secondary quotes + the Sept 2025 QRG update summary [97][98][127]. PDF parsing was intentionally skipped per method policy.
- **Keyword volumes:** Performance Suite estimates, not Google Keyword Planner; exact volumes will differ [111][112][113].
- **Bing guidelines full text:** client-rendered page; only snippets verified [11]. A secondary claim that Bingbot announced "headless Chromium rendering in late 2024" could not be verified and likely misdates the 2019 Edge adoption [6] — treat Bing's 2019 evergreen Edge rendering [17] as the current fact.
- **DuckDuckGo own-index JS rendering** is secondary-sourced (podcast + trade press) [21].
- **AI crawler JS execution:** no official OpenAI/Perplexity statement that they execute JS; "raw HTML only" is an industry inference [6][80].
- **noscript guidance** is old and mixed (2018–2019) [14][15].
- **Cloudflare Pages "Block AI training bots"/"Manage robots.txt" default-on toggles** are claimed by a third-party hands-on report; verify in your dashboard [129].
- **FAQ rich result deprecation timeline** (RRT support June 2026, SC API Aug 2026) from Google changelog + SEJ [29][45].

## Open questions

1. Whether OAI-SearchBot/PerplexityBot execute JS at all (no official documentation) — static HTML remains the only safe assumption.
2. Exact 2026 status of DuckDuckGo's own index at scale (rolling out; share of production traffic unknown) [21].
3. Whether Google will adjust CWV thresholds or replace INP (no evidence of change as of Aug 2026).
4. Bytespider compliance posture (no operator documentation).
5. Whether Google treats Impressum presence beyond a trust signal (no official statement).

## Sources

**Verification note (2026-08-09):** every URL below was checked via HTTP request (curl, browser UA) and, where the server blocks non-browser clients, via content fetch or API. All 124 draft URLs plus the 4 additions below are reachable and on-topic; **no dead links found**. Entries marked ⚠ are reachable but were only partially verifiable (bot-protected but content confirmed, or client-rendered page).

Primary/official:
1. https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics — Google, Understand JavaScript SEO Basics (updated 2026-03-04)
2. https://blogs.bing.com/webmaster/october-2018/bingbot-Series-JavaScript,-Dynamic-Rendering,-and-Cloaking-Oh-My — Bing Webmaster Blog 2018
7. https://developers.cloudflare.com/browser-run/how-to/pre-render-pages/ — Cloudflare, Pre-render pages for crawlers
8. https://developers.google.com/crawling/docs/crawl-budget — Google, Crawl Budget Management
12. https://developers.google.com/search/docs/appearance/ai-features — Google, AI Features and Your Website (updated 2025-12-10)
17. https://blogs.bing.com/webmaster/october-2019/The-new-evergreen-Bingbot-simplifying-SEO-by-leveraging-Microsoft-Edge — Bing Webmaster Blog 2019
20. https://duckduckgo.com/duckduckgo-help-pages/results/sources — DuckDuckGo Help, result sources
22. https://developers.openai.com/api/docs/bots — OpenAI, Overview of OpenAI Crawlers
23. https://docs.perplexity.ai/docs/resources/perplexity-crawlers — Perplexity Crawlers
26. https://developers.google.com/search/blog/2024/10/sitelinks-search-box — Google, Farewell, Sitelinks Search Box (2024)
27. https://developers.google.com/search/docs/appearance/site-names — Google, Site names in Google Search (updated 2025-12-10)
28. https://developers.google.com/search/docs/appearance/structured-data/dataset — Google, Dataset structured data (updated 2025-12-10)
29. https://developers.google.com/search/updates — Google Search Central changelog
30. https://developers.google.com/search/blog/2023/08/howto-faq-changes — Google, Changes to HowTo and FAQ rich results (2023)
31. https://developers.google.com/search/docs/appearance/structured-data/breadcrumb — Google, Breadcrumb docs
32. https://developers.google.com/search/docs/appearance/structured-data/organization — Google, Organization docs
33. https://developers.google.com/search/docs/appearance/structured-data/local-business — Google, Local business docs
34. https://developers.google.com/search/docs/appearance/structured-data/speakable — Google, Speakable (BETA)
35. https://developers.google.com/search/docs/appearance/structured-data/search-gallery — Google, structured data gallery
36. https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data — Google, Intro to structured data
37. https://support.google.com/webmasters/answer/7445569 — Google Search Console Help, Rich Results Test
38. https://developers.google.com/search/blog/2025/11/update-on-our-efforts — Google, simplifying the search results page (2025-11)
39. https://ogp.me/ — Open Graph protocol spec
40. https://developers.facebook.com/docs/sharing/best-practices/ — Facebook Sharing Best Practices ⚠ (HTTP 400 to curl; content confirmed via fetch — page live)
41. https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/ — Cloudflare, Email Address Obfuscation
42. https://developers.cloudflare.com/bots/get-started/bot-fight-mode/ — Cloudflare, Bot Fight Mode
43. https://developers.cloudflare.com/fundamentals/reference/cdn-cgi-endpoint/ — Cloudflare, /cdn-cgi/ endpoint
44. https://developers.cloudflare.com/pages/functions/plugins/vercel-og/ — Cloudflare, vercel-og Pages plugin
49. https://github.com/vercel/satori — Satori
50. https://github.com/kvnang/workers-og — workers-og
52. https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler — Anthropic crawler documentation
54. https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers — Google, Common crawlers (Google-Extended)
55. https://developers.google.com/search/docs/crawling-indexing/robots/intro — Google, Robots.txt Introduction
56. https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec — Google, robots.txt spec interpretation
57. https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers — Google, Overview of Google crawlers
58. https://support.apple.com/en-us/119829 — Apple, About Applebot
59. https://developers.facebook.com/docs/sharing/webmasters/web-crawlers — Meta, Web Crawlers ⚠ (HTTP 400 to curl; content confirmed via fetch — page live)
60. https://developer.amazon.com/amazonbot — Amazon, About AmazonBot
61. https://commoncrawl.org/faq — Common Crawl FAQ
62. https://www.rfc-editor.org/rfc/rfc9309.html — RFC 9309 (robots.txt standard)
63. https://sitemaps.org/protocol.html — sitemaps.org protocol
64. https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap — Google, Build and Submit a Sitemap
65. https://developers.cloudflare.com/cache/concepts/default-cache-behavior/ — Cloudflare, Default Cache Behavior
66. https://developers.cloudflare.com/cache/get-started/ — Cloudflare, Get started with Cache
67. https://developers.cloudflare.com/cache/how-to/cache-rules/settings/ — Cloudflare, Cache Rules settings
68. https://developers.cloudflare.com/cache/concepts/customize-cache/ — Cloudflare, Customize cache
69. https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/ — Cloudflare, Managed robots.txt
70. https://developers.cloudflare.com/ai-crawl-control/features/manage-ai-crawlers/ — Cloudflare, Manage AI crawlers
71. https://developers.cloudflare.com/ai-crawl-control/features/track-robots-txt/ — Cloudflare, Track robots.txt
72. https://developers.cloudflare.com/ai-crawl-control/reference/bots/ — Cloudflare, Bot reference
73. https://blog.cloudflare.com/cloudflare-ai-audit-control-ai-content-crawlers/ — Cloudflare Blog, AI Audit launch
74. https://blog.cloudflare.com/ai-audit-enforcing-robots-txt/ — Cloudflare Blog, enforcing robots.txt
75. https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/ — Cloudflare Blog, Perplexity stealth crawling (2025-08-04)
76. https://blog.cloudflare.com/from-googlebot-to-gptbot-whos-crawling-your-site-in-2025/ — Cloudflare Blog, Googlebot to GPTBot (2025)
77. https://blog.cloudflare.com/radar-2025-year-in-review/ — Cloudflare Radar 2025 Year in Review
78. https://blog.cloudflare.com/control-content-use-for-ai-training/ — Cloudflare Blog, control content use for AI training
82. https://developers.google.com/search/docs/appearance/core-web-vitals — Google, Understanding CWV and search results (updated 2025-12-10)
83. https://web.dev/articles/vitals — web.dev, Web Vitals
84. https://web.dev/blog/inp-cwv-march-12 — web.dev, INP becomes a CWV (2024-03-12)
85. https://developer.chrome.com/docs/web-platform/soft-navigations — Chrome for Developers, measuring soft navigations
86. https://developer.chrome.com/docs/crux/release-notes — CrUX release notes
89. https://support.google.com/webmasters/answer/9205520 — Google Search Console Help, CWV report
92. https://web.dev/articles/ttfb — web.dev, TTFB
93. https://web.dev/articles/optimize-ttfb — web.dev, Optimize TTFB
94. https://developers.cloudflare.com/cache/how-to/edge-browser-cache-ttl/set-browser-ttl/ — Cloudflare, Browser Cache TTL
95. https://developers.cloudflare.com/cache/concepts/cache-control/ — Cloudflare, Origin Cache Control
96. https://developers.google.com/crawling/docs/myths-about-crawling — Google, Myths about crawling
103. https://developers.google.com/search/docs/fundamentals/creating-helpful-content — Google, helpful-content guidance
104. https://www.gesetze-im-internet.de/ddg/__5.html — § 5 DDG (official German law text)
105. https://www.ihk.de/osnabrueck/recht-und-fair-play/aktuelles/ddg-ersetzt-das-tmg-6220008 — IHK Osnabrück, DDG ersetzt TMG
106. https://bak.de/tmg-heisst-jetzt-ddg-impressum-ueberpruefen/ — Bundesarchitektenkammer, TMG heißt jetzt DDG
107. https://www.ihk.de/koblenz/unternehmensservice/recht/rechtsauskuenfte-von-a-z/it-recht/merkblatt-impressum-3462798 — IHK Koblenz, Impressum Merkblatt
108. https://www.bmjv.de/SharedDocs/FAQ/DE/FAQ_Database/Onlineplattformen_Schutzregelungen/FAQ-Onlineplattformen_Schutzregelungen-008.html — BMJV FAQ Impressumspflicht
118. https://www.dwd.de/DE/leistungen/hitzewarnung/hitzewarnung.html — DWD Hitzewarnung
119. https://www.dwd.de/DE/presse/pressemitteilungen/DE/2026/20260625_dwd-warnt-ueber-langen-zeitraum-vor-hitze_news.html — DWD Presse 25.06.2026
120. https://www.dwd.de/DE/wetter/thema_des_tages/2026/6/17.html — DWD Thema des Tages (Hitzewarnungen)
122. https://www.bing.com/forbusiness/ — Bing Places for Business
128. https://business.google.com/de/ad-solutions/local-service-ads/ — Google Lokale Dienstleistungen (Local Services Ads DE, official; added to support the "official support via Local Services Ads for household services in DE" claim) — verified 2026-08-09

Secondary / trade / third-party:
5. https://www.indexprobe.com/en/blog/javascript-seo/ — IndexProbe, JS SEO
6. https://crawlix.app/blog/javascript-rendering-seo/ — Crawlix, JS rendering 2026
9. https://www.onely.com/blog/googles-two-waves-of-indexing/ — Onely, two waves of indexing (2019)
10. https://www.seroundtable.com/google-no-two-waves-indexing-29225.html — SERoundtable (2020)
11. https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a — Bing Webmaster Guidelines (current) ⚠ (reachable HTTP 200, but page is client-rendered — only snippet-level content was verifiable, as flagged in §2)
13. https://docs.prerender.io/docs/how-do-i-integrate-prerender-with-cloudflare-workers — Prerender.io, Cloudflare Workers
14. https://www.seroundtable.com/google-noscript-tag-18729.html — SERoundtable, noscript (2018)
15. https://www.seroundtable.com/google-supports-noscript-tag-26536.html — SERoundtable, noscript images (2019)
16. https://www.searchenginejournal.com/google-no-need-to-worry-about-using-javascript/408788/ — SEJ (2020)
18. https://blogs.bing.com/webmaster/december-2019/Announcing-future-user-agents-for-Bingbot — Bing Webmaster Blog (2019)
21. https://insideduckduckgo.substack.com/p/duck-tales-why-duckduckgo-is-building — Inside DuckDuckGo, Duck Tales Ep. 22
24. https://www.seroundtable.com/bing-powers-chatgpt-search-38345.html — SERoundtable, Bing powers ChatGPT Search (2024)
25. https://webmasters.stackexchange.com/questions/900/can-text-content-in-an-html5-canvas-element-be-indexed-by-search-engines — webmasters.SE, canvas indexing ⚠ (HTTP 403 to bots; content confirmed via StackExchange API — page live)
45. https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/ — SEJ, FAQ rich results dropped (2026)
46. https://link.boo/guides/x-link-card-not-showing — link.boo, X card guide
47. https://stackoverflow.com/questions/72889599/twitter-card-images-no-longer-generating-properly-from-wordpress-site-links — SO, Twitter card validator removal ⚠ (HTTP 403 to bots; content confirmed via StackExchange API — page live)
48. https://www.thatdevpro.com/reference/html-twitter-cards/ — ThatDevPro, Twitter Cards reference ⚠ (first curl attempt timed out; content confirmed via fetch — page live)
51. https://help.openai.com/en/articles/7842364-how-chatgpt-and-our-language-models-are-developed — OpenAI help ⚠ (HTTP 403 to curl; content confirmed via fetch — page live)
53. https://www.perplexity.ai/help-center/en/articles/10354969-how-does-perplexity-follow-robots-txt.html — Perplexity help, robots.txt ⚠ (HTTP 403 to curl; content confirmed via fetch — page live; confirms PerplexityBot respects robots.txt)
79. https://agentgrade.com/agents/bytespider — AgentGrade, Bytespider
80. https://crawlytics.app/resources/ai-bots-list — Crawlytics, AI bots list (2026)
81. https://www.voctos.com/blog/robots-txt-ai-crawlers/ — Voctos, robots.txt for AI crawlers (2026)
87. https://www.seroundtable.com/google-clarifies-page-experience-core-web-vitals-37046.html — SERoundtable, page experience clarification
88. https://www.searchenginejournal.com/core-web-vitals-google-ranking-systems/511020/ — SEJ, CWV in ranking systems
90. https://www.debugbear.com/docs/core-web-vitals-ranking-factor — DebugBear, CWV ranking factor
91. https://www.seroundtable.com/google-time-to-first-byte-24847.html — SERoundtable, TTFB not used (2017)
97. https://priceweber.com/blog/understanding-googles-ymyl-guidelines/ — PriceWeber, YMYL (§2.3 quote)
98. https://www.mariehaynes.com/july-2022-qrg-update/ — Marie Haynes, July 2022 QRG
99. https://www.semrush.com/blog/eeat/ — Semrush, E-E-A-T
100. https://www.searchenginejournal.com/google-about-us-contact-pages-not-important/512241/ — SEJ, About/Contact
101. https://www.inventivo.de/blog/seo/e-e-a-t-konkret-umsetzen — INVENTIVO, E-E-A-T Praxis-Guide (DE)
102. https://seranking.com/de/blog/google-eeat-ymyl/ — SE Ranking DE, E-E-A-T/YMYL
109. https://www.seroundtable.com/google-trust-associations-memberships-26687.html — SERoundtable, trust associations
110. https://www.searchenginejournal.com/trust-metrics-and-google/424679/ — SEJ, trust metrics
111. https://www.performance-suite.io/keyword-db/de-de/hitzeschutz-fenster-innen/ — Performance Suite, keyword data
112. https://www.performance-suite.io/keyword-db/de-de/hitzeschutzfolie-f%C3%BCr-fenster/ — Performance Suite, keyword data
113. https://www.performance-suite.io/keyword-db/de-de/dachfenster-folieren/ — Performance Suite, keyword data
114. https://www.seokratie.de/local-seo-fuer-fortgeschrittene/ — Seokratie, Local SEO (DE)
115. https://www.sistrix.de/frag-sistrix/seo-grundlagen/local-seo/ — SISTRIX, Local SEO (DE)
116. https://www.seopt.de/local-seo-landingpages/ — SEOPT, local landing pages (DE)
117. https://www.getsichtbar.com/blog/lokale-landing-pages-ai-sichtbarkeit — getSichtbar, lokale Landing Pages (DE)
121. https://www.getsichtbar.com/blog/bing-copilot-ai-sichtbarkeit — getSichtbar, Bing Copilot visibility (DE)
123. https://ki-q.de/blog/news/local-ai-visibility-bing-places-indexnow/ — KI-Q, Local AI Visibility 2026 (DE)
124. https://folienservice-bayern.de/produkte/sonnenschutzfolie/ — Folienservice Bayern (example city page)
125. https://anikawachter.de/google-business-profile-ohne-ladenlokal-handwerker — Anika Wachter, GBP service-area (DE)
126. https://www.handwerk-magazin.de/kuenstliche-intelligenz-bei-der-suche-was-chatgpt-perplexity-co-fuer-die-digitale-sichtbarkeit-von-betrieben-bedeuten-337473/ — handwerk magazin (DE)
127. https://searchengineland.com/google-updates-search-quality-raters-guidelines-adding-ai-overview-examples-ymyl-definitions-461908 — Search Engine Land, QRG update (Sept 2025)
129. https://agentcookbooks.com/blog/cloudflare-pages-html-cache-the-missing-rule/ — AgentCookbooks, Cloudflare Pages HTML cache rule + AI-bot toggle defaults (added to support the "default-on toggles" caveat) — verified 2026-08-09
130. https://seotest.app/blog/og-image-size-format-best-practices — seotest.app, OG Image Size & Format 2026 (added to support the 1200×630 / <1 MB / PNG-JPG / declared-dimensions claims) — verified 2026-08-09
131. https://www.esfol.de/ — eS-FOL, Sonnenschutz im Raum Schwerte und Dortmund (added to support the "Raum Schwerte und Dortmund" service-area example) — verified 2026-08-09
