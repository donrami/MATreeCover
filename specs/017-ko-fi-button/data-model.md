# Data Model: Ko-fi Donation Button (feature 017)

Phase 1 output. Entities, fields, relationships, validation rules, and state derived from the feature spec. The feature adds no persistence, no runtime state, and no new data flow — it is a static markup + CSS change, so the model below is deliberately small.

## Entities

### DonationLink (configuration)

The single external destination the button activates. This is the feature's only configuration value (spec Key Entities).

| Field | Value | Constraint |
|-------|-------|------------|
| `href` | `https://ko-fi.com/M4Q624RYOV` | Fixed. Owner's Ko-fi page (spec Input). Exact match — no trailing slash variants, no query strings. |
| `target` | `_blank` | FR-002: opens in a new tab; map page stays open. |
| `rel` | `noopener` | External-link safety (spec edge case); matches the site's existing external-link pattern (`target="_blank" rel="noopener"` in `index.html`). |
| `type` | external link | FR-008: plain link. No script, no tracking, no form, no fetch. |

### DonationButton (header element)

The header element rendering the Ko-fi visual donation link. Subject to the touch-target, no-overlap, focus, and safe-area contracts (spec Key Entities).

| Field | Value | Constraint |
|-------|-------|------------|
| `element` | `<a class="ko-fi" href=… target="_blank" rel="noopener">` | Single anchor, direct child of `.surface-header` (research R-4). |
| `visual` | `<img src="https://storage.ko-fi.com/cdn/kofi3.png?v=6" width="143" height="36" alt="Baumfläche auf Ko-fi unterstützen">` | FR-003 renders correctly under CSP; R-1/R-6/R-8. |
| `alt` | `Baumfläche auf Ko-fi unterstützen` | FR-006: identifies the donation link; German (spec edge case, research R-6). |
| `hit area (mobile)` | ≥ 44 × 44 px | FR-004; padding-based enlargement, image visual stays 36 px (R-3). |
| `spacing (mobile)` | ≥ 8 px to adjacent controls | FR-004; existing flex `gap: 8px` (R-3). |
| `focus indicator` | visible, matches existing controls | FR-006; existing `:focus-visible` pattern (`.surface-toggle` uses `outline: 2px solid var(--subtle)`). |
| `placement` | header, before `.surface-toggle` | Chevron stays rightmost (feature 012); always visible in collapsed AND expanded states (FR-001). |

## Relationships

- `DonationLink` is a value embedded in `DonationButton` — the anchor carries the link's `href`/`target`/`rel`.
- `DonationButton` belongs to `SurfaceHeader` (`.surface-header`), which belongs to `Surface` (`#surface`). The button inherits the surface's state machine and safe-area handling — it does not own any of its own.
- `DonationButton` MUST NOT overlap any member of the existing control set: `#baeume`, `.brightness`, `#surface-toggle`, MapLibre zoom controls, attribution, `.legal-link` (Impressum), legend — in either surface state (FR-005).

## Validation rules (from requirements)

| Rule | Source | Enforcement |
|------|--------|-------------|
| Button visible in header at all widths ≥ 320 px, both surface states | FR-001 | quickstart Q1/Q3; smoke checklist |
| Activation opens Ko-fi page in new tab, map stays open | FR-002 | quickstart Q2; headless smoke |
| Image never blocked/broken/blank | FR-003 | quickstart Q6 (CSP + browser render) |
| Touch target ≥ 44×44, ≥ 8 px spacing (mobile) | FR-004 | quickstart Q4 |
| No overlap/occlusion/input interception of any existing control | FR-005 | quickstart Q5 (extended matrix) |
| Alt text identifies donation link; focus indicator visible | FR-006 | acceptance test; quickstart Q7 |
| Collapsed header incl. button ≤ 20 % viewport height (map ≥ 80 %) | FR-007 | quickstart Q8 |
| No tracking/analytics/script; plain external link | FR-008 | acceptance test (markup shape) |
| CSP change limited to image host; all else byte-identical | FR-009 | acceptance test; quickstart Q6 |
| All existing tests/gates pass | FR-010 | quickstart Q9 |

## State transitions

No new state. The button is static markup and inherits two existing, orthogonal states from the surface:

| State | Owner | Effect on button |
|-------|-------|------------------|
| `is-collapsed` (default on mobile) | `#surface` (toggled by `#surface-toggle` in `main.js`) | Header stays visible; button visible and operable (FR-001/FR-004). |
| `is-collapsed` removed (expanded) | `#surface` | Header stays visible; button unchanged. |
| Hover / `:focus-visible` / active | button itself | Visual feedback only, matches existing controls. |

Transitions: link activation is the only event — it navigates to `DonationLink.href` in a new tab (no-opener), no state change on the map page.

## Invariants (global, unchanged)

Map values, colors, labels, popups, interactions, caching semantics, security headers, hashed-bundle contract: byte-identical to the pre-feature bundle (FR-009/FR-013). The button is purely additive.
