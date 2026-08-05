# Feature Specification: Mannheim Tree-Cover Parity

**Feature Branch**: `main`

**Created**: 2026-08-03

**Status**: Draft

**Input**: Reproduce CityTreeCover for Mannheim. Match its data meaning and presentation, reuse valid prior data, and prevent further scope growth.

## Scope

### Goal

Create the smallest complete Mannheim version of the deployed CityTreeCover map.

### In Scope

- A public, full-window map with the reference dark appearance.
- Mannheim buildings colored by their mean tree-cover percentage within a 60 m radius.
- The reference legend, building interaction, map controls, and optional tree layer.
- A Mannheim-only default view with the area outside the city boundary obscured.
- Reuse of accepted artifacts from the archived mannheim workspace.
- One static German presentation for desktop and mobile browsers.
- Required map and Mannheim data attribution.

### Out of Scope

- Any study area beyond Mannheim, except the minimum 60 m halo required by FR-006.
- Statistics panels, charts, district summaries, search, filters, or shareable map state.
- Heat, weather, shade simulation, planting advice, or time-series comparisons.
- User accounts, authentication, editing, analytics, databases, or application servers.
- A language selector or an internationalization framework.
- Textured tree patterns, automatic camera flights, or extra explanatory panels.
- Label Studio, a labeling campaign, model training, or model fine-tuning.
- Synthetic, demonstration, or placeholder data in a published map.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Mannheim Color Map (Priority: P1)

A visitor opens the page and sees Mannheim buildings colored like the reference map. The city boundary defines the complete visible study area.

**Why this priority**: The color map is the product's primary value and the missing result in the previous attempt.

**Independent Test**: Open the page in a clean browser. Compare the initial view, palette, outlines, legend, and boundary against the reference.

**Acceptance Scenarios**:

1. **Given** a first visit, **When** the map loads, **Then** Mannheim fills the view and the exterior remains obscured.
2. **Given** valid building data, **When** rendering completes, **Then** each Mannheim building uses the reference color scale.
3. **Given** the map is visible, **When** the visitor pans or zooms, **Then** no analytical feature appears outside Mannheim.
4. **Given** a 360-pixel-wide screen, **When** the page loads, **Then** the legend and controls remain readable and usable.
5. **Given** the map is visible, **When** the visitor uses navigation controls, **Then** zoom and north reset work.
6. **Given** the map is visible, **When** attribution opens, **Then** all required providers and licenses are identified.

---

### User Story 2 - Inspect a Building Value (Priority: P2)

A visitor points to a building and selects it. The visitor then reads the building's tree-cover percentage.

**Why this priority**: This interaction explains the colors without adding a dashboard or other scope.

**Independent Test**: Select known buildings with low, middle, and high values. Confirm the displayed values and colors against the accepted data.

**Acceptance Scenarios**:

1. **Given** a building is under the pointer, **When** the pointer enters it, **Then** the pointer indicates that selection is available.
2. **Given** a building has a valid value, **When** the visitor selects it, **Then** a compact popup shows two decimal places.
3. **Given** a building has no valid value, **When** selected, **Then** the map identifies it as unavailable instead of showing zero.

---

### User Story 3 - Toggle Detected Tree Cover (Priority: P3)

A visitor can compare the building colors with detected tree areas. The tree layer starts hidden and uses the reference flat green style.

**Why this priority**: The optional layer supports visual interpretation and is the reference map's only additional data control.

**Independent Test**: Activate and deactivate the tree button. Confirm visibility, button state, style, and unchanged camera position.

**Acceptance Scenarios**:

1. **Given** the page has loaded, **When** no action occurs, **Then** the tree layer remains hidden.
2. **Given** the tree layer is hidden, **When** the visitor activates `Bäume`, **Then** detected tree areas appear in flat green.
3. **Given** the tree layer is visible, **When** the visitor deactivates it, **Then** the layer disappears without moving the map.

---

### User Story 4 - Reuse Prior Work Safely (Priority: P4)

A maintainer evaluates existing Mannheim artifacts before any download or compute job. Accepted artifacts are reused, while failed artifacts are replaced once.

**Why this priority**: This avoids lost work, repeated downloads, local memory exhaustion, and unnecessary GPU costs.

**Independent Test**: Start from the prior workspace inventory. Confirm each planned job has an accepted input, a stated gap, and a resource decision.

**Acceptance Scenarios**:

1. **Given** an equivalent artifact passes acceptance checks, **When** planning continues, **Then** no replacement download or calculation is scheduled.
2. **Given** an artifact fails a coverage or quality check, **When** it blocks publication, **Then** only that artifact and its dependents are regenerated.
3. **Given** a job needs a GPU or exceeds local limits, **When** it is reached, **Then** work pauses and requests a RunPod.
4. **Given** replacement inference is required, **When** the owner supplies RunPod capacity, **Then** accepted existing weights run without new training data.

### Edge Cases

- A building near the boundary needs imagery from a minimal 60 m exterior halo. The map must never publish that exterior area.
- Missing halo imagery must produce an unavailable value. It must not produce a false zero value.
- A building that crosses the boundary may be included. Its visible geometry must stop at the boundary.
- Missing or corrupt data must produce a clear unavailable state. Synthetic data must not replace it.
- A failed tree-layer load must not hide the already loaded building layer.
- Values at palette stops must use the specified stop color. Values between stops must use the same continuous transition as the reference.
- The legend and toggle must not cover required map controls on narrow screens.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST provide a public map without registration or account controls.
- **FR-002**: The initial view MUST show the full official Mannheim boundary with minimal padding and north at the top.
- **FR-003**: The map MUST obscure base-map content outside Mannheim at every supported view.
- **FR-004**: The published building set MUST match the accepted official Mannheim inventory. It MUST contain no outside, synthetic, or duplicate buildings.
- **FR-005**: Each building value MUST equal the mean of 60 m-radius tree-cover percentages sampled across that building footprint.
- **FR-006**: Analysis MAY use only the minimum 60 m exterior halo needed for complete Mannheim building values.
- **FR-007**: The published map MUST exclude all halo geometry, buildings, tree areas, and values outside Mannheim.
- **FR-008**: A valid building value MUST range from 0% through 100% and display with two decimal places.
- **FR-009**: Missing required imagery MUST produce an unavailable value. The product MUST distinguish this state from a valid 0% value.
- **FR-010**: Building fills MUST use the reference palette below with 75% opacity. Outlines MUST remain thin, gray, and subordinate.

| Tree cover | Reference color |
|------------|-----------------|
| 0% | `#ffd524` |
| 12% | `#e6854a` |
| 24% | `#a97e65` |
| 24.08% | `#0674aa` |
| 32% | `#1db6ff` |
| 40% | `#39c2ff` |
| 48% | `#56ceff` |
| 80% and above | `#6ad4ff` |

- **FR-011**: The map MUST interpolate between palette stops. Values above 80% MUST retain the final reference color.
- **FR-012**: The legend MUST use the deployed German description and labels `0`, `15`, `30`, `50`, and `100`.
- **FR-013**: The page title MUST be `Baumfläche`. The only data-layer control MUST be the `Bäume` button.
- **FR-014**: Building hover MUST show a selection pointer. Building selection MUST open the reference's compact value popup.
- **FR-015**: The tree layer MUST start hidden. When active, it MUST use flat `#39C43D` at 75% opacity.
- **FR-016**: Toggling the tree layer MUST not change the current center, zoom, bearing, or pitch.
- **FR-017**: Visitors MUST have zoom-in, zoom-out, and north-reset controls.
- **FR-018**: The layout MUST preserve the reference legend and control arrangement on desktop and narrow mobile screens.
- **FR-019**: Required base-map and Mannheim data attributions MUST remain reachable from the map.
- **FR-020**: A failed optional layer MUST not prevent visitors from using another layer that loaded successfully.
- **FR-021**: Before new downloads or calculations, the project MUST validate candidate artifacts for source, extent, resolution, completeness, and lineage.
- **FR-022**: The project MUST reuse every candidate artifact that passes its acceptance checks.
- **FR-023**: Failed derived artifacts MUST invalidate their dependents. Independent accepted inputs MUST remain reusable.
- **FR-024**: The feature MUST NOT require Label Studio, new training labels, model training, or model fine-tuning.
- **FR-025**: Any replacement inference MUST use existing weights and start only after the owner provides RunPod capacity.

### Operational Constraints

- **OR-001**: Local jobs MUST keep peak resident memory at or below 12 GiB.
- **OR-002**: Local jobs MUST NOT load a complete city raster or vector into memory. Each job MUST stay within OR-001.
- **OR-003**: A job MUST stop before execution when it needs a GPU or cannot meet OR-001. The maintainer MUST request a RunPod.
- **OR-004**: Each accepted specification, plan, implementation slice, and validation milestone MUST have a dedicated commit before the next milestone starts.
- **OR-005**: Data files above 50 MiB MUST stay outside ordinary repository history unless the owner approves them. The repository MUST record each excluded file's path, size, checksum, and source.

### Key Entities

- **Mannheim Boundary**: The official municipal polygon that defines display, publication, and accepted building membership.
- **Building Footprint**: An accepted official building geometry with a stable identifier and optional building value.
- **Detected Tree Area**: A classified canopy area from the accepted imagery and canopy result.
- **Building Value**: The mean 60 m-radius tree-cover percentage across one building footprint.
- **Reusable Artifact**: A prior input or result with known source, extent, resolution, completeness, lineage, and acceptance state.
- **Published Map**: The one Mannheim release that combines accepted buildings, values, tree areas, legend, and controls.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A parity review confirms the dark map, building styles, popup, legend, tree toggle, navigation controls, and mobile layout. It finds no extra feature.
- **SC-002**: On first load, the full Mannheim boundary is visible. No unmasked map area or analytical feature appears outside it.
- **SC-003**: The published building count exactly matches the accepted official Mannheim inventory. The outside and synthetic building counts are zero.
- **SC-004**: For 100 sampled buildings, an independent recalculation differs from the published value by at most one percentage point.
- **SC-005**: At least 17 of 20 distributed image checks correctly distinguish obvious tree crowns from roofs, roads, and water.
- **SC-006**: At least 90% of test visitors report a selected building value within 30 seconds without instructions.
- **SC-007**: At least 90% of test visitors toggle tree areas within 15 seconds. The camera remains unchanged in every trial.
- **SC-008**: On a 25 Mbps connection with 50 ms latency, the map becomes usable within 10 seconds. At least 95% of interactions finish within two seconds.
- **SC-009**: Recorded local processing runs remain at or below 12 GiB peak memory. No GPU job starts on the local machine.
- **SC-010**: The artifact ledger shows zero repeat downloads or calculations for accepted prior artifacts.

## Assumptions

- The deployed CityTreeCover page is the authority for visible scope and presentation.
- The reference repository is the authority for the 60 m metric and palette values.
- One current Mannheim release is sufficient. Historical comparison is not required.
- The map uses German labels only and processes no personal data.
- The current official Mannheim boundary and building inventory remain suitable for publication.
- A minimal 60 m exterior halo is necessary to avoid biased values for boundary buildings.
- Existing artifacts are candidates, not trusted results, until they pass FR-021.
- The previous canopy result fails the current sanity check. Its dependent values and tree areas cannot be published.
- A replacement canopy result will require one owner-approved RunPod inference unless a valid prior result is found.
- Systematic commits protect source and decisions. Large imagery remains in the prior workspace.

## Dependencies and Evidence

- Reference source: [CityTreeCover](https://github.com/jcscaptures/CityTreeCover).
- Presentation authority: [StadtBegruenung](https://schultz-web.de/StadtBegruenung/).
- Reuse source: the archived mannheim workspace.
- Reusable inputs include the Mannheim boundary, buffered boundary, imagery tiles, valid-area mask, and official building geometries.
- Current evidence identifies 93,024 official building footprints.
- Release metadata declares 460 extracted imagery tiles. Planning must verify the exact count.
- Current evidence measures only 0.48% canopy pixels in the latest citywide mask. This result fails the reuse gate.
- Mannheim imagery and building products require the applicable LGL attribution under `DL-DE/BY-2.0`.
- Adapted reference source must preserve the reference project's MIT notice.
