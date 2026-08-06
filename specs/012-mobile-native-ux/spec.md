# Feature Specification: Mobile-First Native UX

**Feature Branch**: `012-mobile-native-ux`

**Created**: 2026-08-06

**Status**: Draft

**Input**: User description: "Now that the site is functional and published and getting good feedback, it is time to work on the UX/UI to provide a high quality experience with mobile first and native to ensure optimal interaction and space usage on both desktop and mobile without inflating the features too much. You should try to use skills and online resources for the UX/UI research and not depend only on inference."

## Scope

### Goal

Give the published Mannheim tree-cover map a high-quality, mobile-first, native-feeling experience on both phones and desktops. The map is currently desktop-first: a large legend card, a tools card, and a city-overview panel sit permanently in a left stack, which on a phone hides most of the map behind chrome. This feature reworks the presentation and interaction so the map is the dominant surface, every control is comfortable to use by hand, and the same components behave consistently across screen sizes. It changes how the existing interface looks and is operated, and it deliberately adds no new features.

Design direction is grounded in external UX/UI research, not inference alone:
- Native map conventions (Google Maps, Apple Maps): a full-bleed map, minimal permanent chrome, an expandable legend surface, and floating tool controls in the thumb-reachable zone.
- Thumb-zone ergonomics: the lower half of the screen and the bottom corners are the easiest to reach one-handed, so frequent actions live there.
- Touch-target consensus: WCAG 2.5.5 (minimum 44x44), Apple HIG (44 pt), Material (48 dp), with spacing between adjacent targets.

### In Scope

- Reorganize the mobile layout so the map fills the screen; legend, city-overview, and tools present as compact, expandable surfaces instead of a permanently stacked column.
- Place every interactive control on mobile within the thumb-friendly lower zone, at native touch-target size with adequate spacing, without overlapping the zoom control or attribution.
- Keep popups (building, district) fully visible; the legend surface must never hide the tapped building's popup.
- Treat the layout robustly across viewport changes: safe areas (notch, home indicator), browser chrome show/hide, small and landscape phones, and desktop narrow windows.
- Use native-feeling motion (slide, scale) for expand/collapse and surface transitions, and honor reduced-motion preference.
- Make the desktop layout share the same components and behavior as mobile, space-optimized, with the map dominant.
- Preserve every existing feature and its behavior (Bäume toggle, Helligkeit slider, first-visit story modal, city-overview panel, district popup, attribution, Impressum).

### Out of Scope

- New data, new map views, new tools, or new content sections (no feature inflation).
- Changing the tree-cover values, color semantics, or the 30% shade guideline.
- Rewriting the site in a native language or framework; "native feel" means native-like web interaction patterns, not native code.
- Adding analytics, accounts, or a server.
- Altering existing German copy content or the accuracy disclaimer (feature 010).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mobile Map That Uses Every Pixel (Priority: P1)

A visitor opens the map on a phone. Instead of a tall stack of cards covering most of the screen, they see the map filling the display. The legend, city-overview numbers, and controls no longer permanently block the map; they are tucked behind a compact, thumb-reachable surface the visitor can expand when they want the explanation, then collapse to keep exploring. Single-tap a building, pinch to zoom, and drag to pan all work naturally with no overlay getting in the way.

**Why this priority**: Mobile-first and maximum map space are the explicit core of this feature. A phone visitor gets the largest possible usable map with the least permanent chrome, which is the single biggest quality improvement.

**Independent Test**: Open the published bundle in a narrow (mobile) viewport and verify the map fills the screen with the legend collapsed, then expand and collapse the legend with one tap and confirm building taps still work while collapsed.

**Acceptance Scenarios**:

1. **Given** a mobile viewport, **When** the page loads, **Then** the map is the dominant surface and the legend/summary content is collapsed by default behind a visible control.
2. **Given** the collapsed legend surface, **When** the visitor taps the expand control, **Then** the surface expands smoothly and reveals the legend, city-overview, and controls without reloading or hiding the map.
3. **Given** the expanded surface, **When** the visitor taps the collapse control, **Then** the surface collapses and the map regains the full viewport.
4. **Given** the collapsed surface, **When** the visitor taps a building, **Then** the building value popup opens and remains fully visible (not hidden behind the surface).
5. **Given** a mobile viewport, **When** the visitor pinches, drags, or taps, **Then** the map gestures respond immediately and the collapsed surface does not intercept or block them.

---

### User Story 2 - Native-Size, Thumb-Reachable Tools (Priority: P2)

On a phone, the tools the visitor actually uses (Bäume toggle, Helligkeit slider, legend expand/collapse, zoom, popup close) sit within the lower thumb-friendly zone at a comfortable size. Each control is large enough to tap accurately without a second attempt, adjacent controls are spaced so a thumb does not accidentally hit the wrong one, and the brightness slider is easy to grab and drag. The tools stay accessible even when the legend is collapsed.

**Why this priority**: Native feel depends on comfortable, ergonomic controls. Tools are secondary to exploring the map but essential to using it, so they rank above desktop polish but below the mobile-first map surface.

**Independent Test**: In a mobile viewport, measure every interactive control's touch target and spacing, and confirm the tools are reachable one-handed in the lower half of the screen while the legend is collapsed.

**Acceptance Scenarios**:

1. **Given** a mobile viewport, **When** all interactive controls are measured, **Then** each has a touch target of at least 44x44 px with at least 8 px clear spacing from adjacent targets.
2. **Given** the collapsed legend surface, **When** the visitor looks for the Bäume toggle and Helligkeit slider, **Then** both remain visible and operable without expanding the legend.
3. **Given** a mobile viewport, **When** the visitor uses the brightness slider with one hand, **Then** the slider thumb is large enough to grab and drag without the browser zooming or a nearby control being triggered.
4. **Given** the map's zoom control, **When** the new mobile controls are placed, **Then** none of them overlap the zoom control or the attribution.

---

### User Story 3 - Consistent, Space-Optimized Desktop (Priority: P3)

On a desktop, the visitor sees the same components and behavior as mobile, sized appropriately for a large screen with the map still dominant. The legend/summary surface is compact and can collapse to give the map more room, the controls remain reachable and consistent, and every existing feature (story modal, district popup, attribution, Impressum) keeps working exactly as before. Nothing new appears on desktop; nothing familiar disappears.

**Why this priority**: Desktop already works and has good feedback, so this story mainly guards consistency, reduces space waste, and prevents the mobile rework from introducing a divergent or feature-creeped desktop experience.

**Independent Test**: Open the published bundle in a desktop viewport, confirm the shared components render consistently with mobile, collapse the legend to reclaim map space, and verify all existing interactions still behave.

**Acceptance Scenarios**:

1. **Given** a desktop viewport, **When** the page loads, **Then** the map is the dominant surface and the legend/summary surface matches the mobile component set (not a separate design).
2. **Given** the expanded legend/summary surface, **When** the visitor collapses it, **Then** the map reclaims the freed space and no content is clipped.
3. **Given** a desktop viewport, **When** the visitor uses Bäume, Helligkeit, the story modal, the district popup, attribution, or Impressum, **Then** each works with the same behavior as before this feature.
4. **Given** any viewport width, **When** the window is resized across breakpoints, **Then** the layout adapts without broken overlaps or content overflow.

---

### Edge Cases

- Very small phones (about 320 px wide) and landscape phones: the surface and controls must remain usable and never overflow the viewport.
- Devices with notches and home indicators: controls and the legend surface must clear the safe-area insets and not be clipped or partially hidden.
- The browser address bar or home indicator appearing or hiding: the layout must not jump or clip controls (no viewport instability).
- The legend, city-overview, or story content being taller than the screen: the expandable surface must scroll internally rather than overflow the viewport.
- A tapped building near the bottom of the screen: the popup must reposition above the legend surface so it stays fully visible.
- Reduced-motion preference: all transitions degrade to instant, non-animated state changes.
- Large OS text or zoomed browser text: the surface must reflow, not break layout or clip labels.
- Desktop window resized narrow enough to cross into the mobile breakpoint: behavior and controls must transition cleanly in both directions.
- The map gesture and the legend-surface drag/slide conflict: when collapsed, the surface must not intercept map gestures.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On mobile viewports, the map MUST be the dominant surface; the legend and summary content MUST be collapsed behind a control by default rather than permanently covering the map.
- **FR-002**: Users MUST be able to expand and collapse the legend/summary surface with a single tap, and the control MUST sit in the thumb-friendly lower zone.
- **FR-003**: Every interactive control (legend expand/collapse, Bäume, Helligkeit, zoom, popup and modal close) MUST have a minimum touch target of 44x44 px and at least 8 px clear spacing from adjacent targets on mobile.
- **FR-004**: On mobile, the primary tools (Bäume, Helligkeit) MUST remain visible and operable while the legend is collapsed, and MUST be placed in the thumb-friendly lower zone.
- **FR-005**: The map's zoom control and attribution MUST remain visible and MUST NOT be overlapped by any new mobile control placement.
- **FR-006**: Building and district popups MUST remain fully visible when the legend surface is expanded or collapsed; the map MUST keep the popup clear of the surface.
- **FR-007**: The layout MUST adapt to safe-area insets and browser-chrome show/hide without clipping controls and without visible viewport jump.
- **FR-008**: Expand, collapse, and surface transitions MUST use native-feeling motion (slide, scale) and MUST respect the reduced-motion preference by rendering instant, static state changes when it is set.
- **FR-009**: Desktop MUST use the same components and behavior as mobile (shared collapsed legend surface, consistent controls, map dominant) with no separate mobile-only design.
- **FR-010**: This feature MUST NOT add, remove, or rename any existing feature or control; Bäume, Helligkeit, the first-visit story modal, the city-overview panel, district popup, attribution, and Impressum MUST keep their current behavior.
- **FR-011**: All new copy MUST be German and MUST follow the site's copy conventions (no em-dashes or en-dashes).
- **FR-012**: The refresh MUST introduce zero new network requests and MUST NOT require a server; the bundle MUST remain static and fully functional offline on first load.
- **FR-013**: Existing performance budgets MUST hold: all interactions stay within the current 2-second interaction budget, with no regression in the first usable map.
- **FR-014**: Accessibility MUST be maintained or improved: every control MUST be keyboard-operable with a visible focus state, all new surfaces MUST meet WCAG AA color contrast, and screen-reader labels MUST describe the controls.

### Key Entities *(include if feature involves data)*

- **Legend/Summary Surface**: The expandable mobile surface that holds the legend title, gradient scale, city-overview numbers, and tools; it can be collapsed to a compact handle and expanded to reveal content, and it scrolls internally when content is taller than the screen.
- **Map Tool Controls**: Bäume toggle and Helligkeit slider; always accessible, thumb-reachable, native-size touch targets, independent of whether the legend surface is open.
- **Map Popups**: Building value popup and district statistics popup; persistent, repositioned to stay clear of the legend surface in every map position.
- **Viewport/Chrome State**: The responsive layout state derived from screen width, safe-area insets, and browser-chrome visibility; it drives which arrangement of the shared components is shown. No new user data is introduced.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a mobile viewport, when the legend/summary surface is collapsed, the map occupies at least 80% of the viewport height (measurable in a narrow viewport).
- **SC-002**: 100% of interactive controls on mobile meet the minimum 44x44 px touch target with at least 8 px spacing (verifiable by direct measurement).
- **SC-003**: A first-time mobile user can expand and collapse the legend surface in under 2 seconds of familiarization, and the map remains interactive while collapsed.
- **SC-004**: Building-tap popups remain fully visible (not obscured) in 100% of tested building positions on mobile, with the surface both expanded and collapsed.
- **SC-005**: The layout produces zero visible layout shift when the browser chrome (address bar, home indicator) appears or hides.
- **SC-006**: No interaction-time regression: all interactions complete within the existing 2-second interaction budget.
- **SC-007**: The refresh performs zero new network requests compared to the published site, and offline first load remains functional.
- **SC-008**: Existing test suites remain green; `make check-public` stays clean and the manual smoke checklists pass.
- **SC-009**: All new copy contains zero em-dashes and zero en-dashes (mechanical check).
- **SC-010**: A keyboard-only user can reach and operate every control with a visible focus state, and all new surfaces meet WCAG AA contrast.

## Assumptions

- "Native feel" means native-like web interaction patterns (bottom-sheet-style expandable surfaces, thumb-zone placement, 44-48 px touch targets, smooth slide/scale transitions). It does not mean a rewrite in native code; the site stays a static web bundle with no build tool and no new third-party dependencies (existing project constraint).
- The mobile-first design follows the industry-standard native map convention (Google Maps, Apple Maps): full-bleed map, minimal permanent chrome, an expandable legend/summary surface, and floating tool controls in the thumb zone. This is a documented design decision, not a feature addition.
- Touch-target sizing follows the consensus of WCAG 2.5.5 (44x44), Apple HIG (44 pt), and Material (48 dp), with spacing between targets.
- This feature changes presentation, layout, and interaction only. It never adds, removes, or renames functionality; the plan must prove parity with the existing feature set.
- Reduced-motion users receive instant, non-animated behavior for all transitions.
- The site language is German, and all new copy follows the conventions from feature 007 (hyphens only, no em-dashes or en-dashes).
- A shared component set adapts across breakpoints (mobile below roughly 768 px, desktop above); behavior, not appearance, is the definition of consistency.
- Existing performance budgets (interaction under 2 seconds, first usable map) and the static/offline constraints continue to hold unchanged.
