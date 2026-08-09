# Quickstart: Ko-fi Donation Button (feature 017)

Validation guide. Run these scenarios in order to prove the feature works end to end. Details live in the [contracts](contracts/) and [data model](data-model.md). This file is the run guide, not the implementation.

**Revision note (2026-08-09)**: the button moved from the surface header to the surface footer and is visible only when the surface is expanded (hidden when collapsed); its accessible name is "Unterstützen" (spec `## Clarifications`). All scenarios below reflect that placement.

## Prerequisites

- Branch `017-ko-fi-button`, clean worktree.
- `git`, `bash`, `python3.11`, `.venv` with dev extras (`make bootstrap`), `curl`.
- For Q2/Q4/Q5/Q6/Q8 (browser): `node`, a Chromium build (`CHROME_PATH`, default `/usr/bin/chromium`).
- For Q9 (perf + parity): `node`, Chromium, `scripts/perf-measure.sh` as committed.
- A local build of the published bundle is produced by `make publish` into `dist/`; browser scenarios can run against `dist/` served over HTTP (CSP `img-src` allows the external Ko-fi CDN regardless of the serving origin) or the live site.

## Q1 — Desktop: visible when expanded, hidden when collapsed (US1, FR-001, SC-001)

```text
make publish
.venv/bin/python -m pytest tests/acceptance/test_ko_fi.py -q
```

Expected: acceptance tests green ([ko-fi-button.md](contracts/ko-fi-button.md) machine checks). Manual (≥ 768 px viewport, panel expanded by default): the Ko-fi button is clearly visible in the surface footer without scrolling — centered at the bottom of the expanded panel. Toggle the chevron to collapse: the button disappears (the footer lives in the collapsible body); toggle back: it reappears. Verified at 768, 1280, 1920 px.

## Q2 — New-tab activation (US1, FR-002, SC-002)

```text
node scripts/smoke-verify.mjs <url>   # ko-fi scenario: visible in footer, click, new tab, map page open
```

Expected: clicking the button opens `https://ko-fi.com/M4Q624RYOV` in a new tab (exact URL); the map page remains open and interactive in the original tab; the external page cannot control the map page (`rel="noopener"`, verified in the acceptance test). Note: a `curl` HEAD to the Ko-fi page returns 403 (Ko-fi bot protection, research R-1) — browsers load it normally; judge by the browser tab, not curl.

## Q3 — Mobile: collapsed sheet has no button, map dominant (US2, FR-001/007, SC-004)

Open a mobile viewport (e.g. 375 × 812), sheet collapsed by default.

- [ ] No donation button visible in the collapsed sheet (header and body hidden — the footer is part of the collapsible body).
- [ ] Sheet chrome ≤ 20 % of viewport height; map ≥ 80 %.

Expand the sheet:

- [ ] The Ko-fi button is visible in the sheet footer without scrolling (sticky footer, R-4).

Measure sheet height vs. viewport in devtools; record the numbers for the width matrix.

## Q4 — Touch target and spacing (US2, FR-004, SC-005)

In the mobile viewport with the sheet expanded, inspect the button's computed box:

```js
const b = document.querySelector('.ko-fi').getBoundingClientRect();
b.width + 'x' + b.height   // >= 44x44
```

Expected: hit box ≥ 44 × 44 px. Visually the image stays 36 px tall (padding enlarges the hit area, [ko-fi-button.md](contracts/ko-fi-button.md)). Confirm ≥ 8 px clear spacing to adjacent interactive content (legend-note link "Details unter Datenquellen") — `.surface-body-inner` flex `gap: 12px` + footer padding provide it.

## Q5 — No-overlap matrix (FR-005, SC-004)

At each width in {320, 375, 768, 1280, 1920} px, in the expanded surface state (the collapsed state has no button), run the established overlap-matrix script with the ko-fi rect added:

```js
const rects = [...document.querySelectorAll('#baeume, .brightness, #surface-toggle, .legal-link, #attribution, .maplibregl-ctrl-top-right, .ko-fi')]
  .map(el => { const r = el.getBoundingClientRect(); return { id: el.id || el.className, l: r.left, t: r.top, r: r.right, b: r.bottom }; });
const overlap = (a, b) => a.l < b.r && a.r > b.l && a.t < b.b && a.b > b.t;
const pairs = [];
for (let i = 0; i < rects.length; i++)
  for (let j = i + 1; j < rects.length; j++)
    if (overlap(rects[i], rects[j])) pairs.push([rects[i].id, rects[j].id]);
pairs; // must be []
```

Expected: no pairs at any cell; no horizontal overflow at 320 px (143 px image fits the 292 px footer width). The map stays pan/zoom-able with the sheet collapsed (the button never intercepts map gestures — it is hidden in that state).

## Q6 — Image renders under the extended CSP (US3, FR-003/009)

```text
.venv/bin/python -m pytest tests/acceptance/test_ko_fi.py -q -k csp
```

Expected: acceptance test green — meta CSP `img-src` contains `https://storage.ko-fi.com`; `script-src 'self'` / `connect-src` / `style-src` byte-identical to the locked values; the Worker header CSP byte-identical to the meta ([csp-image-host.md](contracts/csp-image-host.md)). Manual: load the page in a browser, devtools console shows zero CSP violations, the button image renders (no broken-image/blank state). The Ko-fi image is fetched from `https://storage.ko-fi.com/cdn/kofi3.png?v=6` (CDN serves WebP — covered by `img-src`).

## Q7 — Keyboard accessibility (US3, FR-006)

- [ ] Tab from the page start: the button receives focus with a visible focus indicator.
- [ ] Enter activates the link; Ko-fi opens in a new tab.
- [ ] Inspect the accessible name (devtools accessibility panel): it is exactly "Unterstützen", identifying the link as a support/donation link in German.

## Q8 — 320 px floor and safe areas (SC-001, FR-007, edge cases)

At 320 × 568 (iPhone SE), sheet expanded and collapsed:

- [ ] Expanded: the footer button renders centered, nothing wraps or overflows; the 143 px image fits the 292 px footer width.
- [ ] Collapsed: no donation chrome; collapsed sheet height ≤ 20 % of viewport (≤ 113 px at 568 px height) — the button is not part of the collapsed strip, so no image-shrink fallback is needed.
- [ ] City panel open (tap a district): body content scrolls beneath the sticky footer; the button stays visible without scrolling.
- [ ] Notched device (e.g. 375 × 812 with safe-area inset): footer content clears the notch/home indicator (existing sheet `env(safe-area-inset-bottom)` padding), the button is never clipped.
- [ ] Resize across the 768 px breakpoint both directions: layout transitions cleanly, no broken overlaps.

## Q9 — Nothing regresses (US4, FR-010, SC-007)

```text
make check-public && make check-layout && make check-or005 && make check-history
.venv/bin/python -m pytest tests/ -q
bash scripts/perf-measure.sh <url>
node scripts/parity-render.mjs --archive dist/buildings.pmtiles --out /tmp/parity-017
```

Expected: all governance gates green; full test suite green (including all pre-existing tests — the CSP extension breaks no pinned assertion, research R-2); all 8 interactions within the 2 s budget, desktop interaction median ≤ 123 ms, first usable ≤ 10 s; parity render shows building values, colors, labels, popups identical to the previous bundle. Manual: map pan/zoom, Bäume toggle, brightness slider, surface toggle, popups, attribution, Impressum, legend — all behave exactly as before; the header row is unchanged (title → tools → toggle); the button is purely additive (FR-013).

## Success criteria cross-check

| Criterion | Proven by |
|-----------|-----------|
| SC-001 button visible in the surface footer when expanded, hidden when collapsed, both breakpoints, widths 320/375/768/1280/1920 | Q1, Q3, Q5, Q8 |
| SC-002 every activation opens Ko-fi in a new tab | Q2 |
| SC-003 image renders, zero broken/blocked states | Q6 |
| SC-004 no overlap at any width in the expanded state; map ≥ 80 % on mobile collapsed | Q5, Q3 |
| SC-005 touch target ≥ 44 × 44 | Q4 |
| SC-006 accessible name "Unterstützen"; keyboard operable with focus indicator | Q7 |
| SC-007 zero regressions; budgets hold; map identical | Q9 |
