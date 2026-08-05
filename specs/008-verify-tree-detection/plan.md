# Implementation Plan: Verify Tree Detection Quality

**Branch**: `008-verify-tree-detection` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-verify-tree-detection/spec.md`

## Summary

Produce verifiable evidence of how well the reused Erlangen-trained tree-detection model recognizes trees on Mannheim DOP20 imagery — the basis of every building value on the published map. The chosen form (Q1, resolved in spec): a **structured visual inspection**, not numeric metrics. The owner inspects a documented, reproducible sample of imagery patches with the production canopy mask overlaid, rates each patch against fixed criteria, and gets a per-district findings report in the repository. The published map and site stay untouched (Q2); nothing gates or remediates based on findings (Q3).

Mechanics: three new pipeline subcommands (`verify-sample`, `verify-render`, `verify-report`) in the existing offline Python CLI (`src/pipeline/`, click, RSS-gated wrapper, event log). `verify-sample` stratifies ~100 patch centers across Mannheim's 17 official Stadtteile (proportional to building count, floor 2) and across three building-value bands, using a fixed seed; the sample is reproducible. `verify-render` crops 1024-px review windows (204.8 m at 20 cm GSD) from the accepted DOP20 tiles and composites the production canopy mask overlay into PNGs under `verification/patches/` (gitignored — OR-005). The owner reviews the PNGs and records ratings in `verification/ratings.jsonl` against documented criteria (correct / over-detection / under-detection). `verify-report` generates `verification/report.md`: overall rating summary, per-district table with the flagging rule (<50% of a district's patches rated correct → flagged), district-value trust assessment, the comparison with the model author's Erlangen→Bamberg warning (from the owner-written `verification/notes.md`), and the mandatory disclosure list (degenerate patches, small samples, boundary areas, single-inspector uncertainty, re-inspection divergence).

District boundaries are the only external input: the official GDI-MA Stadtteile layer (dl-de/by-2-0, same license family as the LGL data already credited), committed as a small GeoJSON in `verification/stadtteile.geojson` with attribution.

Zero map/site changes: existing pytest suites must stay green, and no published artifact (dist-assets, workspace outputs) is touched by any verify subcommand.

## Technical Context

**Language/Version**: Python ≥ 3.11 (pipeline, matches `pyproject.toml`); no frontend change.

**Primary Dependencies**: None new. Existing: rasterio (windowed tile reads), numpy (overlay compositing), shapely (stratum geometry), pyproj (EPSG:25832 handling), click (subcommands). The district boundary GeoJSON is fetched once at implementation time from the GDI-MA open-data services; it is not a runtime dependency.

**Storage**: Files in the repo under `verification/`: `stadtteile.geojson` (committed, small), `sample.jsonl`, `ratings.jsonl`, `notes.md`, `report.md` (committed). Review PNGs under `verification/patches/` are gitignored (OR-005: no >50 MiB files tracked; 100 PNGs would bloat the repo). Workspace (`data/archive/workspace`, read-only archive) is only read: `mosaic/extract/` tiles, `mosaic/canopy_prediction_mask.tif` + `.json`, `tables/buildings.geojson` (values), `boundary.geojson`.

**Testing**: pytest additions in `tests/pipeline/test_verify.py`: sample reproducibility (same seed → identical sample), stratum coverage (all 38 districts, band counts), ratings schema validation, report generation from a fixture ratings file. Existing acceptance/pipeline suites untouched and must remain green (SC-006). Manual procedure documented in `quickstart.md`; the visual inspection itself is the owner's manual step (not automated).

**Target Platform**: Linux x86_64, Python 3.11 (pipeline; same as DEVELOPMENT.md prerequisites).

**Project Type**: Offline data pipeline (CLI) — verification tooling; plus a human-in-the-loop inspection workflow.

**Performance Goals**: Verify subcommands run CPU-only and comfortably under the OR-001 RSS gate (12 GiB): windowed rasterio reads never load a full 10k×10k-px tile (≈300 MB/band); per-patch crop + composite is seconds of CPU. Sample generation and report generation are sub-second. Total render run: ~100 patches × a few seconds ≈ minutes.

**Constraints**:
- OR-001: peak RSS ≤ 12 GiB (wrapper aborts at exit code 3) — windowed reads keep it orders of magnitude below.
- OR-003: no local GPU path; verification must NOT run the model (it reviews the existing mask). No RunPod involvement.
- OR-005: no `*.tif`, `*.pmtiles`, or >50 MiB files tracked; `verification/patches/` gitignored.
- FR-010 (repo governance): `make check-public` must stay clean — report and notes are public-safe (no personal paths, credentials, or internal tooling references).
- FR-005/FR-010 (feature): no change to map data, values, tree layer, legend, site pages, or controls; verify subcommands are read-only over the workspace and repo.
- FR-004: reproducible sample — fixed seed, documented selection rule, deterministic algorithm.
- The archived workspace is read-only; all verification outputs live in the repo, not the workspace.
- District data license: dl-de/by-2-0 (matches existing LGL credits); attribution recorded in `verification/README.md` and the report.

**Scale/Scope**: 38 Stadtteile; ~93k buildings (EPSG:25832, `value` property in `tables/buildings.geojson`); 303 accepted DOP20 tiles (`tiles.csv`), ~227 tiles present in `mosaic/extract/`; 1 binary canopy mask (EPSG:25832, 0.2 m GSD); ~100 sample patches; 3 rating categories; 1 report.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No `constitution.md` exists in `.specify/memory/` (only a template) — no constitution-derived gates. The gates applied are the repository's documented governance rules (DEVELOPMENT.md) and the feature spec:

| Gate | Requirement | Status (design) |
|------|-------------|-----------------|
| OR-001 | Peak RSS ≤ 12 GiB on every pipeline invocation | PASS — windowed rasterio reads; no full-tile loads |
| OR-003 | No local GPU path; model inference only via owner-supplied RunPod | PASS — verification reviews the existing mask, runs no inference |
| OR-005 | No `*.tif`/`*.pmtiles`/>50 MiB files tracked in git | PASS — PNGs gitignored; committed files are small JSON/MD/GeoJSON |
| FR-010 | `make check-public` clean (no personal paths/credentials) | PASS — new artifacts are public-safe by construction; verified in acceptance |
| SC-006 | Zero changes to published map/site; existing suites green | PASS — verify subcommands read-only; regression gate = existing pytest + git diff |
| FR-004 | Reproducible sample (seed + documented rule) | PASS — fixed seed, deterministic allocation algorithm (contract) |
| Spec Q3 | No gating/remediation in this feature | PASS — report records findings + recommendations only |

## Project Structure

### Documentation (this feature)

```text
specs/008-verify-tree-detection/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── verify-sample.md
│   ├── verify-ratings.md
│   └── verify-report.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/pipeline/
├── cli.py               # + verify-sample, verify-render, verify-report (wrapped, gated)
├── verify.py            # NEW: sample selection, patch rendering, report generation
└── … (existing modules unchanged)

verification/            # NEW, committed (mirrors the validation/ convention)
├── README.md            # what this is + district data attribution
├── stadtteile.geojson   # official Mannheim Stadtteil boundaries (GDI-MA, dl-de/by-2-0)
├── sample.jsonl         # reproducible patch sample (generated)
├── ratings.jsonl        # owner ratings (generated empty, filled by inspection)
├── notes.md             # owner qualitative writeup: comparison + limitations (template)
├── report.md            # generated findings report (generated)
└── patches/             # review PNGs — GITIGNORED (OR-005)

tests/pipeline/
└── test_verify.py       # NEW: reproducibility, coverage, schema, report (pytest)

.gitignore               # + verification/patches/
```

**Structure Decision**: single Python package (`src/pipeline/`), following the existing module layout — one new module `verify.py` plus three subcommand registrations in `cli.py`, exactly like the existing `accept`/`values`/`trees`/`publish`/`runpod_infer` pattern. No new package, no frontend files, no new top-level tooling. Verification artifacts live in a dedicated `verification/` directory at repo root, mirroring the existing `validation/` events directory.

## Complexity Tracking

No constitution violations to justify. The design adds one module and three subcommands to the existing single-package CLI; no new abstractions, no new services, no storage layer beyond flat files.
