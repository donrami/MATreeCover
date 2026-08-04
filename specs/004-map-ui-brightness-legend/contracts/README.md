# Contracts

This feature changes three surfaces of the published map: the
base-map brightness control, the placement of the static UI
elements, and the legend's color-scale presentation. Everything else
in the existing contract set (`specs/001-replicate-mannheim-tree-cover/contracts/`,
`specs/003-darken-base-map/contracts/base-map-style.md`) is
untouched — the building palette, tree layer, popup payload, layer
order, and interaction behavior are not modified.

| File | Surface | Audience |
|---|---|---|
| `base-map-brightness.md` | The `basemap` layer's brightness contract: static default, runtime range, session scope, layer isolation. Supersedes 003's fixed `[0.6, 0.7]` window at runtime only. | Frontend maintainer; smoke checklist author. |
| `ui-layout.md` | The static UI element placement contract: which elements exist, where they live, and the pairwise non-overlap invariant at every supported viewport. | Frontend maintainer; smoke checklist author. |
| `legend-gradient.md` | The legend's gradient-bar contract: color stops, tick labels, value-proportional positions, and screen-reader text. | Frontend maintainer; smoke checklist author. |

All contracts are derived from the spec (FR-001..FR-018); no
behavior is added that the spec does not require.
