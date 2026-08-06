# Contract: Surface Interaction

Feature 012, FR-002, FR-004, FR-006, FR-008, FR-010, SC-006.

## Component contract: `#surface`

The legend/summary surface is **one component** with two parts, shared across breakpoints
(FR-008). It replaces the static `#left-stack` column in `src/site/index.html`.

### Header (`.surface-header`) — always present

Carries, in DOM order:

1. Legend title (the existing `#legend h1`, e.g. the legend heading).
2. Tools: Bäume toggle (`#baeume`) and Helligkeit slider (`#brightness-slider`).
3. Expand/collapse toggle button (the control that reveals/hides the body).

The header is the persistent part of the surface. Because the tools live in the header, they
remain **visible and operable while the surface is collapsed** (FR-004) and sit in the
thumb-friendly lower zone on mobile (FR-003).

### Body (`.surface-body`) — collapsible

Carries the full legend (description, gradient bar, ticks, units, note) and the
city-overview panel (the existing `#city-panel` content). Hidden when collapsed; revealed when
expanded, with internal scroll when taller than the screen.

## State + toggle

- Surface state is `collapsed` or `expanded`, represented by a class (e.g. `is-collapsed`) on
  `#surface`.
- The toggle is a `<button>` with `aria-expanded` and `aria-controls="surface-body"`; it is
  keyboard-operable (native button: Enter/Space) and has a visible focus state (FR-014).
- Collapsed-by-default on mobile (FR-001); expanded-by-default on desktop (matches current).
- State is session-only, DOM-backed. Nothing is persisted; no storage read/write added.

## Motion (FR-008)

- Body slides in/out via `transform: translateY`; toggle chevron scales/rotates; transitions
  animate `transform`/`opacity` only (compositor-safe).
- `@media (prefers-reduced-motion: reduce)` makes all transitions instant.

## Popup clearance (FR-006)

- On surface expand: `map.setPadding({ bottom: <sheetHeightPx> })`.
- On surface collapse: `map.setPadding({ bottom: 0 })`.
- MapLibre then keeps both the building popup and the district popup fully visible above the
  surface in every map position, including a building tapped near the bottom (R-7, edge case).
- This applies in both breakpoints (padding is layout-agnostic). The existing persistent popup
  instances, content, and click arbitration are unchanged (FR-010).

## Feature parity (FR-010)

The following MUST keep their current behaviour exactly:

- Bäume toggle (visibility-only change to `trees-fill`, `aria-pressed`).
- Helligkeit slider (5..100 to `raster-brightness-max`, session-only).
- First-visit story modal (self-contained, storage-guarded, focus-trapped).
- City-overview panel content (rendered from `metadata.city_stats`; hides when missing).
- Building popup and district popup (content, anchors, click arbitration).
- Attribution and Impressum links.
- Zoom control (top-right, unchanged position).

This feature only relocates these into the shared surface header/body and changes their
geometry, never their function.

## Performance (SC-006)

- Expand/collapse MUST be a compositor-only `transform`/`opacity` transition: no layout or
  paint thrash, so the interaction completes well inside the 2 s budget.
- No new blocking work at load: the surface is static DOM; no new network request, no new
  source (FR-012).
- Re-measure and add `surface_toggle` to `interaction_latency_ms` in
  `validation/perf-budget.json`.
