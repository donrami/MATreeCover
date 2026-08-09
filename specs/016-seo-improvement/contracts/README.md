# Contracts: SEO Assessment & Improvement (feature 016)

Interface contracts produced by this feature. Each contract is the reviewed, committed statement of a crawler- or user-facing surface; changing one is a contract change and must be reflected in the implementation and the assessment report together.

| Contract | Requirement | Subject |
|----------|-------------|---------|
| [on-page-metadata.md](on-page-metadata.md) | FR-002/003/004, US1, SC-002/003 | Title, meta description, canonical tag per page |
| [link-preview.md](link-preview.md) | FR-005, US2, SC-005 | Open Graph + Twitter Card tags, og:image |
| [visible-content.md](visible-content.md) | FR-006, US1, SC-004/SC-010 | Visible crawlable content, single DOM copy, modal behavior |
| [structured-data.md](structured-data.md) | FR-007, SC-007 | JSON-LD WebSite/Organization (+ optional Dataset), CSP interplay |
| [crawler-files.md](crawler-files.md) | FR-008/009/010, US3, SC-006 | robots.txt, sitemap.xml, root-domain coordination |
| [assessment-report.md](assessment-report.md) | FR-001/011, US5, SC-001/SC-009 | Committed report contract, server-side verification |

Cross-cutting rules that apply to every contract here:

- **Additive only**: no contract may alter map values, colors, labels, popups, interactions, caching semantics, security headers, or the hashed-bundle contract (FR-012, feature 014/015).
- **Change together**: contract changes, implementation, and assessment-report entries for the same surface land in the same commit (OR-004 discipline, feature 015 precedent).
- **Machine-checkable**: every rule a script can enforce is enforced by a committed acceptance test (`tests/acceptance/test_seo_metadata.py`), never by documentation alone.
- **No new dependencies**: enforcement uses Python stdlib, curl, and the existing parity/rendering tooling only.
- **No client-side tracking**: verification is server-side only (FR-001).
