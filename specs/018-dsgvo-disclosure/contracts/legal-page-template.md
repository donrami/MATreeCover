# Contract: Legal / Info Page Template

Target: `src/site/impressum.html`, `src/site/attribution.html`, `src/site/datenschutz.html` (new). The shared template that all three info pages follow so the document set feels coherent and renders identically across the four pages (front page + 3 info pages).

## Purpose

The site's three info pages are static German HTML documents that share the same visual, structural, and accessibility contract. The fourth page (`datenschutz.html`) is a new instance of this template. The contract is the editorial and engineering rule that the new page MUST follow, so the existing layout-overlap matrix, accessibility lint, and template-parity checks stay green.

## Template rules

### `<head>` block

The new page contains the following `<meta>` tags, in this order:

| Tag | Value | Rationale |
|-----|-------|-----------|
| `<meta charset="utf-8">` | UTF-8 | Standard. |
| `<meta name="viewport" content="width=device-width, initial-scale=1">` | Responsive viewport | Standard. |
| `<meta name="description" content="...">` | German description | SEO + accessibility. |
| `<link rel="canonical" href="https://abu-hamad.de/map/datenschutz">` | Canonical URL | Mirrors the existing pages. |
| `<meta property="og:title" content="Datenschutzerklärung – Mannheim Baumfläche">` | OpenGraph title | Mirrors the existing pages. |
| `<meta property="og:description" content="...">` | OpenGraph description | SEO + link sharing. |
| `<meta property="og:url" content="https://abu-hamad.de/map/datenschutz">` | OpenGraph URL | Mirrors the existing pages. |
| `<meta property="og:type" content="website">` | OpenGraph type | Mirrors the existing pages. |
| `<meta property="og:image" content="https://abu-hamad.de/map/og-image.png">` | OpenGraph image | Mirrors the existing pages. |
| `<meta name="twitter:card" content="summary_large_image">` | Twitter card type | Mirrors the existing pages. |
| `<meta name="theme-color" content="#0e1414">` | Dark mode theme color | Mirrors the existing pages. |

The `<title>` element MUST read "Datenschutzerklärung – Mannheim Baumfläche". The `<html lang="de">` MUST be set.

### `<style>` block

The new page contains the same in-line `<style>` block as `src/site/impressum.html`, byte-for-byte. The block defines the dark-mode color scheme, the typography, the back-link, and the max-width 40 rem `<main>` wrapper. No new rules are added.

### `<body>` block

The new page contains:

1. A `<main>` element with the content.
2. An `<h1>` element reading "Datenschutzerklärung".
3. The 9 content blocks in FR-002 order, each in plain German. Each is a `<section>` with a `<h2>` heading.
4. A back-link `<a href="../">← Zur Karte</a>` outside the `<main>` (or at the bottom of `<main>`; mirror the existing pattern).

The back-link `←` arrow is decorative and conveys no semantic information. The back-link MUST be keyboard-reachable in tab order from the footer link and from the page heading.

### Footer block

The new page does NOT contain a footer with a legal-link group. A back-link to the map is sufficient. The existing `impressum.html` and `attribution.html` pages also do not have a footer legal-link group; the legal-link group is only on the front page's footer.

### Color scheme

The new page uses the same dark-mode color scheme as the existing info pages:

- Background: `#0e1414` (deep dark green).
- Foreground: `#e3e8e8` (off-white).
- Heading: `#ffffff`.
- Link: `#9fc4ff` (light blue).
- Link hover: `#c4d8ff`.
- Focus: a 2 px solid outline in the same blue.

These values are inherited from the existing `<style>` block in `impressum.html`. No new color is introduced.

### Accessibility

- The page is keyboard-navigable. Every interactive element is reachable in tab order, with a visible focus indicator.
- The page has a `<h1>` (the document title) followed by `<h2>` (the content-block headings). The heading hierarchy is strict.
- The page has no `<img>` elements (no alt-text needed).
- The page has no ARIA overrides needed. The German compound nouns "Datenschutzerklärung", "Betroffenenrechte", and "Speicherdauer" are announced as single tokens by standard screen readers.
- The page has no focus traps.
- The page has no live regions.

## Content blocks (FR-002)

The new page contains exactly the following 9 blocks, in this order, each in plain German. Each block is a `<section>` with a `<h2>` heading and one or more `<p>` paragraphs.

1. **Verantwortlicher** — Full name, address (Mannheim), and contact email of the operator (reused from the Impressum).
2. **Datenschutzbeauftragter** — Statement that no Data Protection Officer is appointed. Includes a brief justification.
3. **Zwecke und Rechtsgrundlagen** — Service delivery (Art. 6(1)(b) DSGVO for the donation link. Art. 6(1)(f) for the public-interest map) and tile serving (Art. 6(1)(f)).
4. **Empfänger und Drittländertransfer** — Named recipients: Cloudflare Inc. (US, EU-U.S. Data Privacy Framework, DPA), BKG / basemap.de (DE), MapLibre glyph CDN (US, demotiles.maplibre.org), Ko-fi (US, image CDN + outbound link). For each: data type, legal basis, retention.
5. **Speicherdauer** — No server-side storage. Cloudflare logs per Cloudflare DPA. On-device `localStorage` persisted until the visitor clears browser storage.
6. **Betroffenenrechte** — Access (Art. 15), rectification (Art. 16), erasure (Art. 17), restriction (Art. 18), portability (Art. 20), objection (Art. 21), complaint to LfDI BW.
7. **Cookies und localStorage** — Explicit statement: no cookies. One `localStorage` key (`matreecover.story-dismissed`) only on explicit action. § 25(2) Nr. 2 TDDDG.
8. **Keine automatisierten Entscheidungen / kein Profiling** — Art. 22 statement.
9. **Stand** — "Letzte Aktualisierung: 2026-08-10".

## Regression constraints

- The new page contains no scripts, no iframes, no third-party resources, no analytics, no cookies, no localStorage reads or writes, no fonts, no images.
- The CSP `<meta>` tag in `index.html` and the Worker's `Content-Security-Policy` response header remain byte-identical. The new page is covered by the existing policy.
- The visual rendering is identical to `impressum.html` and `attribution.html` outside the content. The layout-overlap matrix stays green.
- The accessibility (keyboard navigation, screen reader, focus) is identical to the existing info pages.
- The new page loads in under 1 second on a 3G connection (single small HTML document, no scripts, no fonts).
- The deploy record includes the new file in the manifest.

## Acceptance checks (run by quickstart)

- The page is in `src/site/datenschutz.html` and `dist-assets/datenschutz.html` after deploy.
- The page returns HTTP 200 on `https://abu-hamad.de/map/datenschutz`.
- The page contains all 9 content blocks in FR-002 order.
- The page is included in `src/site/sitemap.xml`.
- The page is reachable via the footer link on `https://abu-hamad.de/map/`.
- The page is reachable via the back-link on `https://abu-hamad.de/map/impressum`.