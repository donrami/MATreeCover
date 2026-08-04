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

## Darkened base map (003-darken-base-map, SC-001/SC-002/SC-003,
FR-001..FR-008)

Measured 2026-08-04 on the published bundle at
`raster-brightness-max: 0.65`; evidence in
`validation/darken/luminance.json`.

- [X] Base map is measurably darker: mean luminance of a fixed
      basemap-only region dropped ≥30% vs the pre-change bundle
      (measured 0.1691 → 0.1183, ratio 0.6995; median per-pixel
      scaling 0.6632 ≈ 0.65) (SC-001, FR-001).
- [X] Base map stays grayscale: no hue or tint on the base map;
      per-pixel transform scales RGB channels identically (FR-002).
- [X] Building value colors unchanged: palette stops and 0.75 opacity
      identical to the reference (FR-003); light colors improved
      contrast (yellow ΔE 70.7 vs darkened background).
- [X] Every value color distinguishable from the darkened background
      at default zoom: yellow 70.7, orange 42.6, brown 17.7, dark
      blue 31.8, light blues 33–40 (ΔE; brown is the dark end of the
      frozen scale and remains clearly visible) (SC-002, FR-004).
- [X] Unavailable buildings visible: marker lightened to `#b8b8b8`
      at 0.8 during implementation (the dark marker collapsed to
      ΔE 4.6 against darkened blocks, violating FR-007); measured
      local ΔE 22–30 on real buildings (FR-007).
- [X] Tree layer clearly visible over the darkened base map when
      toggled on (green ΔE 66.6) (FR-006).
- [X] Darkening applies at every zoom level (constant paint value,
      no zoom stops) (FR-008).
- [X] Street and district labels legible by eye at a downtown zoom:
      ten sampled labels read without strain (SC-003; confirmed by
      maintainer eyeball pass on the served bundle 2026-08-04;
      structural + OCR evidence: edge positions 90.8% preserved, OCR
      reads "Friedrichsplatz", "Jesuitenkirche").

## Brightness slider (004-map-ui-brightness-legend, FR-001..FR-007,
FR-016, SC-001)

Measured 2026-08-04 on the published bundle; evidence in
`validation/brightness-slider/luminance.json`.

- [X] A "Helligkeit" slider exists in the tools card, default value
      65 (FR-001, FR-003).
- [X] On load the map matches the pre-feature bundle appearance
      (FR-003).
- [X] Dragging dims the base map live; buildings and trees keep
      their colors (FR-002, FR-004).
- [X] Dragging does not pan the map; panning does not reset the
      slider (FR-006).
- [X] Reloading resets the slider and the map to the default
      (FR-007).
- [X] Slider visible and usable at 360 px viewport width (FR-016).
- [X] Luminance gates pass: minimum < 10% of default, maximum
      restores the original un-darkened luminance (SC-001).

## Low-brightness inversion (004-map-ui-brightness-legend, FR-019,
SC-008)

Measured 2026-08-04 on the published bundle after the inversion
slice; evidence in `validation/brightness-slider/luminance.json`.

- [X] Dragging below 25 crossfades the base map gradually into the
      photo-negative; no sudden switch at the threshold (FR-019).
- [X] At 5, streets and labels render lighter gray than the
      near-black background and remain legible (FR-019, SC-008).
- [X] At 5, inverted features never exceed the 0.65 cap
      (per-pixel sRGB luminance ≤ 0.65; measured max 0.6275 sRGB;
      SC-008, clarification Q4).
- [X] The inverted map stays grayscale: no hue shift (FR-019).
- [X] Buildings, trees, popup, and zoom controls unaffected at any
      slider position (FR-019, FR-014).
- [X] At slider ≥ 25 the rendering is identical to the pre-inversion
      appearance (FR-003 regression).

## Gradient legend (004-map-ui-brightness-legend, FR-010..FR-013,
FR-018, SC-005)

- [X] Legend shows one continuous gradient bar, no segment
      boundaries (FR-010/FR-011).
- [X] Tick labels 0, 15, 30, 50, 100 at proportional positions
      (FR-012).
- [X] Title, description, and "Prozent" unit retained (FR-013).
- [X] Screen-reader value list present; values exposed as text
      (FR-018).
- [X] At 360 px the bottom strip shows the gradient with all labels
      visible (SC-005).

## Result

- [X] All applicable checks pass.
