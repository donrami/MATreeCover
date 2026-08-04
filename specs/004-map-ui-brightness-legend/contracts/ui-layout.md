# Contract: Static UI Layout (No Overlap)

**Feature**: Map UI, Brightness Slider & Gradient Legend |
**Branch**: `004-map-ui-brightness-legend`
**Source of truth**: `src/site/index.html` (markup) +
`src/site/style.css` (positioning); `src/site/main.js` mounts the
MapLibre navigation control.

## Purpose

Fix the reported overlap (Bäume button vs. map zoom controls) and
make it structurally impossible to regress: the tools card and the
navigation control must live in different screen columns, and every
static element must be pairwise disjoint at all supported viewports.

## Placement contract

| Element | Position (desktop, >480 px) | Position (narrow, ≤480 px) |
|---|---|---|
| `#legend` (color legend card) | top-left (`top: 12px; left: 12px`) | bottom strip (`bottom: 12px; left/right: 12px`) — existing media query |
| `#controls` (tools card: Bäume + slider) | left column, below the legend card | `bottom: 76px; right: 12px` (above the legend strip) — existing media query anchor |
| NavigationControl (MapLibre) | top-right (`.maplibregl-ctrl-top-right`) | top-right, unchanged |
| `#attribution` (attribution slot) | bottom-right (`bottom: 4px; right: 4px`) | bottom-right, unchanged |
| Popup | transient, anchored to clicked building | transient, dismissible |

## Invariants

1. **Different columns (FR-008).** The tools card must never occupy
   the top-right corner the navigation control uses. At desktop the
   tools card is in the left column; at ≤480 px it sits above the
   legend strip on the right, clear of the top-right zoom control.
2. **Pairwise disjoint (FR-008, SC-003).** The clickable areas of
   the five static elements are pairwise disjoint at every width
   ≥320 px and every zoom level. The popup is excluded from this
   hard constraint while open (FR-017).
3. **Bäume fully clickable (FR-009, SC-004).** The toggle must
   receive clicks at its entire rendered area, including the
   location where it overlapped the zoom control before this
   feature.
4. **Slider permanently visible (FR-016).** The brightness control
   is a standalone element inside the tools card at all viewport
   sizes; it is never hidden behind a toggle or menu.
5. **Responsive collapse preserved.** The ≤480 px legend bottom
   strip keeps its existing behavior; the tools card stacks above it
   without covering it, the zoom control, or the attribution slot.
6. **Error surface safe.** The buildings-failure message rendered
   into the attribution slot must not overlap other elements.
7. **Popup never permanent (FR-017).** The popup may transiently
   cover elements while open, must be dismissible, and must never
   permanently occlude a control.

## Verification

- Overlap matrix: `getBoundingClientRect` pairwise-disjoint check at
  widths 320, 480, 768, 1280, 1920 px × 3 zoom levels (SC-003;
  quickstart Scenario 3; `smoke_us4.md`).
- Click-through at the former overlap rectangle (SC-004; quickstart
  Scenario 4).
- Visual check at each matrix cell: legend strip, tools card, zoom
  control, and attribution all reachable (quickstart Scenario 3).
