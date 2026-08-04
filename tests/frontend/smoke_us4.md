# US4 Frontend Smoke Checklist — UI Placement / No Overlap

**Goal**: Verify no two static UI elements overlap at any supported
viewport width and zoom level, and that the Bäume toggle is fully
clickable where it previously overlapped the zoom control.

**Maps**: FR-008, FR-009, FR-016, FR-017, SC-003, SC-004 (spec
004-map-ui-brightness-legend, user story 2).

**Setup**: Run `make publish`. Serve `dist/` with a Range-capable
static server (nginx or equivalent). Open the served URL in a clean
browser with WebGL 2.

**Layout under test**: legend card + tools card (Bäume, Helligkeit
slider) stacked in the left column (`#left-stack`); MapLibre
navigation control top-right; attribution bottom-right; popup
transient.

## Checks

- [X] Tools card (Bäume + Helligkeit slider) is in the left column
      below the legend card, not in the top-right corner (FR-008).
- [X] No two static elements overlap at any matrix cell: widths 320,
      480, 768, 1280, 1920 px × zoom levels {default, default+2,
      default−2} (SC-003). Console check at each cell:
      ```js
      const ids = ['legend', 'controls', 'attribution'];
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
- [X] At every matrix cell all four elements are visually reachable:
      zoom in/out/north reset work, Bäume toggles the tree layer,
      the slider is draggable, attribution is visible (FR-008).
- [X] Bäume toggle is fully clickable, including at the former
      overlap location (top-right, below the zoom buttons): a click
      there toggles the tree layer, never another element (FR-009,
      SC-004).
- [X] Brightness slider is permanently visible (no toggle needed) at
      all viewport sizes (FR-016).
- [X] Popup is transient: opening it over another element does not
      permanently occlude any control; the close button works and
      empty-space click closes it (FR-017).
- [X] Buildings-layer failure message in the attribution slot does
      not overlap other elements (spec edge case).

Measured 2026-08-04; matrix evidence in
`validation/brightness-slider/overlap.json`.

## Result

- [X] All applicable checks pass.
