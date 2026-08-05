# Phase 0 Research

**Branch**: `005-host-on-personal-domain` | **Date**: 2026-08-04
**Inputs**: `spec.md` (clarified 2026-08-04: map at
`https://abu-hamad.de/map`, Cloudflare hosting, GoDaddy registrar,
Hostinger blog + email continuity), `plan.md` technical context,
`src/site/main.js` / `index.html` / `style.json` (relative asset
refs), `src/pipeline/publish.py` (bundle contents), two web research
passes (Cloudflare path-based static hosting; GoDaddy→Cloudflare
nameserver migration with Hostinger email/blog).

This is a deployment feature. No `src/` code changes. The spec's
clarification "Cloudflare — Pages hosts the site shell; a public R2
bucket hosts the data" is refined here: Cloudflare **Pages** cannot
serve a path prefix and returns `200` instead of `206` for Range
requests, so the serving mechanism is a **Workers route** with a
**Workers Static Assets** shell plus an **R2 binding** for the large
data files (R-001, R-002, R-003). The user-visible contract
(renders at `https://abu-hamad.de/map/`, no redirect to a foreign
URL) is unchanged.

## R-001 — Path-based serving: Workers route, not Pages (FR-001)

**Decision**: Serve the map at the path `abu-hamad.de/map/*` via a
**Workers route** that maps exactly the `/map*` URL patterns to one
Worker (`abu-hamad.de/map`, `abu-hamad.de/map/*`, plus the
`www.abu-hamad.de/map*` equivalents). All other paths continue to
the origin defined in DNS — the Hostinger WordPress blog at the
root. The canonical URL is `https://abu-hamad.de/map/` (trailing
slash), with a 301 from `/map`.

**Rationale**: Cloudflare Pages custom domains and Workers Custom
Domains are both **hostname-scoped** (a domain or subdomain, never
a path prefix — confirmed in official docs and an open community
feature request since 2022). Workers **routes** are the documented
mechanism for path-prefix mapping: "Routes map URL patterns to
Workers and proxy only matched paths; unmatched paths continue to
the origin." The apex A record (Hostinger blog) stays in DNS; the
route runs on top of the proxied record and intercepts only
`/map*`. The bundle's asset references are all relative
(`style.json`, `vendor/*.js`, `pmtiles://…` — verified in
`src/site/`), which resolves correctly only at a trailing-slash
URL: `https://abu-hamad.de/map/` → `/map/style.json`,
`/map/vendor/…`; without the trailing slash they would resolve at
the root and hit the blog. Hence canonical `/map/` + 301 from
`/map`.

**Alternatives considered**: *Pages custom domain*: hostname-scoped,
cannot attach at `/map`; rejected. *Workers Custom Domain*: also
hostname-scoped, and the apex already has a CNAME-free A record for
the blog; rejected. *Subdomain `map.abu-hamad.de`*: works, but the
spec (clarified) requires the path under the apex; rejected.

## R-002 — Workers Static Assets: the small-file shell (FR-004)

**Decision**: The Worker serves the bundle's small files (everything
under 25 MiB) as **Workers static assets** (`assets.directory =
dist/` in `wrangler.toml`): `index.html`, `style.css`, `main.js`,
`style.json`, `attribution.html`, `vendor/{maplibre-gl.js,
maplibre-gl.css, pmtiles.js}`, `boundary.geojson` (75 KB),
`manifest.json`. All are well under the 25 MiB per-file limit.

**Rationale**: Workers static assets have a 25 MiB per-file limit on
all plans (raised total caps in Sep 2025 do not change it), 20,000
files on free — our shell is ~1 MB in ~9 files. Asset requests are
**free and unlimited** (not counted against the 100k/day Worker
invocation limit), with native trailing-slash handling and default
`Cache-Control: public, max-age=0, must-revalidate` + ETag —
revalidates after every deploy, never serves stale (spec edge case).
Serving a subdirectory requires wrangler ≥ 3.98.0 (pinned in
tooling).

**Alternatives considered**: *Everything on R2*: the small files
would cost Class B ops per request and lose the free unlimited
asset serving; rejected. *Pages for the shell*: Pages cannot serve
at a path prefix (R-001); rejected.

## R-003 — R2 binding for the large data files (FR-005, FR-007)

**Decision**: The three files over 25 MiB —
`buildings.pmtiles` (33 MB), `trees.pmtiles` (77 MB),
`buildings.geojson` (54 MB) — live in an R2 bucket
(`matreecover-data`) and are served by the **same Worker** via an
R2 binding: the Worker passes the client's `Range` header through to
`env.DATA.get(key, { range })` and forwards the `206` +
`Content-Range` from R2. URLs stay relative (`/map/buildings.pmtiles`
etc.), so the bundle is transferred byte-identically (SC-007).

**Rationale**: R2 supports HTTP Range natively ("unconditionally
return HTTP 206 on ranged requests"; Workers binding range reads are
GA), has a free tier of 10 GB-month storage, 1M Class A and 10M
Class B ops/month, and **zero egress fees** — a perfect fit for
bandwidth-heavy tile serving. ~164 MB of data fits the free storage;
each tile range request is one Class B op (10M free ≈ 300k+ tile
fetches/day). R2 does NOT need a public bucket custom domain here —
and cannot have one at a path anyway (bucket custom domains are
hostname-scoped); the binding keeps everything under `/map/`. An
interrupted object upload never corrupts the live object: a single
PUT is atomic per object (multipart materializes only at
completion; our files need single PUT — the 5 GiB multipart
threshold does not apply).

**Alternatives considered**: *Public bucket + custom domain
`data.abu-hamad.de`*: changes the data URLs in `style.json`
(breaking byte-identity, SC-007) and cannot be path-scoped;
rejected. *Workers static assets for the big files*: 25 MiB limit
excludes them (and Pages-style asset serving does not guarantee
206); rejected. *r2.dev public subdomain*: rate-limited dev-only,
foreign URL; rejected.

## R-004 — Canonical URL and trailing slash (FR-001)

**Decision**: Canonical map URL = `https://abu-hamad.de/map/`.
Requests to `/map` (no slash), and to `www.abu-hamad.de/map*`, are
301-redirected to the canonical URL by the Worker. The
Worker/asset layer serves the bundle only under `/map/`.

**Rationale**: All bundle asset references are relative (verified:
`STYLE_URL = 'style.json'`, `fetch('boundary.geojson')`,
`pmtiles://buildings.pmtiles`), so they resolve correctly only at a
trailing-slash base. Workers static assets have native
trailing-slash handling (`html_handling: auto-trailing-slash`).
FR-003 (single canonical redirect, no loop) is satisfied by
canonicalizing both the missing-slash and the `www` hostname to
`https://abu-hamad.de/map/`.

**Alternatives considered**: *Serve at `/map` without slash*: breaks
relative resolution (assets would resolve against the root and hit
the blog); rejected. *No www handling for /map*: www visitors would
404 on the blog; the redirect is required (FR-003).

## R-005 — Free-plan limits fit (SC-004, scale)

**Decision**: One Worker with four routes
(`abu-hamad.de/map`, `abu-hamad.de/map/*`,
`www.abu-hamad.de/map`, `www.abu-hamad.de/map/*`) on the free plan.
Worker invocations: only data-file requests invoke the Worker
(asset navigations are served free without invoking it); a
personal map site stays far below the 100k invocations/day, 10 ms
CPU, 50 subrequests, and 128 MB memory limits. Route limits (1,000
per zone) are irrelevant at 4.

**Rationale**: Official free-plan limits confirmed: 100k
requests/day per account, 10 ms CPU, 50 subrequests, 100 Workers,
3 MB gzipped bundle (the Worker code is a few KB); static-asset
requests are free and unlimited. Each tile fetch is one R2 binding
subrequest (1 of 50 per request) — fine. The known-issues caveat:
with path-component route patterns, keep exactly one Worker on the
`/map*` patterns (no sibling pattern conflict).

**Alternatives considered**: *Multiple Workers for shell vs data*:
unnecessary; one Worker serves both (assets natively, R2 by
binding); simpler and avoids the route-specificity caveat.

## R-006 — Atomic deploys and rollback (FR-010, SC-006)

**Decision**: Deploy order: (1) upload the three R2 objects with
`wrangler r2 object put` (atomic per object; an interrupted upload
leaves the previous object intact and unreferenced), (2) deploy the
Worker version with `wrangler deploy` (uploads code + assets, then
activates the new version atomically as the last step — an
interrupted asset upload never creates a deployment, so the
previous version keeps serving), (3) verify live, (4) write the
deploy record, (5) prune local archives beyond the last 3 releases.
Rollback = `wrangler rollback` (immediate new deployment of the
previous version) plus re-upload of the previous release's R2
objects from the kept local archive.

**Rationale**: Cloudflare's versions-and-deployments model is
atomic by construction: a deployment switches traffic to a new
version in one step, and the direct-upload flow activates only at
the completion token. R2 PUT is atomic per object. This satisfies
FR-010/SC-006 without any symlink machinery (the Hostinger-era
symlink-flip design is obsolete). Rollback via `wrangler rollback`
is documented and immediate. Data rollback needs the previous
objects re-uploaded (R2 keys are stable names, overwritten per
release) — the deploy record keeps sha256s and the script keeps the
last 3 local `dist` archives for this.

**Alternatives considered**: *Versioned R2 keys per release*
(`releases/<ts>/buildings.pmtiles`): requires patching `style.json`
URLs per release (breaks byte-identity) or a Worker rewrite layer;
stable keys + atomic overwrite + rollback-by-re-upload is simpler.
*Keep old objects under `prev/` prefixes*: extra bookkeeping;
local archives suffice.

## R-007 — Cache contract: no stale version after updates (spec edge case)

**Decision**: Data files (R2): uploaded with
`Cache-Control: no-cache` (`--cache-control` at `r2 object put`),
plus `no-transform` on the `.pmtiles` objects so edge compression
never strips `Content-Length` (a 206 slice requires it). Shell
assets: keep the Worker-assets default `public, max-age=0,
must-revalidate` + ETag. No long `max-age` anywhere — filenames are
not content-hashed, so any long cache would serve stale content
after a deploy. No Cloudflare edge cache is used for the data path:
Workers Caching does not store 206 responses (the Worker returns
R2's 206 directly; every request hits R2 — within the free Class B
budget and faster/simpler than cache-slicing).

**Rationale**: Confirmed: Cloudflare honors origin/Worker
`Cache-Control` on the free plan (no forced minimum TTL; the 120 min
default applies only when no headers exist); R2 object
`Cache-Control` is set at upload and honored at the edge;
`no-transform` preserves `Content-Length` for compressed-eligible
types (`.geojson` is compressible by default; `.pmtiles` binaries
are not). `no-store` is rejected as before: it would force
re-downloading 54 MB `buildings.geojson`-class payloads every visit
and break SC-004 for repeat visitors. Revalidation (ETag from R2,
ETag from assets) keeps bandwidth low via 304s.

**Alternatives considered**: *Edge-cache the data with a Cache
Everything rule*: the community-reported range-via-cache pitfalls
(200-with-full-body bugs, cache-miss full download before first
byte) make direct-R2 the safer choice at this scale; rejected.
*Content-hashed filenames*: breaks byte-identity (SC-007); rejected.

## R-008 — DNS migration: GoDaddy → Cloudflare, records first (FR-014)

**Decision**: Ordered migration with the new zone fully populated
BEFORE the nameserver switch: (1) inventory every record from the
Hostinger DNS Zone Editor (A `@`/`www` blog, MX, TXT SPF/DMARC/DKIM,
any `mail` A) and corroborate with `dig @1.1.1.1`; (2) create the
Cloudflare zone (free, full setup) and reconcile the imported zone
record-for-record — blog A records **DNS-only (grey)** first; (3)
stage the Worker and `/map*` routes (inert until activation); (4)
change nameservers at GoDaddy (Domain Settings → DNS →
Nameservers → "I use my own nameservers" → Cloudflare's two NS);
(5) after the zone flips to Active and Universal SSL is Active, flip
the blog records to proxied (orange) with SSL mode **Full (strict)**
(Hostinger's free Let's Encrypt satisfies the origin-cert
requirement); (6) verify blog + email + /map per the FR-014 gate.

**Rationale**: The NS change at the registrar only changes where
resolvers look; it cannot alter Hostinger-hosted mailboxes or
files. The outage-free pattern is: the new authoritative zone is a
faithful copy of the old one before anyone is pointed at it.
Confirmed record shapes: MX `mx1.hostinger.com` (5) /
`mx2.hostinger.com` (10); SPF `v=spf1 include:_spf.mail.hostinger.com
~all` (single line — duplicate SPF is a perm-error); DMARC TXT at
`_dmarc`; DKIM CNAMEs (auto-created at Hostinger, must be recreated
at Cloudflare). Email stays **DNS-only** (Cloudflare does not proxy
MX/SMTP). Blog A records must be **proxied** for the `/map*` routes
to work (routes run on proxied traffic) — hence the grey-first,
orange-after-activation sequence; proxying a cert-bearing origin
requires Full (strict), not Flexible (redirect loops).

**Alternatives considered**: *Keep DNS at Hostinger*: Cloudflare
routes need a proxied record on Cloudflare DNS; impossible.
*Proxied from the start*: Universal SSL is not presented until the
zone is Active — the grey-first sequence avoids a cert window;
rejected. *Full (non-strict) TLS mode*: works, but Full (strict) is
the documented safe default with a public-CA origin; chosen.

## R-009 — www canonicalization for the map path (FR-003)

**Decision**: The Worker also owns the `www.abu-hamad.de/map*`
patterns and 301-redirects them to `https://abu-hamad.de/map/`
(single redirect, no loop). The `www` **root** remains the
WordPress blog's own www→apex behavior (Hostinger, unchanged) — the
map and the blog each keep one canonical form.

**Rationale**: FR-003 requires the `www` variant of the domain to
land on the same site via a single canonical redirect. For the map
path, the Worker's 301 to the apex `/map/` is that single redirect.
The blog's www handling is pre-existing behavior (the root is not
this feature's target).

**Alternatives considered**: *CF Bulk Redirect for /map*: an extra
moving part; the Worker already owns the path; rejected.

## R-010 — Performance verification on the live path (SC-004)

**Decision**: Re-run the project's published measurement method
(`validation/perf-budget.json`: Chromium + CDP
`Network.emulateNetworkConditions` 50 ms / 25 Mbps, cold cache,
time-to-first-usable) against `https://abu-hamad.de/map/`, record
under `validation/live-perf.json`. Budgets: first usable ≤ 10 s,
interactions ≤ 2 s (local reference: 2.5 s / 80–211 ms).

**Rationale**: SC-004 is defined on the live site. The data path is
direct R2 206 responses from Cloudflare's edge — low latency; the
`no-cache` contract adds revalidation round-trips only. The local
record remains the reference for content parity.

**Alternatives considered**: *Rely on the local record*: the spec
measures the live site; rejected.

## R-011 — Tooling: wrangler CLI + a small Worker project (FR-009)

**Decision**: New repo files: `workers/map/` — `wrangler.toml`
(name, `main = index.js`, `assets.directory = ../../dist`, R2
binding, the four routes, pinned wrangler ≥ 3.98.0 in
`package.json` devDependencies), `index.js` (asset shell + R2 range
passthrough + canonical redirects, ~40 lines, zero deps, no build
step), and `scripts/deploy-cf.sh` implementing the R-006 sequence
(publish → r2 put ×3 → verify checksums → wrangler deploy → live
verify → record → prune). No changes to `Makefile`, `src/`, or
`dist/` contents.

**Rationale**: wrangler is the documented CLI for Worker deploys and
R2 object puts (v4: `--remote` for data ops; single PUT up to 5 GiB
— no multipart needed for our files); `wrangler deploy` is the
atomic version switch; `wrangler rollback` the rollback. The Worker
is plain JS (no npm build); assets come straight from `dist/` so
SC-007 holds. The script keeps the last 3 local archives for data
rollback.

**Alternatives considered**: *Hostinger-era `scripts/deploy.sh`
(symlink flip)*: obsolete — no shell access on Cloudflare, and the
platform's atomic deploy replaces the mechanism; deleted in this
regeneration. *Terraform/CI*: no CI exists in the project; a
maintainer-run script matches FR-009's "executable by the
maintainer".

## R-012 — Storage and scale feasibility (spec edge cases)

**Decision**: R2 free tier holds the data (~164 MB) with 10 GB head
room; Class B ops (10M/month) cover tile serving; egress is free.
The blog and email remain on Hostinger's existing plan (untouched;
their limits are out of scope). Storage head room is checked by the
deploy script before upload.

**Rationale**: Confirmed R2 free tier: 10 GB-month storage, 1M
Class A / 10M Class B ops, zero egress. Worker free tier:
100k invocations/day — only data-file requests invoke the Worker.
The Hostinger plan's storage is unaffected by this feature (the
bundle never touches Hostinger).

**Alternatives considered**: *Put the whole bundle on Hostinger*:
rejected by the clarification (map hosted on Cloudflare).

## R-013 — Unsupported-browser and mixed-content behavior preserved (FR-012, FR-003)

**Decision**: No bundle change: the no-WebGL-2 behavior ships
unchanged; the bundle references only HTTPS external sources
(verified: CSP `default-src 'self'`, basemap tiles and glyphs over
HTTPS — prior research R-009 stands). The success gate re-checks
the console for mixed-content errors at `/map/`.

**Rationale**: FR-012 is client-side behavior a static server cannot
change; the deployment must not alter the bundle (SC-007). The only
new network surface is Cloudflare's edge serving `/map/` over HTTPS
(Universal SSL, apex + www) — no plain-HTTP references exist to
break.

**Alternatives considered**: none — no bundle change is permitted.

## R-014 — OR-005 and governance (project rules)

**Decision**: No large files enter git: `dist/` stays gitignored;
R2 uploads stream from local `dist/`; new repo files are small text
(`wrangler.toml`, `index.js`, `scripts/deploy-cf.sh`). OR-004 commit
discipline unchanged (plan via `make commit-plan`, slices via
`make commit-slice`).

**Rationale**: The project rule OR-005 forbids tracking `*.pmtiles`
and >50 MiB files; the Cloudflare deploy never requires them in git
(the Hostinger-era design already respected this; the Cloudflare
design keeps it).

## Consolidated decisions

- Serving: one Worker, routes `abu-hamad.de/map*` (+ www) →
  canonical `https://abu-hamad.de/map/`; shell = Workers static
  assets (free, unlimited); data = R2 binding with native 206
  passthrough; no Pages, no bucket custom domain (hostname-scoped).
- Atomicity: `r2 object put` per object (atomic), `wrangler deploy`
  last step (atomic version switch); interrupted upload → previous
  version live; rollback = `wrangler rollback` + re-upload previous
  data from kept local archives.
- Cache: `no-cache` + `no-transform` on data, assets default
  revalidate — never stale after a deploy; no edge cache on data.
- DNS: inventory → recreate at Cloudflare (A blog grey, MX/SPF/
  DMARC/DKIM DNS-only) → stage routes → GoDaddy NS switch → Active +
  Universal SSL → orange + Full (strict); FR-014 email/blog gate
  before declaring success.
- Tooling: `workers/map/` + `scripts/deploy-cf.sh`; no `src/`
  changes; SC-007 byte-identity preserved.
