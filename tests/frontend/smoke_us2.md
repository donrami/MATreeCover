# US2 Frontend Smoke Checklist — Inspect a Building Value

**Goal**: Read a building's tree-cover value (quickstart.md Scenario 2).

**Maps**: FR-008, FR-009, FR-014, SC-004, SC-006.

**Setup**: Serve the published bundle with a Range-capable static
server (`python -m http.server` has no Range support; use nginx or
equivalent). Open the page in a clean browser.

**State note**: The canopy mask is accepted and `values` pass, so the
popup shows real values. Buildings without a valid value are present
and must read `–`.

## Checks

- [ ] Hovering a building changes the cursor to a pointer (FR-014).
- [ ] Moving away from a building restores the default cursor (FR-014).
- [ ] Clicking a building opens a compact popup (FR-014).
- [ ] The popup shows the value with two decimal places (FR-008).
      Example: `12.34%`.
- [ ] A building without a valid value shows `–` in the popup. It never
      shows `0.00%` (FR-009).
- [ ] The popup closes again (close button or clicking the map).

## Independent recalculation

- [ ] `pytest tests/pipeline/test_values_recalc.py` passes: 100 sampled
      buildings agree within one percentage point (SC-004).

## Result

- [ ] All applicable checks pass.
