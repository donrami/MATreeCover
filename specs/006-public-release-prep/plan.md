# Implementation Plan: Public Release Preparation

**Branch**: `006-public-release-prep` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-public-release-prep/spec.md`

## Summary

Prepare the repository for public release on GitHub. Rewrite `README.md` as a user-focused document (English): what the map shows, how to read it, a link to the live map at `https://abu-hamad.de/map/`, credits to the reference project (CityTreeCover, MIT) and the data providers (LGL, basemap.de, `dl-de/by-2-0`), and the project license. Add a `LICENSE` file (MIT, preserving the CityTreeCover copyright and permission notice). Move all developer workflow content into a new `DEVELOPMENT.md`. Scrub personal data from every tracked file — the absolute personal workspace defaults (6 code files), owner hosting details in `specs/005`, the Cloudflare `zone_id`, RunPod SSH defaults, and harness-internal workflow references — and enforce the result with a new scan gate (`make check-public`).

## Technical Context

**Language/Version**: Documentation in Markdown (English); hygiene gate in POSIX shell (bash). Repository runtime unchanged: Python 3.11 pipeline, static-site JS, Cloudflare Worker.

**Primary Dependencies**: None new. The scan gate uses `git grep` and standard shell utilities only.

**Storage**: N/A — no data changes; the archived mannheim workspace stays gitignored under `data/archive/`.

**Testing**: Existing pytest suite must stay green (regression risk: workspace default change in `src/pipeline/workspace.py` and `tests/conftest.py`). New validation: `scripts/check-public.sh` (FR-010/SC-003), doc assertions and link checks in `quickstart.md` (SC-001..007).

**Target Platform**: GitHub public repository (Markdown rendering; GitHub community standards: README, LICENSE, credits).

**Project Type**: Documentation and repository-hygiene feature on a static web-map project (Python pipeline + static site + Cloudflare Worker).

**Performance Goals**: N/A (documentation feature).

**Constraints**: FR-010 (no personal absolute paths or credentials in any tracked file); FR-008 (no developer workflow content in the README); FR-007 (LICENSE file matches the README's stated license); FR-003 (live map link required — user-confirmed URL `https://abu-hamad.de/map/`); OR-005 (large data files never tracked) must not regress.

**Scale/Scope**: 127 tracked files; ~30 files created or edited across the repo root, `scripts/`, `src/pipeline/`, `tests/`, `workers/map/`, and `specs/001..006`; 6 new planning artifacts in `specs/006-public-release-prep/`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No `constitution.md` is ratified (only the template exists). Gates are derived from the de-facto governance documented in the README/Makefile and the approved feature spec:

| Gate | Source | Status |
|------|--------|--------|
| G1 OR-004: one commit per accepted spec/plan/slice/milestone | README "Governance" | PASS — new artifacts are committed via `make commit-plan` (this plan) and `make commit-slice` (implementation); no change to the rule |
| G2 OR-005: no `*.tif`, `*.pmtiles`, or >50 MiB `*.geojson` tracked | README, `scripts/check_or005.py` | PASS — unchanged; hygiene gate is additive and must not weaken this check |
| G3 FR-010: no personal paths/credentials in tracked files | Feature spec | PASS by design — enforced by the new scan gate (SC-003) |
| G4 FR-007: LICENSE exists and matches README statement | Feature spec | PASS by design — LICENSE artifact in scope |
| G5 FR-008: README free of dev workflow content | Feature spec | PASS by design — dev content relocated to DEVELOPMENT.md |

No gate violations; no unjustified complexity introduced. Re-check after Phase 1: all gates still hold (scan gate design, LICENSE layout, and specs/ sanitization introduce no new violations).

## Project Structure

### Documentation (this feature)

```text
specs/006-public-release-prep/
├── plan.md              # This file (plan command output)
├── research.md          # Phase 0 output (plan command)
├── data-model.md        # Phase 1 output (plan command)
├── quickstart.md        # Phase 1 output (plan command)
├── contracts/           # Phase 1 output (plan command)
│   ├── readme.md        #   README content contract (FR-001..006, 008, 012)
│   ├── public-hygiene.md#   Scan-gate pattern contract (FR-010, SC-003)
│   └── license.md       #   License + credits contract (FR-004..007, 011)
└── tasks.md             # Phase 2 output (tasks command output)
```

### Source Code (repository root)

```text
# Repository root — files created or edited by this feature
README.md                  # REWRITE: user-focused (FR-001..006, 008, 012)
DEVELOPMENT.md             # NEW: dev workflow moved from README, sanitized (FR-009)
LICENSE                    # NEW: MIT, project + CityTreeCover notices (FR-007)
Makefile                   # EDIT: relative WORKSPACE default; bootstrap branch -> main;
                           #       new `check-public` target
scripts/check-public.sh    # NEW: hygiene scan gate (FR-010, SC-003)
scripts/check-prereqs.sh   # EDIT: relative workspace default
scripts/runpod-deploy.sh   # EDIT: relative workspace default; env-var SSH key/port
scripts/deploy-cf.sh       # EDIT: parameterize owner-infra gates (host/zone vars)
src/pipeline/workspace.py  # EDIT: repo-root-relative default workspace
tests/conftest.py          # EDIT: repo-root-relative default workspace
workers/map/wrangler.toml  # EDIT: zone_id placeholder; local override file gitignored
src/site/attribution.html  # EDIT: align basemap.de credit to official string
specs/001..005/            # EDIT: sanitize personal paths + internal-tooling refs
```

**Structure Decision**: The existing flat single-project layout is preserved. User-facing and legal documents live at the repo root (`README.md`, `DEVELOPMENT.md`, `LICENSE`); enforcement is a `make check-public` target backed by `scripts/check-public.sh`; spec-process provenance stays under `specs/` (sanitized). No new directories or projects are introduced.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. The scan gate (one small script, one make target) is the only new executable surface; it is the cheapest way to make SC-003 repeatable and CI-ready.
