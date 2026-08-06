# Contracts: Mobile-First Native UX

Feature 012. Contracts pin the layout, interaction, and accessibility semantics that the
implementation slices and the acceptance suite must satisfy.

| Contract | Defines |
|----------|---------|
| [layout-ux.md](layout-ux.md) | Breakpoints, surface geometry (bottom sheet / panel), map-dominant layout, safe-area + dynamic viewport handling, no-overlap matrix (FR-001, FR-002, FR-005, FR-007, FR-008, SC-001, SC-005) |
| [surface-interaction.md](surface-interaction.md) | `#surface` component contract: header/body DOM, state + motion, tools-in-header (FR-004), popup clearance via `map.setPadding` (FR-006), feature parity (FR-010), performance (SC-006) |
| [touch-a11y-copy.md](touch-a11y-copy.md) | Touch targets 44x44 px / 8 px spacing (FR-003), keyboard/focus/ARIA/contrast (FR-014), German copy no em/en dashes (FR-011), SC-009/SC-010 |

Cross-cutting rules apply to every contract:

- **Zero new network requests** (FR-012, SC-007). This feature is pure CSS/HTML/JS rework of
  existing elements. No new `fetch`, no new MapLibre source, no new request. The static bundle
  stays fully functional offline on first load.
- **No feature add/remove/rename** (FR-010). Bäume, Helligkeit, first-visit story modal,
  city-overview, building popup, district popup, attribution, Impressum all keep their current
  behaviour. Only presentation and placement change.
- **German copy only, no em-dashes, no en-dashes**, hyphens only inside compounds (FR-011,
  feature 007 convention). The existing `UNAVAILABLE` en-dash constant (FR-009) is unchanged.
- **Accessibility** (FR-014): every control keyboard-operable with a visible focus state, all
  new surfaces meet WCAG AA contrast on the dark theme, screen-reader labels describe controls.
- **Default view unchanged** (SC-004): `style.json` palette, layer order, and metadata stay
  verbatim; no new view or toggle introduced.
