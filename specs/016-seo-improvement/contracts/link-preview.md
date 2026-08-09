# Contract: Link-preview metadata (feature 016)

Requirement: FR-005 (US2, SC-005). Subject: Open Graph + Twitter Card tags and the preview image on the map page. Implementation: head of `src/site/index.html` plus `src/site/og-image.png`. Enforcement: `tests/acceptance/test_seo_metadata.py`. Live check: quickstart Q2.

## Required tags (map page only)

| Property | Value |
|----------|-------|
| `og:title` | German, descriptive, semantically consistent with the `<title>` (may be identical). |
| `og:description` | German, 100–160 characters, summarizes the map content. |
| `og:type` | `website` |
| `og:url` | `https://abu-hamad.de/map/` (the canonical URL, E1). |
| `og:site_name` | Site name, e.g. "Baumfläche Mannheim". |
| `og:locale` | `de_DE` (research D4). |
| `og:image` | Absolute URL `https://abu-hamad.de/map/og-image.png` (served from the map path). |
| `og:image:width` | `1200` |
| `og:image:height` | `630` |
| `twitter:card` | `summary_large_image`. Required. There is no OG fallback for X/Twitter (research D4). |

No `twitter:image` or `twitter:title/description` is needed. `summary_large_image` together with the `og:*` set is the standard working configuration (research R-008).

## og:image contract (E4)

- **Format**: PNG or JPG only. WebP is inconsistently decoded by scrapers (research D4).
- **Dimensions**: 1200×630 px, ratio 1.91:1. Declared in `og:image:width/height`.
- **Size**: under 1 MB.
- **Served**: from the map path, HTTP 200, unhashed filename. The feature 014 hashed-bundle contract excludes it. A hashed name would break cached previews and the `og:image` URL.
- **Content**: a visual render of the current map (colors, data version, labels). Must not show a stale or wrong city (spec edge case).
- **Generation**: `scripts/parity-render.mjs` export mode (1200×630 viewport render), committed in `src/site/` (research D9).
- **Freshness invariant**: any change to the map rendering (colors, data, labels) MUST regenerate and recommit `og-image.png` in the same change. Metadata-only changes need no regeneration. A mismatch is a correctness bug.

## Rules

1. All ten tags above are present with correct values in the raw HTML of `dist/index.html`. No JavaScript is required.
2. Exactly one `og:*` per property. No duplicate `og:image`.
3. The `og:image` URL is absolute. Relative URLs break most scrapers.
4. No client-side tracking is added (FR-001). The tags are static markup only.
5. Other head content (CSP, stylesheets, preloads) is unchanged (FR-012).

## Machine checks (acceptance test)

- Parse the raw HTML head. All ten properties are present, values non-empty. `og:locale == de_DE`. `og:type == website`. `og:url` equals the canonical URL.
- The `og:image` filename in the tag exists in `dist/`, is PNG or JPG, is exactly 1200×630 px, and is under 1 MB.
- `twitter:card == summary_large_image`.

## Live verification (quickstart Q2)

- Fetch `https://abu-hamad.de/map/og-image.png`. Expect HTTP 200, content-type `image/png`, dimensions 1200×630 (`file` or `identify`), size under 1 MB.
- Share the URL on at least three of Facebook/LinkedIn/X/WhatsApp/Telegram/Discord/Slack. The preview shows title, description, and the map image (SC-005).

## Regression notes

- The preview image is not content-hashed and not in the sitemap (crawler-files contract).
- Regenerating the image is part of the deploy checklist when the map rendering changes. Quickstart Q7 re-runs the parity comparison and the visual-match check.
