# Research: Security Audit & Repo Housekeeping (feature 015)

Phase 0 output. Every NEEDS CLARIFICATION from the plan and every open question in the spec is resolved here with a decision, rationale, and alternatives.

## R1 — Secret pattern additions (FR-001, FR-003, SC-007)

- **Decision**: extend `check-public.sh` from 19 to ~31 patterns by adding P20–P31, sourced from the well-established gitleaks rule set ([gitleaks config](https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml)) and the repo's actual infrastructure (Cloudflare, R2/AWS-compatible, GitHub, RunPod/SSH).
- **Rationale**: the repo's deploy surface uses Cloudflare (zone id already covered by P9, but API tokens/keys are not), AWS-compatible R2 (only `AKIA` key ids covered, not secret keys or temp session keys), and GitHub. The audit must cover every credential class that could plausibly be committed.
- **Alternatives considered**: vendoring gitleaks itself (rejected — new heavyweight dependency, requires Go binary in a no-build repo; the existing self-maintained pattern approach keeps the gate dependency-free and reviewable); a generic high-entropy string scanner (rejected — false positives on the 282 KB artifact manifest and hashed filenames).

New patterns (full regexes live in `scripts/public-patterns.txt`; contracts quote only IDs + rationale to stay scan-clean):

| ID | Class | Rationale |
|----|-------|-----------|
| P20 | GitHub fine-grained PAT `github_pat_` | Same class as P6 (classic PAT) |
| P21 | Cloudflare API token (assignment form) | 40-char base62 bare tokens would false-positive on hashes; require `CLOUDFLARE/CF … TOKEN/KEY =` assignment |
| P22 | Cloudflare `X-Auth-Email` / `X-Auth-Key` header form | Legacy API auth header |
| P23 | AWS secret access key (`aws … secret/access … "…40 chars…"`) | Complements P8 key-id |
| P24 | AWS temp session key `ASIA` prefix | Same class as P8 |
| P25 | npm token `npm_` | Registry credential |
| P26 | Slack token / webhook `xox[baprs]-`, `hooks.slack.com/services/` | Team chat credential |
| P27 | Stripe live key `sk_live_` | Payment credential |
| P28 | Google API key `AIza` | Cloud credential |
| P29 | PGP private key block | Complements P5 (SSH/RSA/EC only today) |
| P30 | PuTTY key `PuTTY-User-Key-File` | Complements P5 |
| P31 | `.netrc`-style `machine … login … password` | Git/curl credential file marker |
| P32 | `Desktop/…` path fragment | Personal machine layout (after DEVELOPMENT.md rewording, see R10) |

- **P9 drift fix**: the script's `zone_id` regex and the 006 contract table have already drifted. Moving all regexes to one shared file removes the class of bug where contract and gate disagree.

## R2 — Single source of truth for patterns (FR-003)

- **Decision**: extract all patterns into `scripts/public-patterns.txt` (one ERE per line, `# P# — rationale` comment blocks). `check-public.sh` reads it; the new `check-git-history.sh` reads it; the contract documents IDs and rationale without quoting regexes.
- **Rationale**: FR-003 requires gate and contract to change together and stay in sync; a shared file makes "gate extended" and "contract updated" the same edit. Keeping regexes out of markdown contracts means the contract files themselves need no hygiene exemption.
- **Alternatives considered**: patterns in a markdown table parsed by the gate (rejected — fragile parsing, and quoting literals forces exemptions); duplicating the array in two scripts (rejected — drift, exactly the P9 bug class).
- **Exemption set becomes**: `.gitignore`, `scripts/check-public.sh`, `scripts/public-patterns.txt`. The 006 contract stops quoting literals and loses its exemption (contract change, same commit).

## R3 — Git history scan (FR-001, FR-011, SC-001)

- **Decision**: new gate `scripts/check-git-history.sh`. For each commit in `git rev-list --all` (89 commits), run `git grep -nIE '<all patterns as alternation>' <commit>`; also scan commit messages via `git log --all --format='%H%x00%s%x00%b'`. Any finding must appear in `scripts/history-exemptions.tsv` (`pattern-id \t commit \t path`); unexempted findings fail the gate.
- **Rationale**: full-tree scan per commit finds any secret in any historical version of any file — the definition of "never live" evidence. The committed exemptions ledger makes the gate reproducible and enforces forward prevention: a future commit that adds a secret fails until a dispositioned exemption row exists. History rewriting stays out of scope (spec assumption).
- **Alternatives considered**: `git log -p` diff scanning (rejected — misses secrets that were committed and later reverted, and re-scans unchanged lines); `git rev-list --objects --all` + blob content scan (rejected — git grep is simpler and already available); gitleaks `--log-opts` (rejected — external dependency, R1).
- **Cost**: 89 commits × one `git grep` (single process per commit, ~31-pattern alternation over ~272 files) — estimated under 60 s. Acceptable as a make target and a pytest test.
- **Semantics**: exit 0 = "clean: N commits scanned, M exempted findings, 0 open". Output lists every finding line `commit:path:line:match` and every exemption applied. No network access.

## R4 — Security headers on the Worker (FR-004)

- **Decision**: apply the canonical Cloudflare Workers header set ([security-headers example](https://developers.cloudflare.com/workers/examples/security-headers)) to **every** Worker response — static assets, R2 passthroughs (200 and 206), and 404s — via an `applySecurityHeaders(headers)` helper that only ever sets/overrides the security keys:

  | Header | Value | Note |
  |--------|-------|------|
  | `X-Content-Type-Options` | `nosniff` | all responses |
  | `X-Frame-Options` | `DENY` | page is never embedded |
  | `Referrer-Policy` | `strict-origin-when-cross-origin` | HTTPS-only site |
  | `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()` | privacy additive |
  | `Strict-Transport-Security` | `max-age=31536000` | no `includeSubDomains`/`preload` — apex also serves blog/email subdomains; keep HSTS scoped to the map host |
  | `X-XSS-Protection` | `0` | legacy filter is deprecated; `0` disables its interference |
  | `Content-Security-Policy` | identical to the committed meta tag | header + meta both apply (intersection); keeping them identical avoids a stricter-than-intended policy |

- **Rationale**: the Worker is the only internet-facing code (US2); today only `Cache-Control` is set and only on hashed assets. Headers on R2 responses are the explicit gap the spec calls out. `strict-origin-when-cross-origin` is the modern default and never leaks path on cross-origin requests (MapLibre fetches tiles cross-origin — the tile requests already carry no referrer value beyond origin, unchanged behavior).
- **Alternatives considered**: Cloudflare dashboard transform rules (rejected — not in the repo, not versioned, violates "committed gates"); `_headers` file for static assets (rejected — Cloudflare's `_headers` applies to assets only, not R2 passthroughs, and the worker already owns responses); COEP/COOP (rejected — COEP `require-corp` would require CORP headers on the third-party basemap and font origins we do not control, which would break the map: a regression; COOP adds nothing for a frame-less static page); HSTS with `preload` (rejected — subdomain blast radius, R4 table).
- **Regression guard**: header helper runs after the R2 branch builds its response; it must not touch `Content-Range`, `ETag`, `Accept-Ranges`, or `Content-Length`. Range 206 re-verified in quickstart S6 and by the existing `deploy-cf.sh verify` Range gate.
- **CSP source of truth**: `src/site/index.html` meta tag stays authoritative (it is the committed policy that the browser already enforces); the Worker header mirrors it. Policy keeps `sgx.geodatenzentrum.de` (basemap), `demotiles.maplibre.org` (glyphs, see R8), `data:`/`blob:` (PMTiles worker), and `style-src 'unsafe-inline'` (feature 014 inlined styles) — no tightening that could break the map.

## R5 — R2 data surface (FR-005)

- **Decision**: the `DATA_KEYS` whitelist (3 keys) is the access boundary and stays. Review adds two verifications, no worker change: (a) R2 bucket public access must be OFF (dashboard setting — access only via the Worker binding); (b) `deploy-cf.sh verify` gains an assertion that a non-data key under `/map/` returns 404 (ASSETS `not_found_handling = "none"` already yields 404) and the three declared keys return 206 on Range requests.
- **Rationale**: FR-005 requires proof that only the three declared keys are reachable; a 404 assertion on unknown keys turns the whitelist into an observable contract.
- **Alternatives considered**: listing all bucket objects in the gate (rejected — requires R2 admin credentials in CI; the Worker binding is the enforcement point and is code-reviewed).

## R6 — Deploy scripts secret handling (FR-006)

- **Decision**: review result — PASS with two documented notes and one small fix.
  - `deploy-cf.sh`: sources `scripts/deploy-cf.env` (gitignored), uses `MATREECOVER_*` env vars with neutral defaults, no `set -x`, no secret echoed. The DNS values it prints in `verify-dns` are public DNS records, not credentials. No change needed.
  - `runpod-deploy.sh`: takes an SSH key *path* (never content), prints tunnel commands with the path, pod-side `server.log` never leaves the pod. PASS.
  - Fix (low): pod dependency install uses unpinned `pip install segmentation-models-pytorch rasterio`. Pin the resolved versions in the script so the supply chain is reproducible; recorded in the audit report.
- **Rationale**: the spec asks to review and fix gaps; the only real gap is dependency pinning on the pod.
- **Alternatives considered**: pinning via a pod-side `requirements.txt` (rejected — one-line pin in the script is the minimal change; a new file would need a sync rule).

## R7 — Endpoint trust model (FR-007)

- **Decision**: document the trust model in `contracts/endpoint-trust-model.md` and fix two findings:
  - **HIGH — binds `0.0.0.0`**: if the RunPod pod's network allows inbound port 8000, `/infer` is publicly reachable without authentication. The SSH tunnel (`-L 8000:localhost:8000`) targets the pod's own localhost, so binding `127.0.0.1` is sufficient and strictly safer. Fix: default bind `127.0.0.1`, env `BIND_ADDR` override for deliberate pod-internal exposure.
  - **MEDIUM — no request-size cap**: `self.rfile.read(Content-Length)` trusts the client. Fix: reject `Content-Length > 1 MiB` with 413 before reading; non-numeric length already falls into the 400 path.
  - LOW (document, no code change): the `inputs` request field is accepted but unused — inference always processes the whole `TILE_ROOT`. The contract documents this.
- **Documented accepted risks**: no authentication on `/infer` (single-owner, SSH-tunnel-only exposure once bound to loopback; token auth would add key management for no threat-model gain); inference holds a global lock and can run for hours (serialized by design; owner-only); model and weights are owner-supplied (trusted input); logs go to stderr on the pod only.
- **Rationale**: OR-003 fixes the exposure path at the source (bind) instead of adding auth at a boundary that should not exist.
- **Alternatives considered**: token auth on `/infer` (rejected — over-engineering for a loopback-only service; R7 accepted-risk record); firewall documentation only (rejected — code-level fix is stronger and testable).

## R8 — Vendored library provenance (FR-008)

- **Decision**: commit `src/site/vendor/PROVENANCE.md` with name, version, license, source URL, and sha256 for `maplibre-gl.js`, `maplibre-gl.css` (MapLibre GL JS 5.7.1, BSD-3-Clause, github.com/maplibre/maplibre-gl-js) and `pmtiles.js` (pmtiles 4.4.0, BSD-3-Clause, github.com/protomaps/PMTiles). Hashes computed from the tracked files at implementation time; the record is updated when the files change (rule documented in the contract and DEVELOPMENT.md).
- **Declared runtime dependencies** (part of the record): the LGL basemap tiles (`sgx.geodatenzentrum.de`, already attributed, dl-de/by-2-0) and the glyph/font origin `demotiles.maplibre.org` (MapLibre's public demo CDN, used by the committed `style.json` `glyphs` URL).
- **Finding**: `demotiles.maplibre.org` is a third-party demo origin — availability and supply-chain risk, and DEVELOPMENT.md's "no other third-party scripts are used" claim is inaccurate. Disposition: **accepted risk** (MEDIUM, owner sign-off) — GET-only requests, no data leaves the page, CSP already restricts to fonts; vendoring the glyphs is a possible follow-up that would require a render-parity check (out of scope for the audit, which must not change the bundle).
- **Alternatives considered**: vendoring the fonts now (rejected — changes the bundle and network behavior, needs re-render parity; out of the "no bundle change" constraint); recording only the two JS libs (rejected — the runtime dependency declaration is the point of FR-008).
- **Hash pinning**: record sha256 as evidence, not as a blocker — the contract states the record is updated on vendor updates (spec edge case).

## R9 — Layout gate (FR-009, FR-011, SC-003)

- **Decision**: new gate `scripts/check-layout.sh` + committed manifest `scripts/layout-manifest.tsv` (TAB-separated `tracked-path \t documentation-reference`), one row per top-level tracked entry. Semantics:
  - every `git ls-files` path must start with a manifest row (or be a listed root-level file);
  - every manifest row must exist in the current tracked tree (no dead doc entries);
  - no tracked file may sit at the repo root outside the documented root set.
  - exit 0/1 with one `path → documentation-reference` mismatch line per failure.
- **Rationale**: the spec requires the layout to be *machine-checkable* and the gate to be committed (documentation-only rules are explicitly insufficient). A TSV manifest is the boring, stable machine form; the DEVELOPMENT.md "What is in this repository" section is the human form. Sync rule: changing the layout section without updating the manifest fails the gate, and vice versa — the manifest is authoritative for the gate, the section must name it.
- **Alternatives considered**: parsing DEVELOPMENT.md headings in the gate (rejected — markdown parsing is fragile and breaks on any prose edit); `.gitattributes`/`.gitignore`-style patterns (rejected — cannot express "documented reference" provenance); a generated manifest with a doc-generation script (rejected — generation adds a build step to a no-build repo).
- **After housekeeping (R10) the root set is**: `.gitignore`, `CHANGELOG.md`, `DEVELOPMENT.md`, `LICENSE`, `Makefile`, `README.md`, `pyproject.toml`, `artifacts.manifest.json`, `tiles.csv`, `screenshot/`, plus the ten top-level directories.

## R10 — Housekeeping moves and dispositions (FR-009, FR-010)

All moves are `git mv` (history preserved, references checked; none of the moved files are referenced by code — verified by grep):

| Path | Action | Disposition / reason |
|------|--------|----------------------|
| `cited.md` (root) | `git mv` → `outputs/cited.md` | DEVELOPMENT.md already describes the verified source list as living in `outputs/`; this aligns tree with docs. Update the two DEVELOPMENT.md references. |
| `notes/s2_abstracts.json`, `notes/s2_abstracts2.json` | `git mv` → `outputs/` | Semantic-Scholar abstracts are literature-review evidence; `outputs/` is the documented lit-review home. Empty `notes/` disappears with git. |
| `info` (WebP 1024×640, no extension) | owner decision, recommended `git mv` → `outputs/info.webp` | Undocumented binary media with no code references and undetermined content at plan time; recorded in the audit report for owner sign-off (move / rename / delete). Never silently deleted. |
| `progress.md` (72 B boilerplate template) | owner decision, recommended delete (documented) | Empty scaffold ("Status / Tasks / Files Changed / Notes" with no content); no references. Disposition recorded; deletion happens only with owner sign-off in the audit report. |
| `screenshot/` | keep, document | README references `screenshot/map.png`; the layout section gains the entry. |
| `outputs/.plans/` | keep, document | Internal planning drafts; layout entry added. |
| root docs (`README.md`, `LICENSE`, `Makefile`, `pyproject.toml`, `.gitignore`, `CHANGELOG.md`, `artifacts.manifest.json`, `tiles.csv`) | keep, enumerate | Layout section must name every root-level file (SC-003); `artifacts.manifest.json` and `tiles.csv` already documented, the rest gain entries. |

- **Docs updates (FR-010)**: DEVELOPMENT.md (layout section enumerates every root file; governance section documents `check-history` + `check-layout`; lit-review references point at `outputs/cited.md`; "no other third-party scripts" claim corrected to declare the font origin; vendored section references PROVENANCE.md), CHANGELOG.md (2026-08-08 security-audit entry), feature-history table (015 row), README.md (no content change required — verified accurate; optional security link).
- **Large-file interaction (OR-005)**: all moved files are small text/media; no `*.tif`/`*.pmtiles`/`>50 MiB` enters the tracked set. `data/`, `dist/`, `.omp/` remain gitignored; `check-prereqs.sh` paths untouched.
- **Alternatives considered**: keeping strays at root with doc entries (rejected — duplicates the `cited.md` documentation-vs-reality mismatch the audit exists to fix); deleting `info`/`progress.md` outright without owner decision (rejected — spec edge case forbids deletion on assumption).

## R11 — Audit report location and shape (FR-002, FR-012, SC-006)

- **Decision**: `verification/security-audit-2026-08-08.md`. Structure: scope; method (tools, commands, pattern list reference); findings table (ID, severity, location, description, disposition: remediated / never-live / accepted risk with reason + owner sign-off); housekeeping decisions table; gate summary; how to re-run every check.
- **Rationale**: `verification/` is the repo's documented evidence home (tree-detection reports live there); the report is a permanent, reviewable artifact a stranger can verify dispositions against (SC-006). Keeps the root clean and the layout gate simple.
- **Alternatives considered**: root-level `SECURITY.md` (rejected — a new root file for one report; the layout gate would then document it, but `verification/` already exists for evidence); `specs/015/` (rejected — the report outlives the feature and belongs with evidence, not process docs).

## R12 — Deploy verification extension (US2, FR-004/005)

- **Decision**: `deploy-cf.sh verify` gains: (a) security-header assertions on `/map/` (index) and on a 206 range response from an R2 key; (b) 404 assertion for an unknown data key. Contract updates: `specs/005-host-on-personal-domain/contracts/hosting-config.md` §3 gains the header checks; the 015 `security-headers.md` contract is the reference.
- **Rationale**: the acceptance scenario for US2 explicitly allows "run existing deploy-cf.sh verify gates against the review's response-header assertions" — extending `verify` makes the header contract machine-checked at deploy time.
- **Alternatives considered**: staging Worker deploy (rejected — the existing verify gates run against the live deploy; header checks are additive and non-destructive).

## Open questions resolved

| Question | Resolution |
|----------|------------|
| `info` file content / home | Owner decision at implementation; recommended `outputs/info.webp` (R10). |
| `progress.md` | Owner decision; recommended documented deletion (R10). |
| `demotiles.maplibre.org` fonts | Accepted risk, declared runtime dependency (R8). |
| R2 public-access toggle | Dashboard verification step in quickstart S6; code-level whitelist unchanged (R5). |
| Pod dependency versions | Pinned at implementation from the pod's resolved versions (R6). |
