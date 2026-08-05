# Contract: Verify Sample

Scope: how the inspection sample is selected and what
`verification/sample.jsonl` must contain. Requirements: FR-001, FR-004;
success criteria SC-001, SC-002, SC-004. See [../data-model.md](../data-model.md).

## Selection algorithm

1. **Frame**: buildings with `has_value = true` in the workspace file
   `tables/buildings.geojson` (EPSG:25832). The frame is fixed for a
   given workspace.
2. **Strata**: 38 official Stadtteile (from `verification/stadtteile.geojson`,
   official GDI-MA layer) × value bands `[0,10)`, `[10,30)`, `[30,100]`.
   Band membership is the building's `value` property.
3. **Allocation**:
   - District share: proportional to the district's building count in
     the frame, with a floor of 1 patch per district that has
     buildings. All 38 districts have buildings.
   - Band share within a district: proportional to the band's building
     count, over non-empty bands only.
   - Total target: 100 patches; rounding by largest remainder, applied
     first at district level, then at band level.
4. **Draw**: within each district×band cell, patch centers are drawn
   uniformly at random without replacement from the cell's building
   centroids.
5. **Seed**: fixed default `20260805`; recorded in every sample record
   and overridable via a CLI flag for experimentation (the recorded
   seed is the reproducible one).
6. **Coverage check**: a drawn center must lie within the imagery extent
   of the accepted DOP20 tiles (`tiles.csv` + `mosaic/extract/`). If it
   does not, the draw is replaced deterministically from the remaining
   centroids in the same cell and marked `resampled: true`. If a cell is
   exhausted, its remaining slots are redistributed to the next cell by
   district order. Draws are never silently dropped (FR-008).
7. **Degeneracy**: after rendering, each patch record carries a
   `degeneracy` field: `null`, `no-imagery`, `empty-mask`, or
   `full-mask` (set by `verify-render`, see [verify-ratings.md](verify-ratings.md)
   for handling).

## `verification/sample.jsonl` schema

One JSON object per line, UTF-8, keys in this order:

```json
{
  "patch_id": "p001",
  "seed": 20260805,
  "district_code": "030",
  "district_name": "Neckarstadt-West",
  "value_band": "0-10",
  "center_easting": 472100.5,
  "center_northing": 5480200.3,
  "building_id": "b-58f4e1fa870d",
  "resampled": false,
  "degeneracy": null
}
```

| Field | Rule |
|-------|------|
| patch_id | `p` + 3 digits, unique, `p001`…`p100` |
| seed | Integer; identical across all records of one run |
| district_code | 3 digits, must exist in `stadtteile.geojson` |
| district_name | Official name for the code |
| value_band | One of `0-10`, `10-30`, `30-100` |
| center_easting / center_northing | EPSG:25832, 1 decimal |
| building_id | Must exist in the frame |
| resampled | Boolean |
| degeneracy | `null` \| `no-imagery` \| `empty-mask` \| `full-mask` |

## Invariants (tested)

- 100 records; unique patch_ids.
- Every district with buildings appears with ≥ 2 records (SC-004).
- Band counts per district match the documented allocation (rounding by
  largest remainder).
- Same seed + same workspace ⇒ byte-identical file (SC-002).
- No record without a district (point-in-polygon is total over the
  city).
