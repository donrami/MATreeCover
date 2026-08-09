# Contract: Assessment report (feature 016)

Requirement: FR-001/011 (US5, SC-001/SC-009). Subject: the committed SEO assessment report and the server-side verification method. Implementation: `verification/seo-assessment-2026-08-09.md` (new file). Enforcement: review + quickstart Q8 reproducibility.

## Report contract

The report is the feature's audit deliverable. A maintainer six months out must be able to read it and reproduce every claim.

| Section | Required contents |
|---------|-------------------|
| Current state | Evidence per page, fetched before the change: raw HTML state (title, description, canonical, OG tags, JSON-LD, visible text) with the fetch date. Include the live-site baseline (spec assumption: site unverified in Search Console, no historical analytics). |
| Findings | Each finding with a severity (high / medium / low) and a disposition: `fixed` (changed in this feature), `documented` (deliberately left, rationale recorded), `owner-side` (action for the domain owner, e.g. root robots.txt). No finding without a disposition (SC-001). |
| Research summary | The scoped research R-001…R-009 and decisions D1–D10 from `specs/016-seo-improvement/research.md`, with the source list. |
| Verification | Reproducible before/after checks: exact commands and expected output for each (fetch page, inspect head, validate sitemap, validate structured data, og:image checks). Each listed check must reproduce (SC-001). |
| Root coordination | Exact lines for the blog-origin `robots.txt` (FR-010): the `Sitemap:` line, optional data-file disallows, and the Cloudflare 120-min `robots.txt` edge-cache purge note (research D5). Marked owner-side, not deployed from this repo. |
| Tradeoffs | AI-bot policy side effect: disallowing the data files may reduce AI-assistant citations of the page. Recorded as an owner-visible tradeoff. The default is data files blocked for all bots, HTML pages accessible (FR-008). |
| Measurement | Server-side only (FR-001/011): Cloudflare logs for traffic evidence; Search Console and Bing Webmaster properties verified via DNS record or file upload. Zero client-side tracking added. |

## Verification method (server-side, FR-011/SC-009)

- Search Console and Bing Webmaster support DNS-record or file-based verification. No HTML tag or client script is used, so no analytics or tracking is introduced (FR-001).
- Traffic evidence comes from existing server-side signals (Cloudflare logs) and from crawl statistics in the verified properties. The report states this explicitly.
- The report's verification section lists the exact commands from quickstart Q8. Every listed check must reproduce its stated result.

## Machine checks

- The report exists at `verification/seo-assessment-2026-08-09.md` and contains the section headings above (light acceptance assertion: file exists, sections present).
- Each finding row has a severity and one of the three dispositions (review check in Q8).

## Regression notes

- The report joins the established evidence home `verification/` (same pattern as `verification/security-audit-2026-08-08.md`, feature 015). No layout-manifest change is needed (the directory is already documented).
- The report is committed with the feature, not after it. Before/after evidence is captured at implementation time and written into the committed document.
