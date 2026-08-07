# Feature Specification: Popup Comparative Context

**Feature Branch**: `main`
**Created**: 2026-08-07
**Status**: Draft
**Input**: User description: "we need to enhance the popups that appear when clicking a building or a district. The scope should include improving the way the data is shown for impact and clarity, and think about metrics or indicators that puts a certain district or building in comparative context to the rest ... we need to plan this well"

## Scope

### Goal

Make the building and district popups instantly informative: a visitor sees **what** the number is, **how good or bad it is** relative to the district and the city, and — for districts — **where the district stands** among all 38 Mannheim districts. Restructure popup content for visual hierarchy and comprehension, without changing the underlying data or the interaction model from features 002 and 011.

### Current State (evidence)

- Building popup (`src/site/main.js`, `buildingPopupHtml` + `buildingDistrictHtml`): three lines — "Baumanteil im 60-m-Umkreis" value, "Stadtteil" name, "Durchschnitt im Stadtteil" average. No comparison to the city, no assessment of the value.
- District popup (`districtPopupHtml`): four lines — name, "Gebäude" count, "Baumanteil im Durchschnitt" mean, "Anteil unter 30 %" share. No rank, no city comparison, no quartile context.
- Available client-side without pipeline changes: city statistics (`city_stats.mean_value_pct`, `share_gte30_pct`, `tree_count` in style metadata, consumed by `renderCityPanel`) and all 38 district features (`mean_value`, `n_buildings`, `share_lt30`), which is enough to compute rank, quartile band, and all deltas.
- Site language: German. All popup copy stays German.
- Data model: district average = mean tree-share of the district's buildings; city average = mean tree-share across all Mannheim buildings (publish-time value). "60-m-Umkreis" = tree share in the 60 m radius around the building. 30 % = adequate-shading threshold used across the app.

### In Scope

- Building popup: headline value plus comparison against the district average and the city average, each with a signed delta in percentage points and an assessment word ("über"/"unter"/"auf …-Niveau").
- District popup: headline mean plus comparison against the city average, a rank among all districts ("Platz X von 38"), a quartile band with text label and color, and the existing building-count and share-below-30 % lines.
- 30 %-threshold indicator on the building popup ("erreicht"/"verfehlt").
- Brief metric explanation in both popups so the numbers cannot be misread ("Was bedeutet das?" help line).
- Visual hierarchy: name header, prominent value, secondary context block, badge, footnote. Color used only as reinforcement — every color-coded fact also has a text label.
- Graceful degradation when data is missing (building without value, district without mean, stale city stats).
- Interaction model from features 002/011 unchanged: at most one popup open, building click replaces building popup, district click replaces district popup, empty-space click closes.

### Out of Scope

- Any new data dimensions (heat, green space, tree counts per district, per-building percentiles). Only data already present in the published bundle is used.
- Changes to value computation, palette, building properties, pipeline, district geometry, or the map layers.
- Changing the existing interaction/arbitration behavior (002/011).
- Number-formatting reform (keeps current dot-decimal convention).
- Changes outside Mannheim.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Building Value in Context (Priority: P1)

A visitor clicks a building and immediately sees the building's tree-share value, whether it is above or below the average of its district and of the whole city, and how far (delta in percentage points). No mental arithmetic needed.

**Why priority**: The building popup is the most-clicked surface (002). A bare percentage tells a visitor nothing about whether the building is good or bad; the district/city comparison is what makes the number meaningful.

**Independent Test**: On the published bundle, click ten buildings in different districts. For each, read the value line and both comparison lines; verify the assessment words and deltas are correct by cross-checking against the district's mean and the city average.

**Acceptance Scenarios**:
1. **Given** a building with a valid value, **When** the visitor clicks it, **Then** the popup shows the value ("Baumanteil im 60-m-Umkreis") prominently, the district name, and the district average with a signed delta (e.g. "−2,3 pp" style, dot-decimal per convention).
2. **Given** the building value is below the district average, **When** the popup renders, **Then** the district comparison line reads "unter dem Stadtteil-Durchschnitt" with a negative delta; the equivalent applies for "über".
3. **Given** the building value is within 0.1 pp of the district average, **When** the popup renders, **Then** the line reads "auf Stadtteil-Niveau" with delta "±0,0 pp" (neutral, no color).
4. **Given** a building with a valid value, **When** the popup renders, **Then** it also compares the value against the city average with delta and assessment word, using the same rules as scenarios 2–3.
5. **Given** a building with a valid value, **When** the popup renders, **Then** it states whether the building reaches the 30 % adequate-shading threshold ("erreicht"/"verfehlt").
6. **Given** a building without a valid value, **When** the visitor clicks it, **Then** the value line shows the unavailable marker (never `0.00 %`), no deltas are computed, and the district name + district average context lines still render.

### User Story 2 - District Standing Among All Districts (Priority: P1)

A visitor clicks a district and immediately sees where the district stands: its average tree share, whether it is above or below the city average, its rank out of 38 districts, and which quarter of districts it falls into.

**Why priority**: District-level comparison ("how does this district compare to the rest") is the explicit core of the request, and district rank/quartile is the strongest possible comparative indicator available in the bundle.

**Independent Test**: On the published bundle, click ten districts. Verify the rank shown for each matches an independently computed ordering of the 38 districts by average tree share, and that the quartile label matches the rank.

**Acceptance Scenarios**:
1. **Given** a district with a valid mean, **When** the visitor clicks it, **Then** the popup shows the district name as header and the mean as the headline value.
2. **Given** the district mean is above the city average, **When** the popup renders, **Then** a comparison line reads "über dem Stadtdurchschnitt" with a signed delta; the equivalent applies for "unter", and within 0.1 pp it reads "auf Stadtniveau".
3. **Given** a valid district mean, **When** the popup renders, **Then** it shows the rank as "Platz X von 38" where rank 1 is the district with the highest average tree share.
4. **Given** a valid district mean, **When** the popup renders, **Then** it shows a quartile band label — "oberstes Viertel", "oberes Mittelfeld", "unteres Mittelfeld", "unterstes Viertel" — consistent with the rank (bounds documented in Requirements).
5. **Given** a valid district mean, **When** the popup renders, **Then** the existing "Gebäude" count and "Anteil unter 30 %" lines remain present.
6. **Given** a district without a valid mean, **When** the visitor clicks it, **Then** the popup shows name and building count, marks the mean as unavailable, and hides rank/quartile/city comparison.

### User Story 3 - Understand the Numbers (Priority: P2)

A visitor who is unsure what "Baumanteil im 60-m-Umkreis" or the 30 % threshold means can get a one-line explanation inside the popup, without leaving the map.

**Why priority**: "Impact and clarity" requires that numbers not be misread. An unexplained metric invites wrong conclusions (e.g., treating the 60-m-radius share as the building's own roof coverage).

**Independent Test**: On the published bundle, open both popup types and verify an explanation of the headline metric and of the 30 % threshold is present and readable on desktop and mobile widths.

**Acceptance Scenarios**:
1. **Given** either popup open, **When** the visitor reads the footnote, **Then** it explains what the headline metric measures in one plain-German sentence.
2. **Given** the building popup open, **When** the visitor reads the footnote, **Then** the 30 % adequate-shading threshold is explained.
3. **Given** a narrow viewport (mobile), **When** the popup renders, **Then** all content is visible or scrollable within the popup; no line is clipped.

### Edge Cases

- Building without valid value: unavailable marker on the value line, no deltas, district context still shown (see US1-S6).
- District without valid mean: no rank, no quartile, no city comparison; name and building count still shown.
- City statistics missing from style metadata (stale bundle): all city-average comparisons are hidden; district rank/quartile still computed from the 38 district features.
- Fewer than two districts with valid means: rank/quartile hidden entirely.
- Ties in district means: ranking is deterministic — sort by mean descending, then by name ascending; tied districts receive distinct sequential ranks (documented, reproducible).
- Deltas rounding to zero (|Δ| < 0.1 pp): rendered as neutral "auf …-Niveau", no misleading sign.
- Building value exactly 30.0 %: counts as "erreicht" the threshold.
- District mean exactly equal to city average: "auf Stadtniveau".
- Rapid clicks between building and district: existing 002/011 arbitration preserved — one popup at a time, last click wins.
- Popup at viewport edge: stays within the visible area (existing behavior), new content must not increase clipping risk on small screens.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Building popup MUST show the building's tree-share value ("Baumanteil im 60-m-Umkreis") as the headline, with label, value, and unit.
- **FR-002**: Building popup MUST show the district name.
- **FR-003**: Building popup MUST show the district average together with the signed delta between building value and district average, and an assessment word: "über dem Stadtteil-Durchschnitt" (delta > +0.1 pp), "unter dem Stadtteil-Durchschnitt" (delta < −0.1 pp), "auf Stadtteil-Niveau" (|delta| ≤ 0.1 pp).
- **FR-004**: Building popup MUST show the city average together with the signed delta and assessment word ("über/unter dem Stadtdurchschnitt", "auf Stadtniveau"), using the same 0.1 pp rule.
- **FR-005**: Building popup MUST state whether the building reaches the 30 % threshold ("erreicht"/"verfehlt").
- **FR-006**: Building without valid value MUST show the unavailable marker on the value line, MUST NOT compute or show deltas, and MUST still show the district context lines. It MUST never display a fabricated value.
- **FR-007**: District popup MUST show the district name as header, the mean as headline value, the building count, and the share of buildings below 30 % (existing lines preserved).
- **FR-008**: District popup MUST show the city average with signed delta and assessment word (same 0.1 pp rules as FR-003/FR-004).
- **FR-009**: District popup MUST show the district's rank among all districts as "Platz X von 38", rank 1 = highest mean; ties broken deterministically (mean desc, then name asc).
- **FR-010**: District popup MUST show a quartile band consistent with the rank: "oberstes Viertel" (rank 1–10), "oberes Mittelfeld" (11–19), "unteres Mittelfeld" (20–28), "unterstes Viertel" (29–38). (38 districts → bands of 10/9/9/10; exact split documented in plan.)
- **FR-011**: District without valid mean MUST show the mean as unavailable, MUST hide rank, quartile, and city comparison, and MUST still show name and building count.
- **FR-012**: Both popups MUST include a footnote explaining the headline metric in one plain-German sentence; the building popup footnote MUST also explain the 30 % threshold.
- **FR-013**: Both popups MUST present content with a consistent visual hierarchy: name header, headline value, context lines, badge, footnote. Every color-coded fact MUST also carry a text label (no color-only encoding).
- **FR-014**: When city statistics are missing from the published bundle, city-comparison lines MUST be hidden; district rank/quartile MUST still render when at least two districts have valid means.
- **FR-015**: The interaction model MUST remain unchanged from features 002/011: at most one popup open, building click shows/replaces building popup, district click shows/replaces district popup, empty-space click closes; popup close button and German close tooltip keep working.
- **FR-016**: Popup content MUST fit (be fully visible or scrollable) at mobile viewport widths without clipping any line.
- **FR-017**: All new labels, assessment words, and explanations MUST be German, consistent with existing popup copy.

### Key Entities

- **Building Footprint**: accepted official building geometry; optional tree-share value ("Baumanteil im 60-m-Umkreis", two decimals, may be unavailable). Key attributes for this feature: `has_value`, `value_str`.
- **District (Stadtteil)**: one of 38 administrative districts; carries `name`, `n_buildings`, `mean_value`, `share_lt30`. Comparative attributes computed at display time: rank (1–38), quartile band, delta vs city average.
- **City Statistics**: publish-time city-wide aggregates (`mean_value_pct`, `share_gte30_pct`, `tree_count`); source of the city-average reference in both popups.
- **Selection Popup**: single compact popup per entity type (building popup / district popup); state: open/closed, which entity it shows, which context lines are available.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the published bundle, a visitor can determine whether a building is above or below its district average in under 5 seconds without instructions (tested with 10 buildings).
- **SC-002**: On the published bundle, a visitor can determine where a district stands relative to the rest (above/below city average, rank, quartile) in under 5 seconds without instructions (tested with 10 districts).
- **SC-003**: Rank and quartile shown in the district popup match an independent computation for 100 % of the 38 districts (automated cross-check).
- **SC-004**: 100 % of building clicks on buildings with valid values show the value, both deltas, and the threshold status; 0 % show a wrong or fabricated value.
- **SC-005**: No regression of features 002/011: at most one popup open at any time across 20 mixed building/district/empty-space clicks; hover cursor, unavailable marker, close button, and German close tooltip still work.
- **SC-006**: Popup content renders without clipped lines on a 360 px wide viewport for both popup types (manual check, 3 representative districts/buildings each).
- **SC-007**: 90 % of sampled popups show the metric footnote; a visitor reads and understands what "60-m-Umkreis" measures (5-person comprehension spot check, 4 of 5 correct restatement).

## Assumptions

- All comparative metrics are computed client-side from data already in the published bundle (38 district features, style-metadata city stats). No pipeline, data, or publish-time changes.
- The city average reference is the publish-time `mean_value_pct` (already shown in the "Mannheim im Überblick" panel) so popups and panel never contradict.
- Delta display keeps the current dot-decimal convention (e.g. "4.2 %", "−2.3 pp"); no German-comma reform.
- "pp" (percentage points) is used for deltas so visitors do not confuse them with relative percentages.
- The 0.1 pp neutral band ("auf …-Niveau") prevents misleading signs from rounding.
- Quartile bands are derived from rank over the 38-district set (10/9/9/10 split); if the district set size changes, bands adapt proportionally — documented in plan.
- The 30 % threshold and its "ausreichende Beschattung" wording follow existing app copy.
- The popup interaction/arbitration model (002/011) is a fixed contract; this feature only changes popup *content and presentation*.
- Heat and other new data dimensions are out of scope; a future feature can add them into the same layout.

## Dependencies

- Feature 002 (building popup interaction) and feature 011 (district popup stats, city overview) behavior must remain intact (FR-015).
- Published bundle must contain the stadtteile source (38 features with `mean_value`) and `city_stats` metadata; degradation paths defined in FR-006/FR-011/FR-014 cover stale bundles.
- Verification assets: `verification/stadtteile.geojson` (38 districts) for the rank cross-check (SC-003).
