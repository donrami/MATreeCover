# Quickstart: Verify Tree Detection Quality

Validation guide for the feature. Each scenario is runnable and
independently proves part of the spec. Prerequisites: repo bootstrap
(`make bootstrap`), the mannheim workspace at
`data/archive/workspace` (or `MANNHEIM_WORKSPACE`), `verification/`
artifacts. Implementation details live in [tasks.md](../tasks.md); the
schemas are in [contracts/](contracts/) and the entities in
[../data-model.md](../data-model.md).

## Scenario 1 — Sample is generated and reproducible (FR-004, SC-001/002)

```text
python -m src.pipeline.cli verify-sample          # writes verification/sample.jsonl
cp verification/sample.jsonl /tmp/sample.1.jsonl
python -m src.pipeline.cli verify-sample          # same seed, same workspace
diff /tmp/sample.1.jsonl verification/sample.jsonl
```

Expected: exit 0 both runs; `diff` empty; 100 records; every district
with buildings present with ≥ 2 patches; band counts match the
documented allocation.

## Scenario 2 — Review patches are rendered (FR-001, FR-008, OR-001/005)

```text
python -m src.pipeline.cli verify-render
ls verification/patches/ | wc -l
```

Expected: exit 0; PNG count equals the number of rated patches (100
minus any `no-imagery` degenerates); each PNG is 1024×1024 px, true
color with the canopy mask overlay; `verification/patches/` is
gitignored (`git status` shows it untracked); peak RSS recorded in
`validation/event.log.jsonl` is far below the 12 GiB gate.

## Scenario 3 — Owner inspects and rates (FR-002, SC-002)

Manual step: open the PNGs, apply the criteria from
[contracts/verify-ratings.md](contracts/verify-ratings.md), write one
JSON object per patch into `verification/ratings.jsonl` (re-inspect
every 10th patch; resolve divergences and record them).

Expected: every non-`no-imagery` patch has exactly one rating with
rating ∈ {correct, over, under}; no rating for `no-imagery` patches.

## Scenario 4 — Report is generated and complete (FR-003/006/007/008, SC-003/004/005/007/008)

```text
python -m src.pipeline.cli verify-report          # needs ratings + notes.md
```

Expected: exit 0; `verification/report.md` contains the method section
(seed, sample, strata), overall rating counts, the per-district table
covering all 38 districts with n and rating distribution, flagged
districts (correct share < 50 %) marked, the comparison section naming
the Erlangen→Bamberg warning, all five limitation classes with content,
and non-binding recommendations. Invalid ratings (missing patch, unknown
rating) make the command exit 1.

## Scenario 5 — Zero changes to the published map/site (FR-005/010, SC-006)

```text
git status --porcelain                                   # only verification/ + code changes
.venv/bin/python -m pytest tests/                        # full suite green
make check-public                                        # FR-010 scan clean
```

Expected: no diff in `dist-assets/`, `src/site/`, `workers/`, or
workspace files; the existing pytest suite passes unchanged; the public
scan stays clean.

## Scenario 6 — District boundaries documented (R-2)

```text
python - <<'EOF'
import json
fc = json.load(open('verification/stadtteile.geojson'))
print(len(fc['features']))
EOF
```

Expected: 38 features; `verification/README.md` records the source
(GDI-MA), license (dl-de/by-2-0), download date, and attribution.
