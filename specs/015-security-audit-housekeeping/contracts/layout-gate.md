# Contract: Layout Gate

Target: `scripts/check-layout.sh`, `scripts/layout-manifest.tsv`, DEVELOPMENT.md ("What is in this repository"). Requirement sources: FR-009, FR-010, FR-011; SC-003.

## Purpose

Make "the tracked tree matches the documented layout" machine-checkable and enforced, so the audited layout persists. A new contributor can find any file by reading DEVELOPMENT.md's layout section — and the gate proves the section is accurate.

## Layout manifest

`scripts/layout-manifest.tsv` is the machine-checkable form of the DEVELOPMENT.md layout section. Format: TAB-separated rows, one per top-level tracked entry.

```text
<tracked-path>\t<documentation-reference>
```

Rows:

| tracked-path | documentation-reference |
|--------------|------------------------|
| `.gitignore` | DEVELOPMENT.md "What is in this repository" (root files) |
| `CHANGELOG.md` | ditto |
| `DEVELOPMENT.md` | ditto |
| `LICENSE` | ditto |
| `Makefile` | ditto |
| `README.md` | ditto |
| `pyproject.toml` | ditto |
| `artifacts.manifest.json` | ditto (pipeline artifact manifest) |
| `tiles.csv` | ditto (DOP20 tile index) |
| `screenshot/` | ditto (README screenshot) |
| `scripts/` | ditto |
| `specs/` | ditto |
| `src/` | ditto |
| `tests/` | ditto |
| `validation/` | ditto |
| `verification/` | ditto |
| `workers/` | ditto |
| `outputs/` | ditto |

Housekeeping resolved the strays (`cited.md`, `notes/`, `info`, `progress.md`) before this manifest was frozen; their dispositions are in the audit report.

## Gate semantics (`check-layout.sh`)

- Every `git ls-files` path must start with a manifest row (top-level match).
- Every manifest row must exist in the current tracked tree (no dead documentation entries).
- No tracked file may sit at the repo root outside the documented root set.
- Exit 0: `clean: N tracked paths, M documented entries`. Exit 1: one `path → expected documentation-reference` mismatch line per failure, then a summary.
- Shell + `git` only. Never requires network access.

## Sync rule

Changing the layout section of DEVELOPMENT.md without updating the manifest fails the gate. Changing the manifest without updating the section fails the section's own accuracy check (a reviewer diff of the two). The section must name the manifest as its machine form:

> The layout manifest at `scripts/layout-manifest.tsv` is the machine-checkable form of this section; `make check-layout` enforces it.

Any file relocation is a contract change: move the file, update the manifest (and the section if the top-level entry changes), update any references, and re-run `make check-layout` plus the full test suite before commit (spec edge case: moves break Makefile targets, script paths, and imports — the suite catches them).

## Constraints inherited from other gates

- No `*.tif`, `*.pmtiles`, or `>50 MiB` geojson enters the tracked set (OR-005, `check_or005.py`). Housekeeping moves only small tracked files.
- Gitignored local dirs (`data/`, `dist/`, `dist-assets/`, `.omp/`, `.venv/`) never appear in the manifest and are never tracked.
- Layout rows must not be added for untracked files: the manifest describes tracked reality, not aspiration.
