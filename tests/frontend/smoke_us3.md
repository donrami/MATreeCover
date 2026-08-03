# US3 Frontend Smoke Checklist — Toggle Detected Tree Cover

**Goal**: Toggle the detected tree layer (quickstart.md Scenario 3).

**Maps**: FR-013, FR-015, FR-016, FR-020, SC-005, SC-007.

**Setup**: Serve the published bundle with
`python -m http.server -d dist`. Open the page in a clean browser.

**Quarantine note**: The tree layer needs an accepted canopy mask. The
mask fails acceptance. Then `trees.pmtiles` is `pending`. The layer is
not in the published style. The checks below apply once the mask is
accepted (post-RunPod). The toggle wiring is in the bundle.

## Checks

- [ ] On load, the tree layer is hidden (FR-015).
- [ ] Only one data-layer button exists. Its label is `Bäume` (FR-013).
- [ ] Clicking `Bäume` shows the tree layer in flat `#39C43D` at
      75% opacity (FR-015).
- [ ] The camera does not move when toggling (FR-016). Read
      `map.getCenter()`, `map.getZoom()`, `map.getBearing()`,
      `map.getPitch()` before and after. All four stay unchanged.
- [ ] Clicking `Bäume` again hides the layer. The camera stays
      unchanged (FR-016).

## Image sanity

- [ ] `pytest tests/pipeline/test_image_sanity.py` passes: at least
      17 of 20 crops distinguish canopy from roofs, roads, and water
      (SC-005).

## Result

- [ ] All applicable checks pass.
