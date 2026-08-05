# Implementation Plan: Fix Building Popup Interaction

**Branch**: `main` | **Date**: 2026-08-04
**Spec**: [spec.md](./spec.md)
**Input**: Feature specification from
`specs/002-fix-building-popup/spec.md`
**Source truth**: committed spec (`spec.md`) authoritative. The
unfilled constitution template carries no
binding constraints; binding constraints are the spec's functional
requirements FR-001..FR-011 and the operational constraint "no
change published data or acceptance state allowed". Frontend source
of truth for library behavior is the vendored bundle
`src/site/vendor/maplibre-gl.js` (MapLibre GL JS 5.7.1), which ships
in the published bundle. The published `dist/` bundle from the prior
feature (`001-replicate-mannheim-tree-cover`) is the verification
target, unchanged.

## Technical Context

**Language/Version**: Vanilla ESM JavaScript, no build tool — the
existing `src/site/main.js` convention. No new dependencies;
MapLibre GL JS 5.7.1 and pmtiles are already vendored.

**Storage**: None. This feature touches no data, no artifacts, no
manifests. The operational constraint forbids changing published
data or acceptance state.

**Testing**:
- **Frontend behavior** (manual + browser, no test framework —
  matches the prior feature's `tests/frontend/smoke_us2.md`
  pattern): drive the published bundle in a browser, run the six
  quickstart scenarios, record popup-count via
  `document.querySelectorAll('.maplibregl-popup').length`.
- **No unit tests**: no test framework exists for the vanilla-ESM
  frontend; adding one is out of scope (research R-010).
- **No pipeline tests**: no pipeline code changes.

**Target Platform**: Published map in desktop and mobile browsers
(touch), German locale, ESM support — unchanged from the prior
feature. The served bundle is static; no server changes.

**Constraints**:
- No change to published data or acceptance state (operational
  constraint). Frontend behavior only.
- One commit per slice/milestone (prior feature OR-004 discipline,
  `Makefile` targets).
- Popup content frozen: German label `Baumanteil im 60-m-Umkreis`
  and the two-decimal value or `–` (spec assumptions).
- No camera, zoom, pan, palette, or layer-order changes (out of
  scope).
- No hover tooltips, no address/id/completeness/links in the popup
  (out of scope).

**Scale/Scope**: One code path — `wireBuildingsInteractions()` in
`src/site/main.js` (plus smoke checklist update
`tests/frontend/smoke_us2.md`). Everything else in the frontend is
untouched. Verification runs against the existing published bundle.

## Constitution Check

No constitution file exists in this workspace
(unfilled template, same as the prior feature). No binding
constitution constraints. Binding constraints are the spec's
functional requirements FR-001..FR-011 and the operational
constraint. This check is re-run after the design artifacts are
generated (see Post-design re-check).

## Gate Evaluation

| ID | Requirement (paraphrased) | Plan evidence |
|---|---|---|
| FR-001 | Keep compact popup showing building's tree-cover value, two decimals | Popup content contract `contracts/popup-interaction.md` § 4; content unchanged from today. |
| FR-002 | Building click opens/replaces popup with that building's value | Single instance updated via `setLngLat` + `setHTML` (research R-002); transition table in `data-model.md` E-001. |
| FR-003 | Building click never closes popup; empty-space click closes | `closeOnClick: false` + map-level `queryRenderedFeatures` close handler (research R-003); rules B2/B4 in the contract. |
| FR-007 | No-valid-value building shows unavailable marker, never zero | `has_value === false` ⇒ en dash `–` (research R-009); quickstart Scenario 5. |
| FR-008 | Hover selection pointer unchanged | `mousemove`/`mouseleave` handlers untouched (contract § 5). |
| FR-009 | Touch taps behave like mouse clicks | MapLibre standard tap-to-click, no custom touch code (research R-006); quickstart Scenario 6. |
| FR-010 | Tree layer visibility does not block building selection | Layer-filtered click dispatch queries `buildings-fill` regardless of z-order (research R-007); quickstart Scenario 6. |
| FR-011 | After close, next building click re-opens popup | `popup.addTo(map)` re-attach path (research R-002); quickstart Scenario 3. |
| OP-001 | No change to published data or acceptance state | No pipeline, data, or manifest edits in this plan; verification is browser-only against the existing bundle. |

**Gate result**: PASS. Every FR has a concrete plan element; the
operational constraint is enforced by the plan's scope (frontend
files only). No violation requires justification; `Complexity
Tracking` stays empty.

### Post-design re-check

Re-evaluated after `research.md`, `data-model.md`, `contracts/*`,
`quickstart.md` were generated:

- **FR-002 / FR-003** — `data-model.md` E-001 state transitions:
  building click always ends `OPEN`; only empty-space and close
  button end `CLOSED`. `contracts/popup-interaction.md` rules B1–B9.
- **FR-007** — `data-model.md` E-003 invariant: `has_value == false`
  ⇒ `–`, never `0.00%`; contract § 4.
- **FR-010** — research R-007 grounds the mechanism in the vendored
  source; quickstart Scenario 6 verifies it with the `Bäume` toggle
  on.
- **OP-001** — quickstart Setup serves the existing `dist/` bundle;
  no data artifact is regenerated or re-accepted.

**Gate result (design)**: PASS. No new violations. `Complexity
Tracking` stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/002-fix-building-popup/
├── spec.md                 # committed feature spec
├── checklists/requirements.md
├── plan.md                 # this file
├── research.md             # Phase 0 output
├── data-model.md           # Phase 1 output
├── quickstart.md           # Phase 1 output
└── contracts/
    ├── README.md
    └── popup-interaction.md  # Phase 1 output
```

### Source Code (repository root)

```text
src/site/
└── main.js                 # wireBuildingsInteractions(): the only
                            #   edited file in this feature
tests/frontend/
└── smoke_us2.md            # extended with this feature's checks
```

`tasks.md` is the Phase 2 output, generated by the tasks command, not
created here.

## Implementation approach (summary, detailed tasks in `tasks.md`)

1. In `wireBuildingsInteractions()`: create one module-level
   `maplibregl.Popup` with `closeButton: true`, `offset: 8`,
   `className: 'building-popup'`, `closeOnClick: false`.
2. `buildings-fill` click handler: update the single instance
   (anchor + HTML from `has_value` / `value_str`) and `addTo(map)`
   when closed.
3. Map-level `click` handler: `queryRenderedFeatures(point,
   { layers: ['buildings-fill'] })`; remove the popup when empty.
4. Keep hover handlers, tree toggle, error handling untouched.
5. Extend `tests/frontend/smoke_us2.md` with the new checks; run all
   quickstart scenarios against the published bundle.

## Complexity Tracking

No constitution violations. Table intentionally empty.
