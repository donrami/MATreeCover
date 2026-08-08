# US3 Frontend Smoke Checklist — Toggle Detected Tree Cover

**Goal**: Toggle the detected tree layer (quickstart.md Scenario 3).

**Maps**: FR-013, FR-015, FR-016, FR-020, SC-005, SC-007.

**Setup**: Serve the published bundle with a Range-capable static
server (`python -m http.server` has no Range support; use nginx or
equivalent). Open the page in a clean browser.

**State note**: The canopy mask is accepted and `trees.pmtiles` is
published in `dist/`, so the toggle renders the detected tree layer
with real data.

## Checks

- [X] On load, the tree layer is hidden (FR-015).
- [X] Only one data-layer button exists. Its label is `Bäume` (FR-013).
- [X] Clicking `Bäume` shows the tree layer in flat `#39C43D` at
      75% opacity (FR-015).
- [X] The camera does not move when toggling (FR-016). Read
      `map.getCenter()`, `map.getZoom()`, `map.getBearing()`,
      `map.getPitch()` before and after. All four stay unchanged.
- [X] Clicking `Bäume` again hides the layer. The camera stays
      unchanged (FR-016).

## Image sanity

- [X] `pytest tests/pipeline/test_image_sanity.py` passes: at least
      17 of 20 crops distinguish canopy from roofs, roads, and water
      (SC-005).

## Result

- [X] All applicable checks pass.

- [x] Feature-014 bundle re-verified 2026-08-08 (scripts/smoke-verify.mjs fresh-profile driver + acceptance suite; zoom, controls, popups, trees toggle, no console errors)
