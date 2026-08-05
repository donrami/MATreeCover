# Feature Specification: First-Visit Story Modal

**Feature Branch**: `007-first-visit-story`
**Created**: 2026-08-05
**Status**: Draft
**Input**: User description: "we need to create some sort of a landing page or modal for when the user visits the page for the first time. It should provide a short story on how this map came to be with references to the spiegel article and the refrerence project, as well as the context of the current heatwave june/july 2026."

## Clarifications

### Session 2026-08-05

- Q: Landing page or modal? → A: Modal overlay on the map page. The map stays visible and immediately usable after dismissal; no separate URL is introduced.
- Q: Which Spiegel article is "the spiegel article"? → A: "Hitze in Europa: Wie gut Stadtbäume vor extremer Wärme schützen" (DER SPIEGEL, Wissenschaft/Natur, July 2026). This is the article the reference project CityTreeCover names as its origin in its own README; it also provides the heatwave context the story needs.
- Q: How often may the modal appear? → A: Once per browser. Dismissal is stored on-device; the modal never reappears on later visits unless that state is cleared.
- Q: Language? → A: German, matching map page (`lang="de"`).
- Q: Who writes the German story text? → A: Implementer drafts the copy; user reviews and approves final wording before merge.
- Q: Which dash forms are banned? → A: Em-dash (—) and en-dash (–) both banned; hyphen (-) allowed only inside compounds (e.g. "60-m-Umkreis").
- Q: How is AI-pattern-free prose verified? → A: Both: mechanical checks in acceptance (dash grep plus banned-phrase list) and a human prose review.
- Q: Should the modal link to the project's own source repository? → A: Yes. Third link in the link row, text "Quellcode auf GitHub", target https://github.com/donrami/MATreeCover (public, resolves HTTP 200, verified 2026-08-05), `target="_blank" rel="noopener"` like the other two links (FR-006). This extends the T006 final-wording approval to the new link row.

## Scope

### Goal

Give first-time visitors a short, dismissible story modal on the map page: how this map came to be — the Spiegel article, the CityTreeCover reference project, and the Mannheim replication — and why it matters during the June/July 2026 heatwave in Germany.

### In Scope

- Modal appears automatically on first visit to the map page, overlaying the loaded map.
- German-language story content with three narrative elements: map origin, references (Spiegel article + CityTreeCover project, each with a working link), and the June/July 2026 heatwave context.
- Dismissal via a visible close button or the Escape key; dismissal persists on-device so the modal does not reappear.
- Keyboard operation and screen-reader support (dialog semantics, managed focus).
- Responsive layout: modal fits all supported viewport widths (≥320 px), content scrolls without clipping, no overlap with existing UI elements.
- No new network requests, no tracking, no analytics.

### Out of Scope

- A separate landing page URL or route (modal overlay chosen instead).
- Multi-language versions (German only).
- Re-showing the modal after a time interval or on a schedule.
- Any change to map data, building values, tree layer, legend, popup content, or existing controls (Bäume toggle, Helligkeit slider, zoom).
- Measuring or reporting how often the modal is seen or dismissed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time Visitor Reads the Story (Priority: P1)

A visitor opens the map page for the first time. A short modal appears over the map telling the story: the Spiegel article about how city trees protect against extreme heat, the CityTreeCover project that grew out of reading it, and how this Mannheim map applies the same idea — plus the context of the June/July 2026 heatwave. The visitor reads it, closes it, and uses the map normally.

**Why priority**: This is the entire feature. Without the story on first visit, there is nothing to deliver.

**Independent Test**: Open the map page in a browser with no stored dismissal state. The modal appears automatically, contains all three story elements with working links, and is dismissible; the map is fully usable immediately after dismissal.

**Acceptance Scenarios**:

1. **Given** a visitor opens the map page for the first time (no stored dismissal), **When** the page finishes loading, **Then** the story modal appears automatically over the map.
2. **Given** the modal is open, **When** the visitor reads it, **Then** it tells how the map came to be: the Spiegel article, the CityTreeCover reference project, and the Mannheim replication of that approach.
3. **Given** the modal is open, **When** the visitor reads the story, **Then** it references the Spiegel article by title with a working link.
4. **Given** the modal is open, **When** the visitor reads the story, **Then** it references the CityTreeCover project by name with a working link.
5. **Given** the modal is open, **When** the visitor reads the story, **Then** it places the map in the context of the June/July 2026 heatwave in Germany.
6. **Given** the modal is open, **When** the visitor clicks the close button or presses Escape, **Then** the modal closes and the map becomes fully interactive.
7. **Given** the modal is open, **When** the visitor looks at the map behind it, **Then** the map is fully rendered and unchanged; closing the modal causes no layout shift.

### User Story 2 - Returning Visitor Is Not Shown the Modal Again (Priority: P2)

A visitor who already read and dismissed the story returns to the map page days later. The modal does not reappear; the map is immediately usable.

**Why priority**: "First visit" semantics are the point of the feature. Showing the modal to returning visitors would be noise and would erode the "no tracking, quiet" character of the site.

**Independent Test**: Open the page, dismiss the modal, reload the page, and revisit in a fresh session of the same browser. The modal appears exactly once and never again.

**Acceptance Scenarios**:

1. **Given** a visitor dismissed the modal on an earlier visit, **When** the visitor opens the map page again in the same browser, **Then** the modal does not appear.
2. **Given** a visitor dismissed the modal, **When** the page is reloaded in the same browser, **Then** the modal does not appear.
3. **Given** the browser's on-device state for the page is cleared, **When** the visitor opens the map page, **Then** the modal appears again (first-visit behavior restored).
4. **Given** on-device storage is unavailable or blocked, **When** the visitor opens the map page, **Then** the modal still appears and remains dismissible for that visit.

### User Story 3 - Visitor Follows the References (Priority: P2)

A reader wants to see the sources. From the modal, the visitor opens the Spiegel article, the CityTreeCover project, and the map's own source repository. All open in a new tab; the map page and its state are not lost.

**Why priority**: The references are a core content requirement, not decoration. Broken or misdirecting links would make the story untrustworthy.

**Independent Test**: Open the modal and click each reference. Each link resolves to the expected page in a new tab, and the map page remains open behind it.

**Acceptance Scenarios**:

1. **Given** the modal is open, **When** the visitor activates the Spiegel article link, **Then** the article opens in a new tab and the link resolves to the DER SPIEGEL article "Hitze in Europa: Wie gut Stadtbäume vor extremer Wärme schützen".
2. **Given** the modal is open, **When** the visitor activates the CityTreeCover link, **Then** the project page opens in a new tab and the link resolves to the reference project's repository.
3. **Given** the modal is open, **When** the visitor activates the source-repository link ("Quellcode auf GitHub"), **Then** the repository page opens in a new tab and the link resolves to github.com/donrami/MATreeCover.
4. **Given** one or more references are open in new tabs, **When** the visitor returns to the map tab, **Then** the map is unchanged and fully usable.

### Edge Cases

- On-device storage unavailable or blocked (private mode, disabled storage): modal still appears and is dismissible for the current visit; it may reappear on the next visit.
- Very narrow screens (≥320 px): modal fits the viewport; content scrolls inside the modal, nothing clips, and the modal never overlaps or occludes the legend, controls, or attribution beyond its own bounds.
- Keyboard users: modal can be opened-read-closed entirely by keyboard; Escape closes it; focus moves into the modal on open and returns to the page on close.
- Screen readers: the modal is announced as a dialog with a name; the story text is readable as content, not only as visual marks.
- Text zoom / large font settings: story content remains readable; the modal scrolls instead of clipping.
- Links: all reference links (Spiegel article, CityTreeCover, source repository) open in new tabs so the map is never navigated away.
- Modal open while the map loads: the map renders behind the modal; closing the modal causes no reflow or reload.
- The attribution page (separate page in the site) must never show the modal.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On a visitor's first visit to the map page — no stored dismissal state — the story modal MUST appear automatically, overlaying the loaded map.
- **FR-002**: The modal MUST present the story in German, with all of the following elements:
  - how the map came to be (the Spiegel article, the CityTreeCover reference project, and this Mannheim map as a replication of that approach);
  - a reference to the Spiegel article "Hitze in Europa: Wie gut Stadtbäume vor extremer Wärme schützen" with a working link;
  - a reference to the CityTreeCover reference project with a working link;
  - a reference to the project's own source repository ("Quellcode auf GitHub", https://github.com/donrami/MATreeCover) with a working link;
  - the context of the June/July 2026 heatwave in Germany and why tree cover matters in it.
- **FR-003**: The story MUST explain the map's central value in one or two sentences: buildings are colored by the average tree cover in their 60-m surroundings, matching the legend text already on the page.
- **FR-004**: The modal MUST be dismissible by a visible close button and by pressing the Escape key.
- **FR-005**: Dismissal MUST be stored on-device, and the modal MUST NOT appear again on any later visit in the same browser while that state exists.
- **FR-006**: The reference links MUST open in a new tab or window, never navigating the map page away.
- **FR-007**: While the modal is open, the map MUST remain visible and fully rendered; map interactions MUST resume immediately after dismissal, with no layout shift.
- **FR-008**: The modal MUST be fully operable with the keyboard: focus moves into the modal when it opens, Escape closes it, and focus returns to the page when it closes.
- **FR-009**: The modal MUST be exposed to screen readers as a dialog with a name, and its story text MUST be available as readable content.
- **FR-010**: The modal MUST remain fully usable at all supported viewport widths (≥320 px): content scrolls within the modal, no text is clipped, and the modal does not overlap the legend, controls, or attribution.
- **FR-011**: The feature MUST NOT add any network request, tracker, or analytics; all state stays on-device.
- **FR-012**: The modal MUST appear only on the map page and never on the attribution page.
- **FR-013**: If on-device storage is unavailable, the modal MUST still appear and remain dismissible for the current visit.
- **FR-014**: The feature MUST NOT change the map's data, building values, tree layer, legend, popup content, or the behavior of the Bäume toggle, Helligkeit slider, or zoom controls.
- **FR-015**: The story copy MUST be written in natural, human-sounding German prose: no em-dash (—) or en-dash (–) anywhere in the modal text, hyphens only inside compounds (e.g. "60-m-Umkreis"), and no AI-typical phrases (verified by a banned-phrase check in acceptance).

### Key Entities *(include if feature involves data)*

- **First-Visit Dismissal State**: an on-device record per browser that the story was already dismissed; determines whether the modal shows on page load. No data leaves the device.
- **Story Content**: the German narrative shown in the modal — map origin (article → reference project → this map), the 60-m tree-cover explanation, the three reference links (Spiegel article, CityTreeCover, source repository), and the June/July 2026 heatwave context. Written as natural human prose: no em-dash or en-dash, hyphens only inside compounds, no AI-typical phrases; drafted by the implementer, final wording approved by the user.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of first-time visitors (no stored dismissal) see the modal automatically on page load, in German.
- **SC-002**: After an explicit dismissal, the modal appears zero further times across repeated visits and reloads in the same browser.
- **SC-003**: The modal contains all required story elements — Spiegel article reference with working link, CityTreeCover reference with working link, source-repository reference with working link ("Quellcode auf GitHub"), map-origin narrative, and June/July 2026 heatwave context — verifiable by inspection and by activating all three links.
- **SC-004**: A first-time visitor can dismiss the modal with a single action (close button or Escape) and the map is fully interactive immediately after, with no layout shift.
- **SC-005**: No regression: existing map interactions (pan, zoom, Bäume toggle, Helligkeit slider, building popup) pass the existing smoke checklist unchanged.
- **SC-006**: The modal is fully operable by keyboard and announced as a dialog by screen readers; focus enters the modal on open and returns to the page on close.
- **SC-007**: The modal adds no network requests and no tracking; page-load behavior is unchanged apart from the modal appearing.
- **SC-008**: The modal is usable at every supported viewport width (≥320 px): content scrolls, nothing clips, and no static UI element is occluded beyond the modal's own bounds.
- **SC-009**: The story copy passes both copy-quality gates: mechanical acceptance checks find zero em-dashes, zero en-dashes, and no banned AI-typical phrases in the modal text; the user has reviewed and approved the final wording.

## Assumptions

- Modal overlay is the chosen form (the request allowed "landing page or modal"); the map remains the page's primary content and stays immediately usable.
- Language is German, matching the map page.
- Copy authorship: the implementer drafts the German story text; the user reviews and approves the final wording before merge.
- Writing bar: the story reads as natural human prose, free of AI-typical phrasing; the modal text contains no em-dash or en-dash, and hyphens appear only inside compounds.
- "First visit" means: the browser has no stored dismissal state for the map page.
- Dismissal persists on-device; the site's "no account, no tracking" principle extends to this feature (no analytics of modal views).
- Story facts are sourced from the reference project's README (origin: Spiegel article; built during the July 2026 heatwave) and from the Spiegel article itself (city trees protect against extreme heat; roughly 30% of a 60-m radius should be shaded).
- The story text is static content shipped with the page; it is not fetched at runtime.
- The modal appears only on the map page; the attribution page is untouched.
- While the modal is open, the map is visible but not interactive; interaction resumes on dismissal (standard modal behavior).

## Dependencies Evidence

- Map page is a static, no-build site: `src/site/index.html` (`lang="de"`, title "Baumfläche"), `src/site/main.js`, `src/site/style.css`; page ships a strict Content-Security-Policy (`script-src 'self'`), so modal behavior and story content must live in the existing page bundle, not in inline scripts or fetched resources.
- Existing UI elements the modal must not collide with: legend card (`#left-stack`), Bäume toggle and Helligkeit slider (`#controls`), zoom controls, attribution slot (`#attribution`) — the no-overlap constraint established by feature 004 applies.
- Reference project: CityTreeCover by Jakob Schultz, https://github.com/jcscaptures/CityTreeCover (MIT License, credited in the repo LICENSE); its README states the project emerged from reading the Spiegel article and was built during the July 2026 heatwave in Germany.
- Spiegel article: "Hitze in Europa: Wie gut Stadtbäume vor extremer Wärme schützen", DER SPIEGEL (Wissenschaft/Natur), July 2026, https://www.spiegel.de/wissenschaft/natur/hitze-in-europa-wie-gut-stadtbaeume-vor-extremer-waerme-schuetzen-a-9a0b26e5-f8ae-4fa5-a897-2f2b026f5226 — same article reference project cites as its origin; article reports city trees protect against extreme heat, roughly 30% 60-m surroundings recommended as shaded area (Croeser, Rahman & Ghosh, 2026).
- Project source repository: https://github.com/donrami/MATreeCover (public, verified resolving HTTP 200 on 2026-08-05); link text "Quellcode auf GitHub", `target="_blank" rel="noopener"`.
- Existing smoke tests (`tests/`, `acceptance/`) cover map interactions and must remain green.
