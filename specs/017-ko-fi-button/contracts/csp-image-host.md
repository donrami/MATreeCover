# Contract: CSP Image-Host Extension (Ko-fi)

Target: `src/site/index.html` (meta tag), `workers/map/index.js` (`SECURITY_HEADERS`), `specs/015-security-audit-housekeeping/contracts/security-headers.md`. Requirement sources: FR-009; spec Edge Cases; feature 015 (locked CSP, contract-change rule).

## Purpose

The Ko-fi button renders an image from Ko-fi's CDN. The feature-015 CSP allows images only from the site itself, inline `data:`, and the LGL basemap host. The button's image would be blocked unless `img-src` gains the Ko-fi image host. This contract scopes that change to the minimum: one origin, one directive, three files updated in lockstep.

## The change

`img-src` gains exactly one origin:

```text
BEFORE: img-src 'self' data: https://sgx.geodatenzentrum.de;
AFTER:  img-src 'self' data: https://sgx.geodatenzentrum.de https://storage.ko-fi.com;
```

Full policy after the change (identical in all three carriers):

```text
default-src 'self'; img-src 'self' data: https://sgx.geodatenzentrum.de https://storage.ko-fi.com;
style-src 'self' 'unsafe-inline'; script-src 'self';
connect-src 'self' https://sgx.geodatenzentrum.de;
worker-src 'self' blob:; font-src 'self' https://demotiles.maplibre.org
```

## Lockstep rule (three locations, one commit)

The policy exists in exactly three places and they must stay byte-identical:

1. `<meta http-equiv="Content-Security-Policy">` in `src/site/index.html` — the source of truth (feature 015 contract).
2. `SECURITY_HEADERS["Content-Security-Policy"]` in `workers/map/index.js` — the Worker header on every response. Header and meta both apply (intersection), so they must match.
3. The policy text block in `specs/015-security-audit-housekeeping/contracts/security-headers.md` — the committed contract. Changing the policy is a contract change: update the contract, the meta tag, and the Worker header together (feature 015 rule), and re-run the live-map verification (feature 015 quickstart S6) before deploy.

## Locked directives (byte-identical, no other change)

`default-src`, `style-src`, `script-src`, `connect-src`, `worker-src`, `font-src` stay exactly as locked by feature 015. In particular:

- `script-src 'self'` — the Ko-fi widget script (`ko-fi.com/widgets/widget_2.js`) is NOT added, and no `'unsafe-inline'`/`'unsafe-eval'` appears (FR-008, R-1).
- `connect-src 'self' https://sgx.geodatenzentrum.de` — no Ko-fi origin added; the button makes no network call besides the `<img>` fetch.
- `style-src 'self' 'unsafe-inline'` — unchanged (feature 014 inlined styles).

## Out of scope

- No `script-src` / `connect-src` / `style-src` / `worker-src` / `font-src` change, ever, for this feature.
- No preconnect/preload hint for `storage.ko-fi.com` (R-8).
- The image host is the only Ko-fi origin allowed: `storage.ko-fi.com` (image CDN). `ko-fi.com` itself (the destination page) is navigated to via top-level navigation — it needs no CSP allowance (FR-002).

## Verification

- Acceptance test `tests/acceptance/test_ko_fi.py`: meta CSP contains the new origin in `img-src`; `script-src`/`connect-src`/`style-src` byte-equal the locked values; Worker header CSP byte-equal the meta CSP.
- Quickstart Q6: published page in a browser — button image renders (no broken-image state) under the extended policy; map, tiles, fonts, and popups unaffected; console shows zero CSP violations.
- `deploy-cf.sh verify` re-run after deploy (feature 015 quickstart S6) — asserts security headers present; the assertion is presence-based, so it passes with the extended value.
