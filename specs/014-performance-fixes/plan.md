# Implementation Plan: Performance Fixes

**Branch**: `014-performance-fixes` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-performance-fixes/spec.md`

## Summary

Implement the 2026-08-08 performance audit findings on the published map (abu-hamad.de/map/). Four workstreams:

1. Repeat-visit caching: cacheable PMTiles range responses (R2 metadata) and immutable-cached hashed assets (worker header rule).
2. Main-thread load reduction: `fadeDuration: 0` and simplified low-zoom building geometry.
3. Critical path: preload of the map library, preconnect to the basemap origin, CSS inlined into the HTML, favicon added.
4. Regression safety: parity gates, full test suite, deploy verification, and re-measured budgets.

Design decisions are in [research.md](research.md). Contracts: [contracts/](contracts/). Validation: [quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.11 (publish step, parity checks), JavaScript (frontend, worker), shell (deploy).

**Primary Dependencies**: MapLibre GL JS 5.7.1 (vendored), pmtiles 4.4.0 (vendored), tippecanoe 2.80.0 (tile build), pmtiles Python lib >= 3.0 (parity checks), Cloudflare Workers (hosting), R2 (data).

**Storage**: R2 bucket for pmtiles archives and buildings.geojson. dist/ (gitignored) for the published bundle. Workspace at data/archive/workspace/ (gitignored).

**Testing**: pytest (existing suite, acceptance, image sanity), Lighthouse 13.4.1 (lab metrics), CDP perf harness (to be added as a committed script).

**Target Platform**: Static web map. Cloudflare Worker edge + R2. Desktop and mobile browsers.

**Project Type**: Static site with a thin Worker (edge proxy for R2 range passthrough) and an offline Python pipeline.

**Performance Goals**: Mobile Lighthouse score >= 85 (was 67). TBT < 1.5 s (was 6.3 s). LCP < 2.0 s (was 2.45 s). Warm-visit same-origin transfer < 100 KB (was ~900 KB).

**Constraints**: FR-001 (no tracking, no RUM). FR-011 (no interaction, content, or value changes). CSP stays as-is (style-src 'unsafe-inline' already permits inline CSS). OR-005 (no pmtiles or large geojson in git). Existing deploy gates (Range 206, redirects, cert) must stay green. No build tool in the frontend: publish.py is the single emitter.

**Scale/Scope**: One published bundle. Two R2 archives (34 MB buildings, 80 MB trees). 12,570 buildings rendered at the initial view. 56 requests / 2.3 MB mobile cold load today.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The repo ships no memory constitution file. The governing rules are the documented constraints in DEVELOPMENT.md and the specs (OR-001 to OR-005, FR-010, FR-013/FR-014, SC-005/SC-008 precedent).

| Gate | Status | Evidence |
|---|---|---|
| OR-001 (pipeline peak RSS < 12 GiB) | PASS | Rebuild is tippecanoe on a 56 MB geojson. publish.py streams inputs (OR-002). No new heavy step. |
| OR-003 (no local GPU) | PASS | Not applicable. No model runs in this feature. |
| OR-004 (one commit per accepted spec/plan/slice) | PASS | Plan committed via `make commit-plan`. Implementation proceeds in slices with their own commits. |
| OR-005 (no *.pmtiles, *.tif, > 50 MiB geojson tracked) | PASS | Rebuild writes to gitignored workspace and dist/. Nothing new tracked. |
| FR-010 (check-public clean) | PASS | No personal paths or credentials added. New files are code and docs. |
| FR-013/FR-014 (deploy gates) | PASS | Cache header change must keep the Range 206 gate green. The verify gate gains a cache-control check. |
| SC-005 (image sanity) | PASS | Re-run for the rebuilt archive. Parity gates in contracts/low-zoom-simplification.md. |
| SC-008 (time budget) | PASS | Budget unchanged (10 s first usable). Re-measured in quickstart S2/S3. |
| FR-001 (no tracking) | PASS | No RUM added. Lab measurement only. |
| CSP | PASS | Inline CSS allowed (style-src 'unsafe-inline'). Preconnect and preload targets already allow-listed. |

Re-check after Phase 1 design: all gates still PASS. No violations to justify. Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/014-performance-fixes/
├── plan.md              # This file
├── research.md          # Phase 0: decisions and evidence
├── data-model.md        # Phase 1: entities and invariants
├── quickstart.md        # Phase 1: validation scenarios S1-S7
├── contracts/           # Phase 1: interface contracts
│   ├── README.md
│   ├── cache-headers.md
│   ├── hashed-bundle.md
│   └── low-zoom-simplification.md
└── tasks.md             # Phase 2 output (created by the task-list step)
```

### Source Code (repository root)

```text
src/site/                    # frontend sources (no build tool)
├── index.html               # gains preconnect, preload, favicon link (publish injects)
├── main.js                  # gains fadeDuration: 0 in the Map constructor
├── style.css                # unchanged source, inlined at publish
├── favicon.svg              # NEW small self-hosted icon
└── vendor/                  # maplibre-gl.js/.css, pmtiles.js (unchanged)

src/pipeline/publish.py      # gains the hashing + inlining + rewrite post-process step

workers/map/index.js         # gains the per-path Cache-Control override on ASSETS responses

scripts/deploy-cf.sh         # pmtiles cache metadata in upload-data; cache-control check in verify

Makefile                     # pmtiles-buildings gains -S 10 --simplify-only-low-zooms

tests/                       # parity checks (pmtiles feature counts, properties),
                             # publish rewrite assertions, perf harness script

scripts/perf-measure.sh      # NEW committed CDP/Lighthouse harness (method of perf-budget.json)
```

**Structure Decision**: The repo is a single flat project (static frontend + pipeline + worker). No new projects or packages are introduced. The hashing logic lives in publish.py because it is the single emitter of dist/. The worker header rule lives in workers/map/index.js next to the existing ASSETS and R2 branches. This matches the existing layout.

## Complexity Tracking

No constitution violations. No complexity justification needed.
