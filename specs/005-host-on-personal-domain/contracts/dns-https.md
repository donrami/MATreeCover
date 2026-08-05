# DNS & HTTPS Contract

**Branch**: `005-host-on-personal-domain` | **Date**: 2026-08-04
**Source**: `spec.md` FR-001/FR-002/FR-003/FR-014, edge cases (DNS
propagation, SSL issuance/expiry, email/blog outage), research
R-008/R-009. **Entity**: E-003 (PersonalDomain), E-004
(BlogAndEmailServices).

This contract fixes the domain layer: registrar, nameserver
migration, record inventory, certificate, and the email/blog
continuity requirement (FR-014).

## 1. Canonical addresses

- Map: `https://abu-hamad.de/map/` (canonical; `/map` and
  `www.abu-hamad.de/map*` 301 to it — FR-001, FR-003).
- Blog root: `https://abu-hamad.de/` (unchanged, Hostinger
  WordPress; its own www behavior is pre-existing).
- Email: unchanged (Hostinger mailboxes, `@abu-hamad.de`).

## 2. Registrar and nameserver migration

- Registrar: **GoDaddy** (clarified 2026-08-04). Nameservers are
  changed there.
- Today the domain's DNS serves Hostinger (blog + email). The
  migration moves the authoritative zone to Cloudflare (free
  plan, full setup).
- GoDaddy path: Domain Portfolio → domain → Domain Settings → DNS
  → Nameservers → "I use my own nameservers" → enter Cloudflare's
  two NS hostnames → Save. Propagation: most updates within an
  hour, up to 48 h globally (research R-008).
- Rollback: point the GoDaddy nameservers back to Hostinger's
  (e.g. `ns1.dns-parking.com` / `ns2.dns-parking.com`) — the
  Hostinger zone was never modified.

## 3. Ordered migration (outage-free)

1. **Inventory** (no risk): copy every record from the Hostinger
   DNS Zone Editor verbatim (A `@`/`www`, MX, TXT SPF/DMARC/DKIM,
   any `mail` A); corroborate with `dig @1.1.1.1 abu-hamad.de
   {A,MX,TXT,NS}`. Save as `validation/dns-migration-<ts>.json`.
2. **Build the Cloudflare zone** (no risk): add `abu-hamad.de`
   (free, full setup); reconcile the imported zone record-for-record
   against the inventory. Blog A records **DNS-only (grey)** for
   now; MX/SPF/DMARC/DKIM/mail **DNS-only** always.
3. **Stage the map**: deploy the Worker + the four routes
   (inert until the zone activates).
4. **Cutover**: change nameservers at GoDaddy to Cloudflare's two
   NS. The zone flips Pending → Active automatically (first check
   ~60 s, then at growing intervals).
5. **Activate proxying** (only after the zone and Universal SSL are
   Active): flip blog A records to proxied (orange), set SSL mode
   **Full (strict)**, re-verify the blog.
6. **Verify** per §5 (FR-014 gate).

## 4. HTTPS certificate

- Cloudflare Universal SSL, free, auto-issued on full setup,
  covering apex + ALL first-level subdomains; presented only when
  records are proxied. Provisioned ~15 min to 24 h AFTER the zone
  becomes Active — which is why records stay grey until then
  (research R-008).
- The map path is served over HTTPS automatically (Worker route on
  the zone's edge certificate).
- Origin (blog) TLS: Hostinger's free Let's Encrypt satisfies
  Full (strict) — never Flexible (redirect loops).

## 5. FR-014 gate (email + blog continuity)

Before declaring success, all of these must pass:

- `dig @1.1.1.1 abu-hamad.de NS` and `dig @8.8.8.8 abu-hamad.de NS`
  return only Cloudflare nameservers (two resolvers, catching
  lagging caches).
- `dig abu-hamad.de A` / `www` return the Hostinger blog IP; the
  blog loads over HTTPS (again after the proxy flip).
- `dig abu-hamad.de MX` returns `mx1.hostinger.com` (5) and
  `mx2.hostinger.com` (10); `dig abu-hamad.de TXT` contains the
  full single SPF line with `include:_spf.mail.hostinger.com`;
  `dig _dmarc.abu-hamad.de TXT` returns the DMARC policy; DKIM
  CNAMEs present.
- Mail receive: external account → Hostinger mailbox, confirmed in
  webmail (`https://mail.hostinger.com`).
- Mail send: Hostinger mailbox → external address; headers show
  SPF=pass, DKIM=pass, DMARC=pass (e.g. mail-tester.com).

**Invariants**:

- The nameserver switch happens only after the Cloudflare zone is a
  record-for-record copy of the Hostinger zone (R-008).
- Email records are never proxied (Cloudflare does not proxy
  MX/SMTP); SPF stays a single record (duplicates are a
  perm-error).
- The DNS migration does not touch Hostinger-hosted mailboxes or
  files — it only changes where resolvers look (R-008).
