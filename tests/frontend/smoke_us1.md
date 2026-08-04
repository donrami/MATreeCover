# US1 Frontend Smoke Checklist

**Goal**: View the Mannheim color map (quickstart.md Scenario 1).

**Maps**: FR-001..FR-004, FR-010/FR-011, FR-012/FR-013, FR-017, FR-019,
FR-018, SC-001, SC-002, SC-008.

**Setup**: Run `make publish`. Serve `dist/` with a Range-capable
static server (`python -m http.server` has no Range support and
cannot serve the PMTiles layers; use nginx or equivalent). Open the
served URL in a clean browser with WebGL 2.

**State note**: The canopy mask is accepted (FR-021, completeness
1.0). The bundle contains `buildings.pmtiles`, `trees.pmtiles`, and
`buildings.geojson`. All checks below apply.

## Checks

- [X] Title bar reads `Baumfläche` (FR-013).
- [X] Full Mannheim boundary fills the viewport. Minimal padding.
      North up. No camera flight (FR-002).
- [X] Base map is dark. Everything outside the boundary is black
      (FR-003).
- [X] Legend is visible. German description. Labels `0`, `15`, `30`,
      `50`, `100` (FR-012).
- [X] Only one data-layer control exists. Label `Bäume` (FR-013).
- [X] Zoom in, zoom out, and north-reset controls are visible and
      functional (FR-017).
- [X] Attribution control is reachable. It lists LGL (`dl-de/by-2-0`),
      basemap.de, CityTreeCover (FR-019).
- [X] Reload at 360 px viewport width. Legend and controls remain
      readable and usable (FR-018).
- [X] No analytics or telemetry (FR-001).
- [X] No third-party requests. Only the basemap tiles and the vendored
      libs load.

## Palette checks

Building values are accepted (`values` pass). All checks apply.

- [X] Buildings use the reference palette at 75% opacity (FR-010).
- [X] Building outlines are thin gray (FR-010).
- [X] Colors interpolate continuously between stops. Values above 80%
      keep the final reference color (FR-011).

## Result

- [X] All applicable checks pass.
