# Data Model: Ko-fi Donation Button (feature 017)

Phase 1 output. Entities, fields, relationships, validation rules, and states derived from the feature spec. The feature adds no persistence, no runtime state, and no new data flow — it is a static markup + CSS change, so the model below is deliberately small.

**Revision note (2026-08-09)**: the owner re-decided the placement in the clarification session — the button lives in the surface **footer**, is visible **only when the surface is expanded** (hidden when collapsed), and its accessible name is the short German label **"Unterstützen"** (spec `## Clarifications`; FR-001, FR-006). The earlier header placement is superseded.

## Entities

### DonationLink (configuration)

The single external destination the button activates. This is the feature's only configuration value (spec Key Entities).

| Field | Value | Constraint |
|-------|-------|------------|
| `href` | `https://ko-fi.com/M4Q624RYOV` | Fixed. Owner's Ko-fi page (spec Input). Exact match — no trailing slash variants, no query strings. |
| `target` | `_blank` | FR-002: opens in a new tab; the map page stays open. |
| `rel` | `noopener` | External-link safety (spec edge case); matches the site's existing external-link pattern (`target="_blank" rel="noopener"` in `index.html`). |
| `type` | external link | FR-008: plain link. No script, no tracking, no form, no fetch. |

### DonationButton (footer element)

The surface-footer element rendering the Ko-fi banner visual donation link. Subject to the touch-target, no-overlap, focus, safe-area, and collapsed-visibility contracts (spec Key Entities; FR-001, FR-004…FR-007).

| Field | Value | Constraint |
|-------|-------|------------|
| `element` | `<a class="ko-fi" href=… target="_blank" rel="noopener">` | Single anchor inside `<footer class="surface-footer">`, which is the last child of `.surface-body` (research R-4). |
| `visual` | `<img src="https://storage.ko-fi.com/cdn/kofi3.png?v=6" width="143" height="36" alt="Unterstützen">` | FR-003 renders correctly under CSP; R-1/R-6/R-8. |
| `accessible name` | `Unterstützen` (from `img alt`) | FR-006: identifies the support/donation link; short German label, owner-chosen (spec Clarifications Q3; research R-6). |
| `hit area (mobile)` | ≥ 44 × 44 px | FR-004; padding-based enlargement, image visual stays 36 px (R-3). |
| `spacing (mobile)` | ≥ 8 px to adjacent interactive content | FR-004; `.surface-body-inner` flex `gap: 12px` + footer padding (R-3). |
| `focus indicator` | visible, matches existing controls | FR-006; existing `:focus-visible` pattern (`.surface-toggle` uses `outline: 2px solid var(--subtle)`). |
| `placement` | footer of the surface body; visible only when expanded | FR-001; hidden when collapsed, full banner in the footer when expanded (spec Clarifications Q1/Q2). |
| `scroll behavior` | `position: sticky; bottom: 0` | FR-001 "without scrolling" when expanded, even with tall body content (research R-4). |

## Relationships

- `DonationLink` is a value embedded in `DonationButton` — the anchor carries the link's `href`/`target`/`rel`.
- `DonationButton` belongs to `SurfaceFooter` (`.surface-footer`), which belongs to `SurfaceBody` (`.surface-body`, the feature-012 collapsible part), which belongs to `Surface` (`#surface`). The button inherits the surface's collapse machine and safe-area handling — it does not own any of its own. It is NOT a member of `SurfaceHeader`.
- `DonationButton` MUST NOT overlap any member of the existing control set: `#baeume`, `.brightness`, `#surface-toggle`, MapLibre zoom controls, attribution, `.legal-link` (Impressum), legend — in the expanded surface state (FR-005). The collapsed state has no donation button, so no overlap is possible there.

## Validation rules (from requirements)

| Rule | Source | Enforcement |
|------|--------|-------------|
| Button visible in the surface footer when expanded, at all widths ≥ 320 px, without scrolling | FR-001 | quickstart Q1/Q3; smoke checklist |
| Button hidden when the surface is collapsed | FR-001 | quickstart Q1/Q3; smoke checklist |
| Activation opens the Ko-fi page in a new tab, map stays open | FR-002 | quickstart Q2; headless smoke |
| Image never blocked/broken/blank | FR-003 | quickstart Q6 (CSP + browser render) |
| Touch target ≥ 44×44, ≥ 8 px spacing (mobile, expanded) | FR-004 | quickstart Q4 |
| No overlap/occlusion/input interception of any existing control (expanded state) | FR-005 | quickstart Q5 (extended matrix) |
| Accessible name "Unterstützen"; focus indicator visible | FR-006 | acceptance test; quickstart Q7 |
| Collapsed sheet chrome ≤ 20 % viewport height (map ≥ 80 %); the button is hidden in this state | FR-007 | quickstart Q3 |
| No tracking/analytics/script; plain external link | FR-008 | acceptance test (markup shape) |
| CSP change limited to the image host (already landed); all else byte-identical | FR-009 | acceptance test; quickstart Q6 |
| All existing tests/gates pass | FR-010 | quickstart Q9 |

## State transitions

No new state. The button is static markup and inherits the surface's existing collapse state:

| State | Owner | Effect on button |
|-------|-------|------------------|
| `is-collapsed` (default on mobile) | `#surface` (toggled by `#surface-toggle` in `main.js`) | `.surface-body` gets `max-height: 0; overflow: hidden` — the footer button is hidden (FR-001). |
| `is-collapsed` removed (expanded; desktop default) | `#surface` | `.surface-body` opens — the footer button is visible, pinned to the sheet bottom via sticky (FR-001). |
| Hover / `:focus-visible` / active | button itself | Visual feedback only, matches existing controls. |

Transitions: link activation is the only event — it navigates to `DonationLink.href` in a new tab (no-opener); no state change on the map page. The popup-clearance padding in `main.js` (`syncPadding`) measures `surface.offsetHeight` when the sheet is expanded, so the footer height is included automatically — no JS change.

## Invariants (global, unchanged)

Map values, colors, labels, popups, interactions, caching semantics, security headers, hashed-bundle contract: byte-identical to the pre-feature bundle (FR-009/FR-013). The button is purely additive. The header carries no donation chrome.
