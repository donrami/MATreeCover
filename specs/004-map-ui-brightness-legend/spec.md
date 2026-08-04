# Feature Specification: Map UI, Brightness Slider & Gradient Legend

**Feature Branch**: `004-map-ui-brightness-legend`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "I think it would be nice to have a slider for the raster map brightness so the user can lower the brightness to almost black to see the building colors more prominently (good for editorial style images). And while we are at it, I want us to rework the UI elements placement to ensure no 2 elements overlap (such is currently the case with the Bäume button and the map zoom controls). Also regarding the map color legend, I would like to have it as a gradient bar and not discrete color categories, analogous to the legend of the reference project showcase https://schultz-web.de/StadtBegruenung/"

## Clarifications

### Session 2026-08-04

- Q: Should the brightness slider cover only dimming, or the full range from near-black up to the original light basemap? → A: Full range; the default position reproduces today's darkened appearance.
- Q: Should the brightness control be permanently visible or collapsible? → A: Permanently visible as a standalone control on the map at all viewport sizes.
- Q: How should street lines and text labels stay visible when brightness is very low? → A: Invert the base map in the low-brightness range (photo-negative): streets and labels render as lighter gray on the dark background, all map detail stays readable, no new data.

## Scope

### Goal

Three related frontend refinements to the published map:

1. Give visitors a **brightness slider** for the raster base map that can dim it to near-black, so building tree-cover colors dominate the image (editorial-style output).
2. **Rework the UI element placement** so no two elements overlap at any supported viewport size and zoom level (today the Bäume toggle overlaps the map zoom controls).
3. Replace the **discrete color-swatch legend** with a **continuous gradient bar**, analogous to the legend of the reference project https://schultz-web.de/StadtBegruenung/.

### In Scope

- A user-adjustable brightness control for the raster base map, spanning the full range from near-black up to the original un-darkened basemap appearance, with the default position reproducing today's published appearance.
- Live brightness updates while the user adjusts the control; no reload or confirm step.
- A default control position that reproduces today's published appearance exactly, so existing visitors see no change on load.
- Rework of map UI placement (legend card, Bäume toggle, zoom controls, attribution, popup) so elements never overlap at any supported viewport width (≥320 px) and any zoom level, including the existing narrow-screen responsive layout (≤480 px).
- A legend rendered as one continuous gradient bar spanning the building palette, with value labels 0, 15, 30, 50, 100 at positions proportional to their values, matching the reference project's presentation.
- The change applies at every zoom level and only affects presentation; no data or pipeline changes.

### Out Scope

- Any change to the building color palette, value scale, tree layer styling, popup content, or hover behavior.
- Persisting the slider position across page reloads or sessions (session-only control).
- Dark-mode or theme systems, base map provider changes, or map-style inversion.
- Anything outside Mannheim; no changes to map data, values, tiles, or pipeline artifacts.
- No new network requests: dimming and the gradient legend are client-side visual changes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dim the Base Map for Editorial-Style Images (Priority: P1)

A journalist or editor wants a dramatic map image where the building tree-cover colors are the focal point. They drag the brightness slider down; the base map fades continuously from its default appearance toward near-black, and the building colors stay at full strength. At the lowest setting the map is almost black, with buildings clearly glowing in the foreground; street lines and text labels invert to a lighter gray so the map stays readable as a dark backdrop.

**Why this priority**: This is the primary request; without the slider the feature has no value.

**Independent Test**: Load the published map, drag the slider from default to minimum, and observe the base map dim continuously while building colors stay unchanged. Deliverable: a working brightness slider with a near-black minimum.

**Acceptance Scenarios**:

1. **Given** the map loaded at the default view, **When** the user drags the brightness slider downward, **Then** the raster base map dims continuously (no jumps) toward near-black.
2. **Given** the brightness slider at its lowest position, **When** a visitor views buildings, **Then** every building palette color remains clearly distinguishable from the near-black background.
3. **Given** the map loaded with the slider at its default position, **When** the page renders, **Then** the appearance is identical to today's published map (no visual regression on load).
4. **Given** the slider lowered, **When** the visitor clicks a building, **Then** the popup opens normally with unchanged content.
5. **Given** the tree layer toggled on, **When** the slider is lowered, **Then** tree polygons remain clearly visible at full opacity.
6. **Given** the slider released at a mid-range position, **When** the user then pans or zooms, **Then** the brightness stays at the chosen value (no snap-back, no interference with map gestures).
7. **Given** the slider raised above the default position, **When** a visitor views the map, **Then** the base map brightens continuously toward the original un-darkened appearance.
8. **Given** the brightness slider at its lowest position, **When** a visitor views the map, **Then** street lines and text labels render in a lighter gray than the background and remain legible (inverted base map).

### User Story 2 - Clean, Non-Overlapping Controls (Priority: P1)

A visitor wants to toggle the Bäume layer, zoom the map, and adjust the new brightness control. Today the Bäume button overlaps the map zoom controls, so one of them is hard to reach. After the rework, every control occupies its own space: the brightness control, zoom controls, Bäume toggle, legend, and attribution never overlap at any viewport size or zoom level; the popup, when open, may cover them only transiently and must remain dismissible.

**Why this priority**: The overlap is a visible, user-reported defect that blocks normal use of two controls; fixing placement is required for a usable map.

**Independent Test**: Load the map at several viewport widths and zoom levels and verify that the clickable areas of all UI elements are pairwise disjoint and each control responds to clicks. Deliverable: no two elements overlap in any tested configuration.

**Acceptance Scenarios**:

1. **Given** the map loaded on a desktop viewport, **When** the zoom controls and the Bäume toggle render, **Then** neither occludes the other and both are fully clickable.
2. **Given** any supported viewport width (≥320 px), **When** all UI elements render, **Then** no two elements' clickable areas overlap.
3. **Given** a narrow screen (≤480 px), **When** the legend collapses to its bottom-strip form and controls stack, **Then** no overlap occurs and every control remains reachable.
4. **Given** the user clicks the location where the overlap existed before, **When** the click lands, **Then** the intended control responds; no control is unreachable due to occlusion.
5. **Given** a building near the viewport edge is clicked, **When** the popup opens, **Then** it can be dismissed and does not permanently cover any other control.

### User Story 3 - Gradient Legend Bar (Priority: P2)

A visitor reads the legend to interpret building colors. Instead of separate color swatches, the legend shows one continuous gradient bar from the lowest to the highest tree-cover value, with the value labels 0, 15, 30, 50, 100 placed along the bar at positions proportional to their values — just like the reference project https://schultz-web.de/StadtBegruenung/. Any building color can be matched to a point on the bar.

**Why this priority**: The gradient is a presentation improvement; the slider and the overlap fix have higher user impact. Still independently valuable for legibility.

**Independent Test**: Load the map, confirm the legend renders as a single continuous gradient bar with all five value labels visible, and compare building colors against the bar. Deliverable: a gradient legend matching the reference presentation.

**Acceptance Scenarios**:

1. **Given** the map loaded, **When** the legend renders, **Then** it shows one continuous gradient bar with no gaps or segment boundaries between colors.
2. **Given** the gradient bar, **When** a visitor reads it, **Then** the labels 0, 15, 30, 50 and 100 are visible at positions corresponding to their values along the bar.
3. **Given** the gradient bar, **When** a visitor compares a building's color to the bar, **Then** the building color matches a point on the bar (gradient endpoints and interior colors derive from the building palette).
4. **Given** a narrow screen, **When** the legend collapses to its bottom strip, **Then** the gradient legend remains fully visible and its labels do not clip or overlap.
5. **Given** the legend card, **When** a visitor reads the unit caption, **Then** the existing title, description, and unit information remain present; only the presentation of the color scale changes.

### Edge Cases

- Slider at minimum: the base map inverts, so street lines and labels stay legible as light gray on the near-black background; building colors must stay distinguishable.
- Dragging the slider must not pan or zoom the map, and panning/zooming must not reset the slider.
- Touch devices: the slider must be usable by touch without conflicting with the zoom controls.
- Keyboard users: the slider must be operable via keyboard (focus, arrow keys) and announce its value.
- Viewport resized while the slider is mid-drag: layout must re-flow without overlap and without losing the chosen brightness.
- Dense-label, high-zoom areas: zoom controls and the Bäume toggle must stay separated at every zoom level.
- Buildings-layer failure (existing error surface in the attribution slot): the error message must not overlap other controls.
- Gradient interpolation across the palette (yellow → orange → brown → blue → light blue): no segment may render as an unintended color; the gradient follows the palette stops.
- Very low brightness combined with tree layer on: trees must remain visible against the near-black map.
- Low-brightness inversion: the transition from normal dimming to the inverted base map must be gradual across the low end of the slider range, with no sudden switch; the inverted map must stay grayscale (no hue shift), and buildings must remain distinguishable over it.
- Narrow screens: the permanently visible brightness control must remain reachable and non-overlapping in the stacked layout (≤480 px).
- Screen readers: the gradient bar must not regress legend accessibility — the value labels must remain available as text, not only as visual marks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The map MUST provide a user-adjustable brightness control for the raster base map.
- **FR-002**: Adjusting the brightness control MUST change the raster base map continuously across the full range: lowering it dims the map to near-black, raising it brightens the map back toward its original un-darkened appearance.
- **FR-003**: The control's default position MUST reproduce the current published appearance of the base map on load.
- **FR-004**: The brightness control MUST affect only the raster base map; building colors, tree layer, and popup content MUST remain unchanged at any brightness setting.
- **FR-005**: Brightness changes MUST take effect live while the user adjusts the control, without a confirm step or page reload.
- **FR-006**: The brightness control MUST remain usable (pointer drag, touch, keyboard) without interfering with map pan, zoom, or the other UI controls.
- **FR-007**: The brightness value MUST NOT persist across page reloads or sessions.
- **FR-008**: No two static UI elements (brightness control, zoom controls, Bäume toggle, legend, attribution) MAY overlap at any supported viewport width (≥320 px) and any zoom level.
- **FR-009**: The Bäume toggle MUST remain a fully clickable control, not occluded by any other element.
- **FR-010**: The map color legend MUST render as a continuous gradient bar instead of discrete color categories.
- **FR-011**: The gradient bar MUST span the building palette from lowest to highest tree-cover value with no gaps.
- **FR-012**: The legend MUST display the value labels 0, 15, 30, 50 and 100 at positions proportional to their values along the gradient bar.
- **FR-013**: The legend MUST retain its existing title, description, and unit label; only the presentation of the color scale changes from discrete swatches to a gradient bar.
- **FR-014**: Existing interactions (building click popup, hover pointer, Bäume toggle, empty-space close) MUST behave unchanged.
- **FR-015**: The change MUST NOT add new network requests or alter map data, tiles, or any pipeline artifact.
- **FR-016**: The brightness control MUST be permanently visible on the map as a standalone control at all supported viewport sizes (≥320 px); it MUST NOT be hidden behind a toggle or menu.
- **FR-017**: The popup MAY transiently cover other elements while open, but MUST remain dismissible and MUST NOT permanently occlude any control.
- **FR-018**: The gradient legend MUST remain interpretable by screen readers; the value labels MUST be exposed as text, not only as visual marks.
- **FR-019**: At very low brightness settings, the base map MUST render inverted so that street lines and text labels appear lighter than the map background; the inversion MUST preserve the map's grayscale character and MUST NOT affect building colors, the tree layer, or popup content.

### Key Entities *(include if feature involves data)*

- **Base Map (raster)**: the grayscale street map with baked-in labels shown behind all data layers; the entity the brightness control dims.
- **Building Footprint**: polygon colored by tree-cover value (yellow-to-blue scale) or marked unavailable (gray); must stay at full color so it stands out against the dimmed map.
- **Tree Layer**: optional detected-tree polygons toggled by the Bäume button; must remain clearly visible at any brightness.
- **Color Legend**: the gradient-bar representation of the building color scale; communicates the value-to-color mapping and its unit.
- **UI Controls**: brightness control, zoom controls, Bäume toggle, attribution slot, and popup; the static controls must occupy pairwise non-overlapping screen regions at all supported viewports, and the popup must remain dismissible.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Moving the brightness control from default to minimum dims the base map's background to below 10% of its default background luminance (feature pixels excluded — their legibility is covered by SC-008), and moving it to maximum restores the original un-darkened luminance (measured on the same viewport, zoom, and area).
- **SC-002**: At minimum brightness, 100% of building palette colors remain distinguishable from the near-black background (contrast check at the default zoom).
- **SC-003**: In a viewport matrix of at least 5 widths (≥320 px) and 3 zoom levels, 100% of UI-element pairs have zero overlapping clickable areas.
- **SC-004**: At the former overlap location, the Bäume toggle receives clicks 100% of the time (no occlusion).
- **SC-005**: The legend renders as a single continuous gradient; the labels 0, 15, 30, 50 and 100 are all visible at their proportional positions on both a desktop and a narrow (≤480 px) viewport.
- **SC-006**: No regression: building click popup, hover pointer, Bäume toggle, and empty-space close pass the existing smoke checklist unchanged.
- **SC-007**: No added network cost: the page loads the same tiles and data; dimming and the gradient legend are client-side visual changes.
- **SC-008**: At the minimum brightness setting, sampled street lines and text labels measure lighter than the surrounding background (per-pixel feature luminance exceeds background luminance) and remain legible by eye; the base map stays grayscale.

## Assumptions

- The brightness slider is session-only; its default position reproduces today's already-darkened base map (the result of the darken-base-map feature, 003).
- The slider spans the full range from near-black up to the original un-darkened basemap; the default position reproduces today's darkened appearance. Brightening above the default is permitted and simply restores the pre-darkening light map.
- At low brightness, street lines and labels remain visible through inversion rather than fading; buildings remain the focal point against the dark backdrop.
- The tree layer, when toggled on, renders at full opacity regardless of base-map brightness.
- The gradient legend interpolates linearly between the existing palette stops; tick labels are 0, 15, 30, 50, 100, matching both the current legend and the reference project.
- Supported viewports are at least 320 px wide, with the existing responsive breakpoint at 480 px preserved.
- No persistence, no new data, no pipeline changes; purely client-side visual and layout changes.
- The existing darker default (003) remains the baseline; the slider extends it into a user-controlled value rather than replacing it.
- The brightness control is permanently visible as a standalone control; no collapsible or toggle behavior is required.
- In the low-brightness range the base map renders inverted (negative image): originally dark features (streets, labels) appear as lighter gray on the dark background. The inversion engages gradually below approximately 25 on the slider and is fully active at the minimum; only the raster base map is transformed.

## Dependencies Evidence

- The base map is a grayscale raster (basemap.de `de_basemapde_web_raster_grau`) rendered beneath all data layers in `src/site/style.json`; it already carries a static darkening paint property from the darken-base-map feature (003), which this slider extends into a user-controlled value.
- The map zoom control (MapLibre NavigationControl) is added at the top-right (`src/site/main.js`, `onMapLoad`); the Bäume toggle is positioned below it (`src/site/style.css`, `#controls` comment "top-right below the navigation control") — the documented source of the reported overlap.
- The legend currently renders discrete color swatches for the values 0, 15, 30, 50, 100 (`src/site/index.html`, `#legend`); the reference project https://schultz-web.de/StadtBegruenung/ presents the same five values on a continuous gradient bar.
- The building palette spans yellow (`#ffd524` at 0%) through orange/brown to blues (`#6ad4ff` at 100%); the gradient bar must interpolate through these stops.
- Feature 003 (darken-base-map) established the darker default appearance and is the prerequisite for this feature's default slider position.
- The site is a static, no-build bundle (vendored MapLibre + PMTiles, CSP `default-src 'self'`); visual changes must stay client-side with no added downloads (perf-budget contract in `validation/perf-budget.json`).
