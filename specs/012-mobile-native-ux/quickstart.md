# Quickstart: Mobile-First Native UX

Validation guide for feature 012. This feature changes presentation and interaction only; the
data pipeline, map sources, and `style.json` are untouched. Validation proves the mobile-first,
map-dominant layout, thumb-friendly native-size tools, and desktop consistency without
regressing any existing feature.

## Prerequisites

- Repo checked out on branch `012-mobile-native-ux`.
- Python 3.11 and `make` per [DEVELOPMENT.md](../../DEVELOPMENT.md).
- A modern browser with WebGL 2 for the manual mobile/desktop checks.
- The published bundle buildable via `make publish` (or a dev server serving `dist/`).

## Setup

```text
make check-prereqs
make bootstrap        # venv + deps + acceptance suite
make publish          # build the static dist/ bundle
```

## Automated checks

```text
.venv/bin/python -m pytest tests/                      # full suite stays green (SC-008)
make check-public                                      # public-release scan stays clean (SC-008)
```

New static assertions (in `tests/acceptance/test_style.py`) verify:

- `#surface` markup with `.surface-header` and `.surface-body` exists in `index.html`.
- The mobile media query sets interactive controls to >= 44x44 px targets and >= 8 px spacing
  (touch-a11y-copy contract).
- A `@media (prefers-reduced-motion: reduce)` block disables transitions (layout-ux contract).
- `style.json` palette and layer order are unchanged (SC-004).

The zero-em/en-dash copy check (SC-009) runs as part of the suite or the smoke checklist.

## Manual validation scenarios

Open the published bundle in a browser. Use the browser's responsive/device toolbar to switch
between a mobile viewport (e.g. 375 x 812) and a desktop viewport (>= 768 px wide).

### Scenario 1: Mobile map is the dominant surface (US1, FR-001, SC-001)

1. Set a mobile viewport. Load the page.
2. Verify the map fills the screen and the legend/city-overview content is collapsed behind a
   compact bottom header.
3. Verify the collapsed surface leaves the map occupying at least 80% of the viewport height
   (measure header height vs. viewport).
4. Pinch-zoom, drag-pan, and tap a building. Verify gestures respond immediately and the
   collapsed surface does not intercept or block them (US1).

### Scenario 2: Expand/collapse + popup visibility (US1, FR-002, FR-006)

1. Single-tap the expand control. Verify the body slides up revealing the legend, city
   overview, and controls without a reload, map still visible above the sheet (FR-002).
2. Tap the collapse control. Verify the surface collapses and the map regains the full
   viewport.
3. Tap a building near the bottom while expanded. Verify its value popup stays fully visible
   above the sheet (FR-006). Repeat collapsed. Test several positions.

### Scenario 3: Native-size, thumb-reachable tools (US2, FR-003, FR-004, FR-005)

1. In a mobile viewport, measure every interactive control (Bäume, Helligkeit, expand toggle,
   zoom buttons, popup close). Verify each touch target is at least 44x44 px with at least
   8 px spacing (FR-003).
2. With the legend collapsed, verify Bäume and Helligkeit remain visible and operable
   (FR-004).
3. Verify no new control overlaps the zoom control (top-right) or attribution (bottom-right)
   (FR-005).

### Scenario 4: Consistent, space-optimized desktop (US3, FR-008)

1. Set a desktop viewport. Load the page. Verify the surface uses the same component set as
   mobile (header/body, tools, controls) and the map is dominant.
2. Collapse the surface. Verify the map reclaims the freed space with no content clipped.
3. Exercise Bäume, Helligkeit, the story modal, district popup, attribution, and Impressum.
   Verify each works exactly as before this feature (FR-010).

### Scenario 5: Edge cases

1. Very small phone (>= 320 px) and a landscape phone: surface and controls remain usable and
   never overflow the viewport.
2. A notched device: controls and surface clear the safe-area insets and are never clipped
   (FR-007).
3. Resize a desktop window across the 768 px breakpoint in both directions: layout transitions
   cleanly with no broken overlaps or content overflow.
4. Browser address bar showing/hiding: no visible layout shift (SC-005).
5. Reduced-motion preference on: all expand/collapse transitions render instant, non-animated
   (FR-008).
6. Large OS text / zoomed browser: the surface reflows and does not break layout or clip
   labels.

## Expected outcomes

- All automated checks pass and `make check-public` is clean (SC-008).
- Mobile: map dominant, collapsed by default, one-tap expand/collapse, tools thumb-reachable
  and >= 44x44 px, popups fully visible, no overlap of zoom or attribution.
- Desktop: same components, collapsible surface, map dominant, all existing features
  unchanged (FR-010).
- Zero new network requests and offline-first load intact (FR-012, SC-007).
- All new copy German, zero em/en dashes (FR-011, SC-009).
- Keyboard-only user reaches and operates every control with visible focus (SC-010).

## References

- Surface layout, breakpoints, safe-area, motion: [contracts/layout-ux.md](contracts/layout-ux.md)
- Surface component, tools-in-header, popup clearance, parity: [contracts/surface-interaction.md](contracts/surface-interaction.md)
- Touch targets, accessibility, copy: [contracts/touch-a11y-copy.md](contracts/touch-a11y-copy.md)
- UI state model and invariants: [data-model.md](data-model.md)
- Design research grounding: [research.md](research.md)
