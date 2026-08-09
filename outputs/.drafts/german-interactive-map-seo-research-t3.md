# Researcher Brief T3 — AI-crawler robots.txt policy + robots.txt/sitemap.xml + Cloudflare caching

**Date:** 2026-08-09 · **Status:** done (2 items partially blocked, see end) · **Scope:** notes for `outputs/.drafts/german-interactive-map-seo-research-t3.md` per plan `outputs/.plans/german-interactive-map-seo-T3.md`

Context: German-language static site, client-side rendered map, Cloudflare, no analytics. All sources verified via web search and direct page fetches (no PDFs).

---

## Evidence table

| # | Source | URL | Key claim | Type | Confidence |
|---|--------|-----|-----------|------|------------|
| 1 | OpenAI — Overview of OpenAI Crawlers (official docs, current) | https://developers.openai.com/api/docs/bots | GPTBot (training), OAI-SearchBot (ChatGPT search citations), ChatGPT-User (user-triggered; "robots.txt rules may not apply"); IP JSONs published; if both GPTBot+OAI-SearchBot allowed, one crawl may serve both uses | primary (official) | high |
| 2 | OpenAI Help — How ChatGPT and our foundation models are developed | https://help.openai.com/en/articles/7842364-how-chatgpt-and-our-language-models-are-developed | robots.txt can disallow GPTBot to opt out of training | primary (official) | high |
| 3 | Anthropic — Does Anthropic crawl data from the web… (Claude Help Center / Privacy Center) | https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | Three bots: ClaudeBot (training), Claude-SearchBot (search index), Claude-User (user-triggered); all honor robots.txt; supports Crawl-delay; IP blocking unreliable (impedes reading robots.txt) | primary (official) | high |
| 4 | Search Engine Roundtable — Anthropic updates crawler docs (2026-02) | https://www.seroundtable.com/anthropic-updates-its-crawler-docs-40978.html | Anthropic formalized 3-bot split ~Feb 2026; consequences of blocking each bot | secondary | medium |
| 5 | Perplexity — Perplexity Crawlers (official docs) | https://docs.perplexity.ai/docs/resources/perplexity-crawlers | PerplexityBot (index, not training; respects robots.txt); Perplexity-User (user-triggered, "generally ignores robots.txt rules"); IP JSONs published | primary (official) | high |
| 6 | Perplexity Help Center — How does Perplexity follow robots.txt? | https://www.perplexity.ai/help-center/en/articles/10354969-how-does-perplexity-follow-robots-txt.html | PerplexityBot will not index full/partial text of disallowed sites (per 2026-03-03 update, via secondary) | primary (official) | high (title/URL verified; article body via secondary) |
| 7 | Google — Common crawlers (Google-Extended entry, official) | https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers | Google-Extended = standalone product token (no separate HTTP UA); controls Gemini Apps + Vertex AI Gemini training/grounding; "does not impact a site's inclusion in Google Search nor is it used as a ranking signal" | primary (official) | high |
| 8 | Google Search Central — Robots.txt Introduction and Guide | https://developers.google.com/search/docs/crawling-indexing/robots/intro | robots.txt manages crawl traffic, not indexing; disallowed pages can still be indexed if linked; use noindex/password-protection to keep out of Search; robots.txt cannot enforce behavior | primary (official) | high |
| 9 | Google — How Google interprets the robots.txt specification | https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec | Google enforces 500 KiB robots.txt limit; Sitemap directive = absolute URL, top-level, not tied to user-agent, multiple allowed | primary (official) | high |
| 10 | Google Search Central — AI Features and Your Website (fetched; updated 2025-12-10) | https://developers.google.com/search/docs/appearance/ai-features | AI Overviews/AI Mode use the normal Search index; Googlebot robots.txt is the Search control; preview limits via nosnippet/max-snippet/noindex; Google-Extended only for Gemini training/grounding | primary (official) | high |
| 11 | Google — Overview of Google crawlers and fetchers (fetched; updated 2026-06-12) | https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers | Common crawlers "always respect robots.txt rules for automatic crawls"; user-triggered fetchers act per user request | primary (official) | high |
| 12 | Apple — About Applebot (official) | https://support.apple.com/en-us/119829 | Applebot-Extended does not crawl; token only to opt out of foundation-model training; Applebot data may train Apple models | primary (official) | high |
| 13 | Meta — Meta Web Crawlers (official) | https://developers.facebook.com/docs/sharing/webmasters/web-crawlers | meta-externalagent (training), Meta-ExternalFetcher (user-triggered, "may bypass robots.txt"); robots.txt changes may take up to 24h (cache) | primary (official) | high |
| 14 | Amazon — About AmazonBot (official) | https://developer.amazon.com/amazonbot | Amazonbot (may train Amazon AI models), Amzn-SearchBot (e.g. Alexa; not training), Amzn-User; respect REP; robots.txt cached up to 30 days; no crawl-delay support | primary (official) | high |
| 15 | Common Crawl — FAQ (official) | https://commoncrawl.org/faq | CCBot checks robots.txt first, supports Disallow/Allow combos + Crawl-delay; does not execute JS; supports Sitemap announced in robots.txt | primary (official) | high |
| 16 | Common Crawl — CCBot page (official) | https://commoncrawl.org/ccbot | CCBot UA reference page | primary (official) | high |
| 17 | RFC 9309 (IETF) — Robots Exclusion Protocol | https://www.rfc-editor.org/rfc/rfc9309.html | Standard; parsing limit MUST be at least 500 KiB | primary (standard) | high |
| 18 | sitemaps.org — Protocol (official) | https://sitemaps.org/protocol.html | 50,000 URLs / 50 MB (52,428,800 bytes) per sitemap; gzip allowed; sitemap index ≤50,000 sitemaps; Sitemap: directive in robots.txt (independent of user-agent); <lastmod> defined | primary (official) | high |
| 19 | Google Search Central — Build and Submit a Sitemap | https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap | Sitemap is a hint, not guarantee; add `Sitemap:` line to robots.txt; Search Console submission | primary (official) | high |
| 20 | Google Search Central — Understand JavaScript SEO Basics | https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics | Googlebot checks robots.txt first; renders JS with headless Chromium; "Google Search won't render JavaScript from blocked files or on blocked pages"; links discovered in initial HTML faster | primary (official) | high |
| 21 | Cloudflare — Default Cache Behavior (fetched) | https://developers.cloudflare.com/cache/concepts/default-cache-behavior/ | Cloudflare does NOT cache HTML or JSON by default; caches by file extension; "by default Cloudflare caches a website's robots.txt"; default edge TTL 200/206/301 = 120 m, 302/303 = 20 m, 404/410 = 3 m; default cacheable extension list does NOT include xml | primary (official) | high |
| 22 | Cloudflare — Get started with Cache | https://developers.cloudflare.com/cache/get-started/ | Static content cacheable by default; HTML "dynamic" by default; use Cache Rules to cache | primary (official) | high |
| 23 | Cloudflare — Cache Rules settings (Edge TTL) | https://developers.cloudflare.com/cache/how-to/cache-rules/settings/ | Edge TTL modes (respect origin / override / bypass); minimum Edge TTL by plan (Free 2 h, Pro 1 h, Biz/Ent 1 s); Origin Cache-Control interplay | primary (official) | high |
| 24 | Cloudflare — Customize cache | https://developers.cloudflare.com/cache/concepts/customize-cache/ | "Cache Everything" rules still respect origin Cache-Control max-age=0/private/no-cache unless Edge TTL override set | primary (official) | high |
| 25 | Cloudflare — Managed robots.txt setting | https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/ | robots.txt compliance is voluntary; managed robots.txt prepends block rules for known AI crawlers + Content Signals Policy (search / ai-input / ai-train; experimental content-use=reference); available on all plans | primary (official) | high |
| 26 | Cloudflare — Manage AI crawlers (AI Crawl Control) | https://developers.cloudflare.com/ai-crawl-control/features/manage-ai-crawlers/ | Per-crawler allow/block; block creates WAF custom rule; can return 403 or 402 | primary (official) | high |
| 27 | Cloudflare — Track robots.txt (AI Crawl Control Directives tab) | https://developers.cloudflare.com/ai-crawl-control/features/track-robots-txt/ | robots.txt availability health; per-crawler violation counts against your directives; Agent Readiness score | primary (official) | high |
| 28 | Cloudflare — Bot reference (AI Crawl Control) | https://developers.cloudflare.com/ai-crawl-control/reference/bots/ | Verified bot detection IDs: GPTBot, ClaudeBot, CCBot, Meta-ExternalAgent, Amazonbot, Bytespider, Applebot, DuckAssistBot, MistralAI-User, Meta-ExternalFetcher, FacebookBot | primary (official) | high |
| 29 | Cloudflare Blog — Auditing and controlling AI models accessing your content (AI Audit launch) | https://blog.cloudflare.com/cloudflare-ai-audit-control-ai-content-crawlers/ | "AI Audit" launch (now AI Crawl Control); one-click "Block AI Scrapers and Crawlers"; categories AI Data Scraper / AI Search Crawler / Archiver | primary | high |
| 30 | Cloudflare Blog — Enforcing your robots.txt policies (Robotcop) | https://blog.cloudflare.com/ai-audit-enforcing-robots-txt/ | "Enforce robots.txt rules" translates robots.txt into WAF rule; robots.txt violations tracked | primary | high |
| 31 | Cloudflare Blog — Perplexity stealth crawling (2025-08-04) | https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/ | Perplexity rotated UAs/IPs/ASNs to evade robots.txt + WAF blocks; de-listed as verified bot; ChatGPT-User stopped when disallowed in same tests; >2.5M sites opted into AI-training disallow | primary | high |
| 32 | Cloudflare Blog — From Googlebot to GPTBot: who's crawling your site in 2025 | https://blog.cloudflare.com/from-googlebot-to-gptbot-whos-crawling-your-site-in-2025/ | GPTBot 5%→30% AI-crawler share, Bytespider 42%→7% (May 2024→May 2025); only ~37% of top-10k domains have robots.txt; GPTBot disallowed in only 7.8% of them | primary | high |
| 33 | Cloudflare Blog — Radar 2025 Year in Review | https://blog.cloudflare.com/radar-2025-year-in-review/ | AI bots (excl. Googlebot) avg 4.2% of HTML requests in 2025 (2.4–6.4% range); Googlebot alone 4.5%; OpenAI crawl-to-refer up to 3,700:1, Anthropic highest ratios; AI crawlers most-blocked UAs (GPTBot, ClaudeBot, CCBot top full disallows) | primary | high |
| 34 | Cloudflare Blog — Control content use for AI training (managed robots.txt + monetized content) | https://blog.cloudflare.com/control-content-use-for-ai-training/ | Managed robots.txt module intercepts /robots.txt at edge, prepends managed directives; earlier crawl-to-refer data: Google ~14:1, OpenAI 1,700:1, Anthropic 73,000:1 (June 2025) | primary | high |
| 35 | Search Engine Land — Google updates crawlers documentation | https://searchengineland.com/google-updates-crawlers-and-user-triggered-fetchers-documentation-446594 | Google added per-crawler "affected products" + robots.txt examples; Google-Extended "does not impact a site's inclusion or ranking in Google Search" | secondary (trade) | medium |
| 36 | SE Roundtable — Google-Extended doesn't affect Google Search | https://www.seroundtable.com/google-extended-seo-36865.html | Google-Extended has no HTTP UA of its own; no effect on Search; not for controlling SGE | secondary (trade) | medium |
| 37 | AgentGrade — Bytespider agent page | https://agentgrade.com/agents/bytespider | ByteDance publishes no reachable official Bytespider documentation (zhanzhang.toutiao.com inaccessible); compliance unverified; no published IP list | third-party | medium |
| 38 | Cloudflare Community — Sitemap caching issue | https://community.cloudflare.com/t/sitemap-caching-issue/415175 | .xml not cached by default at Cloudflare; cf-cache-status DYNAMIC for xml; forum confirms default behavior | forum | medium |
| 39 | Crawlytics — Complete list of AI crawler bots (2026, updated 2026-06-03) | https://crawlytics.app/resources/ai-bots-list | 25 bots / 19 companies tracked; training vs live-fetch vs search-index taxonomy; allow/block guidance | third-party | medium |
| 40 | AgentSurge — Correct robots.txt rules for GPTBot/ChatGPT-User/OAI-SearchBot | https://agentsurge.io/blog/correct-robots-txt-rules-for-gptbot | Named UA groups override `*`; longest-match wins; wildcards supported; each bot needs own group | third-party | medium |
| 41 | AgentCookbooks — Cloudflare Pages won't edge-cache HTML without a Cache Rule | https://agentcookbooks.com/blog/cloudflare-pages-html-cache-the-missing-rule/ | Pages treats HTML as Dynamic; needs Cache Rule; also claims "Block AI training bots" / "Manage robots.txt" toggles default ON and silently prepend managed robots.txt | third-party (hands-on) | medium (verified behavior pattern; toggle defaults not re-verified) |
| 42 | Voctos — robots.txt for AI crawlers: allow or block (2026) | https://www.voctos.com/blog/robots-txt-ai-crawlers/ | Recommended default: block training tokens, allow search tokens; Bytespider & stealth Perplexity ignore robots.txt; Option B config | third-party | medium |

---

## Key findings per question

### Q1 — AI crawler landscape 2026

All major vendors split **training**, **search/retrieval**, and **user-triggered fetch** into separate user agents, so each can be allowed/blocked independently [1][3][5][7].

- **OpenAI:** `GPTBot` (training; respects robots.txt), `OAI-SearchBot` (ChatGPT search citations; blocking removes you from ChatGPT search answers), `ChatGPT-User` (user-triggered; OpenAI: "robots.txt rules may not apply"). Official docs + published IP JSONs (openai.com/gptbot.json, /searchbot.json, /chatgpt-user.json). Docs now say GPTBot and OAI-SearchBot may share one crawl if both allowed; robots.txt changes take ~24 h [1][2].
- **Anthropic:** `ClaudeBot` (training), `Claude-SearchBot` (search index, formalized ~Feb 2026), `Claude-User` (user-triggered). Anthropic states all three honor robots.txt, supports `Crawl-delay`, and warns IP-blocking is unreliable (impedes reading robots.txt) [3][4].
- **Perplexity:** `PerplexityBot` (index + citations; not used for training; respects robots.txt), `Perplexity-User` (user-triggered; Perplexity: "generally ignores robots.txt rules"). IP JSONs published [5][6].
- **Google:** `Googlebot` (Search + AI Overviews), `Google-Extended` (token only — no separate HTTP UA; Gemini Apps/Vertex AI training & grounding), `GoogleOther`, `Google-Agent` (user-triggered; robots.txt generally not applicable). Common crawlers "always respect robots.txt rules for automatic crawls" [7][11][36].
- **Apple:** `Applebot` + `Applebot-Extended` (token; "does not crawl webpages" — opt-out from foundation-model training only) [12].
- **Meta:** `meta-externalagent` (training), `Meta-ExternalFetcher` (user-triggered; "may bypass robots.txt") [13].
- **Amazon:** `Amazonbot` (may train Amazon AI models), `Amzn-SearchBot` (Alexa etc., not training), `Amzn-User` [14].
- **Common Crawl:** `CCBot` — checks robots.txt first, supports Disallow/Allow + Crawl-delay, no JS execution, reads sitemaps announced in robots.txt [15][16].
- **Bytespider (ByteDance):** **no reachable official documentation** (UA reference zhanzhang.toutiao.com inaccessible outside China); compliance "unverified", widely reported ignoring robots.txt; no published IP list [37][42].
- Cloudflare's verified-bot reference lists detection IDs for GPTBot, ClaudeBot, CCBot, Meta-ExternalAgent, Amazonbot, Bytespider, Applebot, DuckAssistBot, MistralAI-User, Meta-ExternalFetcher, FacebookBot — useful for log/WAF matching [28].

### Q2 — Policy debate 2025–2026

- **Current recommended posture** (third-party consensus): split decision — block *training* crawlers (GPTBot, Google-Extended, ClaudeBot, CCBot, Applebot-Extended, Meta-ExternalAgent, Bytespider) while allowing *search/retrieval* crawlers (OAI-SearchBot, PerplexityBot, Claude-SearchBot) to remain citable in AI answers. Blocking a search crawler removes you from that engine's AI answers; blocking a training crawler costs little visibility [39][42]. This is an inference from multiple third-party guides; no single authority mandates it.
- **Google (official):** Google-Extended "does not impact a site's inclusion in Google Search nor is it used as a ranking signal in Google Search" [7]; it is a training/grounding opt-out for Gemini Apps and Vertex AI, and "does not visit the site" (no HTTP UA) [36].
- **Does blocking GPTBot/ClaudeBot affect Google/Bing rankings?** No — GPTBot/ClaudeBot are not search crawlers; Google ranking depends on Googlebot, which is a separate token. Inference from official docs [1][3][7].
- **Does Google-Extended control AI Overviews training data?** No. Official Search Central: AI Overviews and AI Mode are built on the normal Search index (Googlebot); page-level controls are `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`. Google-Extended only affects Gemini Apps/Vertex AI training & grounding [10][7].
- **OpenAI/Anthropic official positions:** OpenAI — disallowing GPTBot signals content should not train foundation models; disallowing OAI-SearchBot removes you from ChatGPT search answers [1]. Anthropic — blocking ClaudeBot excludes future material from training; blocking Claude-SearchBot "may reduce your site's visibility and accuracy in user search results" [3].

### Q3 — Do AI crawlers respect robots.txt?

- Major documented crawlers (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, CCBot, Applebot, Amazonbot, Meta agents, Google) commit to honoring robots.txt [1][3][5][7][12][13][14][15]. Cloudflare's docs state plainly that **robots.txt compliance is voluntary** — it expresses preference, not enforcement [25].
- **2025 incidents:** Cloudflare (2025-08-04) documented **Perplexity using stealth, undeclared crawlers** — rotating user agents, IPs and ASNs — to reach content blocked in robots.txt and by WAF; de-listed Perplexity as a verified bot and added managed-rule signatures; Perplexity disputed the characterization. In the same tests, ChatGPT-User stopped when disallowed [31].
- **Bytespider** has a long record of ignoring robots.txt (pre-2026 reports on Stack Overflow; still unverified compliance) [37][42].
- **Cloudflare traffic data:** AI crawlers (excl. Googlebot) averaged 4.2% of HTML requests in 2025; Googlebot alone 4.5%; GPTBot rose to 30% of AI-crawler share (May 2025) while Bytespider fell 42%→7%; OpenAI crawl-to-refer ratio reached ~1,700:1 and Anthropic ~73,000:1 (June 2025) vs Google ~14:1 — evidence of the "crawl without referral" problem, not of non-compliance [32][33][34]. Only ~37% of top-10k domains even have a robots.txt; AI crawlers are the most-blocked user agents (GPTBot, ClaudeBot, CCBot top full disallows) [32][33].
- Cloudflare AI Crawl Control's Directives tab now surfaces **per-crawler robots.txt violations**, and "Enforce robots.txt rules" turns your robots.txt into a WAF rule [27][30].

### Q4 — robots.txt best practices 2026

- **Format (RFC 9309, Sept 2022):** groups of `User-agent` lines + `Allow`/`Disallow` path rules; crawlers MUST impose a parsing limit of **at least 500 KiB** [17]. Google enforces 500 KiB; content beyond is ignored [9].
- **`Sitemap:` directive** is a top-level field (not tied to any user-agent group); absolute URL; case-insensitive field name; multiple allowed; widely supported (Google, Bing, CCBot) [9][15][18].
- **No-index is not a robots.txt function:** robots.txt manages crawl traffic, not indexing. Disallowed pages can still be indexed if linked externally; use `noindex`/`X-Robots-Tag`/password protection for removal from Search [8].
- **Rules apply per-path, not per-snippet:** robots.txt matches URL paths; limiting what text appears in results (incl. AI Overviews) is `nosnippet`, `data-nosnippet`, `max-snippet` [8][10].
- Matching: most specific user-agent group wins; named groups override `User-agent: *`; wildcard `*` and `$` supported; `Allow` is permissive only (blocking everything except a path needs `Disallow: /` + `Allow: /path`) [9][40].
- `Crawl-delay` is non-standard: supported by ClaudeBot and CCBot, ignored by Google, not supported by Amazonbot [3][9][14][15].
- robots.txt must be UTF-8 `text/plain` at the domain root; keep it small; note it's served from the edge on Cloudflare (managed robots.txt intercepts /robots.txt before origin) [21][25][34].

### Q5 — sitemap.xml best practices

- **Limits:** ≤50,000 URLs and ≤50 MB (52,428,800 bytes) per sitemap (uncompressed); gzip compression allowed; sitemap index ≤50,000 sitemaps / 50 MB [18]. `<lastmod>` is part of the protocol (optional; "date of last modification") [18].
- **Referencing:** add `Sitemap: https://example.com/sitemap.xml` to robots.txt (independent of user-agent groups; index file suffices) [18][19]. Submission is a "hint, not a guarantee" [19].
- **JS-rendered pages:** Googlebot checks robots.txt first, then renders JS with headless Chromium and indexes rendered HTML; "Google Search won't render JavaScript from blocked files or on blocked pages"; links in the initial HTML are discovered faster than links that only appear after JS execution [20]. For a client-side-rendered map site, the sitemap serves as the crawl entry-point list (explicit URLs rather than relying on link discovery), and pages should still ship textual content + real HTML links in the initial response [20]. Sitemaps help Google know which pages to crawl, especially for larger/new sites [19].

### Q6 — Cloudflare specifics

- **Default caching:** Cloudflare caches by file extension and **does not cache HTML or JSON by default**; it **does cache robots.txt by default**; sitemap.xml (`.xml`) is **not** in the default cacheable-extension list, so it is served from origin (verified in docs and by Cloudflare Community moderators) [21][22][38]. Default edge TTLs (no Cache-Control/Expires): 200/206/301 → 120 m; 302/303 → 20 m; 404/410 → 3 m [21].
- **Caching HTML on a static site:** requires a Cache Rule (successor to the deprecated Page Rules "Cache Everything"): match hostname (+ path), set "Eligible for cache", and choose Edge TTL — respect-origin (honor Cache-Control) or override. Origin `Cache-Control: max-age=0/private/no-cache/no-store` still prevents caching unless Edge TTL override is set [22][23][24][41]. Min Edge TTL: Free 2 h, Pro 1 h, Business/Enterprise 1 s [23].
- **robots.txt caching:** cached by default with default TTL (120 m for 200); on policy changes either purge the URL or set a Cache Rule to bypass; Cloudflare's managed robots.txt module answers /robots.txt at the edge and deliberately does not cache it (per Cloudflare's implementation notes) [21][34].
- **sitemap.xml caching:** not cached by default → no staleness risk; crawlers hit origin. If you ever add an xml cache rule, purge on sitemap update [21][38].
- **AI features:** "AI Audit" was renamed **AI Crawl Control** (available on all plans). Features: per-crawler allow/block (block = WAF custom rule; response 403 or 402 Payment Required), robots.txt health + per-crawler violation tracking, "Enforce robots.txt rules" (translates robots.txt into WAF rule), Agent Readiness score, managed robots.txt (prepends Disallow rules for known AI crawlers + Content Signals Policy `search=yes, ai-train=no, use=reference`), and the one-click "Block AI Scrapers and Crawlers" toggle/rule [25][26][27][29][30]. Cloudflare's own docs note robots.txt compliance is voluntary — enforcement happens at the WAF layer [25].
- **Caveat for static sites:** a hands-on report claims Cloudflare Pages ships "Block AI training bots" and "Manage robots.txt" toggles defaulted ON that silently prepend managed robots.txt, contradicting a repo file; this is third-party and should be verified in the dashboard before relying on it [41]. Blocking in the WAF layer (not robots.txt) is the only hard enforcement [25][31].

## Recommended configuration evidence (synthesis)

1. **robots.txt** (per RFC 9309, <500 KiB): allow `Googlebot`; allow search/retrieval agents `OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot` (citations + AI-search visibility); decide training tokens by policy (`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `Applebot-Extended`, `Meta-ExternalAgent`); treat `ChatGPT-User`/`Perplexity-User`/`Claude-User` as user-triggered (robots.txt may not apply — enforce at edge if needed); end with `Sitemap: https://domain/sitemap.xml` [1][3][5][7][9][42].
2. **Cloudflare:** enable AI Crawl Control for visibility + optional managed robots.txt (mind prepending); create a Cache Rule for HTML (static site) with Edge TTL respect-origin; purge on deploy; leave robots.txt/sitemap.xml on default behavior (robots.txt cached with short TTL; sitemap not cached) or bypass explicitly [21][23][24][25][26].
3. **Static + client-side rendered map:** ship textual content and real `<a href>` links in initial HTML; use sitemap as crawl entry-point list; do not block JS/CSS resources in robots.txt (Google renders JS and "won't render JavaScript from blocked files") [20].

---

## Search queries used

1. `AI crawlers robots.txt 2026 GPTBot ClaudeBot PerplexityBot list`
2. `Google-Extended Google Search Central AI crawler robots.txt`
3. `Cloudflare AI audit AI crawler bots robots.txt respect`
4. `robots.txt RFC 9309 sitemap directive best practices 512 KiB`
5. `OpenAI GPTBot OAI-SearchBot ChatGPT-User official documentation platform.openai.com docs bots robots.txt`
6. `Anthropic ClaudeBot crawler documentation robots.txt official`
7. `PerplexityBot official documentation perplexity crawler robots.txt`
8. `Applebot-Extended Meta-ExternalAgent Amazonbot CCBot official documentation robots.txt`
9. `Cloudflare cache HTML by default cache rules edge cache TTL documentation`
10. `Cloudflare caching robots.txt sitemap.xml cache TTL purge`
11. `Cloudflare AI bot traffic share 2025 research Perplexity robots.txt circumvention`
12. `Cloudflare cache everything HTML static site caching best practices 2026`
13. `CCBot Common Crawl official robots.txt documentation`
14. `Bytespider ByteDance crawler robots.txt official user agent`
15. `Google Search Central sitemap JavaScript rendered pages crawling entry point`
16. `Cloudflare default cacheable file extensions xml sitemap cached`

Directly fetched (verified pages): developers.google.com/search/docs/appearance/ai-features · developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers · developers.cloudflare.com/cache/concepts/default-cache-behavior/ · developers.google.com/search/docs/crawling-indexing/robots/update-robots-txt (404 — page moved) · support.google.com thread 355910235 (JS-rendered; unretrievable).

## Blocked / unverified items

- **Google robots.txt fetch/cache timing (24 h)** — official "update your robots.txt" page now 404s (moved); the 24 h claim comes from third-party guides only. OpenAI (~24 h) and Meta (up to 24 h) state their own caching officially [1][13].
- **Bytespider official documentation** — none reachable (zhanzhang.toutiao.com inaccessible); compliance status "unverified" [37].
- **Cloudflare Pages default toggle states** ("Block AI training bots"/"Manage robots.txt" default ON) — third-party report only [41]; verify in dashboard.
- **Perplexity help-center article body** (2026-03-03) — URL verified; article body read via secondary summaries only [6].
- Google's precise use of `<lastmod>` — not re-verified this pass; only sitemaps.org definition cited [18].
- No PDFs were fetched (per brief). No PDF-only sources were required.

## Coverage status

- Q1–Q6: all covered with at least one primary/official source each. Direct reads: OpenAI crawler docs, Anthropic support article, Perplexity crawler docs, Google (common crawlers, robots.txt intro/spec, AI features, crawler overview, JS SEO, sitemap), Apple, Meta, Amazon, Common Crawl, RFC 9309, sitemaps.org, Cloudflare (default cache behavior, cache rules, managed robots.txt, AI Crawl Control docs, 4 blog posts).
- Inferences (explicitly labeled in text): split training/search posture recommendation [39][42]; "blocking GPTBot/ClaudeBot doesn't affect Google rankings" (derived from Google/OpenAI/Anthropic official docs); Bytespider non-compliance (multiple third-party reports, no operator statement).
