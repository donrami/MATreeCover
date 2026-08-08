# Performance audit — abu-hamad.de/map/

Audit date: 2026-08-08
Audited page: https://abu-hamad.de/map/ (production, Cloudflare Worker + R2)

## Verdict

- Lighthouse performance score: 67 mobile, 81 desktop.
- One metric fails the Core Web Vitals thresholds: Total Blocking Time 6.3 s mobile.
- LCP 2.45 s mobile sits exactly at the good threshold. CLS is 0. TTFB is 50 ms.
- The site passes its own SC-008 time budget on desktop-class hardware (perf-budget.json: 1.4 s vs 10 s budget).
- The risk is low-end mobile CPU and repeat-visit caching, not the network edge.

## Method

- Lighthouse 13.4.1 in headless Chromium 150.
- Mobile preset: Moto G Power emulation, 4x CPU throttle, 1.6 Mbps, 150 ms RTT, cold cache.
- Desktop preset: no throttling, cold cache.
- Independent CDP run: 4x CPU throttle, 150 ms RTT, 1.6 Mbps, cleared cache. It measured LCP 2.25 s, FCP 0.5 s, CLS 0, TTFB 33 ms.
- Response headers inspected with curl. Worker and deploy sources reviewed.
- Thresholds from web.dev (LCP 2.5 s, INP 200 ms, CLS 0.1).
- Score weights from the Lighthouse scoring docs (TBT 30%, LCP 25%, CLS 25%, FCP 10%, Speed Index 10%).
- No CrUX field data exists for this domain. This is a lab-only audit.

## Critical findings

### C1 — Main-thread CPU cost of the initial map render (score driver)

Evidence:

- TBT 6310 ms mobile (the 200 ms good threshold, 600 ms needs-improvement threshold).
- 20 long tasks between 229 ms and 973 ms during load, all attributed to maplibre-gl.js.
- maplibre-gl.js bootup: 1034 ms scripting, 8496 ms total main-thread time.
- Main-thread breakdown: Other 7784 ms, Script Evaluation 1540 ms, Style and Layout 229 ms.
- The initial z10.9 view renders 12,570 building polygons (perf-budget.json) plus 34 basemap tiles.

Impact: TBT carries 30% of the score. Reducing TBT to 1.5 s alone moves the mobile score from 67 to about 85. Reducing it to 600 ms moves the score to about 95.

Fixes, in order of impact:

Fix: rebuild buildings.pmtiles with stronger geometry simplification at low zoom levels (tippecanoe). The city-scale view does not need every building vertex. This is the largest CPU lever. It needs a pipeline rebuild, a re-upload, and the SC-008 re-measurement.
2. Set `fadeDuration: 0` in the Map constructor. This removes the 300 ms cross-fade render pass at init. One line in main.js.
3. Optional: start the buildings layer hidden and reveal it after the first frame. This moves perceived load but does not cut total work.

### C2 — PMTiles responses are uncacheable (repeat visits and pan/zoom)

Evidence: both pmtiles objects carry `cache-control: no-store, no-transform` (curl headers, and scripts/deploy-cf.sh lines 91-92). No browser cache. No Cloudflare edge cache. Every pan, zoom, and repeat visit re-downloads the same tile bytes from the R2 origin.

Impact: a repeat mobile visit still transfers about 2.3 MB. Pan and zoom tile latency is one R2 round trip instead of a cache hit. The PMTiles range-request architecture only pays off when the ranges are cached.

Fix: upload with `cache-control: public, max-age=86400, stale-while-revalidate=604800`. Keep `no-transform`. Cloudflare needs it to cache range responses without corruption. Verify with `cf-cache-status: HIT` on a repeated range request. One line in deploy-cf.sh, then re-run `scripts/deploy-cf.sh verify`.

### C3 — Text assets revalidate on every load

Evidence: `cache-control: public, max-age=0, must-revalidate` on index.html, main.js, style.css, and style.json. Each visit issues four conditional requests.

Impact: about 4 RTTs (roughly 600 ms on the mobile profile) added to every repeat load.

Fix: content-hash the filenames at publish time (main-<hash>.js, style-<hash>.css) and serve them with `max-age=31536000, immutable`. Keep the HTML at max-age=0. Worker deploys are atomic. Stale hashed files cannot mix.

## Medium findings

### M1 — Render-blocking CSS

style.css (5.1 KB brotli) and maplibre-gl.css (10 KB) block first paint. Lighthouse attributes 150 ms of waste to them. Inline style.css into the HTML, or preload maplibre-gl.css. Estimated FCP saving: 100-200 ms mobile.

### M2 — maplibre-gl.js is on the critical path and not preloaded

248 KB transfer, 940 KB on disk, 1034 ms scripting on the throttled CPU. A `<link rel="preload" as="script">` in the head starts the download one RTT earlier. Cheap, small LCP gain.

### M3 — Basemap payload is 1.4 MB (61 percent of mobile transfer)

34 PNG tiles from sgx.geodatenzentrum.de at 65-118 KB each. The host sends no Timing-Allow-Origin, so resource timing hides these sizes. Cheap fix: preconnect to sgx.geodatenzentrum.de (saves about 2 RTTs of tile arrival). A WebP or AVIF tile proxy would be the real lever. It conflicts with the no-server static architecture.

### M4 — No favicon

index.html has no icon link. Browsers request /favicon.ico and get a 404. One wasted request and console noise.

### M5 — Dead R2 asset

buildings.geojson (56 MB) is uploaded but never referenced by main.js or style.json. It costs R2 storage only, no user impact. Keep it for the pipeline or delete it.

## What is already good

- TTFB 36-50 ms, served from the Cloudflare edge (cf-cache-status HIT).
- CLS 0. Layout shifts are eliminated.
- FCP 0.5 s desktop, 0.9 s mobile.
- Brotli compression active (main.js 29.5 KB to 9.8 KB).
- HTTP/2, zero third-party scripts, strict CSP.
- Interactions measured at 3-123 ms on desktop hardware (perf-budget.json).
- The basemap origin caches tiles for 3 days (public max-age=259200).
- First paint fetches 409 KB of a 34 MB buildings archive via range requests.

## Notes

INP could not be measured directly. This harness disables PerformanceEventTiming delivery. INP triangulates from TBT and the repo's interaction measurements. Desktop INP is fine. Mobile INP degrades with the same main-thread contention as TBT. Fixing C1 protects INP.

Field data would require real-user monitoring. The site promises no tracking (FR-001). A self-hosted, cookieless web-vitals beacon is possible but optional.

## Recommended order

1. C2 caching fix. One line, immediate repeat-visit win.
2. C1 geometry simplification plus fadeDuration. The score driver.
3. C3 hashed assets.
4. M1-M4 quick wins.

Estimated combined effect: mobile score 67 to about 90, repeat-visit transfer 2.3 MB to about 100 KB.
