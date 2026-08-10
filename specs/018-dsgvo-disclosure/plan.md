# Implementation Plan: DSGVO Disclosure (Datenschutzerklärung)

**Branch**: `research/dsgvo-cookies-conformity` (research) → feature slug `018-dsgvo-disclosure` | **Date**: 2026-08-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/018-dsgvo-disclosure/spec.md`

**Builds on**: `validation/dsgvo-assessment-2026-08-10.md` (commit `dbb21c4` on `research/dsgvo-cookies-conformity`) — the Phase 0 research deliverable. This plan is the Phase 1 design; the assessment is the research.

## Summary

Add a single static German Datenschutzerklärung page at `https://abu-hamad.de/map/datenschutz`, link it from the existing Impressum footer and from the Impressum privacy paragraph, harden the existing Ko-fi donation link `rel` attribute, soften the README's privacy claim, and document the § 25(2) Nr. 2 TDDDG exemption for the single `localStorage` key. No new JavaScript, no new CSS, no CSP change, no new external hosts, no new behavior. The site remains tracking-free.

Technical approach: hand-author the new page in the same in-line-styled template as `src/site/impressum.html` and `src/site/attribution.html`. Add the page to the existing `dist-assets/` build output (no script change). Update the two existing templates (the footer template and the Impressum privacy paragraph) and the sitemap. No new tests are added; the existing test suite, gate chain, and deploy verification (`scripts/deploy-cf.sh verify`) continue to run and stay green.

## Technical Context

- **Language/Version**: HTML5 (German), CSS3 (in-line, no preprocessor). No JavaScript added by this feature. Existing `src/site/main.js` is not touched.
- **Primary Dependencies**: none added. Existing: vendored MapLibre GL JS 5.7.1, vendored pmtiles 4.4.0, Cloudflare Worker runtime.
- **Storage**: none added. Existing: `localStorage["matreecover.story-dismissed"]` (story-modal dismissal). Schema and behavior unchanged.
- **Testing**: existing project test suite — acceptance (`tests/acceptance/`), endpoint (`tests/endpoint/`), pipeline (`tests/pipeline/`). Layout-overlap matrix (`scripts/layout-manifest.tsv` + `make check-layout`), public-hygiene (`make check-public`), commit-checks (`make check-history`), CSP byte-equality test (HTML `<meta>` vs Worker response header), and the deploy verification (`scripts/deploy-cf.sh verify`) all run unchanged.
- **Target Platform**: Cloudflare Worker + R2 + static assets, same as the rest of the site. Browser target: modern (the existing site targets MapLibre 5.7.1 which requires a WebGL2-capable browser); the new page is plain HTML5 and works on any browser that opens the existing info pages.
- **Project Type**: web (static + Worker).
- **Performance Goals**: the new page is a sub-1 KB HTML document with no scripts, no fonts, no images. LCP under 1 s on a 3G connection. No regression of existing performance budgets (`validation/perf-budget.json`).
- **Constraints**: no behavioral change; no new scripts; no new external hosts; no CSP change; no cookie banner; no consent flow; no new CSS rules; no new wrapper element. The single new file is a same-template sibling of the existing three info pages.
- **Scale/Scope**: 1 new HTML file (~120 lines), 1 new footer link, 1 attribute change (Ko-fi `rel`), 1 paragraph replacement in Impressum, 1 sitemap entry, 1 doc-only update in `specs/007-first-visit-story/contracts/dismissal-state.md`, 1 README paragraph softened.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No `.specify/memory/constitution.md` file exists in this repo. The Constitution Check is vacuous as a literal gate, but the project's implicit invariants (derived from the 17 prior features and the housekeeping pass) are enforced by the existing gates and by the explicit FR-012 requirement that no behavioral change ships. The invariants:

1. **Privacy-by-design** — no new tracking, no new cookies, no new analytics, no new fingerprinting surface. The site is tracking-free and stays tracking-free.
2. **No CSP or security-header change** — the existing CSP `<meta>` tag and the Worker's `Content-Security-Policy` response header are byte-identical and remain byte-identical. The CSP byte-equality test stays green.
3. **Visual parity** — the new page follows the same template (same dark-mode color scheme, same `<style>` block, same back-link, same `<title>` + `<h1>` pattern, same `<main>` wrapper, same max-width 40 rem) as the existing three info pages. The layout-overlap matrix stays green.
4. **Test parity** — the full project test suite passes unchanged. No test is skipped, modified, or added spuriously.
5. **Map lock** — the mapping features (010, 012, 014, 016, 017) state that values, colors, labels, popups, and interactions must not change. This feature changes one `<a>` in the footer and one Ko-fi `rel` attribute; both are visual edits that a visitor will not see except on direct inspection, and they do not affect the map.
6. **No new dependencies** — no new tech, no new vendor, no new library. The new file is plain HTML.
7. **Documented in the deploy record** — the existing deploy record (`validation/deploy-*.json`) includes the new file in the manifest; the deploy verification (`scripts/deploy-cf.sh verify`) passes.

All 7 invariants are respected by the FR-001 to FR-014 set. No violation.

## Project Structure

### Documentation (this feature)

```text
specs/018-dsgvo-disclosure/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── legal-page-template.md
├── checklists/          # requirements.md (generated by /speckit.specify)
├── spec.md              # the feature specification
└── tasks.md             # Phase 2 output (created by /speckit.tasks, NOT by /speckit.plan)
```

### Source Code (repository root)

No new source directory. The change touches six existing files:

```text
src/site/
├── datenschutz.html     # NEW — German Datenschutzerklärung page
├── index.html           # EDIT — footer legal-link group + Ko-fi rel
├── impressum.html       # EDIT — privacy paragraph → one-sentence pointer
├── sitemap.xml          # EDIT — add datenschutz URL
└── (no other files)

README.md                # EDIT — soften privacy claim, name recipients

specs/007-first-visit-story/contracts/
└── dismissal-state.md   # EDIT — add § 25(2) Nr. 2 TDDDG exemption argument
```

**Structure Decision**: Single project. The site is a static+Worker layout; the new content fits within `src/site/` and the existing templates. No new packages, no new build pipeline, no new test files.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

The Constitution Check has no violations. No cost-rising alternatives are introduced:

- **No new build step**: the existing `dist-assets/` step that copies `src/site/*.html` to the publish directory already handles the new file.
- **No new test**: the existing test suite covers the new file through the layout-overlap matrix (the page is a same-template sibling of `impressum.html` and `attribution.html`, so the layout gate verifies it) and the public-hygiene gate (no new scanned patterns).
- **No new acceptance scripts**: the deploy verification `scripts/deploy-cf.sh verify` already verifies the `/map/` route; the new `/datenschutz` route is automatically picked up by the same asset-serving check.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
