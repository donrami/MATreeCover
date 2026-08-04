# Contract: `tree-cover` CLI

The maintainer-facing CLI for the data pipeline. One binary, several
subcommands. Each subcommand is a single-purpose job and runs as a
child process so the wrapper can measure peak RSS via
`/usr/bin/time -v`.

## Surface

```text
python -m src.pipeline.cli <subcommand> [options]
```

## Subcommands

### `accept`

Re-validates every artifact in `artifacts.manifest.json` against
the five FR-021 criteria, refreshes the manifest, and prints a
summary.

- **Inputs**: existing `artifacts.manifest.json`, the artifacts
  it references.
- **Outputs**: refreshed `artifacts.manifest.json`; prints
  per-artifact `pass` / `fail` / `pending`.
- **Exit code**: `0` if every `pass`-able artifact passes; `1`
  otherwise.
- **Memory**: reads metadata only, not full rasters; safe under
  the 12 GiB cap.
- **Notes**: deterministic, idempotent. Used as the gate before
  every `publish`.

### `publish`

Clips every accepted layer to the official boundary, writes the
static `dist/` bundle, and emits the `PublishedMap` record.

- **Inputs**: accepted artifacts; the MapLibre style contract
  (`map-style.md`).
- **Outputs**: `dist/index.html`, `dist/style.json`, PMTiles
  (or pointers to them if generated earlier), `PublishedMap`
  record.
- **Exit code**: `0` on success; `1` on any failed acceptance.
- **Memory**: streams inputs, never loads a full raster
  (OR-002).
- **Notes**: refuses to run if any required artifact is
  `pending` or `fail`.

### `values`

Computes the per-building 60 m value from the accepted canopy
mask. Chunked 1000 px tiles, never a full mosaic in memory
(OR-002).

- **Inputs**: accepted canopy mask, accepted buildings.
- **Outputs**: `buildings.geojson` with the `value`,
  `value_str`, `has_value`, `completeness` fields.
- **Notes**: `requires_runpod` is `false` because this step
  uses the accepted mask as input, not the model.

### `trees`

Polygonizes the accepted canopy mask into tree-area polygons
for the `Bäume` layer. Clips to the official boundary
(FR-007) and reprojects to EPSG:4326.

- **Inputs**: accepted canopy mask, official boundary.
- **Outputs**: `trees_polygons.geojson` with stable ids
  `tree-<n>` and `canopy_pixel_count`.
- **Exit code**: `0` on success; `1` on input failure.
- **Memory**: windowed 1000 px chunk reads with a 1 px overlap;
  never loads the full mask (OR-002).
- **Notes**: the PMTiles step (`make pmtiles-trees`) consumes
  the output with tippecanoe.

### `runpod-infer` *(gated)*

Runs the canopy model on the imagery tiles and writes a binary
canopy mask. Refuses to run unless `MANNHEIM_RUNPOD_ENDPOINT` is
set in the environment (OR-003, FR-025). The local machine never
invokes a GPU.

- **Outputs**: `canopy_mask.tif` and `canopy_mask.json`.
- **Exit code**: `0` on success; `2` if the RunPod endpoint is
  missing (the script prints `STOP — request RunPod capacity`).
- **Memory**: the inference itself runs on RunPod; the local
  pre/post steps stay under the 12 GiB cap.
- **Notes**: uses existing `deepLabV3plus-resnet34` weights only.
  No new training, no new labels (FR-024).

## Common behavior

- Every subcommand writes a per-invocation row to
  `validation/event.log.jsonl` with `ts`, `subcommand`,
  `rss_peak_bytes`, `gpu_used`, `exit_code`, and `inputs`.
- Every subcommand validates its inputs against
  `artifacts.manifest.json` first; a `pending` or `fail` input
  short-circuits the subcommand with a non-zero exit.
- Every subcommand exits non-zero on RSS > 12 GiB. The wrapper
  enforces this with `/usr/bin/time -v`; the script's own
  RSS poll is a secondary check.

## Errors

| Code | Meaning |
|---|---|
| `0` | Success. |
| `1` | Acceptance or input failure. |
| `2` | RunPod gate tripped; the local machine stopped. |
| `3` | RSS exceeded 12 GiB. |

Only reachable codes are listed. Local GPU inference is impossible by
construction (OR-003): `runpod-infer` stops at the gate (`2`) and no
local inference code path exists, so no GPU exit code is defined.
