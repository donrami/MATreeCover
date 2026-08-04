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
- The checks below stay unchecked until the fix lands and a browser
  run confirms each scenario.

### Scenario 1 — Ten-building click sequence (SC-001, FR-002, FR-003)

- [ ] Click ten distinct buildings in a row.
- [ ] Every click shows the clicked building's value with two decimals.
- [ ] The popup content changes between clicks.
- [ ] Each click shows the value of the building just clicked.
- [ ] `document.querySelectorAll('.maplibregl-popup').length` never
      reads more than `1` between clicks (SC-001).
- [ ] Repeated clicks on the same point keep exactly one popup.
- [ ] That popup still shows the same building's value.
- [ ] No click in the sequence ever closes the popup (FR-003).

### Scenario 2 — Replace, do not close (FR-002, SC-002)

- [ ] Click building A.
- [ ] Within ~1 s click building B.
- [ ] The popup now shows building B's value (FR-002).
- [ ] The popup never disappears between the two clicks.
- [ ] No blink to zero popups occurs.
- [ ] Within two seconds of each click the popup shows that building's
      value (SC-002).
- [ ] Spot-check on the ten-click run from Scenario 1 passes for all
      ten clicks.

### Scenario 3 — Empty-space close and re-open (FR-003, FR-011, SC-003)

- [ ] Click a building to open a popup.
- [ ] Click empty map space.
- [ ] Repeat the open-then-close cycle ten times.
- [ ] All ten empty-space clicks close the popup (SC-003).
- [ ] Confirm via
      `document.querySelectorAll('.maplibregl-popup').length === 0`.
- [ ] Empty-space clicks when no popup is open do nothing.
- [ ] No error and no popup appears from those clicks.
- [ ] Click the boundary mask or the black area outside Mannheim.
- [ ] The popup closes there too.
- [ ] After a close the next building click re-opens the popup
      normally (FR-011).

### Scenario 4 — Close button and popup click-through (FR-004)

- [ ] Click a building to open the popup.
- [ ] Click the popup's close button.
- [ ] The popup closes (FR-004).
- [ ] Re-open a popup over a small building.
- [ ] Click the popup body.
- [ ] The popup stays open and still shows the same building's value.
- [ ] The click does not re-anchor the popup.
- [ ] The click does not select any building underneath.

### Scenario 5 — Regression (FR-007, FR-008, SC-005)

- [ ] Hover a building.
- [ ] The cursor becomes a pointer (FR-008).
- [ ] Move away.
- [ ] The cursor restores.
- [ ] Click a building without a valid value.
- [ ] The popup shows `–` and never `0.00%` (FR-007).
- [ ] The label still reads `Baumanteil im 60-m-Umkreis`.

### Scenario 6 — Touch taps and tree-layer overlay (FR-009, FR-010)

- [ ] In device-emulation mode, or on a touch device, tap a building.
- [ ] The popup opens exactly as for a mouse click (FR-009).
- [ ] Tap a second building.
- [ ] The popup content replaces.
- [ ] Tap empty space.
- [ ] The popup closes.
- [ ] Enable the `Bäume` toggle so tree polygons cover part of a
      building.
- [ ] Click that building through the tree area.
- [ ] The popup still opens with the building's value (FR-010).
- [ ] Zoom so a building sits at the very edge of the viewport.
- [ ] Click that edge building.
- [ ] The popup stays fully inside the visible area.

## Result

- [ ] US2 base checks pass.
- [ ] Popup fix Scenarios 1 and 3 pass.
- [ ] Scenarios 1 and 3 cover SC-001 and SC-003.
- [ ] Popup fix Scenarios 2, 4, 5, 6 pass.

End of checklist.
