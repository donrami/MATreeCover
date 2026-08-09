# Quickstart: SEO Assessment & Improvement (feature 016)

Validation guide. Run these scenarios in order to prove the feature works end to end. Details live in the [contracts](contracts/) and [data model](data-model.md). This file is the run guide, not the implementation.

## Prerequisites

- Branch `016-seo-improvement`, clean worktree.
- `git`, `bash`, `python3.11`, `.venv` with dev extras (`make bootstrap`), `curl`, `file`.
- For Q2/Q7 (image + parity): `node`, a Chromium build (`CHROME_PATH`, default `/usr/bin/chromium`).
- For Q3 (live fetch) and Q5 (validators): access to the live site or a local `dist/` build (`make publish`).
- A local build of the published bundle is produced by `make publish` into `dist/`.

## Q1 — On-page metadata (US1, FR-002/003/004, SC-002/003)

```text
make publish
.venv/bin/python -m pytest tests/acceptance/test_seo_metadata.py -q
curl -s https://abu-hamad.de/map/ | head -c 2000
```

Expected: acceptance tests green. Raw HTML contains a single title (30–60 chars, not "Baumfläche"), a single meta description (100–160 chars), and a canonical tag matching `https://abu-hamad.de/map/`. The same holds for `/map/impressum` and `/map/attribution` with their own descriptions and canonicals; their titles are unchanged. Values follow [on-page-metadata.md](contracts/on-page-metadata.md).

## Q2 — Link previews (US2, FR-005, SC-005)

```text
curl -sI https://abu-hamad.de/map/og-image.png
file dist/og-image.png
```

Expected: `og:title`, `og:description`, `og:type=website`, `og:url`, `og:site_name`, `og:locale=de_DE`, `og:image`, `og:image:width=1200`, `og:image:height=630`, `twitter:card=summary_large_image` all present in the raw HTML ([link-preview.md](contracts/link-preview.md)). The image fetch returns 200, `image/png`, 1200×630 px, under 1 MB. Manual: share the URL on at least three of Facebook/LinkedIn/X/WhatsApp/Telegram/Discord/Slack; the card shows title, description, and the map image.

## Q3 — Crawler files (US3, FR-008/009/010, SC-006)

```text
curl -sI https://abu-hamad.de/map/robots.txt
curl -s https://abu-hamad.de/map/robots.txt
curl -s https://abu-hamad.de/map/sitemap.xml
```

Expected: `robots.txt` returns 200 `text/plain` with `Disallow:` for `buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson` under `User-agent: *`, and no HTML disallow ([crawler-files.md](contracts/crawler-files.md)). `sitemap.xml` returns 200 XML listing exactly `https://abu-hamad.de/map/`, `/map/impressum`, `/map/attribution`, no `lastmod`, no data files or hashed assets. Open the assessment report and confirm the root-domain `Sitemap:` line and optional disallows are documented as owner-side actions.

## Q4 — Story in the first-visit modal (US1, FR-006, final Clarifications 2026-08-09)

```text
curl -s https://abu-hamad.de/map/ | grep -c 'SPIEGEL\|CityTreeCover\|Datenquellen'
.venv/bin/python -m pytest tests/acceptance/test_seo_metadata.py -q -k story
```

Expected (final Clarifications 2026-08-09): the full story text (story, method, sources, disclaimer) exists exactly once in the raw HTML, inside the first-visit modal — there is no visible section under the map, the map is the only page content. A distinctive story phrase occurs exactly once in the document. The modal shows over the map without scrolling ([visible-content.md](contracts/visible-content.md)). Owner decision: the earlier >= 80 % visible-word and raw-HTML self-sufficiency criteria (SC-004/SC-010) are superseded.

## Q5 — Structured data and CSP (FR-007, SC-007)

```text
.venv/bin/python -m pytest tests/acceptance/test_seo_metadata.py -q -k jsonld
```

Expected: the JSON-LD block parses; `WebSite` (name, url, alternateName, no `SearchAction`) and `Organization` present; `FAQPage`/`LocalBusiness`/`Speakable` absent ([structured-data.md](contracts/structured-data.md)). Manual: open the live page in a browser under the locked CSP (map loads, fonts, popups work) and paste the page URL into the Google Rich Results Test — zero errors. The CSP meta tag is byte-identical to the pre-feature value.

## Q6 — Story modal preserved (feature 007, Clarifications 2026-08-09)

```text
node scripts/smoke-verify.mjs https://abu-hamad.de/map/   # or follow tests/frontend/smoke_us5.md
```

Expected: first visit opens the modal over the map (no scrolling); the modal holds only a link to the attribution page, which opens in a new tab; dismiss persistence is unchanged (dismiss → no modal next visit). No second story copy exists in the DOM.

## Q7 — Nothing regresses (US4, FR-012/013, SC-008)

```text
make check-public && make check-layout && make check-or005
.venv/bin/python -m pytest tests/ -q
bash scripts/perf-measure.sh https://abu-hamad.de/map/
node scripts/parity-render.mjs --archive dist/buildings.pmtiles --out /tmp/parity-016
```

Expected: all gates green, full test suite green, all 8 interactions within the 2 s budget, desktop interaction median <= 123 ms, first usable <= 10 s. Parity render: building values, colors, labels, and popups identical to the previous bundle. The generated `og-image.png` visually matches the current map rendering (regenerate + recommit it if the map render changed, [link-preview.md](contracts/link-preview.md)).

## Q8 — Assessment report reproducible (US5, FR-001, SC-001/SC-009)

```text
# follow verification/seo-assessment-2026-08-09.md, section "Verification"
```

Expected: every listed check reproduces its stated result (fetch page, inspect head, validate sitemap, validate structured data, og:image checks). The report documents current-state evidence, every finding with severity and disposition (fixed / documented / owner-side), the research sources, and the root-domain coordination lines. Search Console / Bing Webmaster properties are verified server-side (DNS or file upload) with zero client-side tracking added.

## Success criteria cross-check

| Criterion | Proven by |
|-----------|-----------|
| SC-001 report committed, checks reproduce | Q8 |
| SC-002 one indexable URL per page | Q1 |
| SC-003 titles/descriptions unique, no bare "Baumfläche" | Q1 |
| SC-004 (superseded, final Clarifications) | — |
| SC-005 previews show title, description, image; og:image 1200×630 < 1 MB | Q2 |
| SC-006 robots.txt + sitemap 200, correct types, 3 URLs, no data files; policy documented | Q3 |
| SC-007 JSON-LD zero errors, only visible content marked up | Q5 |
| SC-008 zero regressions, budgets hold | Q7 |
| SC-009 server-side verification, no client tracking | Q8 |
| SC-010 (superseded, final Clarifications) | — |
