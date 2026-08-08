# Implementation Plan: Security Audit & Repo Housekeeping

**Branch**: `015-security-audit-housekeeping` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/015-security-audit-housekeeping/spec.md`

## Summary

Audit the public repository's security posture and reorganize the tracked tree so layout and documentation match reality — with zero regressions. Six workstreams:

1. **Secrets audit (FR-001/002/003)**: scan tracked files and full git history (89 commits) for credential patterns; extend `check-public.sh` from 19 patterns to ~31 via a shared pattern file (`scripts/public-patterns.txt`); new gate `scripts/check-git-history.sh` with an exemptions ledger; every finding dispositioned in the committed audit report.
2. **Deployed surface (FR-004/005/006/007)**: security headers on every Worker response (assets + R2 passthroughs, preserving 206 semantics), documented CSP contract, R2 access model review, deploy-script secret-handling review, RunPod endpoint trust model documented + high-severity fixes (bind 127.0.0.1, request-size cap).
3. **Supply chain (FR-008)**: committed provenance record for vendored MapLibre 5.7.1 / pmtiles 4.4.0; the demotiles.maplibre.org font origin declared as a runtime dependency (accepted risk, documented).
4. **Housekeeping (FR-009/010)**: move `cited.md` → `outputs/`, `notes/s2_abstracts*.json` → `outputs/`, delete boilerplate `progress.md` (owner sign-off), document every root file in DEVELOPMENT.md; new layout gate `scripts/check-layout.sh` + `scripts/layout-manifest.tsv`.
5. **Audit report (FR-012)**: `verification/security-audit-2026-08-08.md` recording scope, method, findings, severities, dispositions, accepted-risk list.
6. **Regression verification (FR-013/014)**: full pytest suite, all gates, deploy verification, perf + parity proof the live map is unchanged.

Design decisions are in [research.md](research.md). Contracts: [contracts/](contracts/). Validation: [quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Bash (gates, deploy), JavaScript (Worker, frontend), Python 3.11 (pipeline, endpoint, pytest), shell (housekeeping moves).

**Primary Dependencies**: none new. Existing: MapLibre GL JS 5.7.1 (vendored), pmtiles 4.4.0 (vendored), Cloudflare Workers + R2, pytest. Audit tooling is stdlib git + grep; no third-party scanner is introduced (patterns are self-maintained, matching the repo's no-build, no-extra-deps ethos).

**Storage**: none new. R2 bucket `matreecover-data` (3 declared keys) and the Worker assets binding are reviewed, not changed architecturally.

**Testing**: pytest (existing suites + new gate tests in `tests/acceptance/`), deploy verification gates (`deploy-cf.sh verify` gains header assertions), perf/parity harness.

**Target Platform**: Static web map (Cloudflare Worker edge + R2), offline pipeline, RunPod endpoint behind SSH tunnel.

**Project Type**: Static site with thin edge Worker + offline Python pipeline + review/audit deliverable. No new projects or packages.

**Performance Goals**: unchanged budgets — 8 interactions ≤ 2 s, desktop median ≤ 123 ms, first usable ≤ 10 s (SC-005/SC-008). New gates must not meaningfully slow the suite (history scan: 89 commits × ~31 patterns, estimated < 60 s).

**Constraints**: zero user-visible change; all existing tests/gates stay green; git history not rewritten; no `*.tif`/`*.pmtiles`/`>50 MiB` files tracked (OR-005); local-only dirs (`data/`, `dist/`, `.omp/`, …) stay gitignored; CSP must keep basemap, fonts, inline styles working.

**Scale/Scope**: 272 tracked files, 89 commits, 3 R2 keys, 1 Worker, 1 endpoint.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The repository ships no standalone constitution file; the governing rules are the documented constraints in DEVELOPMENT.md and the specs (OR-001…OR-005, FR-001, FR-010, FR-013/FR-014, SC-005/SC-008 precedent), as established by feature 014. Evaluated against this feature:

| Gate | Status | Evidence |
|------|--------|----------|
| OR-001 (pipeline peak RSS < 12 GiB) | PASS | No pipeline compute changes. New gates are grep/git operations on ~272 files / 89 commits. |
| OR-003 (no local GPU) | PASS | Endpoint changes are HTTP-layer (bind address, request-size cap); no model runs locally. |
| OR-004 (one commit per accepted spec/plan/slice) | PASS | Plan committed via `make commit-plan`; implementation in slices with own commits. |
| OR-005 (no *.tif / *.pmtiles / >50 MiB geojson tracked) | PASS | Housekeeping moves only tracked files; `data/` stays gitignored; new artifacts are docs + small scripts. |
| FR-010 (check-public clean) | PASS | Patterns move to a shared file; no new personal paths or credentials added; DEVELOPMENT.md rewords the desktop workspace mention. |
| FR-013/FR-014 (deploy gates) | PASS | Header additions must keep Range 206 + cache semantics green; `verify` gains header assertions, verified before merge. |
| SC-005 (image sanity) | PASS | No bundle/data changes; parity re-run in quickstart S8. |
| SC-008 (time budget) | PASS | Budgets unchanged; re-measured in quickstart S8. |
| FR-001 (no tracking/analytics) | PASS | No analytics or RUM added; security headers and gates only. |
| CSP | PASS | Policy unchanged in effect (meta tag stays authoritative); header mirrors it; basemap/fonts/inline styles still allowed. |

Re-check Phase 1 design: all gates still PASS. No violations; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/015-security-audit-housekeeping/
├── plan.md              # this file
├── research.md          # Phase 0: decisions + evidence
├── data-model.md        # Phase 1: entities, invariants, transitions
├── quickstart.md        # Phase 1: validation scenarios S1–S8
├── contracts/           # Phase 1: interface contracts
│   ├── README.md
│   ├── secrets-scan.md          # FR-001/002/003: patterns, history scan, exemptions
│   ├── security-headers.md      # FR-004: header set, CSP, scope, regression notes
│   ├── layout-gate.md           # FR-009/011: manifest format, gate semantics
│   ├── vendored-provenance.md   # FR-008: record format, update rule
│   └── endpoint-trust-model.md  # FR-007: exposure, validation, accepted risks
└── tasks.md             # Phase 2 output (created by the task-generation command, not this one)
```

### Source Code (repository root)

```text
scripts/
├── public-patterns.txt     # NEW single source of truth for P1–P31 secret patterns
├── check-public.sh         # refactored: sources public-patterns.txt (P1–P31)
├── check-git-history.sh    # NEW gate: full-history secret scan + exemption ledger
├── history-exemptions.tsv  # NEW committed ledger: pattern|commit|path → disposition ref
├── check-layout.sh         # NEW gate: tracked tree vs layout-manifest.tsv
├── layout-manifest.tsv     # NEW machine-checkable layout (mirror of DEVELOPMENT.md §layout)
└── deploy-cf.sh            # verify gains security-header + unknown-data-key 404 checks

workers/map/index.js        # gains applySecurityHeaders() on ALL responses (assets + R2)

src/site/index.html         # unchanged (CSP meta tag stays the policy source of truth)
src/site/vendor/
├── PROVENANCE.md           # NEW vendored-lib record (name, version, license, source, sha256)
└── maplibre-gl.js / .css / pmtiles.js   # unchanged

src/endpoint/server.py      # bind 127.0.0.1 by default (BIND_ADDR override); 413 on >1 MiB body

outputs/
├── cited.md                # MOVED from repo root (docs already describe it in outputs/)
├── s2_abstracts.json       # MOVED from notes/
├── s2_abstracts2.json      # MOVED from notes/
└── info.webp               # MOVED from root `info` (owner disposition recorded in report)

verification/
└── security-audit-2026-08-08.md   # NEW committed audit report (FR-012)

tests/acceptance/
├── test_public_hygiene.py  # NEW SC-007: synthetic pattern → gate fails naming file+pattern
├── test_secret_scan.py     # NEW: check-git-history runs clean on this repo
└── test_layout.py          # NEW: check-layout runs clean on this repo

tests/endpoint/
├── test_bind.py            # NEW: default 127.0.0.1 bind, BIND_ADDR override
└── test_request_size.py    # NEW: oversized Content-Length → 413

DEVELOPMENT.md / CHANGELOG.md / README.md / specs/006…/public-hygiene.md   # updated to match
```

**Structure Decision**: single flat project (static frontend + pipeline + worker + gates) — no new top-level directories, no new packages. New enforcement lives in `scripts/` next to the existing gates (`check-public.sh`, `check_or005.py`); the audit report joins the existing evidence home `verification/` (same pattern as `verification/report.md`); the provenance record sits next to the vendored files it describes. This matches the documented layout; the layout gate itself enforces it.

## Complexity Tracking

No constitution violations. No complexity justification needed.
