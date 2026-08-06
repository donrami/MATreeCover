# Data Model: Mobile-First Native UX

This feature is presentation-only (FR-010): it introduces no user data, no persistence, and no
network state. The entities below are the **UI component and viewport state model** that drives
the responsive layout. They are the contract the frontend (`src/site/index.html`,
`main.js`, `style.css`) and the acceptance tests must satisfy.

State is session-only and lives in the DOM (a class on `#surface`). Nothing is written to
`localStorage`, no server round-trip, no new `fetch` (FR-012).

## Entities

### 1. Legend/Summary Surface (`#surface`)

The single shared component that replaces the static `#left-stack`. One component, two
geometries depending on the viewport breakpoint (FR-008).

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | `surface` |
| `mode` | enum `bottom-sheet` / `panel` | Derived from viewport width: `< 768px` = bottom-sheet (fixed, bottom); `>= 768px` = panel (absolute, top-left). Pure CSS. |
| `state` | enum `expanded` / `collapsed` | DOM class `is-collapsed`; `aria-expanded` mirrors it on the toggle. |
| `defaultState` | `collapsed` (mobile) / `expanded` (desktop) | FR-001 (mobile collapsed by default); desktop starts expanded to match current behaviour. |
| `header` | element `.surface-header` | Always present. Holds legend title, Bäume toggle, Helligkeit slider, expand/collapse toggle. |
| `body` | element `.surface-body` | The collapsible part. Holds full legend (desc, gradient, ticks, units, note) + city-overview panel. |
| `height` | dynamic | Mobile expanded: `min(55dvh, 100dvh - safe-area)`, `overflow-y: auto`. Collapsed: header height only. |

**Relationships**
- Owns (contains) the **Map Tool Controls** in its header (R-2).
- Contains the **City Overview** content in its body (moved from the old `#city-panel` in the
  left stack; unchanged markup/logic otherwise).
- Drives **Viewport/Chrome State**: expanding changes `map.setPadding`, which repositions
  **Map Popups**.

**State transitions**

```text
collapsed --(single tap on toggle; aria-expanded true)--> expanded
expanded  --(single tap on toggle; aria-expanded false)--> collapsed
```

Transition rules:
- Collapsed (mobile) MUST leave the map occupying >= 80% of the viewport height (SC-001).
- Expand MUST show the body without a page reload and MUST keep the map visible above the
  sheet (FR-002).
- The toggle MUST be keyboard-operable (Enter/Space) and announce state via `aria-expanded`
  (FR-014).
- Motion is a slide/scale `transform`/`opacity` transition; under
  `prefers-reduced-motion: reduce` the state change is instant (FR-008).

### 2. Map Tool Controls

Bäume toggle + Helligkeit slider. Always visible and operable whether the surface is
collapsed or expanded (FR-004). They live in the surface header, so the collapsed bottom-sheet
strip still exposes them.

| Field | Type | Notes |
|-------|------|-------|
| `baeume` | button | Existing `#baeume`; `aria-pressed`; toggles `trees-fill` visibility. Unchanged behaviour (FR-010). |
| `brightness` | range input | Existing `#brightness-slider`; maps 5..100 to `raster-brightness-max`. Unchanged behaviour (FR-010). |
| `touchTarget` | px | >= 44x44 on mobile, >= 8 px spacing (FR-003). |
| `placement` | zone | Surface header, thumb-friendly lower zone on mobile (FR-003). |

**Relationships**
- Contained by the surface header (R-2).
- Must never overlap the zoom control (top-right) or attribution (bottom-right) (FR-005).

### 3. Map Popups

Building value popup and district statistics popup. Persistent single instances already wired
in `main.js` (FR-001..FR-011); behaviour and content unchanged (FR-010).

| Field | Type | Notes |
|-------|------|-------|
| `buildingPopup` | MapLibre Popup | Class `building-popup`. Value + district context lines. |
| `districtPopup` | MapLibre Popup | Class `district-popup`. District stats. |
| `clearance` | rule | MUST stay fully visible above the surface when expanded or collapsed (FR-006). |

**Clearance invariant**: whenever the surface state changes to `expanded`,
`map.setPadding({ bottom: sheetHeightPx })` is applied; on `collapsed` it is reset to
`{ bottom: 0 }`. MapLibre then keeps any open popup above the padded band at every map
position, including a building tapped near the bottom (R-7, edge case).

### 4. Viewport/Chrome State

Responsive layout state derived from screen width, safe-area insets, and browser-chrome
visibility. It drives which geometry the surface uses and how controls are padded.

| Field | Type | Notes |
|-------|------|-------|
| `breakpoint` | `< 768px` / `>= 768px` | Selects bottom-sheet vs. panel. Pure CSS media query (R-8). |
| `viewportHeight` | dynamic | Sized with `dvh`/`svh` (fallback `vh`) so the sheet matches the visible viewport as the browser address bar shows/hides, avoiding layout jump (FR-007, SC-005). |
| `safeInsets` | `env(safe-area-inset-*)` | Padding applied to the bottom sheet and fixed chrome to clear notches/home indicator (FR-007). |
| `reducedMotion` | `prefers-reduced-motion: reduce` | Forces instant, non-animated state changes (FR-008). |
| `mapPadding` | `{ bottom: number }` | Mirrored from the surface state; feeds popup clearance (R-7). |

**Invariants**
- Zero visible layout shift when the browser address bar or home indicator appears/hides
  (SC-005).
- Surface and controls are never clipped or partially hidden behind safe-area insets or
  browser chrome (FR-007).
- On very small phones (>= 320 px) and landscape phones the surface and controls never
  overflow the viewport (edge cases).

## Not data

The map data layer is untouched: `style.json` palette, layer order, metadata
(`mannheim_bbox`, `city_stats`), and every source stay verbatim (SC-004). No new layer, no new
source, no new fetch (FR-012). The only change to the pipeline is none: `src/pipeline/` is not
modified by this feature.

## Validation summary

- FR-001/SC-001: collapsed surface leaves map >= 80% viewport height on mobile.
- FR-002: single-tap expand/collapse from the thumb zone.
- FR-003: every interactive control >= 44x44 px with >= 8 px spacing on mobile.
- FR-004: tools visible/operable while collapsed.
- FR-005: zoom and attribution never overlapped.
- FR-006: popups fully visible with surface expanded or collapsed.
- FR-007/SC-005: safe-area + chrome adaptation, no layout shift.
- FR-008: slide/scale motion; reduced-motion instant.
- FR-010: no feature added/removed/renamed.
- FR-014: keyboard operable, visible focus, WCAG AA, ARIA labels.
