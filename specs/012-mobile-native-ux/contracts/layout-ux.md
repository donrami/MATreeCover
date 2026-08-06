# Contract: Layout & UX

Feature 012, FR-001, FR-002, FR-005, FR-007, FR-008, SC-001, SC-005.

## Breakpoint

A single breakpoint at **768 px** (R-8).

| Width | Surface mode | Default state |
|-------|--------------|---------------|
| `< 768 px` | bottom sheet (fixed, full-width, bottom) | collapsed (FR-001) |
| `>= 768 px` | panel (absolute, top-left) | expanded (matches current desktop) |

The breakpoint must transition cleanly in both directions as the window resizes across it
(edge case): the surface component, controls, and JS wiring are identical in both modes, only
the CSS geometry changes (FR-008).

## Map-dominant layout

- `#map` stays full-bleed (`position: absolute; inset: 0`) in every mode.
- When the surface is **collapsed on mobile**, the surface chrome (header + safe-area padding)
  must occupy no more than 20% of the viewport height, leaving the map >= 80% (SC-001).
- The map must remain interactive (pan, pinch-zoom, tap) with the surface collapsed; the
  collapsed surface must not intercept map gestures on the map area (US1).

## Surface geometry

### Mobile bottom sheet (`< 768px`)

- `position: fixed; left: 0; right: 0; bottom: 0; width: 100%; z-index: 20` (above the map,
  below the story modal at `z-index: 30`).
- Expanded body max-height: `min(55dvh, 100dvh - safe-area-bottom)` with `overflow-y: auto`,
  so the sheet scrolls internally and never overflows the visible viewport (edge case:
  address bar taller than the screen).
- The collapsed header sits at the bottom (thumb zone, R-4).
- Zoom control stays top-right; attribution stays bottom-right; Impressum stays bottom-left.
  The sheet never overlaps them (see no-overlap matrix).

### Desktop panel (`>= 768px`)

- `position: absolute; top: 12px; left: 12px; z-index: 10`, same as the current `#left-stack`
  position.
- Expanded body height is content-driven with an internal scroll cap; collapsed body is hidden
  and the map reclaims the freed space (P3, no content clipped).
- Same header/body markup, same controls, same JS as mobile (FR-008).

## Safe-area + browser-chrome handling (FR-007, SC-005)

- The sheet and any fixed chrome MUST pad with `env(safe-area-inset-top/bottom/left/right)` so
  controls are never clipped or partially hidden behind notches or the home indicator.
- Viewport-height sizing MUST use dynamic viewport units (`dvh`/`svh`) with a `vh` fallback, so
  the expanded sheet matches the visible viewport as the browser address bar shows/hides.
- This MUST produce zero visible layout shift when browser chrome appears or hides (SC-005).
- On very small phones (>= 320 px) and landscape phones the surface and controls MUST NOT
  overflow the viewport.

## No-overlap matrix

Reuse the feature-004/011 overlap-matrix technique: assert each fixed/absolute control's
bounding box against every other in both surface states and both breakpoints.

| Control A | Control B | Rule |
|-----------|-----------|------|
| Surface header (mobile) | Zoom (top-right) | Disjoint; header is bottom, zoom is top (FR-005) |
| Surface (any state) | Attribution (bottom-right) | Disjoint; attribution not hidden or covered (FR-005) |
| Surface | Impressum `.legal-link` (bottom-left) | Disjoint |
| Tools in header | Zoom | Disjoint (FR-005) |
| Tools in header | Attribution | Disjoint (FR-005) |
| Popups | Surface (expanded or collapsed) | Disjoint via `map.setPadding` (FR-006) |

## Motion (FR-008)

- Expand/collapse uses `transform: translateY` and `opacity` transitions (compositor-safe);
  the toggle chevron uses a scale/rotate transition.
- `@media (prefers-reduced-motion: reduce)` disables all transitions and animations, making
  every state change instant and non-animated.
