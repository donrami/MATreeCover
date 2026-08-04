# Data Model

**Branch**: `main` | **Date**: 2026-08-04
**Source**: `spec.md` § Key Entities, acceptance scenarios, edge
cases, and the existing frontend in `src/site/main.js`.

This feature touches no pipeline data. Only two entities are in
scope: the click classification over the existing `buildings-fill`
layer and the single selection popup. The `BuildingFootprint` fields
used by the popup are restated here from the prior feature's
data model (`specs/001-replicate-mannheim-tree-cover/data-model.md`,
entity E-003) because they are the popup's payload contract; they are
not re-derived.

## E-001 — SelectionPopup

The single compact popup that shows the currently selected building's
tree-cover value. Exactly one instance exists for the lifetime of the
page.

| Field | Type | Notes |
|---|---|---|
| `state` | `"open" \| "closed"` | Open iff the popup is attached to the map. |
| `building_id` | string \| `null` | `null` when closed. Never changes while open except via a building click. |
| `anchor` | `{ lng, lat }` | The click point (FR assumption: "popup anchors click point", not the building centroid). |
| `label` | `"Baumanteil im 60-m-Umkreis"` | Frozen by spec; never changes. |
| `value_str` | string | Two decimals plus `%`, or `–` (en dash) when the building has no valid value (FR-007). |
| `instance` | `maplibregl.Popup` | Created once with `closeButton: true`, `offset: 8`, `className: 'building-popup'`, `closeOnClick: false`. |

**Invariants**:
- At most one `SelectionPopup` exists at any moment, structurally
  (SC-001). There is no code path that constructs a second instance.
- `state == "open"` implies exactly one popup attached to the map.
- `state == "closed"` implies zero popups attached to the map.
- `building_id == null` iff `state == "closed"`.
- The popup never shows `0.00%` for a building without a valid
  value; it shows `–` (FR-007).
- The popup never moves on its own: its anchor changes only on a
  building click (`setLngLat`) or when it is removed.
- No hover tooltip, no address, no building id, no links (out of
  scope list).

## E-002 — MapClickEvent

A classified click on the map canvas.

| Field | Type | Notes |
|---|---|---|
| `point` | `{ x, y }` | Canvas pixel coordinates; the `queryRenderedFeatures` input. |
| `lngLat` | `{ lng, lat }` | Geographic position; the popup anchor. |
| `kind` | `"building" \| "empty"` | `building` iff `queryRenderedFeatures(point, { layers: ['buildings-fill'] })` returns at least one feature. |
| `building` | feature \| `null` | The first `buildings-fill` feature at the point; only when `kind == "building"`. |
| `value_str` | string \| `null` | `building.properties.value_str`; only when the feature has `has_value === true`. |

**Invariants**:
- The classification is deterministic: the same point and layer
  state always produce the same `kind`.
- `kind == "empty"` includes clicks on the boundary mask and on
  areas outside Mannheim (no `buildings-fill` feature there).
- Tree polygons overlapping a building do not change `kind`
  (FR-010): the layer filter names `buildings-fill`, so the building
  under the tree is found.
- Clicks on the popup DOM (body, close button) never produce a
  `MapClickEvent` — the popup is not part of the canvas input path
  (research R-005).
- Touch taps produce the same events as mouse clicks via MapLibre's
  standard tap-to-click handling (FR-009, research R-006).

## E-003 — BuildingFootprint (popup-relevant subset)

Restated from the prior feature's E-003; only the fields the popup
reads are listed. No values change in this feature.

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | string | LGL ALKIS | `feature.properties.id`; not displayed (out of scope). |
| `has_value` | bool | derived | `true` iff a valid value was computed. |
| `value_str` | string | derived | Two decimals, e.g. `"12.34"`; `null` when `has_value == false`. |

**Invariants**:
- `has_value == false` ⇒ popup shows `–`, never `0.00%` (FR-007).
- `value_str` is trusted as already-formatted; the frontend only
  appends `%` and HTML-escapes it (research R-009).

## State transitions — SelectionPopup

```
CLOSED --building click--> OPEN(building_id = clicked)
CLOSED --empty click--> CLOSED                 (no-op)
CLOSED --close button--> CLOSED                (no-op; no popup exists)
OPEN(a) --building click b--> OPEN(b)          (replace; FR-002)
OPEN(a) --building click a--> OPEN(a)          (no observable change)
OPEN(a) --empty click--> CLOSED                (FR-003)
OPEN(a) --close button--> CLOSED               (FR-004)
OPEN(a) --layer error--> OPEN(a)               (research R-008; no change)
```

**Transition rules**:
- A building click always ends in `OPEN` (FR-002, FR-003: "building
  click MUST never close popup"). There is no transition from
  `OPEN` to `CLOSED` caused by a building click.
- Rapid clicks between two buildings: the popup reflects the last
  clicked building; no intermediate state shows two popups
  (SC-001).
- After `CLOSED`, the next building click re-opens normally
  (FR-011).

## Relationships

```
MapClickEvent ── classifies ──> SelectionPopup transition
BuildingFootprint ── payload ──> SelectionPopup.value_str
```

## Validation rules summary

| Rule | Source | Where checked |
|---|---|---|
| At most one popup at any moment | SC-001 | `src/site/main.js` (single instance); quickstart Scenario 1 |
| Building click replaces, never closes | FR-002, FR-003 | `src/site/main.js`; quickstart Scenarios 1–2 |
| Empty-space click closes | FR-003 | `src/site/main.js`; quickstart Scenario 3 |
| Close button closes | FR-004 | `src/site/main.js`; quickstart Scenario 4 |
| Unavailable building shows `–`, never `0.00%` | FR-007 | `src/site/main.js`; quickstart Scenario 5 |
| Hover pointer unchanged | FR-008 | `src/site/main.js` (untouched); quickstart Scenario 5 |
| Touch taps behave like clicks | FR-009 | MapLibre tap-to-click; quickstart Scenario 6 |
| Tree layer does not block selection | FR-010 | `src/site/main.js` layer handler; quickstart Scenario 6 |
| Re-open after close works | FR-011 | `src/site/main.js`; quickstart Scenario 3 |
