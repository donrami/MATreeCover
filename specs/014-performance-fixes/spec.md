# Feature Specification: Performance Fixes

**Feature Branch**: `main`
**Created**: 2026-08-08
**Status**: Draft
**Input**: User description: "we need to plan and properly implement the performance fixes without introducing new bugs"

## Scope

### Goal

Ship the performance audit findings (`validation/perf-audit-2026-08-08.md`) without regressing any existing behavior. The map must load and respond faster on repeat visits and on low-end mobile hardware. Every existing interaction, value, color, and label stays identical.

### Current State (evidence)

- Lighthouse 13.4.1 lab (2026-08-08): mobile score 67, TBT 6310 ms, LCP 2459 ms, FCP 900 ms, CLS 0, TTFB 50 ms. Desktop score 81, TBT 420 ms, LCP 0.5 s.
- 20 long tasks of 229-973 ms during load, all attributed to maplibre-gl.js (1034 ms scripting, 8496 ms total). The initial z10.9 view renders 12,570 building polygons.
- buildings.pmtiles and trees.pmtiles are served with `cache-control: no-store, no-transform` (scripts/deploy-cf.sh lines 91-92). No browser or edge caching of range responses.
- index.html, main.js, style.css, style.json are served with `cache-control: public, max-age=0, must-revalidate`. Four conditional requests per visit.
- Two render-blocking stylesheets sit in the head: style.css (5.1 KB brotli) and vendor/maplibre-gl.css (10 KB).
- maplibre-gl.js (940 KB, 248 KB transfer) is fetched at the end of the body and not preloaded.
- Basemap tiles (sgx.geodatenzentrum.de, 34 requests, 1412 KB on mobile) are fetched without preconnect. The origin caches tiles for 3 days.
- No favicon: browsers request /favicon.ico and get a 404.
- The map already passes its own SC-008 time budget (first usable 1388 ms vs 10 s) and all 8 interactions (3-123 ms vs 2 s budget) on desktop-class hardware.

### In Scope

- Cache headers for the PMTiles archives. Browser and edge caching enabled, no-transform preserved.
- Content-hashed static asset filenames with long-lived immutable caching. The HTML keeps revalidation.
- Main-thread load reduction. Cross-fade disabled at init, simplified low-zoom building geometry in the published buildings.pmtiles.
- Critical-path improvements. Preload the map library. Preconnect to the basemap origin. Move stylesheets out of the render-blocking path. Add a favicon.
- Regression gates. Full test suite, deploy verification, image sanity, interaction latency re-measurement, value parity.

### Out Scope

- Field monitoring or RUM (FR-001: no tracking).
- WebP/AVIF basemap tile proxy (needs server infrastructure, conflicts with the static architecture).
- buildings.geojson housekeeping (56 MB unused R2 object, storage only, no user impact, separate change).
- Any value, palette, label, popup, or interaction change.
- Desktop-specific tuning beyond what the shared fixes deliver.

## User Scenarios & Testing

### User Story 1 - Repeat Visits Load Fast (Priority: P1)

A visitor who already opened the map returns within days. The page and the tiles re-render from cache instead of re-downloading, so the map appears noticeably faster on slow connections.

**Why priority**: repeat visits are the common case for a reference map. The audit showed the entire 2.3 MB mobile payload re-downloads on every visit because the range responses are uncacheable.

**Independent Test**: Load the page twice on the throttled profile (150 ms RTT, 1.6 Mbps). Record network bytes and map-ready time on both runs. Verify the second run transfers under 100 KB same-origin and that repeated pmtiles range requests hit the edge cache.

**Acceptance Scenarios**:
1. **Given** a visitor loads the map once, **When** they load it again within the cache TTL, **Then** no previously fetched pmtiles range is re-transferred and the same-origin transfer is under 100 KB.
2. **Given** a fresh pmtiles range request, **When** repeated within the cache TTL, **Then** the edge serves it (cf-cache-status HIT) with a correct 206 Content-Range.
3. **Given** a newly deployed bundle, **When** a visitor loads it, **Then** the new hashed assets are fetched exactly once and subsequent loads reuse them without revalidation round trips.
4. **Given** a visitor loads the map, **When** the HTML is revalidated, **Then** the browser still checks for a newer version on each navigation (max-age=0 on the document).

### User Story 2 - Low-End Phones Can Use the Map (Priority: P1)

On a phone-class CPU, the map becomes interactive without minutes of blocked main thread. Buildings still appear with identical colors and values.

**Why priority**: the mobile lab profile (4x CPU throttle) showed 6.3 s of main-thread blocking. That is a failing Core Web Vital and a real low-end-device experience.

**Independent Test**: Run the Lighthouse mobile profile before and after. Verify TBT under 1.5 s and LCP under 2.0 s. Then compare rendered tiles and building values for visual and data parity.

**Acceptance Scenarios**:
1. **Given** the mobile lab profile, **When** the page loads cold, **Then** TBT is under 1.5 s (was 6310 ms) and LCP is under 2.0 s (was 2459 ms).
2. **Given** the map at initial city scale, **When** buildings render, **Then** every building keeps its exact value and color. Only outline density may differ.
3. **Given** a zoom into z14, **When** buildings render, **Then** geometry is identical to the current bundle, with no simplification visible at street scale.
4. **Given** the map during zoom or pan, **When** a frame transitions, **Then** no cross-fade artifacts appear and the transition renders directly.
5. **Given** the mobile profile, **When** a building, district, or toggle interaction happens after load, **Then** the interaction settles within the existing 2 s budget.

### User Story 3 - First Load Starts Faster (Priority: P2)

The first visit on any device shows the map shell sooner. The map library download starts earlier, the basemap connection is pre-warmed, and no stylesheet blocks the first paint.

**Why priority**: first impressions, and the audit's critical-path findings. These are cheap, low-risk wins.

**Independent Test**: Record FCP and the request waterfall on the throttled profile. Verify the map library request starts before body parsing. Verify the basemap connection uses a pre-warmed socket. Verify no external stylesheet blocks first paint.

**Acceptance Scenarios**:
1. **Given** a cold load, **When** the HTML parses, **Then** the map library download begins before the parser reaches the end-of-body script tag.
2. **Given** a cold load, **When** the basemap tiles are requested, **Then** the connection to the basemap origin is already open.
3. **Given** a cold load, **When** first paint happens, **Then** no render-blocking stylesheet request delays it.
4. **Given** a cold load, **When** the browser requests the site icon, **Then** it receives a valid icon (HTTP 200), not a 404.

### User Story 4 - Deploys Stay Safe (Priority: P2)

Maintainers ship the fixes knowing every existing gate passes and the map still looks and behaves identically.

**Why priority**: the user explicitly requires the fixes without new bugs. This story makes that requirement testable.

**Independent Test**: Run the full acceptance suite, the deploy verification gate, and the interaction re-measurement. Diff rendered tiles before and after the geometry rebuild.

**Acceptance Scenarios**:
1. **Given** the code changes, **When** the test suite runs, **Then** every existing test passes and the acceptance suite (FR-021 per artifact) passes.
2. **Given** a deploy, **When** the FR-013/FR-014 gates run, **Then** Range 206, redirects, cache headers, cert, DNS, and email continuity checks all pass.
3. **Given** the rebuilt buildings.pmtiles, **When** image sanity runs, **Then** no artifacts appear (no missing, degenerate, or misaligned buildings).
4. **Given** the rebuilt buildings.pmtiles, **When** values are re-checked, **Then** the tree-share values match the current bundle exactly.
5. **Given** the published site, **When** the interaction latency harness runs, **Then** all 8 interactions stay within the 2 s budget and the desktop median stays at or below the current 123 ms.

### Edge Cases

- Mid-visit archive re-upload: a browser may hold cached ranges up to the TTL while the R2 object changes. The map tolerates this because values are unchanged and geometry converges on the next visit. Keep the data TTL at one day.
- Stale hashed assets after rollback: if a deploy rolls back, old hashed files are gone from the bundle. The HTML references only current hashes, so no mixed-version load can occur.
- Cloudflare range caching: the worker supports single-range requests only (existing contract). Edge caching must not corrupt Content-Range. Keep no-transform set and re-verify 206 responses after the header change.
- Over-simplification: at city scale, very small buildings could collapse. The acceptance gates (feature parity per tile, image sanity) catch this. The simplification level is chosen conservatively.
- fadeDuration zero: MapLibre must accept 0 without error and render direct transitions. Verified in the browser during acceptance.
- CSP: the inline stylesheet is allowed by the existing style-src 'unsafe-inline' policy. Preload and preconnect are same-origin or already allow-listed (connect-src covers sgx.geodatenzentrum.de).
- Favicon: the icon must be self-hosted. The CSP img-src allows 'self' and data:.
- Mobile 360 px viewport: no layout or popup change is in scope. Nothing here alters the DOM structure.
- Cold-cache measurement variance: TBT and LCP are lab values. Acceptance uses the same Lighthouse 13.4.1 profile and three runs, taking the median.

## Requirements

### Functional Requirements

- **FR-001**: Data archives (buildings.pmtiles, trees.pmtiles) MUST be served with cache headers that allow browser and edge caching for at least one day, while preserving no-transform and correct HTTP Range (206) passthrough.
- **FR-002**: Static assets (main.js, style.css, style.json, vendor scripts and styles) MUST be served with content-hashed filenames and long-lived immutable caching (one year).
- **FR-003**: The HTML document MUST keep revalidation semantics (max-age=0 or no-cache) so every deploy reaches visitors immediately.
- **FR-004**: The map MUST render its initial view without cross-fade animation passes.
- **FR-005**: The published buildings.pmtiles MUST use simplified geometry at low zoom levels (city scale) that is visually equivalent to the current bundle.
- **FR-006**: Building tree-share values MUST be identical after the geometry rebuild. Geometry density is the only permitted change.
- **FR-007**: The map library download MUST start before the parser reaches the end-of-body script.
- **FR-008**: The page MUST pre-warm the connection to the basemap tile origin.
- **FR-009**: No external stylesheet MUST block first paint (styles inlined or preloaded).
- **FR-010**: The site MUST serve a valid favicon (no 404).
- **FR-011**: All existing behaviors MUST remain unchanged: popup arbitration (one popup, last click wins), tree toggle, district popups, city overview, brightness slider, German labels, click arbitration.
- **FR-012**: The deploy verification gates (Range 206, redirects, cache headers, cert, DNS, email continuity) MUST pass after the change.
- **FR-013**: The acceptance suite and image sanity checks MUST pass for the rebuilt archives.
- **FR-014**: The interaction latency measurements MUST stay within the existing budgets (2 s per interaction, all 8 interactions).
- **FR-015**: The mobile lab metrics MUST meet: TBT under 1.5 s and LCP under 2.0 s on the audit's Lighthouse profile.

### Key Entities

- **buildings.pmtiles**: the 34 MB building layer archive. Gains cache headers and simplified low-zoom geometry. Source of building values (unchanged).
- **trees.pmtiles**: the 80 MB tree layer archive. Gains cache headers only.
- **Static asset bundle**: index.html plus hashed main.js, style.css, style.json, and vendor files. The HTML is the only un-hashed, always-revalidated entry point.
- **R2 data objects**: storage for the archives. Their HTTP metadata controls the cache behavior.
- **Edge cache (Cloudflare)**: caches range responses and text assets. Verified via cf-cache-status.

## Success Criteria

Measurable Outcomes

- **SC-001**: Lighthouse mobile performance score is at least 85 (was 67) with TBT under 1.5 s and LCP under 2.0 s (median of 3 runs).
- **SC-002**: Lighthouse desktop performance score does not drop below 81 and TBT stays under 500 ms.
- **SC-003**: A repeat visit on the throttled profile transfers under 100 KB same-origin. At least 90 % of previously fetched pmtiles ranges are served with zero network bytes.
- **SC-004**: A repeated pmtiles range request is served from the edge cache (cf-cache-status HIT) with a correct 206 Content-Range.
- **SC-005**: All 8 interactions stay within the 2 s budget. The desktop interaction median stays at or below 123 ms.
- **SC-006**: Rendered output is visually equivalent after the geometry rebuild. No missing or degenerate buildings at z10-z14, image sanity passes, and building values match the current bundle exactly.
- **SC-007**: Every existing automated test and deploy gate passes (test suite, acceptance suite, FR-013/FR-014 verification).
- **SC-008**: The favicon request returns HTTP 200 on the published site.

## Assumptions

- Lab measurement with Lighthouse 13.4.1 (the audit's profile) and the repo's headless interaction harness remains the acceptance method. The SC-008 time-budget precedent in validation/perf-budget.json continues to hold.
- Cloudflare's edge caches single-range 206 responses when cache-control allows it and no-transform is set. If this assumption fails during implementation, the fallback is browser-only caching, with SC-004 adjusted.
- A data cache TTL of one day balances staleness and hit rate. An immutable asset TTL of one year is safe because filenames are content-hashed and the worker deploys atomically.
- The geometry rebuild keeps the pipeline's existing acceptance rules (manifest, artifact completeness). Only tippecanoe simplification parameters change at low zooms.
- No RUM is added (FR-001: no tracking). Field verification remains out of scope.
- The basemap origin remains sgx.geodatenzentrum.de and keeps its current tile size and format. No proxy is introduced.
