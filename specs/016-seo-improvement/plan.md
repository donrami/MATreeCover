# Implementation Plan: SEO Assessment & Improvement

**Branch**: `016-seo-improvement` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/016-seo-improvement/spec.md`

## Summary

Assess the live map site's search-engine and link-sharing visibility, then close the highest-impact gaps without touching the map itself (values, colors, labels, popups, interactions). Current state: 10-character title "Baumfläche", no meta description, no canonical, no Open Graph/Twitter Card, no structured data, and the only informative text (story, method, sources, accuracy) lives inside a `hidden` story dialog — invisible to non-JS crawlers.

Deliverables: (1) committed assessment report (`verification/seo-assessment-2026-08-09.md`) with before/after evidence; (2) on-page metadata on all three pages (title, meta description, canonical); (3) full Open Graph + Twitter Card set with a 1200×630 preview image generated from the current map rendering; (4) a visible, crawlable content section (single DOM copy — modal scrolls to it, feature 007 preserved); (5) JSON-LD WebSite/Organization markup (no FAQPage/LocalBusiness/Speakable — research D3); (6) `/map/robots.txt` + `/map/sitemap.xml`; (7) root-domain `robots.txt` coordination documented owner-side (blog origin, E-004). Zero client-side tracking (FR-001 preserved); server-side search-engine property verification only.

## Technical Context

**Language/Version**: HTML/CSS/vanilla JS frontend (no build tool), Python 3.11 offline pipeline, Cloudflare Worker (`workers/map/index.js`).

**Primary Dependencies**: none new. Vendored MapLibre GL JS 5.7.1 / pmtiles 4.4.0 unchanged (PROVENANCE.md untouched). Preview-image generation reuses committed `scripts/parity-render.mjs` (node + Chromium, already the repo's rendering/parity tooling).

**Storage**: static bundle — `src/pipeline/publish.py` `STATIC_FILES` tuple → `dist/` → `dist-assets/` → Worker assets binding; large data files stay in R2. New files (`robots.txt`, `sitemap.xml`, `og-image.png`) join `STATIC_FILES`; they MUST NOT enter the content-hash set (feature 014 `hashed-bundle` contract — hashed filenames would break URLs in `og:image`, sitemap, and bots' cached copies).

**Testing**: pytest suites (`tests/acceptance|pipeline|endpoint`); governance gates `make check-public` / `check-layout` / `check-or005` / commit checks; perf harness `scripts/perf-measure.sh`; parity `scripts/parity-render.mjs`; smoke `scripts/smoke-verify.mjs` + `tests/frontend/*.md`. New raw-HTML assertions land as acceptance tests (`tests/acceptance/test_seo_metadata.py`).

**Target Platform**: static bundle served by Cloudflare Worker at `https://abu-hamad.de/map/` (canonical, trailing slash); `www`/no-trailing-slash variants 301 to it; literal `/map/index.html` already 307-redirects (research D1). Only other pages: `/map/impressum`, `/map/attribution`. Domain root and all non-`/map/*` paths belong to the blog origin (E-004). German-only content; no `hreflang`.

**Project Type**: web (static frontend + Cloudflare Worker + offline Python pipeline).

**Performance Goals**: unchanged budgets (feature 014, SC-008) — 8 interactions ≤ 2 s, desktop interaction median ≤ 123 ms, first usable ≤ 10 s. New work is static text/JSON-LD/meta tags only: no new JS on the interaction path, no new render-blocking resources. The visible content section adds static DOM text; CWV (LCP/CLS) must not regress — verified by the perf harness.

**Constraints**:
- CSP locked (feature 015): no header/meta change. JSON-LD is an inline `<script type="application/ld+json">` data block — per HTML spec §4.12.1 data blocks are not script-executed and `script-src 'self'` does not apply (decision D1); verified in browser + Rich Results Test in quickstart.
- Hashed-bundle contract (feature 014): only `main.js`, `style.css`, `style.json`, `vendor/*` get content hashes; the three new static files must stay unhashed.
- FR-001 (no analytics, no application server): verification is server-side only (DNS/file-based Search Console + Bing Webmaster); no client-side tags.
- `og:image` must be static (not a dynamic endpoint), PNG or JPG, 1200×630 (1.91:1), < 1 MB, visually matching the current map rendering — regenerate when the map render changes (freshness edge case).
- Sitemap staleness: no hand-written `lastmod` (either omit it or use the publish timestamp; never claim a date that is not true).
- Robots.txt scope: crawlers only honor the domain-root `/robots.txt` (blog origin). The map-path file is informational/direct-submission; the authoritative root file needs owner coordination, documented in the assessment report (FR-010), not deployed from this repo. Cloudflare caches `robots.txt` by default (120-min edge TTL for 200 responses without cache-control — research D5) — noted for the owner-side purge rule.
- AI-bot policy: already enforced at zone level (research D1/D5); the map-path file disallows the three data files for ALL user agents, does not duplicate the zone policy, and does not block HTML pages.

**Scale/Scope**: 3 HTML pages, 2 crawler-facing files, 1 preview image, 1 JSON-LD block, 1 visible content section, 1 committed assessment report, 6 contracts, 1 new acceptance test module.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The repository ships no standalone constitution file; governing rules are the documented constraints in DEVELOPMENT.md (OR-001…OR-005, FR-001, FR-010, FR-013/FR-014, SC-005/SC-008 precedent), established in features 014/015.

| Gate | Status | Evidence |
|------|--------|----------|
| OR-001 (pipeline peak RSS < 12 GiB) | PASS | No pipeline compute changes. New files are small text + one PNG; publish copies them like other STATIC_FILES. |
| OR-003 (no local GPU) | PASS | `og:image` rendered from committed PMTiles via node/Chromium parity tooling (same class as existing parity checks); no model inference anywhere. |
| OR-004 (one commit per accepted spec/plan/slice) | PASS | Plan committed via `make commit-plan`; implementation lands in slices with own commits. |
| OR-005 (no `*.tif` / `*.pmtiles` / > 50 MiB geojson tracked) | PASS | New tracked files: HTML/XML/text edits, one PNG < 1 MB, docs. `data/` stays gitignored. |
| FR-001 (no analytics, no application server) | PASS | Verification is server-side only (DNS/file-based Search Console/Bing Webmaster). No client-side tracking added. |
| FR-010/FR-003 (015: `check-public` clean) | PASS | New copy is German prose and metadata; no personal paths, credentials, or internal references. Gate must stay green; synthetic-pattern test unaffected. |
| FR-009/FR-011 (015: `check-layout`) | PASS | All new files land in already-documented locations (`src/site/`, `tests/acceptance/`, `verification/`, `specs/016-seo-improvement/`); no new top-level entries, manifest unchanged. |
| CSP (015, locked) | PASS | No CSP change. JSON-LD is a data block (`application/ld+json`), not subject to `script-src 'self'` (HTML spec §4.12.1; decision D1). Quickstart verifies page loads and validators pass under the locked CSP. |
| SC-005/SC-008 (014: interaction budgets + visual parity) | PASS | Static text/metadata only — no interaction-path code change; perf harness + parity render prove budgets and identical map rendering. |
| FR-012/FR-013 (015: zero user-visible change) | PASS* | The feature's contract IS a user-visible text change (visible story section replaces the hidden dialog as the single copy source). The locked constraints — map values, colors, labels, popups, interactions, caching semantics, security headers, hashed-bundle contract — remain unchanged; modal dismiss-persistence behavior preserved (spec Clarifications 2026-08-09). |

*The visible-text addition is the scoped intent of this feature (FR-006), not a regression; every other locked surface stays byte-identical.

Re-check after Phase 1 design: all gates still PASS; no violations. Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/016-seo-improvement/
├── plan.md              # this file (plan command output)
├── research.md          # Phase 0: decisions D1–D8, scoped research R-001…R-008, verifier evidence
├── data-model.md        # Phase 1: entities, invariants, transitions
├── quickstart.md        # Phase 1: validation scenarios Q1–Q8
├── contracts/           # Phase 1: interface contracts
│   ├── README.md
│   ├── on-page-metadata.md   # FR-002/003/004: title, description, canonical per page
│   ├── link-preview.md       # FR-005: Open Graph + Twitter Card + og:image
│   ├── visible-content.md    # FR-006: visible section, single DOM copy, ≥80 % rule
│   ├── structured-data.md    # FR-007: JSON-LD WebSite/Organization (+ optional Dataset)
│   ├── crawler-files.md      # FR-008/009/010: robots.txt, sitemap.xml, root-domain coordination
│   └── assessment-report.md  # FR-001/011: report contract + server-side verification
└── tasks.md             # Phase 2 output (NOT created by the plan command)
```

### Source Code (repository root)

```text
src/site/
├── index.html           # + meta description, canonical, OG/Twitter tags, JSON-LD,
│                        #   visible content section (single story copy; modal scrolls to it)
├── impressum.html       # + meta description, canonical (title kept)
├── attribution.html     # + meta description, canonical (title kept)
├── robots.txt           # NEW: data-file disallows (all user agents), zone policy documented
├── sitemap.xml          # NEW: exactly 3 canonical URLs, no lastmod staleness
├── og-image.png         # NEW: 1200×630 map preview (generated via parity tooling, committed)
└── vendor/              # unchanged (PROVENANCE.md untouched)

src/pipeline/publish.py  # STATIC_FILES += robots.txt, sitemap.xml, og-image.png (unhashed)

scripts/
├── parity-render.mjs    # reused; gains og:image export mode (1200×630 viewport render)
└── (other gates unchanged)

tests/acceptance/
└── test_seo_metadata.py # NEW: raw-HTML assertions (title/desc/canonical/OG, robots, sitemap,
                         #   ≥80 % visible words, JSON-LD parses, CSP-compatible)

tests/frontend/
└── smoke_us5.md         # updated: story modal now opens/scrolls to the visible section

verification/
└── seo-assessment-2026-08-09.md  # NEW: committed assessment report (FR-001)
```

**Structure Decision**: single flat project (static frontend + worker + pipeline + gates), no new top-level directories, no new packages — same decision as features 014/015. The report joins the established evidence home `verification/`; the new test module joins `tests/acceptance/` next to the other surface gates (`test_layout.py`, `test_public_hygiene.py`); assets join `src/site/` where `publish.py` already copies from. All paths are already documented in DEVELOPMENT.md's layout section, so `check-layout` needs no manifest change.

## Complexity Tracking

No constitution violations. No complexity justification needed.
