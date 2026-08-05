# Contract: Verify Report

Scope: the structure and content rules of `verification/report.md`.
Requirements: FR-003, FR-006, FR-007, FR-008, FR-009; success criteria
SC-003, SC-004, SC-005, SC-007, SC-008. See [../data-model.md](../data-model.md).

## Generation

`verify-report` generates `verification/report.md` from:

- `verification/sample.jsonl` (method, strata, degeneracy summary)
- `verification/ratings.jsonl` (overall + per-district findings)
- `verification/notes.md` (owner-written comparison and limitations)

All numbers in the report come from the ratings/sample files. The owner
never hand-edits numbers in the report; judgment text lives in
`notes.md` and is merged in verbatim.

## Structure

```text
# Verifikation der Baumerkennung (Mannheim)         [title, DE matching the map]
Datum / Date, seed, sample size, workspace id, district layer source + license

## Methode (Method)
- sample design (districts × bands, allocation rule, seed)
- inspection criteria summary (link: contracts/verify-ratings.md)
- re-inspection rule (every 10th patch)

## Gesamtergebnis (Overall findings)
- rating counts and shares across the rated sample
- count of unrated patches (degeneracy no-imagery), disclosed separately

## Ergebnisse nach Stadtteil (Per-district findings)
- table: district | n | correct | over | under | assessment | flag
- assessment ∈ {trustworthy, overstated, understated, inconclusive}
- flag = "FLAGGED" when correct share < 50 % in the district

## Vergleich mit dem Referenz-Transferproblem (Comparison)
- the model author's Erlangen→Bamberg warning vs. what the inspection
  shows for Mannheim; qualitative (no published reference numbers)
  — text from notes.md

## Einschränkungen (Limitations)
- degenerate patches (no-imagery / empty-mask / full-mask counts)
- small-sample districts (n below a documented minimum, e.g. < 5)
- boundary/halo areas
- single-inspector judgment
- re-inspection divergence (if any)

## Empfehlungen (Recommendations, non-binding)
- follow-up options for the owner (e.g. disclaimer, threshold review,
  re-inspection) — explicitly NOT actions of this feature (FR-009)
```

## Rules

- **Flagging (FR-003)**: a district is flagged when fewer than half of
  its rated patches are `correct`. The overall (city-wide) correct share
  is stated so the flag reads against the baseline.
- **Assessment**: `trustworthy` when correct share ≥ 50 % and n ≥ 5;
  `inconclusive` when n < 5 (small sample, edge case); otherwise
  `overstated` (over-dominates) or `understated` (under-dominates).
- **Districts without buildings**: not applicable in Mannheim (all 38
  have buildings), but the rule stands: if a district had no buildings,
  it would be listed with n = 0, not omitted.
- **Comparison (FR-007)**: the section must exist and must explicitly
  name the model author's reported transfer problem and whether the
  Mannheim findings match, contradict, or are inconclusive relative to
  it.
- **Disclosure (FR-008)**: all five limitation classes must appear with
  content (counts or explicit "none observed"); empty sections are not
  allowed.
- **Public-safety (FR-010)**: report and notes must pass the repo's
  public scan — no personal paths, credentials, or internal tooling
  references.

## Invariants (tested)

- Report generation fails (exit 1) on a missing/invalid ratings file.
- The per-district table covers every district with buildings.
- Flagged districts satisfy the < 50 % rule; un-flagged ones do not.
- Every number in the report matches the ratings file (spot-checked by
  test on a fixture ratings set).
- All limitation classes present with non-empty content.
