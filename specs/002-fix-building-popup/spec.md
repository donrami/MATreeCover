# Feature Specification: Fix Building Popup Interaction

**Feature Branch**: `main`

**Created**: 2026-08-04

**Status**: Draft

**Input**: Building selection currently does not work reliably. Clicking a
building opens the value popup. Clicking a second building closes the
popup instead of showing the second building's value. The interaction
should be redesigned so the compact value popup reliably follows building
clicks. Interview (2026-08-04): keep the compact value popup. Clicking any
building shows that building's value. Clicking empty map space closes the
popup.

## Scope

### Goal

Make building selection predictable: clicking any building always shows
that building's tree-cover value in the compact popup. At most one popup is
open at any time. Clicking empty map space dismisses it.

### In Scope

- One popup at a time, showing the last clicked building's value.
- Clicking a building always shows that building's value, replacing the
  previous popup.
- Clicking empty map space closes the open popup.
- The popup close button keeps working.
- Buildings without a valid value keep showing the unavailable marker,
  never a false zero.
- Hover selection pointer unchanged.
- Same behavior for touch taps.
- Building clicks remain selectable when the tree layer is visible.

### Out Scope

- Any popup content beyond the current value: no address, building ID,
  completeness display, or links.
- Hover tooltips or hover highlighting.
- Side panels, detail views, lists, or any layout outside the popup.
- Changes to value computation, palette, building properties, or pipeline
  data.
- Changes to camera, zoom, or pan behavior.
- Anything outside Mannheim.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select Any Building Value (Priority: P1)

visitor clicks buildings in sequence; every click shows the clicked
building's tree-cover value. Clicking empty space dismisses the popup.

**Why priority**: the popup is the only way to read a building's value
(FR-014 of the base feature). A popup that vanishes on the second click
makes the map unusable for comparison.

**Independent Test**: On the published bundle, click ten distinct
buildings in a row. Confirm the popup re-opens on every click with that
building's value and that no second popup ever appears.

**Acceptance Scenarios**:

1. **Given** map loaded with buildings, **When** visitor clicks a
   building, **Then** a compact popup shows that building's tree-cover
   value with two decimal places.
2. **Given** popup showing building A's value, **When** visitor clicks
   building B, **Then** popup now shows building B's value. Popup never
   closes on a building click.
3. **Given** popup open, **When** visitor clicks a map point that has no
   building, **Then** popup closes.
4. **Given** popup open, **When** visitor presses the close button,
   **Then** popup closes.
5. **Given** building with no valid value, **When** visitor clicks it,
   **Then** popup shows the unavailable marker, never `0.00%`.
6. **Given** popup open on building A, **When** visitor clicks building A
   again, **Then** popup stays open showing building A's value.
7. **Given** tree layer visible, **When** visitor clicks a building
   partly covered by tree areas, **Then** popup shows that building's
   value.

### Edge Cases

- Rapid clicks between two buildings: popup must always reflect the last
  clicked building, with no moment where two popups exist.
- Click on the popup itself (body or close button) must not re-trigger
  building selection underneath.
- A click on the boundary mask or outside Mannheim is empty space and must
  close the popup.
- Clicking a building after the popup was closed by empty-space click must
  re-open the popup normally.
- Repeated clicks on the same point must not accumulate popups.
- A building at the very edge of the viewport: popup must stay within the
  visible area.
- Buildings layer failure must not change popup behavior for whatever
  renders.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Product MUST keep the compact popup showing a building's
  tree-cover value to two decimal places (refines FR-014 of the Mannheim
  Tree-Cover Parity feature).
- **FR-002**: Clicking any building MUST open the popup for that building
  and replace any popup currently open.
- **FR-003**: At most one popup MUST be open at any time.
- **FR-004**: Clicking a map point that contains no building MUST close the
  open popup.
- **FR-005**: The popup close button MUST close the popup.
- **FR-006**: A building click MUST never close the popup. It always
  selects the clicked building.
- **FR-007**: A building without a valid value MUST show the unavailable
  marker in the popup, never a zero value.
- **FR-008**: Hovering a building MUST keep showing the selection pointer.
- **FR-009**: Touch taps MUST behave like mouse clicks for open, replace,
  and close.
- **FR-010**: Tree layer visibility MUST NOT block or alter building
  selection.
- **FR-011**: After a popup is closed, the next building click MUST re-open
  the popup normally.

### Operational Constraints

- No change to the published data or its acceptance state is allowed.
  This feature is frontend behavior only.

## Key Entities

- **Building Footprint**: accepted official building geometry with an
  optional tree-cover value (two decimals or unavailable).
- **Selection Popup**: the single compact popup showing the currently
  selected building's value. Its state is open or closed, and which
  building it shows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the published bundle, a sequence of ten distinct building
  clicks shows the correct value for each clicked building. The popup
  count never exceeds one at any moment.
- **SC-002**: At least 95% of building clicks show the clicked building's
  value within two seconds.
- **SC-003**: Every empty-space click closes the popup (ten trials).
- **SC-004**: A visitor can read the tree-cover value of any building
  within 30 seconds without instructions.
- **SC-005**: No regression: hover pointer, close button, and unavailable
  marker still pass the US2 smoke checklist.

## Assumptions

- The popup anchors at the click point, matching the reference
  CityTreeCover behavior. It does not move to the building centroid.
- Popup content stays as today: German label "Baumanteil im 60-m-Umkreis"
  and the value. No content changes.
- Hover feedback stays a pointer cursor. No hover highlight or tooltip.
- Touch taps reuse the map's standard tap-to-click handling. No custom
  touch logic.
- The published dist bundle is the source of truth for verification.

## Dependencies Evidence

- Current implementation: `src/site/main.js` `wireBuildingsInteractions`
  creates a new popup per building click. The popup library version in use
  defaults to closing a popup on any map click, so a second building click
  closes the popup instead of showing the second building's value.
- Defect reproduced in browser against the published bundle: click
  building A opens "Baumanteil im 60-m-Umkreis / 4.21%". Click building B
  closes the popup entirely (popup count returns to zero).
- Reference behavior: CityTreeCover `website/app.js` opens the value popup
  at the click point on every building click.
- Base feature: Mannheim Tree-Cover Parity, FR-014 (hover pointer +
  compact value popup), US2 smoke checklist `tests/frontend/smoke_us2.md`.
