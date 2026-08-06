# Contracts: Heatwave Map Insights

Feature 011. These contracts pin the data and UI semantics that the
implementation slices and the acceptance suite defend.

| Contract | Defines |
|----------|---------|
| [district-stats.md](district-stats.md) | District layer, statistics derivation, district popup, building popup enrichment, click arbitration (FR-006, FR-007, FR-009) |
| [city-overview.md](city-overview.md) | City stats metadata schema, overview panel content and placement (FR-008, FR-010) |
| [publish-bundle.md](publish-bundle.md) | Pipeline additions, manifest entries, attribution page, zero-request guarantee (FR-010, FR-014, SC-002..SC-009) |

Cross-cutting rules that apply to every contract:

- Zero new network requests (FR-010, SC-007). All derived data ships
  in already-fetched resources: the stadtteile GeoJSON source and
  style.json metadata.
- German copy only, no em-dashes and no en-dashes, hyphens only inside
  compounds (FR-011, feature 007 convention). The popup's existing
  en-dash UNAVAILABLE constant is unchanged.
- The default view must render unchanged: no new view or toggle is
  introduced, and the published buildings palette stays verbatim
  (FR-012, SC-004).
- Accessibility: new popups and the city panel are keyboard-operable
  with sufficient color contrast on the dark background (FR-013).
- All statistics are computed from the accepted building values at
  publish time; a stale-value run must fail the publish gate
  (FR-007, FR-010).

Removed with the 2026-08-06 scope clarification: the
`heat-exposure-view.md` contract (exposure classes, view toggle, class
legend, class popup; FR-001..FR-005) was deleted because the
Hitzebelastung view is out of scope.
