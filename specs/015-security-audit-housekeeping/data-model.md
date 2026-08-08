# Data Model: Security Audit & Repo Housekeeping (feature 015)

Phase 1 output. Entities, fields, validation rules, and state transitions that the feature's artifacts must satisfy. This feature is an audit + housekeeping pass over an existing repository, so the "data" is the audit's own records plus the enforcement artifacts.

## Entities

### E1 — SecretPattern

The machine-checkable secret definitions. Single source of truth: `scripts/public-patterns.txt`.

| Field | Type | Rule |
|-------|------|------|
| id | string `P\d+` | Unique. P1–P19 exist (feature 006); P20–P32 added by this audit. Never reused. |
| regex | ERE | One line per pattern. Must match `grep -E`. Quoted only in the pattern file (contracts reference IDs, not literals). |
| rationale | text | Comment block above the regex. Why the string is forbidden. |
| applies_to | enum | `tracked`, `history`, `both` (all new patterns are `both`) |

Validation: every pattern in the pattern file is used by both gates; every pattern ID in the contracts exists in the file. Adding a pattern without updating the contract (FR-003) or the exemption ledger is a gate failure.

### E2 — Finding

A secret-scan hit. Recorded in the audit report; machine form is `scripts/history-exemptions.tsv`.

| Field | Type | Rule |
|-------|------|------|
| id | string `F\d+` | Unique per report. |
| pattern_id | ref E1 | Which pattern matched. |
| location | path / commit:path | Tracked file path, or historical `commit:path:line`. |
| line / match | string | Evidence text. |
| severity | enum `high`/`medium`/`low` | Per assessment, not per pattern. |
| disposition | enum `remediated` / `never-live` / `accepted-risk` | FR-002: every finding MUST have one. |
| evidence | text | For `never-live`: why it never reached a live service. For `remediated`: rotation proof. For `accepted-risk`: reason + owner sign-off. |
| owner_signoff | name + date | Required for `accepted-risk`. |

Invariant (FR-002/SC-001): the report has zero findings without a disposition; no dispositioned `remediated` finding points at a still-live credential.

### E3 — HistoryExemption

A ledger row that keeps the history gate green for a dispositioned historical hit.

| Field | Type | Rule |
|-------|------|------|
| pattern_id | ref E1 | The pattern that matched. |
| commit | sha | The historical commit containing the hit. |
| path | path | File within that commit. |
| disposition_ref | ref E2 id | Must resolve to a dispositioned finding in the audit report. |

Validation (FR-011): `scripts/check-git-history.sh` fails when a history finding has no exemption row; fails when an exemption row does not match any actual finding (stale/creeping exemptions); fails when an exemption row references a nonexistent report finding. Exemption ledger and gate change only together with the contract.

### E4 — SecurityHeader

The deployed-surface contract (FR-004). Contract: `contracts/security-headers.md`; implementation: `workers/map/index.js`.

| Field | Type | Rule |
|-------|------|------|
| name | header name | From the decided set (R4). |
| value | string | Fixed, committed value. |
| scope | enum `all` / `html` | `all` = every Worker response (assets, R2 200/206, 404). |
| must_not_touch | set | On 206: `Content-Range`, `ETag`, `Accept-Ranges`, `Content-Length` must pass through unchanged. |

Invariant (FR-013): header injection never alters body, status, or caching semantics; the existing `verify` Range/206 and cache-header gates stay green.

### E5 — CspPolicy

| Field | Type | Rule |
|-------|------|------|
| source_of_truth | path | `src/site/index.html` meta tag — the committed, browser-enforced policy. |
| worker_header | string | Must be byte-identical to the meta value (both apply = intersection; drift would silently tighten). |
| required_allowlist | set | `sgx.geodatenzentrum.de` (basemap), `demotiles.maplibre.org` (fonts), `data:`/`blob:` (PMTiles worker), `style-src 'unsafe-inline'` (feature 014). Any tightening that removes these breaks the map (spec edge case). |

### E6 — DataKey

The R2 surface (FR-005). Immutable set in the Worker: `buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson`.

| Rule | Check |
|------|-------|
| Only these keys answer 200/206 under `/map/` | `deploy-cf.sh verify` asserts 206 on Range for all three |
| Any other data-looking key returns 404 | `verify` gains an unknown-key 404 assertion |
| Range passthrough preserved | Existing 206 + `Content-Range` gate unchanged |
| Bucket public access off | Manual dashboard check in quickstart S6 (not in repo) |

### E7 — LayoutManifestRow

Machine-checkable layout (FR-009/011). File: `scripts/layout-manifest.tsv`.

| Field | Type | Rule |
|-------|------|------|
| tracked_path | top-level path | One row per top-level tracked entry (file or dir). |
| documentation_ref | text | Where DEVELOPMENT.md's layout section describes it. |

Invariants (SC-003): every `git ls-files` path starts with a manifest row; every row exists in the tree; no root-level file outside the documented root set (R10). Layout section and manifest change together; the section names the manifest as its machine form.

### E8 — VendoredLibrary

Supply-chain record (FR-008). File: `src/site/vendor/PROVENANCE.md`.

| Field | Rule |
|-------|------|
| name, version | Matches the vendored file and DEVELOPMENT.md's pin. |
| license, source_url | Recorded per library. |
| sha256 | Of the tracked vendored file; recomputed on update (evidence, not a blocker). |

Plus a declared-runtime-dependency list: LGL basemap origin (attributed) and `demotiles.maplibre.org` fonts (accepted risk, owner sign-off, R8). No undeclared runtime dependency may be introduced.

### E9 — HousekeepingDecision

Every move/delete/keep of a stray file (FR-009). Recorded in the audit report.

| Field | Type | Rule |
|-------|------|------|
| path | old path | The stray. |
| action | `move` / `delete` / `keep-and-document` | Never silent: every action recorded. |
| destination / reason | text | For `move`: target dir documented in layout. For `delete`: owner sign-off (spec edge case: never delete on assumption). |

### E10 — AuditReport

The committed deliverable (FR-012). File: `verification/security-audit-2026-08-08.md`.

| Section | Contents |
|---------|----------|
| Scope & method | Commands, pattern file reference, boundary statements (out of scope list). |
| Findings | E2 rows by severity, each with disposition + evidence. |
| Accepted risks | E2 rows of type `accepted-risk`, with reason + owner sign-off. |
| Housekeeping decisions | E9 rows. |
| Gate summary | Re-run results for every gate (SC-006: a reviewer can verify dispositions). |

## State transitions

**Finding lifecycle** (E2):

```text
open ──► dispositioned
          ├─ remediated     (rotation proof recorded)
          ├─ never-live     (evidence recorded)
          └─ accepted-risk  (reason + owner sign-off recorded)
```

Rules: every `open` finding at audit end is a gate failure (SC-001). `accepted-risk` requires sign-off; `remediated` requires the credential to be unusable.

**History gate** (E3): a historical hit is `green` only while its exemption row exists and resolves to a dispositioned finding. Removing the disposition without removing the exemption fails the gate (no orphan exemptions).

**Gate states** (all enforcement artifacts): `green` (exit 0) / `red` (exit 1 with named file + pattern + reason). FR-014 requires every gate green after the change; SC-007 requires a synthetic pattern to turn `check-public` red with file + pattern named.

## Validation rules consolidated from the spec

- FR-002: every finding has exactly one disposition; accepted-risk needs owner sign-off.
- FR-003: pattern additions land in gate + contract in the same change; gate stays green on the audited tree.
- FR-005: three keys only; 206 preserved; unknown keys 404.
- FR-009: every tracked file resolves to a documented location; no undocumented root strays.
- FR-011: enforcement is machine-checkable (gates), not documentation-only.
- FR-013/FR-014: no user-visible change; all existing tests and gates pass; deploy verification gates (redirects, Range 206, cache headers, cert, DNS, email) stay green.
- OR-005: no `*.tif`, `*.pmtiles`, or `>50 MiB` geojson enters the tracked set; moved files are small.
- SC-005: interaction budget (8 interactions ≤ 2 s, desktop median ≤ 123 ms) and building values/colors/labels identical to the current bundle.
