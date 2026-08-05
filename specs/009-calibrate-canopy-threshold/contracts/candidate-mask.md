# Contract: Candidate Mask

Scope: how a candidate mask is produced and what makes it acceptable.
Requirements: FR-001, FR-002, FR-008; success criteria SC-001, SC-006.
See [../data-model.md](../data-model.md).

## Inference request

`POST <endpoint>/infer` with JSON:

```json
{
  "model": "deepLabV3plus-resnet34",
  "inputs": ["mosaic/extract/dop20rgb_32_457_5488_1_bw_2024.tif", "..."],
  "threshold": 0.6
}
```

| Field | Rule |
|-------|------|
| threshold | Optional float in (0, 1); absent → 0.5 (unchanged 008 behavior) |

Response: the binary canopy mask as GeoTIFF bytes (EPSG:25832, 0.2 m,
full tile coverage), thresholded per-pixel at the requested value.

## Metadata

The companion `<mask>.json` MUST record at least:

```json
{
  "model": "deepLabV3plus-resnet34",
  "crs": "EPSG:25832",
  "ground_sampling_distance_m": 0.2,
  "threshold": 0.6,
  "generated_at": "…"
}
```

## Acceptance (FR-008)

A candidate mask is accepted for re-verification and value comparison
only if:

- the metadata JSON exists next to the mask,
- `metadata["threshold"]` equals the requested threshold,
- `metadata["crs"]` is EPSG:25832 and GSD is 0.2 m,
- the mask raster covers the same extent as the published mask.

Any violation → the mask is rejected (no partial evidence).

## Production flow (owner pod, OR-003)

```text
bash scripts/runpod-deploy.sh <host> [port] [ssh_key]
ssh -p <port> -i <ssh_key> -N -L 8000:localhost:8000 <host>
MANNHEIM_RUNPOD_ENDPOINT=http://127.0.0.1:8000/infer \
  python -m src.pipeline.cli runpod-infer --threshold 0.6 --out mosaic/canopy_prediction_mask_t060.tif
```

The same with `0.65` / `_t065.tif`.
