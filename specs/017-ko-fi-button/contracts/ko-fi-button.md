# Contract: Ko-fi Donation Button

Target: `src/site/index.html`, `src/site/style.css`. Requirement sources: FR-001…FR-008, US1…US3; spec Key Entities, Edge Cases, and `## Clarifications`. Enforcement: `tests/acceptance/test_ko_fi.py`, `tests/frontend/smoke_ko_fi.md`, `scripts/smoke-verify.mjs`.

## Purpose

The owner's Ko-fi donation button lives in the surface **footer** and is visible only when the surface is expanded — it is hidden when the surface is collapsed. Placement was re-decided by the owner in the clarification session after the header was judged too prominent (spec `## Clarifications`, session 2026-08-09; spec Assumptions). The button is a plain external link with zero script dependency. The header carries no donation chrome.

## Required markup

Inside the surface body, as the last child of `.surface-body`, after `.surface-body-inner`:

```html
<footer class="surface-footer">
  <a class="ko-fi" href="https://ko-fi.com/M4Q624RYOV" target="_blank" rel="noopener">
    <img src="https://storage.ko-fi.com/cdn/kofi3.png?v=6" width="143" height="36"
         alt="Unterstützen">
  </a>
</footer>
```

| Attribute | Rule | Source |
|-----------|------|--------|
| `href` | `https://ko-fi.com/M4Q624RYOV`, exact | FR-002; DonationLink in data-model.md |
| `target` | `_blank` | FR-002 |
| `rel` | `noopener` | spec edge case; site pattern |
| `img src` | official CDN URL, `?v=6` verbatim | R-1; FR-003 |
| `img width/height` | 143 × 36 (rendered CSS px) | R-8: reserves layout space, no CLS |
| `img alt` | exactly `Unterstützen` | FR-006; accessible name is the owner-chosen short German label (R-6) |

No other attributes. In particular: no `onerror` (CSP `script-src 'self'` blocks inline handlers anyway), no `style` attribute, no external class from the Ko-fi snippet (site CSS governs).

## Behavior

- Activation opens `https://ko-fi.com/M4Q624RYOV` in a new tab; the map page stays open and unchanged (FR-002).
- The link is the only interactive behavior. No scripts run on the map page as a result of the button (FR-008).
- If the image CDN or the Ko-fi page is unreachable, the site remains fully functional: the alt text renders and the link still works (spec edge case, R-9).
- Collapsed-state visibility: when `#surface` has `is-collapsed`, `.surface-body` collapses (feature-012 rules: `max-height: 0; overflow: hidden`), so the footer button is hidden. This is the intended de-emphasis tradeoff, not a regression (spec Edge Cases, "Collapsed-state visibility"; R-4).

## Visual and layout rules

| Rule | Value | Source |
|------|-------|--------|
| Placement | `.surface-footer` is the last child of `.surface-body`; the `.ko-fi` anchor is its only child | R-4; FR-001 |
| Header | no donation element in `.surface-header` (DOM order title → tools → toggle unchanged, feature 012) | R-4; spec Clarifications |
| Visibility | expanded-only: hidden when `is-collapsed`, visible when expanded | FR-001 |
| Scroll behavior | `.surface-footer { position: sticky; bottom: 0 }` — visible without scrolling whenever the body is expanded | FR-001; R-4 |
| Alignment | centered (`display: flex; justify-content: center`), centered in the footer | R-4 |
| Separator | `border-top: 1px solid var(--subtle)` and `background: var(--panel-bg)` so body content scrolls beneath the footer | R-4 |
| Collapsed sheet height | header chrome only, ≤ 20 % of viewport height (map ≥ 80 %); the button is not part of the collapsed chrome | FR-007 |
| Touch target (mobile) | ≥ 44 × 44 px; member of the feature-012 rule group (`#baeume, .surface-toggle, .brightness input`); 36 px visual via padding | FR-004; R-3 |
| Spacing (mobile) | ≥ 8 px clear spacing to adjacent interactive content (`.surface-body-inner` flex `gap: 12px` + footer padding) | FR-004; R-3 |
| Focus indicator | visible `:focus-visible`, matches existing controls (e.g. `.surface-toggle` outline pattern) | FR-006 |
| Safe area | inherited from the mobile sheet rule `#surface { padding-bottom: env(safe-area-inset-bottom) }`; never clipped on notched devices | R-7; spec edge case |
| Overlap | never overlaps Bäume toggle, brightness slider, surface toggle, zoom control, attribution, Impressum link, or legend — expanded state | FR-005; quickstart Q5 matrix |
| No horizontal overflow | at widths 320, 375, 768, 1280, 1920 px, expanded state (143 px image fits the 292 px available at 320 px) | FR-005; SC-001 |

## Regression constraints

- No change to map values, colors, labels, popups, interactions, caching semantics, or the hashed-bundle contract (FR-009/FR-013).
- No new static files: `src/pipeline/publish.py` and `scripts/layout-manifest.tsv` are untouched (R-1).
- The CSP change (image host only) is **already landed** in all three carriers (meta tag, Worker header, feature-015 contract) and is placement-agnostic — this revision makes no further policy change (R-2; contract `csp-image-host.md`).
- CSS: delete the obsolete header-packing rules (`.ko-fi` order overrides in the ≤ 680 px media block, the ≤ 350 px image-shrink block); add the `.surface-footer` rules and keep the additive `.ko-fi` base/focus rules. No rule owned by features 012/014 is modified except removing the feature-017 header rules listed above.
- No JS change: `main.js` desktop-expand default and `syncPadding` (measures `surface.offsetHeight`) already accommodate the footer (R-4).
- All interaction-latency budgets hold (quickstart Q9).

## Machine checks (acceptance test)

`tests/acceptance/test_ko_fi.py` asserts: the anchor exists with exact `href`/`target`/`rel`; the image exists with exact `src`/`width`/`height` and `alt="Unterstützen"` exactly; the anchor sits inside `.surface-footer`; `.surface-footer` is the last child of `.surface-body`; no `.ko-fi` element remains in `.surface-header`; the mobile touch-target rule group still contains `.ko-fi` (44 px min-height CSS present); the deleted header-packing rules are absent; the CSP meta `img-src` contains `https://storage.ko-fi.com` while `script-src`/`connect-src`/`style-src` stay byte-identical to the locked values; the Worker header CSP is byte-identical to the meta CSP.
