# Research notes T1 — JS-rendered map content: indexability & search-engine rendering behavior

Status: done (all 6 questions covered). Draft notes only — NOT the final report.
Researched: 2026-08-09. Dates of key docs noted inline; anything older than ~2023 flagged as potentially outdated.

---

## Key findings per question

### Q1. Google JS rendering (verified against official docs)

- Google's current official guidance (JavaScript SEO Basics, `Last updated 2026-03-04 UTC` [1]) describes a three-phase pipeline: **Crawling → Rendering → Indexing**. Googlebot runs an **evergreen version of Chromium** [1][3].
- Rendering is queued, not guaranteed-instant: "The page may stay on this queue for a few seconds, but it can take longer than that. Once Google's resources allow, a headless Chromium renders the page and executes the JavaScript. Googlebot parses the rendered HTML for links again... Google also uses the rendered HTML to index the page." [1]. A `noindex` tag can cause Google to skip rendering entirely [1][2].
- "Two-wave indexing" is **no longer the operative model**. Martin Splitt (2019): "two waves of indexing play less and less of a role" [10]; (2020): "there's no such thing as the second wave of crawling... It's all an oversimplification" [12]; Splitt reported median crawl-to-render time ~5 seconds (I/O-era statement) [11]. Current official docs no longer describe two waves [1].
- JS-only content and links: indexable in principle — Google renders and indexes the rendered DOM, and discovers links added by JS (rendered links are re-parsed) [1]. BUT reliability depends on rendering success; if rendering fails/times out or resources are blocked, JS-only content never reaches the index [2][7]. Google: "If the content isn't visible in the rendered HTML, Google won't be able to index it." [1]
- Google's explicit recommendation: "server-side or pre-rendering is still a great idea because it makes your website faster for users and crawlers, **and not all bots can run JavaScript**." [1] Google also removed its old "design for accessibility / JS-off" advice in Mar 2025 as outdated, while reiterating that other bots don't render like Googlebot [4].
- Crawl budget: capacity limit + crawl demand [9]; JS-heavy sites spend more crawler resources per URL (third-party analyses quantify render-queue waste [6][7] — these are secondary claims, use with care).

### Q2. Best-practice architecture for an interactive map on a static site

- **Visible static HTML outside the canvas is the primary recommendation.** Google's AI-features doc likewise lists "Making sure that important content is available in textual form" as a best practice [14].
- **`<noscript>` is unreliable as a content strategy.** Current Google JS SEO Basics does not mention `<noscript>` at all [1]. Historically: John Mueller (2018): Google "simply ignores or does not trust content within the noscript tag" for web content [18]; Gary Illyes (2019): Google does index noscript content; John Mueller confirmed noscript is used for images [19]. Evidence is mixed/dated — treat `<noscript>` as a degraded-fallback aid, never as the primary carrier of important text. (Flag: needs current verification, no 2025–2026 official statement found.)
- **Prerendering options** (all documented):
  - **prerender.io + Cloudflare Worker**: official integration guide — Worker checks User-Agent, routes bot requests to prerender.io, serves cached rendered HTML; requires Cloudflare proxy mode; SXG must be disabled [15][16][17].
  - **Cloudflare Browser Run (official, current)**: Worker + Browser Run binding renders a public URL in managed headless Chrome (`quickAction("content")`, `waitUntil: "networkidle2"`), returns rendered HTML; recommended to cache rendered HTML and only render hostnames you control [8]. This fits the brief's Cloudflare hosting.
  - Bing itself recommends dynamic rendering / prerendered static HTML for JS-heavy sites (2018, official Bing blog — see Q3).
- Progressive enhancement for maps: content behind user interaction is not seen — "Googlebot doesn't interact with anything when it crawls webpages" [20]. Static heading/description/list of locations/regions outside the map canvas mirrors both Google's guidance and the real-estate prerendering patterns [21].

### Q3. Bing

- Bing's **current** Webmaster Guidelines (updated 2025, intro rewritten to cover "Bing search experiences, Copilot, and grounding API results") say Bing relies on clear discovery and crawl signals "to find, render, and index content accurately"; emphasize sitemaps, IndexNow, lastmod [13]. **Note: the guidelines page is client-rendered; full text could not be fetched (stub only) — see Blocked.** The snippet-level content is real but partial.
- Official Bing blog (2018): "bingbot is generally able to render JavaScript. However, bingbot does not necessarily support all the same JavaScript frameworks..." Bing recommends detecting the bingbot UA and **prerendering static HTML server-side** ("dynamic rendering"), and states this is not cloaking if the same content is served in good faith [2][22].
- 2019: Bing adopted **Microsoft Edge (Chromium) as its rendering engine**; Bingbot became evergreen; new user agents `bingbot/2.0` announced Dec 2019 [23][24][25].
- Known limitations: older guideline text warned "Rich media (Flash, JavaScript, etc.) can lead to Bing not being able to crawl through navigation, or not see content embedded in a webpage" [26] — this phrasing was current as of ~2020; I could not confirm whether it remains in the current guidelines (blocked).
- **Unverified claim flagged:** a 2026 blog table states Bingbot "announced headless Chromium-based rendering in late 2024" [7]. I found no primary source for a 2024 announcement; it appears to conflate the 2019 Edge adoption. Do not use without further verification.

### Q4. DuckDuckGo

- Official help page: DDG's traditional links and images results are "largely sourced from Bing"; DDG also maintains its own crawler (DuckDuckBot) and "many indexes" for Instant Answers [27]. So for 2025–2026, DDG indexing of classic results ≈ Bing's index → Bingbot rendering applies.
- DuckDuckGo is building its **own full web search index** (founder Gabriel Weinberg & CTO Caine Tighe, Duck Tales podcast Ep. 22, ~Mar 2026); CTO describes a pipeline with a **two-pass JavaScript rendering approach**; index already live for part of production traffic as of early 2026 [28][29]. Secondary reporting only (Agent Wars) — mark as medium confidence.
- No official DDG statement about JS rendering of crawled pages found in this pass (blocked item).

### Q5. AI search engines

- **Google AI Overviews / AI Mode**: official doc (`Last updated 2025-12-10 UTC`): to appear as a supporting link, "a page must be indexed and eligible to be shown in Google Search with a snippet... **There are no additional technical requirements.**" AI features use query fan-out over the standard Google index [14]. Control via `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`; `Google-Extended` is only for AI training/grounding in other systems [14][30]. Implication: AI Overviews inherit Googlebot rendering.
- **ChatGPT Search / OpenAI**: official crawler docs — `OAI-SearchBot` "is used to surface websites in search results in ChatGPT's search features"; blocking it removes pages from ChatGPT search answers; `GPTBot` is training-only; `ChatGPT-User` is user-initiated and robots.txt "may not apply"; ~24 h propagation for robots.txt changes [31]. ChatGPT Search also uses third-party search providers, notably **Bing** [32]. Evidence that Bing's index powers much of ChatGPT Search (2024): a site penalized in Bing disappeared from ChatGPT search results [33]. No statement that OAI-SearchBot executes JS (see Q6 inference).
- **Perplexity**: official docs — `PerplexityBot` "designed to surface and link websites in search results on Perplexity," not used for foundation-model training; `Perplexity-User` fetches pages on user request and "generally ignores robots.txt rules" [34]. No JS-rendering statement in official docs; third-party guide states PerplexityBot captures "the rendered page text after server-side rendering or pre-rendering" and has a limited render budget for JS-only content [35] (secondary, medium confidence).
- **Bing Copilot**: current guidelines state the same core crawling/indexing foundation underlies "Bing search experiences, Copilot, and grounding API results" [13].

### Q6. Content that is not indexable in practice

- **Canvas/WebGL-rendered map tiles & text**: content drawn into a canvas is pixels — no DOM text nodes, no links; crawlers cannot extract it [36][37][38][39]. Fallback text between `<canvas>` tags is only picked up if present as real HTML [39]. (Experimental Google Chrome "HTML-in-Canvas" API with `layoutsubtree` would keep DOM content searchable, but it is new/experimental [40].)
- **Dynamically injected markers/overlays**: real-world case (Google Maps overlay content, Stack Overflow, 2014): overlay content was not indexed [41]; the 2026-era guidance is that interaction-dependent content is invisible because Googlebot does not interact with pages [20][1].
- **Data loaded via fetch/XHR without static HTML equivalents**: indexable only if the render pass succeeds; blocked resources (robots.txt-disallowed JS/CSS), execution errors, or timeouts drop the content [1][2][7].
- **AI-crawler inference:** OpenAI, Perplexity, and other AI-crawler docs describe fetching pages for indexing but none document JS execution; 2026 industry tables claim AI crawlers receive raw HTML only (Google & Bing render; "almost nothing else does") [7]. This is an aggregated industry claim — **inference, not official** — but it is consistent with the official docs' silence on rendering and with Google/Bing being the only engines documenting JS rendering.

---

## Architecture recommendation evidence (synthesis)

For a static HTML + client-side interactive map site (Cloudflare):
1. Ship all discoverable text (page H1/H2s, region/location descriptions, location lists with real `<a href>` links) as **static HTML in the initial response** — this is what Google indexes immediately [1], what Bing's prerender advice targets [2], and what AI crawlers that don't execute JS can read [7][35].
2. Keep the map canvas/WebGL as progressive enhancement on top of that HTML; don't rely on `<noscript>` for primary content [1][18].
3. Optionally prerender bot requests at the edge (Cloudflare Worker + Browser Run [8], or prerender.io [15]) for JS-derived HTML — but with static fallback content, prerendering is a performance/extra-bot optimization, not a correctness requirement for Google [1].
4. Map tiles, marker popups, and XHR-only data need static equivalents (textual lists/pages) to be indexable at all [36][39][41].

---

## Sources

1. Google Search Central — Understand JavaScript SEO Basics (last updated 2026-03-04) — https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics (fetched, verified)
2. Bing Webmaster Blog — bingbot Series: JavaScript, Dynamic Rendering, and Cloaking. Oh My! (2018-10) — https://blogs.bing.com/webmaster/october-2018/bingbot-Series-JavaScript,-Dynamic-Rendering,-and-Cloaking-Oh-My (fetched via search, quoted)
3. web.dev — Making JavaScript and Google Search work together (I/O 2019) — https://web.dev/blog/javascript-and-google-search-io-2019
4. Search Engine Journal — Google Removes JavaScript SEO Warning, Says It's Outdated (2025) — https://www.searchenginejournal.com/google-removes-javascript-seo-warning-says-its-outdated/568829/
5. Search Engine Journal — Google Updates JavaScript SEO Docs With Canonical Advice (2025) — https://www.searchenginejournal.com/google-updates-javascript-seo-docs-with-canonical-advice/563545/
6. IndexProbe — JavaScript SEO: What Google Actually Indexes After Rendering — https://www.indexprobe.com/en/blog/javascript-seo/
7. Crawlix — JavaScript Rendering in 2026 — https://crawlix.app/blog/javascript-rendering-seo/
8. Cloudflare — Pre-render pages for crawlers (Browser Run tutorial, compatibility_date 2026) — https://developers.cloudflare.com/browser-run/how-to/pre-render-pages/ (fetched, verified)
9. Google — Crawl Budget Management — https://developers.google.com/crawling/docs/crawl-budget
10. Onely — Is Google's Two Waves of Indexing Over? (2019) — https://www.onely.com/blog/googles-two-waves-of-indexing/
11. Onely — Google's Rendering Delay is 5 Sec. (2019) — https://www.onely.com/blog/googles-rendering-delay-5-seconds/
12. Search Engine Roundtable — Google Says There Is No Such Thing As Two Waves Of Indexing Or Crawling (2020) — https://www.seroundtable.com/google-no-two-waves-indexing-29225.html
13. Bing Webmaster Guidelines (current) — https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a (fetch blocked to stub; quoted via search)
14. Google Search Central — AI Features and Your Website (last updated 2025-12-10) — https://developers.google.com/search/docs/appearance/ai-features (fetched, verified)
15. Prerender.io docs — How do I integrate Prerender with Cloudflare Workers? — https://docs.prerender.io/docs/how-do-i-integrate-prerender-with-cloudflare-workers
16. Prerender.io docs — How Prerender.io works with CDNs — https://docs.prerender.io/docs/how-does-prerender-work-with-cdns-like-cloudflare-fastly-or-akamai
17. GitHub — prerender/prerender-cloudflare-worker — https://github.com/prerender/prerender-cloudflare-worker
18. Search Engine Roundtable — Google: Avoid Using The noscript For Content You Want Google To Trust (2018) — https://www.seroundtable.com/google-noscript-tag-18729.html
19. Search Engine Roundtable — Google Supports Noscript Tag For Images But What About Web Content? (2019) — https://www.seroundtable.com/google-supports-noscript-tag-26536.html
20. Search Engine Journal — Google: No Need to Worry About Using JavaScript (2020) — https://www.searchenginejournal.com/google-no-need-to-worry-about-using-javascript/408788/
21. Prerender.info — Real Estate SEO: Pre-rendering for Listings & Sold-Status — https://prerender.info/use-cases/real-estate
22. Search Engine Journal — Bing's Recommendations for Optimizing JavaScript Sites for Search Crawlers — https://www.searchenginejournal.com/bings-recommendations-for-optimizing-javascript-sites-for-search-crawlers/276507/
23. Bing Webmaster Blog — The new evergreen Bingbot simplifying SEO by leveraging Microsoft Edge (2019-10) — https://blogs.bing.com/webmaster/october-2019/The-new-evergreen-Bingbot-simplifying-SEO-by-leveraging-Microsoft-Edge
24. Bing Webmaster Blog — Announcing future user-agents for Bingbot (2019-12) — https://blogs.bing.com/webmaster/december-2019/Announcing-future-user-agents-for-Bingbot
25. Search Engine Land — Bingbot goes evergreen (2019) — https://searchengineland.com/bingbot-goes-evergreen-323216
26. Screaming Frog — Is Bing Really Rendering & Indexing JavaScript? (2020) — https://www.screamingfrog.co.uk/blog/bing-javascript/
27. DuckDuckGo Help Pages — Where do DuckDuckGo search results come from? — https://duckduckgo.com/duckduckgo-help-pages/results/sources
28. Inside DuckDuckGo — Duck Tales Ep.22: Why DuckDuckGo is building its own web search index — https://insideduckduckgo.substack.com/p/duck-tales-why-duckduckgo-is-building
29. Agent Wars — DuckDuckGo Building Its Own Web Search Index to Power AI Products (2026-03-15) — https://agent-wars.com/news/2026-03-15-duckduckgo-building-its-own-web-search-index-to-power-ai-products (secondary)
30. Google Search Central blog — Top ways to ensure your content performs well in Google's AI features (2025-05) — https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search
31. OpenAI — Overview of OpenAI Crawlers — https://developers.openai.com/api/docs/bots (fetched, verified)
32. OpenAI Help Center — ChatGPT Search — https://help.openai.com/en/articles/9237897-chatgpt-search.ejs
33. Search Engine Roundtable — Bing Powers ChatGPT Search (2024) — https://www.seroundtable.com/bing-powers-chatgpt-search-38345.html
34. Perplexity — Perplexity Crawlers — https://docs.perplexity.ai/docs/resources/perplexity-crawlers (fetched, verified)
35. Citare — How Perplexity Indexes Websites — https://www.citare.ai/guides/how-perplexity-indexes-websites (secondary)
36. Utsubo — WebGL & Three.js Site SEO: Make 3D Sites Rankable (2026) — https://www.utsubo.com/blog/webgl-three-js-site-seo-rankable-guide
37. codesoltech — Flutter for Web SEO: Is It Actually Search-Ready? — https://www.codesoltech.com/blog/flutter-for-web-seo/
38. webmasters.stackexchange — Can text content in an HTML5 <canvas> element be indexed by search engines? — https://webmasters.stackexchange.com/questions/900/can-text-content-in-an-html5-canvas-element-be-indexed-by-search-engines
39. webmasters.stackexchange — GoogleBot Indexing dynamic site content in Google Maps overlay — https://stackoverflow.com/questions/24598264/googlebot-indexing-dynamic-site-content-in-google-maps-overlay
40. GoogleChrome/modern-web-guidance (GitHub) — expose-canvas-content-to-browser-features.md — https://github.com/GoogleChrome/modern-web-guidance/blob/main/skills/modern-web-guidance/guides/user-experience/expose-canvas-content-to-browser-features.md
41. WebAshes — HTML-in-Canvas API: How to Make 3D WebGL Experiences Fully Searchable — https://webashes.com/html-in-canvas-api/

---

## Search queries used (web search; all recorded)

Round 1: "Google Search Central JavaScript SEO best practices rendering Googlebot" | "Google two-wave indexing JavaScript rendered content 2025" | "Googlebot evergreen Chromium rendering queue budget JavaScript sites" | "Bing Webmaster Tools JavaScript SPA rendering support 2025" | "does Bing execute JavaScript index rendered content" | "Bing crawler JavaScript rendering limitations SEO"
Round 2: "DuckDuckGo index powered by Bing crawler JavaScript rendering" | "OpenAI ChatGPT Search crawler OAI-SearchBot documentation how indexing works" | "Perplexity bot crawling documentation indexing pages AI search" | "Google noscript tag SEO recommendation JavaScript content fallback" | "prerender.io Cloudflare Workers prerender static site SEO interactive map" | "canvas WebGL content SEO not indexable map tiles JavaScript markers"
Round 3: "Bingbot headless Chromium rendering 2024 2025 announcement update" | "Google AI Overviews how content selected indexed crawl Googlebot 2025" | "ChatGPT Search Bing index relationship how search results generated 2025"
Round 4: "Martin Splitt two-wave indexing less role Onely interview rendering" | "DuckDuckGo own search index announcement official help page how it works" | "Bing webmaster guidelines down-level experience JavaScript rich media current text"

Fetched directly: developers.google.com JS SEO basics; bing.com webmaster-guidelines (stub only); developers.openai.com/api/docs/bots; docs.perplexity.ai perplexity-crawlers; developers.google.com AI features; developers.cloudflare.com browser-run pre-render.

---

## Blocked / unverified items

- **Bing Webmaster Guidelines full text**: page is client-side rendered; fetch returned only a stub banner. Content quoted via search-result snippets only. The old "rich media (Flash, JavaScript...)" warning paragraph could not be confirmed as present/absent in the current version. → needs follow-up (try Wayback Machine / Google cache).
- **Bing 2024 "headless Chromium" announcement**: claimed by Crawlix [7]; no primary source found; likely a misdate of the 2019 Edge adoption. Unverified.
- **noscript current status**: no 2025–2026 official Google statement; last data points are 2018–2019 (Mueller vs Illyes). Flagged uncertain.
- **DuckDuckGo JS rendering**: official docs silent; own-index two-pass JS rendering only reported via podcast + secondary news (medium confidence).
- **AI crawler JS execution**: no official OpenAI/Perplexity statement that they execute JS; "raw HTML only" is an industry-aggregated inference [7].
- No PDFs were fetched (per brief). Google's AI Overviews PDF exists at https://search.google/pdf/google-about-AI-overviews-AI-Mode.pdf — cited via search snippet only, full text blocked.

## Coverage status

- Q1 ✅ done (official doc fetched; two-wave history verified via Onely/SERoundtable)
- Q2 ✅ done (Google guidance + noscript history + prerender.io/Cloudflare prerender docs)
- Q3 ⚠️ mostly done (official Bing blog + guidelines snippets; full guidelines text blocked)
- Q4 ⚠️ done with caveats (official DDG help page; own-index effort is secondary-sourced)
- Q5 ✅ done (official Google, OpenAI, Perplexity docs verified by fetch)
- Q6 ✅ done (multiple sources; AI-crawler claim marked as inference)
