# Feature Specification: Darken Base Map

**Feature Branch**: `main`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "I was wondering if he can make the base map a bit darker to see the building colors better"

## Clarifications

### Session 2026-08-04

- Prior feature (002-fix-building-popup) interview explicitly deferred base-map darkening to its own spec: "track base-map darkening as its own spec/branch later." This spec is that follow-up.
- No new clarifications required: the request is a single, well-bounded visual change. "A bit darker" is interpreted as a noticeable darkening that stays within the existing grayscale character of the map and keeps map labels legible (see Assumptions).

## Scope

### Goal

Make building tree-cover colors easier to distinguish by darkening the base map behind them. The map stays a grayscale street map with legible labels; only its overall background tone changes.

### In Scope

- Darkening the base map background so it is visibly darker than today.
- Keeping the map's grayscale character (no new hues that compete with the building color scale).
- Keeping street and district labels legible after darkening.
- Keeping all overlay layers (buildings, trees) visible and distinguishable on the darkened background.
- The change applies at every zoom level.

### Out Scope

- Any change to the building color palette or value scale (yellow-to-blue tree-cover colors stay exactly as today).
- Any change to the tree layer styling, popup behavior, hover behavior, or the Bäume toggle.
- Any change to map data, value computation, or the pipeline.
- Dark-mode or map-style inversion, custom map themes, or changing the base map provider.
- Anything outside Mannheim.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Distinguish Building Colors on a Darker Map (Priority: P1)

A visitor opens the map to compare tree-cover values across buildings. Today the light gray base map washes out the building colors, especially the lighter end of the scale, making it hard to see which buildings have more tree cover at a glance. With a darker base map, each building's color stands out clearly against the background.

**Why priority**: This is the entire point of the request; without it the feature has no value.

**Independent Test**: Load the published map, hide buildings, and record the base map's brightness. Show buildings and confirm each palette color is clearly distinguishable against the background. Deliverable: a visibly darker base map with unchanged building colors.

**Acceptance Scenarios**:

1. **Given** the map loaded at the default view, **When** the base map renders, **Then** the base map is noticeably darker than the current published version (measured background luminance drops by at least 30%).
2. **Given** the map loaded, **When** a visitor looks at buildings, **Then** every building color in the palette is clearly distinguishable from the darkened background (no palette color blends into the background).
3. **Given** the map loaded, **When** a visitor compares two neighboring buildings with different values, **Then** the color difference is easier to perceive than on the current map.

### User Story 2 - Keep Map Context Readable (Priority: P2)

A visitor uses street names and district labels to locate buildings of interest. Darkening must not sacrifice that context.

**Why priority**: The map remains a navigation aid; illegible labels would trade one problem for another.

**Independent Test**: Load the map, zoom to a downtown area, and read ten street or district labels. All ten must remain legible.

**Acceptance Scenarios**:

1. **Given** the map loaded at a downtown zoom level, **When** a visitor reads street or district labels, **Then** all sampled labels remain legible against the darkened background.
2. **Given** the map loaded, **When** a visitor pans across the city, **Then** no area renders with labels that are unreadably low-contrast against the background.

### User Story 3 - Overlay Layers Stay Visible (Priority: P2)

A visitor toggles the tree layer and clicks buildings. Darkening must not hide the trees or gray "no value" buildings.

**Why priority**: Overlays are the product's data; they must survive a background change.

**Independent Test**: Toggle the tree layer on and off, and click a building without a value; confirm both remain clearly visible on the darkened map.

**Acceptance Scenarios**:

1. **Given** the tree layer toggled on, **When** a visitor views the map, **Then** tree polygons remain clearly visible against the darkened base map.
2. **Given** a building without a valid value, **When** a visitor views the map, **Then** the building's gray "unavailable" marker remains visible, distinct from the background.
3. **Given** the map loaded, **When** a visitor clicks buildings, **Then** popup and hover behavior are unchanged (no regression).

### Edge Cases

- Lightest palette color (yellow at 0% tree cover) must remain clearly visible on the darkened background.
- Gray "no value" buildings must not disappear into the darkened background.
- Zoom levels where the base map shows dense street detail: darkening must not make roads indistinguishable from background.
- Visitors with color-vision deficiency: grayscale character of the base map must be preserved so no new hue competes with the color scale.
- Slow connections: darkening must not add any new download or affect load time (same map tiles, same data).
- Label collision areas (city center): darkening must not reduce label legibility anywhere in the viewport.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The base map MUST render noticeably darker than the current published version.
- **FR-002**: The base map MUST remain grayscale; darkening MUST NOT introduce new hues.
- **FR-003**: Building tree-cover colors MUST remain exactly as today (palette and value scale unchanged).
- **FR-004**: Every building palette color MUST remain distinguishable from the darkened background.
- **FR-005**: Street and district labels MUST remain legible after darkening at all zoom levels.
- **FR-006**: The tree layer MUST remain clearly visible when toggled on.
- **FR-007**: Buildings without a valid value MUST remain visible and distinct from the background.
- **FR-008**: The darkening MUST apply at every zoom level, including the default view.
- **FR-009**: Existing interactions (building click popup, hover pointer, Bäume toggle, empty-space click) MUST behave unchanged.
- **FR-010**: The change MUST NOT alter map data, values, or any pipeline artifact; it is purely a visual change.

### Key Entities

- **Base Map**: the grayscale street map shown behind all data layers; carries labels and road detail. The entity being darkened.
- **Building Footprint**: polygon colored by tree-cover value (yellow-to-green scale) or marked unavailable (gray). Its appearance is the reason for the change and must not change.
- **Tree Layer**: optional detected-tree polygons shown over the map when toggled on; must stay visible.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Measured average background luminance of the base map drops by at least 30% versus the current published version (same viewport, same zoom, same area).
- **SC-002**: 100% of building palette colors pass a contrast check against the new background (each palette color is distinguishable from the background at default zoom).
- **SC-003**: At least 10 of 10 sampled street/district labels remain legible at a downtown zoom level.
- **SC-004**: No regression: building click popup, hover pointer, Bäume toggle, and empty-space close still pass the existing smoke checklist (US2/US3) unchanged.
- **SC-005**: No added network cost: the published bundle serves the same tiles and data; page load behavior is unchanged.

## Assumptions

- "A bit darker" means a clear, noticeable darkening of the background tone while the map stays a legible grayscale street map; it does not mean dark-mode inversion.
- The darkening applies uniformly across the map area; no per-zoom or per-region tuning is required.
- The building color palette, tree layer styling, and all interaction behavior are out of scope and stay untouched.
- The base map source and tile set remain unchanged; only its rendered appearance darkens.
- Color-vision safety is preserved by keeping the base map grayscale.

## Dependencies Evidence

- Current base map is a light grayscale raster (basemap.de `de_basemapde_web_raster_grau`) rendered underneath the buildings layer (`src/site/style.json`, layers `basemap` then `buildings-fill`).
- Building palette spans yellow (`#ffd524` at 0% tree cover) to light blue (`#6ad4ff` capped at high values), via orange/brown and dark blue; a light background reduces color discrimination, particularly for the light end of the scale.
- Feature 002 (fix-building-popup) interview on 2026-08-04 explicitly deferred base-map darkening to a separate feature.
- The reference CityTreeCover keeps a light base map; darkening is a deliberate, documented divergence for building-color contrast.
