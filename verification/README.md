# Verification: Tree Detection Quality

Evidence that the reused tree-detection model recognizes trees on
Mannheim aerial imagery — the basis of every building value on the
published map. Feature: `specs/008-verify-tree-detection/` (spec, plan,
contracts, quickstart).

## Artifacts

| File | Content | Status |
|------|---------|--------|
| `stadtteile.geojson` | Official Mannheim Stadtteil boundaries (38 Stadtteile, EPSG:25832) | committed, input |
| `sample.jsonl` | Reproducible sample of 100 patch centers (seed, strata) | generated |
| `patches/` | 1024×1024 review PNGs with canopy-mask overlay | generated, gitignored |
| `ratings.jsonl` | Owner ratings per patch (correct / over / under) | owner-filled |
| `notes.md` | Owner writeup: comparison + limitations | owner-filled |
| `report.md` | Generated findings report (per-district, flags, disclosures) | generated |

Run order: `verify-sample` → `verify-render` → owner rates → `verify-report`.

## District data attribution

- Source: Stadt Mannheim, GDI-MA WFS `stadtteil_grenze`
  (`https://www.gis-mannheim.de/mannheim/mod_ogc/wfs_getmap.php?mapfile=stadtteil_grenze&service=WFS`).
- License: Datenlizenz Deutschland – Namensnennung – Version 2.0
  (dl-de/by-2-0), the city's standard open-data license for these
  services.
- Downloaded: 2026-08-05. 38 official Stadtteile (codes 011–174,
  matching the city's statistical Stadtteilschlüssel); total area
  144.86 km², no overlaps, all polygons valid.
- Attribution: "Stadt Mannheim, GDI-MA, dl-de/by-2-0
  (https://www.govdata.de/dl-de/by-2-0)".
