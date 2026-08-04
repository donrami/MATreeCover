# Data Model

**Branch**: `004-map-ui-brightness-legend` | **Date**: 2026-08-04
**Source**: `spec.md` § Key Entities + clarifications,
`src/site/style.json`, `src/site/index.html`, `src/site/style.css`,
`research.md` R-001/R-003/R-004.

This feature introduces no data entities and no persisted state
(FR-007). The entities below document the UI surface the feature
operates on and the invariants the plan must hold. Layer order and
the building palette are carried forward frozen from 003's data
model (E-002, E-003).

## E-001 — BaseMapLayer (brightness surface)

The grayscale basemap raster layer. Its brightness becomes
user-adjustable while the static default stays as 003 shipped it.

| Field | Value | Notes |
|---|---|---|
| `layer.id` / `type` | `"basemap"` / `"raster"` | Unchanged. |
| `source.id` | `"basemap"` | Same tile URLs (SC-007). |
| `paint.raster-brightness-min` | `0` (default) | Fixed. Transform is `out = max * in`. |
| `paint.raster-brightness-max` (static) | `0.65` | Unchanged in `style.json` — the no-JS / on-load default. |
| `paint.raster-brightness-max` (runtime) | `[0.05, 1.0]`, default `0.65` | Set via `setPaintProperty`; user-adjustable (FR-001/FR-002). Supersedes 003's `[0.6, 0.7]` static-window clause at runtime only (research R-008). |
| low-range behavior | below slider 25 the inverted layer (E-006) crossfades in (FR-019) | `basemap` keeps `max = v/100`; the inverted layer carries the visual. |

**Invariants**:
- Grayscale in, grayscale out: the scale is identical across RGB
  channels, so hue/saturation are untouched at every slider position
  (FR-004, 003 contract invariant 1).
- Only this layer is affected; layers above (mask, buildings, trees)
  are not processed by the raster shader (FR-004).
- Session-only: the runtime value lives in page memory and resets to
  0.65 on reload (FR-007).

## E-002 — BrightnessControl

The slider element and its state.

| Field | Value | Notes |
|---|---|---|
| element | native `<input type="range">` | Keyboard, touch, and ARIA semantics native (FR-006). |
| range | `min=5`, `max=100` | Maps identity to `raster-brightness-max` 0.05..1.0 (research R-001). |
| default value | `65` | Reproduces today's published appearance (FR-003). |
| label | "Helligkeit" (visible) + `aria-label` | German UI language retained (localization unchanged). |
| state | in-memory only | No persistence (FR-007); survives pan/zoom (US1 acceptance 6). |
| wiring | `addEventListener('input', …)` in `main.js` | CSP `script-src 'self'` forbids inline handlers (research R-002). |

**Invariants**:
- The control is permanently visible at all viewport sizes (FR-016),
  rendered inside the tools card, never hidden behind a toggle.
- Dragging it does not pan the map, and map gestures do not reset
  its value (FR-006, edge cases).
- It is part of the pairwise non-overlap set (FR-008).

## E-003 — ToolsCard (UI container)

The container holding the Bäume toggle and the BrightnessControl.

| Field | Value | Notes |
|---|---|---|
| current position | `top: 12px; right: 12px` | The overlap source (shares the top-right corner with the navigation control). |
| new position | left column, below the legend card | `#controls` moves to `top` = legend card bottom + gap, `left: 12px`; see `contracts/ui-layout.md`. |
| ≤480 px behavior | `bottom: 76px; right: 12px` (existing media query) | Kept; now holds two controls; must stay above the legend strip and clear of attribution. |

**Invariants**:
- The tools card and the navigation control are in different screen
  columns at all widths ≥320 px (FR-008, research R-003).
- The Bäume toggle remains a fully clickable control (FR-009,
  SC-004).

## E-004 — ColorLegend (gradient)

The legend card's color-scale presentation, changed from discrete
swatches to a continuous gradient bar.

| Field | Value | Notes |
|---|---|---|
| title / description / unit | "Baumfläche" / "Durchschnittlicher Baumanteil im 60-m-Umkreis" / "Prozent" | Unchanged (FR-013). |
| gradient stops | palette stops at value fractions: `0 → #ffd524`, `12 → #e6854a`, `24 → #a97e65`, `24.08 → #0674aa`, `32 → #1db6ff`, `40 → #39c2ff`, `48 → #56ceff`, `80 → #6ad4ff`, held to 100 | Continuous bar, no gaps (FR-010/FR-011); the cap at 80 is the existing palette behavior. |
| tick labels | `0`, `15`, `30`, `50`, `100` at `left: 0%, 15%, 30%, 50%, 100%` | Value-proportional positions (FR-012). |
| screen-reader text | `role="img"` + `aria-label` + visually-hidden value list | FR-018: values exposed as text, not only visual marks (research R-004). |

**Invariants**:
- No segment renders as an unintended color: every gradient pixel is
  a convex combination of adjacent frozen palette stops (spec edge
  case "gradient interpolation").
- All five tick labels remain visible without clipping at desktop
  and ≤480 px widths (SC-005, US3 acceptance 4).
- The legend card stays top-left at desktop, collapses to the bottom
  strip at ≤480 px (existing media query, unchanged position rules).

## E-006 — BasemapInvertedLayer

Second raster layer sharing the `basemap` source; renders the
photo-negative used at very low brightness (FR-019).

| Field | Value | Notes |
|---|---|---|
| `layer.id` | `"basemap-inverted"` | New layer, inserted between `basemap` and `outside-mask`. |
| `source` | `"basemap"` | Same source as E-001 — tiles fetched once (SC-007). |
| `paint.raster-brightness-min` | `1` | With max 0, the shader computes `out = 1 - in` (research R-010). |
| `paint.raster-brightness-max` | `0` | Values in `[0,1]` — MapLibre clamps outside that range (research R-011). |
| `paint.raster-opacity` | `s(v)`, ramp 0→1 for slider 25→5 | Crossfade with the dimmed basemap; continuous, no seam (R-011/R-012). |
| `layout.visibility` | `"none"` when `s = 0`, else `"visible"` | Skips a wasted render pass at normal brightness. |

**Invariants**:
- Inverting gray yields gray: the low-brightness map stays grayscale
  (FR-019, contract invariant 1).
- The inverted layer never affects buildings, trees, mask, or popup
  content — it renders below `outside-mask` (FR-019).
- At slider ≥ 25 the layer is invisible; the default appearance
  (FR-003) is untouched.
- Background remains dark at minimum: measured p10 luminance ratio
  0.002 of default (SC-001; research R-012).

## E-005 — UI element placement (static set)

The five static elements governed by FR-008:

`ColorLegend` (top-left) · `ToolsCard` (left column, below legend) ·
NavigationControl (top-right, MapLibre-owned) · Attribution
(bottom-right) · Popup (transient — FR-017, excluded from the hard
pairwise constraint).

**Invariants**:
- Pairwise disjoint clickable areas at every width ≥320 px and every
  zoom level (SC-003, verification matrix in research R-005).
- The popup may transiently cover elements while open but must be
  dismissible and never permanently occlude a control (FR-017).
- Buildings-layer failure text in the attribution slot must not
  overlap other controls (spec edge case).

## Rendering Order

Unchanged from 003 except one added layer between the basemap and
the mask (bottom to top):

```
basemap            (brightness user-adjustable)
basemap-inverted   (photo-negative, opacity s(v); new — FR-019)
outside-mask       (black fill outside Mannheim — unchanged)
buildings-fill     (palette at 0.75 / 0.8 opacity — frozen)
buildings-line     (#555555 outlines — frozen)
trees-fill         (green, default hidden — frozen)
```

The inverted layer is the only addition; nothing is removed or
reordered (research R-011).

## State Transitions

One runtime state, session-scoped:

```
load      → slider 65; basemap max 0.65; inverted opacity 0 (hidden)
input ≥ 25→ slider v; basemap max v/100; inverted opacity 0 (hidden)
input < 25 → slider v; basemap max v/100; inverted opacity s(v) =
             clamp((25 − v)/20, 0, 1), layer made visible
input = 5  → basemap max 0.05; inverted opacity 1 (fully inverted)
reload    → all values discarded, back to load state (FR-007)
```
