# Feature Specification: Host Site on Personal Domain (abu-hamad.de)
**Feature Branch**: `005-host-on-personal-domain`
**Created**: 2026-08-04
**Status**: Draft
**Input**: User description: "we need to prepare and perform correctly the deployment of the site on my personal domain from hostinger https://abu-hamad.de/"

## Clarifications

### Session 2026-08-04

- Q: Should the map site stay at https://abu-hamad.de/ as its address, or may the domain redirect to an externally hosted site? → A (REVISED 2026-08-04, confirmed): The map must NOT take the domain root — the root stays with the WordPress blog and the abu-hamad.de email. The map lives at the sub-path `https://abu-hamad.de/map` and is hosted on Cloudflare, rendering AT that path (Cloudflare serves /map; the root keeps the blog and email; no redirect to a foreign URL). The earlier answer "site at the domain root" was based on a misunderstanding.
- Q: Which free/cheap platform serves the site under the custom domain? → A: Cloudflare — Pages hosts the site shell; a public R2 bucket hosts the PMTiles/GeoJSON data files (free tier, Range-serving, atomic deploys).
- Q: Are you OK with moving the domain's nameservers to Cloudflare (free plan)? → A: Yes, move nameservers to Cloudflare. Note (2026-08-04): the registrar is GoDaddy (not Hostinger), and Hostinger hosts the WordPress blog and, critically, the abu-hamad.de email — email and blog continuity must be preserved across the DNS move.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Public Access at the Personal Domain (Priority: P1)

A visitor who has never seen the project types `https://abu-hamad.de/map` into a browser. The German-language Mannheim tree-cover map site loads at that address: the page title, header, legend, and map viewport appear, and the dark-themed base map with colored buildings is visible without any manual setup.

**Why priority**: This is the core of the request — without the site being publicly reachable at the personal domain, nothing else in this feature has value.

**Independent Test**: Open `https://abu-hamad.de/map` in a fresh browser profile and confirm the site renders instead of an error page, directory listing, or placeholder.

**Acceptance Scenarios**:

1. **Given** the deployment is complete, **When** a visitor opens `https://abu-hamad.de/map` in any modern browser, **Then** the published tree-cover map site loads and renders.
2. **Given** the deployment is complete, **When** a visitor opens the site, **Then** all visible texts are in German and match the locally published version.
3. **Given** the deployment is complete, **When** a visitor opens the `www` variant of the domain, **Then** the browser lands on the same site (redirected to one canonical address) without an error.
4. **Given** the deployment is complete, **When** a visitor opens the site on a phone, **Then** the site renders at the supported narrow viewport without broken layout.

### User Story 2 - Fully Functional Interactive Map (Priority: P1)

A visitor on the live site pans and zooms the map, clicks a building and reads its tree-cover popup, and toggles the `Bäume` tree layer. Every interaction behaves exactly as it does on the locally published bundle — buildings keep their colors, the popup opens with the correct value, and the tree layer appears/disappears on toggle. All map data layers (buildings, trees, boundary) load over the network, including at deep zoom levels.

**Why priority**: A map site that renders but whose data layers fail to load is broken for its primary purpose. This story proves the hosting environment serves the tile data correctly.

**Independent Test**: On the live site, pan, zoom, click a building, and toggle the tree layer; confirm each interaction succeeds.

**Acceptance Scenarios**:

1. **Given** the live site is loaded, **When** a visitor pans and zooms across Mannheim, **Then** the map stays responsive and buildings render at every zoom level.
2. **Given** the live site is loaded, **When** a visitor clicks a building, **Then** a popup opens showing the same tree-cover value as the local bundle.
3. **Given** the live site is loaded, **When** a visitor toggles the `Bäume` layer, **Then** tree polygons appear and disappear immediately.
4. **Given** the live site is loaded, **When** a visitor zooms to the deepest zoom level, **Then** building details continue to render (tile data is fully served, not truncated).

### User Story 3 - Secure HTTPS Delivery (Priority: P2)

A visitor opens `https://abu-hamad.de/map` and the browser shows a valid HTTPS connection: no certificate warning, no "not secure" indicator, no mixed-content blocking. The padlock is present on first load.

**Why priority**: Browsers warn on insecure or mixed-content pages, which would erode trust and could block map assets entirely. Secure delivery is a precondition for the site being usable by the public.

**Independent Test**: Load the site and inspect the browser address bar for a valid certificate with no warnings; check the console for mixed-content errors.

**Acceptance Scenarios**:

1. **Given** the deployment is complete, **When** a visitor loads the site, **Then** the browser reports a valid HTTPS certificate with no security warning.
2. **Given** the site is served over HTTPS, **When** the page loads, **Then** no asset request is blocked as mixed content.
3. **Given** the site is loaded, **When** a visitor clicks the padlock, **Then** the certificate details are valid and issued for the domain.

### User Story 4 - Acceptable Performance on a Real Connection (Priority: P2)

A visitor on a typical broadband connection (throttled to 25 Mbps with 50 ms latency, as used in the project's published performance record) loads the site. The first usable map appears within the project's established budget of 10 seconds, and map interactions (popup, zoom, toggle) respond within 2 seconds.

**Why priority**: The tile bundle is large on disk (~171 MB); correct range-request serving is what keeps first paint small. If the host does not serve partial content correctly, load times explode and the site is effectively unusable.

**Independent Test**: Load the live site under the throttled profile used in `validation/perf-budget.json` and measure time to first usable map and interaction latency.

**Acceptance Scenarios**:

1. **Given** a throttled 25 Mbps / 50 ms connection, **When** a visitor opens the site, **Then** the first usable map appears within the 10-second budget.
2. **Given** the live site is loaded, **When** a visitor clicks a building or toggles the tree layer, **Then** the interaction responds within the 2-second budget.
3. **Given** the live site, **When** a visitor pans to an unvisited area, **Then** new tiles load progressively without the whole page blocking.

### User Story 5 - Repeatable, Safe Updates (Priority: P3)

The maintainer builds a new version of the site and wants to publish it to the personal domain. Following a documented deployment procedure, the new bundle is uploaded and the live site switches to it. Visitors never see a half-uploaded site; if the upload fails partway, the previous version remains live.

**Why priority**: The domain is the permanent home of the project; publishing new features (like the brightness slider from feature 004) must be a routine, low-risk operation.

**Independent Test**: Run the documented deployment procedure with a modified bundle; confirm the live site serves the new content and that an interrupted upload leaves the old version intact.

**Acceptance Scenarios**:

1. **Given** a documented deployment procedure, **When** the maintainer follows it with a newly published bundle, **Then** the live site serves the new version.
2. **Given** an upload interrupted mid-way, **When** a visitor loads the site, **Then** the previous complete version is still served (no broken intermediate state).
3. **Given** the deployment procedure, **When** the maintainer runs it, **Then** it completes without manual edits to the live server's file layout.

### Edge Cases

- Domain DNS records point at the host but have not propagated yet: visitors see the host's default page or an error until propagation completes; the deployment procedure must state how to confirm propagation.
- The hosting plan's SSL certificate is not yet issued or has expired: browsers show a certificate warning; the procedure must verify a valid certificate after setup.
- The hosting service does not serve partial-content (Range) requests for the PMTiles layers: the map renders but tile data never appears; the procedure must verify partial-content serving before declaring success.
- A stale version is served from browser/proxy cache after an update: visitors on old sessions may see the previous version until reload; cache headers or versioned assets must handle this.
- The upload of the ~171 MB bundle is interrupted: partial files must never be served as the live site.
- Storage or bandwidth limits of the hosting plan are exceeded: upload fails or the site becomes unreachable; the procedure must account for the bundle size against plan limits.
- A visitor's browser lacks WebGL 2: the site must show its existing unsupported-browser behavior instead of a blank map.
- Mixed content: any asset referenced over plain HTTP on the HTTPS page is blocked; all references must be served over HTTPS.
- Both `abu-hamad.de` and `www.abu-hamad.de` must resolve consistently; no duplicate content or broken redirect loops.
- Email or blog outage during the DNS migration: moving nameservers to Cloudflare must not break the Hostinger-hosted abu-hamad.de email or the WordPress blog; MX/SPF/DMARC and blog records are migrated to Cloudflare before the switch and verified afterwards (FR-014).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site MUST be publicly reachable over HTTPS at `https://abu-hamad.de/map`, rendered at that path (Cloudflare serves it under the domain; no redirect to an external URL); the domain root remains the WordPress blog and the email service (REVISED 2026-08-04).
- **FR-002**: The site MUST be served with a valid HTTPS certificate for the domain such that browsers show no security warning.
- **FR-003**: The `www` variant of the domain MUST resolve to the same site via a single canonical redirect, with no redirect loop.
- **FR-004**: The live site MUST serve the same content as the locally published bundle (`make publish` output), including identical German texts, styling, and behavior.
- **FR-005**: All map data layers (buildings, trees, boundary mask) MUST load on the live site at all zoom levels.
- **FR-006**: The interactive map on the live site MUST support pan, zoom, building popups, and the `Bäume` toggle with behavior identical to the local bundle.
- **FR-007**: The live site MUST serve map data via partial-content (Range) requests so that only the requested viewport tiles are transferred.
- **FR-008**: On a throttled 25 Mbps / 50 ms connection, the first usable map MUST appear within 10 seconds and interactions MUST respond within 2 seconds.
- **FR-009**: A documented, repeatable deployment procedure MUST exist and MUST be executable by the maintainer to publish updated bundles.
- **FR-010**: Updating the live site MUST NOT expose visitors to a partially uploaded version; the previous complete version MUST remain served until the new version is fully in place.
- **FR-011**: The deployment MUST NOT add analytics, tracking, server-side components, or a database; the site remains a plain static bundle.
- **FR-012**: The deployment MUST preserve the existing unsupported-browser (no WebGL 2) behavior rather than failing silently.
- **FR-013**: The deployment MUST verify, before declaring success, that DNS resolves, the certificate is valid, HTTPS serves the site, and partial-content requests work.
- **FR-014**: The deployment MUST NOT break the existing `abu-hamad.de` email service (Hostinger) or the WordPress blog during the DNS migration; their DNS records (MX, SPF, DMARC; blog host records) are migrated to Cloudflare and verified before the nameserver switch.

### Key Entities *(include if feature involves data)*

- **Published Site**: the version of the site currently live at the personal domain; visitors interact with exactly one complete version at a time.
- **Deployment Bundle**: the complete static output of the project's publish step (HTML, styles, scripts, map data, attribution); the unit that is uploaded and replaced atomically.
- **Personal Domain**: the canonical public address (`abu-hamad.de`) with its DNS records and HTTPS certificate; the stable identity of the live site.
- **Hosting Environment**: the platform serving the map path (Cloudflare: site shell + R2 data) alongside the existing Hostinger services (WordPress blog, email) at the domain root; constrained by storage, bandwidth, and protocol support (partial content, HTTPS).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of test loads of `https://abu-hamad.de/map` in modern browsers render the map site with no error page, placeholder, or directory listing.
- **SC-002**: 100% of interactive checks (pan, zoom, building popup, tree toggle) pass on the live site at all zoom levels.
- **SC-003**: Browser loads of the live site show a valid HTTPS certificate with zero security warnings and zero mixed-content errors.
- **SC-004**: On a throttled 25 Mbps / 50 ms connection, first usable map appears in under 10 seconds and interactions respond in under 2 seconds, matching the project's published performance budget.
- **SC-005**: The documented deployment procedure publishes an updated bundle successfully on the first attempt without manual server-side file edits.
- **SC-006**: An interrupted deployment leaves the previously live version fully functional (zero visitor-visible downtime from failed updates).
- **SC-007**: The live site's visible content matches the locally published bundle byte-for-byte for all text and structure (no unintended content drift during deployment).

## Assumptions

- The personal domain `abu-hamad.de` is registered at GoDaddy (registrar). Its DNS currently serves Hostinger-hosted services: a WordPress blog and the abu-hamad.de email. The map site is NOT served from Hostinger's web hosting; it is served by Cloudflare — Pages hosts the site shell, a public R2 bucket hosts the PMTiles/GeoJSON data files (clarified 2026-08-04). Nameservers move from Hostinger to Cloudflare (free plan, set at GoDaddy); MX/SPF/DMARC records for email and the blog's records are migrated to Cloudflare BEFORE the switch so email and the blog keep working. The map's deployment target is a sub-path of the domain, not the root (REVISED 2026-08-04).
- The deployment target is the sub-path `https://abu-hamad.de/map` (REVISED 2026-08-04), NOT the root — the root remains the WordPress blog and the email service; the map renders at the path (Cloudflare serves it; no redirect to an external URL).
- The hosting environment provides HTTPS (free certificate) and supports partial-content (Range) requests for the PMTiles layers; the plan verifies both and falls back only if verification fails.
- The deployable artifact is the static bundle produced by the project's publish step (`dist/`, ~171 MB on disk), with no build step required on the host.
- The site remains German-language and static: no server-side rendering, no analytics, no database — consistent with the project's existing constraints.
- Deployment is performed by the repository maintainer, who has credentials to the hosting account; the documented procedure targets that audience.
- Browsers used to verify the deployment are modern and WebGL 2-capable, matching the project's stated prerequisites.

## Dependencies

- `make publish` produces the deployable `dist/` bundle (documented in README "Publish + static hosting").
- The PMTiles layers require HTTP byte serving (Range requests); the README explicitly notes that a plain static server without Range support will not serve the map data — hosting verification must cover this.
- The project's published performance record (`validation/perf-budget.json`, measured at 25 Mbps / 50 ms: first usable map 2.5 s vs 10 s budget, interactions 80–211 ms vs 2 s budget) is the reference for SC-004.
- The live site must remain consistent with prior accepted features (darkened base map 003, map UI/brightness/legend 004) already present in the bundle.
