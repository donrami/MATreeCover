# Research: DSGVO Disclosure (feature 018)

Phase 0 output. Every NEEDS CLARIFICATION from the plan and every open question in the spec is resolved here with a decision, rationale, and alternatives.

The Phase 0 research for this feature is the read-only DSGVO / TDDDG conformity assessment `validation/dsgvo-assessment-2026-08-10.md` (commit `dbb21c4` on branch `research/dsgvo-cookies-conformity`). The assessment is the legal-research deliverable. This section consolidates the technical decisions surfaced by the assessment into a single short file for the plan.

## R1 — Site tracking posture stays tracking-free (FR-012, A-003)

- **Decision**: this feature does not introduce cookies, analytics, fingerprinting, third-party scripts, or non-essential storage. The new Datenschutzerklärung explicitly states the site is tracking-free, lists the only `localStorage` write (`matreecover.story-dismissed`), and cites the § 25(2) Nr. 2 TDDDG exemption.
- **Rationale**: the site is privacy-by-design and the assessment confirmed that adding tracking would be a regression of the existing posture. The assessment explicitly recommends against a cookie banner (DSK OH Digitale Dienste v1.2, § 3.2: a banner implies non-essential storage that does not exist).
- **Alternatives considered**:
    - Cookie banner (rejected — implies non-essential storage).
    - Explicit opt-in for the `localStorage` key (rejected — over-engineering for a single key that is itself the user's expression of preference; the dismissal is the opt-in).

## R2 — No CSP change (FR-012, A-004)

- **Decision**: the existing CSP `<meta http-equiv="Content-Security-Policy">` in `src/site/index.html` and the Worker's `Content-Security-Policy` response header remain byte-identical. The new page is same-origin, static, with the same in-line `<style>` block pattern as the other info pages. No new external host is needed.
- **Rationale**: the existing CSP `style-src 'self' 'unsafe-inline'` already covers the in-line `<style>` block on the new page. The existing `default-src 'self'` blocks scripts and connect-src beyond the allowlist. The new page contains no scripts and no fetch calls, so the existing policy is sufficient.
- **Alternatives considered**:
    - Adding a `script-src` relaxation for the page (rejected — no scripts are needed).
    - Removing the `'unsafe-inline'` style rule (rejected — would require refactoring the entire info-page template to a CSS file, see R5).

## R3 — Datenschutzerklärung content blocks (FR-002)

- **Decision**: the new page contains 9 content blocks in fixed order, as specified in FR-002. The blocks are: Verantwortlicher, Datenschutzbeauftragter, Zwecke und Rechtsgrundlagen, Empfänger und Drittländertransfer, Speicherdauer, Betroffenenrechte, Cookies und localStorage, Keine automatisierten Entscheidungen / kein Profiling, Stand.
- **Rationale**: the 9 blocks are the minimum Art. 13 DSGVO disclosure plus the § 25(2) TDDDG statement required for the `localStorage` key. Order chosen so the visitor reads "who is responsible" first, "what data flows" second, "how long" third, "your rights" fourth, and the regression-prevention statements last.
- **Alternatives considered**:
    - Dynamic consent or preference page (rejected — over-engineering; the assessment recommends against it).
    - Placeholder for future sub-pages (rejected — premature; one page is enough for a static site).
    - Separate GDPR or DSGVO-AG-specific section (rejected — the site's processing is uniform across visitors; no special-category data).

## R4 — MapLibre glyph CDN is disclose-only (FR-002, A-006)

- **Decision**: the new Datenschutzerklärung discloses the `demotiles.maplibre.org` glyph CDN as a third-party recipient (US-origin, IP and User-Agent implicit). Self-hosting is deferred to a follow-up feature.
- **Rationale**: self-hosting the glyphs requires copying ~5-10 MB of font files into `src/site/vendor/` and a CSS-shim or `@font-face` rule change. The assessment classified this as a deferred-hardening item, not a blocker. Disclosure is the minimum Art. 13 obligation. Self-hosting is defense-in-depth that does not change the legal posture.
- **Alternatives considered**:
    - Self-hosting in this feature (rejected — out of scope per the user's "minimal disruption" framing).
    - Removing the `font-src` directive (rejected — would break the map).

## R5 — Template parity (FR-003)

- **Decision**: the new page is a byte-template sibling of `src/site/impressum.html`. Same `<!DOCTYPE html>`, same `<html lang="de">`, same `<meta>` tags, same `<title>` + `<h1>` pattern, same in-line `<style>` block, same `<main>` wrapper, same max-width 40 rem, same dark-mode color scheme, same back-link, same footer. The only differences are the title text, the heading text, and the body content.
- **Rationale**: the three existing info pages (index, impressum, attribution) are visually identical outside the content. Adding a fourth page in a different style would create a visual inconsistency. The existing `<style>` block contains hard-coded color values. A new file would require either a copy of the block or a refactor to a separate CSS file (rejected — breaks the "no new CSS rules" invariant).
- **Alternatives considered**:
    - Refactoring to `src/site/style.css` (rejected — the existing template is in-line; refactoring is a separate feature).
    - Creating a shared template (rejected — no template engine in the project, no build step; the in-line pattern is the project's deliberate choice for a static site).

## R6 — Footer legal-link group is a flat sibling list (FR-004, FR-005)

- **Decision**: the second legal-link `<a>` is added as a sibling of the existing one, separated by a single space. No new wrapper element, no separator dot, no icon, no new CSS class.
- **Rationale**: the existing `<a class="legal-link">` styling renders well as a flat list. Adding a separator would require a new CSS rule or a different DOM structure, which violates the "minimal disruption" framing.
- **Alternatives considered**:
    - A `<nav>` wrapper (rejected — the existing footer has no `<nav>`; introducing one would change the semantic structure).
    - A `<ul><li>` list (rejected — the existing link is a bare `<a>`, not a list).
    - A separator dot via CSS `::before` (rejected — introduces a new CSS rule).

## R7 — Ko-fi `rel` attribute upgrade (FR-006)

- **Decision**: the Ko-fi donation link's `rel` attribute is upgraded from `"noopener"` to `"noopener noreferrer nofollow sponsored"`. The `href`, `target`, `class`, and inner `<img>` are unchanged.
- **Rationale**: `noopener` is the original OWASP recommendation. Adding `noreferrer` strips the `Referer` header on the outgoing request (redundant with the HTTP `Referrer-Policy: strict-origin-when-cross-origin` header but defense-in-depth). `nofollow` tells search engines not to follow the link. `sponsored` is the disambiguating value that signals the link is monetization. The change is a single attribute edit that costs nothing.
- **Alternatives considered**:
    - Using a `rel="noopener external"` (rejected — `external` is not a recognized value and is ignored by browsers).
    - Leaving the link with `noopener` only (rejected — the assessment's P2 item recommends the hardening; no reason to skip).

## R8 — Impressum "Datenschutz" paragraph is a one-line pointer (FR-007)

- **Decision**: the existing multi-sentence "Datenschutz" paragraph in `src/site/impressum.html` is replaced by a single sentence: "Mehr Informationen zum Datenschutz finden Sie in der [Datenschutzerklärung](/datenschutz)."
- **Rationale**: the existing paragraph under-discloses recipients (it mentions only BKG) and contradicts the new Datenschutzerklärung. Reducing it to a one-line pointer keeps the Impressum brief and sends the visitor to the right page.
- **Alternatives considered**:
    - Keeping the paragraph and adding a link at the end (rejected — the paragraph is misleading and would still contradict the new page).
    - Expanding the paragraph to a full statement (rejected — duplicates the new page).

## R9 — sitemap.xml and robots.txt (FR-008, FR-009)

- **Decision**: `src/site/sitemap.xml` is edited to add a `<url>` entry for `datenschutz` with `<lastmod>2026-08-10</lastmod>`. `src/site/robots.txt` is unchanged. It implicitly allows the new page.
- **Rationale**: the sitemap is the canonical "all pages" list for SEO. The robots.txt existing rule disallows the data files (buildings.pmtiles, trees.pmtiles, etc.). The new page is allowed.
- **Alternatives considered**:
    - Skipping the sitemap entry (rejected — SEO regression; the existing three info pages are listed).
    - Editing robots.txt to add a special rule (rejected — unnecessary; the existing rule already allows it).

## R10 — README softening (FR-011)

- **Decision**: the existing README's privacy-related sentence is rewritten to acknowledge that the visitor's IP and User-Agent reach Cloudflare, BKG, and Ko-fi as part of standard HTTP. The new wording links to the Datenschutzerklärung.
- **Rationale**: the existing README reads as a marketing claim of "zero data leaves the browser," which is technically inaccurate (standard HTTP delivers connection data to the operator's edge). The new wording is honest and points to the authoritative disclosure.
- **Alternatives considered**:
    - Removing the privacy claim entirely (rejected — the site is genuinely privacy-by-design; the claim is correct in spirit).
    - Expanding the README to a full privacy section (rejected — the README is the README; the disclosure belongs on a dedicated page).

## R11 — Doc-only update in spec 007 (FR-010)

- **Decision**: `specs/007-first-visit-story/contracts/dismissal-state.md` is updated with a 3-5 sentence paragraph documenting the § 25(2) Nr. 2 TDDDG exemption argument for the `matreecover.story-dismissed` key.
- **Rationale**: the dismissal-state contract is the authoritative description of the storage schema and behavior. The exemption argument belongs in the contract so future maintainers do not accidentally re-introduce a cookie or analytics.
- **Alternatives considered**:
    - Putting the exemption argument in the new Datenschutzerklärung only (rejected — the contract is the source of truth for the storage behavior).
    - Putting it in a separate legal-opinion document (rejected — over-ceremony for a single key).

## R12 — Branch and deploy ordering

- **Decision**: the implementation lands on the current branch `research/dsgvo-cookies-conformity` (which already carries the assessment as `dbb21c4`). The feature directory is `specs/018-dsgvo-disclosure/`. The spec and plan are reviewed and approved before any code change.
- **Rationale**: the user's request was "research the DSGVO and cookies conformity" on the new branch, then "see what needs to be added/changed." The research came first, and the implementation naturally follows on the same branch. The feature slug `018-dsgvo-disclosure` distinguishes the implementation scope from the broader research scope.
- **Alternatives considered**:
    - A separate implementation branch (rejected — adds a round-trip and a merge; the research did not branch away from `ux-improvements`).
    - Landing on `main` directly (rejected — `main` is locked; the project's spec workflow gates all changes through a feature branch).
