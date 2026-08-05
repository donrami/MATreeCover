# Quickstart: Calibrate Canopy Detection Threshold

Validation guide. Scenarios 1–2 prove the local changes (implementable
now); scenarios 3–6 run after the pod produces the candidate masks.
Prerequisites: repo bootstrap, mannheim workspace, the 008 sample and
ratings (`verification/sample.jsonl`, seed 20260805).

## Scenario 1 — Threshold parameterization (FR-001)

```text
python -m src.pipeline.cli runpod-infer --help    # shows --threshold, --out
```

Expected: options present, default threshold 0.5. Endpoint behavior
without a threshold is unchanged (pod-side test in the deploy run).

## Scenario 2 — Local tooling tests (FR-003/FR-005 machinery)

```text
.venv/bin/python -m pytest tests/pipeline/test_verify.py -q
```

Expected: all pass, including the new mask-path parameter test and the
value-delta test on synthetic masks.

## Scenario 3 — Candidate masks produced (FR-002, SC-001)

```text
MANNHEIM_RUNPOD_ENDPOINT=http://127.0.0.1:8000/infer \
  python -m src.pipeline.cli runpod-infer --threshold 0.6 --out mosaic/canopy_prediction_mask_t060.tif
MANNHEIM_RUNPOD_ENDPOINT=http://127.0.0.1:8000/infer \
  python -m src.pipeline.cli runpod-infer --threshold 0.65 --out mosaic/canopy_prediction_mask_t065.tif
```

Expected: two masks + metadata JSONs recording thresholds 0.6 / 0.65;
both full coverage EPSG:25832 at 0.2 m.

## Scenario 4 — Re-verification (FR-003/004, SC-002/003)

```text
python -m src.pipeline.cli verify-render --mask mosaic/canopy_prediction_mask_t060.tif
# owner rates verification/ratings_t060.jsonl (same 100 patches, 008 criteria)
python -m src.pipeline.cli verify-render --mask mosaic/canopy_prediction_mask_t065.tif
# owner rates verification/ratings_t065.jsonl
```

Expected: for at least one candidate — over share < 39 % AND ≥ 90 % of
the 59 previously correct patches remain correct.

## Scenario 5 — Value deltas (FR-005, SC-004)

```text
python -m src.pipeline.cli verify-value-delta --mask mosaic/canopy_prediction_mask_t060.tif
python -m src.pipeline.cli verify-value-delta --mask mosaic/canopy_prediction_mask_t065.tif
```

Expected: `verification/value-delta_t060.md` / `_t065.md` with city
mean shift, district table, ranking correlation; 100 % of buildings
covered.

## Scenario 6 — Decision and optional release (FR-006/007, SC-005/007)

Owner records the decision in `verification/report.md`. If publishing:
`trees` → `make pmtiles-buildings pmtiles-trees` → `accept` →
`publish` → `scripts/deploy-cf.sh` (existing path; site byte-identical
otherwise). Zero-change gate: `pytest tests/`, `git status` shows no
site diffs, `make check-public`.
