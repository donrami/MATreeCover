# Contracts

This feature changes one interface: the click-to-popup interaction of
the published map. Everything else in the existing contract set
(`specs/001-replicate-mannheim-tree-cover/contracts/`) is untouched —
the popup payload still comes from the same PMTiles `has_value` /
`value_str` fields, and the map style is not modified.

| File | Surface | Audience |
|---|---|---|
| `popup-interaction.md` | The building-click → popup behavior contract. | Frontend browser; frontend maintainer; smoke checklist author. |

All contracts are derived from the spec; no behavior is added that
the spec does not require.
