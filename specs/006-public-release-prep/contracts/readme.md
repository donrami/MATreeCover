# Contract: Public README

Target file: `README.md` (repo root). Requirement sources: FR-001..006, FR-008, FR-009, FR-012; SC-001, SC-002, SC-004, SC-006.

## Purpose

The README is the repository's front door for **visitors**, not developers: people who found the map or the repository and want to know what this project is, how to use the map, where the data comes from, and who made it. It must be readable in full by a non-technical person in under 3 minutes.

## Language

English (FR-012, user decision). The map UI itself stays German; the README may note that in one sentence. No jargon, no acronyms without a plain-language gloss, no internal project terminology (OR-00x, FR-xxx, acceptance suites).

## Required structure (in order)

1. **Title + one-line pitch** — project name and one sentence: a web map of Mannheim where every building is colored by the average tree cover within 60 m of it.
2. **Live map** — a prominent link to `https://abu-hamad.de/map/` (canonical URL, trailing slash), labeled e.g. "Open the live map" (FR-003, user requirement). Optional: a screenshot of the map captured from the live deployment.
3. **What this map shows** — plain-language description: dark-themed map, buildings colored by tree-cover percentage, city boundary.
4. **How to read the map / use it** — the color legend, clicking a building to see its value, the tree-layer toggle (FR-002).
5. **Where the data comes from** — one short paragraph: aerial imagery and building data processed into a canopy mask; methodology note (per-building mean tree cover within a 60 m radius). Credit lines per `contracts/license.md` (FR-005).
6. **Credits** — the reference project section per `contracts/license.md` (FR-004).
7. **License** — states MIT and links `./LICENSE` (FR-006). One sentence, no legal prose.
8. **For developers** — one line linking `DEVELOPMENT.md` (FR-009).

## Forbidden content (hard rules)

- Any command, shell prompt, code block, exit code, port number, or path (FR-008, SC-004).
- Any reference to internal workflow tooling: `speckit`, `.specify`, `.spec-workflow`, `omp` (hygiene contract).
- Any personal absolute path or credential material (FR-010).
- Any statement about the license that contradicts `LICENSE` (FR-007).
- Any URL other than the ones listed in the required structure, unless added deliberately and verified (SC-006).

## Link registry (must resolve at publication, SC-006)

| Link | Purpose |
|------|---------|
| `https://abu-hamad.de/map/` | live map (FR-003) |
| `https://github.com/jcscaptures/CityTreeCover` | reference project (FR-004) |
| `https://www.govdata.de/dl-de/by-2-0` | data license text (FR-005) |
| `https://www.bkg.bund.de` | basemap.de source note target (FR-005) |
| `./LICENSE` | project license (FR-006) |
| `DEVELOPMENT.md` | developer document (FR-009) |

## Verification

- `grep -F "https://abu-hamad.de/map/" README.md` matches (FR-003).
- The first half of the file contains no fenced code block and no line beginning with `$ `, `make `, `python -m`, `bash `, or `npx ` (SC-004).
- Every URL in the link registry returns HTTP 200/OK (SC-006).
- README's license statement matches `LICENSE` (SC-005).
