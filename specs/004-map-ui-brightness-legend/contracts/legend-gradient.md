# Contract: Legend Gradient Bar

**Feature**: Map UI, Brightness Slider & Gradient Legend |
**Branch**: `004-map-ui-brightness-legend`
**Source of truth**: `src/site/index.html` (legend markup) +
`src/site/style.css` (gradient and tick styles); palette stops from
`src/site/style.json` (`buildings-fill` interpolate).

## Purpose

Present the building color scale as one continuous gradient bar with
value-proportional tick labels, matching the reference project's
presentation, without regressing the legend's semantics for screen
readers (FR-010..FR-013, FR-018).

## Legend contract

| Property | Required value |
|---|---|
| card title | "Baumfläche" (unchanged, FR-013) |
| description | "Durchschnittlicher Baumanteil im 60-m-Umkreis" (unchanged) |
| unit | "Prozent" (unchanged) |
| gradient | one continuous `linear-gradient`, no gaps or segment boundaries (FR-010/FR-011) |
| color stops | palette stops at value fractions: `0 → #ffd524`, `12 → #e6854a`, `24 → #a97e65`, `24.08 → #0674aa`, `32 → #1db6ff`, `40 → #39c2ff`, `48 → #56ceff`, `80 → #6ad4ff`; `#6ad4ff` held constant from 80 to 100 |
| tick labels | `0`, `15`, `30`, `50`, `100` at `left: 0%, 15%, 30%, 50%, 100%` — value-proportional (FR-012) |
| screen-reader text | `role="img"` + `aria-label` describing the scale, plus the five values available as text (visually hidden list) (FR-018) |

## Invariants

1. **Continuous, no gaps (FR-011).** The bar renders as a single
   gradient; no discrete swatch segments are visible.
2. **Palette-faithful (FR-010, spec edge case).** Every gradient
   pixel is a convex combination of adjacent frozen palette stops;
   the gradient never introduces an unintended color. The 80→100 cap
   matches the buildings layer's existing behavior.
3. **Value-proportional ticks (FR-012).** Tick positions equal the
   values they label divided by 100; label order is left-to-right
   ascending.
4. **All labels visible (SC-005).** At desktop and ≤480 px widths all
   five tick labels render without clipping or mutual overlap; the
   unit caption remains.
5. **Semantics preserved (FR-018).** Assistive technology reads the
   values and unit as text; the visual gradient does not replace the
   textual information.
6. **No new network cost (SC-007).** The gradient is CSS; no image
   asset or request is added.

## Verification

- Visual: one continuous bar; five tick labels at proportional
  positions (quickstart Scenario 5; `smoke_us1.md` extension).
- Narrow viewport: legend strip shows the gradient with all labels
  visible (quickstart Scenario 5).
- Screen reader: values `0 15 30 50 100` and unit "Prozent" are
  announced (manual check with a screen reader or DOM inspection of
  the accessible text).
