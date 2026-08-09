## 2026-08-08 — security audit and housekeeping (015)
- Secrets audit: full git-history scan (`make check-history`, 91 commits) plus extended tracked-file gate (`make check-public`, P1–P32) against the shared pattern file `scripts/public-patterns.txt`; every historical finding dispositioned in `verification/security-audit-2026-08-08.md`; no live credential found, nothing rotated.
- Deployed surface: security headers + CSP (byte-identical to the meta tag) on every Worker response; deploy verification gains header and unknown-key-404 assertions; endpoint binds loopback by default and rejects bodies over 1 MiB with 413; pod dependencies pinned.
- Supply chain: committed provenance record `src/site/vendor/PROVENANCE.md`; demotiles font origin declared as accepted risk.
- Housekeeping: layout gate (`make check-layout`) enforces the documented tree; root strays relocated into `outputs/` (cited.md, s2_abstracts, info) or deleted with recorded disposition (progress.md); docs (DEVELOPMENT.md, CHANGELOG, feature history) now match reality.

## 2026-08-09 — SEO assessment and improvement (016)
- Committed assessment report `verification/seo-assessment-2026-08-09.md`: before/after evidence, findings with severity + disposition, research decisions D1–D10, reproducible verification, owner-side root-coordination lines, server-side measurement (zero client-side tracking, FR-001).
- On-page metadata on all three pages: descriptive German title (30–60 chars, never the bare "Baumfläche"), unique German meta description (100–160 chars), canonical tag per page.
- Link previews: full Open Graph + Twitter Card set on the map page (`og:locale=de_DE`, `twitter:card=summary_large_image`, declared 1200×630 dimensions) with a committed `src/site/og-image.png` generated from the current map render via the new `scripts/parity-render.mjs --export-og` mode (1200×630, 212 KB).
- Story content (final state, Clarifications 2026-08-09): the first-visit story modal shows over the map without scrolling and holds the full story text (feature 007 content restored: story, links, Methode, Datenquellen, Genauigkeit) as the single DOM copy; there is no visible section under the map — the map is the only page content. Owner decision: the visible-content SEO criteria (FR-006 visibility, SC-004/SC-010) are superseded for the story text.
- Structured data: inline JSON-LD `WebSite` + `Organization` (no `FAQPage`/`LocalBusiness`/`Speakable`, no `SearchAction`); CSP untouched (data block per HTML spec §4.12.1).
- Crawler files: `/map/robots.txt` (three data-file disallows, no HTML disallow) and `/map/sitemap.xml` (exactly three canonical URLs, no `lastmod`); root-domain coordination documented owner-side.
- Regression sweep: 173 tests green, gates clean (public/layout/or005/history), perf budgets hold (first usable 376 ms, interactions ≤ 14 ms median), parity property samples identical, hashed-bundle contract CSP byte-identical.
- Deployed 2026-08-09 (final version `6d911d61-233c-453d-a858-0098342be1af`): FR-013/FR-014 gates PASS; HTTP→HTTPS scheme redirect live (`http://abu-hamad.de/map/` → 301 → https); modal verified over the map with the full story, no scrolling, nothing under the map; live verification: all three pages' metadata, robots.txt 200 text/plain, sitemap.xml 200 XML, og-image.png 200 PNG 1200×630 (211,775 B); live perf cold LCP 444 ms / CLS 0 / 5 interactions median 13–14 ms; deploy record `validation/deploy-20260809-140623.json`; quickstart Q1–Q8 recorded in the assessment report.

# CHANGELOG

## 2026-08-08 — performance fixes (014)
- Repeat visits: PMTiles archives now served with `public, max-age=86400, stale-while-revalidate=604800, no-transform` (browser + edge cacheable); static assets ship with content-hashed filenames and `immutable` caching; only the HTML revalidates per visit.
- Main-thread load: initial render without cross-fade (`fadeDuration: 0`) and simplified low-zoom building geometry (`-S 10 --simplify-only-low-zooms`). Median mobile TBT 6310 ms to 2790 ms (−56 %). Visual parity gates pass (rendered counts, properties, screenshots at z10-z18).
- Critical path: stylesheets inlined into the HTML (no render-blocking stylesheet requests), map library preloaded, basemap origin preconnected, favicon added (no more 404).
- Verification: committed perf harness (scripts/perf-measure.sh, perf-probe.mjs, parity-render.mjs), publish hashing engine with unit tests, full suite green, deploy gates extended with a pmtiles cache-control check.

## 2026-08-08 — popup comparative context (013)
- Building popup: headline tree-share value ("Baumanteil im 60-m-Umkreis"), 30 % threshold badge ("erreicht"/"verfehlt"), district and city comparison lines with signed pp delta and assessment word, metric footnote.
- District popup: name header, mean headline, rank "Platz X von 38", quartile band badge, city comparison, existing building-count and below-30 % lines kept, metric footnote.
- Rank/quartile computed client-side once at map load from the full 38-district set with deterministic tie-break; graceful degradation when data is missing (building without value, district without mean, stale city stats).
- Visual hierarchy header → headline → badge → context → footnote, color always paired with a text label, mobile fit via internal scroll and width clamp at 360 px. Interaction model unchanged (FR-015).

## 2026-08-06 — tree-canopy-30-heat literature review
- Wrote plan to outputs/.plans/tree-canopy-30-heat.md.
- Verified primary sources: Konijnendijk 2023 (3-30-300; 30% rests on Astell-Burt & Feng health evidence, Ziter 40% cited for heat), NGBS ICC 700-2020 (≥30% building-wall shading, primary PDF), Ziter 2019 PNAS (≥40% threshold), Iungman 2023 Lancet (30% target → 0.4°C, 2644 deaths), Ouyang 2020 (20–30% efficiency optimum), Li 2023 Nanjing (25–45% by building height), Ettinger 2024 (no threshold), Krayenhoff 2021 (0.3°C/10%), Zaerpour 2025 (SUHI 2× overestimate; −1.5°C at +30%).
- Research evidence brief: outputs/tree-canopy-30-heat-research-1.md (39 items; low-confidence items excluded from final).
- Draft: outputs/tree-canopy-30-heat.md; chart: outputs/tree-canopy-30-heat-cooling.png.
- Next: verifier pass on citations/URLs, reviewer pass, provenance file.
- 2026-08-06: verifier + reviewer passes done (0 dead URLs, 0 FATAL). Fixed: BMWSB Hitzeschutzstrategie 2025 adopts Iungman 30% (German lineage added), Astell-Burt graded-gradient nuance, Venter 6-fold SUHI, Kalkstein scenario bounds, EU NRL wording, NGBS credit framing, provenance file created. Final artifacts verified on disk.
