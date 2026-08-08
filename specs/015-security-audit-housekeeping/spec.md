# Feature Specification: Security Audit & Repo Housekeeping

**Feature Branch**: `main`
**Created**: 2026-08-08
**Status**: Draft
**Input**: User description: "we need to security audit and housekeep/organize the repo without regressions"

## Scope

### Goal

Audit the repository's security posture and reorganize it so the tracked tree and documentation match reality — with zero regressions. No map behavior, value, color, or interaction changes. Every existing test, gate, and deploy step keeps passing.

### Current State (evidence)

- The repo is a public, MIT-licensed GitHub project serving a live static map at `https://abu-hamad.de/map/`. No application server, no database, no analytics (FR-001 of feature 001).
- The deployed surface is: a Cloudflare Worker (`workers/map/index.js`, `wrangler.toml`) serving the static bundle from an assets binding and streaming `buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson` from R2 with HTTP Range (206) passthrough; the DNS/email/blog continuity gates in `scripts/deploy-cf.sh`; and the RunPod inference endpoint (`src/endpoint/server.py`) that is reachable only over an SSH tunnel and never runs locally (OR-003).
- Secrets hygiene is partially enforced today: `scripts/check-public.sh` (FR-010) scans all tracked files for 19 patterns (personal home paths, SSH key references and private-key material, GitHub/OpenAI/AWS credentials, real Cloudflare zone ids, harness-internal references). `.gitignore` excludes `.env*`, `*.pem`, `*.key`, `*.crt`, `*.p12`, `*.jks`, `*.secret.*`, and `scripts/deploy-cf.env`. The committed `wrangler.toml` carries a `<your-zone-id>` placeholder. Git history has never been scanned for secrets.
- The Worker serves hashed assets with immutable caching and the HTML with revalidation (feature 014). A content security policy exists but is not documented as a reviewed contract; no audit has checked whether security headers (content-type sniffing, framing, referrer) are set on all responses including R2 passthroughs.
- The tracked tree is 276+ files across `src/`, `scripts/`, `workers/`, `specs/` (001–014), `tests/`, `validation/`, `verification/`, `outputs/`, `notes/`, `data/`, plus 11 root-level files. `DEVELOPMENT.md` documents a layout; `info` (15.8 KB), `progress.md`, `cited.md`, and `notes/s2_abstracts*.json` sit at or near the root without a documented home, and `cited.md` also appears under `outputs/` per the DEVELOPMENT.md text. No committed gate verifies the layout matches the documentation.
- Vendored frontend libraries are pinned by version (MapLibre GL JS 5.7.1, pmtiles 4.4.0) with license notes in DEVELOPMENT.md, but there is no committed provenance/integrity record.
- Git status is clean; all current content is committed.

### In Scope

- Secrets and credentials audit: scan all tracked files and the full git history for credential patterns, personal paths, and infra secrets; extend `check-public.sh` with any new patterns; remediate or document every finding.
- Deployed-surface security review: Worker response headers and CSP across static assets and R2 passthroughs, R2/asset access model, deploy-script secret handling and shell hardening, endpoint trust model and input validation. Fix high-risk findings; document accepted risks.
- Supply-chain hygiene: committed provenance record for vendored libraries (version, license, source); verify no undeclared runtime dependencies.
- Housekeeping: make the tracked tree match a documented layout; consolidate or relocate stray/duplicate root-level files; ensure README, DEVELOPMENT.md, CHANGELOG, and the spec index are accurate.
- A committed security audit report recording findings, severity, and disposition.
- New additive enforcement so the audited state persists (extended hygiene gate and/or a layout gate).
- Regression verification: full test suite, all governance gates, deploy verification gates, and proof the live map is unchanged.

### Out Scope

- Rewriting git history. Default is forward prevention plus rotation of any live secret found; history rewriting happens only if a live secret was actually exposed and the owner approves.
- Changes to GitHub repository settings (branch protection, collaborators). The audit documents recommendations only.
- Penetration testing of third-party services (Cloudflare, RunPod, LGL basemap). The audit covers the repository and the code it deploys.
- Any change to map content, values, colors, labels, popups, or interactions. The bundle and data files are touched only by unrelated future features.
- Field monitoring or analytics (FR-001: no tracking).

## User Scenarios & Testing

### User Story 1 - The Repository Contains No Secrets (Priority: P1)

The maintainer can prove — from a committed scan, not a promise — that no credential, personal path, or private key material exists anywhere in the repository's tracked files or git history. Anything that is found is either remediated (rotated if it was live) or documented as an accepted risk with a recorded reason.

**Why priority**: the repo is public and the deploy scripts carry real infrastructure (R2, Cloudflare, RunPod). A leaked credential is the highest-impact failure mode this audit can prevent. It also makes the existing FR-010 gate trustworthy.

**Independent Test**: Run the extended `make check-public` plus a full git-history secret scan. The scan reports zero findings, and the audit report lists every pattern checked, every historical hit and its disposition (rotated / never live / accepted risk).

**Acceptance Scenarios**:
1. **Given** the full tracked file set, **When** scanned with every credential pattern the audit identifies, **Then** zero findings remain, or each finding is recorded in the audit report with a disposition (rotated, never-live, or accepted risk with owner sign-off).
2. **Given** the full git history, **When** scanned for the same patterns, **Then** every historical hit is enumerated in the audit report with a disposition; no live secret remains usable.
3. **Given** any credential or personal path that appears in tracked files, **When** the FR-010 gate runs, **Then** it fails with the file and pattern named (the gate catches it).
4. **Given** a new pattern discovered during the audit, **When** the gate is extended, **Then** the gate script and its contract document are updated together and the gate stays green on the current tree.

### User Story 2 - The Deployed Surface Is Reviewed and Hardened (Priority: P1)

The maintainer knows what the Worker, R2, deploy scripts, and the RunPod endpoint expose, and the high-risk gaps are closed. The site keeps working exactly as before.

**Why priority**: the Worker is the only internet-facing code in the project. Response headers, cache behavior, and data access are the boundary between the public and the owner's infrastructure.

**Independent Test**: Deploy the reviewed Worker to a staging environment (or run the existing `deploy-cf.sh verify` gates against the review's response-header assertions), exercise a map load, an R2 range request, and the continuity gates, and confirm the audit report's high-severity findings are closed.

**Acceptance Scenarios**:
1. **Given** any response from the Worker (asset or R2 passthrough), **When** inspected, **Then** the response carries the documented security headers and the content security policy; the policy does not block the map's basemap, fonts, or inline styles.
2. **Given** a data request, **When** served from R2, **Then** only the three declared data keys are reachable and Range passthrough still returns correct 206 responses.
3. **Given** the deploy scripts, **When** reviewed, **Then** no secret is written to any committed or logged artifact, and shell handling follows the repo's hardening conventions.
4. **Given** the RunPod endpoint code, **When** reviewed, **Then** its trust model is documented (SSH-tunnel-only exposure, input validation behavior) and any high-risk gap is fixed.
5. **Given** the audit findings, **When** sorted by severity, **Then** every high-severity finding is remediated and every accepted risk is recorded with a reason, in the committed audit report.

### User Story 3 - The Repository Layout Matches Its Documentation (Priority: P2)

A new contributor (or the maintainer in six months) can find any file by reading `DEVELOPMENT.md`'s layout section. Root-level strays and duplicates are consolidated or explicitly documented; nothing meaningful is deleted.

**Why priority**: the repo has grown to 14 features and 276+ tracked files. Layout drift costs time and hides dead or duplicate content; the audit is the right moment to settle it.

**Independent Test**: Diff the tracked file tree against `DEVELOPMENT.md`'s "What is in this repository" section. Every tracked file resolves to a documented directory or a documented root-level file, and the README/CHANGELOG/spec index agree with reality.

**Acceptance Scenarios**:
1. **Given** the tracked file set, **When** compared against the documented layout, **Then** every file is in a documented location; the layout section names every root-level file and directory.
2. **Given** files without a documented home (`info`, `progress.md`, `cited.md`, `notes/`, and any duplicates), **When** the housekeeping pass runs, **Then** each is relocated into a documented directory, merged with an existing home, or kept at root with an explicit documented reason — never silently deleted.
3. **Given** the documentation, **When** checked for accuracy, **Then** README.md, DEVELOPMENT.md, CHANGELOG.md, and the spec index describe the current state (commands, paths, feature history).
4. **Given** the reorganized tree, **When** all commands run, **Then** every Makefile target, script path, and import referenced in the docs still resolves (no breakage from moves).

### User Story 4 - Nothing Regresses (Priority: P2)

The maintainer ships the audit knowing the map is byte-for-byte the same experience and every gate still passes.

**Why priority**: the user explicitly requires the audit and housekeeping "without regressions". This story makes that requirement testable and protects the live site.

**Independent Test**: Run the full pytest suite, `make check-public`, `make check-or005`, the acceptance suite, and the deploy verification gates; then drive the published site with the interaction harness and compare rendered output for parity.

**Acceptance Scenarios**:
1. **Given** the audited tree, **When** the full test suite runs, **Then** every existing test passes (acceptance, pipeline, endpoint).
2. **Given** the audited tree, **When** the governance gates run, **Then** `check-public`, `check-or005`, and the commit checks all pass.
3. **Given** a deploy, **When** the FR-013/FR-014 verification gates run, **Then** redirects, Range 206, cache headers, cert, DNS, and email continuity checks pass.
4. **Given** the published site, **When** the interaction latency harness runs, **Then** all 8 interactions stay within the 2 s budget and the desktop median stays at or below 123 ms.
5. **Given** the published map, **When** compared for visual and data parity, **Then** building values, colors, labels, and popups are identical to the current bundle.

### Edge Cases

- **Secret in git history**: history rewriting is destructive and out of scope by default. If the scan finds a live credential in history, the disposition is rotation (and optionally owner-approved history rewrite), not silent deletion.
- **Gate exemption creep**: every new `check-public` pattern may need an exempt file. Exemptions must stay in sync with the contract document; an exemption that hides a real leak is a finding.
- **CSP tightening breaks the map**: the policy must keep allowing the basemap origin (`sgx.geodatenzentrum.de`), `data:`/`blob:` where used, and the inline styles feature 014 relies on. Any tightening is verified against a live map load before deploy.
- **Security headers on R2 passthroughs**: adding headers must not corrupt Content-Range or the 206 response; re-verify range requests after any header change.
- **Housekeeping moves break references**: Makefile targets, `deploy-cf.sh` paths, imports, and spec contracts reference files by path. A layout gate and the full test suite catch breakage before commit.
- **Root-level file purpose is unknown** (`info`, `progress.md`): do not delete on assumption. Relocate with an owner decision recorded in the audit report, or keep and document.
- **Duplicate documentation** (`cited.md` at root vs under `outputs/`): consolidate to one canonical location and cross-link, rather than maintaining two copies that can drift.
- **Vendored library integrity**: provenance is recorded as version + license + source URL; an upstream hash can be recorded if retrievable, but the record itself must not block future library updates.
- **Large-file gate interaction**: any housekeeping move must not pull `*.tif`, `*.pmtiles`, or > 50 MiB files into the tracked set (`check-or005` must stay green).
- **Local-only files**: `data/`, `dist/`, `dist-assets/`, `.venv/`, `.omp/` are gitignored; housekeeping must not track them or break the workspace path assumptions in `check-prereqs.sh`.

## Requirements

### Functional Requirements

- **FR-001**: The repository MUST be scanned — tracked files and full git history — for credential patterns, personal paths, and private key material. The scan MUST cover at least the patterns already in `check-public.sh` plus any new patterns the audit identifies.
- **FR-002**: Every secret-scan finding MUST have a recorded disposition in the committed audit report: remediated (rotated if the secret was or is live), never-live (safe to ignore, with evidence), or accepted risk (with owner sign-off and reason).
- **FR-003**: The FR-010 public-hygiene gate MUST be extended with every new pattern the audit adds, and the gate's contract document MUST be updated in the same change. The gate MUST stay green on the audited tree.
- **FR-004**: Every response served by the Worker — static assets and R2 data passthroughs — MUST be reviewed for security headers and a content security policy, and the resulting policy MUST be documented as a reviewed contract.
- **FR-005**: The R2 data surface MUST expose only the three declared data keys (`buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson`), with Range (206) passthrough preserved.
- **FR-006**: The deploy scripts MUST NOT write secrets into committed, logged, or deployable artifacts; their secret handling and shell hardening MUST be reviewed and any gaps fixed.
- **FR-007**: The RunPod endpoint's trust model MUST be documented (exposure path, input validation, what runs with what privileges), and any high-risk gap found in review MUST be fixed.
- **FR-008**: Vendored frontend libraries MUST have a committed provenance record (name, version, license, source) that matches the actual vendored files; no undeclared runtime dependency MAY be introduced.
- **FR-009**: Every tracked file MUST live in a location documented by `DEVELOPMENT.md`'s layout section; root-level files MUST each be documented or relocated; duplicates MUST be consolidated to one canonical location.
- **FR-010**: README.md, DEVELOPMENT.md, CHANGELOG.md, and the spec index MUST accurately describe the current repository (layout, commands, feature history) after the housekeeping pass.
- **FR-011**: The audited state MUST be enforced by committed gates: the extended `check-public` and, where the layout is machine-checkable, a layout gate. Documentation-only rules are not sufficient.
- **FR-012**: A security audit report MUST be committed, recording scope, method, findings with severity, dispositions, and the accepted-risk list.
- **FR-013**: All existing behavior MUST remain unchanged: map values, colors, labels, popups, interactions, caching semantics, and the static architecture (no analytics, no server, no database).
- **FR-014**: All existing tests and gates MUST pass after the change: pytest suites (acceptance, pipeline, endpoint), `check-public`, `check-or005`, commit checks, and the FR-013/FR-014 deploy verification gates.

### Key Entities

- **Secret inventory**: every credential pattern, where it appears (tracked files, history), and its disposition. Recorded in the audit report.
- **Deployed surface**: the Worker (headers, CSP, routing), the R2 bucket (keys, access, object metadata), the domain/DNS, and the RunPod endpoint. The reviewed boundary between public traffic and owner infrastructure.
- **Tracked file tree**: the 276+ tracked files and directories; the subject of the layout gate and the housekeeping pass.
- **Governance gates**: `check-public.sh` (FR-010), `check_or005.py` (OR-005), `commit-check.sh`, `check-prereqs.sh`. The enforcement layer that must stay green and grow with the audit.
- **Audit report**: the committed deliverable recording findings, severities, and dispositions.
- **Documentation set**: README.md, DEVELOPMENT.md, CHANGELOG.md, spec index. Must match reality after the pass.

## Success Criteria

Measurable Outcomes

- **SC-001**: The secrets scan (tracked files + git history) reports zero open findings: every hit has a disposition, and no live credential remains usable. This is reproducible from the committed audit report and gate.
- **SC-002**: Every high-severity security finding is remediated. Every accepted risk is listed in the audit report with a reason and owner sign-off.
- **SC-003**: 100 % of tracked files resolve to a documented location in DEVELOPMENT.md's layout section; zero undocumented root-level strays remain.
- **SC-004**: Every existing automated test and gate passes after the change: full pytest suite, `check-public`, `check-or005`, commit checks, and the FR-013/FR-014 deploy verification.
- **SC-005**: The published map shows no user-visible change: all 8 interactions within the 2 s budget, desktop interaction median at or below 123 ms, and building values/colors/labels identical to the current bundle.
- **SC-006**: The audit report is committed and describes scope, method, findings by severity, and dispositions; a reviewer unfamiliar with the repo can verify each disposition.
- **SC-007**: The extended hygiene gate catches every new pattern: a synthetic test file containing each pattern makes the gate fail with the file and pattern named.

## Assumptions

- Git history is not rewritten by default. If the scan finds a credential that was or is live, the disposition is rotation plus forward prevention; history rewriting happens only with explicit owner approval.
- The audit's method is repository and code review: scanning, static inspection, and verification against the existing gates and harness — not penetration testing of third-party services (Cloudflare, RunPod, LGL) or GitHub account settings.
- The site's existing contracts remain authoritative: no analytics (FR-001), static architecture, Range-passthrough data serving, feature 014 caching semantics. Security changes are additive (headers, policy, gates), not architectural.
- The current behavior is correct and must not change; "regression" means any change a visitor can observe in values, colors, layout, or interaction, or any test/gate that stops passing.
- Root-level files whose purpose is unclear (`info`, `progress.md`, `cited.md`, `notes/`) are assumed to have value until proven otherwise; their disposition is a documented owner decision, not silent deletion.
- The RunPod endpoint continues to run only on owner-supplied capacity behind an SSH tunnel (OR-003); the audit documents and hardens that model, it does not assume a public endpoint.
