# Feature Specification: Ko-fi Donation Button

**Feature Branch**: `017-ko-fi-button`
**Created**: 2026-08-09
**Status**: Draft
**Input**: User description: "we need to add my ko-fi button with reasonable placement in both desktop and mobile <a href=https://ko-fi.com/M4Q624RYOV target=_blank><img height=36 ... src=https://storage.ko-fi.com/cdn/kofi3.png?v=6 ... alt=Buy Me a Coffee at ko-fi.com /></a>"

## User Scenarios & Testing

### User Story 1 - Desktop Visitors Find and Use the Donation Button (Priority: P1)

A visitor on a desktop viewport sees a clearly identifiable Ko-fi donation button in the panel header, understands it is a way to support the project, clicks it, and lands on the owner's Ko-fi page in a new tab — without leaving the map.

**Why priority**: Donating is the entire purpose of the feature, and desktop is the primary surface of the map site. If the button is not visible and clickable on desktop, the feature delivers no value.

**Independent Test**: Load the published page at a desktop viewport (≥ 768 px), assert the button is visible in the header, click it, and assert a new tab opens at `https://ko-fi.com/M4Q624RYOV` while the map page stays open.

**Acceptance Scenarios**:
1. **Given** a desktop viewport, **When** the page loads, **Then** a clearly identifiable Ko-fi donation button is visible in the surface header without scrolling.
2. **Given** the visible button, **When** it is clicked, **Then** the Ko-fi page (`https://ko-fi.com/M4Q624RYOV`) opens in a new tab and the map page remains open in the original tab.
3. **Given** the surface panel, **When** it is in both the collapsed and expanded states, **Then** the button remains visible in the header in both states.

### User Story 2 - Mobile Visitors Find and Use the Donation Button (Priority: P1)

A visitor on a phone sees the same donation button in the collapsed bottom-sheet header without losing map space, can tap it comfortably (touch target at least 44 × 44 px), and reaches the Ko-fi page in a new tab while the map stays fully interactive.

**Why priority**: Mobile is the other half of the request ("both desktop and mobile") and the layout is already map-dominant with strict touch and no-overlap contracts. The button must exist on mobile without degrading the map experience.

**Independent Test**: Load the published page at a mobile viewport (< 768 px) with the sheet collapsed, assert the button is visible in the header, that its touch target is at least 44 × 44 px, that tapping it opens the Ko-fi page in a new tab, and that the map still pans and zooms.

**Acceptance Scenarios**:
1. **Given** a mobile viewport with the surface sheet collapsed, **When** the page loads, **Then** the button is visible in the header and the map still occupies at least 80 % of the viewport height.
2. **Given** the button on mobile, **When** it is tapped, **Then** its touch target is at least 44 × 44 px and the Ko-fi page opens in a new tab.
3. **Given** any viewport width ≥ 320 px, **When** the header renders, **Then** the button does not overlap, occlude, or intercept input of the Bäume toggle, brightness slider, surface toggle, zoom control, attribution, Impressum link, or legend.

### User Story 3 - The Button Renders and Is Accessible (Priority: P2)

The button image renders visibly (it is not blocked by content security policy and never appears as a broken image), carries a text alternative that identifies it as a donation link, and is reachable and operable with a keyboard alone, with a visible focus indicator.

**Why priority**: A button that renders broken or cannot be reached by keyboard is a broken donation path and a regression against the site's accessibility contracts.

**Independent Test**: Load the published page, confirm the button image is visually rendered (no broken-image state), inspect its accessible name, and operate it with keyboard-only navigation (Tab to focus, Enter to activate).

**Acceptance Scenarios**:
1. **Given** the published site, **When** the page loads, **Then** the Ko-fi button renders its visual correctly — never a broken, blank, or content-policy-blocked image.
2. **Given** the button, **When** its accessible name is inspected, **Then** it has a text alternative that identifies it as a donation/support link.
3. **Given** the button, **When** navigating with keyboard only, **Then** it is reachable in tab order and shows a visible focus indicator.

### User Story 4 - Nothing Regresses (Priority: P2)

The maintainer ships the button knowing the map experience, layout invariants, security posture, and performance budgets are unchanged — the button is purely additive.

**Why priority**: Every prior feature locked layout invariants (no-overlap matrix), security headers and CSP, touch targets, and performance budgets; the button must not silently break any of them.

**Independent Test**: Run the full test suite, all governance gates (layout/overlap gate, commit checks, public-hygiene checks), the interaction-latency harness, and a visual parity comparison of the published map.

**Acceptance Scenarios**:
1. **Given** the changed tree, **When** the full test suite runs, **Then** every existing test passes.
2. **Given** the published page, **When** the layout overlap matrix is asserted at widths ≥ 320 px in both surface states, **Then** no two controls overlap and the map-dominant layout (map ≥ 80 % on mobile when collapsed) is preserved.
3. **Given** the published page, **When** security headers and content security policy are checked, **Then** the page carries the same security headers as before and the button's image is served without weakening the policy beyond the minimum needed for the image host.
4. **Given** the published page, **When** the interaction-latency harness runs, **Then** all interactions stay within the existing latency budgets.

### Edge Cases

- **Image blocked by content security policy**: the current policy allows images only from the site itself, inline data, and one external map provider — not the Ko-fi image CDN. If the policy is not extended for the image host, the button renders as a blocked/broken image. Published-page verification must confirm the image loads. Only the image-source rule may change; script, connect, and style rules stay untouched.
- **36 px image vs. 44 px touch target**: the provided button image is 36 px tall; on mobile the existing touch contract requires a hit area of at least 44 × 44 px with at least 8 px spacing to adjacent controls. The button's hit area must be enlarged without visually enlarging the image, so the header stays compact.
- **Dense header at narrow widths (≥ 320 px)**: the header row already contains the title, the Bäume toggle, the brightness slider, and the surface toggle. At 320 px the added button must not cause wrapping, overflow, or overlap; the no-overlap matrix must still pass.
- **Safe-area insets on mobile**: the header is part of a fixed bottom sheet on mobile; the button must not be clipped or partially hidden behind notches or the home indicator (existing safe-area padding contract).
- **External-link safety**: opening the Ko-fi page in a new tab must not let the external page control the map page (no-opener semantics), consistent with existing external links on the site.
- **Ko-fi unavailability**: if the Ko-fi page or the image CDN is unreachable, the site must remain fully functional — the button is a plain link with no script dependency and no blocking request.
- **Language consistency**: the site is German; the donation button's text alternative should not be a raw English-only string unless intentionally kept as the brand's standard label.

## Requirements

### Functional Requirements

- **FR-001**: The map page MUST display a clearly identifiable Ko-fi donation button in the surface header at all viewport widths ≥ 320 px, visible in both the collapsed and expanded header states without scrolling.
- **FR-002**: The button MUST link to the owner's Ko-fi page (`https://ko-fi.com/M4Q624RYOV`) and MUST open it in a new tab when activated, without leaving the map page.
- **FR-003**: The button MUST render its visual correctly in the published site: the rendered image MUST never appear blocked, broken, or blank.
- **FR-004**: On mobile viewports (< 768 px), the button's touch target MUST be at least 44 × 44 px, with at least 8 px clear spacing to adjacent controls.
- **FR-005**: The button MUST NOT overlap, occlude, or intercept input of any existing control (Bäume toggle, brightness slider, surface toggle, zoom control, attribution, Impressum link, legend) at any supported viewport width or surface state.
- **FR-006**: The button MUST have a text alternative identifying it as a donation/support link, MUST be reachable and operable via keyboard alone, and MUST show a visible focus indicator.
- **FR-007**: The button MUST preserve the map-dominant layout: on mobile with the sheet collapsed, the header chrome including the button MUST occupy no more than 20 % of the viewport height, leaving the map at least 80 %.
- **FR-008**: The button MUST NOT introduce any tracking, analytics, or script execution from the external site; it is a plain external link.
- **FR-009**: All existing behavior MUST remain unchanged: map values, colors, labels, popups, interactions, caching semantics, security headers, and the hashed-bundle contract. Any content security policy change is limited to allowing the button's image host; script, style, and connect rules MUST stay unchanged.
- **FR-010**: All existing tests and gates MUST pass after the change: pytest suites, layout/overlap gates, commit checks, and interaction-latency budgets.

### Key Entities

- **Donation link**: the single external destination (`https://ko-fi.com/M4Q624RYOV`) that the button activates; its URL and label are the feature's only configuration.
- **Donation button**: the header element rendering the Ko-fi visual with the donation link; subject to the touch-target, no-overlap, focus, and safe-area contracts.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The button is visible in the surface header on both breakpoints (desktop ≥ 768 px, mobile < 768 px) in both collapsed and expanded states, verified at viewport widths 320, 375, 768, 1280, and 1920 px.
- **SC-002**: Every activation of the button from the published site opens the Ko-fi page in a new tab (automated click test, 100 % success).
- **SC-003**: The button visual renders in the published bundle with zero broken-image or content-policy-blocked states (visual/browser verification).
- **SC-004**: The button never overlaps any other control in the layout overlap matrix at any width ≥ 320 px in either surface state; on mobile with the sheet collapsed, the map occupies at least 80 % of the viewport height.
- **SC-005**: The button's mobile touch target is at least 44 × 44 px with at least 8 px spacing to adjacent controls.
- **SC-006**: Keyboard-only users can reach and activate the button with a visible focus indicator, and the button exposes a text alternative identifying it as a donation link.
- **SC-007**: Zero regressions: the full test suite and all governance gates pass, all interaction-latency budgets hold, and map values, colors, labels, popups, and interactions are identical to the current published bundle.

## Assumptions

- Placement decision (session 2026-08-09, owner-confirmed): the button lives in the surface header and is always visible on both breakpoints — desktop panel header and mobile collapsed bottom-sheet header. No story-modal or footer placement.
- The button's destination is `https://ko-fi.com/M4Q624RYOV`; the provided Ko-fi image and label are the default visual, adapted to the site's existing styling and accessibility contracts where required (touch target, focus indicator, language).
- The button image is loaded from Ko-fi's image CDN; if the site's content security policy blocks it, the policy is extended for the image host only — never for scripts, connections, or styles.
- The button is purely additive: no change to map data, rendering, caching, existing header tools, or security posture beyond the minimal image-host allowance.
- No tracking, analytics, or third-party script is added; donation success is measured by the owner on the Ko-fi platform, not on this site.
