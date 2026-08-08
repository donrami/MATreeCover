# Quickstart: Security Audit & Repo Housekeeping (feature 015)

Validation guide. Run these scenarios in order to prove the feature works end-to-end. Details live in the [contracts](contracts/) and [data model](data-model.md); this file is the run guide, not the implementation.

## Prerequisites

- Branch `015-security-audit-housekeeping`, clean worktree.
- `git`, `bash`, `python3.11`, `.venv` with the dev extras (`make bootstrap`), `curl`.
- For S5/S6 (deploy verification): `npx wrangler`, `scripts/deploy-cf.env` (gitignored) or the `MATREECOVER_*` env vars, and access to the live site.
- For S8 (perf/parity): `node`, a Chromium build (`CHROME_PATH`).

## S1 — Hygiene gate extended and self-testing (US1, FR-003, SC-007)

```text
make check-public
.venv/bin/python -m pytest tests/acceptance/test_public_hygiene.py -q
```

Expected: `clean: N tracked files scanned` (exit 0), and the pytest test green. The test writes a temp file containing each pattern P1–P32 and asserts the gate fails with that file and pattern named. A pattern that stops matching fails the test (SC-007).

## S2 — Full git history scan (US1, FR-001/002, SC-001)

```text
make check-history
```

Expected: `clean: 89 commits scanned, M exempted findings, 0 open` (exit 0). Every exempted finding resolves to a dispositioned row in `verification/security-audit-2026-08-08.md` (SC-001/SC-006). Negative check: temporarily add a synthetic secret to a file and commit — the gate must fail naming commit, file, pattern, and line. Revert and amend.

## S3 — Layout gate (US3, FR-009/011, SC-003)

```text
make check-layout
```

Expected: `clean: N tracked paths, M documented entries` (exit 0). Spot-check: every file listed under `outputs/` (including `cited.md`, `s2_abstracts*.json`, `.plans/`) resolves in DEVELOPMENT.md's layout section; root contains exactly the manifest's root set; `info`/`progress.md`/`notes/` are gone with dispositions recorded in the audit report.

## S4 — Full regression suite (US4, FR-014)

```text
make check-or005
.venv/bin/python -m pytest tests/ -q
```

Expected: `check-or005` clean; all acceptance, pipeline, and endpoint tests pass, including the new `test_layout.py`, `test_secret_scan.py`, `test_public_hygiene.py`, `test_bind.py`, `test_request_size.py`. Any test that references a moved file path proves the housekeeping pass updated its references.

## S5 — Endpoint trust model (US2, FR-007)

```text
.venv/bin/python -m pytest tests/endpoint/ -q
```

Expected: threshold tests still pass; `test_bind.py` asserts the default bind is `127.0.0.1` and `BIND_ADDR` overrides it; `test_request_size.py` asserts `Content-Length > 1 MiB` → 413 before any body read. The trust model in [endpoint-trust-model.md](contracts/endpoint-trust-model.md) matches `server.py`.

## S6 — Deployed surface review (US2, FR-004/005)

Requires a deploy of the reviewed Worker, or the live deploy after the header change:

```text
bash scripts/deploy-cf.sh verify
```

Expected: the existing FR-013 gates pass (DNS, redirects, Range 206, cache headers, cert) plus the new assertions: security headers present on `/map/` (index) and on a 206 range response from an R2 key; unknown data-looking key returns 404. Manual checks:

```text
curl -sI https://abu-hamad.de/map/ | grep -iE 'content-security-policy|x-content-type-options|x-frame-options|referrer-policy|permissions-policy|strict-transport-security'
curl -s -H 'Range: bytes=0-1023' -o /dev/null -D - https://abu-hamad.de/map/buildings.pmtiles | grep -iE 'HTTP/|content-range|content-type-options'
```

Expected: every header present with the values in [security-headers.md](contracts/security-headers.md); 206 with correct `Content-Range` and `nosniff`; the CSP header byte-identical to the meta tag in `src/site/index.html`. Map loads in a browser: basemap tiles, fonts, tree toggle, and popups all work (CSP did not tighten anything away). R2 dashboard: bucket public access is OFF.

## S7 — Supply chain and housekeeping docs (FR-008/009/010)

```text
git diff --stat
.venv/bin/python -m pytest tests/acceptance/test_layout.py tests/acceptance/test_manifest.py -q
```

Expected: `src/site/vendor/PROVENANCE.md` records both libraries with sha256 matching `sha256sum src/site/vendor/*.js src/site/vendor/*.css`; the demotiles font origin is declared as an accepted risk; DEVELOPMENT.md, README.md, CHANGELOG.md and the feature-history table describe the current tree (layout, gates `check-history`/`check-layout`, moved files); CHANGELOG has the 2026-08-08 security-audit entry.

## S8 — No user-visible regression (US4, FR-013, SC-005)

```text
bash scripts/perf-measure.sh https://abu-hamad.de/map/        # interaction latency harness
node scripts/parity-render.mjs                                 # rendered-output parity vs current bundle
```

Expected: all 8 interactions within the 2 s budget, desktop median ≤ 123 ms, first usable ≤ 10 s (SC-008); rendered building values, colors, labels, and popups identical to the pre-audit bundle (SC-005). Acceptance criteria FR-013: map values, colors, labels, popups, interactions, and caching semantics unchanged — the audit changed headers, gates, and file locations only.

## Success criteria cross-check

| Criterion | Proven by |
|-----------|-----------|
| SC-001 zero open secret findings | S1 + S2 |
| SC-002 high-severity findings remediated | S5 + S6 + audit report |
| SC-003 100% tracked files documented | S3 |
| SC-004 all tests and gates pass | S1–S4 |
| SC-005 map unchanged | S8 |
| SC-006 report verifiable by a stranger | S2 + audit report cross-reference |
| SC-007 gate catches every new pattern | S1 synthetic test |
