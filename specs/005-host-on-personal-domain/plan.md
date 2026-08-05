# Implementation Plan: Host on Personal Domain

**Branch**: `005-host-on-personal-domain` | **Date**: 2026-08-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-host-on-personal-domain/spec.md` (clarified 2026-08-04)

## Summary

Serve the published static map bundle at the path
`https://abu-hamad.de/map/` on Cloudflare's free plan, while the
domain root keeps the existing Hostinger services (WordPress blog,
email). The map renders AT the path (no redirect to a foreign URL,
FR-001 as clarified). Mechanism (research R-001..R-003): one
Cloudflare **Worker** with **routes** `abu-hamad.de/map*` (+ www
equivalents) serves the bundle's small files as **Workers static
assets** (free, unlimited) and streams the three large data files
(`buildings.pmtiles` 33 MB, `trees.pmtiles` 77 MB,
`buildings.geojson` 54 MB — all over 25 MiB, the asset limit) from
an **R2 binding** with native HTTP Range/206 passthrough (FR-007).
Cloudflare Pages and bucket custom domains are hostname-scoped and
cannot serve a path prefix — they are excluded by research. Deploys
are atomic by platform design (R-006): `r2 object put` per object,
then `wrangler deploy` as the last step; an interrupted upload never
replaces the live version (FR-010, SC-006); rollback is
`wrangler rollback` plus re-upload of the previous data from kept
local archives. The DNS migration (R-008) moves the zone from
Hostinger to Cloudflare at GoDaddy with the new zone fully populated
first (A `@`/`www` → Hostinger blog, MX/SPF/DMARC/DKIM → Hostinger
email), so email and the blog keep working (FR-014); blog records
start DNS-only and flip to proxied with SSL mode Full (strict) only
after the zone and Universal SSL are Active. Cache contract
(R-007): `no-cache` + `no-transform` on R2 data, asset default
revalidation — no stale version after updates. No changes to
`src/site/` or `src/pipeline/`; new files are a small Worker project
(`workers/map/`) and `scripts/deploy-cf.sh`; SC-007 byte-identity
holds. FR-011 (no server-side components, database, or analytics)
holds — the Worker is a static-file server, not an application.

## Technical Context

**Language/Version**: Plain JavaScript for the Worker (`index.js`,
~40 lines, zero dependencies, no build step); Bash for
`scripts/deploy-cf.sh`; wrangler CLI (≥ 3.98.0 for subdirectory
asset serving, pinned in `workers/map/package.json`). The deployed
bundle is unchanged (vanilla HTML/CSS/JS + vendored MapLibre GL
5.7.1).

**Primary Dependencies**: Cloudflare (free plan): Workers routes,
Workers static assets, R2 (binding, 10 GB free, zero egress),
Universal SSL. Local: `wrangler` (npx), `curl`/`dig`/`openssl` for
the FR-013 gate, `rsync` no longer needed. Hostinger keeps the
blog and email (untouched, FR-014). No new runtime dependencies in
the bundle.

**Storage**: Cloudflare R2 bucket `matreecover-data` (~164 MB of
data files; free tier 10 GB-month, 1M Class A / 10M Class B ops,
zero egress); Worker assets (~1 MB shell, free unlimited). Local
`dist-archive/` keeps the last 3 release bundles for data rollback.

**Testing**: FR-013 live gate: `dig` (NS/A/MX/TXT at public
resolvers), `curl` (200, 301 `/map`→`/map/`, `Cache-Control`,
Range 206 on `.pmtiles`), `openssl` certificate validity for apex +
www; browser console for mixed content. FR-014 gate: blog loads,
email send/receive with SPF/DKIM/DMARC pass (mail-tester).
Manual smoke checklists (`tests/frontend/smoke_us1..4.md`) re-run
against `https://abu-hamad.de/map/`; throttled CDP perf
re-measurement recorded under `validation/live-perf.json` (SC-004).
No pytest changes (no data/pipeline change).

**Target Platform**: Public internet — modern browsers (WebGL 2);
Cloudflare Workers edge (LiteSpeed/Hostinger no longer involved in
the map path).

**Project Type**: Static-site deployment (operations feature; the
site remains a static bundle served by a static-file Worker,
FR-011).

**Performance Goals**: SC-004 — first usable map ≤ 10 s and
interactions ≤ 2 s at 25 Mbps / 50 ms on the live path (local
reference: 2.5 s / 80–211 ms). The data path is direct R2 206
responses from Cloudflare's edge; the `no-cache` contract adds
revalidation round-trips only (R-007, R-010).

**Constraints**:

- The map MUST render at `https://abu-hamad.de/map/` (trailing
  slash — relative asset refs require it, R-004); `/map` and
  `www.abu-hamad.de/map*` 301 to it (FR-001, FR-003).
- Range/206 MUST work for the PMTiles layers (FR-007): served by
  the Worker from R2 (native 206); never from Workers assets or
  Pages (no guaranteed 206, R-002/R-003).
- Data files are `no-cache` + `no-transform`; assets revalidate by
  default — no long cache on non-hashed names (R-007).
- Deploys MUST be atomic: R2 PUT per object, `wrangler deploy`
  last; interrupted uploads leave the previous version live
  (FR-010, SC-006, R-006).
- DNS migration MUST keep the Hostinger email and blog working:
  full record inventory and recreation at Cloudflare BEFORE the
  GoDaddy nameserver switch; email records DNS-only (FR-014,
  R-008).
- Blog A records must be proxied (orange) for `/map*` routes to
  function; SSL mode Full (strict) after Universal SSL is Active
  (R-008).
- OR-005: no large files enter git (R2 uploads stream from local
  `dist/`; `dist/` stays gitignored).

**Scale/Scope**: One domain (GoDaddy registrar), one Cloudflare
zone, one Worker + one R2 bucket, the existing Hostinger blog and
email untouched. New repo files: `workers/map/{wrangler.toml,
index.js, package.json}`, `scripts/deploy-cf.sh`; validation
records under `validation/`; README deployment section; no `src/`
changes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No constitution file exists (`.specify/memory/constitution.md`
absent — same as 004), so no constitution-derived gates. The
de-facto gates are the project's operating rules (Makefile,
README) and the spec's own constraints:

- **OR-004 (one commit per accepted spec/plan/slice)**: PASS —
  plan committed via `make commit-plan`; implementation lands via
  `make commit-slice`.
- **OR-005 (no `*.tif`/`*.pmtiles`/>50 MiB `.geojson` tracked)**:
  PASS — new files are small text (`wrangler.toml`, `index.js`,
  `deploy-cf.sh`); `dist/` remains gitignored; R2 uploads stream
  from local disk (R-014).
- **FR-011 (no analytics/server-side components/database)**: PASS —
  the Worker serves static files and R2 objects only; no
  application logic, no database, no analytics.
- **SC-007 (no content drift; live = local bundle)**: PASS by
  construction — assets come straight from `dist/`, data files
  are transferred byte-identically with sha256 verification
  (R-003, R-006); data URLs stay relative under `/map/`.
- **FR-014 (email + blog continuity)**: PASS by procedure — the
  new Cloudflare zone is a record-for-record copy of the Hostinger
  zone before the nameserver switch; FR-014 gate verifies email
  send/receive and blog after the cutover (R-008).
- **Spec edge cases**: DNS propagation (dig at two resolvers,
  24–48 h); SSL not yet issued (zone Pending → Universal SSL
  Active; records stay grey until then); Range unsupported (206
  gate on the live `.pmtiles`); stale cache (no-cache contract);
  interrupted upload (atomic R2 PUT + atomic Worker deploy);
  storage limits (R2 free tier check in the script);
  www/non-www consistency (Worker canonical redirect, R-009);
  email/blog outage during migration (FR-014 gate) — all addressed
  in research R-001..R-014 and the quickstart scenarios.
- **Spec clarification refinement**: the clarified spec says
  "Pages hosts the site shell; a public R2 bucket hosts the data".
  Research R-001/R-003 refines the mechanism — Pages and bucket
  custom domains are hostname-scoped, so the shell is a Worker
  route with static assets and the data comes via an R2 binding
  (URLs stay under `/map/`). The user-visible contract (renders at
  `/map/`, Cloudflare, no redirect) is unchanged; the plan records
  the refinement rather than a gate violation.

Post-design re-check: no new gates introduced. The design adds a
small Worker project and a deploy script; it changes no source
files, adds no dependencies to the bundle, and extends no
governance surface.

## Project Structure

### Documentation (this feature)

```text
specs/005-host-on-personal-domain/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output — Cloudflare topology, DNS migration
├── data-model.md        # Phase 1 output — entities E-001..E-005 + release lifecycle
├── quickstart.md        # Phase 1 output — Scenarios 1–7 validation guide
├── contracts/           # Phase 1 output
│   ├── README.md
│   ├── deployment.md    # Cloudflare deploy procedure, atomicity, rollback
│   ├── hosting-config.md# Worker/R2/route config + DNS records table + SSL mode
│   ├── dns-https.md     # GoDaddy NS switch, record inventory, email continuity
│   └── bundle.md        # dist/ split (assets vs R2), sha256 identity
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
workers/
└── map/                 # NEW — the Cloudflare Worker project
    ├── wrangler.toml    #   name, main index.js, assets.directory ../../dist,
    │                    #   R2 binding (matreecover-data), routes /map* + www/map*
    ├── index.js         #   asset shell + R2 range passthrough + /map→/map/ and
    │                    #   www→apex 301s (~40 lines, zero deps, no build)
    └── package.json     #   devDependency: wrangler (pinned ≥ 3.98.0)

scripts/
└── deploy-cf.sh         # NEW: make publish → sha256 manifest → r2 object put ×3
                         #      → wrangler deploy (atomic) → live verify → record
                         #      → prune local archives (keep 3) (contracts/deployment.md)

src/                     # UNCHANGED — bundle content is not modified (FR-004, SC-007)
├── site/                #   (index.html, style.css, main.js, style.json, attribution.html, vendor/)
└── pipeline/            #   (publish.py already emits dist/; no change)

validation/
├── dns-migration-<ts>.json  # NEW: record inventory + FR-014 verification results
├── live-perf.json           # NEW (SC-004): throttled measurement vs /map/
└── deploy-<ts>.json         # NEW per run: release id, sha256s, deploy results

README.md                # Deployment section added: point to workers/map + scripts/deploy-cf.sh
```

**Structure Decision**: The deployment feature is a small Cloudflare
Worker project (`workers/map/`) plus a deploy script
(`scripts/deploy-cf.sh`) and validation records — consistent with
the existing `scripts/` and `validation/` conventions. `src/` and
`Makefile` are untouched: the bundle must remain byte-identical to
`make publish` output (SC-007), and the Worker serves `dist/`
directly as assets. The Worker is placed under `workers/map/` (not
`src/`) because it is deployment infrastructure, not part of the
application bundle.

## Complexity Tracking

No Constitution Check violations; table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
