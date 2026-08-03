# US2 Frontend Smoke Checklist — Inspect a Building Value

**Goal**: Read a building's tree-cover value (quickstart.md Scenario 2).

**Maps**: FR-008, FR-009, FR-014, SC-004, SC-006.

**Setup**: Serve the published bundle with
`python -m http.server -d dist`. Open the page in a clean browser.

**Quarantine note**: The popup needs accepted building values. The canopy
mask fails acceptance. Then values are `pending`. The checks below apply
once values are accepted (post-RunPod). The interaction wiring is present
in the bundle already.

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
