# Contract: Story Modal — Placement, Dialog Semantics, Dismissal

**Feature**: First-Visit Story Modal |
**Branch**: `007-first-visit-story`
**Source of truth**: `src/site/index.html` (markup) +
`src/site/style.css` (layout) + `src/site/main.js` (behavior).

## Purpose

A first-time visitor gets a short, dismissible German story about
the map, shown once per browser, without disturbing the map or the
existing UI. This contract fixes the modal's geometry (no overlap,
FR-010), its accessibility semantics (FR-008, FR-009), and its
dismissal wiring (FR-004, FR-005, FR-007).

## Markup contract

```html
<div class="story-backdrop" id="story-backdrop" hidden>
  <div class="story-modal" id="story-dialog" role="dialog"
       aria-modal="true" aria-labelledby="story-title" tabindex="-1">
    <h2 id="story-title">…</h2>
    <button id="story-close" type="button" class="story-close"
            aria-label="Schließen">✕</button>
    <!-- story content per contracts/story-content.md -->
  </div>
</div>
```

- Markup exists **only** in `index.html` — never in
  `attribution.html` (FR-012). `main.js` is included by the map
  page only, so the attribution page cannot show the modal by
  construction.
- The backdrop starts with the `hidden` attribute; `main.js`
  removes it on first visit, re-adds it on dismissal (plus DOM
  removal).
- The close button is a real `<button type="button">` with a
  visible glyph and an `aria-label` — visible close button
  (FR-004), keyboard operable (FR-008).

## Placement contract (no overlap, FR-010)

The backdrop is `position: fixed; inset: 0; z-index: 30` — above
`#left-stack`/`#attribution` (z-index 10) and MapLibre's controls
(default stacking inside the map container). The dialog card sits in
the viewport's safe zone, disjoint from the five existing static
elements at every width ≥320 px:

| Element | Desktop (>480 px) | Narrow (≤480 px) |
|---|---|---|
| `#legend` (legend card) | top-left (`top: 12px; left: 12px`) | bottom strip (`bottom: 12px`) |
| `#controls` (tools card) | left column, below legend | stacked above the legend strip |
| NavigationControl (MapLibre) | top-right | top-right |
| `#attribution` + MapLibre attribution | bottom-right | bottom-right |
| **`.story-modal`** | **top margin 286 px** (below the left column, bottom ≈ 266 px), centered horizontally, `max-width: 480px`, `max-height: calc(100vh - 310px)` (286 top + 24 bottom reserve clears the attribution row), `overflow-y: auto` | **top margin 117 px** (below the zoom control, bottom ≈ 97 px), centered, `width: calc(100vw - 24px)`, `max-height: calc(100vh - 300px)` (117 top + 183 bottom reserve clears the bottom strip ≈ 158 px, top ≈ 598 px at 768 px viewport), `overflow-y: auto` |

### Invariants

1. **Pairwise disjoint (FR-010, SC-008).** The modal's
   `getBoundingClientRect()` never intersects `#legend`, `#controls`,
   the NavigationControl, `#attribution`, or the MapLibre attribution
   at any width ≥320 px while open. The 004 overlap matrix is
   extended with the modal rect (quickstart Scenario 6;
   `smoke_us5.md`).
2. **Internal scroll, never page scroll.** Tall story content, text
   zoom, and small viewports scroll inside the modal
   (`overflow-y: auto`); nothing is clipped (spec edge cases).
3. **No layout shift (FR-007).** The backdrop is a fixed overlay;
   the map container's box never changes. Removing the backdrop on
   close causes no reflow and no reload; the map is immediately
   interactive again.
4. **Backdrop intercepts while open.** The map is visible but not
   interactive while the modal is open (spec assumption); no
   MapLibre API call is needed — the overlay owns pointer events.

## Dialog semantics and focus contract (FR-008, FR-009)

| Event | Behavior |
|---|---|
| Open | Remove `hidden`; focus the dialog element (`tabindex="-1"`); screen reader announces dialog name from `aria-labelledby` |
| Tab / Shift+Tab | Trapped inside the dialog: cycle close button + the two reference links; focus never leaves while open |
| Escape | Closes (same path as close button) |
| Close (button or Escape) | Remove backdrop from DOM; restore focus to the previously focused element (document body on page-load open); tear down listeners |

- Story text is real text content (paragraphs and links), never
  `aria-hidden` or image-only (FR-009).
- `aria-modal="true"` removes the rest of the page from the
  accessibility tree while open (standard dialog pattern; research
  R-4).

## Dismissal contract (FR-004, FR-005, FR-013)

- Dismissal happens only through an explicit action: close-button
  click or Escape. Clicking the backdrop does **not** dismiss
  (dismissal must be explicit, and accidental map clicks under the
  overlay must not destroy the story).
- On dismissal: persist via `localStorage`
  (`contracts/dismissal-state.md`), or the in-memory fallback when
  storage is unavailable; then remove the overlay and restore focus.
- The modal never reappears in the same browser while the
  dismissal state exists (FR-005, SC-002).

## Verification

- Overlap matrix including the open modal rect at widths 320, 480,
  768, 1280, 1920 px (quickstart Scenario 6; `smoke_us5.md`).
- Keyboard-only flow and screen-reader spot check (quickstart
  Scenario 5).
- Dismissal + persistence across reloads and sessions (quickstart
  Scenario 3); storage-blocked fallback (quickstart Scenario 4).
