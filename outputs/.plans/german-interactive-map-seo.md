# Plan: SEO Best Practices 2026 — German Interactive Map Website

- **Slug:** `german-interactive-map-seo`
- **Date:** 2026-08-09
- **Context:** German-language website; static HTML, client-side rendered interactive map (e.g., heat-protection / heat-warning content), hosted on Cloudflare, no analytics installed. Topic clusters span technical SEO, structured data, social previews, AI-crawler policy, Core Web Vitals, E-E-A-T/YMYL, cross-engine JS handling, and German local SEO.

## Key questions

1. **Indexability of JS-rendered map content** — How do Google, Bing, DuckDuckGo, and AI search engines treat client-side JS-rendered content on a static site in 2026? What architecture is recommended (visible static fallback text, progressive enhancement, prerendering) so the map content is indexable while the site stays static?
2. **Schema.org structured data** — Which schema types apply here (WebSite, Dataset, Organization, LocalBusiness)? Which rich results are realistic in 2026? Validation workflow (Rich Results Test / Schema Markup Validator status in 2026)?
3. **Open Graph / Twitter Card link previews** — Best practices for map/dataset pages; dynamic OG images; Cloudflare compatibility; X/Twitter Card status in 2026.
4. **AI-crawler robots.txt policy** — Current (2026) conventions for GPTBot, ClaudeBot, Google-Extended, PerplexityBot, Applebot-Extended, and others: allow vs. block guidance, whether blocking affects Google/Bing rankings, and how to decide posture without analytics.
5. **robots.txt / sitemap.xml best practices** — Format rules, sitemap location/index limits, Cloudflare-specific caching implications (e.g., serving cached robots.txt/sitemap, TTLs).
6. **Core Web Vitals & HTML caching as ranking factors** — 2026 thresholds (INP status), whether CWV remains a ranking factor, and whether HTML caching (Cloudflare cache rules, browser caching, edge caching) influences rankings or is purely performance.
7. **E-E-A-T / YMYL for heat-protection content** — How Google evaluates health/safety content; Impressum (§5 DDG, post-DSA), Datenschutzerklärung, contact/author signals as trust factors; practical on-page signals for a small site.
8. **Bing / DuckDuckGo / AI-search JS handling** — How each indexes JS-rendered pages; DDG's reliance on Bing; AI search engines' crawling/rendering behavior.
9. **German local SEO keywords** — Keyword patterns for heat-protection topics in German ("Hitzeschutz", "Hitzewarnung", local city + service combinations), local SEO signals without analytics, Google Business Profile relevance for a map site.

## Evidence needed

- Google Search Central documentation: JS rendering, robots.txt, XML sitemaps, structured data, Core Web Vitals, E-E-A-T/helpful-content guidance.
- Official crawler bot docs / aggregator (OpenAI GPTBot, Anthropic ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended, Bytespider) + 2025–2026 commentary on AI-crawler robots.txt posture.
- Bing Webmaster Tools docs on JavaScript indexing; DuckDuckGo docs on its Bing-backed index.
- Cloudflare docs: caching (incl. HTML/static asset caching, cache rules), Cloudflare for AI / AI audit features, Workers/prerender options if any.
- schema.org definitions (WebSite, Dataset); Google Search Central structured-data documentation; status of Rich Results Test in 2026.
- Open Graph protocol spec; X/Twitter Card docs and 2026 status (deprecation notes if any).
- German legal/SEO sources on Impressum under §5 DDG (post-DSA), trust signals, and local SEO keyword research (e.g., SISTRIX, Ryte, Searchmetrics, IONOS/Homepage blog material).
- web.dev / Chrome for Developers for CWV thresholds and INP guidance; official statements on ranking-factor status.

## Scale decision

**Scale: 4 parallel research tracks (multi-domain survey).**
Rationale: 9 question clusters spanning current-reality facts (AI crawlers, 2026 CWV status, Rich Results Test status), documentation-heavy topics (schema.org, robots, sitemaps), and regional specifics (German YMYL/Impressum/local SEO). Far exceeds the 3–10 tool-call threshold for direct mode. Not a "what is X" explainer.

Plan: 4 parallel researchers → lead-owned synthesis → mandatory `verifier` citation pass → mandatory `reviewer` verification pass → final deliverable + provenance.

## Task ledger

| # | Task | Owner | Status | Output |
|---|------|-------|--------|--------|
| 0 | Plan artifact | lead | done | `outputs/.plans/german-interactive-map-seo.md` |
| 1 | Researcher briefs T1–T4 | lead | pending (post-approval) | `outputs/.plans/german-interactive-map-seo-T{1..4}.md` |
| 2 | T1: JS indexability (Google rendering) + Bing/DDG/AI-search JS handling | researcher | done (2026-08-09) | `outputs/.drafts/german-interactive-map-seo-research-t1.md` |
| 3 | T2: schema.org WebSite/Dataset rich results + OG/Twitter cards | researcher | done (2026-08-09) | `outputs/.drafts/german-interactive-map-seo-research-t2.md` |
| 4 | T3: AI-crawler robots.txt policy + robots/sitemap best practices + Cloudflare caching | researcher | done (2026-08-09) | `outputs/.drafts/german-interactive-map-seo-research-t3.md` |
| 5 | T4: CWV 2026 thresholds + HTML caching as ranking factor + E-E-A-T/YMYL/Impressum + German local SEO keywords | researcher | done (2026-08-09) | `outputs/.drafts/german-interactive-map-seo-research-t4.md` |
| 6 | Synthesis draft (lead, not delegated) | lead | in progress | `outputs/.drafts/german-interactive-map-seo-draft.md` |
| 7 | Citation pass + URL verification | verifier (mandatory) | pending | `outputs/.drafts/german-interactive-map-seo-cited.md` |
| 8 | Verification/review pass | reviewer (mandatory, after verifier) | pending | `outputs/.drafts/german-interactive-map-seo-verification.md` |
| 9 | Final deliverable + provenance | lead | pending | `outputs/german-interactive-map-seo.md`, `outputs/german-interactive-map-seo.provenance.md` |

## Verification log

- [ ] Plan file exists on disk (this file).
- [x] After approval: briefs T1–T4 written; each researcher brief is self-contained.
- [x] 4 research files exist (verified on disk 2026-08-09; ~11.8k words total); each records ≥3 distinct search queries and URLs.
- [x] Researchers ran in parallel (concurrency 4, failFast false): 4/4 succeeded.
- [ ] Draft exists; every critical claim maps to a source URL or note (no invented numbers).
- [ ] Cited file exists on disk; URLs reachable or marked dead.
- [ ] Reviewer pass completed; FATAL issues fixed; on-disk `rg`/`grep` proof of fixes.
- [ ] Final `outputs/german-interactive-map-seo.md` + provenance exist.
- [ ] Provenance states `Verification: PASS | PASS WITH NOTES | BLOCKED` with missing checks listed.

## Decision log

- **Slug:** `german-interactive-map-seo` (4 words, derived from topic).
- **Scale:** 4 researchers — multi-domain, current-reality-heavy survey. Direct mode rejected because the brief spans >10 distinct tool-call-worthy sub-questions and requires parallel domain coverage.
- **memory_remember:** not available in the visible toolset → skipped; plan stored on disk only (recorded here for provenance).
- **Deliverable location:** `outputs/` (practical best-practices report, not a paper-style draft).
- **PDF policy:** no PDF parsing; use docs/HTML/abstracts/web snippets; mark full-text-PDF-only sources as blocked rather than fetching.
- **Concurrency/fail-fast:** researchers run with `concurrency: 4`, `failFast: false`; verifier runs before reviewer (never in the same parallel call).
