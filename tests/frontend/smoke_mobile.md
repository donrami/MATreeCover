# Smoke Checklist: Mobile-First Native UX (feature 012)

Manual browser checklist for the mobile-first, map-dominant layout. Run against the
published bundle (`dist/`) in a browser with a responsive/device toolbar. Applies to
US1, US2, US3 and the edge cases in `spec.md`.

**Prerequisites**: bundle built (`make publish`), a modern browser with WebGL 2.

**Conventions**: German copy, no em-dashes, no en-dashes (FR-011). No feature added,
removed, or renamed (FR-010).

## Automated checks (run first)

```text
.venv/bin/python -m pytest tests/acceptance/test_style.py -q
make check-public
```

`test_style.py` now also asserts: `#surface` markup with `.surface-header` /
`.surface-body`, mobile collapsed-by-default, the reduced-motion block, the 768 px
breakpoint, and 44 px touch targets (FR-001/FR-003/FR-008, R-8).

## Mobile: US1 map dominant (FR-001, SC-001)

Open a mobile viewport (e.g. 375 x 812).

- [ ] Map fills the screen; legend/city-overview is collapsed behind a compact bottom
      header by default.
- [ ] Collapsed header is no more than 20% of the viewport height; map occupies at least
      80% (measure header height vs. viewport).
- [ ] Pinch-zoom, drag-pan, and tap respond immediately; the collapsed surface does not
      intercept gestures on the map area.
- [ ] Single tap on the expand control slides the body up revealing legend, city
      overview, and tools, with the map still visible above the sheet.
- [ ] Single tap on the collapse control restores the map to full viewport.
- [ ] The expand/collapse control renders as a bare arrow (chevron) with no surrounding
      box, on both mobile and desktop.

## Legend scale bar (30% shade guideline)

- [ ] The orange-to-blue transition begins exactly at the 30% tick: the bar shows warm
      colors up to 30% and blue from 30% onward, with no blue before the 30% mark.
- [ ] From 30% to 100% the bar shows a continuous gradient from dark blue to pale cyan
      (no flat, same-shade region).

## Mobile: popup clearance (FR-006)

- [ ] Expanded: tap a building near the bottom; its value popup stays fully visible
      above the sheet. Repeat at several positions.
- [ ] Collapsed: tap a building; its popup is fully visible above the sheet.

## Mobile: native-size thumb tools (US2, FR-003, FR-004, FR-005)

- [ ] Every interactive control (Bäume, Helligkeit slider, expand toggle, zoom buttons,
      popup close) has a touch target of at least 44 x 44 px.
- [ ] Adjacent controls have at least 8 px clear spacing.
- [ ] With the legend collapsed, Bäume and Helligkeit remain visible and operable.
- [ ] Attribution (map data/copyright) and Impressum sit top-left and stay visible with
      the sheet collapsed or expanded; the attribution box wraps within its width and
      never overlaps the zoom control (top-right).

## Desktop: consistent, space-optimized (US3, FR-008)

Open a desktop viewport (>= 768 px wide).

- [ ] The surface is a top-left panel, expanded by default, using the same component set
      as mobile (header/body, tools, controls).
- [ ] Collapse the panel; the map reclaims the freed space with no content clipped.
- [ ] Bäume, Helligkeit, the story modal, district popup, building popup, attribution,
      and Impressum all behave exactly as before this feature (FR-010).

## Edge cases

- [ ] Very small phone (>= 320 px): surface and controls are usable and never overflow
      the viewport.
- [ ] Landscape phone: same, no overflow; collapsed header stays under 20% of viewport.
- [ ] Notched device: controls and surface clear the safe-area insets, never clipped.
- [ ] Resize a desktop window across the 768 px breakpoint in both directions: the layout
      transitions cleanly with no broken overlaps or overflow.
- [ ] Browser address bar shows/hides: no visible layout shift (SC-005).
- [ ] Reduced-motion preference on: all expand/collapse transitions are instant and
      non-animated (FR-008).
- [ ] Large OS text or zoomed browser: the surface reflows and does not break layout or
      clip labels.

## Copy gate (SC-009)

- [ ] All new copy is German with zero em-dashes and zero en-dashes (mechanical check in
      `test_style.py`).

## Expected outcome

All automated checks pass, `make check-public` stays clean (no new findings from this
feature), and every manual scenario above passes without regressing any existing feature.
