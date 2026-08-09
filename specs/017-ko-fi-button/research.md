# Research: Ko-fi Donation Button (feature 017)

Phase 0 output. Each decision records what was chosen, why, and what was considered. Evidence is grounded in repo state and live fetches; none of the repo-side facts are speculative.

## R-1 — Ko-fi official embed standard

- **Decision**: use the official plain-`<a><img>` embed. Link `https://ko-fi.com/M4Q624RYOV`, image `https://storage.ko-fi.com/cdn/kofi3.png?v=6`, rendered height 36 px (CSS px), `?v=6` cache-buster kept verbatim. No Ko-fi widget script.
- **Rationale**: the embed is a static anchor with a single image — zero scripts, zero tracking (FR-008). The `?v=6` query is part of the official CDN URL and must stay.
- **Alternatives considered**: (a) Ko-fi widget script (`ko-fi.com/widgets/widget_2.js`) — rejected, executes third-party JS and adds an external script origin (violates FR-008/FR-009 script-src lock); (b) self-hosting the button image — rejected, duplicates the brand asset and would need a new static file plus publish change, with zero benefit (the CDN is the canonical source and is covered by the image-host allowance).
- **Evidence**: standard embed confirmed in Ko-fi button usage threads (luizdepra/hugo-coder issue #923, "Technically Product" ko-fi button article). Live fetch of the image URL returned HTTP 200, `Content-Type: image/webp`, natural size 580×146 (so the CDN serves WebP regardless of the `.png` name; `img-src` covers any image format). Aspect 580:146 → at `height="36"` the rendered width is ≈ 143 px. `https://ko-fi.com/M4Q624RYOV` answered 403 to a `curl` HEAD — Ko-fi bot protection for non-browser agents; browsers load it normally (verified in quickstart Q2).

## R-2 — Minimal CSP extension for the image host

- **Decision**: extend `img-src` by exactly one origin: `https://storage.ko-fi.com`. New directive: `img-src 'self' data: https://sgx.geodatenzentrum.de https://storage.ko-fi.com`. Update all three policy carriers in lockstep: the `<meta http-equiv="Content-Security-Policy">` tag in `src/site/index.html`, the `SECURITY_HEADERS["Content-Security-Policy"]` string in `workers/map/index.js` (must stay byte-identical to the meta — feature-015 contract: header + meta both apply, intersection), and the policy text in `specs/015-security-audit-housekeeping/contracts/security-headers.md` (policy changes are contract changes — update contract, meta, and header together, per that contract's own rule).
- **Rationale**: the button needs exactly one external resource, the button image. All other directives (`script-src`, `style-src`, `connect-src`, `worker-src`, `font-src`, `default-src`) stay byte-identical — FR-009 of this spec and the feature-015 lock.
- **Alternatives considered**: (a) `img-src *` or a wildcard — rejected, weakens policy beyond need; (b) `connect-src` or `script-src` additions — rejected, nothing connects or executes; (c) no CSP change with a self-hosted image — rejected in R-1.
- **Evidence**: repo grep — the CSP string appears in exactly the meta tag and the Worker header; `deploy-cf.sh verify` and the acceptance tests only assert header *presence* and `script-src 'self'`, none pins the full string, so the extension breaks no existing gate (verified: `test_seo_metadata.py:314` asserts exactly one CSP meta and `script-src` contents only).

## R-3 — Mobile touch target 44×44 and 8 px spacing

- **Decision**: the ko-fi link joins the existing feature-012 touch-target rule group (`#baeume, .surface-toggle, .brightness input[type=range]` → `min-width: 44px; min-height: 44px`). Hit area is enlarged without changing the visual: the 36 px image sits inside an anchor that adds vertical padding (36 + 2×4 = 44 px height); the 143 px-wide image already exceeds 44 px width. Spacing comes from the existing flex `gap: 8px` on `.surface-header` and `.surface-tools` — hit boxes keep ≥ 8 px between them, visual spacing only grows.
- **Rationale**: reuse the locked contract instead of inventing a second convention (FR-004 of this spec, feature 012 FR-003).
- **Alternatives considered**: (a) CSS transform/negative-margin hacks to inflate the hit area — rejected, padding is the boring, robust technique; (b) a larger transparent `<img>` — rejected, alters rendering path.
- **Evidence**: `src/site/style.css` mobile block (lines ~478-487) documents the 44×44/8 px contract and the exact rule group; the `.surface-header` padding/gap rules are read from the same file.

## R-4 — Header packing at 320 px (the binding width)

- **Decision**: the ko-fi link is a direct child of `.surface-header` (NOT inside `.surface-tools`, which is `flex-wrap: nowrap` with `min-width: 200px` on mobile — adding 143+ px there would overflow every width below ~530 px). DOM order: title → tools → ko-fi → toggle, so the chevron stays rightmost (feature-012 "bare arrow at the edge" contract). Flexbox wrap then yields, at ≤ 350 px with the existing `order` override: row 1 `[title, ko-fi, toggle]`, row 2 `[tools]` — measured fit 84 + 151 + 44 + 2×8 gap = 295 ≤ 296 available at 320 px (320 − 2×12 header padding). Above 350 px and below ~533 px: row 1 `[title, tools, toggle]` (min 350 px incl. gaps), row 2 `[ko-fi]` right-aligned; at ≥ 533 px everything fits one row. At most 2 rows everywhere; collapsed strip height = 2×44 + 8 gap + 16 padding = 112 px ≤ 20 % of 568 px (iPhone SE, 113.6 px) — the binding constraint.
- **Rationale**: keeps every 012 invariant (≤ 20 % strip, ≥ 80 % map, no overflow) with the existing wrap machinery and no changes to locked rules.
- **Alternatives considered**: (a) ko-fi inside `.surface-tools` — rejected, nowrap + min-width 200 makes it overflow below ~530 px; (b) a dedicated third row always — rejected, 3 rows break the 20 % budget on 320×568; (c) title-row placement at all widths — rejected, looks odd on desktop; (d) shrinking the brand image below 36 px globally — rejected, the owner provided the default visual; only the ≤ 350 px case MAY reduce to 32-34 px (hit area unchanged) if browser measurement at 320×568 shows the 112 px budget exceeded.
- **Evidence**: computed from `style.css` read at lines 34-127 (header flex, gap, padding) and 405-503 (mobile media queries, `order` overrides, 44×44 group); widths taken from the feature-012/016 smoke matrix (320, 375, 768, 1280, 1920). Exact pixels verified in-browser in quickstart Q5/Q8; if measurement contradicts the math, the ≤ 350 px image-height reduction is the fallback.

## R-5 — External-link safety

- **Decision**: `target="_blank" rel="noopener"`.
- **Rationale**: site pattern — every existing external link in `index.html` (SPIEGEL, CityTreeCover, GitHub, attribution) uses `target="_blank" rel="noopener"`. Prevents the Ko-fi page from controlling the map page (spec edge case). Modern browsers imply `noopener` for `target=_blank`, but explicit matches the site contract.
- **Alternatives considered**: `rel="noopener noreferrer"` — rejected, the site's own links do not use `noreferrer`, and the referrer policy header (`strict-origin-when-cross-origin`) already limits referrer leakage; consistency wins.
- **Evidence**: `src/site/index.html` story section links.

## R-6 — German alt text (language consistency)

- **Decision**: German alt text identifying the donation link: `alt="Baumfläche auf Ko-fi unterstützen"`. The brand visual ("Support me on Ko-fi" painted into the image) stays as provided.
- **Rationale**: FR-006 requires the text alternative to identify the link as donation/support; the site is German (spec edge case "Language consistency" — no raw English-only string unless the brand label is intentionally kept). The visible brand label IS the image content; the alt serves screen readers and the no-image fallback.
- **Alternatives considered**: keep the brand alt "Buy Me a Coffee at ko-fi.com" — rejected, English-only on a German page, and "ko-fi.com" in the alt is redundant with the link destination; a longer descriptive alt ("Spenden-Button: Unterstütze dieses Projekt bei Ko-fi") — acceptable but the short form is on par with the site's other concise alt/labels.
- **Evidence**: spec edge case text; FR-006.

## R-7 — Safe-area insets on mobile

- **Decision**: no new code — the ko-fi link inherits the existing `.surface-header { padding-bottom: max(8px, env(safe-area-inset-bottom)); }` (mobile block), same as the tools it joins. Verification only: notched-device check in quickstart Q8.
- **Rationale**: the button is a header child; the header already carries the safe-area contract (feature 012 FR-007/SC-005).
- **Alternatives considered**: per-element safe-area padding — rejected, redundant with the header rule.
- **Evidence**: `style.css` mobile block, `.surface-header` rule.

## R-8 — Performance and CLS

- **Decision**: `width="143" height="36"` attributes on the `<img>` (rendered CSS-px size matching the R-1 aspect math; `height: auto` NOT used — the attributes reserve the box). No preconnect/preload for the image host. Image is a normal non-blocking `<img>` fetch.
- **Rationale**: reserved dimensions prevent layout shift when the external image arrives (SC-003: never "blank" — alt text shows until the fetch completes); no preconnect keeps the request surface minimal (FR-008, and the perf harness measures first-usuable; an extra DNS/connection hint for one 5-15 KB image is not on the critical path).
- **Alternatives considered**: preconnect to `storage.ko-fi.com` — rejected, single small image, no measurable benefit and an extra connection to a third party; CSS `aspect-ratio` instead of attributes — attributes are the boring, legacy-proof choice.
- **Evidence**: perf budgets from DEVELOPMENT.md (014 SC-008: first usable ≤ 10 s, measured 1.39 s); the image fetch in R-1 was fast (200 in < 1 s from this network). Budgets re-measured in quickstart Q9.

## R-9 — Ko-fi unavailability fallback

- **Decision**: nothing special — plain `<a>` with `<img>`; if the CDN is unreachable the alt text renders and the link still works. No `onerror` handler, no JS.
- **Rationale**: spec edge case: "if Ko-fi page or image CDN unreachable, site must remain fully functional — button plain link no script dependency no blocking request." Inline `onerror` would be blocked by `script-src 'self'` anyway (no 'unsafe-inline'), so a JS fallback is not even available — the no-JS design is the only compliant one.
- **Alternatives considered**: (a) local fallback image on `onerror` — rejected, blocked by CSP and adds a static file; (b) CSS-only fallback (background + hiding broken img) — rejected, over-engineering for a brand asset with stable CDN availability.
- **Evidence**: CSP meta `script-src 'self'` (no unsafe-inline) read from `index.html`.

## Consolidation

| # | Unknown / choice | Decision | Grounded by |
|----|------------------|----------|-------------|
| R-1 | Ko-fi embed form | Plain `<a><img>`, official CDN URL, height 36 | Live fetch (200, 580×146 WebP), embed references |
| R-2 | CSP change | `img-src` += `https://storage.ko-fi.com`, 3 locations lockstep | Repo grep of CSP carriers + gates |
| R-3 | Touch target | Join 012 rule group, padding hit-area | style.css mobile block |
| R-4 | 320 px packing | Header child, DOM title→tools→ko-fi→toggle, ≤ 2 rows | style.css layout math |
| R-5 | New-tab safety | `rel="noopener"` | index.html existing links |
| R-6 | Alt text | German donation text | FR-006, spec edge case |
| R-7 | Safe area | Inherit header rule, verify only | style.css mobile block |
| R-8 | Perf/CLS | width/height attrs, no preconnect | 014 budgets, R-1 fetch |
| R-9 | CDN outage | No-JS design, alt fallback | CSP script-src lock |
