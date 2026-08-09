# Contract: Ko-fi Donation Button

Target: `src/site/index.html`, `src/site/style.css`. Requirement sources: FR-001…FR-008, US1…US3; spec Key Entities and Edge Cases. Enforcement: `tests/acceptance/test_ko_fi.py`, `tests/frontend/smoke_ko_fi.md`, `scripts/smoke-verify.mjs`.

## Purpose

The owner's Ko-fi donation button lives in the surface header, always visible on both breakpoints (desktop panel header, mobile collapsed bottom-sheet header), in both collapsed and expanded surface states. It is a plain external link with zero script dependency. Placement was owner-confirmed (spec Assumptions: header, not the story modal).

## Required markup

Inside `.surface-header`, between `.surface-tools` and `#surface-toggle` (the chevron stays the rightmost header element — feature 012):

```html
<a class="ko-fi" href="https://ko-fi.com/M4Q624RYOV" target="_blank" rel="noopener">
  <img src="https://storage.ko-fi.com/cdn/kofi3.png?v=6" width="143" height="36"
       alt="Baumfläche auf Ko-fi unterstützen">
</a>
```

| Attribute | Rule | Source |
|-----------|------|--------|
| `href` | `https://ko-fi.com/M4Q624RYOV`, exact | FR-002; DonationLink in data-model.md |
| `target` | `_blank` | FR-002 |
| `rel` | `noopener` | spec edge case; site pattern |
| `img src` | official CDN URL, `?v=6` verbatim | R-1; FR-003 |
| `img width/height` | 143 × 36 (rendered CSS px) | R-8: reserves layout space, no CLS |
| `img alt` | German donation text (above) | FR-006; spec language edge case |

No other attributes. In particular: no `onerror` (CSP `script-src 'self'` blocks inline handlers anyway), no `style` attribute, no external class from the Ko-fi snippet (site CSS governs).

## Behavior

- Activation opens `https://ko-fi.com/M4Q624RYOV` in a new tab; the map page stays open and unchanged (FR-002).
- The link is the only interactive behavior. No scripts run on the map page as a result of the button (FR-008).
- If the image CDN or Ko-fi page is unreachable, the site remains fully functional: the alt text renders and the link still works (spec edge case, R-9).

## Visual and layout rules

| Rule | Value | Source |
|------|-------|--------|
| Placement | direct child of `.surface-header`, DOM order title → tools → ko-fi → toggle | R-4; chevron rightmost |
| Desktop (≥ 768 px) | one header row: title left, tools + ko-fi + chevron right | R-4 |
| Mobile (< 768 px) | participates in the existing wrap layout; at most 2 header rows at any width ≥ 320 px | R-4; FR-007 |
| ≤ 350 px | order override: row 1 `[title, ko-fi, toggle]`, row 2 `[tools]`; image height MAY drop to 32-34 px if the 20 % height budget fails at 320×568 | R-4 fallback |
| Collapsed header height | ≤ 20 % of viewport height (map ≥ 80 %) | FR-007 |
| Touch target (mobile) | ≥ 44 × 44 px; join the existing rule group (`#baeume, .surface-toggle, .brightness input`) | FR-004; R-3 |
| Spacing (mobile) | ≥ 8 px clear spacing to adjacent controls (existing flex `gap: 8px`; visual spacing only grows) | FR-004; R-3 |
| Focus indicator | visible `:focus-visible`, matches existing controls (e.g. `.surface-toggle` outline pattern) | FR-006 |
| Safe area | inherited from `.surface-header { padding-bottom: max(8px, env(safe-area-inset-bottom)) }`; never clipped on notched devices | R-7; spec edge case |
| Overlap | never overlaps Bäume toggle, brightness slider, surface toggle, zoom control, attribution, Impressum link, or legend | FR-005; quickstart Q5 matrix |
| No horizontal overflow | at widths 320, 375, 768, 1280, 1920 px, both surface states | FR-005; SC-001 |

## Regression constraints

- No change to map values, colors, labels, popups, interactions, caching semantics, or the hashed-bundle contract (FR-009/FR-013).
- No new static files: `src/pipeline/publish.py` and `scripts/layout-manifest.tsv` are untouched (R-1).
- No change to any CSS rule owned by features 012/014 except additive `.ko-fi` rules. The existing touch-target rule group gains `.ko-fi` as a member; nothing else in the mobile media query changes.
- All interaction-latency budgets hold (quickstart Q9).

## Machine checks (acceptance test)

`tests/acceptance/test_ko_fi.py` asserts: the anchor exists with exact `href`/`target`/`rel`; the image exists with exact `src`/`width`/`height` and a German alt mentioning "Ko-fi" and a donation/support word; `.ko-fi` participates in the mobile touch-target rule group (44 px min-height CSS present); the CSP meta `img-src` contains `https://storage.ko-fi.com` while `script-src`/`connect-src`/`style-src` stay byte-identical to the locked values; the Worker header CSP is byte-identical to the meta CSP.
