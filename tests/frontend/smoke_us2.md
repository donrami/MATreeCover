# US2 Frontend Smoke Checklist — Inspect a Building Value.

## Goal

- Read a building's tree-cover value.
- Quickstart Scenario 2 covers this run.
- Maps FR-008, FR-009, FR-014, SC-004, SC-006.

## Setup

- Serve the published bundle with a Range-capable static server.
- `python -m http.server` has no Range support.
- Use nginx or equivalent.
- Open the page in a clean browser.

## State note

- The canopy mask is accepted.
- `values` pass.
- Buildings without a valid value read `–`.

## Base checks

- [X] Hovering a building changes the cursor to a pointer (FR-014).
- [X] Moving away restores the default cursor (FR-014).
- [X] Clicking a building opens a compact popup (FR-014).
- [X] The popup shows the value with two decimals (FR-008).
- [X] A building without a valid value shows `–` (FR-009).
- [X] The popup closes on the close button or a map click.

## Independent recalculation

- [X] `pytest tests/pipeline/test_values_recalc.py` passes.
- [X] 100 sampled buildings agree within one percentage point (SC-004).

## Popup interaction fix

- Maps FR-001 to FR-011.
- Maps SC-001 to SC-005.
- Source `specs/002-fix-building-popup/quickstart.md` Scenarios 1–6.

### Pre-fix reproduction

- `wireBuildingsInteractions()` builds a fresh `maplibregl.Popup` per
  click.
- It omits `closeOnClick: false`.
- MapLibre's default map-wide close listener then closes popup A when
  popup B opens.
- A second building click closes the popup instead of replacing it.
- All checks below passed on 2026-08-04 against the served `dist/`
  bundle (nginx, 127.0.0.1:8088) after commit 810bd6f.

### Scenario 1 — Ten-building click sequence (SC-001, FR-002, FR-003)

- [X] Click ten distinct buildings in a row.
- [X] Every click shows the clicked building's value with two decimals.
- [X] The popup content changes between clicks.
- [X] Each click shows the value of the building just clicked.
- [X] `document.querySelectorAll('.maplibregl-popup').length` never
      reads more than `1` between clicks (SC-001).
- [X] Repeated clicks on the same point keep exactly one popup.
- [X] That popup still shows the same building's value.
- [X] No click in the sequence ever closes the popup (FR-003).

### Scenario 2 — Replace, do not close (FR-002, SC-002)

- [X] Click building A.
- [X] Within ~1 s click building B.
- [X] The popup now shows building B's value (FR-002).
- [X] The popup never disappears between the two clicks.
- [X] No blink to zero popups occurs.
- [X] Within two seconds of each click the popup shows that building's
      value (SC-002).
- [X] Spot-check on the ten-click run from Scenario 1 passes for all
      ten clicks.

### Scenario 3 — Empty-space close and re-open (FR-003, FR-011, SC-003)

- [X] Click a building to open a popup.
- [X] Click empty map space.
- [X] Repeat the open-then-close cycle ten times.
- [X] All ten empty-space clicks close the popup (SC-003).
- [X] Confirm via
      `document.querySelectorAll('.maplibregl-popup').length === 0`.
- [X] Empty-space clicks when no popup is open do nothing.
- [X] No error and no popup appears from those clicks.
- [X] Click the boundary mask or the black area outside Mannheim.
- [X] The popup closes there too.
- [X] After a close the next building click re-opens the popup
      normally (FR-011).

### Scenario 4 — Close button and popup click-through (FR-004)

- [X] Click a building to open the popup.
- [X] Click the popup's close button.
- [X] The popup closes (FR-004).
- [X] Re-open a popup over a small building.
- [X] Click the popup body.
- [X] The popup stays open and still shows the same building's value.
- [X] The click does not re-anchor the popup.
- [X] The click does not select any building underneath.

### Scenario 5 — Regression (FR-007, FR-008, SC-005)

- [X] Hover a building.
- [X] The cursor becomes a pointer (FR-008).
- [X] Move away.
- [X] The cursor restores.
- [X] Click a building without a valid value.
- [X] The popup shows `–` and never `0.00%` (FR-007).
- [X] The label still reads `Baumanteil im 60-m-Umkreis`.

### Scenario 6 — Touch taps and tree-layer overlay (FR-009, FR-010)

- [X] In device-emulation mode, or on a touch device, tap a building.
- [X] The popup opens exactly as for a mouse click (FR-009).
- [X] Tap a second building.
- [X] The popup content replaces.
- [X] Tap empty space.
- [X] The popup closes.
- [X] Enable the `Bäume` toggle so tree polygons cover part of a
      building.
- [X] Click that building through the tree area.
- [X] The popup still opens with the building's value (FR-010).
- [X] Zoom so a building sits at the very edge of the viewport.
- [X] Click that edge building.
- [X] The popup stays fully inside the visible area.

## Result

- [X] US2 base checks pass.
- [X] Popup fix Scenarios 1 and 3 pass.
- [X] Scenarios 1 and 3 cover SC-001 and SC-003.
- [X] Popup fix Scenarios 2, 4, 5, 6 pass.

End of checklist.

- [x] Feature-014 bundle re-verified 2026-08-08 (scripts/smoke-verify.mjs fresh-profile driver + acceptance suite; zoom, controls, popups, trees toggle, no console errors)
