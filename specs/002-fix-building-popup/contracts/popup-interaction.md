# Contract: Popup Interaction

**Branch**: `main` | **Date**: 2026-08-04
**Applies to**: `src/site/main.js` — `wireBuildingsInteractions()`
and the `index.html` / `style.css` popup classes it depends on.
**Source**: `spec.md` FR-001..FR-011, acceptance scenarios 1–7,
edge cases, assumptions.

This contract is the observable behavior of the selection popup on
the published bundle. The smoke checklist and quickstart verify it
verbatim.

## 1. Popup instance

- Exactly one `maplibregl.Popup` instance exists for the lifetime of
  the page. No code path constructs a second one (SC-001).
- Constructor options are fixed: `closeButton: true`, `offset: 8`,
  `className: 'building-popup'`, `closeOnClick: false` (research
  R-002).
- `closeOnClick: false` is mandatory: it removes MapLibre's
  map-wide click-close listener, which is the mechanism that closed
  the popup on building clicks (research R-001).

## 2. Click classification

- Every canvas click is classified by
  `map.queryRenderedFeatures(point, { layers: ['buildings-fill'] })`.
  - Non-empty → `building` click.
  - Empty → `empty` click.
- The classification ignores layer z-order: a building under a tree
  polygon still classifies as `building` (FR-010).
- Clicks on the popup DOM (body or close button) never reach the
  canvas and produce no click event (research R-005).
- Touch taps classify identically to mouse clicks via MapLibre's
  standard tap-to-click handling (FR-009).

## 3. Behavior rules

| # | Input | Result |
|---|---|---|
| B1 | Building click, popup closed | Popup opens at the click point showing that building's value. |
| B2 | Building click, popup open | Popup stays open, re-anchored to the new click point, showing the new building's value (FR-002). |
| B3 | Click same building again | Popup stays open, content unchanged (acceptance scenario 6). |
| B4 | Empty-space click | Popup closes (FR-003). Covers boundary mask and outside Mannheim. |
| B5 | Close button click | Popup closes (FR-004). |
| B6 | Building click after close | Popup re-opens normally (FR-011). |
| B7 | Rapid clicks A then B | Final state is exactly the B state; no moment with two popups (SC-001). |
| B8 | Building at viewport edge | Popup auto-anchors inside the visible area (research R-004). |
| B9 | Buildings layer error | Popup behavior unchanged (research R-008). |

- There is no input that closes the popup other than B4 and B5.
- A building click never closes the popup (FR-003).

## 4. Popup content

- Label: exactly `Baumanteil im 60-m-Umkreis` (frozen by spec).
- Value line, for a building with `has_value === true`:
  `value_str` with `%` appended, HTML-escaped. Example:
  `4.21%`.
- Value line, for a building with `has_value === false`:
  the en dash `–`. Never `0.00%` (FR-007).
- The popup shows no address, no building id, no completeness
  display, no links (out of scope).
- The popup never shows a value for a building other than the one
  last clicked.

## 5. Untouched behavior (regression surface)

- Hover pointer: `mousemove` / `mouseleave` on `buildings-fill` set
  and clear `cursor: pointer` (FR-008). Unchanged.
- No hover tooltip, no hover highlighting (out of scope).
- Camera, zoom, pan, bearing, pitch: untouched.
- Tree toggle (`Bäume`): untouched.
- Attribution, navigation controls, initial view: untouched.

## 6. Verification

Run the scenarios in `quickstart.md`. The checklist
`tests/frontend/smoke_us2.md` is extended with the new checks and is
the per-release regression gate for this contract.
