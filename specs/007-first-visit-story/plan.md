# Implementation Plan: First-Visit Story Modal

**Branch**: `007-first-visit-story` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-first-visit-story/spec.md`

## Summary

On the map page (`src/site/index.html`), a first-time visitor — no
stored dismissal state — gets a short, dismissible German story modal
over the loaded map: how the map came to be (the SPIEGEL article →
the CityTreeCover reference project → this Mannheim replication), why
tree cover matters in the June/July 2026 heatwave, and the map's
central value (buildings colored by average tree cover in the 60-m
surroundings, matching the legend text already on the page).

Mechanics: static modal markup in `index.html` (no fetch — CSP
`script-src 'self'` forbids inline scripts, FR-011 forbids network
requests), layout in `style.css`, behavior in `main.js`. Show on
DOM-ready at `init()` (map renders behind; the "modal open while map
loads" edge case is explicitly allowed). Dismissal via visible close
button or Escape (FR-004); dismissal persists in `localStorage`
(key `matreecover.story-dismissed`), so the modal never reappears in
the same browser (FR-005); when storage is unavailable the modal
still shows and dismisses for the current visit via an in-memory
flag (FR-013). The dialog follows the WAI-ARIA dialog pattern:
`role="dialog"`, `aria-modal="true"`, labelled by its title, focus
moves in on open, is trapped while open, returns on close, Escape
closes (FR-008/FR-009). The modal box lives in a viewport safe zone
that is pairwise-disjoint from legend, tools card, zoom control, and
attribution at every supported width ≥320 px (FR-010, extends the
004 no-overlap contract); verification reuses the 004 overlap-matrix
technique plus a new smoke checklist `tests/frontend/smoke_us5.md`.

No map data, style, layer, popup, toggle, slider, or zoom behavior
changes (FR-014). No new network requests, no analytics (FR-011).

## Technical Context

**Language/Version**: Vanilla HTML/CSS/JS (ES2022, no build tool);
vendored MapLibre GL JS 5.7.1 + pmtiles (unchanged).

**Primary Dependencies**: None new — native `localStorage`, standard
DOM APIs (`hidden`, `focus`, `keydown`). No libraries.

**Storage**: `localStorage` (on-device), key
`matreecover.story-dismissed`, value `"1"` (presence = dismissed).
All access wrapped in `try/catch`; on failure a session-only
in-memory flag takes over (FR-013). No cookies, no server, no
analytics value stored (FR-011).

**Testing**: Manual smoke checklists (documented project convention):
new `tests/frontend/smoke_us5.md` (first-visit modal: appearance,
content, links, dismissal, persistence, storage-blocked, keyboard,
overlap matrix, no-network, attribution page). Existing pytest
suites untouched (no pipeline or data change). Quickstart scenarios
1–9 are the runnable validation guide.

**Target Platform**: Modern browser with WebGL 2 (unchanged from the
existing bundle); supported viewport widths ≥320 px.

**Project Type**: Static web map (frontend).

**Performance Goals**: No change. The modal is static DOM shipped in
`index.html`; opening/closing it adds zero network requests and no
tile re-renders. Closing removes the overlay from the DOM — no
reflow of the map container (FR-007).

**Constraints**:
- CSP `script-src 'self'` — no inline scripts; all behavior in
  `main.js` via `addEventListener`. CSP `style-src 'unsafe-inline'`
  permits inline styles (not needed).
- `STATIC_FILES` in `src/pipeline/publish.py` is
  `("index.html", "style.css", "main.js", "style.json", "attribution.html")`
  — modal markup must live in `index.html`; no new static asset.
- FR-010 no-overlap with `#legend`, `#controls`, MapLibre
  NavigationControl (top-right), `#attribution` + MapLibre
  attribution (bottom-right) at every width ≥320 px — extends the
  004 `ui-layout` contract.
- FR-012: modal on the map page only; `attribution.html` includes
  neither the markup nor `main.js`.
- FR-006: both reference links `target="_blank" rel="noopener"` —
  the map tab is never navigated away.
- Story content is static German text, grounded in the SPIEGEL
  article (2026-07-29) and the CityTreeCover README (both links
  verified resolving, HTTP 200, 2026-08-05).

**Scale/Scope**: Three files in `src/site/` edited in place
(`index.html` markup, `style.css` modal layout, `main.js` wiring) +
one new smoke checklist + optional validation record. Applies to
the map page only.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No `constitution.md` is ratified (only the template exists in
`.specify/memory/`). As in plans 004 and 006, gates are derived from
the de-facto governance (README/Makefile) and the approved feature
spec:

| Gate | Source | Status |
|------|--------|--------|
| G1 OR-004: one commit per accepted spec/plan/slice/milestone | README "Governance", Makefile `commit-spec`/`commit-plan`/`commit-slice`/`commit-milestone` | PASS — this plan is committed via `make commit-plan`; implementation lands as slices via `make commit-slice` |
| G2 OR-005: no `*.tif`, `*.pmtiles`, or >50 MiB `*.geojson` tracked | README, `scripts/check_or005.py` | PASS — no new data files; feature is pure frontend markup/CSS/JS |
| G3 FR-011 / SC-007: no network requests, no tracking | Feature spec | PASS by design — static markup in `index.html`, no `fetch`, no external resources; `localStorage` is on-device |
| G4 FR-014: no change to map data, layers, popup, controls | Feature spec | PASS by design — modal is an additive overlay; `main.js` gains one module, no MapLibre style/layer/paint changes |
| G5 FR-010 / SC-008: no overlap with existing UI at ≥320 px | Feature spec + 004 contract | PASS by design — safe-zone placement below the left column (desktop) / above the bottom strip (≤480 px); verified via the extended overlap matrix (quickstart Scenario 6) |
| G6 FR-012: modal only on the map page | Feature spec | PASS by construction — markup and wiring live only in `index.html`/`main.js`; `attribution.html` is untouched |

No gate violations; no unjustified complexity introduced.

**Post-design re-check (Phase 1)**: all gates still hold — the
design adds static markup, CSS, one self-contained `main.js` module,
and one smoke checklist; it introduces no new dependencies, no new
projects, no new data files, no network requests, and no MapLibre
style/layer/paint changes (G1–G6 unchanged). Overlap safety (G5) is
now pinned by the safe-zone geometry in `contracts/story-modal.md`
and verified by the extended overlap matrix (quickstart Scenario 6).

## Project Structure

### Documentation (this feature)

```text
specs/007-first-visit-story/
├── plan.md              # This file (plan command output)
├── research.md          # Phase 0 output (plan command)
├── data-model.md        # Phase 1 output (plan command)
├── quickstart.md        # Phase 1 output (plan command)
├── contracts/           # Phase 1 output (plan command)
│   ├── README.md
│   ├── story-modal.md   #   placement, dialog semantics, dismissal wiring (FR-004..010)
│   ├── story-content.md #   German story content contract (FR-002, FR-003, FR-006)
│   └── dismissal-state.md # localStorage contract + fallback (FR-005, FR-013)
└── tasks.md             # Phase 2 output (tasks command output)
```

### Source Code (repository root)

```text
src/
└── site/
    ├── index.html      # EDIT: story modal markup (backdrop + dialog + content)
    ├── style.css       # EDIT: modal layout, safe-zone sizing, responsive rules
    └── main.js         # EDIT: show-on-first-visit, focus trap, dismissal + persistence

tests/
└── frontend/
    ├── smoke_us1.md     # unchanged (map + popup regression surface)
    ├── smoke_us2.md     # unchanged (popup regression surface)
    ├── smoke_us3.md     # unchanged (tree toggle regression surface)
    ├── smoke_us4.md     # unchanged (overlap matrix; modal rect added at runtime by smoke_us5)
    └── smoke_us5.md     # NEW: first-visit story modal checklist (FR-001..014)

validation/
└── first-visit-story/   # optional: recorded overlap matrix + dismissal evidence
```

**Structure Decision**: The existing flat single-project static-site
layout is preserved. All changes stay inside `src/site/` because the
feature is presentation-only (spec Out of Scope: no data, no
pipeline). The modal markup is embedded in `index.html` rather than
a new asset because `publish.py` copies `STATIC_FILES` verbatim and
adding a new HTML partial would require touching the publisher. The
smoke-checklist convention is extended with one new file because the
first-visit behavior is a new verification surface not covered by
the existing four checklists.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No Constitution Check violations; this table is intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
