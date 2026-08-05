# Quickstart: First-Visit Story Modal

**Feature**: 007-first-visit-story | **Branch**: `007-first-visit-story`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

This guide proves the feature works end to end. It is a run guide —
implementation details live in [data-model.md](data-model.md) and
[contracts/](contracts/). The repeatable checklist is
`tests/frontend/smoke_us5.md`.

## Prerequisites

- Built bundle: `make publish` (copies `src/site/` verbatim into
  `dist/` — `STATIC_FILES` in `src/pipeline/publish.py`; the modal
  markup ships inside `index.html`).
- Served over HTTP with Range support (the map reads PMTiles over
  range requests): nginx or equivalent. A plain
  `python -m http.server` is **not** Range-capable and will break
  the map.
- A browser profile with **no stored state** for the site origin
  (fresh profile, or clear site data first). WebGL 2 enabled.
- DevTools available (network panel, storage panel, device toolbar)
  for scenarios 4, 6, 7.

## Setup

1. `make publish`
2. Serve `dist/` (e.g. nginx root pointing at `dist/`).
3. Open `http://<host>/` in a fresh profile. The map loads; the
   story modal appears on top (Scenario 1).

## Scenarios

### Scenario 1 — First visit shows the modal (FR-001, SC-001)

- [ ] Fresh profile, no stored dismissal state.
- [ ] Open the map page; after the page finishes loading the story
      modal appears automatically over the map.
- [ ] The map is visible and fully rendered behind the modal
      (tiles continue loading behind the overlay — spec edge case).
- [ ] The modal is in German (`lang="de"` page, German copy).

### Scenario 2 — Story complete, links work (FR-002, FR-003, FR-006, SC-003)

- [ ] Modal contains all required elements (contract:
      [story-content.md](contracts/story-content.md)):
      map-origin narrative (SPIEGEL → CityTreeCover → Mannheim
      replication), SPIEGEL article link with the article title,
      CityTreeCover link, source-repository link ("Quellcode auf
      GitHub"), June/July 2026 heatwave context.
- [ ] The central-value sentence states that buildings are colored
      by average tree cover in the 60-m surroundings (matches the
      legend text "Durchschnittlicher Baumanteil im 60-m-Umkreis").
- [ ] Activate the SPIEGEL link: opens in a **new tab**, resolves
      to "Hitze in Europa: Wie gut Stadtbäume vor extremer Wärme
      schützen" (DER SPIEGEL).
- [ ] Activate the CityTreeCover link: opens in a **new tab**,
      resolves to `github.com/jcscaptures/CityTreeCover`.
- [ ] Activate the source-repository link: opens in a **new tab**,
      resolves to `github.com/donrami/MATreeCover`.
- [ ] Return to the map tab: the map is unchanged and fully usable.

### Scenario 3 — Dismissal and persistence (FR-004, FR-005, SC-002, SC-004)

- [ ] Dismiss via the visible close button: modal disappears with a
      single action.
- [ ] Dismiss via Escape on a fresh first visit (re-clear site data
      first): modal closes.
- [ ] Immediately after dismissal the map is fully interactive
      (pan, zoom); there is no layout shift — compare the map
      container's bounding box before/after close
      (`document.getElementById('map').getBoundingClientRect()`
      unchanged) and no reload (network panel shows no reload).
- [ ] Reload the page: modal does **not** reappear.
- [ ] Close the tab, reopen the page in the same browser: modal
      does **not** reappear (persistence across sessions — key
      `matreecover.story-dismissed` present in DevTools → Storage →
      Local Storage).
- [ ] Clear site data (DevTools → Application → Clear site data):
      modal appears again (first-visit behavior restored).

### Scenario 4 — Storage unavailable (FR-013)

- [ ] DevTools → Settings → Block storage (or an equivalent private
      mode with storage disabled).
- [ ] Fresh load: modal still appears.
- [ ] Modal is dismissible (close button and Escape both work).
- [ ] Reload: modal appears again (no persistence possible — the
      on-device state cannot be stored; contract:
      [dismissal-state.md](contracts/dismissal-state.md)).
- [ ] No console errors from the storage fallback.

### Scenario 5 — Keyboard and screen reader (FR-008, FR-009, SC-006)

- [ ] Keyboard-only: on first load, focus moves into the modal
      automatically.
- [ ] Tab cycles within the modal (close button ↔ reference links);
      focus never leaves the modal while it is open.
- [ ] Escape closes; focus returns to the page (body).
- [ ] Screen-reader spot check (NVDA/VoiceOver): the dialog is
      announced with its name ("Wie diese Karte entstanden ist");
      the story text is read as content; links are announced.

### Scenario 6 — No overlap at all supported widths (FR-010, SC-008)

- [ ] With the modal open, run the 004 overlap-matrix script with
      the modal rect added, at widths 320, 480, 768, 1280, 1920 px
      (device toolbar) × default zoom:
      ```js
      const ids = ['legend', 'controls', 'attribution'];
      const nav = document.querySelector('.maplibregl-ctrl-top-right');
      const modal = document.getElementById('story-dialog');
      const rects = [...ids.map(id => document.getElementById(id)), nav, modal]
        .filter(Boolean)
        .map(el => { const r = el.getBoundingClientRect();
          return { id: el.id || (el === modal ? 'modal' : 'nav'),
                   l: r.left, t: r.top, r: r.right, b: r.bottom }; });
      const overlap = (a, b) => a.l < b.r && a.r > b.l && a.t < b.b && a.b > b.t;
      const pairs = [];
      for (let i = 0; i < rects.length; i++)
        for (let j = i + 1; j < rects.length; j++)
          if (overlap(rects[i], rects[j])) pairs.push([rects[i].id, rects[j].id]);
      pairs; // must be []
      ```
- [ ] At 320 px: the modal fits the viewport (no horizontal
      overflow), content scrolls inside the modal, nothing is
      clipped.
- [ ] Text zoom at 200% (browser zoom or font-size setting): story
      content stays readable; the modal scrolls instead of clipping.
- [ ] Legend, tools card, zoom control, and attribution remain
      reachable around the modal at every width.

### Scenario 7 — No network, no tracking (FR-011, SC-007)

- [ ] DevTools network panel: loading the map page with the modal
      open adds **no** requests beyond the baseline (no fonts, no
      analytics, no story fetch). Contract:
      [story-modal.md](contracts/story-modal.md).
- [ ] The only storage write is `matreecover.story-dismissed` on
      dismissal (no timestamps, no counters).

### Scenario 8 — Attribution page never shows the modal (FR-012)

- [ ] Open the attribution page (`/attribution`): no modal appears,
      no story markup, no modal behavior.

### Scenario 9 — No regression (FR-007, FR-014, SC-005)

- [ ] After dismissal, run the existing smoke checklists unchanged:
      `smoke_us1.md` (map + popup), `smoke_us2.md` (popup),
      `smoke_us3.md` (tree toggle), `smoke_us4.md` (overlap
      matrix) — all green.
- [ ] Building popup, Bäume toggle, Helligkeit slider, and zoom
      behave exactly as before the feature.

## Expected outcomes

- SC-001..SC-008 all green: modal appears once per browser, in
  German, complete with working links, dismissible by close button
  and Escape, no overlap, no network traffic, no regression, fully
  keyboard- and screen-reader-operable.
- Existing pytest suite untouched and still green (no pipeline or
  data change in this feature).
