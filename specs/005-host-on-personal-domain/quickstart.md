# Quickstart — Host on Personal Domain

**Branch**: `005-host-on-personal-domain` | **Date**: 2026-08-04

End-to-end validation guide for the deployment of the published
bundle to `https://abu-hamad.de/map/` on Cloudflare, with the
domain root (WordPress blog) and email staying on Hostinger.
Every scenario is a pass/fail check against the clarified spec's
user stories, acceptance scenarios, and success criteria
SC-001..SC-007 plus FR-014. Contracts:
`contracts/deployment.md`, `contracts/hosting-config.md`,
`contracts/dns-https.md`, `contracts/bundle.md`; entities in
`data-model.md`; design rationale in `research.md`.

## Prerequisites

- Cloudflare account (free plan is sufficient) with the
  `abu-hamad.de` zone added and the Worker + routes staged
  (`contracts/hosting-config.md` §1).
- GoDaddy access (registrar — nameserver switch) and Hostinger
  hPanel access (DNS zone inventory; blog and email stay there).
- Local machine: repo checkout, `make publish` working, `npx
  wrangler` (≥ 3.98.0, pinned in `workers/map/package.json`)
  logged in, and `curl`, `dig`, `openssl`.
- A modern browser with WebGL 2; browser devtools with throttling.

## Setup (one-time bootstrap — `contracts/dns-https.md` §3)

1. Inventory every record from the Hostinger DNS Zone Editor;
   corroborate with `dig @1.1.1.1 abu-hamad.de {A,MX,TXT,NS}`;
   save as `validation/dns-migration-<ts>.json`.
2. Create the Cloudflare zone (free, full setup); reconcile the
   imported records — blog A records grey, email records DNS-only.
3. Deploy the Worker and the four routes (inert until activation).
4. Change nameservers at GoDaddy to Cloudflare's two NS; wait for
   the zone to flip to Active (first check ~60 s, then growing
   intervals; up to 48 h globally).
5. After Universal SSL shows Active: flip the blog A records to
   proxied (orange) and set SSL mode **Full (strict)**.
6. Run Scenario 7 (FR-014 gate) — the deployment is not declared
   successful until it passes; then Scenario 6 (FR-013 gate).

Then each release:

```text
git checkout 005-host-on-personal-domain
bash scripts/deploy-cf.sh   # publish → r2 put ×3 → verify → wrangler deploy → verify
```

## Scenario 1 — Public access at the map path (US1, FR-001, FR-003,
FR-004, SC-001, SC-007)

**Maps to**: user story 1, all acceptance scenarios.

1. In a fresh browser profile (no cache), open
   `https://abu-hamad.de/map/`.
2. **Pass criteria**:
   - The tree-cover map site renders at the path — no error page,
     directory listing, or placeholder (SC-001); the address bar
     stays on `abu-hamad.de/map/` (no redirect to a foreign URL).
   - All visible texts are German and match the locally published
     bundle (`dist/`): title "Baumfläche", controls
     "Bäume"/"Helligkeit", legend with unit "Prozent",
     attribution (FR-004, SC-007). Compare side-by-side with the
     local bundle served via nginx.
   - `https://abu-hamad.de/map` (no slash) 301s to `/map/`; the
     page loads.
   - `https://www.abu-hamad.de/map/` 301s to
     `https://abu-hamad.de/map/` (single canonical redirect,
     FR-003).
   - At a 360 px viewport (devtools device mode), the map renders
     without broken layout (US1 acceptance 4).
   - The domain root `https://abu-hamad.de/` still shows the
     WordPress blog — the map does not displace it.
3. Byte-level check (SC-007):
   ```sh
   curl -s https://abu-hamad.de/map/index.html | sha256sum
   sha256sum dist/index.html
   ```
   The two hashes match; the same holds for `style.css`,
   `main.js`, `style.json`, `attribution.html` and the R2 data
   files (the deploy record runs this for the full bundle).

## Scenario 2 — Fully functional interactive map on the live site
(US2, FR-005, SC-002)

**Maps to**: user story 2.

1. On `https://abu-hamad.de/map/`: pan, zoom to deep zoom levels
   (z16–z18), click buildings, toggle `Bäume`.
2. **Pass criteria**:
   - Buildings keep their palette colors at all zoom levels; data
     layers load over the network at deep zoom (FR-005).
   - Clicking a building opens the popup with the correct value;
     click on empty space closes it (matches local behavior).
   - Toggling `Bäume` shows/hides the tree layer immediately.
   - The network tab shows 206 responses for the `.pmtiles` range
     requests (FR-007).
3. Repeat the project's manual smoke checklists against the live
   URL: `tests/frontend/smoke_us1.md`, `smoke_us2.md` (popup),
   `smoke_us3.md` (tree toggle), `smoke_us4.md` (UI overlap) — all
   pass on live (SC-002).

## Scenario 3 — Secure HTTPS delivery (US3, FR-002, SC-003)

**Maps to**: user story 3, all acceptance scenarios.

1. Load `https://abu-hamad.de/map/` in the browser.
2. **Pass criteria**:
   - Address bar shows the padlock on first load; no "not secure"
     indicator, no certificate warning (US3 acceptance 1).
   - Clicking the padlock: certificate is valid and covers
     `abu-hamad.de` and `www.abu-hamad.de` (check by loading
     `https://www.abu-hamad.de/map/` — no warning before the
     301) (US3 acceptance 3).
   - Browser console shows zero mixed-content errors; every
     request in the Network tab is HTTPS (US3 acceptance 2).
   - Command-line corroboration:
     ```sh
     curl -v https://abu-hamad.de/map/ 2>&1 | grep -i 'SSL certificate verify ok'
     ```

## Scenario 4 — Performance budget on the live site (US4, SC-004)

**Maps to**: user story 4.

1. Re-run the project's published measurement method
   (`validation/perf-budget.json` documents it) against
   `https://abu-hamad.de/map/`: Chromium headless, CDP
   `Network.emulateNetworkConditions` latency 50 ms / download 25
   Mbps, cold cache per run; time-to-first-usable = navigation
   start → map `load` + buildings source loaded + buildings
   rendered; interaction latencies for popup, zoom, tree toggle.
2. **Pass criteria**:
   - First usable map ≤ 10 s (local reference: 2.5 s).
   - Interactions ≤ 2 s each (local reference: 80–211 ms).
   - Record the result under `validation/live-perf.json` with the
     same schema as `perf-budget.json` (SC-004).
3. The `no-cache` contract adds revalidation round-trips only; if
   the budget fails, verify throttle/cold-cache first, then
   investigate R2 latency — never "fix" it by long-caching the
   data files (contract invariant, `hosting-config.md` §2).

## Scenario 5 — Repeatable deploy, interruption safety, rollback
(US5, FR-009, FR-010, SC-005, SC-006)

**Maps to**: user story 5, all acceptance scenarios.

1. Make a trivial content change (e.g. a visible German text edit
   in `src/site/index.html`), `make publish`, and run
   `bash scripts/deploy-cf.sh`. It must complete without any manual
   edit of the Cloudflare config (FR-009 acceptance 3, SC-005) and
   write `validation/deploy-<ts>.json`.
2. **Pass criteria**:
   - The live site at `/map/` shows the changed text; the Worker
     deployment is the new version; the previous version is
     reachable via `wrangler rollback` (FR-009 acceptance 2).
   - Byte-identity gate: live files match the new local `dist/`
     (SC-007).
3. **Interrupted-upload drill** (FR-010, SC-006): start a deploy
   and kill the `r2 object put` for `trees.pmtiles` mid-transfer.
   - **Pass criteria**: the live site still serves the previous
     version fully functional (SC-006); the interrupted object
     retains its previous checksum (PUT atomicity); no partial
     data is ever referenced.
4. **Rollback drill**: `wrangler rollback`, then re-upload the
   previous release's R2 objects from `dist-archive/`
   (`contracts/deployment.md` §3.9).
   - **Pass criteria**: `/map/` immediately serves the previous
     version; verification gates pass again.
5. Verify the old symlink-era procedure (`scripts/deploy.sh`) is
   gone — replaced by `deploy-cf.sh` (clean cutover, R-011).

## Scenario 6 — FR-013 success gate (DNS, cert, redirects, Range,
cache)

**Maps to**: spec Functional Requirements FR-013 and edge cases
(DNS propagation, SSL not issued, Range unsupported, stale cache).

Run before declaring any deployment successful:

```sh
# DNS resolves for both hostnames (edge: propagation up to 24–48 h)
dig +short abu-hamad.de A
dig +short www.abu-hamad.de A

# Map path: 200, canonical 301s, no redirect loop, no-cache headers
curl -sI https://abu-hamad.de/map/ | head -8        # 200, Cache-Control: no-cache
curl -sI https://abu-hamad.de/map   | head -3       # 301 → /map/
curl -sI https://www.abu-hamad.de/map/ | head -5   # 301 → https://abu-hamad.de/map/

# Range/partial-content works for the PMTiles layers (FR-007)
curl -s -D - -o /dev/null -H 'Range: bytes=0-1023' \
  https://abu-hamad.de/map/buildings.pmtiles | head -8   # 206, Content-Range

# Certificate valid for both hostnames (edge: not issued / expired)
echo | openssl s_client -servername abu-hamad.de -connect abu-hamad.de:443 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
# repeat with -servername www.abu-hamad.de; both list abu-hamad.de + www
```

**Pass criteria**:

- Both hostnames resolve; `/map/` serves 200; `/map` and the www
  variant produce exactly one 301 to the canonical URL (FR-003).
- `buildings.pmtiles` Range request returns `206 Partial Content`
  with a correct `Content-Range` (FR-007, FR-013) — if not, check
  the R2 object headers (content-type, `no-transform`) and that the
  route hits the Worker.
- Certificate validates for both hostnames with future expiry
  (FR-002); if "not yet issued", wait for Universal SSL to reach
  Active and re-check.
- `index.html` and the data files are served with
  `Cache-Control: no-cache` (or revalidation headers) — no stale
  version after updates (spec edge case).

## Scenario 7 — FR-014 gate (email + blog continuity)

**Maps to**: spec FR-014 and the DNS-migration edge case.

```sh
dig +short abu-hamad.de NS                    # Cloudflare NS only
dig @8.8.8.8 abu-hamad.de NS                  # same (second resolver)
dig +short abu-hamad.de MX                     # mx1/mx2.hostinger.com, 5/10
dig +short abu-hamad.de TXT                    # SPF includes _spf.mail.hostinger.com
dig +short _dmarc.abu-hamad.de TXT             # DMARC policy present
dig +short abu-hamad.de A                      # Hostinger blog IP
```

1. **Pass criteria**:
   - The blog loads at `https://abu-hamad.de/` over HTTPS, before
     and after the proxy flip (TLS mode Full (strict)).
   - Mail receive: send a test message from an external account to
     a Hostinger mailbox; confirm delivery in webmail
     (`https://mail.hostinger.com`).
   - Mail send: reply to an external address; headers show
     SPF=pass, DKIM=pass, DMARC=pass (e.g. via mail-tester.com).
   - The record inventory in `validation/dns-migration-<ts>.json`
     matches the live Cloudflare zone (FR-014).
2. The nameserver migration is rolled back at GoDaddy immediately
   if any of these fail (the Hostinger zone was never modified).

## What to do when a scenario fails

- Scenario 1 failure (path 404 or blog shown at /map): check the
  routes in `wrangler.toml` (`abu-hamad.de/map` + `/map/*`) and
  that the apex A record is proxied (routes run on proxied
  traffic, `hosting-config.md` §3); check the Worker deployment
  is active.
- Scenario 2 failure (layers missing at depth): verify 206 on the
  `.pmtiles` (Scenario 6); if missing, check the R2 object
  `no-transform` header and the binding; never move the data to
  Workers assets (no guaranteed 206, research R-002/R-003).
- Scenario 3 failure (cert warning / mixed content): check the
  zone is Active and Universal SSL is Active (records were grey
  until then); check the console for the blocked resource —
  every external source is HTTPS by design (`dns-https.md` §4).
- Scenario 4 failure (perf): re-verify throttle/cold-cache first;
  then measure R2 latency. Never long-cache the data files to
  "fix" it (`hosting-config.md` §2).
- Scenario 5 failure (deploy broke live): `wrangler rollback`
  immediately (`contracts/deployment.md` §3.9); if the flip
  itself failed, check `wrangler deploy` output and the asset
  upload — an interrupted upload never activates.
- Scenario 6/7 failure: any red line blocks declaring success —
  resolve per the listed cause; never skip the gates.
- Do not declare the deployment successful until Scenarios 1, 2,
  3, 6, and 7 pass, and Scenario 4's record is written.
