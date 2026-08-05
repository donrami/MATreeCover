# Data Model

**Branch**: `005-host-on-personal-domain` | **Date**: 2026-08-04
**Source**: `spec.md` (clarified 2026-08-04) § Key Entities + edge
cases, `research.md` R-001..R-014, `src/pipeline/publish.py`,
`dist/` listing.

This feature introduces no application data entities and no
persisted application state (FR-011). The entities below document
the deployment surface: the published map site, the bundle split
across Cloudflare assets and R2, the personal domain with its DNS
migration, the preserved Hostinger services, and the Cloudflare
release lifecycle.

## E-001 — PublishedMapSite

The version of the map currently live at
`https://abu-hamad.de/map/`; visitors interact with exactly one
complete version at a time (FR-010).

| Field | Value | Notes |
|---|---|---|
| canonical URL | `https://abu-hamad.de/map/` | Trailing slash required (relative asset refs, R-004). |
| redirects | `/map` → `/map/`; `www.abu-hamad.de/map*` → canonical | Single 301s, no loop (FR-001, FR-003). |
| serving | Cloudflare Worker, route `abu-hamad.de/map/*` (+ www) | Everything else on the hostname goes to the blog origin (R-001). |
| active release | Worker deployment version (100% traffic) | Set by `wrangler deploy` (R-006). |
| root behavior | unchanged — WordPress blog + email | Not this feature's target (clarified). |
| verification state | unverified / verified / failed | Set by the FR-013 gate. |
| visible content | byte-identical to local `dist/` | SC-007. |

**Invariants**:

- Exactly one active Worker deployment; visitors never see a
  partial release (FR-010).
- `/map/` serves the map; every other path on apex/www serves the
  blog origin (never a mix).
- The address bar shows `abu-hamad.de/map/` — no redirect to a
  foreign URL (clarified FR-001).

## E-002 — DeploymentBundle

The complete static output of `make publish` (`dist/`), split by
size for Cloudflare serving.

| Field | Value | Notes |
|---|---|---|
| small files (Worker assets) | `index.html`, `style.css`, `main.js`, `style.json`, `attribution.html`, `vendor/{maplibre-gl.js,maplibre-gl.css,pmtiles.js}`, `boundary.geojson`, `manifest.json` | All < 25 MiB (asset limit, R-002); ~1 MB. |
| large files (R2) | `buildings.pmtiles` (33 MB), `trees.pmtiles` (77 MB), `buildings.geojson` (54 MB) | Over 25 MiB → R2 objects, served via Worker binding with Range passthrough (R-003). |
| total | ~171 MB on disk | perf record: 171,062,607 bytes. |
| identity | per-file `sha256` + count + total bytes | Computed by `deploy-cf.sh`; verified before and after deploy (R-006). |
| URL shape | all relative under `/map/` | No URL patching → SC-007 byte-identity (R-003). |

**Invariants**:

- The live release's files are byte-identical to local `dist/`
  (SC-007); data URLs are never rewritten (R-003).
- A release is never modified after its verification step.
- The bundle contains no server-side components, database, or
  analytics (FR-011).

## E-003 — PersonalDomain

The canonical public address `abu-hamad.de` with its DNS migration
and certificate story.

| Field | Value | Notes |
|---|---|---|
| registrar | GoDaddy | Nameservers set there (R-008). |
| nameservers (after) | Cloudflare's two NS | Moved from Hostinger after the new zone is fully populated. |
| DNS zone | Cloudflare (free, full setup) | A `@`/`www` → Hostinger blog IP; MX `mx1/mx2.hostinger.com`; TXT SPF/DMARC/DKIM; any `mail` A (R-008). |
| certificate | Cloudflare Universal SSL (apex + www), auto | Presented once records are proxied and the zone is Active (R-008). |
| map path | `/map/` → Worker route | The only path this feature owns. |

**Invariants**:

- The zone is a record-for-record copy of the Hostinger zone
  BEFORE the nameserver switch (outage-free, R-008).
- Email records stay DNS-only (Cloudflare does not proxy MX/SMTP).
- Universal SSL covers apex + www; certificate validity verified by
  the FR-013 gate.

## E-004 — BlogAndEmailServices (preserved, FR-014)

The Hostinger-hosted services at the domain root that the migration
must not break.

| Field | Value | Notes |
|---|---|---|
| WordPress blog | `https://abu-hamad.de/` (and www) | A record → Hostinger IP; recreated at Cloudflare; proxied only after zone Active + SSL mode Full (strict) (R-008). |
| email | Hostinger mailboxes (`@abu-hamad.de`) | MX `mx1.hostinger.com` (5) / `mx2.hostinger.com` (10); SPF `v=spf1 include:_spf.mail.hostinger.com ~all`; DMARC `_dmarc` TXT; DKIM CNAMEs — all recreated at Cloudflare, DNS-only (R-008). |
| mailboxes/files | remain at Hostinger | DNS migration cannot touch them (R-008). |

**Invariants**:

- No email outage: MX/SPF/DMARC/DKIM identical at Cloudflare before
  the switch; verified with a send/receive test (FR-014 gate).
- No blog outage: same A records, same IP; blog verified after the
  cutover and again after the proxy flip.
- SPF stays a single record (duplicates are a perm-error).

## E-005 — CloudflareRelease (Worker version + R2 objects)

The unit of atomic change on the Cloudflare side.

| Field | Value | Notes |
|---|---|---|
| Worker version | code + assets + bindings snapshot | Activated by `wrangler deploy` (atomic, 100% traffic) (R-006). |
| R2 objects | `buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson` in `matreecover-data` | Stable keys, overwritten per release; single PUT atomic per object (R-006). |
| object config | content-type (`application/vnd.pmtiles`, `application/geo+json`); `Cache-Control: no-cache`; `no-transform` on pmtiles | R-007. |
| state | staged → verified → active → retired | Lifecycle below. |
| local archive | `dist-archive/<ts>/` | Last 3 releases kept for data rollback (R-006). |

**State transitions** (release lifecycle):

```text
make publish (local)                              → bundle identity (E-002)
r2 object put ×3 (atomic per object)              → staged        (live untouched)
verify checksums (local vs R2)                    → verified      (abort keeps live)
wrangler deploy (assets+code, atomic last step)   → active        (100% traffic at once)
post-deploy live verification                     → verified-active or ROLLBACK
rollback: wrangler rollback + re-upload prev data → previous release re-activated
prune local archives beyond 3                     → retired       (after success)
```

**Failure transitions**:

- Interrupted `r2 object put` → object stays at its previous
  version (PUT atomicity); the release stays staged; live
  untouched (FR-010 acceptance 2).
- Interrupted `wrangler deploy` → no deployment is created (the
  direct-upload flow activates only at the completion token); the
  previous version keeps serving (R-006).
- Post-deploy verification fails → `wrangler rollback`; previous
  R2 objects re-uploaded from the kept archive.

**Invariants**:

- The active transition is one atomic platform operation
  (`wrangler deploy`), never a partial file swap.
- Data objects are never referenced before their checksums are
  verified.

## State machine summary (PublishedMapSite × CloudflareRelease)

```text
bootstrap      DNS inventory → Cloudflare zone recreated (grey) → routes staged
               → GoDaddy NS switch → zone Active → Universal SSL Active
               → A records proxied + SSL mode Full (strict) → FR-014 gate passes
deploy N       R2 put → verify → wrangler deploy → verify live
failure        release stays staged/verified; previous version live
rollback       wrangler rollback + re-upload previous data
prune          local archives beyond 3 removed after success
```

All transitions are driven by `scripts/deploy-cf.sh` and the
documented DNS migration procedure; the WordPress blog and email at
the root are never part of a map release (E-004, FR-014).
