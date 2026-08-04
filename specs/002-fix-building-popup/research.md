# Phase 0 Research

**Branch**: `main` | **Date**: 2026-08-04
**Inputs**: `spec.md`, `src/site/main.js`, vendored
`src/site/vendor/maplibre-gl.js` (MapLibre GL JS 5.7.1), prior feature
contracts (`specs/001-replicate-mannheim-tree-cover/contracts/`).

This feature is a frontend-only interaction fix. Every unknown is
resolved against the vendored MapLibre source that ships in the
published bundle — that bundle is the source of truth, not the
upstream library docs. No data changes, no pipeline changes.

## R-001 — Root cause of the popup defect

**Decision**: The defect is the combination of (a) creating a fresh
`maplibregl.Popup` on every building click and (b) MapLibre's default
`closeOnClick: true`, which registers a map-wide click-close listener
at `addTo()` time.

**Rationale**: Verbatim from the vendored source
(`src/site/vendor/maplibre-gl.js`, MapLibre 5.7.1):

```js
this.options.closeOnClick && this._map.on("click", this._onClose)
```

with the option default compiled as `closeOnClick:!0`. The current
`wireBuildingsInteractions()` runs `new maplibregl.Popup(...).addTo(map)`
on every click. Click 1 on building A opens popup A. Click 2 on
building B fires the `buildings-fill` layer handler, which creates
popup B and registers popup B's close listener; then popup A's
close listener and popup B's close listener both fire on the same
map click — the popup count returns to zero. This matches the spec's
defect reproduction exactly ("popup count returns zero").

**Alternatives considered**:
- *Tracking multiple popups and closing the previous one*: still
  needs an explicit close on empty space and leaves a window where
  two popups exist during dispatch (SC-001 forbids any moment with
  two popups).
- *Global `map.on('click')` guard checking `event.features`*: does
  not fix the close listener that `addTo()` already registered.

## R-002 — Popup lifecycle: single persistent instance

**Decision**: One module-level popup instance created once, with
`closeButton: true`, `offset: 8`, `className: 'building-popup'`, and
explicit `closeOnClick: false`. Building clicks call
`popup.setLngLat(event.lngLat).setHTML(...)`; if the popup is not
open, `popup.addTo(map)` re-attaches it. Empty-space clicks call
`popup.remove()`.

**Rationale**: A single instance makes "at most one popup" structural
(SC-001) instead of a runtime discipline. `closeOnClick: false`
removes the map-wide close listener entirely, so no code path can
close the popup except the two explicit ones the spec names: empty
space (FR-003) and the close button (FR-004). Re-clicking the same
building re-runs `setLngLat` + `setHTML` on the open popup — no
state change, popup stays open (acceptance scenario 6).

**Alternatives considered**:
- *Per-click instance + `previous?.remove()`*: leaves the
  mid-dispatch double-close race from R-001; SC-001 requires
  "no moment where two popups exist".
- *Popup with `trackPointer`*: popup would follow the cursor, not
  the click point; violates the spec assumption "popup anchors click
  point".

## R-003 — Empty-space close detection

**Decision**: A map-level `map.on('click')` handler queries
`map.queryRenderedFeatures(event.point, { layers: ['buildings-fill'] })`.
If the array is empty, `popup.remove()`. Building clicks therefore
never close the popup: the `buildings-fill` layer handler updates it,
and the map-level handler finds a feature at the point and does
nothing.

**Rationale**: `queryRenderedFeatures` with a `layers` filter returns
features of exactly that layer at the point, independent of z-order
and independent of which listener ran first. This is deterministic
and makes FR-002/FR-003 disjoint by construction: a point is either
on a building (update) or not (close). The boundary mask and the area
outside Mannheim have no `buildings-fill` features, so clicking them
closes the popup (spec edge case "click on boundary mask or outside
Mannheim empty space close popup").

**Alternatives considered**:
- *Closing on `map.on('click')` unless the layer handler fired*:
  depends on listener ordering between layer-filtered and
  map-level handlers; fragile.
- *Inspecting `event.features` on the map-level event*: MapLibre
  populates it only when filtered listeners exist; explicit
  `queryRenderedFeatures` does not rely on that.

## R-004 — Popup stays inside the viewport

**Decision**: Rely on MapLibre's default auto-anchor. No explicit
`anchor` option is passed.

**Rationale**: The vendored source's positioning code computes the
anchor from the popup size against the container bounds (the
`_getAnchor`-equivalent logic that picks `left`/`right`/`bottom`
and the `bottom` fallback when the popup would overflow). A building
at the viewport edge therefore gets a popup that flips inside the
visible area without any custom code (spec edge case).

**Alternatives considered**:
- *`anchor: 'bottom'` always*: pushes the popup off-screen for
  buildings at the top edge; fails the edge case.
- *Manual overflow clamp*: reinvents what the library already does.

## R-005 — Clicking the popup must not re-select a building

**Decision**: No special handling. The popup DOM is a sibling of the
canvas inside the map container; MapLibre click events originate from
the canvas. Clicks on the popup body or close button never reach the
map's click dispatch, so they cannot trigger the `buildings-fill`
handler or the empty-space handler.

**Rationale**: Verifiable in the vendored source (popup content is
managed in its own `_container` element, appended to the map
container, positioned absolutely over the canvas) and confirmed in
the quickstart Scenario 4. The close button's own `click` listener
closes the popup directly (FR-004).

**Alternatives considered**:
- *`event.stopPropagation()` inside popup HTML*: unnecessary; the
  popup is not part of the canvas event path.

## R-006 — Touch taps behave like mouse clicks

**Decision**: No custom touch code. MapLibre's canvas input handler
synthesizes `click` events from taps; the existing `buildings-fill`
click handler and the map-level close handler therefore behave
identically for mouse and touch (FR-009).

**Rationale**: Matches the spec assumption "Touch taps reuse map's
standard tap-to-click handling. No custom touch logic."

**Alternatives considered**:
- *Pointer-event handlers*: would duplicate library behavior and
  create a second code path to keep in parity.

## R-007 — Tree layer never blocks building selection

**Decision**: Keep building clicks wired to the `buildings-fill`
layer handler. MapLibre's layer-filtered click dispatch queries the
named layer at the point regardless of which layer renders on top,
so a click on a tree polygon overlapping a building still fires the
`buildings-fill` handler with that building (FR-010).

**Rationale**: This is the existing mechanism, unchanged. FR-010
("tree layer visibility MUST NOT block alter building selection") is
already satisfied structurally; the quickstart re-verifies it with
the `Bäume` toggle on.

**Alternatives considered**:
- *Raise the buildings layer above trees on click*: changes
  rendering order, out of scope.
- *Hit-testing trees first*: would break selection under trees.

## R-008 — Buildings layer failure must not change popup behavior

**Decision**: Leave `wireErrorHandling()` untouched. A `trees` or
`buildings` source error only toggles layer visibility or writes the
fallback attribution; it never touches the popup instance or its
listeners (spec edge case "buildings layer failure must not change
popup behavior renders").

**Rationale**: The popup code and the error handler are already
decoupled. The fix adds no coupling: the popup instance is created
and updated only inside `wireBuildingsInteractions()`.

**Alternatives considered**: None — the current decoupling satisfies
the edge case as-is.

## R-009 — Popup content unchanged

**Decision**: Keep the exact DOM from the current implementation:
`<div class="popup-label">Baumanteil im 60-m-Umkreis</div>` plus
`<div class="popup-value">` containing `value_str%` (two decimals)
when `has_value === true`, or the en dash `–` (`UNAVAILABLE`)
otherwise. Never `0.00%` for a building without a valid value
(FR-007).

**Rationale**: Spec assumption: "Popup content stays today: German
label 'Baumanteil im 60-m-Umkreis' value. No content changes."
`value_str` in the PMTiles data is already the two-decimal string,
and `has_value` is the `null`-value discriminator (prior feature
contracts `pmtiles-sources.md`, entity `BuildingFootprint`).

**Alternatives considered**: None — content is explicitly frozen by
the spec.

## R-010 — Verification without a test framework

**Decision**: Validate with the existing pattern: a scripted browser
run against the published bundle, executed by the maintainer, plus an
updated smoke checklist in `tests/frontend/`. The spec's success
criteria are interaction outcomes (click sequences, popup counts,
close trials), which are best measured by driving the real bundle in
a browser.

**Rationale**: The prior feature established this pattern
(`tests/frontend/smoke_us2.md`, manual + browser, "Automated browser
tests out of scope"). SC-001..SC-005 are all observable in the
browser; no unit-test framework exists for the vanilla-ESM frontend,
and adding one is out of scope ("no test framework" per the prior
plan; nothing in this spec asks for one).

**Alternatives considered**:
- *Playwright suite*: contradicts the established no-framework
  pattern and the spec's frontend-only scope.
- *Unit tests on a DOM harness*: would test a copy of the logic, not
  the shipped bundle; SC-001's "on published bundle" wording requires
  bundle-level verification.
