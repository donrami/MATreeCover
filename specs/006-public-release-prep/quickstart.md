# Quickstart: Public Release Preparation — Validation Guide

Proves the feature works end to end: README is user-focused, license and credits are correct, and no personal data remains in tracked files. Run from the repository root. All checks map to the spec's success criteria (SC-001..007).

## Prerequisites

- A git checkout of the repository on branch `006-public-release-prep` (or `main`, after merge).
- `bash` and `git`. No network access is required for checks 1–2, 4–5, 8; checks 3, 6–7 need network.

## Scenario 1 — Hygiene gate passes (SC-003, FR-010)

```text
make check-public
```

Expected: exit `0`, output `clean: N tracked files scanned`.

If it fails: each `file:line: match` line names a forbidden pattern (contracts/public-hygiene.md). Fix the file, re-run. A clean run is the precondition for every other scenario.

## Scenario 2 — License exists and matches the README (SC-005, FR-007)

```text
test -f LICENSE && grep -q "MIT License" LICENSE && echo LICENSE-OK
grep -qi "MIT" README.md && echo README-LICENSE-OK
grep -c "Jakob Schultz" LICENSE
```

Expected: `LICENSE-OK`, `README-LICENSE-OK`, and at least `1` for the preserved CityTreeCover copyright (contracts/license.md §1, §5).

## Scenario 3 — Credits present in README and in-app attribution (SC-002, SC-007, FR-004/005/011)

```text
grep -F "https://github.com/jcscaptures/CityTreeCover" README.md
grep -F "CityTreeCover" src/site/attribution.html
grep -F "dl-de/by-2-0" README.md
grep -F "dl-de/by-2-0" src/site/attribution.html
grep -F "GeoBasis-DE" src/site/attribution.html
```

Expected: each command matches. A visitor can name the reference project and its license from the README alone (SC-002).

## Scenario 4 — README is user-focused (SC-001, SC-004, FR-008)

```text
grep -F "https://abu-hamad.de/map/" README.md
grep -nE '^```|^(\$ |make |python -m|bash |npx )' README.md | head
```

Expected: the live map link matches (FR-003, user requirement). The second command prints nothing — no fenced code blocks or commands anywhere in the README. Manual check: read the README top to bottom; a first-time visitor can state what the map shows and how to read a building's color within 2 minutes (SC-001).

## Scenario 5 — No dev workflow content lost (FR-009)

```text
test -f DEVELOPMENT.md && grep -q "MANNHEIM_WORKSPACE" DEVELOPMENT.md && echo DEV-DOC-OK
```

Expected: `DEV-DOC-OK`. The pipeline, deploy, test, and governance sections from the old README live in `DEVELOPMENT.md`, with the workspace documented via the `MANNHEIM_WORKSPACE` environment variable and no personal paths.

## Scenario 6 — README links resolve (SC-006)

```text
for u in https://abu-hamad.de/map/ https://github.com/jcscaptures/CityTreeCover \
         https://www.govdata.de/dl-de/by-2-0 https://www.bkg.bund.de; do
  curl -sfL -o /dev/null "$u" && echo "OK $u" || echo "FAIL $u"
done
```

Expected: `OK` for all four URLs (registry in contracts/readme.md). Any `FAIL` must be fixed before publication.

## Scenario 7 — In-app attribution renders (SC-007)

Open `https://abu-hamad.de/map/` in a browser (or serve the local `dist/` bundle), open the attribution panel, and confirm it lists: LGL with `dl-de/by-2-0`, `© GeoBasis-DE / BKG ... dl-de/by-2-0`, and CityTreeCover (MIT). Matches the manual smoke-checklist style of `tests/frontend/smoke_us*.md`.

## Scenario 8 — Regression: pipeline tests still pass

```text
.venv/bin/python -m pytest tests/ -q
```

Expected: green (acceptance suite, value recalc, image sanity, RSS/GPU gates). On a machine without the mannheim workspace, workspace-dependent tests skip via the `MANNHEIM_WORKSPACE` fixture — skipping is expected, failures are not. This guards the workspace-default change in `src/pipeline/workspace.py` and `tests/conftest.py`.

## Acceptance mapping

| Quickstart step | Success criteria | Functional requirements |
|-----------------|------------------|-------------------------|
| 1 | SC-003 | FR-010 |
| 2 | SC-005 | FR-006, FR-007 |
| 3 | SC-002, SC-007 | FR-004, FR-005, FR-011 |
| 4 | SC-001, SC-004 | FR-001..003, FR-008, FR-012 |
| 5 | — | FR-009 |
| 6 | SC-006 | FR-003 |
| 7 | SC-007 | FR-011 |
| 8 | — | FR-010 (regression guard) |
