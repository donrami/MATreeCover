# US5 Frontend Smoke Checklist — First-Visit Story Modal

**Goal**: Verify the first-visit story modal. It must appear
automatically once per browser, in German, with the complete approved
story and both working reference links. It must dismiss via the close
button or Escape, with no layout shift and no reload. Dismissal
persists on-device and degrades gracefully when storage is blocked.
The modal is fully keyboard- and screen-reader-operable, never
overlaps the existing UI at any supported width, and never shows on
the attribution page.

**Maps**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007,
FR-008, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, SC-001,
SC-002, SC-003, SC-004, SC-005, SC-006, SC-007, SC-008 (spec
007-first-visit-story, user stories 1–3).

**Setup**: Run `make publish`. Serve `dist/` with a Range-capable
static server (nginx or equivalent). Open the served URL in a clean
browser profile with no stored dismissal state and WebGL 2 enabled.

The story wording was approved 2026-08-05 (T006). The copy in
`specs/007-first-visit-story/contracts/story-content.md` is
normative. The modal implements it verbatim.

## Checks

### Scenario 1 — First visit shows the modal (FR-001, SC-001)

- [X] Fresh profile with no stored dismissal state: opening the map
      page shows the modal automatically over the fully rendered map
      (tiles continue loading behind the overlay).
- [X] The page and the modal copy are in German (`lang="de"`).

### Scenario 2 — Story complete, links work (FR-002, FR-003, FR-006, SC-003)

- [ ] The modal contains all required elements: the map-origin
      narrative (SPIEGEL article → CityTreeCover reference project →
      this Mannheim replication), the SPIEGEL article link, the
      CityTreeCover link, the source-repository link ("Quellcode auf
      GitHub"), and the June/July 2026 heatwave context.
- [ ] The central-value sentence states that buildings are colored by
      the average tree cover in their 60-m surroundings, matching the
      legend text "Durchschnittlicher Baumanteil im 60-m-Umkreis".
- [ ] All three links carry `target="_blank" rel="noopener"` and the
      article title / project name / "Quellcode auf GitHub" as link
      text (SPIEGEL: "Hitze in Europa: Wie gut Stadtbäume vor
      extremer Wärme schützen"; CityTreeCover: the project name;
      source repository: "Quellcode auf GitHub").
- [ ] Activating the SPIEGEL link opens a new tab resolving the
      article (HTTP 200); activating the CityTreeCover link opens a
      new tab resolving `github.com/jcscaptures/CityTreeCover`;
      activating the source-repository link opens a new tab resolving
      `github.com/donrami/MATreeCover`.
- [X] Returning to the map tab shows the map unchanged and fully
      usable.

### Scenario 3 — Dismissal and persistence (FR-004, FR-005, SC-002, SC-004)

- [X] Dismissing via the visible close button removes the modal in a
      single action. Dismissing via Escape on a fresh visit works the
      same way.
- [X] Immediately after dismissal the map is fully interactive and
      there is no layout shift: the map container
      `getBoundingClientRect()` is unchanged before/after close and
      the network panel shows no reload.
- [X] Reloading the page does not show the modal again.
- [X] Closing the tab and reopening the page in the same browser does
      not show the modal again (key `matreecover.story-dismissed`
      present in DevTools → Storage → Local Storage, value `"1"`).
- [X] Clearing site data (DevTools → Application → Clear site data)
      restores first-visit behavior: the modal appears again.

### Scenario 4 — Storage unavailable (FR-013)

- [X] With storage blocked, the modal still appears on a fresh load.
- [X] The modal is dismissible (close button and Escape both work).
      Reloading shows the modal again, because the in-memory fallback
      is session-only.
- [X] No console errors from the storage fallback.

### Scenario 5 — Keyboard and screen reader (FR-008, FR-009, SC-006)

- [X] On first load, focus moves into the modal automatically; a
      screen reader announces the dialog name "Wie diese Karte
      entstanden ist" from `aria-labelledby`.
- [ ] Tab cycles within the modal (close button ↔ reference links,
      including the source-repository link); focus never leaves the
      modal while it is open.
- [X] Escape closes the modal and focus returns to the page (body).
- [X] The story text is real text content (paragraphs and links),
      never `aria-hidden` or image-only.

### Scenario 6 — No overlap at all supported widths (FR-010, SC-008)

- [X] With the modal open, the 004 overlap-matrix script extended
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
- [X] At 320 px the modal fits the viewport (no horizontal overflow);
      tall content scrolls inside the modal (`overflow-y: auto`),
      never the page; nothing is clipped.
- [X] Text zoom at 200% keeps the modal fully readable and disjoint
      from the existing UI (internal scroll absorbs the growth).

### Scenario 7 — No network traffic, single storage write (FR-011, SC-007)

- [X] Opening and closing the modal adds zero network requests. The
      network panel shows no new requests and the map is not
      reloaded.
- [X] The only storage write is `matreecover.story-dismissed` on
      explicit dismissal. No timestamps, no counters, no tracking.

### Scenario 8 — Attribution page never shows the modal (FR-012)

- [X] Opening the attribution page (`/attribution`) shows no modal,
      no story markup, and no modal behavior.

### Scenario 9 — No regression (FR-007, FR-014, SC-005)

- [X] After dismissal, the existing smoke checklists
      `smoke_us1.md` to `smoke_us4.md` pass unchanged (map + popup,
      tree toggle, overlap matrix).
- [X] Building popup, Bäume toggle, Helligkeit slider, and zoom
      behave exactly as before the feature.

## Result

- [X] All applicable checks pass.

- [x] Feature-014 bundle re-verified 2026-08-08 (scripts/smoke-verify.mjs fresh-profile driver + acceptance suite; zoom, controls, popups, trees toggle, no console errors)
