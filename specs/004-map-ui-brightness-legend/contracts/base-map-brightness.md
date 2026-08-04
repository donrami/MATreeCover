# Contract: Base Map Brightness (User-Adjustable)

**Feature**: Map UI, Brightness Slider & Gradient Legend |
**Branch**: `004-map-ui-brightness-legend`
**Source of truth**: `src/site/style.json` (static default) +
`src/site/main.js` (runtime updates); copied to `dist/` verbatim by
`publish.py` (patches only camera metadata and quarantine).

## Purpose

The grayscale basemap raster keeps its 003-darkened default, while
its brightness becomes a user-adjustable, session-scoped value
controlled by a permanently visible slider. This contract fixes the
layer's stable properties so the slider cannot silently become a
style swap, a hue shift, a persistence mechanism, or a data change.

## Brightness contract

| Property | Required value |
|---|---|
| `layer.id` / `type` | `"basemap"` / `"raster"` |
| `source` | `"basemap"` (tile set `de_basemapde_web_raster_grau`, same URLs) |
| `paint.raster-brightness-min` | `0` (fixed) |
| `paint.raster-brightness-max` (static) | `0.65` in `style.json` |
| `paint.raster-brightness-max` (runtime) | `[0.05, 1.0]`, default `0.65`, set via `setPaintProperty` |
| runtime default | slider value `65` (identity-mapped: `v / 100`) |
| persistence | none — page memory only, reset to default on reload |
| `layout.visibility` | `"visible"` |

Supersedes: 003's `base-map-style.md` fixed the static value in
`[0.6, 0.7]` as a constant. That window still holds for the static
default (0.65); the runtime range is now user-controlled and wider.
All other 003 invariants remain in force.

## Invariants

1. **Grayscale preserved (FR-004).** The transform
   `out = max * in` (min 0) scales all RGB channels identically. The
   layer must never gain a hue filter, saturation change, or colored
   overlay at any slider position.
2. **Only the basemap is affected (FR-004).** Building colors, the
   tree layer, the outside mask, popup content, and labels-on-other-
   layers must not change with the slider. Raster labels fade with
   the basemap — intended (spec edge case).
3. **Same tiles, same network (SC-007, FR-015).** Source URLs and
   `tileSize` never change; the slider is a client-side render
   transform only, with no added requests.
4. **Session-scoped (FR-007).** No persistence of the value across
   reloads; no localStorage, no URL state, no server state.
5. **Live and continuous (FR-002, FR-005).** Every slider step
   re-renders immediately; the range covers near-black (0.05) to the
   original un-darkened basemap (1.0), with no jumps or snap-back.
6. **Default = today (FR-003).** On load, before any interaction, the
   map renders exactly as the published bundle renders today.
7. **All zoom levels.** The paint value is constant across zooms;
   every zoom renders at the chosen brightness (FR-002 scope).

## Verification

- Luminance: slider minimum measures < 10% of the default's
  background luminance; slider maximum restores the original
  un-darkened luminance (SC-001; quickstart Scenario 2).
- Default appearance: pixel-identical basemap rendering at slider
  default vs. the pre-feature bundle (quickstart Scenario 1).
- No persistence: reloading the page at a non-default slider value
  returns the map to the default appearance (FR-007).
- No data change: `git diff` scope and network tab (quickstart
  Scenario 6).
