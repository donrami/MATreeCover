# Contracts

This feature introduces the live deployment surface of the map:
the Cloudflare serving architecture, the DNS migration, and the
bundle split. Everything in the existing contract set
(`specs/001-replicate-mannheim-tree-cover/contracts/`,
`specs/003-darken-base-map/contracts/base-map-style.md`,
`specs/004-map-ui-brightness-legend/contracts/`) is untouched — the
bundle content, layer order, interaction behavior, and static-bundle
contract are not modified by this feature.

| File | Surface | Audience |
|---|---|---|
| `deployment.md` | The deploy procedure contract: Cloudflare layout, atomic deploy order (R2 put → wrangler deploy), verification, rollback, local archives. | Maintainer running `scripts/deploy-cf.sh`. |
| `hosting-config.md` | The Cloudflare layer contract: Worker/routes, R2 objects (content-type, cache headers), DNS record table, SSL mode, proxy sequence. | Maintainer; quickstart author. |
| `dns-https.md` | The domain contract: <registrar> nameserver switch, record inventory/migration, Universal SSL, email/blog continuity (FR-014). | Maintainer; FR-013/FR-014 gate author. |
| `bundle.md` | The deployment bundle contract: `dist/` file set, the 25 MiB split (assets vs R2), sha256 identity, byte-identical guarantee. | Maintainer; verification script author. |

All contracts are derived from the clarified spec (FR-001..FR-014,
SC-001..SC-007) and research R-001..R-014; no behavior is added
that the spec does not require.
