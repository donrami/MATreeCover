# Data Model: Public Release Preparation

This feature introduces no runtime data. The "entities" are the public documentation and hygiene artifacts the feature creates or changes, with their structural fields and validation rules derived from the feature spec (FR-001..012) and the contracts in `contracts/`.

## Entities

### 1. Public README (`README.md`)

The user-facing front door of the repository. Replaces the current dev-focused README.

| Field | Content | Validation |
|-------|---------|------------|
| title + one-liner | Project name and a one-sentence plain-language pitch | FR-001: explains what the map is; non-technical |
| what-is section | Buildings colored by average tree cover within 60 m; dark-themed map of Mannheim | FR-001 |
| live map link | `https://abu-hamad.de/map/` (canonical, trailing slash) | FR-003, user requirement; link must resolve (SC-006) |
| how-to-read section | Color legend, building selection popup, tree-layer toggle | FR-002 |
| methodology note | 60 m radius explanation in plain language | FR-001 (plain language) |
| credits section | Reference project + data sources (see entity 4) | FR-004, FR-005, SC-002 |
| license section | States MIT, links `LICENSE` | FR-006, FR-007, SC-005 |
| developer link | Link to `DEVELOPMENT.md` | FR-009 |
| map screenshot | Optional but recommended, captured from live deployment | aids SC-001 |

Forbidden content: commands, exit codes, build/deploy steps, internal workflow references, personal paths (FR-008, FR-010). Language: English (FR-012). Full content contract: `contracts/readme.md`.

### 2. License file (`LICENSE`)

Legal document at repo root.

| Field | Content | Validation |
|-------|---------|------------|
| license text | Standard MIT License text | FR-007: identifier matches README statement (SC-005) |
| project copyright | `Copyright (c) 2026 Rami Abu-Hamad` (owner-confirmed) | — |
| reference notice | CityTreeCover copyright `Copyright (c) 2026 Jakob Schultz` + MIT permission notice, preserved per MIT terms | research B; credit contract `contracts/license.md` |

### 3. Developer document (`DEVELOPMENT.md`)

Dev workflow relocated from the README, sanitized.

| Field | Content | Validation |
|-------|---------|------------|
| prerequisites | Linux x86_64, Python 3.11, tippecanoe, mannheim workspace via `MANNHEIM_WORKSPACE` (no absolute default) | FR-010 |
| setup / pipeline / deploy / tests | Sanitized content from the current README | FR-009: retained; FR-010: no personal paths |
| governance | OR-004/OR-005 summary + hygiene gate (`make check-public`) | consistent with repo governance (G1, G2) |
| link target | Referenced from README license/developer section | FR-009 |

### 4. Credits (README credits section + `src/site/attribution.html`)

| Field | Content | Validation |
|-------|---------|------------|
| reference project | CityTreeCover — name, `https://github.com/jcscaptures/CityTreeCover`, MIT | FR-004, SC-002 |
| LGL data | `Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0` (provider + license ref + dataset reference) | FR-005; research B (dl-de/by-2-0 §2 elements) |
| basemap.de | `© GeoBasis-DE / BKG (2026) dl-de/by-2-0`, linked to `bkg.bund.de` and `govdata.de/dl-de/by-2-0`; `(Daten verändert)` marker for modified data | FR-005; research B (official basemap credit) |
| in-app attribution | `src/site/attribution.html` lists CityTreeCover (MIT), LGL, basemap.de — must match README credits | FR-011, SC-007: no regression; alignment task |

### 5. Hygiene scan gate (`scripts/check-public.sh` + `make check-public`)

| Field | Content | Validation |
|-------|---------|------------|
| patterns | Forbidden regex list (personal paths, credentials, internal tooling) | `contracts/public-hygiene.md`; FR-010 |
| exit semantics | 0 = clean, 1 = findings listed | SC-003: zero findings on tracked files |
| integration | `make check-public`; runnable in CI later | G2 additive |

### 6. External entities (referenced, not owned)

- **Reference project**: CityTreeCover (`jcscaptures/CityTreeCover`), MIT, copyright Jakob Schultz 2026.
- **Data sources**: LGL (dl-de/by-2-0), basemap.de (dl-de/by-2-0 alternative license), govdata.de (license texts).

## Relationships

- README —states→ LICENSE (FR-007: statement must match file)
- README —links→ DEVELOPMENT.md (FR-009)
- README credits ⇄ attribution.html credits (must name the same reference project and providers; FR-011)
- Scan gate —guards→ every tracked file (FR-010)
- LICENSE —preserves→ reference MIT notice (research B)

## State transitions

None — static documents; the only transition is "tracked file scanned by gate → clean/findings", where findings must be resolved before the repository is made public.
