# Feature Specification: DSGVO Disclosure (Datenschutzerklärung)

**Feature Branch**: `018-dsgvo-disclosure`
**Created**: 2026-08-10
**Status**: Draft
**Input**: User description: "based on the context in this session, we need to see what needs to be added/changed to our site with minimal disruption to the user flow and absolute minimal use to be DSGVO conform. u can interview me if you need direction"

**Builds on**: `validation/dsgvo-assessment-2026-08-10.md` on `research/dsgvo-cookies-conformity` (dbb21c4) — full gap analysis; this spec implements the P1/P2 items only.

## Goal & Constraints

Make the site **DSGVO-conform without adding any user-facing interaction** (no cookie banner, no consent dialog, no new buttons or modals) and **without changing site behavior** (no new tracking, no CSP changes, no new scripts, no new storage). The site is tracking-free by design; the work is *disclosure* (Art. 13) and three small hardening edits.

Out of scope for this feature (deferred, documented in the assessment as follow-ups):
- Self-hosting MapLibre glyphs (large change, ~1 day).
- General page-typography redesign.
- A multi-language (DE/EN) version of any page.

## Clarifications

### Session 2026-08-10

- Q: What is the supervisory authority for the operator? → A: Address in Impressum is Mannheim, Baden-Württemberg → Landesbeauftragter für den Datenschutz und die Informationsfreiheit Baden-Württemberg (LfDI BW, poststelle@lfdi.bwl.de, https://www.baden-wuerttemberg.datenschutz.de).
- Q: Where should the new legal link live? → A: Footer of `index.html`, immediately next to the existing "Impressum" link, as a sibling `<a class="legal-link">` so the styling contract for the legal-link group is unchanged.
- Q: Should MapLibre glyph CDN be self-hosted in this feature? → A: No — disclose-only in the new Datenschutzerklärung; self-hosting is deferred to a follow-up feature.
- Q: Should a cookie banner be added? → A: No — the site sets no cookies, no non-essential storage; a banner would imply non-essential storage that does not exist, undermining the privacy claim.
- Q: Should the new page be German-only? → A: Yes — the entire site is German; English version out of scope.

## User Scenarios & Testing

### User Story 1 — Visitor reads the site's data practices (Priority: P1)

A privacy-conscious visitor (e.g. a journalist, regulator, or potential donor evaluating the project) opens the site, sees a "Datenschutzerklärung" link in the footer alongside the existing "Impressum" link, clicks it, and reads a short, plain-language statement of:

- who is responsible (Rami Abu-Hamad, Mannheim),
- which third parties receive the visitor's connection data (Cloudflare edge, BKG basemap.de, MapLibre demo glyph CDN, Ko-fi CDN and outbound link),
- on which legal basis each processing happens (Art. 6(1)(b)/(f) DSGVO, § 25(2) Nr. 2 TDDDG for the strictly-necessary `localStorage` key),
- the data subject's rights (access, rectification, erasure, restriction, portability, objection, complaint to LfDI BW),
- that no cookies, no analytics, no fingerprinting, no profiling happens.

**Why this priority**: This is the Art. 13 transparency obligation and the only **substantive** gap. Without it, the site is procedurally non-conform even though the underlying processing is minimal. The current Impressum has only a short paragraph that under-discloses recipients.

**Independent Test**: Load `https://abu-hamad.de/map/`, scroll to the footer, see the new "Datenschutzerklärung" link, click it, land on `https://abu-hamad.de/map/datenschutz` with a German document containing all 9 blocks listed in FR-002. The page is readable on mobile (320 px) and desktop, the link from the footer is keyboard-reachable, and the page is included in the sitemap.

**Acceptance Scenarios**:

1. **Given** the live site, **When** the visitor scrolls to the footer, **Then** two legal links are visible: "Impressum" and "Datenschutzerklärung".
2. **Given** the visitor clicks the "Datenschutzerklärung" link, **When** the new page loads, **Then** it renders without console errors, the `<title>` and `<h1>` both read "Datenschutzerklärung" (German), and the page is reachable in the keyboard tab order from the back-link.
3. **Given** the new page, **When** the visitor reads it, **Then** all 9 required content blocks (FR-002) are present, each in plain German.
4. **Given** the visitor's mobile device (320 px viewport), **When** the page renders, **Then** the prose is fully readable without horizontal scroll and respects the same dark-mode color scheme as the existing `impressum.html`.
5. **Given** a crawler (e.g. Googlebot) fetching `sitemap.xml`, **When** the sitemap is parsed, **Then** `datenschutz` is listed alongside the existing entries.

---

### User Story 2 — Impressum no longer under-discloses (Priority: P1)

A visitor who clicks "Datenschutzerklärung" from the Impressum (instead of the footer) lands on the new page; the Impressum's existing privacy paragraph is reduced to a single sentence plus a clear pointer, so the Impressum no longer makes the misleading "no active collection" claim that under-discloses third-party recipients.

**Why this priority**: The Impressum is the most legally-tested page (regulators start there). Leaving the old paragraph in place would create a contradiction: Impressum says "no active collection", new Datenschutzerklärung says Cloudflare + BKG + MapLibre + Ko-fi receive connection data. Removing the contradiction is part of the same fix as US-1.

**Independent Test**: Open `https://abu-hamad.de/map/impressum`, confirm the "Datenschutzerklärung" section is replaced by a single short sentence ("Mehr Informationen zum Datenschutz finden Sie in der [Datenschutzerklärung](/datenschutz).") and the old multi-sentence paragraph is removed.

**Acceptance Scenarios**:

1. **Given** the live Impressum, **When** a visitor reads the "Datenschutz" section, **Then** the section is at most one sentence and links to the new page.
2. **Given** the new Datenschutzerklärung, **When** a visitor reads it, **Then** it does not contradict the Impressum.

---

### User Story 3 — Existing story-modal remains functional and accessible (Priority: P2)

The story-modal first-visit dismissal flow (`localStorage["matreecover.story-dismissed"]`, the only end-device write) is unchanged. The new Datenschutzerklärung mentions the key and the § 25(2) Nr. 2 TDDDG exemption.

**Why this priority**: Documenting the exemption is the only P2 item, but the existing dismissal flow must not regress.

**Independent Test**: Open the site, click ✕ on the story modal, reload, confirm the story does not re-appear, inspect `localStorage` in DevTools and confirm exactly the `matreecover.story-dismissed` key (no new keys added by this feature).

**Acceptance Scenarios**:

1. **Given** the dismissed story modal, **When** the visitor reloads the page, **Then** no storage key other than `matreecover.story-dismissed` is set.
2. **Given** the new Datenschutzerklärung, **When** a visitor reads the "Cookies / localStorage" block, **Then** the `matreecover.story-dismissed` key is named and the § 25(2) Nr. 2 TDDDG exemption is cited.

---

### User Story 4 — Ko-fi donation link is hardened (Priority: P2)

The existing Ko-fi donation link's `rel` attribute is upgraded from `noopener` to `noopener noreferrer nofollow sponsored` so that the page does not transmit its referrer (redundant with the HTTP `Referrer-Policy: strict-origin-when-cross-origin` header but belt-and-suspenders) and is honest about being an outbound sponsored link.

**Why this priority**: This is a single attribute change that costs nothing, defends the visitor's referrer header, and matches the DSK recommendation for outbound monetization links. Not DSGVO-critical but bundled because the same file is touched.

**Independent Test**: Open the live site, inspect the Ko-fi link, confirm the `rel` attribute is exactly `noopener noreferrer nofollow sponsored`; click it (or simulate), confirm the Ko-fi page opens in a new tab with `window.opener === null`.

**Acceptance Scenarios**:

1. **Given** the published site, **When** the Ko-fi donation link is rendered, **Then** its `rel` attribute is exactly `noopener noreferrer nofollow sponsored`.
2. **Given** the new `rel` value, **When** the link is activated, **Then** the Ko-fi page opens in a new tab and the source tab's `window.opener` is `null`.

---

### User Story 5 — README and story-modal wording reflect actual data flow (Priority: P3)

The README's marketing sentence ("no server, no database, no analytics behind it") is softened to acknowledge that the visitor's IP and User-Agent reach Cloudflare, BKG, and Ko-fi as part of standard HTTP. The story-modal copy is unchanged (it already says "diese Anwendung lädt direkt von BKG"); the README is the only place that read like a privacy-zero claim.

**Why this priority**: DSK best practice — public-facing documents should not contradict the Datenschutzerklärung. Low effort, prevents visitor confusion, prevents a future "your README is misleading" complaint.

**Independent Test**: Read the README on the default branch, confirm no sentence implies zero egress; confirm a sentence names Cloudflare, BKG, and Ko-fi as recipients of standard HTTP connection data and points to the Datenschutzerklärung.

**Acceptance Scenarios**:

1. **Given** the README on the default branch after this feature ships, **When** read top to bottom, **Then** no sentence claims "nothing leaves the browser" or equivalent.
2. **Given** the new README wording, **When** read, **Then** the three external recipients (Cloudflare, BKG, Ko-fi) are named and the link to the Datenschutzerklärung is present.

---

### Edge Cases

- **404 on `/datenschutz`**: the Worker serves static assets via the `ASSETS` binding with `not_found_handling = "none"`; if the file is not yet deployed, the visitor sees a real 404. The deploy step must include `datenschutz.html` in the published `dist-assets/`.
- **Keyboard-only navigation**: the new "Datenschutzerklärung" link in the footer is reachable in tab order, shows a visible focus indicator, and the back-link on the new page returns to the map. No focus trap is added.
- **Screen reader**: the German compound noun "Datenschutzerklärung" is announced as a single token by standard screen readers; no `aria-label` override is needed. The back-link's `← Zur Karte` arrow is decorative and has no semantic effect.
- **Print styles**: the new page is a text document; the default browser print rendering is acceptable. No `@media print` rule is added.
- **CSP unchanged**: the new page is static HTML with the same in-line `<style>` block as `impressum.html` and `attribution.html`; no new external hosts, so the existing CSP `default-src 'self'` is sufficient. The CSP `<meta>` tag and the Worker response header remain unchanged.
- **localStorage in private/incognito mode**: when the story modal is dismissed in a private window, the key is not persisted across sessions (browser-default behavior in private mode); the new Datenschutzerklärung's "Speicherdauer" block explains the storage is on-device and the visitor can clear it via browser settings — this works in both regular and private windows.
- **robots.txt and sitemap.xml coverage**: the new page must be added to `sitemap.xml`; `robots.txt` already allows it implicitly (it only disallows the data files).
- **Re-entry from external links**: if a regulator or a third party links directly to `/datenschutz`, the page must resolve without a redirect. Confirmed: the Worker's `html_handling = "auto-trailing-slash"` will redirect `/datenschutz` to `/datenschutz/` (or vice versa) consistently with the existing pages.
- **Story-modal dismissal spec argument**: the § 25(2) Nr. 2 TDDDG justification for the `localStorage` key is added to `specs/007-first-visit-story/contracts/dismissal-state.md` (a doc-only update in another spec). This is a dependency of US-3's documentation but not a functional change.

## Requirements

### Functional Requirements

- **FR-001**: The site MUST publish a new static page at `https://abu-hamad.de/map/datenschutz` containing the German Datenschutzerklärung.
- **FR-002**: The new page MUST contain the following nine content blocks, in this order, each in plain German:
    1. **Verantwortlicher** — full name, address (Mannheim), and contact email of the operator (reused from the Impressum).
    2. **Datenschutzbeauftragter** — statement that no Data Protection Officer is appointed, with brief justification (private site, no § 38 BDSG threshold met).
    3. **Zwecke und Rechtsgrundlagen** — service delivery (Art. 6(1)(b) DSGVO for the donation link where the visitor is the party, otherwise Art. 6(1)(f) legitimate interest for the public-interest map) and tile serving (Art. 6(1)(f)).
    4. **Empfänger und Drittländertransfer** — named recipients: Cloudflare Inc. (US, EU-U.S. Data Privacy Framework adequacy, DPA), BKG / basemap.de (DE public body), MapLibre demo glyph CDN (US, demotiles.maplibre.org — disclosure of dependency per `src/site/vendor/PROVENANCE.md`), Ko-fi (US, image CDN plus outbound link). For each: data type (IP, User-Agent, referrer, timestamp), legal basis, retention (per the recipient's published policy).
    5. **Speicherdauer** — no server-side storage by the operator; Cloudflare logs per Cloudflare DPA; on-device `localStorage` key persisted until the visitor clears browser storage, with a one-line browser-specific instruction.
    6. **Betroffenenrechte** — access (Art. 15), rectification (Art. 16), erasure (Art. 17), restriction (Art. 18), portability (Art. 20), objection (Art. 21), and the right to lodge a complaint with the **Landesbeauftragte für den Datenschutz und die Informationsfreiheit Baden-Württemberg** (poststelle@lfdi.bwl.de).
    7. **Cookies und localStorage** — explicit statement: "Diese Website setzt keine Cookies. Es wird ausschließlich ein localStorage-Eintrag `matreecover.story-dismissed` gesetzt, und nur, wenn Sie das Story-Fenster aktiv schließen. Rechtsgrundlage: § 25(2) Nr. 2 TDDDG (technisch erforderlich)."
    8. **Keine automatisierten Entscheidungen / kein Profiling** — Art. 22 statement.
    9. **Stand** — "Letzte Aktualisierung: 2026-08-10".
- **FR-003**: The new page MUST mirror the visual and structural template of `src/site/impressum.html` (same dark-mode color scheme, same `<style>` block, same back-link, same `<title>` + `<h1>` pattern, same `<main>` wrapper, max-width 40 rem, German language) so the three info pages feel like a single document set.
- **FR-004**: The footer of `index.html` MUST contain both the existing "Impressum" link and a new "Datenschutzerklärung" link, both as siblings of the existing `<a class="legal-link">`, with the same `class="legal-link"` attribute and the same order they appear in the page (Datenschutzerklärung first because visitors are more likely to want it than the Impressum? — no, keep order: Impressum first to match § 5 DDG expectations, then Datenschutzerklärung).
- **FR-005**: The existing `<a class="legal-link" href="impressum">Impressum</a>` in the footer MUST be followed by a single new sibling: `<a class="legal-link" href="datenschutz">Datenschutzerklärung</a>`, separated by a single space. No new wrapper element, no separator dot, no icon.
- **FR-006**: The Ko-fi donation link's `rel` attribute MUST be updated from `"noopener"` to `"noopener noreferrer nofollow sponsored"`. The `href`, `target`, `class`, and inner `<img>` MUST be unchanged.
- **FR-007**: The Impressum's existing "Datenschutz" section MUST be reduced to a single sentence that points to the new page: "Mehr Informationen zum Datenschutz finden Sie in der [Datenschutzerklärung](/datenschutz)." The old multi-sentence paragraph that mentions BKG-only MUST be removed.
- **FR-008**: `src/site/sitemap.xml` MUST list `datenschutz` alongside the existing entries (index, impressum, attribution). The `<loc>` and `<lastmod>` elements follow the existing pattern.
- **FR-009**: `src/site/robots.txt` MUST continue to allow the new page implicitly (no change required — `robots.txt` only disallows the data files). If the file is updated for any reason, the new page must not be disallowed.
- **FR-010**: `specs/007-first-visit-story/contracts/dismissal-state.md` MUST be updated to add a short paragraph (3–5 sentences) documenting the § 25(2) Nr. 2 TDDDG exemption argument for the `matreecover.story-dismissed` key: (a) the write happens only on explicit user action, (b) without storage the user's expressed dismissal intent cannot be honored across reloads, (c) no alternative mechanism (e.g. server-side preference) is as privacy-friendly because it would itself require tracking.
- **FR-011**: The default-branch `README.md` MUST have its privacy-related wording softened so no sentence implies zero egress. The replacement wording MUST name Cloudflare, BKG, and Ko-fi as recipients of standard HTTP connection data and MUST link to the new Datenschutzerklärung.
- **FR-012**: The new page MUST contain no scripts, no iframes, no third-party resources, no analytics, no cookies, no localStorage reads, no localStorage writes. The CSP `<meta>` tag and the Worker's `Content-Security-Policy` response header MUST remain unchanged (the new page is purely static and same-origin).
- **FR-013**: The new page MUST be reachable in the keyboard tab order from the back-link and from the footer link on `index.html`, and the visible focus indicator MUST be the same one used by the existing legal-link styling (inherited from the project's existing CSS, no new rules added).
- **FR-014**: The deploy artifact (`dist-assets/datenschutz.html`) MUST be produced by the existing build pipeline (no new build step). The deploy record MUST include the new file in the manifest.

### Key Entities

- **Datenschutzerklärung page** — a static German HTML document at `src/site/datenschutz.html`, served at `https://abu-hamad.de/map/datenschutz`. Subject: same template contract as `impressum.html` and `attribution.html`. Lifecycle: edited on this branch, deployed via the existing Cloudflare Worker + ASSETS binding, listed in `sitemap.xml`, discoverable from the footer of `index.html`.
- **Footer legal-link group** — the existing two links ("Impressum" → "Datenschutzerklärung") rendered in the page footer of `index.html`. Subject: same `<a class="legal-link">` styling; no new CSS rules; no new wrapper.
- **`matreecover.story-dismissed` storage key** — the only on-device write the site performs. Documented in the new Datenschutzerklärung and in `specs/007-first-visit-story/contracts/dismissal-state.md`. Behavior unchanged by this feature.

## Success Criteria

- **SC-001**: A visitor on any viewport ≥ 320 px can locate the "Datenschutzerklärung" link in the footer of `https://abu-hamad.de/map/` without scrolling more than one viewport height (the link is in the same row as the existing "Impressum" link).
- **SC-002**: The new `https://abu-hamad.de/map/datenschutz` page returns HTTP 200, renders in under 1 second on a desktop browser with a 3G connection, contains all nine FR-002 content blocks in German, and is reachable via keyboard alone in under 4 tab presses from the back-link.
- **SC-003**: The new page contains no JavaScript, no third-party requests (verified by the browser DevTools Network panel: only the document itself loads), and the page's CSP report-uri is silent (no CSP violation events in the Worker's logs after 7 days of public access).
- **SC-004**: Existing site behavior is unchanged: map values, colors, labels, popups, interactions, the story-modal dismissal flow, the donation button, the security headers, the CSP, and all performance budgets are identical before and after this feature ships. The full test suite passes with no skipped or modified tests.
- **SC-005**: A regulator or visitor reading both the Impressum and the Datenschutzerklärung finds them consistent (no contradiction, no "no active collection" claim in the Impressum, all third-party recipients named in the Datenschutzerklärung).
- **SC-006**: The deploy step for the new page takes no longer than the existing deploy step for `impressum.html` (same file size order of magnitude, same template). The deploy record shows the new file in the manifest.
- **SC-007**: Site visitors see **no new UI element beyond the one additional footer link**. The story modal, the donation button, the brightness slider, the Bäume toggle, the surface panel/sheet, the attribution, the zoom control, and the legend are all visually and functionally identical to the current state.

## Assumptions

- **A-001**: The site operator is Rami Abu-Hamad, residing in Mannheim, Baden-Württemberg. The supervisory authority is therefore the LfDI BW. (Source: `src/site/impressum.html`.)
- **A-002**: The existing build pipeline (which copies `src/site/*.html` to `dist-assets/`) needs no changes to publish the new page; the file is a same-template sibling of the existing three info pages.
- **A-003**: The `localStorage` key `matreecover.story-dismissed` is the only end-device write the site performs (confirmed by the DSGVO assessment, scout artifact `agent://ScoutDSGVO`, 2026-08-10). The § 25(2) Nr. 2 TDDDG exemption argument is sufficient and needs no change to the dismissal flow itself.
- **A-004**: No new CSP directive is required. The new page is same-origin, static, with the same in-line `<style>` block pattern as the other info pages; the existing `style-src 'self' 'unsafe-inline'` already covers it.
- **A-005**: The story-modal first-visit copy is not changed by this feature; only the existing Impressum paragraph is reduced to a pointer, and the README wording is softened. The story modal already says "direkt von der Bundesanstalt für Kartographie und Geodäsie (BKG)" which is consistent with the new Datenschutzerklärung.
- **A-006**: Self-hosting of MapLibre glyphs is deferred to a follow-up feature (or remains a permanent disclosure-only state). This feature discloses the dependency textually in the new page.
- **A-007**: Cloudflare is on the EU-U.S. Data Privacy Framework list at the time of writing (confirmable from https://www.dataprivacyframework.gov/). If that changes, the Datenschutzerklärung must be updated — but that is a maintenance concern, not in scope for this feature.
- **A-008**: The site does not need a `robots.txt` change because the existing `robots.txt` does not block the page. The new `datenschutz` URL is implicitly allowed.
- **A-009**: The project's existing `<a class="legal-link">` styling is sufficient for the new link. No new CSS rules, no new wrapper element, no new visual decoration.
- **A-010**: The deploy step uses a manifest that includes the new file; the existing manifest logic iterates the `src/site/*.html` set and includes the new file automatically (or is updated to do so). This is verified by checking the deploy record after the first deploy.
- **A-011**: The `specs/007-first-visit-story/contracts/dismissal-state.md` update is a doc-only change in another feature's spec directory; it is not a regression of the story-modal feature and does not require a new branch.

## Out of Scope

- Adding a cookie banner or consent dialog. The site sets no non-essential storage; a banner would imply otherwise.
- Self-hosting MapLibre glyphs. Deferred to a follow-up feature; the new Datenschutzerklärung discloses the dependency.
- Translating the new page to English or any other language.
- Changing the story-modal copy beyond the § 25(2) Nr. 2 TDDDG exemption citation (which lives in the new page and in the spec 007 contract, not in the modal itself).
- Adding analytics of any kind.
- Changing the CSP, the security headers, the Worker code, the data flow, the localStorage schema, the build pipeline, or any other behavioral surface.
- Removing the existing `https://demotiles.maplibre.org` font-source entry from the CSP. The dependency is real and the disclosure is the fix.
- Adding a `robots.txt` rule for the new page (it is implicitly allowed).
- A `Wir verkaufen Ihre Daten nicht`-style statement — the assessment found no data sale, and adding such a statement without basis is itself misleading. Omitted.

## Dependencies

- **`src/site/impressum.html`** (existing): the new `datenschutz.html` follows the same template; the existing Impressum's "Datenschutz" section is updated to point to the new page (FR-007).
- **`src/site/index.html`** (existing): the footer legal-link group is updated (FR-005); the Ko-fi `rel` attribute is updated (FR-006).
- **`src/site/sitemap.xml`** (existing): the new page is added (FR-008).
- **`specs/007-first-visit-story/contracts/dismissal-state.md`** (existing): the § 25(2) Nr. 2 TDDDG exemption argument is added (FR-010).
- **`README.md`** (existing, default branch): the privacy-related wording is softened (FR-011).
- **Cloudflare Worker `workers/map/index.js`** (existing): no change. The `ASSETS` binding serves the new page automatically.
- **CSP `<meta>` tag in `index.html`** (existing): no change.
- **Build pipeline**: no change; the new HTML file is published by the same step that publishes the other three info pages.

## Verification

- Manual: load the live `https://abu-hamad.de/map/`, click the new footer link, verify the page loads and contains all nine FR-002 blocks.
- Manual: inspect the page's network panel — no third-party requests, only the document itself.
- Manual: tab through the page with keyboard alone — back-link, content, no focus trap.
- Manual: at viewport 320 px, no horizontal scroll on the new page; text reads at the same line length as `impressum.html`.
- Test suite: full project test suite (unit + interaction-latency + visual parity + layout overlap matrix) passes unchanged.
- Governance gates: layout overlap matrix, public-hygiene checks, commit-checks, CSP byte-equality (HTML `<meta>` vs Worker header) all pass.
- Lighthouse / site audit: re-run a privacy/cookie audit; expect the cookie count to remain 0 and the localStorage count to remain 1 (`matreecover.story-dismissed`).
- Manual: confirm `localStorage` contains exactly the same keys before and after the deploy.
- Manual: read the deployed page once, copy the text into a search engine, confirm no third-party hosts are mentioned in the prose beyond the named recipients (Cloudflare, BKG, MapLibre, Ko-fi).
