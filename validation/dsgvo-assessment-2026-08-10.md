# DSGVO / TDDDG Conformity Assessment — MATreeCover (Baumfläche Mannheim)

- **Date:** 2026-08-10
- **Target:** live production at https://abu-hamad.de/map/ and its two info pages
- **Method:** read-only source review (`src/site/`, `workers/map/`, `src/endpoint/`); cross-check against DSGVO (EU 2016/679), §25 TDDDG (DE), DSK "OH Digitale Dienste" v1.2 guidance; behavior review of third-party request flow at runtime via CSP `img-src` / `font-src` / `connect-src` allowlists; no production change.
- **Branch:** `research/dsgvo-cookies-conformity` — research artifact, no code committed to other paths.

## Executive verdict

**Conformity status: LOW residual risk. The site is tracking-free by design. The remaining work is *disclosure* (Art. 13 DSGVO) and three small hardening items, not behavioral change.**

What the codebase already does right:

- Zero cookies set or read (no `document.cookie`, no `Set-Cookie` from Worker).
- Zero analytics, no telemetry, no error-reporting beacon.
- Zero fingerprinting (no canvas/WebGL hash, no device enumeration).
- Zero server-side personal data collection (Worker is static asset + R2 range passthrough; inference endpoint loopback-only).
- Only one `localStorage` key, written only on explicit user dismissal of the first-visit story modal — exempt under §25(2) Nr. 2 TDDDG as strictly-necessary functional storage.
- No third-party **scripts** (CSP `script-src 'self'`); no Ko-fi widget, no iframe, no tracking pixel.
- Permissions-Policy already disables camera, microphone, geolocation, payment, usb, `interest-cohort` (FLoC).
- Strict CSP, `Referrer-Policy: strict-origin-when-cross-origin`, HSTS, `X-Frame-Options: DENY` on every Worker response (feature 015).

What needs work:

1. **No standalone Datenschutzerklärung page** — the Impressum contains only a short paragraph that omits the third-party recipients that receive technically-required connection data. This is the primary DSGVO gap (Art. 13 transparency obligation).
2. **Third-party recipients not disclosed** to visitors: Cloudflare (edge/CDN), basemap.de (BKG/LGL tiles), MapLibre demo glyph CDN, Ko-fi (image + outbound link).
3. **MapLibre demo glyph CDN** (`demotiles.maplibre.org`) — accepted medium risk per `src/site/vendor/PROVENANCE.md` (owner sign-off 2026-08-08). Either self-host the glyphs or name the recipient with a contractual basis (DPA / legitimate interest) in the Datenschutzerklärung.
4. **README claim "nothing leaves the browser" is wrong** — BKG tile fetches, MapLibre glyph fetches, and the Ko-fi image each transmit IP + UA. Soften the wording.
5. **TDDDG §25(2) Nr. 2 exemption for `matreecover.story-dismissed`** — defensible but should be documented in the spec/contract so a reviewer can verify the strictly-necessary argument.
6. **Ko-fi link** — currently `rel="noopener"`. Add `rel="noopener noreferrer"` (and ideally `rel="noopener noreferrer nofollow sponsored"` for outbound monetization) so the page's referrer and any SEO equity are not transmitted; Ko-fi sets its own cookies when it loads, this is independent of the link attributes but the link attributes limit what the *page* sends.
7. **Right-to-information / right-to-erasure channel** — Impressum already names `rami@abu-hamad.de`. Reuse that email in the new Datenschutzerklärung (Betroffenenrechte, Art. 13(2)(b) and Art. 15/17).
8. **JSON-LD `Organization`** embeds the owner's name + email, which is permissible for an Organization node (public attribution). No fix needed; consider adding `contactPoint` only if a public-facing support contact is desired.

No cookie banner is required, and none should be added. A banner would imply non-essential storage the site does not have, undermining the privacy claim.

## Current data flow (art. 5(1)(f) DSGVO inventory)

| Origin | Direction | Data carried | Trigger | Storage | Lawful basis / rationale |
|--------|-----------|--------------|---------|---------|--------------------------|
| Cloudflare edge (abu-hamad.de) | Browser → Worker → R2 | Client IP, UA, timestamp, request path | Every request | Cloudflare standard logging (DPA, EU region) | Art. 6(1)(f) legitimate interest — service delivery; Art. 28 AV-Vertrag required |
| `abu-hamad.de/map/*` static | Browser ← Worker | None personal | Page load | None server-side | — |
| `sgx.geodatenzentrum.de` (basemap.de BKG) | Browser → BKG | Client IP, UA, tile z/x/y | Map init / pan / zoom | BKG technical logs | Art. 6(1)(f) — public-sector open-data service, strictly required to render the map |
| `demotiles.maplibre.org` | Browser → MapLibre | Client IP, UA, glyph range | Map label rendering | MapLibre demo infra | Art. 6(1)(f) — accepted risk (PROVENANCE.md); mitigate by self-hosting or naming recipient |
| `storage.ko-fi.com` | Browser → Ko-fi CDN | Client IP, UA, referrer (`abu-hamad.de`) | Page load | None from this image; Ko-fi sets cookies on its own site after click | Art. 6(1)(f) — donation button image; outbound link to Ko-fi carries its own consent |
| `ko-fi.com/M4Q624RYOV` (outbound) | Browser → Ko-fi | Client IP, UA, referrer | Click on donation button | Ko-fi cookies/analytics | Outside our control; disclose to user before click |
| `abu-hamad.de/map/stadtteile.geojson`, `boundary.geojson`, `buildings.pmtiles`, `trees.pmtiles`, `buildings.geojson` (R2) | Browser ← Worker (Range passthrough) | None personal | Map init | R2 object storage only | — |
| `localStorage` (`matreecover.story-dismissed`) | Browser only | On-device key `'1'` | Click ✕ / Escape on story modal | On device, never leaves browser | §25(2) Nr. 2 TDDDG — strictly necessary functional storage |

No data is sold, no profiling, no automated decision-making, no transfer to third countries outside what is disclosed above.

## Applicable framework

- **DSGVO (EU 2016/679)** — applies to the processing of personal data of EU residents; the site processes IP addresses and User-Agent strings on every request (Cloudflare, BKG, MapLibre, Ko-fi), so the regulation applies to the owner as the controller for the site's own hosting (Cloudflare is processor under Art. 28).
- **§25 TDDDG (Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz)** since 2024-05-14 — covers any access to or storage of information on the user's end device. The site's only end-device write is the `localStorage` key `matreecover.story-dismissed`. Classified as **strictly necessary** under §25(2) Nr. 2 because the story modal explicitly re-appears on every visit without storage, and the key is the documented mechanism that prevents the re-show. The write happens only on explicit user action (close button or Escape), never on page load or auto-show.
- **DSK "OH Digitale Dienste" v1.2** (Orientierungshilfe der Datenschutzaufsichtsbehörden) — guidance for site operators on §25 application, granular analysis used below.
- **Breyer ruling (EuGH C-582/14)** — IP addresses are personal data when the controller has the legal means to identify the user. The page operator (Rami Abu-Hamad) can be considered a controller for the site's own processing (asset delivery); recipients (Cloudflare, BKG, MapLibre, Ko-fi) act as separate controllers or processors.

## Findings

### H1 — Missing Datenschutzerklärung (Art. 13 DSGVO). **Severity: HIGH.**

The site has only an Impressum with a one-paragraph "Datenschutz" note stating that "keine aktive Erhebung personenbezogener Daten" happens. That statement is technically true, but it does not name the recipients that *technically* receive connection data (Cloudflare edge, BKG basemap.de, MapLibre demo glyph CDN, Ko-fi CDN, Ko-fi as outbound link), it does not name the controller's contact, and it does not enumerate the data subject's rights. German practice since the DSK and various Landesdatenschutzbehörde rulings treats this as a procedural breach even where the substantive processing is minimal.

**Fix:** Create `src/site/datenschutz.html`. Mirror the same template (`<title>`, `<h1>`, visible prose) as `attribution.html` and `impressum.html`. Link it from the legal link in the footer (currently `<a class="legal-link" href="impressum">Impressum</a>` → add a second link to Datenschutz). Add it to `src/site/sitemap.xml` and `src/site/robots.txt` allowlist in feature 016 (which already audits and gates these files).

Required content blocks (minimally):

1. **Verantwortlicher** — full name, address, email (reuse the Impressum block).
2. **Beauftragter / Datenschutzbeauftragter** — not mandatory for a small site (below the §38 BDSG threshold or just not required for private sites that don't process sensitive data at scale). State "nicht benannt" or "nicht erforderlich" with a brief justification.
3. **Zwecke und Rechtsgrundlagen der Verarbeitung** — service delivery (Art. 6(1)(b)/(f)), third-party tile serving (Art. 6(1)(f)).
4. **Empfänger / Drittländertransfer** — name each: Cloudflare Inc. (US, with adequacy via EU-U.S. Data Privacy Framework; DPA in place), BKG (DE, public body), MapLibre demo CDN, Ko-fi (US). For each: what data, retention (if known), legal basis.
5. **Speicherdauer** — none on the server; cloudflare logs per Cloudflare DPA; local storage key persisted until cleared by the user; how the user can clear localStorage (browser-specific or generic instruction).
6. **Betroffenenrechte (Art. 13(2)(b), Art. 15–22)** — access, rectification, erasure, restriction, portability, objection. Right to lodge complaint with the competent Landesdatenschutzbehörde: Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Baden-Württemberg (poststelle@lfdi.bwl.de), since the operator resides in BW. Confirm jurisdiction by checking the Impressum.
7. **Quellen der Daten** — IP, UA, timestamp are derived from the visitor's browser on every request; no active collection.
8. **Cookies / localStorage** — explicit statement: "Diese Website setzt keine Cookies. Es wird ausschließlich ein localStorage-Eintrag `matreecover.story-dismissed` gesetzt, und nur, wenn Sie das Story-Fenster aktiv schließen. Rechtsgrundlage: §25(2) Nr. 2 TDDDG (technisch erforderlich)."
9. **Keine automatisierten Entscheidungen / kein Profiling (Art. 22).**

Update the footer legal link to surface both `<a href="impressum">Impressum</a>` and `<a href="datenschutz">Datenschutzerklärung</a>`.

### H2 — Impressum privacy paragraph under-discloses. **Severity: HIGH (rolled into H1).**

Current wording: short paragraph claiming "es findet keine aktive Erhebung personenbezogener Daten statt", then mentions tiles come "direkt vom BKG". The mention of BKG is good. The mention of Cloudflare is missing. The mention of MapLibre demo glyphs is missing. The mention of Ko-fi (image and outbound link) is missing.

**Fix:** the new `datenschutz.html` covers this fully. Impressum can keep its short paragraph but should link to Datenschutz: "Mehr Informationen finden Sie in der Datenschutzerklärung." and stop claiming that "no active collection" implies no connection data leaves the browser.

### M1 — README "nothing leaves the browser" claim misleading. **Severity: MEDIUM.**

The README marketing-style sentence (paraphrased) — "There is no server. There is no database. There is no analytics behind it." — is true for the owner's own code, but visitors will read it as "nothing I do here is observed". Three outbound recipients observe them: Cloudflare edge, BKG, Ko-fi.

**Fix:** soften the wording in `README.md`. Replace any sentence that implies zero egress with a precise sentence such as: "The site itself does no analytics, sets no cookies, and stores no personal data. Map tiles are loaded from a federal open-data service (BKG basemap.de), the site is served through Cloudflare, and the optional donation button image is hosted on Ko-fi's CDN — each receives the visitor's IP and User-Agent as part of standard HTTP, as documented in the Datenschutzerklärung." Add the `Datenschutzerklärung` link.

### M2 — `matreecover.story-dismissed` strictly-necessary argument is undocumented. **Severity: MEDIUM.**

The localStorage key is written only on explicit user dismissal and read on every page load; without it, the story modal re-appears every visit. The exemption in §25(2) Nr. 2 TDDDG applies to storage that is "absolutely required" for the user-initiated service. The story-modal dismissal is a user-requested service (don't re-show what I've already read), but the argument needs to be on paper.

**Fix:** Update `specs/007-first-visit-story/contracts/dismissal-state.md` to include the §25 TDDDG argument in the "Storage" section: one paragraph citing the section and noting (a) the write happens only on explicit user action, (b) without storage the user's expressed dismissal intent cannot be honored across reloads, (c) no alternative mechanism is equally user-friendly (a server-side preference would itself require tracking). Reference this assessment.

### M3 — Ko-fi link attributes. **Severity: MEDIUM.**

Current: `<a class="ko-fi" href="https://ko-fi.com/M4Q624RYOV" target="_blank" rel="noopener">`. `rel="noopener"` blocks `window.opener` (good). Missing `noreferrer` (Referrer-Policy at the HTTP layer already limits the referrer to origin, but `rel="noreferrer"` on the link is belt-and-suspenders) and missing `nofollow sponsored` (cleanest SEO disclosure for an outbound monetization link; not a DSGVO issue per se but the DSK recommends honest outbound-link labelling).

**Fix:** change to `rel="noopener noreferrer nofollow sponsored"`. Trivial one-line patch.

### M4 — MapLibre demo glyph CDN not self-hosted; not disclosed. **Severity: MEDIUM.**

The PROVENANCE.md already flags this as a documented medium-risk dependency (owner sign-off 2026-08-08). The path is to either:

**(a) Self-host.** Fetch the glyph range files once at build time, vendor them under `src/site/vendor/glyphs/`, update the `glyphs` URL in `src/site/style.json` to point at the same-origin path. Removes the third-party recipient entirely; no consent gate required.

**(b) Disclose and stay.** Add the recipient to the new `datenschutz.html`. Document the legal basis (Art. 6(1)(f) legitimate interest — the map cannot render labels otherwise). Note that MapLibre's demotiles host is not a contracted sub-processor; it is an external controller. The DSK position on third-party resources that are not strictly necessary for the service itself (e.g. analytics) is that legitimate interest is rarely sufficient. Map labels are arguably strictly necessary for the map's purpose, but the argument is weaker than for basemap tiles.

**Recommended:** self-host in a follow-up feature (e.g. feature 018). For this assessment, **(b)** with the new Datenschutzerklärung page covering MapLibre is acceptable as a transitional state.

### M5 — Cloudflare edge logs not disclosed. **Severity: MEDIUM.**

Cloudflare by default retains edge logs at the edge for a bounded period (operationally up to ~7 days for security/abuse, contracted under Cloudflare's DPA / SCCs). The site uses Cloudflare as the CDN (Worker + DNS) per `workers/map/index.js`. The owner is the controller; Cloudflare is a processor under Art. 28.

**Fix:** the new Datenschutzerklärung must name Cloudflare as a processor (Art. 13(1)(e)), and point at Cloudflare's Data Processing Addendum (https://www.cloudflare.com/cloudflare-customer-data-processing-addendum/). Confirm DP Framework coverage for EU residency (Cloudflare is on the EU-U.S. Data Privacy Framework list).

### M6 — No telemetry about consent / privacy changes visible to users. **Severity: LOW.**

Privacy policies should include a "letzte Aktualisierung" date so visitors see freshness. Not required by Art. 13 but a DSK best practice.

**Fix:** add a "Stand: 2026-08-10" line at the bottom of the new Datenschutzerklärung page.

### L1 — `style-src 'unsafe-inline'`. **Severity: LOW (not a privacy finding; informational).**

Inline styles are used (e.g. `style="left:0%"` ticks). Risk-classified as low. Standard CSP hardening would be `'unsafe-inline' 'nonce-…'`. Out of scope for the DSGVO assessment; mention only.

### L2 — `interest-cohort=()` in Permissions-Policy already off — good. **Severity: LOW.**

The header already disables Topics API. No FLoC / Topics exposure. Mention only as positive evidence.

### L3 — JSON-LD `Organization` exposes owner name + email publicly. **Severity: LOW.**

This is a deliberate public attribution and aligned with the Impressum (§5 DDG requires the operator's name and contact). The JSON-LD doesn't add new personal data — it mirrors what's already public. No change required.

### L4 — `<a>` story modal SPIEGEL / GitHub outbound links are `rel="noopener"`. **Severity: LOW.**

Cosmetic — could add `noreferrer` and `nofollow` to keep all outbound links consistent. The HTTP Referrer-Policy already limits to origin-only. Trivial; bundle with M3 if convenient.

## Things explicitly checked and found CONFORMING (no change)

- ✅ **No cookies** anywhere (Worker response, JS, HTML).
- ✅ **No analytics.** CSP `script-src 'self'`; only three `<script>` tags (`maplibre-gl.js`, `pmtiles.js`, `main.js`), all `src/site/vendor/` or local. No gtag/GA/Matomo/Plausible/Umami. `MapLibre GL` has no default telemetry.
- ✅ **No fingerprinting.** No `canvas.toDataURL`, no `getImageData` hash, no `WebGLRenderingContext` enum, no `navigator.userAgent` collection, no battery/network/enumerateDevice calls.
- ✅ **No geolocation API.** Permissions-Policy explicitly disables it; no `navigator.geolocation.*` anywhere.
- ✅ **No third-party scripts.** All CSP restrictions hold. No iframe, no Ko-fi widget, no embed.
- ✅ **No server-side personal data** — Worker does static asset serving + R2 Range passthrough only. No application logs, no DB, no analytics endpoint.
- ✅ **RunPod inference endpoint** (`src/endpoint/server.py`) — bound to 127.0.0.1; not reachable from the public site; bounded by 1 MiB request cap. Already verified by feature 015 security audit.
- ✅ **Vendored libraries** with declared hashes in `src/site/vendor/PROVENANCE.md`.
- ✅ **CSP mirrors the `<meta>` tag byte-for-byte** in HTML and Worker (FR-004).
- ✅ **HTTP security headers** on every Worker response (FR-004): CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, HSTS.
- ✅ **HSTS** with `max-age=31536000` (≥1 year). DSK recommends ≥1 year; OK.
- ✅ **X-Frame-Options: DENY** — clickjacking protected; no embedding of the map in third-party frames.

## Concrete action checklist (priority order)

| # | Action | Severity | Effort | Artifact | Notes |
|---|--------|----------|--------|----------|-------|
| 1 | New `src/site/datenschutz.html` covering Art. 13 blocks listed in H1 | HIGH | 1–2h | New file | Follow `impressum.html` template; add to sitemap/robots (already covered by feature 016) |
| 2 | Footer legal link: add `Datenschutzerklärung` next to `Impressum` | HIGH (with #1) | 5 min | `src/site/index.html` | One-line addition |
| 3 | Ko-fi link `rel="noopener noreferrer nofollow sponsored"` | MED | 5 min | `src/site/index.html` | Bundle with #2 |
| 4 | Update `specs/007-first-visit-story/contracts/dismissal-state.md` with §25 TDDDG short justification | MED | 15 min | Existing spec file | Spec.md update, no JS change |
| 5 | Soften "nothing leaves" wording in `README.md` and feature 017 spec | MED | 15 min | Markdown | Editorial |
| 6 | Self-host MapLibre glyphs (transitional disclosure if not done) | MED (transitional) | ~1 day | `src/site/vendor/glyphs/`, `src/site/style.json` glyphs URL, CSP tightening | See L1 below |
| 7 | Add Story-modal SPIEGEL/GitHub outbound links `noreferrer nofollow` (consistency) | LOW | 5 min | `src/site/index.html` | Optional |
| 8 | "Stand: 2026-08-10" stamp on the new `datenschutz.html` | LOW | 1 min | New file | Built-in with #1 |

Steps 1–3, 5, 7, 8 can ship as a single small feature (e.g. `018-dsgvo-disclosure`). Step 4 is a doc-only update. Step 6 is independent and may be deferred.

## Cited sources

- Verordnung (EU) 2016/679 (DSGVO), insb. Art. 5, 6, 13, 22, 28, 32.
- Gesetz über den Datenschutz und den Schutz der Privatsphäre in der Telekommunikation und bei digitalen Diensten (TDDDG), § 25 (Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz) — https://www.gesetze-im-internet.de/ttdsg/__25.html
- DSK — Orientierungshilfe der Aufsichtsbehörden für Anbieter:innen von digitalen Diensten (OH Digitale Dienste), Version 1.2 — https://www.datenschutzkonferenz-online.de/media/oh/OH_Digitale_Dienste.pdf
- EuGH C-582/14 (Breyer) — IP-Adressen als personenbezogene Daten
- Cloudflare Data Processing Addendum — https://www.cloudflare.com/cloudflare-customer-data-processing-addendum/
- BKG / basemap.de Nutzungsbedingungen — dl-de/by-2-0; https://gdz.bkg.bund.de/
- e-recht24 — "Cookie-Einwilligung nach TDDDG & DSGVO" — https://www.e-recht24.de
- Dr. DSGVO — "Cloudflare: Datentransfers und die DSGVO" — https://dr-dsgvo.de/cloudflare-datentransfers-und-die-dsgvo
- legalweb.io — "Cloudflare DSGVO konform einsetzen" — https://legalweb.io/dsgvo/cdn_cloudflare

## Verification of this assessment

- All claims about cookies/tracking/fingerprinting are sourced from a read-only scout of `src/site/*`, `workers/map/*`, and `src/endpoint/*` on 2026-08-10 (artifact `agent://ScoutDSGVO`); cross-verified by direct `grep` over the static files.
- All claims about headers/CSP match the byte-exact values in `src/site/index.html` and `workers/map/index.js`.
- No production changes made; this artifact is read-only research for `research/dsgvo-cookies-conformity`.
