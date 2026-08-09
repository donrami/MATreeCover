# Contract: On-page metadata (feature 016)

Requirement: FR-002/003/004 (US1, SC-002/003). Subject: `<title>`, `<meta name="description">`, `<link rel="canonical">` on the three pages. Implementation: `src/site/index.html`, `src/site/impressum.html`, `src/site/attribution.html`. Enforcement: `tests/acceptance/test_seo_metadata.py` parses raw HTML from `dist/`.

## Per-page contract

| Page | Canonical URL | Title | Meta description |
|------|---------------|-------|------------------|
| map | `https://abu-hamad.de/map/` | 30–60 chars, German, unique, descriptive of what the map shows and where. Never the bare "Baumfläche" (research R-002: vague titles get rewritten). Example candidate (finalized in tasks phase): "Baumfläche in Mannheim: Karte des Baumanteils an jedem Gebäude" (59 chars). | 100–160 chars, German, unique, covers the map's content (what is shown, how it was made, accuracy note). |
| impressum | `https://abu-hamad.de/map/impressum` | Keep existing: "Impressum – Mannheim Baumfläche" (unchanged, FR-003). | 100–160 chars, German, unique, describes the legal page (publisher/contact summary per § 5 DDG). |
| attribution | `https://abu-hamad.de/map/attribution` | Keep existing: "Datenquellen – Mannheim Baumfläche" (unchanged, FR-003). | 100–160 chars, German, unique, describes data sources (DOP20/LGL, GDI-MA boundary, model reuse) and the accuracy disclaimer. |

## Rules

1. **Exactly one indexable URL per page** (SC-002). The canonical tag value is the absolute canonical URL, byte-equal to the row above. `/map/index.html` already 307-redirects (research D1), so the tag is the standard signal, not a duplicate-content fix. `www`/no-trailing-slash variants 301 to the canonical (existing Worker behavior, unchanged).
2. **Single tag per page**: exactly one `<title>`, one `meta[name=description]`, one `link[rel=canonical]`.
3. **Length rules** are hard constraints for the copy in the tasks phase. Title 30–60 characters. Description 100–160 characters. The acceptance test measures the decoded text length with `len()`, not the HTML source.
4. **German and unique**: all copy German. No two pages share a title or description. No page has the bare title "Baumfläche".
5. **`lang="de"` stays** on all three pages (already present).
6. **No other head change**: charset, viewport, CSP meta, stylesheet links, and preload/preconnect (feature 014) stay exactly as they are. New tags are additive only (FR-012).
7. **impressum/attribution titles are kept** (FR-003). Only descriptions and canonicals are added to those pages.

## Machine checks (acceptance test)

- Raw `dist/index.html`: title length in [30, 60], description length in [100, 160], canonical == `https://abu-hamad.de/map/`, title != "Baumfläche".
- Raw `dist/impressum.html` and `dist/attribution.html`: title preserved verbatim, description length in [100, 160], canonical == row above.
- All three titles pairwise distinct. All three descriptions pairwise distinct.
- No page has more than one of each tag.

## Regression notes

- Publish pipeline must not content-hash these files. Hashing applies only to `main.js`/`style.css`/`style.json`/`vendor/*` (feature 014 contract).
- The map page's `h1` ("Baumfläche") stays. The title change does not touch visible UI (FR-012).
- Copy decisions land in the tasks phase. Changing copy later is a normal edit, not a contract change, as long as the length/uniqueness rules hold.
