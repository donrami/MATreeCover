# Deployment Procedure Contract (Cloudflare)

**Branch**: `005-host-on-personal-domain` | **Date**: 2026-08-04
**Source**: `spec.md` FR-009/FR-010, research R-002/R-003/R-006/
R-007. **Entities**: E-001 (PublishedMapSite), E-005
(CloudflareRelease).

This contract defines how the static bundle is published to
`https://abu-hamad.de/map/` such that visitors never see a
half-uploaded site and an interrupted upload leaves the previous
version live (FR-010, SC-006).

## 1. Cloudflare layout (after one-time setup)

```text
Cloudflare zone abu-hamad.de (free, full setup)
├── DNS: A @ → Hostinger IP (proxied), A www → Hostinger IP (proxied)
│        MX 5 mx1.hostinger.com / MX 10 mx2.hostinger.com (DNS-only)
│        TXT SPF / TXT _dmarc / DKIM CNAMEs (DNS-only)
├── Routes (→ one Worker, name: matreecover-map):
│   abu-hamad.de/map           abu-hamad.de/map/*
│   www.abu-hamad.de/map       www.abu-hamad.de/map/*
├── Worker matreecover-map
│   ├── assets.directory = dist/          (small files, < 25 MiB)
│   └── R2 binding DATA → matreecover-data
└── R2 bucket matreecover-data
    ├── buildings.pmtiles  (application/vnd.pmtiles,   no-cache, no-transform)
    ├── trees.pmtiles      (application/vnd.pmtiles,   no-cache, no-transform)
    └── buildings.geojson  (application/geo+json,      no-cache)
```

## 2. Atomicity invariants

- Data upload and activation are separate steps: the R2 objects are
  uploaded and checksum-verified FIRST; the Worker version is
  activated LAST with `wrangler deploy` (one atomic operation that
  switches traffic to the new version at once).
- An interrupted `r2 object put` leaves the previous object intact
  (single PUT is atomic per object); the release stays staged and
  is never referenced.
- An interrupted `wrangler deploy` never creates a deployment (the
  direct-upload flow activates only at the completion token); the
  previous version keeps serving.
- The live docroot/`/map/` path is never written to incrementally —
  there is no partial state to observe.

## 3. Deploy sequence (`scripts/deploy-cf.sh`)

1. **Build**: `make publish` must succeed (refuses on pending/fail
   required inputs). `dist/` is the release source.
2. **Identity**: compute the local manifest — sorted file list,
   per-file `sha256`, total bytes, file count.
3. **Storage check**: data size vs the R2 free tier (10 GB-month)
   and Worker limits; abort if the margin is insufficient (spec
   edge case).
4. **Upload data**: `wrangler r2 object put` for
   `buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson` with
   the content-types and cache headers of `hosting-config.md` §2.
   Each PUT is atomic; an interrupted transfer leaves the previous
   object live and the release staged.
5. **Verify data BEFORE activation**: read back the objects
   (checksums or `wrangler r2 object get` + sha256) and compare
   against the identity manifest. Any mismatch → abort; live
   unchanged.
6. **Activate**: `wrangler deploy` from `workers/map/` (uploads
   code + assets, then activates the new version atomically).
7. **Post-deploy verify** (live, `hosting-config.md` §3):
   `/map` → 301 `/map/`; `/map/` 200 with the bundle's
   `Cache-Control`; a Range request on `buildings.pmtiles` returns
   206; `www.abu-hamad.de/map` 301s to the canonical; the blog
   root still loads. On failure → rollback (step 9).
8. **Record and prune**: write `validation/deploy-<ts>.json`
   (release id, sha256s, deploy time, verification results); keep
   the last 3 `dist-archive/<ts>/` copies, delete older.
9. **Rollback**: `wrangler rollback` (immediate new deployment of
   the previous Worker version), then re-upload the previous
   release's three R2 objects from the kept `dist-archive`, then
   re-verify live.

## 4. One-time setup (bootstrap — see `dns-https.md`)

DNS inventory → Cloudflare zone created (records grey) → routes +
Worker staged (inert) → nameservers switched at GoDaddy → zone
Active → Universal SSL Active → blog records proxied + SSL mode
Full (strict) → FR-014 gate (email send/receive, blog) passes.
Only after the FR-013/FR-014 gates pass is the deployment declared
successful.

## 5. Verification gates (before declaring success — FR-013)

- DNS resolves for apex and www (`dig` at two public resolvers).
- `/map` 301s to `/map/`; `/map/` serves 200 over HTTPS with a
  valid certificate for both hostnames.
- A Range request on `buildings.pmtiles` returns 206 with a correct
  `Content-Range` (FR-007).
- `index.html` and the data files are served with
  `Cache-Control: no-cache` (or asset revalidation headers) — no
  stale version after updates.
- Bundle identity matches `dist/` (sha256) — SC-007.
- Visible content and interactions match the local bundle
  (quickstart Scenarios 1–2).
- Email and the blog keep working (FR-014; `dns-https.md` §5).

## 6. Non-goals

- No server-side components beyond static-file serving, no
  database, no analytics (FR-011) — the Worker serves assets and
  R2 objects only.
- No build step on Cloudflare (the bundle is pre-built by
  `make publish`; the Worker is plain JS, no npm build).
- No changes to the bundle's file names or contents; assets come
  straight from `dist/` and data URLs stay relative under `/map/`
  (SC-007).
- The WordPress blog and email are never touched by a map deploy
  (E-004, FR-014).
