# Feature Specification: Accuracy Disclaimer on the Site

**Feature Branch**: `010-accuracy-disclaimer`
**Created**: 2026-08-05
**Status**: Draft
**Input**: Calibration decision (feature 009, recorded in `verification/report.md`): keep the published 0.5-threshold values and add a disclaimer to the site. The disclaimer must tell the general accuracy picture — the values are model-based estimates with imperfect tree detection — without naming individual Mannheim districts.

## Scope

### Goal

A short, honest, German disclaimer on the site's attribution page explaining that the tree-cover values come from automated analysis of aerial imagery and are indicative, not exact measurements — the general reliability picture from the verification, without district specifics.

### In Scope

- One new section on the attribution page (`src/site/attribution.html`): the general accuracy picture of the tree detection.
- One short note in the map's legend card (`src/site/index.html` + `style.css`): values are automatic estimates, details linked to the attribution page (owner decision, 2026-08-05 — visibility option B).
- German copy, consistent with the site's existing style (no em-dash/en-dash, hyphens only inside compounds, no AI-typical phrasing).
- The deployed copy of the site in `dist-assets/` stays in sync with the source.

### Out of Scope

- Any mention of individual Mannheim districts or per-district findings.
- Changes to the map page, style, legend, building values, or tree layer.
- New pages, modals, popups, or network requests.
- Publishing the verification numbers or the calibration results on the site.
- Re-releasing the map data (values stay at the 0.5 threshold).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visitor Reads the Accuracy Note (Priority: P1)

A visitor opens the attribution page (linked from the map) and reads a short note: the tree-cover values are automated estimates from aerial imagery; tree detection is imperfect (some non-tree surfaces can count as tree cover, some trees can be missed); the values are a rough overview, not a precise measurement.

**Why priority**: This is the entire feature — the calibration decision (009) makes this note the mitigation for the documented detection inaccuracy.

**Independent Test**: Open the attribution page; the accuracy section is present, in German, names no district, and makes no claim beyond the verification evidence.

**Acceptance Scenarios**:

1. **Given** the attribution page, **When** a visitor opens it, **Then** an accuracy section explains the values are model-based estimates from aerial imagery.
2. **Given** the accuracy section, **When** the visitor reads it, **Then** it states detection is imperfect: non-tree surfaces (roofs, lawns, fields, railway areas) can be counted as tree cover, and some trees can be missed.
3. **Given** the accuracy section, **When** the visitor reads it, **Then** it states the values are indicative, not exact measurements.
4. **Given** the accuracy section, **When** the visitor reads it, **Then** it names no individual Mannheim district and cites no district-level numbers.
5. **Given** the attribution page, **When** the visitor reads the whole page, **Then** the map page, legend, values, and tree layer are unchanged.

### Edge Cases

- Long text on narrow screens: the section scrolls with the page like the rest of the attribution page (no fixed layout).
- The disclaimer must not overstate: it claims nothing beyond the 008/009 evidence (imperfect detection, general reliability).
- No em-dash/en-dash anywhere in the section (site copy convention from 007).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The attribution page MUST include a German accuracy section stating that the tree-cover values are automated estimates from aerial imagery.
- **FR-002**: The section MUST state that tree detection is imperfect — non-tree surfaces can be counted as tree cover and some trees can be missed.
- **FR-003**: The section MUST state that the values are indicative, not exact measurements.
- **FR-004**: The section MUST NOT name any individual Mannheim district and MUST NOT cite district-level numbers.
- **FR-005**: The feature MUST NOT change the building values, tree layer, legend semantics, or any map behavior. The only map-page change is the legend note (FR-010).
- **FR-006**: The feature MUST NOT add any network request, script, or tracking.
- **FR-007**: The section MUST follow the site's German copy convention: no em-dash or en-dash, hyphens only inside compounds, no AI-typical phrasing.
- **FR-008**: The deployed copy of the attribution page (`dist-assets/attribution.html`) MUST match the source change.
- **FR-010**: The map's legend card MUST show a short German note that the values are automatic estimates from aerial imagery, with a link to the attribution page ("Details unter Datenquellen").
- **FR-011**: The legend note MUST NOT change legend semantics (0–100 % scale, tick labels, colors) and MUST NOT add any network request or script.

### Key Entities *(include if feature involves data)*

- **Accuracy Section**: static German text on the attribution page — model-based estimates, imperfect detection (over- and under-detection in general terms), indicative values, no district specifics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The attribution page contains the accuracy section (verifiable by inspection).
- **SC-002**: The section contains zero district names and zero district-level numbers.
- **SC-003**: The section contains zero em-dashes and zero en-dashes (mechanical check).
- **SC-004**: The map page and all map artifacts are byte-identical apart from the attribution page change.
- **SC-005**: Existing test suites remain green; `make check-public` stays clean.

## Assumptions

- The attribution page is the disclaimer's home (it is the site's existing "Datenquellen" page, linked from the map); no map-page UI change.
- Wording is drafted by the implementer and approved by the owner before deploy.
- The map data itself is not re-released: values stay at the 0.5 threshold (009 decision).
- The disclaimer is static HTML; no build or server change.

## Dependencies Evidence

- Attribution page: `src/site/attribution.html` (static, German, dark theme; part of the publish bundle via `src/pipeline/publish.py`; deployed copy tracked at `dist-assets/attribution.html`).
- Decision evidence: `verification/report.md` — calibration section (009): candidates 0.6/0.65, retention 82.9 %/75.8 % in previously correct patches, vision pass finding 70-85 % real-tree loss, decision to keep 0.5.
- Site constraints: static, no build, CSP `script-src 'self'` — the section is pure HTML content, no scripts.
