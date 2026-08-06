# Research: Mobile-First Native UX

Research date: 2026-08-06.

Decisions are codebase-grounded (read `src/site/{index.html,main.js,style.css,style.json}`
via byte inspection; `tests/acceptance/test_style.py`, `tests/acceptance/test_values.py`,
`validation/perf-budget.json`, `DEVELOPMENT.md`, `Makefile`) and grounded in external UX/UI
research fetched live, not inference alone (spec input requirement). The spec is
presentation-only, so no external data or pipeline unknowns exist; the unknowns here are UI
pattern and accessibility choices, resolved by research R-1..R-6.

## R-1 Collapsible legend/summary surface: native map bottom sheet

**Decision**: Replace the permanent `#left-stack` column with one collapsible
legend/summary surface `#surface`. On mobile (< 768px) it is a bottom sheet: collapsed by
default to a compact thumb-reachable header strip, expanded by a single tap to a sliding
panel with internal scroll. On desktop (>= 768px) the identical component is a collapsible
panel top-left, expanded by default.

**Rationale**: The spec requires the map to be the dominant surface with legend/summary
content "collapsed behind a control" (FR-001, SC-001) and a single-tap expand/collapse
(FR-002). This is exactly the native map bottom-sheet convention: Google Maps uses a
multi-state bottom sheet that "peeks" with minimal info, expands to reveal details, and
collapses to return the map (Mobbin bottom-sheet glossary; stellae.design bottom-sheet UX
glossary; Dove Letter Google-Maps bottom sheet). Bottom sheets suit "quick, non-disruptive
actions tied to the current screen", which matches expand-to-understand / collapse-to-explore.
Desktop uses the same component set for consistency (FR-008) rather than a separate design.

**Alternatives considered**:
- Keep the static column but shrink it: rejected, still hides the map on phones (FR-001).
- Full-screen overlay panel on mobile: rejected, hides the map entirely and breaks
  "map dominant".
- Popover triggered by a single button: rejected for the legend, too small to hold the
  city-overview panel and tools comfortably.

## R-2 Tools live in the surface header (visible while collapsed)

**Decision**: Bäume toggle and Helligkeit slider stay in the always-present surface header,
not in the collapsible body. The collapsed surface is therefore a header-only strip that
still exposes both tools.

**Rationale**: The spec's legend/summary surface entity "holds legend title, gradient scale,
city-overview numbers, tools", and FR-004 requires Bäume and Helligkeit to "remain visible
and operable while legend collapsed". Putting the tools in the persistent header satisfies
FR-004 trivially, keeps them in the thumb-friendly lower zone (FR-003), and avoids a second
floating cluster that could overlap the zoom control or attribution (FR-005). This mirrors
native maps where the always-present bottom card header carries the primary actions.

**Alternatives considered**:
- Separate floating tools cluster on the map: rejected, adds an overlap risk with zoom
  (top-right) and attribution (bottom-right), and duplicates controls.
- Tools inside the expanded body only: rejected, violates FR-004 (must work collapsed).

## R-3 Touch-target sizing: 44x44 px minimum, 8 px spacing

**Decision**: All interactive controls on mobile (Bäume, Helligkeit slider, expand/collapse
toggle, zoom buttons, popup close) get a >= 44x44 px touch target with >= 8 px clear spacing
between adjacent targets. MapLibre's default NavigationControl buttons (29 px) are enlarged
to 44 px on mobile via CSS override.

**Rationale**: The consensus the spec cites is confirmed by research: WCAG 2.5.5 (Enhanced)
requires targets at least 44x44 px; Apple HIG uses 44 pt; Material uses 48 dp
(AAArdvark WCAG 2.5.5 plain-English; top10k touch-target checker; accessitool mobile touch
target guide). MIT Touch Lab measured the average fingertip at 16-20 mm wide, and motor-impaired
users see error rates up to 75% higher on small targets (testparty WCAG 2.5.8 guide). The
spec pins 44x44 and 8 px spacing; research confirms those are the standard, defensible values.
Zoom is explicitly a required 44 px control (FR-003), so the 29 px MapLibre default must be
overridden on mobile.

**Alternatives considered**:
- Material's 48 dp everywhere: rejected, spec pins 44 px minimum; 44 is WCAG/HIG-compliant.
- 24 px (WCAG 2.5.8 AA minimum): rejected, below the spec's own FR-003 requirement.

## R-4 Thumb-zone placement: frequent actions in the lower screen

**Decision**: On mobile the collapsed surface header (with tools and expand control) sits at
the bottom of the screen, and the zoom control stays top-right (FR-005). All primary actions
are reachable one-handed in the lower half.

**Rationale**: Steven Hoober's UXmatters one-handed research established that thumb reach
varies by grip but the bottom corners and lower half are the easiest to reach; the most
frequent actions belong there (parachutedesign thumb-zone guide; upslidedesignstudio
one-handed UX; timgraf thumb-zone guide). The spec's assumption is confirmed. Native map apps
place primary tooling in the lower zone while keeping zoom near a corner. Because the zoom
control must not be moved or overlapped (FR-005), we leave NavigationControl top-right
(unchanged) and put the tools in the bottom sheet header.

**Alternatives considered**:
- Move zoom to the bottom (Apple-Maps style): rejected, FR-005 requires zoom to stay and
  forbids overlap; moving it risks breaking the published-control placement contract.
- Tools top-left with the legend: rejected, out of thumb reach (FR-003).

## R-5 Safe-area + browser-chrome handling: dynamic viewport units and insets

**Decision**: Size the bottom sheet with dynamic viewport units (`dvh`/`svh` with a `vh`
fallback) and pad fixed chrome with `env(safe-area-inset-*)`. The sheet uses
`position: fixed` so it tracks the visual viewport; body scrolls internally so the browser
address bar never clips it (edge case).

**Rationale**: `100vh` is taller than the visible viewport on mobile and ignores the
collapsing address bar, causing layout shift and clipped content (sizzy.co CSS viewport units;
ishadeed new-viewport-units; csscodelab dynamic viewport units). `dvh`/`svh` adapt to the
dynamic toolbar and remove the visible jump (SC-005). `env(safe-area-inset-*)` clears notches
and the home indicator (FR-007). This is the standard mobile-safe technique.

**Alternatives considered**:
- Keep `100vh` + hard-coded bottom offsets: rejected, causes SC-005 layout shift and clips
  controls on notched devices.
- Listen for `visualViewport` resize events in JS: rejected, CSS-only `dvh` is simpler, no
  JS layout thrash, no new code paths.

## R-6 Motion: compositor-safe slide/scale, reduced-motion makes it instant

**Decision**: Expand/collapse uses `transform: translateY` + `opacity` transitions on the
surface body and a scale/rotate on the chevron. A global
`@media (prefers-reduced-motion: reduce)` block disables all transitions and animations,
making every state change instant and non-animated (FR-008).

**Rationale**: Transforming/opacity animates on the compositor and avoids layout jank,
protecting the interaction budget (SC-006). The spec requires native-feeling slide/scale
motion that honors reduced-motion preference (FR-008); `prefers-reduced-motion` is the
standard mechanism (Josh W. Comeau accessible animations; openreplay prefers-reduced-motion;
ArcGIS mapping reduced-motion). Disabling transitions under the media query yields instant
state changes exactly as FR-008 requires.

**Alternatives considered**:
- Animate layout properties (height/top): rejected, causes layout/paint jank and misses the
  interaction budget.
- Skip motion entirely: rejected, spec explicitly wants native-feeling motion for users who
  allow it.

## R-7 Popup clearance: map.setPadding instead of per-popup math

**Decision**: When the surface expands, call `map.setPadding({ bottom: sheetHeight })` (and
restore `{ bottom: 0 }` on collapse). MapLibre then keeps building and district popups fully
visible above the sheet at every map position (FR-006).

**Rationale**: The spec requires popups to "remain fully visible, legend surface expanded or
collapsed, map must keep popup clear of surface" (FR-006) and to reposition above the surface
when a tapped building is near the bottom (edge case). `map.setPadding` shifts the rendered
viewport, so MapLibre's automatic popup anchoring keeps any open popup clear of the bottom
padded area without hand-computed offsets per popup. It is the same mechanism MapLibre
supports natively and works identically for the desktop panel (padding is layout-agnostic).
This reuses the one persistent popup instances already wired in `main.js` (FR-001..FR-011),
so parity (FR-010) holds.

**Alternatives considered**:
- Manual `popup.setOffset` / repositioning on toggle: rejected, does not cover popups anchored
  in the padded band and needs per-popup bookkeeping.
- Move popup anchor above the sheet via map.easeTo: rejected, changes the camera, disruptive.

## R-8 Breakpoint: single 768 px threshold

**Decision**: A single layout breakpoint at 768 px: below = mobile bottom-sheet layout,
at/above = desktop collapsible panel. The current narrow-screen media query is 480 px; the
mobile-first mandate and the landscape-phone edge case justify 768 px.

**Rationale**: The spec requires a mobile-first layout and that desktop narrow windows "cross
into the mobile breakpoint" cleanly (edge case). Landscape phones commonly render 640-740 px
wide; 768 px captures them under the bottom-sheet layout so tools stay thumb-reachable and the
map dominant. The spec asks for one component set across sizes (FR-008), so a single
breakpoint that only changes surface geometry (fixed bottom sheet vs. absolute top-left panel)
is the minimal switch.

**Alternatives considered**:
- Keep 480 px: rejected, portrait-first only, misses landscape phones and medium tablets.
- Three breakpoints (e.g. 480/768/1024): rejected, YAGNI; the spec's two target form factors
  (phone, desktop) need one switch.

## Consolidated decisions for the plan

- One `#surface` component: header (title + tools + toggle) + body (legend + city overview).
- Mobile (< 768 px): fixed bottom sheet, collapsed by default, `dvh`-sized, safe-area padded.
- Desktop (>= 768 px): top-left collapsible panel, expanded by default.
- Tools in the persistent header (FR-004); zoom stays top-right (FR-005).
- 44x44 px targets, 8 px spacing, MapLibre zoom buttons enlarged on mobile (FR-003).
- `map.setPadding` for popup clearance (FR-006).
- `transform`/`opacity` motion + `prefers-reduced-motion: reduce` instant (FR-008).
- `dvh`/`svh` + `env(safe-area-inset-*)` for chrome/safe-area (FR-007, SC-005).
- Zero new network requests, no new dependencies, no build tool (FR-012).
