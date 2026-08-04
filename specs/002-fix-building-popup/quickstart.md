# Quickstart — Fix Building Popup Interaction

**Branch**: `main` | **Date**: 2026-08-04

End-to-end validation guide for the popup interaction fix. Every
scenario is a pass/fail check against the spec's user story,
acceptance scenarios, and success criteria SC-001..SC-005. The
behavior contract is `contracts/popup-interaction.md`; the entities
are in `data-model.md`.

## Prerequisites

- The published bundle from the prior feature (`dist/`, buildings
  layer + values accepted, per `artifacts.manifest.json`).
- A Range-capable static server (PMTiles requires HTTP Range;
  `python -m http.server` does not support it — use nginx or
  equivalent).
- A modern desktop browser and one touch-capable device or
  browser-device-emulation mode.
- Node available only if a scripted click driver is used; manual
  clicks are sufficient.

## Setup

```text
git checkout main
make commit-slice        # per-slice commit once the fix is implemented
```

Serve the published bundle:

```text
nginx -c /tmp/nginx-dist.conf   # root .../dist; Range enabled
```

Open the served URL in a clean browser. The popup fix is in the
served `main.js`; re-copy `src/site/main.js` into `dist/` and
refresh if the bundle predates the fix.

## Scenario 1 — Ten-building click sequence (SC-001, FR-002, FR-003)

**Maps to**: user story 1, acceptance scenarios 1–2, edge case
"repeated clicks on same point must not accumulate popups".

1. Click ten distinct buildings in a row.
2. **Pass criteria**:
   - Every click shows a popup with the clicked building's value
     (two decimal places, e.g. `12.34%`).
   - The popup content changes between clicks; each shows the value
     of the building just clicked.
   - At no moment do two popups exist. Verify by watching for
     duplicate popup DOM nodes:
     ```js
     document.querySelectorAll('.maplibregl-popup').length
     ```
     This must never read more than `1` between clicks (SC-001).
   - Repeatedly clicking the same point keeps exactly one popup,
     still showing that building's value.
   - No click in the sequence ever closes the popup (FR-003).

## Scenario 2 — Replace, don't close (FR-002, SC-002)

**Maps to**: acceptance scenario 2, edge case "rapid clicks between
two buildings".

1. Click building A. Record its value.
2. Immediately (within ~1 s) click building B.
3. **Pass criteria**:
   - The popup now shows building B's value.
   - The popup never disappeared between the two clicks (no blink
     to zero popups).
   - Within two seconds of each click, the popup shows that
     building's value (SC-002). Spot-check with a stopwatch on the
     ten-click run from Scenario 1: all ten must pass.

## Scenario 3 — Empty-space close and re-open (FR-003, FR-011, SC-003)

**Maps to**: acceptance scenarios 3 and 7, edge cases "click on
boundary mask or outside Mannheim empty space close popup" and
"clicking building after popup was closed".

1. Click a building. The popup opens.
2. Click empty map space (no building). Repeat ten times, each time
   opening a popup first.
3. **Pass criteria**:
   - All ten empty-space clicks close the popup (SC-003). Verify:
     ```js
     document.querySelectorAll('.maplibregl-popup').length === 0
     ```
   - Empty-space clicks when no popup is open do nothing (no error,
     no popup).
   - Click the boundary mask / the black area outside Mannheim:
     the popup closes there too.
   - After a close, the next building click re-opens the popup
     normally (FR-011).

## Scenario 4 — Close button and popup click-through (FR-004, edge case)

**Maps to**: acceptance scenario 4, edge case "click on popup itself
(body or close button) must not re-trigger building selection".

1. Click a building. The popup opens.
2. Click the popup's close button.
3. **Pass criteria**:
   - The popup closes (FR-004).
4. Re-open a popup over a small building, then click the popup body.
5. **Pass criteria**:
   - The popup stays open and still shows the same building's value.
   - Clicking the popup body does not re-anchor the popup and does
     not select any building underneath (research R-005).

## Scenario 5 — Regression: hover, unavailable marker, content
(FR-007, FR-008, SC-005)

**Maps to**: acceptance scenario 5, US2 smoke checklist.

1. Hover a building.
2. **Pass criteria**:
   - The cursor becomes a pointer on hover and restores on leave
     (FR-008).
3. Click a building without a valid value (present in the data).
4. **Pass criteria**:
   - The popup shows `–` and never `0.00%` (FR-007).
   - The label still reads `Baumanteil im 60-m-Umkreis`.
5. Run the extended smoke checklist:
   ```text
   # manual: tests/frontend/smoke_us2.md (extended with this feature's checks)
   ```

## Scenario 6 — Touch taps and tree-layer overlay (FR-009, FR-010)

**Maps to**: acceptance scenario 7, edge case "building very edge
viewport".

1. In device-emulation mode (or on a touch device), tap a building.
2. **Pass criteria**:
   - The popup opens exactly as for a mouse click (FR-009).
   - Tapping a second building replaces the popup content; tapping
     empty space closes it.
3. Enable the `Bäume` toggle so tree polygons cover part of a
   building, then click that building through the tree area.
4. **Pass criteria**:
   - The popup still opens with the building's value (FR-010).
5. Zoom so a building sits at the very edge of the viewport, then
   click it.
6. **Pass criteria**:
   - The popup stays fully inside the visible area (research R-004).

## What to do when a scenario fails

- The failure is a contract violation: fix the rule it maps to in
  `contracts/popup-interaction.md` terms (e.g. popup instance count,
  click classification, close paths), then re-run the scenario.
- Data-dependent failures (missing `value_str`, wrong `has_value`)
  are pipeline issues, not this feature's; report against the prior
  feature's acceptance state.
- Do not commit the fix until Scenario 1 and Scenario 3 both pass;
  they cover the two success criteria the spec calls measurable
  gates (SC-001, SC-003).
