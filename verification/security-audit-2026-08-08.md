# Security Audit Report — 2026-08-08

**Feature**: 015-security-audit-housekeeping
**Date**: 2026-08-08
**Branch**: `015-security-audit-housekeeping`
**Audit type**: repository and code review (scanning, static inspection, verification against existing gates and harness). Not penetration testing of third-party services (Cloudflare, RunPod, LGL) and no GitHub account settings changes.
**Status**: complete — all slices implemented and verified (2026-08-08)

## Scope

What was audited:

- Secrets and credentials: all tracked files and the full git history (89 commits) scanned for credential patterns, personal paths, and private key material.
- Deployed surface: Cloudflare Worker (`workers/map/index.js`), R2 data surface (3 keys), deploy scripts (`scripts/deploy-cf.sh`, `scripts/runpod-deploy.sh`), RunPod endpoint (`src/endpoint/server.py`).
- Supply chain: vendored frontend libraries (`src/site/vendor/`) and declared runtime dependencies.
- Repository layout: tracked tree vs. documented layout, root-level strays, duplicates.
- Documentation accuracy: README.md, DEVELOPMENT.md, CHANGELOG.md, spec index.

Out of scope: git-history rewriting (forward prevention only), GitHub repository settings, penetration testing of third-party services, any change to map content/values/colors/labels/popups/interactions, field monitoring or analytics.

## Method

- Pattern source: `scripts/public-patterns.txt` (P1–P32), shared by `scripts/check-public.sh` (tracked files) and `scripts/check-git-history.sh` (full history).
- History scan: `git rev-list --all` (89 commits) × `git grep -nIE '<alternation>' <commit>` plus commit-message scan.
- Dispositions: every finding classified `remediated` / `never-live` / `accepted-risk` (FR-002).
- Deployed surface: static review of Worker routing/headers, R2 key whitelist, deploy-script secret handling, endpoint input validation.
- Regression: full pytest suite, all governance gates, deploy verification gates, interaction-latency harness, rendered-output parity (SC-004/SC-005).

### Baseline (pre-audit state)

| Check | Result | Evidence |
|-------|--------|----------|
| `pytest tests/ -q` | 144 passed (58 s) | T004 |
| `make check-public` | clean: 282 tracked files scanned (1 initial finding in `specs/015-security-audit-housekeeping/plan.md` — harness-tool name reference, dispositioned never-live by rewording the doc; no exemption added) | T004 |
| `make check-or005` | OK — every >50 MiB workspace file recorded in manifest | T004 |

## Findings

| ID | Severity | Location | Description | Disposition |
|----|----------|----------|-------------|-------------|
| F1 | low | historical files: specs/001 docs, src/pipeline/workspace.py, tests/conftest.py, Makefile, README, outputs/, cited.md (988 exemption rows) | Owner's local workspace path (Linux home + desktop fragments, P1/P32): the mannheim workspace was referenced by its absolute path on the owner's machine in early feature-001 documents and code defaults | never-live — local workspace layout, never published and never reachable from any live service; scrubbed from tracked files in feature 006; the current tree uses the repo-local archive path (verified by the clean tracked-file scan) |
| F2 | low | historical README.md (SSH tunnel command), old gate/contract files (402 rows) | SSH key path/filename and root-login references (P3/P4/P13) plus the PuTTY marker (P30): a documented tunnel setup command used a placeholder host with the owner's local key path; the gate's own historical versions quoted the literals | never-live — placeholder host only, owner's local key path, removed from tracked files in feature 006; the current tracked tree quotes none of these literals (verified clean) |
| F3 | low | historical .gitignore, scripts/, specs/ (812 rows) | Harness-internal directory and workflow-command references (P10/P11/P12) in historical planning documents and gitignore comments | never-live — internal tooling names, not credentials; the tracked tree is clean and the gitignore remains the documented exemption for the tracked scan |
| F4 | low | historical outputs/, cited.md, specs/, scripts/ (401 rows) | Harness product and tool names (P14–P19: product names, local URI scheme, search-tool names, delegated-agent label) in historical output documents and the gate's own pattern tables | never-live — internal tooling vocabulary scrubbed from tracked files; not credentials |
| F5 | low | commit messages 5fea58c, d3961b5, ddc76ce, e9f4f08 (8 rows) | Commit messages describing the feature-014 scrubbing work quote harness tool names (P10/P11/P14/P15/P17/P18/P19) | never-live — messages describe the cleanup itself; no credential content |
| F6 | medium | historical `workers/map/wrangler.toml` (4 commits: 030f3632, 14b6a654, 2df934c1, ca13a454) | A real Cloudflare zone id (P9) was committed in the redirect rules of early Worker configs; the current `wrangler.toml` carries the angle-bracket placeholder (scrubbed in feature 006) | accepted-risk — a zone id is an identifier, not an authentication credential; exposure in history enables no access without API tokens; rotation would require recreating the zone and breaks the live site, so the id remains in use for the owner's zone. Owner sign-off: 2026-08-08 (feature plan approval) |

No credential pattern (P6–P8, P20–P28) has any occurrence in the full history; no live secret was found, so nothing required rotation.

| F7 | high | `src/endpoint/server.py` | Endpoint bound `0.0.0.0` by default: on a RunPod pod with inbound port exposure, `/infer` would be publicly reachable without authentication | remediated — default bind is now loopback (`127.0.0.1`) with a `BIND_ADDR` override for deliberate pod-internal access; SSH-tunnel workflow unchanged; covered by `tests/endpoint/test_bind.py` |
| F8 | medium | `src/endpoint/server.py` | No request-size cap: `Content-Length` was trusted and the body read in full | remediated — bodies over 1 MiB rejected with 413 before any read; non-numeric lengths 400; covered by `tests/endpoint/test_request_size.py` |
| F9 | low | `scripts/runpod-deploy.sh` | Pod dependency install used unpinned `pip install segmentation-models-pytorch rasterio` | remediated — pinned to `segmentation-models-pytorch==0.3.4`, `rasterio==1.4.4` (matching the local reference environment) |
| F10 | medium | `workers/map/index.js` | Security headers and CSP were absent from every Worker response; the CSP existed only as the meta tag and was not documented as a contract | remediated — `applySecurityHeaders()` sets the documented 7-header set on every response (assets, R2 200/206, 404s, redirects); the CSP header mirrors the meta tag byte-for-byte; contract `contracts/security-headers.md`; verified by `deploy-cf.sh verify` assertions |

## Housekeeping decisions

| Path | Action | Destination / reason | Owner sign-off |
|------|--------|----------------------|----------------|
| `cited.md` (root) | moved | `outputs/cited.md` — the layout section already documented the verified source list under `outputs/`; the two DEVELOPMENT.md references updated | 2026-08-08 (feature plan approval) |
| `notes/s2_abstracts.json`, `notes/s2_abstracts2.json` | moved | `outputs/` — Semantic-Scholar abstract pulls are literature-review evidence; empty `notes/` disappeared with git; the provenance-doc reference updated | 2026-08-08 (feature plan approval) |
| `info` (WebP 1024×640, no extension) | moved | `outputs/info.webp` — undocumented binary media with no code references; extension added on move | 2026-08-08 (feature plan approval) |
| `progress.md` (72-byte boilerplate template) | deleted | No content (empty Status/Tasks/Files-Changed/Notes scaffold), no references; deletion recorded, not silent | 2026-08-08 (feature plan approval) |
| `screenshot/` | kept, documented | README references `screenshot/map.png`; layout section + manifest gained the entry | 2026-08-08 (feature plan approval) |
| `outputs/.plans/` | kept, documented | Internal planning drafts; layout section + manifest cover `outputs/` | 2026-08-08 (feature plan approval) |
| root docs (`.gitignore`, `CHANGELOG.md`, `DEVELOPMENT.md`, `LICENSE`, `Makefile`, `README.md`, `pyproject.toml`, `artifacts.manifest.json`, `tiles.csv`) | kept, enumerated | Layout section now names every root-level file (SC-003) | 2026-08-08 (feature plan approval) |

## Accepted risks

| Risk | Severity | Reason | Owner sign-off |
|------|----------|--------|----------------|
| No authentication on `/infer` | low | Loopback-only after the bind fix; single owner; token auth would add key management for no threat-model gain | 2026-08-08 (feature plan approval) |
| Inference runs for hours, serialized by a global lock | low | Owner-only workload; parallelism would multiply GPU memory | 2026-08-08 (feature plan approval) |

## Gate summary

| Gate | Result |
|------|--------|
| `check-public` | clean: 293 tracked files scanned (P1–P32, shared pattern file) |
| `check-history` | clean: 93 commits scanned, 2030 exempted findings, 0 open (F1–F6 dispositions) |
| `check-layout` | clean: 296 tracked paths, 18 documented entries |
| `check-or005` | OK — no tif/pmtiles/oversized files tracked; gitignored dirs untouched |
| pytest suites | 156 passed (acceptance, pipeline, endpoint) |
| `deploy-cf.sh verify` | FR-013 gates PASS (DNS, redirects, Range 206, cache headers, cert, unknown-key 404). Security-header assertions FAIL against the live pre-audit Worker — the reviewed Worker is committed but not yet deployed (owner-gated Cloudflare deploy); the assertions demonstrably detect the missing headers. Worker header logic proven locally on all response types (200/206/404/301) with Content-Range preserved |
| perf harness | cold LCP 2328 ms (< 10 s budget); interaction medians 13–14 ms (≤ 2 s / ≤ 123 ms budgets) |
| parity harness | renders clean: 12886 buildings initial view; bundle inputs byte-identical to pre-audit (only PROVENANCE.md added) |

## How to re-run every check

- Tracked-file secret scan: `make check-public`
- Full-history secret scan: `make check-history`
- Layout gate: `make check-layout`
- Large-file gate: `make check-or005`
- Test suites: `.venv/bin/python -m pytest tests/ -q`
- Deploy verification: `bash scripts/deploy-cf.sh verify`
- Quickstart scenarios S1–S8: follow `specs/015-security-audit-housekeeping/quickstart.md`
