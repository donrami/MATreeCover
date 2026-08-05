# Contracts: First-Visit Story Modal

**Feature**: 007-first-visit-story | **Branch**: `007-first-visit-story`

| Contract | Covers | Source of truth |
|----------|--------|-----------------|
| [story-modal.md](story-modal.md) | Placement / no-overlap geometry, dialog semantics, focus management, dismissal wiring | `src/site/index.html`, `src/site/style.css`, `src/site/main.js` |
| [story-content.md](story-content.md) | German story copy: required elements, link targets, facts | `src/site/index.html` (static markup) |
| [dismissal-state.md](dismissal-state.md) | `localStorage` key, semantics, storage-unavailable fallback | `src/site/main.js` |

Requirement mapping: FR-001, FR-002, FR-003, FR-004, FR-005,
FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013,
FR-014. Validation: `quickstart.md` scenarios 1–9 and
`tests/frontend/smoke_us5.md`.

Related contract: `specs/004-map-ui-brightness-legend/contracts/ui-layout.md`
— this feature extends its no-overlap placement contract with the
modal as a sixth element while it is open.
