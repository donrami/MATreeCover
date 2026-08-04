# Contracts

This feature changes one interface: the base-map appearance of the
published map style document (`dist/style.json`). Everything else in
the existing contract set
(`specs/001-replicate-mannheim-tree-cover/contracts/`) is untouched —
the building palette, tree layer, popup payload, and interaction
behavior are not modified.

| File | Surface | Audience |
|---|---|---|
| `base-map-style.md` | The `basemap` layer contract of the style document: source, paint, and what must never change. | Frontend maintainer; publish pipeline owner; smoke checklist author. |

All contracts are derived from the spec; no behavior is added that
the spec does not require.
