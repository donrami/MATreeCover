# Quickstart: DSGVO Disclosure (feature 018)

Validation guide. Run these scenarios in order to prove the feature works end-to-end. Details live in the [contracts](contracts/) and [data model](data-model.md); this file is the run guide, not the implementation.

## Prerequisites

- Branch `research/dsgvo-cookies-conformity` (which carries the spec on `specs/018-dsgvo-disclosure/`), clean worktree.
- `git`, `bash`, `python3.11`, `.venv` with the dev extras (`make bootstrap`), `curl`.
- For S13 (deploy verification): `npx wrangler`, `scripts/deploy-cf.env` (gitignored) or the `MATREECOVER_*` env vars, and access to the live site.

## S1 — Spec and contracts review (US1, FR-001 to FR-014, SC-001 to SC-007)

```text
cat specs/018-dsgvo-disclosure/spec.md
cat specs/018-dsgvo-disclosure/plan.md
cat specs/018-dsgvo-disclosure/research.md
cat specs/018-dsgvo-disclosure/data-model.md
cat specs/018-dsgvo-disclosure/contracts/legal-page-template.md
cat specs/018-dsgvo-disclosure/checklists/requirements.md
```

Expected: all 6 files exist. The spec has 5 user stories and 14 functional requirements. The checklist has all 13 quality items checked off. The data model has 5 entities. The contract has 9 content blocks. The research has 12 decisions (R1–R12).

## S2 — Static-page file check (US1, FR-001, FR-003)

```text
test -f src/site/datenschutz.html && echo "new page exists"
test -f dist-assets/datenschutz.html && echo "new page published"
grep -c '<section>' dist-assets/datenschutz.html
```

Expected: both files exist. The published copy has exactly 9 `<section>` elements (one per content block).

## S3 — Footer legal-link group (US1, FR-004, FR-005)

```text
grep -A1 'class="legal-link"' src/site/index.html
```

Expected: two `<a class="legal-link">` siblings. The first links to `impressum` and the second to `datenschutz`. They are separated by a single whitespace.

## S4 — Ko-fi rel attribute (US4, FR-006)

```text
grep 'kofi' src/site/index.html | grep -oE 'rel="[^"]+"'
```

Expected: the `rel` attribute on the Ko-fi link is exactly `noopener noreferrer nofollow sponsored`.

## S5 — Impressum privacy paragraph (US2, FR-007)

```text
grep -A1 'id="datenschutz"' src/site/impressum.html
```

Expected: the `Datenschutz` section in the Impressum is a single sentence. It ends with a link to `/datenschutz`. The old multi-sentence paragraph (mentioning BKG only) is removed.

## S6 — sitemap.xml (US1, FR-008)

```text
grep 'datenschutz' src/site/sitemap.xml
```

Expected: one `<loc>` entry for `https://abu-hamad.de/map/datenschutz` with `<lastmod>2026-08-10</lastmod>`.

## S7 — robots.txt (US1, FR-009)

```text
grep 'datenschutz' src/site/robots.txt
```

Expected: no entry. The new page is implicitly allowed by the existing `robots.txt` (which only disallows the data files).

## S8 — Spec 007 contract update (US3, FR-010)

```text
grep -A5 'TDDDG\|§ 25' specs/007-first-visit-story/contracts/dismissal-state.md
```

Expected: a 3-5 sentence paragraph documenting the § 25(2) Nr. 2 TDDDG exemption argument for the `matreecover.story-dismissed` key.

## S9 — README softening (US5, FR-011)

```text
grep -i 'datenschutz\|datenschutzerklärung' README.md
```

Expected: a sentence in the README that names Cloudflare, BKG, and Ko-fi as recipients of standard HTTP connection data and links to the new Datenschutzerklärung.

## S10 — Layout gate (FR-003, SC-007)

```text
make check-layout
```

Expected: `clean: N tracked paths, M documented entries` (exit 0). The new `src/site/datenschutz.html` is documented or implicitly covered by the existing template entries.

## S11 — Public hygiene gate (FR-012, SC-004)

```text
make check-public
make check-history
```

Expected: both clean. No new findings in the signed-off scan set.

## S12 — Full regression suite (FR-014, SC-004)

```text
make check-or005
.venv/bin/python -m pytest tests/ -q
```

Expected: `check-or005` clean. All acceptance, pipeline, and endpoint tests pass unchanged. The new feature is added without skipping, modifying, or removing any test.

## S13 — Live deploy verification (FR-014, SC-006)

```text
bash scripts/deploy-cf.sh verify
```

Expected: the existing deploy verification gates pass (DNS, redirects, Range 206, cache headers, cert). Plus the manual checks:

```text
curl -sI https://abu-hamad.de/map/datenschutz | grep -iE 'HTTP/|content-security-policy|x-content-type-options|x-frame-options|referrer-policy|permissions-policy|strict-transport-security'
curl -s https://abu-hamad.de/map/datenschutz | grep -c '<section>'
```

Expected: the new page returns 200 with all security headers byte-identical to the index page. The body contains exactly 9 `<section>` elements. The `<title>` and `<h1>` read "Datenschutzerklärung".

## S14 — No behavioral change in the map (US1, SC-004)

```text
bash scripts/perf-measure.sh https://abu-hamad.de/map/        # interaction latency
node scripts/parity-render.mjs                                 # rendered-output parity
```

Expected: all 8 interactions within the 2 s budget. Rendered building values, colors, labels, and popups identical to the pre-feature bundle. The map is unchanged.

## S15 — localStorage schema unchanged (US3, FR-013, SC-004)

Manual browser check:

```text
1. Open https://abu-hamad.de/map/ in a fresh browser profile.
2. Open DevTools → Application → Local Storage.
3. Dismiss the story modal.
4. Inspect localStorage keys.
```

Expected: `localStorage` contains exactly the key `matreecover.story-dismissed`. No new key is added by this feature.

## Success criteria cross-check

| Criterion | Proven by |
|-----------|-----------|
| SC-001 footer link reachable in one viewport | S3 + curl + browser check |
| SC-002 new page 200 + 9 blocks + keyboard in few tab presses | S2 + S13 + manual |
| SC-003 no JS, no third-party, no CSP violations | S13 + browser DevTools Network |
| SC-004 no behavioral change | S12 + S14 + S15 |
| SC-005 Impressum and Datenschutzerklärung consistent | S5 + S2 |
| SC-006 deploy step same cost as impressum | S13 |
| SC-007 no new UI element beyond the footer link | S3 + visual check |
