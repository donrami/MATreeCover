# Contract: Visible content (feature 016)

Requirement: FR-006 (US1, SC-004/SC-010). Subject: the crawlable informative text on the map page and the first-visit story modal behavior (feature 007). Implementation: a visible `<section>` in `src/site/index.html` plus the modal wiring in `src/site/main.js`. Enforcement: `tests/acceptance/test_seo_metadata.py`. Smoke checklist: `tests/frontend/smoke_us5.md` updated.

## Content (single source)

The visible section carries the map page's informative text, in German:

1. Project story: SPIEGEL context (July 2026), the CityTreeCover reference project, the GitHub source link.
2. Method: per-building mean tree cover in a 60-m radius, the 30 % shade guideline.
3. Data sources: DOP20 aerial imagery (LGL), GDI-MA district boundary, reused model weights (as stated on the attribution page).
4. Accuracy disclaimer (feature 010 content).

## Rules

1. **Visible in initial HTML**: the section is not inside `hidden`, `display:none`, `[hidden]`, `aria-hidden` content, or any other hidden container. It renders without user interaction and without JavaScript (research R-001/R-003).
2. **Single DOM location**: the story text exists in EXACTLY one location in the DOM. The visible section is the canonical copy (Clarifications 2026-08-09). The first-visit story modal presents the same content by opening and scrolling to the section. It must not hold a second copy of the text.
3. **Word share**: at least 80 % of the informative words (story, method, sources, disclaimer) appear in raw HTML outside hidden containers (SC-004). The acceptance test counts the informative text once. The single copy makes the count unambiguous.
4. **Self-contained copy**: the section must not reference "the map above" or require map interaction to be understood. Non-JS crawlers see no map (spec edge case). The text explains the map, the data, and the accuracy limits on its own.
5. **Modal behavior preserved** (feature 007, Clarifications 2026-08-09): first visit opens the modal. Dismiss persistence is unchanged. The modal now points at the visible section instead of holding its own hidden copy.
6. **No map change**: the section is added below the map container in the page flow. It does not change map values, colors, labels, popups, or interactions (FR-012).
7. **CWV neutral**: the section is static text. It adds no render-blocking resources and no interaction-path JavaScript (SC-008).

## Machine checks (acceptance test)

- Parse `dist/index.html`. Extract the informative text from the visible section. Assert the section is not inside a hidden container.
- Count informative words in the visible section versus informative words anywhere in hidden containers. Assert the visible share is >= 80 %.
- Assert the story copy (a distinctive phrase, e.g. the SPIEGEL sentence) occurs exactly once in the whole document.
- Assert the visible section contains the disclaimer and the source links.

## Regression notes

- `smoke_us5.md` (first-visit story modal) is updated: open the modal, verify it scrolls to the visible section, verify dismiss persistence still works. `scripts/smoke-verify.mjs` covers the interaction headlessly.
- The story modal previously held its own copy. Removing that copy is part of this feature and is the mechanism that keeps the single-DOM-location rule true.
