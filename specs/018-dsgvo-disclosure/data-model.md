# Data Model: DSGVO Disclosure (feature 018)

Phase 1 output. Entities, fields, validation rules, and state transitions that the feature's artifacts must satisfy. This feature is content-only. The "data model" is the schema of the new page plus the documentation of the single existing `localStorage` key.

## Entities

### E1 — LegalPage

A static HTML document that is one of the site's info pages. The `datenschutz.html` page is a new instance of this entity. `impressum.html`, `attribution.html`, and the front page (`index.html`) are existing instances.

| Field | Type | Rule |
|-------|------|------|
| `url` | path | `https://abu-hamad.de/map/<slug>` where `<slug>` is `index`, `impressum`, `attribution`, or `datenschutz`. |
| `title` | HTML `<title>` | German, matches the page's `<h1>` text. |
| `h1` | HTML `<h1>` | German, used as the document heading. |
| `lang` | HTML `<html lang>` | `"de"` for all info pages. |
| `body` | HTML `<main>` content | The page's content. For `datenschutz`: 9 content blocks in FR-002 order. |
| `back_link` | HTML `<a>` | Optional but present on info pages: a link to the map (`/map/`). |
| `in_sitemap` | boolean | `true` for the info pages; the front page is also listed. |
| `css` | HTML `<style>` block | In-line, same color scheme as the other info pages. |
| `last_updated` | ISO date | "Stand" footer of the page; equals the date of the last edit. |

Validation:
- `url` MUST be unique per info page.
- `title` and `h1` MUST match.
- `lang` MUST be `"de"`.
- `in_sitemap` MUST be `true` for `datenschutz` (FR-008).
- `css` MUST match the template (FR-003).
- `last_updated` MUST be the date the page is last edited.

### E2 — FooterLegalLink

A single link in the page footer's legal-link group. The current instance has 1 link. The new instance has 2 (Impressum + Datenschutzerklärung).

| Field | Type | Rule |
|-------|------|------|
| `class` | HTML class | `"legal-link"` (no other class). |
| `href` | path | `impressum` or `datenschutz` (relative). |
| `text` | string | The link text, in German. |
| `aria_current` | HTML attribute | Not present (info pages are not in the same SPA flow as the map). |

Validation:
- All legal links MUST use the same `class="legal-link"` styling.
- The two elements MUST be siblings in the footer's `<footer class="legal">` (or wherever the existing single link is anchored).
- A separator element (dot, separator `<span>`, etc.) MUST NOT be introduced.

### E3 — LocalStorageKey

The site's only end-device write. Schema unchanged by this feature but documented in the new Datenschutzerklärung.

| Field | Type | Rule |
|-------|------|------|
| `key` | string | `"matreecover.story-dismissed"`. |
| `value` | string | `"1"` (presence indicates dismissal). |
| `written_by` | HTML file | `src/site/main.js` (dismissal handler). |
| `read_by` | HTML file | `src/site/main.js` (story-modal first-render check). |
| `expires_on` | ISO date | Never (the visitor clears via browser settings). |
| `legal_basis` | string | "§ 25(2) Nr. 2 TDDDG" (technisch erforderlich). |

Validation:
- The key MUST be the only `localStorage` write the site performs. Confirmed by the DSGVO assessment scout (`agent://ScoutDSGVO`, 2026-08-10).
- A reader who inspects `localStorage` after a page visit MUST find exactly one key.
- A reader who inspects `localStorage` after dismissing the story modal MUST find exactly one key. The value is `"1"`.

### E4 — SitemapEntry

A row in `src/site/sitemap.xml`.

| Field | Type | Rule |
|-------|------|------|
| `loc` | URL | `https://abu-hamad.de/map/<slug>`. |
| `lastmod` | ISO date | The page's last edit date. |
| `changefreq` | string | Not present in the existing entries. Follow existing pattern. |
| `priority` | number | Not present in the existing entries. Follow existing pattern. |

Validation:
- Every LegalPage (E1) with `in_sitemap == true` MUST have a corresponding SitemapEntry.
- `lastmod` MUST be the page's `last_updated` field.

### E5 — Ko-fiDonationLink

The existing footer donation link. Schema mostly unchanged. One attribute changes.

| Field | Type | Rule |
|-------|------|------|
| `href` | URL | `https://ko-fi.com/...` (existing, unchanged). |
| `target` | string | `_blank` (existing, unchanged). |
| `class` | HTML class | Existing, unchanged. |
| `rel` | string | `"noopener noreferrer nofollow sponsored"` (NEW — upgraded from `"noopener"`). |
| `inner` | HTML | A Ko-fi banner `<img>` (existing, unchanged). |

Validation:
- `rel` MUST be exactly `"noopener noreferrer nofollow sponsored"` (FR-006).
- The `<img>` MUST load from `https://storage.ko-fi.com/...` (allowed by existing CSP `img-src`).
- The href domain MUST be `ko-fi.com` (no other monetization destination).

## State transitions

**LegalPage edit lifecycle** (E1):

```text
draft ──► published ──► revised
```

For this feature, the page transitions from `draft` (in the spec) to `published` (after the first deploy) to `revised` (after any future edit). The page is never archived; the live site continues to serve the latest revision.

**FooterLegalLink lifecycle** (E2):

```text
hidden ──► visible ──► expanded
```

The footer legal-link group transitions from `hidden` (1 link) to `expanded` (2 links) on first deploy. Future edits can add or remove links, but the maintenance rule is to keep the list stable.

**LocalStorageKey state** (E3):

```text
absent ──► present (value "1")
         ↑
         └── visitor clears browser storage
```

The key is absent on the first visit, present after the visitor dismisses the story modal, and absent again if the visitor clears browser storage. No code path sets the value to anything other than `"1"`.

**Ko-fiDonationLink attribute state** (E5):

```text
rel="noopener" ──► rel="noopener noreferrer nofollow sponsored"
```

The single attribute upgrade happens in this feature. Future edits do not change the attribute.

## Validation rules consolidated from spec

- FR-002: the new page contains exactly 9 content blocks in the FR-002 order. Each is in plain German.
- FR-003: the new page matches the existing info-page template (same in-line `<style>` block, same dark-mode color scheme, same back-link, same `<title>` + `<h1>` pattern, same `<main>` wrapper).
- FR-004: the footer of `index.html` contains both the existing "Impressum" link and the new "Datenschutzerklärung" link. Both are `<a class="legal-link">` siblings.
- FR-005: the new link is a single sibling of the existing one. Separated by a single whitespace.
- FR-006: the Ko-fi donation link's `rel` attribute is exactly `"noopener noreferrer nofollow sponsored"`.
- FR-007: the Impressum's "Datenschutz" section is a single sentence linking to the new page.
- FR-008: `src/site/sitemap.xml` contains a `<url>` entry for `datenschutz`.
- FR-010: `specs/007-first-visit-story/contracts/dismissal-state.md` has a 3-5 sentence paragraph documenting the § 25(2) Nr. 2 TDDDG exemption.
- FR-011: the README's privacy-related sentence is rewritten. It names Cloudflare, BKG, and Ko-fi as recipients of standard HTTP connection data and links to the new Datenschutzerklärung.
- FR-012: the new page contains no scripts, no iframes, no third-party resources, no analytics, no cookies, no localStorage reads or writes.
- FR-014: the existing deploy record includes the new file in the manifest.
