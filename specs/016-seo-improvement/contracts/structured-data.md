# Contract: Structured data (feature 016)

Requirement: FR-007 (SC-007). Subject: JSON-LD on the map page, aligned to visible content, valid under the locked CSP. Implementation: inline `<script type="application/ld+json">` in the head of `src/site/index.html`. Enforcement: `tests/acceptance/test_seo_metadata.py`. Rich Results Test: quickstart Q5.

## Required markup

One JSON-LD block (or adjacent blocks) declaring:

| Type | Fields | Notes |
|------|--------|-------|
| `WebSite` | `name`, `url`, `alternateName` | Required. NO `SearchAction` (sitelinks search box removed 2024-11-21, research D3). |
| `Organization` | `name`, `url` | Required. |
| `Dataset` | `subject`, `coverage`, `license`, `sources` | Optional. Feeds Dataset Search, not Google Search rich results (research D3). Include only facts stated on the page (attribution page content). |

## Forbidden markup

`FAQPage`, `LocalBusiness`, and `Speakable` MUST NOT appear (research D3). FAQ rich results ended 2026-05-07. The other types are inapplicable or deprecated.

## Rules

1. **Inline data block**: the JSON-LD is an inline `<script type="application/ld+json">` in `<head>`. Per the HTML spec (§4.12.1) a script element whose type is not a JavaScript MIME type is a data block. It is not executed, and CSP `script-src 'self'` does not apply (research D10).
2. **CSP unchanged**: the locked CSP meta tag (feature 015) is not modified. Quickstart Q5 verifies the page loads in a browser under the existing CSP and that the Rich Results Test reports zero errors.
3. **Aligned to visible content**: every fact in the JSON-LD is stated in the visible page content (title, description, visible section, attribution page). No hidden or inferred claims.
4. **Valid JSON**: the block parses with a JSON parser (stdlib `json.loads` on the extracted script text).
5. **Zero rich-results errors**: the markup passes the Google Rich Results Test with zero errors (SC-007).
6. **No external fetch**: no dynamic structured data. Static markup only (FR-001).

## Machine checks (acceptance test)

- Extract `script[type="application/ld+json"]` from raw `dist/index.html`. Parse each block as JSON.
- Required types `WebSite` and `Organization` are present with non-empty `name`, `url`. `WebSite` also has `alternateName`.
- No `SearchAction` in the `WebSite` record.
- Forbidden types (`FAQPage`, `LocalBusiness`, `Speakable`) are absent across all blocks.
- If `Dataset` is present: `subject`, `coverage`, `license` fields are non-empty.

## Regression notes

- The block adds bytes to the HTML head only. It does not affect the interaction path, budgets, or map rendering (FR-012, SC-008).
- Publish must not hash or move the block. `publish.py` rewrites script `src` attributes by exact string match (feature 014 contract). `application/ld+json` is untouched by that rewrite.
