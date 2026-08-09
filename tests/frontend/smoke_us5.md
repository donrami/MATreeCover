# US5 Frontend Smoke Checklist — First-Visit Story Modal

**Goal**: Verify the first-visit story modal. It must appear
automatically once per browser, in German. It must show over the map
without scrolling and hold the full story text (feature 007 content
restored); it is the single DOM copy of the story.
It must dismiss via the close button or Escape, with no layout shift
and no reload. Dismissal persists on-device and degrades gracefully
when storage is blocked. The modal is fully keyboard- and
screen-reader-operable, never overlaps the existing UI at any
supported width, and never shows on the attribution page.

**Maps**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007,
FR-008, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, SC-001,
SC-002, SC-003, SC-004, SC-005, SC-006, SC-007, SC-008 (spec
007-first-visit-story, user stories 1–3; feature 016 Clarifications
2026-08-09).

**Setup**: Run `make publish`. Serve `dist/` with a Range-capable
static server (nginx or equivalent). Open the served URL in a clean
browser profile with no stored dismissal state and WebGL 2 enabled.

The story wording is normative in
`specs/007-first-visit-story/contracts/story-content.md` and lives
inside the first-visit story modal of `src/site/index.html` (single
DOM copy, feature 016 final Clarifications 2026-08-09). No story
text exists outside the modal.

## Checks

### Scenario 1 — First visit shows the modal (FR-001, SC-001)

- [ ] Fresh profile with no stored dismissal state: opening the map
      page shows the modal automatically over the fully rendered map
      (tiles continue loading behind the overlay).
- [ ] The page and the modal copy are in German (`lang="de"`).

### Scenario 2 — Modal over the map with the full story (feature 016, Clarifications 2026-08-09 final)

- [ ] The modal opens centered over the map and the page does not
      scroll (window.scrollY is unchanged by opening). No story
      section exists under the map; the map is the only page content.
- [ ] The modal holds the full story text (feature 007 content
      restored): the opening paragraph, the SPIEGEL story paragraph,
      the heatwave paragraph, the three links (SPIEGEL article,
      CityTreeCover, "Quellcode auf GitHub"), plus the Methode,
      Datenquellen, and Genauigkeit sections.
- [ ] The modal contains exactly one DOM copy of the story. The
      acceptance test `test_story_single_dom_copy` asserts the SPIEGEL
      sentence occurs exactly once in the raw HTML.
- [ ] All story links carry `target="_blank" rel="noopener"`
      (SPIEGEL: "Hitze in Europa: Wie gut Stadtbäume vor extremer
      Wärme schützen"; CityTreeCover: the project name; source
      repository: "Quellcode auf GitHub"; attribution:
      "Details unter Datenquellen").
- [ ] Activating the SPIEGEL link opens a new tab resolving the
      article (HTTP 200); activating the CityTreeCover link opens a
      new tab resolving `github.com/jcscaptures/CityTreeCover`;
      activating the source-repository link opens a new tab resolving
      `github.com/donrami/MATreeCover`; activating the
      "Details unter Datenquellen" link opens a new tab resolving
      `https://abu-hamad.de/map/attribution` (HTTP 200).
- [ ] Returning to the map tab shows the map unchanged and fully
      usable.

### Scenario 3 — Dismissal and persistence (FR-004, FR-005, SC-002, SC-004)

- [ ] Dismissing via the visible close button removes the modal in a
      single action and leaves the scroll position unchanged (the
      modal never scrolled the page). Dismissing via Escape on a
      fresh visit works the same way.
- [ ] Immediately after dismissal the map is fully interactive and
      there is no layout shift: the map container
      `getBoundingClientRect()` is unchanged before/after close and
      the network panel shows no reload.
- [ ] Reloading the page does not show the modal again.
- [ ] Closing the tab and reopening the page in the same browser does
      not show the modal again (key `matreecover.story-dismissed`
      present in DevTools → Storage → Local Storage, value `"1"`).
- [ ] Clearing site data (DevTools → Application → Clear site data)
      restores first-visit behavior: the modal appears again.

### Scenario 4 — Storage unavailable (FR-013)

- [ ] With storage blocked, the modal still appears on a fresh load.
- [ ] The modal is dismissible (close button and Escape both work).
      Reloading shows the modal again, because the in-memory fallback
      is session-only.
- [ ] No console errors from the storage fallback.

### Scenario 5 — Keyboard and screen reader (FR-008, FR-009, SC-006)

- [ ] On first load, focus moves into the modal automatically; a
      screen reader announces the dialog name "Wie diese Karte
      entstanden ist" from `aria-labelledby`.
- [ ] Tab cycles within the modal (the close button and the
      attribution link); focus never leaves the modal while it is
      open.
- [ ] Escape closes the modal and focus returns to the page (body).
- [ ] The story text is real text content (paragraphs and links),
      never `aria-hidden` or image-only, and lives outside hidden
      containers in the raw HTML.

### Scenario 6 — No overlap at all supported widths (FR-010, SC-008)

- [ ] With the modal open, the 004 overlap-matrix script extended
      with the modal rect returns no pairs at widths 320, 480, 768,
      1280, 1920 px (device toolbar) × default zoom:
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
- [ ] At 320 px the modal fits the viewport (no horizontal overflow);
      tall content scrolls inside the modal (`overflow-y: auto`),
      never the page; nothing is clipped.
- [ ] Text zoom at 200% keeps the modal fully readable and disjoint
      from the existing UI (internal scroll absorbs the growth).

### Scenario 7 — No network traffic, single storage write (FR-011, SC-007)

- [ ] Opening and closing the modal adds zero network requests. The
      network panel shows no new requests and the map is not
      reloaded.
- [ ] The only storage write is `matreecover.story-dismissed` on
      explicit dismissal. No timestamps, no counters, no tracking.

### Scenario 8 — Attribution page never shows the modal (FR-012)

- [ ] Opening the attribution page (`/attribution`) shows no modal,
      no story markup, and no modal behavior.

### Scenario 9 — No regression (FR-007, FR-014, SC-005)

- [ ] After dismissal, the existing smoke checklists
      `smoke_us1.md` to `smoke_us4.md` pass unchanged (map + popup,
      tree toggle, overlap matrix).
- [ ] Building popup, Bäume toggle, Helligkeit slider, and zoom
      behave exactly as before the feature.

## Result

- [ ] All applicable checks pass.
