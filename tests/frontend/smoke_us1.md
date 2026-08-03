# US1 Frontend Smoke Checklist

**Goal**: View the Mannheim color map (quickstart.md Scenario 1).

**Maps**: FR-001..FR-004, FR-010/FR-011, FR-012/FR-013, FR-017, FR-019,
FR-018, SC-001, SC-002, SC-008.

**Setup**: Run `make publish`. Serve `dist/` with
`python -m http.server -d dist`. Open `http://localhost:8000/` in a
clean browser with WebGL 2.

**Quarantine note**: The canopy mask fails acceptance (FR-021). Then
`buildings.pmtiles` is not in the bundle. Palette and outline checks
apply once accepted values exist. Structural checks apply always.

## Checks

- [ ] Title bar reads `Baumfläche` (FR-013).
- [ ] Full Mannheim boundary fills the viewport. Minimal padding.
      North up. No camera flight (FR-002).
- [ ] Base map is dark. Everything outside the boundary is black
      (FR-003).
- [ ] Legend is visible. German description. Labels `0`, `15`, `30`,
      `50`, `100` (FR-012).
- [ ] Only one data-layer control exists. Label `Bäume` (FR-013).
- [ ] Zoom in, zoom out, and north-reset controls are visible and
      functional (FR-017).
- [ ] Attribution control is reachable. It lists LGL (`dl-de/by-2-0`),
      basemap.de, CityTreeCover (FR-019).
- [ ] Reload at 360 px viewport width. Legend and controls remain
      readable and usable (FR-018).
- [ ] No analytics or telemetry (FR-001).
- [ ] No third-party requests. Only the basemap tiles and the vendored
      libs load.

## Palette checks

These apply when building values are accepted.

- [ ] Buildings use the reference palette at 75% opacity (FR-010).
- [ ] Building outlines are thin gray (FR-010).
- [ ] Colors interpolate continuously between stops. Values above 80%
      keep the final reference color (FR-011).

## Result

- [ ] All applicable checks pass.
