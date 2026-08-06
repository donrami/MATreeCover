# Feature Specification: Heatwave Map Insights

**Feature Branch**: `011-heatwave-map-insights`

**Created**: 2026-08-06

**Status**: Draft

**Input**: User description: "I would like to explore what additions to the user-facing page/map would make sense to add. Im not talking about cosmetic changes only, but rather useful information or data that we can derive from dataset for Mannheim, in the context of the heatwaves"

## Scope

### Goal

Add data-derived insights to the Mannheim tree-cover map that put the
existing per-building values into a heatwave context. The dataset already
contains everything needed: the 60-m tree-cover value per building, the
detected tree areas, the official city boundary, and the 38 official
Stadtteile boundaries. The map currently shows raw values and lets the
visitor judge them alone. This feature derives the information the
heatwave discussion needs: how the neighborhoods compare against the
30 % shade guideline, and where Mannheim stands as a whole.

The anchor for "heatwave context" is the shade guideline the site's own
story already cites (SPIEGEL, July 2026): about 30 percent of the 60-m
surroundings should be shaded.

Derived numbers from the accepted dataset (computed 2026-08-06, 92,913
buildings with values of 93,022 total):

- City mean tree cover in the 60-m radius: 22.2 %, median 20.8 %.
- Only 24.1 % of buildings reach the 30 % shade guideline; 16.2 % have
  less than 10 %, 6.3 % less than 5 %.
- District means range from 9.6 % (Innenstadt, 98.2 % of buildings
  below the guideline) to 34.5 % (Niederfeld).
- 153,524 detected tree areas.

### In Scope

- Clickable Stadtteile with per-district statistics in the popup
  (building count, mean tree cover, share below the 30 % guideline).
- A compact city overview panel with derived city-level statistics.
- Enriched building popup: district name and district mean.
- All derived data precomputed into the static bundle; German copy
  consistent with the site's existing style.
- District attribution (official GDI-MA Stadtteile, dl-de/by-2-0) on
  the attribution page, consistent with the existing credits.

### Out Scope

- Any external data source: measured temperatures, land-surface
  temperature, climate models, population or vulnerability data. Only
  data derivable from the published Mannheim dataset is used.
- Changing the underlying tree-cover values, the 0.5-threshold decision
  (feature 009), or the default view's color semantics.
- The "Hitzebelastung" heat-exposure view (removed 2026-08-06): it
  re-encodes the same per-building values with no new information and
  adds a second toggle that risks confusing users. The 30 % guideline
  remains visible as the existing legend tick and through the district
  and city statistics.
- Removing or altering existing features (Bäume toggle, brightness
  slider, story modal, disclaimer).
- Server-side or on-demand computation: everything is precomputed at
  publish time.

## Clarifications

### Session 2026-08-06

- Q: Should the Hitzebelastung view be removed from the feature, or kept as implemented? → A: Remove it (Option B). The heat-exposure view re-encodes the same per-building values with no new information and adds a second toggle that risks confusing users. US1 (FR-001..FR-005, SC-001) is dropped from scope; the 30 % guideline stays visible as the existing legend tick and through the district and city statistics.
- Q: The city panel shows "Erkannte Baumflächen: 153 524" without a unit — is that the number of trees? → A: No. It is the number of detected tree areas (canopy polygons from the published tree layer, `trees_polygons.geojson`), not individual trees; one area can contain several trees. The panel label must state the unit explicitly: "Anzahl der erkannten Baumflächen".

## User Scenarios & Testing *(mandatory)*

### User Story 2 - Neighborhood Comparison via Stadtteile (Priority: P2)

A visitor wants to know which neighborhoods in Mannheim are worst off
during a heatwave. Clicking a Stadtteil opens a popup with statistics
derived from the building values inside it: how many buildings it has,
its mean tree cover, and the share of buildings below the 30 % shade
guideline. This turns the map from "one building at a time" into a
comparison of all 38 districts.

**Why priority**: Heatwave reporting and city planning compare
neighborhoods, not single buildings. The district boundaries and the
building values are both already in the dataset; only the aggregation
is new.

**Independent Test**: Click every one of the 38 Stadtteile and verify
the popup appears with statistics, and that the displayed numbers match
an independent recomputation for at least 5 sampled districts.

**Acceptance Scenarios**:

1. **Given** the map with the district layer visible, **When** the
   visitor clicks a Stadtteil, **Then** a popup shows the district name,
   building count, mean tree cover, and share of buildings below the
   30 % guideline.
2. **Given** a district popup, **When** the visitor compares Innenstadt
   and Niederfeld, **Then** the displayed values differ in the expected
   direction (Innenstadt lower mean, higher share below the guideline),
   matching the dataset.
3. **Given** the district layer, **When** the visitor clicks outside all
   districts, **Then** no district popup appears and any open popup
   closes.

---

### User Story 3 - City Overview Panel (Priority: P3)

A visitor wants a quick answer to "how heat-exposed is Mannheim as a
whole". A compact panel on the map shows derived city statistics: the
mean tree cover in the 60-m radius, the share of buildings that reach
the 30 % shade guideline, and the number of detected tree areas. The
panel gives the numbers the raw map cannot convey by itself.

**Why priority**: The overview turns the map into a communicable story
("only one in four buildings has adequate shade") that raw colors do
not state. It is a small, static addition built from the same derived
aggregates.

**Independent Test**: Open the map, read the panel, and verify each
number against the city-level aggregates recomputed from the dataset.

**Acceptance Scenarios**:

1. **Given** the map, **When** the visitor reads the overview panel,
   **Then** it shows the mean tree cover, the share of buildings at or
   above the 30 % guideline, and the number of detected tree areas.
2. **Given** the overview panel, **When** the numbers are recomputed
   from the published building values, **Then** the displayed values
   match the recomputation (mean within 0.5 percentage points, shares
   within 1 percentage point, tree count within 1 %).
3. **Given** a narrow screen, **When** the visitor opens the map,
   **Then** the panel stays readable and does not break the layout.

---

### User Story 4 - Building Popup with District Context (Priority: P4)

When a visitor clicks a building in the default view, the popup
additionally shows which Stadtteil the building is in and that
district's mean tree cover. This gives immediate context: a building
with 20 % cover reads differently in Innenstadt (above the district
mean) than in Niederfeld (below it).

**Why priority**: It enriches the existing popup with data already
derived for User Story 2, at almost no additional cost, and deepens the
per-building understanding without a new interaction.

**Independent Test**: Click buildings in at least three different
Stadtteile and verify the popup shows the correct district name and
district mean.

**Acceptance Scenarios**:

1. **Given** the default view, **When** the visitor clicks a building
   inside a Stadtteil, **Then** the popup shows the district name and
   the district's mean tree cover in addition to the building's value.
2. **Given** a building outside all district boundaries, **When** the
   visitor clicks it, **Then** the popup shows the value without a
   district line.
3. **Given** the popup, **When** the district data is missing or
   incomplete, **Then** the popup falls back to showing no district
   line rather than an incorrect number.

### Edge Cases

- A building without a value (56 of 93,022): the popup shows the
  existing en-dash placeholder and the building keeps its current
  rendering.
- Districts that are mostly non-residential (industrial, port, forest
  areas): statistics are still derived from the buildings that exist;
  a district with no buildings shows "no data" instead of fabricated
  numbers.
- The district popup on narrow screens: it must not overflow the
  viewport.
- Stale derived data: the precomputed district and city statistics must
  be regenerated with the same pipeline run that publishes the building
  values, so the displayed numbers always belong to the published
  release.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-006**: All 38 official Stadtteile MUST be clickable and MUST open
  a popup with the district name, building count, mean tree cover, and
  share of buildings below the 30 % guideline.
- **FR-007**: District statistics MUST be derived from the same
  per-building values that are published, so the numbers are consistent
  with the map.
- **FR-008**: The map MUST show a city overview panel with the mean
  tree cover, the share of buildings at or above the 30 % guideline, and
  the number of detected tree areas (canopy polygons, not individual
  trees), labeled with the unit explicitly.
- **FR-009**: The building popup in the default view MUST show the
  district name and district mean tree cover when the building lies
  inside a district.
- **FR-010**: All derived data (district statistics, city statistics)
  MUST be precomputed into the static bundle; the site MUST
  make no new network requests and MUST NOT require a server.
- **FR-011**: All new copy MUST be German and MUST follow the site's
  copy conventions (no em-dashes or en-dashes; hyphens only inside
  compounds; no AI-typical phrasing).
- **FR-012**: The existing controls (Bäume toggle, brightness slider)
  MUST keep working, and the default state of the map MUST be
  unchanged.
- **FR-013**: New controls and popups MUST be accessible:
  keyboard-operable, with sufficient color contrast for the district
  popup and the city panel.
- **FR-014**: The attribution page MUST credit the district data source
  (official GDI-MA Stadtteile, dl-de/by-2-0) and MUST briefly explain
  how the statistics are derived, consistent with the existing accuracy
  disclaimer (feature 010).

### Key Entities *(include if feature involves data)*

- **Stadtteil Statistics**: derived per district (building count, mean
  tree cover, share below the guideline); precomputed, keyed by the
  official district name.
- **City Overview Statistics**: derived city-wide aggregates (mean tree
  cover, share at or above the guideline, detected tree count).
- **District Layer**: the 38 official Stadtteile boundaries (GDI-MA),
  shown as interactive areas on the map.
- **Popup Content**: building value, district name, district mean;
  assembled from the precomputed data, never computed on the client.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-002**: All 38 Stadtteile are clickable, and their displayed
  statistics match an independent recomputation for all districts
  (mean within 0.5 percentage points, share within 1 percentage point).
- **SC-003**: The city overview panel matches the dataset aggregates
  (mean 22.2 %, 24.1 % of buildings at or above the guideline) within
  the same tolerances.
- **SC-004**: The map renders the published appearance (no new view is
  introduced), and all existing interactions keep their behavior.
- **SC-005**: All new copy contains zero em-dashes and zero en-dashes
  (mechanical check) and is in German.
- **SC-006**: The existing performance budgets hold: first usable map
  within the current budget and all new interactions within the current
  2-second interaction budget.
- **SC-007**: The page performs zero new network requests compared with
  the published site and remains fully functional offline after first
  load.
- **SC-008**: The existing test suites remain green and `make
  check-public` stays clean.
- **SC-009**: The attribution page credits the district data source and
  explains how the statistics are derived (verifiable inspection),
  consistent with the existing accuracy disclaimer.

## Assumptions

- "Dataset for Mannheim" means the published dataset: 93,022 buildings
  with 60-m tree-cover values, 153,524 detected tree areas, the city
  boundary, and the 38 official Stadtteile. No external data (measured
  temperatures, climate models, population, vulnerability indices) is
  added in this feature.
- The 30 % shade guideline from the SPIEGEL report (July 2026) that the
  site's story modal already cites is the reference for the heatwave
  context, and the exposure-class boundaries (10 % / 30 %) follow the
  thresholds the pipeline already uses for its statistics.
- All derived data is computed once at publish time and shipped as
  static files; there is no server, database, or analytics (existing
  site constraint, FR-001 of the base project).
- The district layer uses the official GDI-MA Stadtteile boundaries
  already used in the verification workflow (dl-de/by-2-0), credited on
  the attribution page.
- The site language is German; all new copy follows the conventions of
  feature 007 (hyphens only, no dashes).
