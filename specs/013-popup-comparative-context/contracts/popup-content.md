# Contract: Popup Content (Comparative Context)

Feature 013, FR-001..FR-008, FR-011..FR-017. Content contract for both popups: hierarchy,
exact German copy, delta rules, badge, footnote, degradation. Values are formatted with
the existing helpers (`formatPercent` dot-decimal, `formatInteger` thin-space thousands,
`escapeHtml`; unavailable marker = en dash `\u2013`).

## Shared hierarchy (FR-013)

Both popups render blocks in this order. Every color-coded fact also carries its text
label — no color-only encoding.

1. **Name header** — district name.
2. **Headline value** — label + prominent value + unit.
3. **Badge** — one-word status (30 % threshold / quartile band), colored + text.
4. **Context lines** — comparisons first, then existing statistics.
5. **Footnote** — "Was bedeutet das?" block with plain-German explanation (FR-012).

## Delta rule (R-3, applied to all three comparisons)

- `delta = value − reference`, computed on raw numbers (building `value_str` 2 decimals;
  district/city means 1 decimal).
- Classification (FR-003/FR-004/FR-008): `delta > +0.1` ⇒ "über"; `delta < −0.1` ⇒
  "unter"; `|delta| ≤ 0.1` ⇒ neutral "auf …-Niveau".
- Display: neutral always renders `±0.0 pp`; otherwise sign + magnitude rounded to 1
  decimal (half-up on magnitude) + ` pp`, minus sign U+2212 ("−2.3 pp"), plus sign "+".
- The displayed delta derives from the classification, so word and number never contradict.

## Building popup

Rendered by `buildingPopupHtml(props, lngLat)` (merges the current
`buildingPopupHtml` + `buildingDistrictHtml`; the click handler passes the click point).

### With valid value (`has_value === true`)

```text
Stadtteil: Lindenhof                                   ← header (FR-002)
Baumanteil im 60-m-Umkreis                             ← headline label (FR-001)
26.2 %                                                 ← headline value

[badge] verfehlt                                       ← FR-005, value < 30
                                                         erreicht when value >= 30

Durchschnitt im Stadtteil                              ← FR-003
9.6 % · +2.7 pp · über dem Stadtteil-Durchschnitt

Stadtdurchschnitt                                      ← FR-004
22.2 % · +4.0 pp · über dem Stadtdurchschnitt

Was bedeutet das?
Der Baumanteil im 60-m-Umkreis ist der Anteil der
Baumkronen an der Fläche im Umkreis von 60 m um das
Gebäude. Ab 30 % gilt die Beschattung als ausreichend. ← FR-012
```

### Without valid value (`has_value === false`, FR-006)

```text
Stadtteil: Lindenhof
Baumanteil im 60-m-Umkreis
–                        ← unavailable marker, never a fabricated value

Durchschnitt im Stadtteil
9.6 %                    ← district context still shown

Was bedeutet das?
Der Baumanteil im 60-m-Umkreis ist der Anteil der
Baumkronen an der Fläche im Umkreis von 60 m um das
Gebäude. Ab 30 % gilt die Beschattung als ausreichend.
```

No badge, no deltas, no city line when the value is missing. The district lookup
(`districtAt(lngLat)` over `querySourceFeatures('stadtteile')`) is unchanged; if no
district is found the header and district lines are omitted (existing behavior).

## District popup

Rendered by `districtPopupHtml(props)`, ranked by feature property `code`.

### With valid mean

```text
Stadtteil: Lindenhof                                  ← header (FR-007)
Baumanteil im Durchschnitt                            ← headline label
26.2 %                                                ← headline value

[badge] oberes Mittelfeld                             ← FR-010 quartile band

Platz 13 von 38                                       ← FR-009, rank 1 = highest mean

Stadtdurchschnitt                                     ← FR-008
22.2 % · +4.0 pp · über dem Stadtdurchschnitt

Gebäude                                               ← FR-007 (existing)
3 383

Anteil unter 30 %                                     ← FR-007 (existing)
98.2 %

Was bedeutet das?
Der Baumanteil im Durchschnitt ist der mittlere
Baumanteil im 60-m-Umkreis aller Gebäude in diesem
Stadtteil.                                            ← FR-012
```

### Without valid mean (FR-011)

```text
Stadtteil: Lindenhof
Baumanteil im Durchschnitt
keine Daten

Gebäude
3 383
```

Rank, quartile badge, and city comparison are hidden. (No district in the current bundle
has a null mean; this is defensive.)

## Assessment words (FR-017, exact copy)

| Comparison | über | unter | neutral |
|------------|------|-------|---------|
| Building vs district | über dem Stadtteil-Durchschnitt | unter dem Stadtteil-Durchschnitt | auf Stadtteil-Niveau |
| Building vs city | über dem Stadtdurchschnitt | unter dem Stadtdurchschnitt | auf Stadtniveau |
| District vs city | über dem Stadtdurchschnitt | unter dem Stadtdurchschnitt | auf Stadtniveau |

## Degradation (FR-006, FR-011, FR-014)

| Condition | Behavior |
|-----------|----------|
| `has_value === false` | marker on value line, no badge/deltas/city line, district lines stay |
| `mean_value == null` | "keine Daten", rank/quartile/city hidden, name + building count stay |
| `city_stats.mean_value_pct` missing | city comparison lines hidden in both popups; rank/quartile unaffected |
| rankings unavailable (fetch failed) | rank/quartile hidden |
| fewer than two valid district means | all rank/quartile content hidden |
| district lookup misses | header + district lines omitted (building popup) |

## Mobile fit (FR-016/SC-006)

Both popup content boxes: `max-height` (viewport-proportional, e.g.
`min(70vh, 420px)`) with `overflow-y: auto`, and `max-width: min(240px,
calc(100vw - 24px))`. All lines remain visible or scrollable at 360 px viewport width;
no line is clipped. MapLibre's existing anchor edge-flip keeps the popup in view.

## Unchanged (FR-015)

Popup instances, `closeOnClick: false`, close button, German close tooltip, hover cursor,
click arbitration (building > district > close), one popup open at a time. Only popup
*content and styles* change.
