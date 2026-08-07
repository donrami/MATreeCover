# Quickstart: Popup Comparative Context

Validation guide for feature 013. Run these on the published bundle to prove the feature
works end to end. Implementation details live in `tasks.md` (Phase 2); contracts and data
model are referenced, not duplicated.

## Prerequisites

- Published bundle: `make publish` (produces `dist/` — `stadtteile.geojson` with 38
  district features, `style.json` with `metadata.city_stats`, `main.js`, `style.css`,
  `index.html`).
- Python 3.11+ with pytest (repo venv, `make bootstrap`).
- Node >= 20 (only for S1's JS cross-check; `which node`).
- Browser (desktop + one 360 px mobile viewport) for S2-S5.

## S1 — Automated rank/quartile cross-check (SC-003)

**What it proves**: rank and quartile shown by the district popup match an independent
computation for 100 % of the 38 districts (FR-009, FR-010, SC-003).

```sh
pytest tests/acceptance/test_rank.py -v
```

Expected: all tests pass. The suite recomputes ranks/quartiles in Python from
`dist/stadtteile.geojson`, then loads `dist/main.js` in a node VM and calls the shipped
`computeDistrictRankings` with the same features — all 38 ranks + quartiles must match
exactly. It also asserts ranks are uniquely 1..38, band bounds hold (1-10 / 11-19 /
20-28 / 29-38), and tied means order alphabetically (Friedrichsfeld before Neckarau at
21.5; Neckarstadt-Nordost before Seckenheim at 19.5).

Reference table for manual spot checks:
[contracts/rank-quartile.md](contracts/rank-quartile.md) (Lindenhof = Platz 13,
oberes Mittelfeld; Innenstadt = Platz 38, unterstes Viertel; Niederfeld = Platz 1,
oberstes Viertel).

## S2 — Building popup context (US1, SC-001, SC-004)

**What it proves**: a building click shows the value, both comparison lines with correct
deltas and assessment words, and the 30 % badge — no mental arithmetic (FR-001..FR-005).

Open the published map. Click ten buildings in different districts. For each, verify:

- Headline "Baumanteil im 60-m-Umkreis" shows the value, dot-decimal (e.g. "12.3 %"),
  matching the published color legend reading.
- District line "Durchschnitt im Stadtteil" shows the district mean plus a signed delta
  and word: "+2.7 pp · über dem Stadtteil-Durchschnitt" when above, "−2.3 pp · unter dem
  Stadtteil-Durchschnitt" when below, "±0.0 pp · auf Stadtteil-Niveau" when |delta| ≤ 0.1.
  Cross-check the delta by hand: `value − district mean` (means in the S1 reference
  table). The word must match the sign.
- City line "Stadtdurchschnitt" shows `22.2 %` (published city average) with its own
  signed delta and word, same rule.
- Badge reads "erreicht" (green) when value ≥ 30, "verfehlt" otherwise; both always carry
  the text label.
- The footnote "Was bedeutet das?" explains the 60-m metric and the 30 % threshold
  (FR-012).

Cross-check deltas for a neutral example: a building at exactly the district mean shows
"auf …-Niveau" with "±0.0 pp".

## S3 — District popup standing (US2, SC-002)

**What it proves**: a district click shows where the district stands — mean, city
comparison, rank, quartile (FR-007..FR-010).

Click ten districts. For each, verify against the reference table:

- Header "Stadtteil" name, headline "Baumanteil im Durchschnitt" mean (e.g. Lindenhof
  "26.2 %").
- Rank line "Platz X von 38" matches the table (rank 1 = highest mean, Niederfeld).
- Quartile badge matches the rank band and carries the text label ("oberstes Viertel",
  "oberes Mittelfeld", "unteres Mittelfeld", "unterstes Viertel").
- City line "Stadtdurchschnitt" shows 22.2 % with signed delta and word (e.g. Lindenhof
  "+4.0 pp · über dem Stadtdurchschnitt"; Innenstadt "−12.6 pp · unter dem
  Stadtdurchschnitt").
- Existing "Gebäude" and "Anteil unter 30 %" lines still present (FR-007).
- Footnote explains the district mean metric.

## S4 — Footnote, hierarchy, mobile fit (US3, SC-006, SC-007)

**What it proves**: numbers cannot be misread; content fits without clipping (FR-012,
FR-013, FR-016).

- Both popup types: verify the visual order name header → headline → badge → context →
  footnote on desktop.
- 360 px viewport (devtools device mode): open both popup types for three representative
  buildings/districts each (one top-quartile, one middle, one bottom). Verify every line
  is visible or reachable by scrolling inside the popup; no line clipped; popup stays
  within the viewport (FR-016).
- Comprehension spot check (SC-007): five people read the building-popup footnote and
  restate what "60-m-Umkreis" measures; at least four must answer correctly.

## S5 — No regression (FR-015, SC-005) + perf

**What it proves**: features 002/011 interaction model intact; performance budget holds.

- Arbitration: perform 20 mixed clicks (building, district, empty space). At most one
  popup is open at any time; last click wins; building click replaces building popup;
  district click replaces district popup; empty-space click closes; close button and
  German close tooltip work.
- Hover cursor on buildings still appears; building without value shows the en dash
  marker, never "0.00 %", with district lines still shown.
- Static contract: `pytest tests/acceptance/test_style.py` still green (style.json
  palette/layers untouched; popup CSS classes asserted).
- Full suite: `make accept` green.
- Perf: re-measure interaction latency per the existing process
  (`validation/perf-budget.json`; interaction budget 2 s). Expected: no regression —
  rank is computed once at load (O(n log n), n = 38); popup render adds O(1) lookups.

## Deliverables checklist

- [ ] S1 passes (SC-003)
- [ ] S2 passes for 10 buildings (SC-001, SC-004)
- [ ] S3 passes for 10 districts (SC-002)
- [ ] S4 passes at 360 px + comprehension check (SC-006, SC-007)
- [ ] S5 passes (SC-005, no perf regression)
