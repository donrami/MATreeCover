# Implementation Plan: Ko-fi Donation Button

**Branch**: `017-ko-fi-button` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/017-ko-fi-button/spec.md` (clarified 2026-08-09: footer placement, expanded-only visibility, accessible name "Unterstützen").

## Summary

Add the owner's Ko-fi donation button to the **surface panel/sheet footer**, visible only when the surface is expanded and hidden when collapsed (FR-001; spec `## Clarifications`, session 2026-08-09 — the owner judged the earlier header placement too prominent). The button is a plain external link (no script, no tracking, FR-008) opening `https://ko-fi.com/M4Q624RYOV` in a new tab with `rel="noopener"` (site pattern), rendering the official Ko-fi button image from `https://storage.ko-fi.com/cdn/kofi3.png?v=6` (CDN serves WebP; natural 580×146, standard embed height 36 → ~143 px wide). Its accessible name is exactly "Unterstützen" (FR-006, owner-chosen short German label; `alt="Unterstützen"` on the image).

**Implementation state**: a header-based implementation already landed on this branch — markup in `.surface-header`, header wrap-packing CSS, the CSP image-host extension in all three carriers, acceptance tests, smoke checklist, and the smoke-verify scenario. This plan **relocates** the landed work to the footer and updates the dependent artifacts. The CSP change itself is placement-agnostic and stays as landed (meta tag in `src/site/index.html`, Worker `SECURITY_HEADERS` in `workers/map/index.js`, policy text in the feature-015 contract `specs/015-security-audit-housekeeping/contracts/security-headers.md`; contract-change rule: contract, meta, and header update together — already done, no further policy change). Script/style/connect/worker/font directives stay byte-identical.

**Layout**: CSS-only relocation. The `.ko-fi` anchor moves out of `.surface-header` into a new `<footer class="surface-footer">` as the last child of `.surface-body` (after `.surface-body-inner`). The footer is `position: sticky; bottom: 0`, centered, with `border-top` and the panel background, so it stays visible without scrolling whenever the body is expanded (FR-001), even with tall city-panel content. Collapsed visibility comes for free from the feature-012 collapse machine (`.surface-body` gets `max-height: 0; overflow: hidden` under `#surface.is-collapsed`). The obsolete header-packing CSS is deleted: the `.ko-fi` order overrides in the ≤ 680 px media block and the ≤ 350 px image-shrink block. No image-shrink fallback is needed — the footer has the full body width (292 px available at 320 px vs. a 143 px image). The mobile touch target stays ≥ 44 × 44 px via padding (36 px visual), with `.ko-fi` remaining a member of the feature-012 mobile rule group; spacing to adjacent interactive content (legend-note link) comes from `.surface-body-inner` `gap: 12px` plus footer padding (≥ 8 px, FR-004). Safe areas are inherited from the mobile sheet rule `#surface { padding-bottom: env(safe-area-inset-bottom) }` — verify only, no new code (R-7).

**No JS change**: `main.js` expands the surface by default on desktop (≥ 768 px), keeps it collapsed by default on mobile, and `syncPadding` measures `surface.offsetHeight` for popup clearance, so the footer height is picked up automatically.

**Storage**: static bundle. No new local files — the button image is external CDN, so `src/pipeline/publish.py` and the `STATIC_FILES` hashed-bundle contract (feature 014) are untouched. Button markup lives in unhashed `index.html`, styles in hashed `style.css`.

**Testing**: pytest suites (`tests/acceptance`, `tests/pipeline`, `tests/endpoint`); update `tests/acceptance/test_ko_fi.py` (footer position instead of header DOM order, exact `alt="Unterstützen"`, absence of the deleted header rules, CSP lockstep assertions unchanged); update `tests/frontend/smoke_ko_fi.md`; extend the ko-fi scenario in `scripts/smoke-verify.mjs` (footer visibility at 768/1280/1920, collapsed-hidden assertion); governance gates `make check-public` / `check-layout` / `check-or005` / `check-history`; perf harness `scripts/perf-measure.sh` + `perf-probe.mjs`; parity `scripts/parity-render.mjs`.

**Target Platform**: static bundle served by the Cloudflare Worker at `https://abu-hamad.de/map/`. Desktop ≥ 768 px (top-left panel, expanded by default); mobile < 768 px (fixed bottom sheet, collapsed by default); floor 320 px (SC-001 widths 320, 375, 768, 1280, 1920).

**Project Type**: web (static frontend + Cloudflare Worker + offline Python pipeline).

**Performance Goals**: unchanged budgets (feature 014, SC-008) — 8 interactions ≤ 2 s, desktop interaction median ≤ 123 ms, first usable ≤ 10 s. The button is static HTML/CSS plus one non-blocking external image: nothing on the interaction path, no new render-blocking resources, no preconnect (single small image; minimal request surface per FR-008). `width`/`height` attributes reserve layout space (no CLS).

**Constraints**:

- CSP locked (feature 015): only `img-src` gains `https://storage.ko-fi.com` — already landed in all three carriers, byte-identical (R-2). No script/connect/style/worker/font change, ever.
- Feature-012 layout invariants: collapsed sheet ≤ 20 % viewport height (map ≥ 80 %), chevron rightmost in the header, touch targets ≥ 44 × 44 px. The footer is hidden in the collapsed state, so the collapsed strip is untouched; the header DOM order stays title → tools → toggle.
- No JS change (main.js surface logic already covers the footer).
- External-link safety: `target="_blank" rel="noopener"` (existing site pattern).
- Language consistency: accessible name "Unterstützen" (German, owner-chosen); the visible brand image keeps Ko-fi's standard English visual (brand label, spec Edge Cases).
- Ko-fi unavailability: the site stays fully functional — plain link + non-blocking image (R-9).
- No tracking, analytics, or third-party script (FR-008).

**Scale/Scope**: relocate 1 existing element into a new footer element, delete 2 obsolete CSS rule groups, add 1 `.surface-footer` rule group, update 1 acceptance module, 1 smoke checklist, 1 headless-smoke scenario, 2 contract docs (ko-fi-button.md rewritten; csp-image-host.md unchanged), 1 CHANGELOG entry. `tasks.md` is stale (header-based) and must be regenerated in the implementation phase.

## Constitution Check

*GATE: before Phase 0 research. Re-check Phase 1 design.* The repository ships no standalone constitution file; the governing rules are the constraints documented in DEVELOPMENT.md (OR-001…OR-005, FR-001, FR-008/FR-010, FR-013, SC-005/SC-008 precedent), established in features 014/015/016.

| Gate | Status | Evidence |
|------|--------|----------|
| OR-001 (pipeline peak RSS < 12 GiB) | PASS | No pipeline compute change. Button static HTML/CSS + external image; `publish.py` untouched. |
| OR-003 (no local GPU) | PASS | No model work anywhere. |
| OR-004 (one commit per accepted spec/plan/slice) | PASS | Plan committed via `make commit-plan`; implementation lands in slices with their own commits. |
| OR-005 (no `*.tif` / `*.pmtiles` / > 50 MiB geojson tracked) | PASS | New tracked files: HTML/CSS edits, one test module, one checklist, docs. `data/` stays gitignored. |
| FR-001 (no analytics, no application server) | PASS | Button is a plain external link `<a><img>`; zero scripts, zero tracking (FR-008 spec). |
| FR-010/FR-003 (015: `check-public` clean) | PASS | Ko-fi profile URL and CDN host are public marketing assets; no personal paths, credentials, or internal references added. Gate must stay green. |
| FR-009/FR-011 (015: CSP lockstep) | PASS | The `img-src` extension is already landed byte-identically in the meta tag, the Worker header, and the feature-015 contract. This plan adds no further policy change (R-2). |
| SC-005/SC-008 (014: interaction budgets + visual parity) | PASS | No interaction-path code change; perf harness + parity render re-run prove identical map rendering. |
| FR-013 (012: map experience unchanged) | PASS* | Map values, colors, labels, popups, interactions untouched. The surface body gains one footer element — the feature's intent. 012 layout invariants (≤ 20 % strip, ≥ 80 % map, chevron rightmost, touch targets) are re-verified via the extended overlap matrix and the 320×568 height check in quickstart; the collapsed strip carries no donation chrome. |

*The footer element and the already-landed CSP image-host addition are scoped to the feature's intent (FR-009 / FR-001…FR-007), not regressions; every other locked surface stays byte-identical.

Re-check Phase 1 design: all gates still PASS; no violations. Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/017-ko-fi-button/
├── plan.md                  # plan command output (this file, footer revision)
├── research.md              # Phase 0: decisions R-1…R-9, grounded evidence (footer revision)
├── data-model.md            # Phase 1: entities, invariants, states (footer revision)
├── quickstart.md            # Phase 1: validation scenarios Q1–Q9 (footer revision)
├── contracts/               # Phase 1: interface contracts
│   ├── README.md            # contract index (ko-fi-button scope line updated)
│   ├── ko-fi-button.md      # FR-001…008: markup, footer layout, hit area, focus (rewritten)
│   └── csp-image-host.md    # FR-009: image-host-only CSP extension (unchanged, already landed)
└── tasks.md                 # Phase 2 output (NOT created by plan command; stale header version — regenerate in implementation)
```

### Source Code (repository root)

```text
src/site/
├── index.html               # MOVE <a class="ko-fi">…</a> out of .surface-header into
│                            #   <footer class="surface-footer"> as last child of
│                            #   .surface-body; alt="Unterstützen"; CSP meta img-src
│                            #   already includes https://storage.ko-fi.com (no change)
└── style.css                # ADD .surface-footer rules (sticky bottom, centered,
                             #   border-top, panel-bg); keep .ko-fi base/focus rules and
                             #   touch-target group membership; DELETE .ko-fi order
                             #   overrides (<= 680 px block) and <= 350 px image-shrink block
workers/map/index.js         # CSP already extended (no change this revision)
specs/015-security-audit-housekeeping/contracts/
└── security-headers.md      # policy text already updated (no change this revision)
tests/acceptance/
└── test_ko_fi.py            # UPDATE: footer position assertions (anchor inside
                             #   .surface-footer, last child of .surface-body, none in
                             #   .surface-header), exact alt="Unterstützen", deleted-rule
                             #   absence; CSP lockstep tests unchanged
tests/frontend/
└── smoke_ko_fi.md           # UPDATE: footer placement, collapsed-hidden, "Unterstützen"
scripts/
├── smoke-verify.mjs         # UPDATE ko-fi scenario: footer visibility at 768/1280/1920,
│                            #   collapsed-hidden assertion, new-tab click unchanged
└── (all gates unchanged)
CHANGELOG.md                 # + release log entry (final phase)
```

**Structure Decision**: single flat project (static frontend + worker + pipeline + gates), no new top-level directories, no new packages, no manifest change — same decision as features 014/015/016. The updated test module stays in `tests/acceptance/`; the checklist stays in `tests/frontend/`; the feature-015 contract file is already updated. All paths are already documented in DEVELOPMENT.md's layout section, so `check-layout` needs no manifest change.

## Complexity Tracking

No constitution violations. No complexity justification needed.
