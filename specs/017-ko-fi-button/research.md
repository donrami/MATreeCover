# Research: Ko-fi Donation Button (feature 017)

Phase 0 output. Each decision records what was chosen, why, and what was considered. Evidence is grounded in the repo state and live fetches; no repo-side fact is speculative.

**Session note (2026-08-09, revised)**: the owner judged the header placement too prominent and re-decided the placement in the clarification session: the button moves from the surface header to the surface panel/sheet **footer**, is visible **only when the surface is expanded** (hidden when collapsed), and its accessible name is the short German label **"Unterstützen"** (spec `## Clarifications`, FR-001, FR-006). A header-based implementation had already landed (markup, CSS, CSP, tests); this revision relocates it.

## R-1 — Ko-fi official embed standard

- **Decision**: use the official plain-`<a><img>` embed. Link `https://ko-fi.com/M4Q624RYOV`, image `https://storage.ko-fi.com/cdn/kofi3.png?v=6`, rendered height 36 px (CSS px), `?v=6` cache-buster kept verbatim. No Ko-fi widget script.
- **Rationale**: static anchor + single image — zero scripts, zero tracking (FR-008). `?v=6` is part of the official CDN URL and stays.
- **Alternatives considered**: (a) Ko-fi widget script (`ko-fi.com/widgets/widget_2.js`) — rejected: third-party JS adds an external script origin and violates FR-008/FR-009 (`script-src` lock); (b) self-hosting the button image — rejected: duplicates a brand asset, requires a new static file plus a publish change, zero benefit (the CDN is already covered by the image-host allowance).
- **Evidence**: standard embed confirmed in Ko-fi button usage threads (luizdepra/hugo-coder issue #923, "Technically Product" ko-fi button article). Live fetch of the image URL returned HTTP 200, `Content-Type: image/webp`, natural size 580×146 (the CDN serves WebP regardless of the `.png` name; `img-src` covers any image format). Aspect 580:146 → `height="36"` renders ≈ 143 px wide. `https://ko-fi.com/M4Q624RYOV` answers 403 to `curl` HEAD — Ko-fi bot protection for non-browser agents; browsers load it normally (verified in quickstart Q2).

## R-2 — Minimal CSP extension: image host (already landed, no further change)

- **Decision**: `img-src` gains exactly one origin, `https://storage.ko-fi.com`, in all three policy carriers. This change **already landed** in the earlier header implementation and is placement-agnostic — the footer relocation adds no further CSP change (FR-009).
- **Rationale**: the button renders its visual from Ko-fi's image CDN in any placement; the feature-015 lock allows images only from `'self'`, `data:`, and the LGL basemap host, so the CDN host must be allowed. The scoped change is one origin, one directive, three files in lockstep (contract `csp-image-host.md`).
- **Alternatives considered**: (a) `img-src *` or a wildcard — rejected, weakens the policy beyond need; (b) `connect-src`/`script-src` additions — rejected, nothing connects or executes; (c) no CSP change with a self-hosted image — rejected in R-1.
- **Evidence**: repo grep — the CSP string appears in exactly three places, all byte-identical and all already containing `https://storage.ko-fi.com` in `img-src`: the meta tag in `src/site/index.html`, `SECURITY_HEADERS["Content-Security-Policy"]` in `workers/map/index.js`, and the policy block in `specs/015-security-audit-housekeeping/contracts/security-headers.md` (with its allowlist row `storage.ko-fi.com | Ko-fi donation button image (feature 017)`). The existing acceptance gates only assert header presence and `script-src 'self'`, not the full string, so the extension breaks no pinned assertion (verified: `test_seo_metadata.py:314` asserts only the CSP meta `script-src` contents).

## R-3 — Mobile touch target 44×44, 8 px spacing

- **Decision**: the `.ko-fi` link keeps its padding-based hit area (36 px image + 2×4 px vertical padding = 44 px height; the 143 px-wide image already exceeds 44 px width) and stays a member of the feature-012 mobile touch-target rule group (`#baeume, .surface-toggle, .brightness input[type=range]` → `min-width: 44px; min-height: 44px`). In the footer, the ≥ 8 px spacing to adjacent interactive content is provided by `.surface-body-inner`'s flex `gap: 12px` plus the footer's own padding — the only adjacent interactive element is the legend-note link ("Details unter Datenquellen").
- **Rationale**: reuse the locked contract instead of inventing a second convention (FR-004 spec, feature 012 FR-003). The spacing source changes from the header flex `gap: 8px` to the body/footer gap — still ≥ 8 px, still no new rule.
- **Alternatives considered**: (a) CSS transform/negative-margin hacks to inflate the hit area — rejected, padding is the boring, robust technique; (b) a larger transparent `<img>` — rejected, alters the rendering path.
- **Evidence**: `src/site/style.css` mobile block documents the 44×44/8 px contract and the exact rule group; `.surface-body-inner { gap: 12px }` read from the same file (base block).

## R-4 — Footer placement: sticky bottom of the surface body (revised)

- **Decision**: the `.ko-fi` anchor moves out of `.surface-header` into a new `<footer class="surface-footer">` that is the **last child of `.surface-body`** (sibling after `.surface-body-inner`), with `position: sticky; bottom: 0;`, centered (`display: flex; justify-content: center`), `border-top: 1px solid var(--subtle)` and `background: var(--panel-bg)` so body content scrolls beneath it. Visibility follows the existing feature-012 collapse machine: `.surface-body` gets `max-height: 0; overflow: hidden` under `#surface.is-collapsed`, so the footer is **automatically hidden when collapsed** and shown when expanded (FR-001). Sticky keeps it visible **without scrolling** whenever the body is expanded, even when the city panel makes content taller than the sheet (FR-001 "without scrolling").
- **Rationale**: the owner's re-decision (spec Clarifications: footer, expanded-only, no donation chrome in the header). Direct-child-of-scroll-container is the robust sticky pattern; no header wrap math, no order overrides, and no ≤ 350 px image-shrink fallback are needed anymore — the footer has the full body width (292 px available at 320 px, the 143 px image fits trivially), so the previous header-packing machinery is deleted rather than adapted.
- **Alternatives considered**: (a) keep the button in the header — rejected by the owner (too prominent); (b) footer inside `.surface-body-inner` as a flex child — rejected: sticky is less obvious from inside a non-scroll container and inherits the inner's padding/gap; (c) static footer at the content end — rejected: with the city panel open the button would scroll below the fold and violate "without scrolling"; (d) dedicated collapsed-state chrome (e.g. a small icon in the header when collapsed) — rejected in the clarification session (owner: hidden when collapsed, full banner in the footer when expanded).
- **Evidence**: `src/site/index.html` surface markup read (header, `#surface-body`, `#surface-body-inner` with `#legend` and `#city-panel`); `style.css` collapse rules (`#surface.is-collapsed .surface-body { max-height: 0; opacity: 0; transform: translateY(12px); overflow: hidden; border-top: none }`) and the 680 px/350 px media blocks containing the now-obsolete `.ko-fi` order/shrink rules; `main.js` — desktop removes `is-collapsed` at ≥ 768 px (expanded by default), mobile stays collapsed by default, `wireSurfaceToggle` flips the class; popup-clearance padding uses `surface.offsetHeight`, so the footer height is picked up automatically — no JS change.

## R-5 — External-link safety

- **Decision**: `target="_blank" rel="noopener"`.
- **Rationale**: the site pattern — every existing external link in `index.html` (SPIEGEL, CityTreeCover, GitHub, attribution) uses `target="_blank" rel="noopener"`. Prevents the Ko-fi page from controlling the map page (spec edge case). Modern browsers imply `noopener` for `target="_blank"`, but the explicit attribute matches the repo and the acceptance test.
- **Alternatives considered**: `rel="noreferrer"` — rejected, `noopener` is the established site convention and the stricter `noreferrer` adds no contract the site uses elsewhere.
- **Evidence**: `index.html` external links.

## R-6 — Accessible name: "Unterstützen" (revised)

- **Decision**: `alt="Unterstützen"` on the `<img>`. The anchor's accessible name is computed from the image's alt text, so the accessible name is exactly **"Unterstützen"** — the short German label the owner chose (spec Clarifications Q3; FR-006/US3). This replaces the earlier `alt="Baumfläche auf Ko-fi unterstützen"`.
- **Rationale**: FR-006 requires an accessible name identifying the donation/support link; the owner explicitly selected the short German label. The visible banner image keeps Ko-fi's standard English brand visual; the accessible name is deliberately not derived from it (spec Edge Cases, "Language consistency").
- **Alternatives considered**: descriptive German ("Unterstütze das Projekt auf Ko-fi") — rejected by the owner's choice (short label); English brand label ("Buy Me Coffee at ko-fi.com") — rejected, English-only on a German page.
- **Evidence**: spec `## Clarifications` (Q3 answer) and FR-006; the acceptance test's word list already contains `unterstütz`, so the existing German-word check stays green while the contract is tightened to an exact match.

## R-7 — Safe-area insets on mobile

- **Decision**: no new code — the footer inherits the mobile sheet rule `#surface { padding-bottom: env(safe-area-inset-bottom); }` (feature 012), which clears notches and the home indicator for the whole sheet. Verification only: notched-device check in quickstart Q8.
- **Rationale**: in the footer placement the button is a child of `.surface-body`, which sits inside the sheet — the sheet-level safe-area padding, not the old header rule, is the applicable contract.
- **Alternatives considered**: per-element safe-area padding — rejected, redundant with the sheet rule.
- **Evidence**: `style.css` mobile block, `#surface` rule.

## R-8 — Performance / CLS

- **Decision**: `width="143" height="36"` attributes on the `<img>` (rendered CSS-px size matching the R-1 aspect math; `height: auto` NOT used — the attributes reserve the box). No preconnect/preload for the image host. The image is a normal non-blocking `<img>` fetch.
- **Rationale**: reserved dimensions prevent layout shift when the external image arrives (SC-003: never "blank" — alt text shows until the fetch completes); no preconnect keeps the request surface minimal (FR-008; the perf harness measures first-usable and interaction budgets — a single small image on the expand path changes nothing).
- **Alternatives considered**: lazy loading (`loading="lazy"`) — rejected, the button is above the expanded fold and lazy adds no benefit; `decoding="async"` — rejected, no measurable need; preconnect — rejected, one small image, request surface stays minimal.
- **Evidence**: existing perf budgets (feature 014, SC-008); R-1 fetch (200 in < 1 s). Budgets re-measured in quickstart Q9.

## R-9 — Ko-fi unavailability fallback

- **Decision**: nothing special — a plain `<a><img>`; if the CDN or the Ko-fi page is unreachable, the alt text renders and the link still works. No `onerror` handler, no JS.
- **Rationale**: spec edge case: "if the Ko-fi page or the image CDN is unreachable, the site must remain fully functional — the button is a plain link with no script dependency and no blocking request." An inline `onerror` would be blocked by `script-src 'self'` (no `'unsafe-inline'`) anyway, so a JS fallback is not even available — the no-JS design is the only compliant one.
- **Alternatives considered**: (a) local fallback image on `onerror` — rejected, blocked by CSP and adds a static file; (b) CSS-only fallback (background + hiding the broken img) — rejected, over-engineering for a brand asset on a stable CDN.
- **Evidence**: CSP meta `script-src 'self'` (no unsafe-inline) read from `index.html`.

## Consolidation

| # | Unknown / choice | Decision | Grounded by |
|----|------------------|----------|-------------|
| R-1 | Ko-fi embed form | Plain `<a><img>`, official CDN URL, height 36 | Live fetch (200, 580×146 WebP), embed references |
| R-2 | CSP change | `img-src` += `https://storage.ko-fi.com` — already landed in all 3 carriers, no further change | Repo grep of the 3 carriers, all byte-identical |
| R-3 | Touch target | Padding-based hit area, joins the 012 rule group; body/footer gap ≥ 8 px | style.css mobile block + body gap |
| R-4 | Placement | `.surface-footer`, sticky bottom of `.surface-body`, expanded-only; header packing machinery deleted | Owner re-decision; style.css collapse rules; main.js default states |
| R-5 | New-tab safety | `rel="noopener"` | index.html existing links |
| R-6 | Accessible name | `alt="Unterstützen"` (exact) | Spec Clarifications Q3; FR-006 |
| R-7 | Safe area | Inherit the mobile sheet rule, verify only | style.css mobile block |
| R-8 | CLS / perf | `width="143" height="36"` reserve; no preconnect | R-1 fetch, feature-014 budgets |
| R-9 | Unavailability | No fallback; plain link, alt renders | CSP `script-src 'self'`; spec edge case |
