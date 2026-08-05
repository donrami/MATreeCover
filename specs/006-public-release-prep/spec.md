# Feature Specification: Public Release Preparation

**Feature Branch**: `006-public-release-prep`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "prepare to make the repo public. It should be of high quality and have a well written readme that is user focused and not dev focused. Credits should be given to the reference project"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Visitor Understands the Map (Priority: P1)

A person who finds the repository (via a link from the live map, a search, or social media) opens the README and immediately understands what this project is: a web map of Mannheim where every building is colored by the average tree cover within 60 meters of it. They learn how to open the map, how to read the colors, what the tree toggle does, and where the data comes from — all in plain language with no developer jargon.

**Why this priority**: The user-focused README is the explicit core of this feature. It is the first and often only thing a visitor sees; without it, the public release has no front door.

**Independent Test**: A first-time visitor who has never seen the project can, using only the README, (a) state what the map shows, (b) open the live map, and (c) explain what a colored building means. The test passes without the visitor reading any other file or asking any questions.

**Acceptance Scenarios**:

1. **Given** the public repository, **When** a first-time visitor opens the README, **Then** the first screenful explains what the map is and what it shows in plain, non-technical language.
2. **Given** the public repository, **When** a visitor reads the README, **Then** they find a working link to the live map.
3. **Given** the public repository, **When** a visitor reads the README, **Then** they understand how to interpret building colors and how to use the tree layer toggle.
4. **Given** the public repository, **When** a visitor reads the README, **Then** the top half of the document contains no commands, code, exit codes, or build/deploy steps.

---

### User Story 2 - The Owner Publishes the Repository Safely (Priority: P2)

The repository owner makes the repository public and is confident it presents well: the license is stated and backed by a license file, the reference project is credited, and no personal information (local file paths, usernames, credentials) leaks into public view.

**Why this priority**: Public readiness ("high quality") is the frame for the whole feature; it must hold even though the visible deliverable is the README.

**Independent Test**: An automated scan of the repository's public files finds no personal absolute paths (e.g. `/home/<username>/...`), no credential material, and no private host details; a license file exists and matches the license named in the README.

**Acceptance Scenarios**:

1. **Given** the repository ready for publication, **When** an automated scan inspects every tracked file, **Then** it finds zero personal absolute file paths and zero credential material.
2. **Given** the repository ready for publication, **When** a reviewer checks the license, **Then** a license file exists in the repository and its terms match the license stated in the README.
3. **Given** the repository ready for publication, **When** a reviewer reads the credits, **Then** the reference project is named, linked, and its license acknowledged.

---

### User Story 3 - The Reference Project Author Finds Credit (Priority: P3)

The author of the reference project (CityTreeCover) — or any contributor checking attribution — finds the repository and sees their project clearly credited: by name, with a link, and with its license preserved.

**Why this priority**: Correct attribution is a legal and ethical requirement of reuse, and the in-app notice already exists; elevating it into the README is a small, independent slice.

**Independent Test**: A reviewer opens the README and the in-app attribution, and can identify the reference project's name, URL, and license in both places without opening any other file.

**Acceptance Scenarios**:

1. **Given** the public repository, **When** a reviewer reads the README's credits section, **Then** the reference project is named, linked to its repository, and its license (MIT) is stated.
2. **Given** the live map, **When** a visitor opens the attribution panel, **Then** the reference project and the data providers are still listed (no regression).

---

### Edge Cases

- **Historical git history contains personal paths**: scrubbing applies to the current tree only; old commits are not rewritten (assumption A-4).
- **The reference project's URL changes or disappears**: the credits section still names the project and its license so attribution survives a dead link.
- **The live map is temporarily unreachable**: the README's map link is clearly labeled, and the README still explains how to view the map locally so the repository is useful on its own.
- **License mismatch**: the license named in the README and the license file must agree; if they ever diverge, the README statement is corrected to match the file.
- **Dead links**: any URL in the README (map, reference project, data providers, license) that no longer resolves is detected and corrected before publication.
- **In-app attribution drift**: the credits in the README and the in-app attribution panel must name the same reference project; a change to one without the other is a defect.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The README MUST open with a plain-language explanation of what the map is and what it shows — buildings colored by average tree cover within a 60 m radius — written for a non-technical visitor.
- **FR-002**: The README MUST explain how to use the map: how to open it, how to read the color legend, and what the tree-layer toggle does.
- **FR-003**: The README MUST include a link to the live map.
- **FR-004**: The README MUST credit the reference project by name, with a link to its repository and a statement of its license.
- **FR-005**: The README MUST credit the map data providers with their license terms.
- **FR-006**: The README MUST state the license of this project and link to the license file in the repository.
- **FR-007**: The repository MUST contain a license file whose terms match the license stated in the README.
- **FR-008**: The README MUST NOT contain developer workflow content: pipeline commands, test commands, exit codes, deployment steps, internal governance references, or vendored-library version listings.
- **FR-009**: Developer workflow content, if retained, MUST live in a separate, clearly labeled developer document linked from the README, so nothing is lost for contributors.
- **FR-010**: No tracked file in the public repository MUST contain an absolute personal file path (e.g. `/home/<username>/...`) or credential material (SSH keys, tokens, passwords, private host details).
- **FR-011**: The in-app attribution panel MUST continue to credit the reference project and all data providers (no regression).
- **FR-012**: The README MUST be written in English (matches the current README and maximizes reach on GitHub); the map's German UI language is unaffected.

### Key Entities *(include if feature involves data)*

- **Public README**: The user-facing document that introduces the project, explains how to use the map, credits sources, and states licensing. Attributes: language, target audience, linked resources.
- **License file**: The legal document in the repository that defines reuse terms. Attribute: license identifier, which must match the README's stated license.
- **Reference project (CityTreeCover)**: The MIT-licensed project this map reproduces. Attributes: name, repository URL, license — referenced by both the README and the in-app attribution.
- **Map data sources (LGL, basemap.de)**: The providers of building, boundary, and base-map data, used under `dl-de/by-2-0`. Attributes: name, license, attribution text.
- **In-app attribution panel**: The visitor-facing credits inside the map itself; must stay consistent with the README's credits.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time visitor can state what the map shows and how to interpret a building's color within 2 minutes of reading the README.
- **SC-002**: A visitor can identify the reference project's name and license from the README's credits section without opening any other file.
- **SC-003**: An automated scan of all tracked files finds zero occurrences of personal absolute paths, usernames in paths, or credential material.
- **SC-004**: The README's first half contains no commands, exit codes, build steps, or deployment steps.
- **SC-005**: A license file exists in the repository and its license identifier matches the one named in the README.
- **SC-006**: 100% of URLs in the README resolve to the intended destination at publication time.
- **SC-007**: The in-app attribution panel still lists the reference project and every required data provider (no regression from the current state).

## Assumptions

- **A-1**: The repository will be made public on GitHub at its existing remote; no repository migration, renaming, or hosting change is in scope.
- **A-2**: The live map remains publicly hosted at its current URL and will be linked from the README.
- **A-3**: All developer workflow content currently in the README (pipeline, tests, deployment, governance) is retained somewhere in the repository, just moved out of the user-facing README.
- **A-4**: Historical git history is not rewritten; the personal-path scrub (FR-010) applies to the current tree only.
- **A-5**: The process documentation under `specs/` remains part of the repository; where it contains personal paths, it is handled consistently with FR-010 (scrubbed or excluded) at the discretion of the implementation plan.
- **A-6**: The license of this project remains MIT, consistent with the current README statement and the reference project's license.
- **A-7**: No new user-facing functionality of the map itself is in scope; this feature changes documentation, licensing, and repository hygiene only.
