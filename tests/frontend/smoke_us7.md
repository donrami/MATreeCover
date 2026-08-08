# US7 Frontend Smoke Checklist — Popup Comparative Context

**Goal**: Verify feature 013 end to end in the browser: the building popup
shows the value with district and city comparisons and the 30 % threshold
badge; the district popup shows the mean, rank "Platz X von 38", quartile
band, and city comparison; both popups explain the metric in the footnote,
follow the shared hierarchy, and fit (scroll) at a 360 px viewport.

**Maps**: FR-001..FR-017, SC-001..SC-007 (spec 013-popup-comparative-context,
user stories 1-3). Contracts: `contracts/popup-content.md`,
`contracts/rank-quartile.md` (reference table).

**Setup**: Run `make publish` (after `make values`, `make pmtiles-buildings`,
`make accept`). Serve `dist/` with a Range-capable static server (nginx or
equivalent; `python -m http.server` has no Range support). Open the served URL
in a clean browser with WebGL 2 and the `matreecover.story-dismissed` key set
(or dismiss the story modal once).

## Checks

### Scenario 1 — Automated rank/quartile cross-check (S1, SC-003)

- [ ] `pytest tests/acceptance/test_rank.py -v` passes: the Python reference
      and the node-VM cross-check of the shipped `computeDistrictRankings`
      agree 100 % on all 38 ranks + quartiles.

### Scenario 2 — Building popup context (US1, S2, SC-001, SC-004)

Click ten buildings in different districts. For each verify:

- [ ] Headline "Baumanteil im 60-m-Umkreis" shows the value dot-decimal
      (e.g. "12.3 %"), matching the legend color reading.
- [ ] District line "Durchschnitt im Stadtteil" shows the district mean plus a
      signed delta and word: "+2.7 pp · über dem Stadtteil-Durchschnitt" when
      above, "−2.3 pp · unter dem Stadtteil-Durchschnitt" when below,
      "±0.0 pp · auf Stadtteil-Niveau" when |delta| ≤ 0.1. Cross-check the
      delta by hand (`value − district mean`; means in the rank reference
      table); the word must match the sign.
- [ ] City line "Stadtdurchschnitt" shows 22.2 % with its own signed delta and
      word, same rule.
- [ ] Badge reads "erreicht" (cool cyan) when value ≥ 30, "verfehlt" (warm)
      otherwise; both always carry the text label.
- [ ] Footnote "Was bedeutet das?" explains the 60-m metric and the 30 %
      threshold ("Ab 30 % gilt die Beschattung als ausreichend.").
- [ ] Neutral example: a building at exactly the district mean shows
      "auf …-Niveau" with "±0.0 pp" and no color.
- [ ] A building without a value shows the en-dash marker (never "0.00 %"),
      no badge/deltas/city line, and the plain district line stays.

### Scenario 3 — District popup standing (US2, S3, SC-002)

Click ten districts. For each verify against the reference table:

- [ ] Header "Stadtteil" name, headline "Baumanteil im Durchschnitt" mean
      (e.g. Lindenhof "26.2 %").
- [ ] Rank line "Platz X von 38" matches the table (rank 1 = highest mean,
      Niederfeld; Innenstadt = 38).
- [ ] Quartile badge matches the rank band and carries the text label
      ("oberstes Viertel", "oberes Mittelfeld", "unteres Mittelfeld",
      "unterstes Viertel") with the R-12 color.
- [ ] City line "Stadtdurchschnitt" shows 22.2 % with signed delta and word
      (e.g. Lindenhof "+4.0 pp · über dem Stadtdurchschnitt"; Innenstadt
      "−12.6 pp · unter dem Stadtdurchschnitt").
- [ ] Existing "Gebäude" and "Anteil unter 30 %" lines still present.
- [ ] Footnote explains the district mean metric.

### Scenario 4 — Footnote, hierarchy, mobile fit (US3, S4, SC-006, SC-007)

- [ ] Both popup types show the visual order: name header → headline → badge
      → context lines → footnote.
- [ ] 360 px viewport (devtools device mode): open both popup types for three
      representative buildings/districts each (one top quartile, one middle,
      one bottom). Verify every line is visible or reachable by scrolling
      inside the popup; no line is clipped; the popup stays within the
      viewport (FR-016).
- [ ] Comprehension spot check (SC-007): five people read the building-popup
      footnote and restate what "60-m-Umkreis" measures; at least four answer
      correctly.

### Scenario 5 — No regression (FR-015, SC-005) + perf

- [ ] Arbitration: perform 20 mixed clicks (building, district, empty space).
      At most one popup is open at any time; last click wins; building click
      replaces building popup; district click replaces district popup;
      empty-space click closes; close button and German close tooltip work.
- [ ] Hover cursor on buildings still appears; the en-dash marker and district
      lines still work for value-less buildings.
- [ ] Static contract: `pytest tests/acceptance/test_style.py` green (style.json
      palette/layers untouched; popup CSS classes asserted).
- [ ] Full suite: `make accept` green.
- [ ] Perf: re-measure interaction latency per `validation/perf-budget.json`
      (interaction budget 2 s). Expected: no regression — rank is computed
      once at load (O(n log n), n = 38); popup render adds O(1) lookups.
- [ ] District clicks add zero network requests (stadtteile.geojson is
      browser-cached from the style source).

## Result

- [ ] All applicable checks pass.

Completed runs are logged to `validation/event.log.jsonl` as smoke-us7 rows
(project convention).

- [x] Feature-014 bundle re-verified 2026-08-08 (scripts/smoke-verify.mjs fresh-profile driver + acceptance suite; zoom, controls, popups, trees toggle, no console errors)
