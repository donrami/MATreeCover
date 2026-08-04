# Data Model

**Branch**: `003-darken-base-map` | **Date**: 2026-08-04
**Source**: `spec.md` § Key Entities, `src/site/style.json`
(current state), `research.md` R-001/R-005.

This feature touches no pipeline data and introduces no new data
entities. The only change is one paint property on one style layer.
The entities below document the style-document surface that the
change operates on, so the contract is explicit about what must stay
fixed.

## E-001 — BaseMapLayer

The grayscale basemap raster layer in the style document. The entity
being darkened.

| Field | Value | Notes |
|---|---|---|
| `layer.id` | `"basemap"` | Unchanged. |
| `layer.type` | `"raster"` | Unchanged. |
| `source.id` | `"basemap"` | Unchanged. Raster tile set `de_basemapde_web_raster_grau`; same URLs (SC-005, spec assumption). |
| `paint.raster-brightness-min` | `0` (default) | Unchanged. |
| `paint.raster-brightness-max` | **NEW** `0.65`, window `[0.6, 0.7]` | The only change. Multiplies every tile pixel: `out = max * in`. |
| `layout.visibility` | `"visible"` | Unchanged. |

**Invariants**:
- The raster transform is `out = brightness_min + (brightness_max - brightness_min) * in` (verified from the vendored shader, research R-001). With min 0 and max 0.65, every pixel scales by 0.65: mean luminance drops 35% (SC-001 gate: ≥30%).
- The source is grayscale in, grayscale out (FR-002): the scale is identical across RGB channels, so hue/saturation are untouched.
- The darkening applies at every zoom level (FR-008): the property is a constant, not zoom-stopped.
- The tile URLs, attribution, and tile size never change (SC-005).

## E-002 — BuildingFootprint

Unchanged by this feature (FR-003). Restated from the prior feature's
data model because it is the layer the darkening must make more
distinguishable.

| Field | Value | Notes |
|---|---|---|
| `fill-color` (has_value) | interpolated stops: `0 → #ffd524`, `12 → #e6854a`, `24 → #a97e65`, `24.08 → #0674aa`, `32 → #1db6ff`, `40 → #39c2ff`, `48 → #56ceff`, `80 → #6ad4ff` | Reference palette (yellow → blue via orange/brown/dark blue). Frozen. |
| `fill-color` (no value) | `#b8b8b8` | Unavailable marker. Lightened from `#444444` (see note). |
| `fill-opacity` | `0.75` (has_value), `0.8` (no value) | No-value branch raised from `0.4` (see note). |
| `line-color` / `line-width` | `#555555` / `0.5` | Outline layer `buildings-line`. Frozen. |

**Invariants**:
- No value-scale stop, value opacity (0.75), or outline value changes
  (FR-003). The unavailable marker is not part of the yellow-to-blue
  value scale; it was adjusted to satisfy FR-007 (see note).
- Every palette color composited over the darkened background must
  remain clearly distinguishable (SC-002, verification method in
  research R-007).
- The unavailable gray must not disappear into the darkened
  background (FR-007): `#b8b8b8` at 0.8 over the background.

**Note (2026-08-04, implementation)**: at `raster-brightness-max:
0.65` the previous marker (`#444444` at 0.4) collapsed to local
ΔE ≈ 4.6 against darkened blocks — below the just-noticeable
difference, violating FR-007. The fill is dark either way, so raising
opacity did not help; the marker was lightened to `#b8b8b8` at 0.8
(neutral gray, no chroma, distinct from every value color), which
measures local ΔE 22–30 against darkened blocks (measured on the
actual buildings via polygon-exact pixel sampling).

## E-003 — TreeLayer

Unchanged by this feature. Must remain clearly visible over the
darkened background (FR-006).

| Field | Value | Notes |
|---|---|---|
| `fill-color` | `#39C43D` | Frozen. |
| `fill-opacity` | `0.75` | Frozen. |
| `layout.visibility` | `"none"` default; toggled by `Bäume` control | Frozen. |

## Rendering Order

Layer order in the style document (bottom to top) is a contract of
this feature (research R-005):

```
basemap            (darkened)
outside-mask       (black fill outside Mannheim — unchanged, still black)
buildings-fill     (palette at 0.75 / 0.4 opacity)
buildings-line     (#555555 outlines)
trees-fill         (green, default hidden)
```

No layer is added, removed, or reordered. The darkening never
affects layers above the basemap because the raster shader processes
only the basemap source.

## State Transitions

None. The style document is static; the change is a constant paint
value with no runtime state.
