# US6 Frontend Smoke Checklist — Heatwave Map Insights

**Goal**: Verify feature 011 end to end in the browser: clickable
Stadtteile with derived statistics, the city overview panel, and the
district context in the building popup. The default view must render
exactly as published (no Hitzebelastung view, no class legend), the
existing controls keep working, and the feature adds zero network
requests.

**Maps**: FR-006..FR-014, SC-002..SC-009 (spec
011-heatwave-map-insights, user stories 2-4). The Hitzebelastung view
(US1, SC-001) was removed from scope on 2026-08-06 (clarification
Option B).

**Setup**: Run `make publish` (after `make values`, `make
pmtiles-buildings`, `make accept`). Serve `dist/` with a Range-capable
static server (nginx or equivalent; `python -m http.server` has no
Range support). Open the served URL in a clean browser with WebGL 2
and the `matreecover.story-dismissed` key set (or dismiss the story
modal once) so the modal does not block the map.

## Checks

### Scenario 1 — Default view unchanged, no heat view (SC-004, FR-012)

- [ ] Default view renders exactly as published: the legend shows the
      gradient bar with ticks 0/15/30/50/100, buildings use the
      published palette, and no district outlines are visible.
- [ ] No "Hitzebelastung" button exists anywhere in the tools card
      (revert regression); the legend shows no class legend block.
- [ ] The Bäume toggle and the Helligkeit slider behave exactly as
      before (smoke_us3.md and smoke_us1.md still pass).

### Scenario 2 — District popup (FR-006, FR-007, SC-002)

- [ ] Clicking inside a Stadtteil (no building under the cursor) opens
      the district popup with: Stadtteil name, "Gebäude" (building
      count, thin space thousands separator, e.g. "3 383"),
      "Baumanteil im Durchschnitt" (mean, dot decimal, e.g. "9.6 %"),
      and "Anteil unter 30 %" (share, e.g. "98.2 %").
- [ ] The popup values match an independent recomputation for 5
      sampled districts; Innenstadt mean is ≈ 9.6 % and Niederfeld
      mean is ≈ 34.5 %, with Innenstadt's share below 30 % higher
      than Niederfeld's (expected direction).
- [ ] A district with `mean_value` null (none in the current data;
      defensive check via a patched property) shows "keine Daten"
      instead of a fabricated number.

### Scenario 3 — Click arbitration (FR-007, FR-009)

- [ ] Building click opens the building popup; any open district popup
      closes.
- [ ] District click (no building) opens the district popup; any open
      building popup closes.
- [ ] Click on empty space closes both popups.
- [ ] No click sequence produces two open popups; a click on a
      district boundary opens exactly one popup.

### Scenario 4 — City overview panel (FR-008, FR-010, SC-003)

- [ ] After the map loads, the `#city-panel` card shows "Mannheim im
      Überblick" with the three values from
      `map.getStyle().metadata.city_stats`: "22.2 %", "24.1 %", and
      "153 524" (thin space separator), the tree count labeled
      "Anzahl der erkannten Baumflächen" (detected tree areas, not
      individual trees).
- [ ] The panel values match the district popup story
      (100 − weighted `share_lt30` ≈ `share_gte30_pct`, within 0.1 pp).
- [ ] With a stale bundle (metadata.city_stats missing) the panel hides
      itself instead of showing placeholders.

### Scenario 5 — Building popup district context (FR-009)

- [ ] Clicking buildings in 3 different districts shows the district
      line: "Stadtteil" with the district name and "Durchschnitt im
      Stadtteil" with the district mean, matching the district popup's
      mean for the same district (same property, same formatting).
- [ ] A building outside all districts (none in the current data;
      tested by removing the stadtteile source or querying a point
      outside the city) shows no district lines and the popup stays as
      today.
- [ ] A building without a value (`has_value` false) keeps the existing
      en-dash placeholder; the district lines still appear when the
      building lies inside a district.

### Scenario 6 — Keyboard and screen reader (FR-013)

- [ ] Building and district popups are reachable by keyboard and their
      close buttons are operable; the popup content has sufficient
      contrast on the dark background.

### Scenario 7 — No network and no storage (FR-010, SC-007)

- [ ] The DevTools network panel shows only the 11 known requests
      (vendor libs, style.css, main.js, style.json, boundary.geojson,
      stadtteile.geojson, basemap tiles, buildings.pmtiles range
      requests, trees.pmtiles only on toggle, attribution.html only on
      click); district clicks and the city panel add zero requests.
- [ ] No new localStorage keys beyond
      `matreecover.story-dismissed`.

### Scenario 8 — Overlap matrix (FR-013, 004 technique)

- [ ] With the city panel rendered, the overlap-matrix script returns
      no pairs at widths 320, 480, 768, 1280, 1920 px:
      ```js
      const ids = ['legend', 'controls', 'city-panel'];
      const nav = document.querySelector('.maplibregl-ctrl-top-right');
      const rects = [...ids.map(id => document.getElementById(id)), nav]
        .filter(Boolean)
        .map(el => { const r = el.getBoundingClientRect();
          return { id: el.id || 'nav', l: r.left, t: r.top, r: r.right, b: r.bottom }; });
      const overlap = (a, b) => a.l < b.r && a.r > b.l && a.t < b.b && a.b > b.t;
      const pairs = [];
      for (let i = 0; i < rects.length; i++)
        for (let j = i + 1; j < rects.length; j++)
          if (overlap(rects[i], rects[j])) pairs.push([rects[i].id, rects[j].id]);
      pairs; // must be []
      ```
- [ ] At 320 px the city panel and the district popup fit the viewport
      with no horizontal overflow.

### Scenario 9 — No regression (SC-008)

- [ ] The existing smoke checklists us1..us5 pass unchanged (map +
      popup, tree toggle, brightness, overlap matrix, story modal).

## Result

- [ ] All applicable checks pass.

Completed runs are logged to `validation/event.log.jsonl` as smoke-us6
rows (project convention).
