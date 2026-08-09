# Implementation Plan: Ko-fi Donation Button

**Branch**: `017-ko-fi-button` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/017-ko-fi-button/spec.md`

## Summary

Add the owner's Ko-fi donation button to the surface header, visible at every supported viewport width (≥ 320 px) in both collapsed and expanded surface states — desktop panel header, mobile collapsed bottom-sheet header (owner-confirmed placement, spec Assumptions). The button is a plain external link (no script, no tracking, FR-008) opening `https://ko-fi.com/M4Q624RYOV` in a new tab with `rel="noopener"` (site pattern), rendering the official Ko-fi button image from `https://storage.ko-fi.com/cdn/kofi3.png?v=6` (CDN serves WebP; natural 580×146, standard embed height 36 → ~143 px wide).

The locked CSP gains exactly one image host (`https://storage.ko-fi.com` in `img-src`), updated together in all three places that carry the policy: the `<meta>` tag in `src/site/index.html`, the Worker `SECURITY_HEADERS` in `workers/map/index.js`, and the policy text in the feature-015 contract `specs/015-security-audit-housekeeping/contracts/security-headers.md` (contract-change rule: update contract, meta, and header together). Script/style/connect/worker/font directives stay byte-identical.

Layout is CSS-only inside the existing header: the link becomes a direct child of `.surface-header` (DOM order title → tools → ko-fi → toggle, so the chevron stays rightmost per feature 012), participating in the existing wrap layout with hard invariants: at most 2 header rows, collapsed strip ≤ 20 % viewport height (map ≥ 80 %), mobile touch target ≥ 44×44 px with ≥ 8 px spacing (joins the existing touch-target rule group), no horizontal overflow. The no-overlap matrix (feature 004 technique, extended per 012/013/016) gains the button rect at widths 320, 375, 768, 1280, 1920 px × both surface states.

Deliverables: (1) header button + CSP image-host extension; (2) new acceptance module `tests/acceptance/test_ko_fi.py`; (3) new manual checklist `tests/frontend/smoke_ko_fi.md` + ko-fi scenario in the headless smoke (`scripts/smoke-verify.mjs`); (4) updated feature-015 security-headers contract; (5) perf harness + parity re-run as regression evidence (SC-007). No new static files: `publish.py`, `layout-manifest.tsv`, and the hashed-bundle contract are untouched.

## Technical Context

**Language/Version**: HTML/CSS/vanilla JS frontend (no build tool), Python 3.11 offline pipeline (untouched), Cloudflare Worker (`workers/map/index.js`).

**Primary Dependencies**: none new. Ko-fi image from `https://storage.ko-fi.com/cdn/kofi3.png?v=6` (official embed URL, `?v=6` cache-buster kept verbatim; CDN serves WebP regardless of the `.png` name — covered by `img-src`). The Ko-fi widget script (`ko-fi.com/widgets/widget_2.js`) is NOT used — plain `<a><img>` only (FR-008).

**Storage**: static bundle. NO new local files: the button image is external CDN, so `src/pipeline/publish.py` `STATIC_FILES` and the hashed-bundle contract (feature 014) are untouched. Button markup lives in unhashed `index.html` (revalidating), styles in hashed `style.css`.

**Testing**: pytest suites (`tests/acceptance`, `tests/pipeline`, `tests/endpoint`); new `tests/acceptance/test_ko_fi.py` (markup + CSP + style assertions, mirroring `test_seo_metadata.py` conventions); governance gates `make check-public` / `check-layout` / `check-or005` / `check-history`; perf harness `scripts/perf-measure.sh` + `perf-probe.mjs`; parity `scripts/parity-render.mjs`; headless smoke `scripts/smoke-verify.mjs` (gains a ko-fi scenario); manual checklist `tests/frontend/smoke_ko_fi.md` (new).

**Target Platform**: static bundle served by Cloudflare Worker at `https://abu-hamad.de/map/`. Desktop ≥ 768 px (top-left panel, expanded by default); mobile < 768 px (fixed bottom sheet, collapsed by default); floor 320 px (SC-001 widths 320, 375, 768, 1280, 1920).

**Project Type**: web (static frontend + Cloudflare Worker + offline Python pipeline).

**Performance Goals**: unchanged budgets (feature 014, SC-008) — 8 interactions ≤ 2 s, desktop interaction median ≤ 123 ms, first usable ≤ 10 s. The button is static HTML/CSS plus one non-blocking external image: nothing on the interaction path, no new render-blocking resources, no preconnect (single small image; minimal request surface per FR-008). `width`/`height` attributes reserve layout space (no CLS).

**Constraints**:
- CSP locked (feature 015): only `img-src` gains `https://storage.ko-fi.com`; `script-src`, `style-src`, `connect-src`, `worker-src`, `font-src` stay byte-identical. Meta tag and Worker header are byte-identical (both apply, intersection — feature-015 contract); both change together with the contract doc.
- Feature-012 layout invariants: collapsed header ≤ 20 % viewport height (map ≥ 80 %), touch targets ≥ 44×44 px with ≥ 8 px spacing, expand/collapse chevron stays the rightmost header element, safe-area insets respected (`.surface-header` already pads `max(8px, env(safe-area-inset-bottom))`).
- 320 px floor: header wraps to at most 2 rows; no horizontal overflow; no overlap with any existing control (Bäume toggle, brightness slider, surface toggle, zoom control, attribution, Impressum link, legend) in either surface state.
- FR-008: no tracking, analytics, or third-party script — plain external link; no `onerror` handler (inline handlers are CSP-blocked anyway; alt text is the fallback).
- External-link safety: `target="_blank" rel="noopener"` (existing site pattern in `index.html`).
- Language consistency: German alt text (FR-006); the brand visual label ("Support me on Ko-fi") stays as provided (spec Assumptions).
- Ko-fi unavailability: site stays fully functional — plain link + non-blocking image.

**Scale/Scope**: 1 new header element, 3 locked-CSP locations updated in lockstep, 1 new acceptance module, 1 new smoke checklist, 1 headless-smoke scenario, 1 contract doc update, 1 CHANGELOG entry.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The repository ships no standalone constitution file; governing rules are the documented constraints in DEVELOPMENT.md (OR-001…OR-005, FR-001, FR-008/FR-010, FR-013, SC-005/SC-008 precedent), established in features 014/015/016.

| Gate | Status | Evidence |
|------|--------|----------|
| OR-001 (pipeline peak RSS < 12 GiB) | PASS | No pipeline compute change. Button is static HTML/CSS + external image; `publish.py` untouched. |
| OR-003 (no local GPU) | PASS | No model work anywhere. |
| OR-004 (one commit per accepted spec/plan/slice) | PASS | Plan committed via `make commit-plan`; implementation lands in slices with own commits. |
| OR-005 (no `*.tif` / `*.pmtiles` / > 50 MiB geojson tracked) | PASS | New tracked files: HTML/CSS/JS edits, one test module, one checklist, docs. `data/` stays gitignored. |
| FR-001 (no analytics, no application server) | PASS | Button is a plain external link with an `<img>`; zero scripts, zero tracking (FR-008 of this spec). |
| FR-010/FR-003 (015: `check-public` clean) | PASS | Ko-fi profile URL and CDN host are public marketing assets; no personal paths, credentials, or internal references added. Gate must stay green. |
| FR-009/FR-011 (015: `check-layout`) | PASS | All new files land in already-documented locations (`src/site/`, `workers/map/`, `tests/acceptance/`, `tests/frontend/`, `specs/017-ko-fi-button/`, `specs/015-…/contracts/`); no new top-level entries, manifest unchanged. |
| CSP (015, locked) | PASS* | The only policy change is the scoped image-host allowance (FR-009 of this spec): `img-src` += `https://storage.ko-fi.com`. All other directives byte-identical. Meta tag, Worker header, and the feature-015 contract update together (contract-change rule). Existing gates only assert header presence and `script-src 'self'` (verified by grep) — none pins the full string. |
| SC-005/SC-008 (014: interaction budgets + visual parity) | PASS | No interaction-path code change; perf harness + parity render re-run prove budgets and identical map rendering. |
| FR-013 (012: map experience unchanged) | PASS* | Map values, colors, labels, popups, interactions untouched. The header gains one additive element — the feature's intent. 012 layout invariants (≤ 20 % strip, ≥ 80 % map, chevron rightmost, touch targets) are re-verified via the extended overlap matrix and the 320×568 height check in quickstart. |

*The CSP image-host addition and the new header element are the scoped intent of this feature (FR-009 / FR-001-007), not regressions; every other locked surface stays byte-identical.

Re-check after Phase 1 design: all gates still PASS; no violations. Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/017-ko-fi-button/
├── plan.md              # this file (plan command output)
├── research.md          # Phase 0: decisions R-1…R-9, grounded evidence
├── data-model.md        # Phase 1: entities, invariants, states
├── quickstart.md        # Phase 1: validation scenarios Q1–Q9
├── contracts/           # Phase 1: interface contracts
│   ├── README.md
│   ├── ko-fi-button.md      # FR-001…007: header element contract (markup, hit area, focus, wrap rules)
│   └── csp-image-host.md    # FR-009: image-host-only CSP extension, three-location lockstep
└── tasks.md             # Phase 2 output (NOT created by the plan command)
```

### Source Code (repository root)

```text
src/site/
├── index.html           # + <a class="ko-fi" …><img …></a> in .surface-header (after
│                        #   .surface-tools, before .surface-toggle); CSP meta img-src
│                        #   += https://storage.ko-fi.com (byte-identical to Worker header)
└── style.css            # + .ko-fi link styles: inline-flex, brand image, focus-visible
                         #   indicator (existing pattern), mobile hit-area >= 44x44 via
                         #   padding, wrap-safe placement in the 012 header layout
                         #   (<= 2 rows, <= 20 % strip at 320 px)

workers/map/index.js     # SECURITY_HEADERS CSP string += https://storage.ko-fi.com
                         #   (byte-identical to the meta tag, feature-015 contract)

specs/015-security-audit-housekeeping/contracts/
└── security-headers.md  # policy text updated (contract-change rule: contract + meta +
                         #   header together), img-src row in the required allowlist

tests/acceptance/
└── test_ko_fi.py        # NEW: ko-fi anchor (href/target/rel/alt), img (src/width/height),
                         #   CSP img-src extension + locked directives, style rule group
                         #   membership, mobile hit-area CSS present

tests/frontend/
└── smoke_ko_fi.md       # NEW: manual browser checklist (US1–US4, edge cases)

scripts/
├── smoke-verify.mjs     # + ko-fi scenario: visible in header, click opens new tab
│                        #   (noopener), map page still open
└── (all gates unchanged)

CHANGELOG.md             # + release log entry (final phase)
```

**Structure Decision**: single flat project (static frontend + worker + pipeline + gates), no new top-level directories, no new packages, no manifest change — same decision as features 014/015/016. The new test module joins `tests/acceptance/` next to the other surface gates; the checklist joins `tests/frontend/`; the contract update touches the existing feature-015 contract file (no new contract file there). All paths are already documented in DEVELOPMENT.md's layout section, so `check-layout` needs no manifest change.

## Complexity Tracking

No constitution violations. No complexity justification needed.
