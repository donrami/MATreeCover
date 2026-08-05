# Research: First-Visit Story Modal

Research date: 2026-08-05. All decisions are codebase-grounded
(read of `src/site/index.html`, `main.js`, `style.css`,
`src/pipeline/publish.py`, 004 contracts) plus live verification of
both reference links (HTTP 200, 2026-08-05). No external unknowns
remained; every "NEEDS CLARIFICATION" candidate from the plan's
Technical Context resolved below.

## R-1 Modal show timing

**Decision**: Show the modal at `init()` in `main.js` — a module
script at the end of `<body>`, which executes after DOM parsing, so
the modal markup is guaranteed present. The map initializes in the
same call and renders behind the overlay.

**Rationale**:
- Acceptance scenario 1 ("When page finishes loading, Then story
  modal appears automatically") is satisfied: the module runs
  before the `load` event completes, so the modal is already visible
  at load-complete.
- The spec's edge case "Modal open while map loads: map renders
  behind modal; closing modal causes no reflow or reload" explicitly
  permits showing the modal before the map finishes rendering.
- Independent of tile-load success: if the tiles layer fails, the
  story still shows (the spec requires the modal on "first visit",
  not on "successful map load").
- Simplest possible wiring: one call in `init()`, no extra event
  dependency.

**Alternatives considered**:
- Wait for MapLibre `map.on('load')`: rejected — delays the story
  until style+tiles load, breaks FR-001 if tiles hang, and
  contradicts the "modal open while map loads" edge case.
- Wait for `window` `load` event: rejected — same failure mode, and
  `init()` already runs after DOM parse.

## R-2 Dismissal persistence mechanism

**Decision**: `localStorage` key `matreecover.story-dismissed`,
value `"1"` (presence = dismissed). Every access wrapped in
`try/catch`; on any storage failure, a session-only in-memory flag
takes over: the modal still appears and dismisses for the current
visit, and reappears on the next visit (FR-013).

**Rationale**:
- FR-005 requires "stored on-device" + "never reappear on later
  visit in same browser": `localStorage` survives reloads, tab
  closes, and browser restarts; `sessionStorage` does not.
- FR-011 (no network, no tracking): `localStorage` never leaves the
  device and adds zero requests; no cookie (cookies would ride
  request headers and are unnecessary).
- The site has no existing storage keys (the brightness slider is
  session-only in-memory), so a single new namespaced key is
  unambiguous. `matreecover.` prefix scopes the key to this project
  on the shared origin.
- `try/catch` is required because `localStorage` access itself can
  throw (blocked cookies/storage in some private modes) — the spec
  mandates graceful degradation (FR-013), never an exception.
- No timestamp/version value is stored: the spec explicitly forbids
  measurement/analytics and "re-show on schedule" is out of scope.

**Alternatives considered**:
- `sessionStorage`: rejected — dies with the tab, violates "later
  visit" persistence (FR-005).
- IndexedDB: rejected — overkill for one boolean flag, async API,
  larger surface for zero benefit.
- Cookie: rejected — unnecessary request-header overhead, violates
  the spirit of "no tracking, quiet" (spec US2).

## R-3 Modal placement — no-overlap contract

**Decision**: A fixed full-viewport backdrop
(`.story-backdrop`, `z-index: 30` — above `#left-stack`/`#attribution`
at `z-index: 10` and the map controls at default stacking) hosts a
centered dialog card `.story-modal` in the viewport's safe zone:

- **Desktop (>480 px)**: modal top margin 260 px — below the left
  column (legend + tools card bottom ≈ 244 px at default font and
  220 px legend width), centered horizontally, `max-width: 480px`,
  `max-height: calc(100vh - 284px)` (260 top + 24 bottom reserve
  clears the bottom-right attribution row), `overflow-y: auto`.
- **Narrow (≤480 px)**: modal top margin 60 px — below the top-right
  zoom control; bottom reserve 160 px keeps it above the bottom
  strip (legend strip ≈ 38 px + gap 10 px + tools card ≈ 92 px,
  bottom-anchored at 12 px ≈ 152 px total); `max-height:
  calc(100vh - 220px)`, `width: calc(100vw - 24px)`,
  `overflow-y: auto`.

**Rationale**:
- FR-010 demands the modal box never overlap legend, tools card,
  zoom control, or attribution at any width ≥320 px. A naive
  centered placement fails at 768–1024 px widths (the left column
  is ~232 px wide; a 480 px centered modal overlaps it), so the
  desktop modal is anchored *below* the left column instead of
  beside it — one rule that is disjoint at every width >480 px.
- Internal scrolling (`overflow-y: auto`) satisfies the "content
  scrolls inside modal, nothing clips" requirement for tall content,
  text zoom, and small viewports (spec edge cases).
- The 004 `ui-layout` contract's verification technique (bounding-box
  pairwise-disjoint matrix at 320/480/768/1280/1920 px) is reused
  and extended with the modal rect while open — same tooling, one
  more element (quickstart Scenario 6, `smoke_us5.md`).
- Offsets are pinned as constants in the contract and re-validated
  by the matrix, so small layout drift in the left column is caught
  by smoke, not silently tolerated.

**Alternatives considered**:
- Center of viewport, always: rejected — overlaps the left column
  at medium widths (computed above).
- Right column beside the zoom control: rejected — at 481–768 px the
  remaining width is <200 px; unusable for a story card.
- Flexbox overlay with `align-items: flex-start` + margin: adopted
  as the mechanism (same geometry, simpler CSS).

## R-4 Dialog semantics and focus management

**Decision**: WAI-ARIA dialog pattern on the modal element:
`role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing at
the story title `id`; `tabindex="-1"` so the dialog itself can
receive focus. Behavior in `main.js`:
- Open: `hidden` attribute removed; focus moves to the dialog
  element (screen reader announces the dialog name — FR-009).
- While open: Tab/Shift+Tab are trapped inside the dialog
  (keydown handler cycling the focusable elements: close button +
  the two reference links); `aria-modal="true"` hides the rest of
  the page from assistive technology.
- Close (close-button click or Escape): overlay removed from the
  DOM; focus restored to the previously focused element (the
  document body, since the modal opens on page load); all listeners
  torn down.

**Rationale**:
- FR-008 (focus enters modal, Escape closes, focus returns) and
  FR-009 (announced dialog name, readable story text) map directly
  onto this pattern; it is the standard, minimal, dependency-free
  implementation.
- Focus moves to the dialog element (not the close button) so the
  announced name + "dialog" role is the first thing a screen-reader
  user hears; Tab then reaches the close button first (DOM order:
  heading, close button, story, links).
- The map needs no programmatic disable: the backdrop intercepts
  pointer events while open; removing it from the DOM makes the map
  immediately interactive again with zero reflow (FR-007).

**Alternatives considered**:
- Native `<dialog>` element with `showModal()`: rejected — focus
  trapping and Escape are built in, but default styling/backdrop
  behavior varies and the project has no precedent for it; the
  manual pattern matches the codebase's plain-DOM style and is
  fully testable via the smoke checklist. (Revisit if the site ever
  needs a second modal.)
- `inert` on page siblings while open: rejected as unnecessary —
  `aria-modal` + the focus trap cover the requirement; `inert`
  would add restore logic for zero observable gain in the smoke
  matrix.

## R-5 Story content — facts and grounding

**Decision**: Static German copy embedded in `index.html` (no fetch,
FR-011), containing the four required elements (FR-002) plus the
central-value sentence (FR-003). Draft copy is normative in
`contracts/story-content.md`; facts:

- SPIEGEL article "Hitze in Europa: Wie gut Stadtbäume vor extremer
  Wärme schützen", DER SPIEGEL, 2026-07-29 (verified live: URL
  resolves HTTP 200; meta title/description confirm the subject —
  streets in many European cities exceed 40 °C, cities have too
  little green, planting more trees alone is not enough).
- CityTreeCover README (verified live via GitHub API): "This project
  emerged reading Spiegel article … says 30% surrounding area
  radius 60 m should be shaded trees (Croeser, Rahman & Ghosh
  (2026))"; "I wanted to get done within current July 2026 heatwave
  in Germany".
- Our map: buildings colored by average tree cover within the 60-m
  surroundings — matches the existing legend text "Durchschnittlicher
  Baumanteil im 60-m-Umkreis" (FR-003).

**Rationale**: The story's claims are grounded in the two primary
sources the spec names; no invented numbers. Both links verified
resolving on 2026-08-05 (User Story 3 requires working links).

**Alternatives considered**:
- Fetch story content at runtime: rejected — FR-011 forbids network
  requests; CSP `script-src 'self'` blocks inline fetching anyway.
- English copy: rejected — clarification Q4 (German, `lang="de"`).

## R-6 No-layout-shift / no-regression guarantees

**Decision**: The overlay is `position: fixed; inset: 0` with the
map untouched beneath; closing removes only the overlay subtree.
The existing map interactions are never touched by the modal code
(`main.js` gains one self-contained module: show/dismiss/persist).

**Rationale**:
- FR-007 (map visible and fully rendered while open; interactions
  resume immediately on dismissal; no layout shift) follows from
  the overlay being a separate fixed layer — the map container's
  box is never resized.
- FR-014 (no change to map data/layers/popup/toggle/slider/zoom) is
  enforced by construction: the feature adds markup, CSS, and one
  JS module; it calls no MapLibre API except none at all.
- Regression surface: existing smoke_us1..us4 unchanged and re-run
  post-dismissal (quickstart Scenario 9).

## R-7 Validation approach

**Decision**: New manual smoke checklist
`tests/frontend/smoke_us5.md` following the established format
(goal, FR/SC mapping, setup, checks, result), plus quickstart
scenarios 1–9 as the runnable guide. The 004 overlap-matrix console
script is reused with the modal rect added. Optional evidence
record under `validation/first-visit-story/` (matrix JSON + network
panel observation), matching the 004 precedent.

**Rationale**: The project validates frontend behavior exclusively
via manual smoke checklists (no browser test framework exists);
pytest covers the pipeline only, which this feature does not touch.

**Alternatives considered**: A Playwright/puppeteer automated test:
rejected — no precedent in the repo; adding a browser-test
dependency contradicts the "no new dependencies" constraint and the
manual-smoke convention.
