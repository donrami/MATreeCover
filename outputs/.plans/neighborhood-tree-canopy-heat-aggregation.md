# Plan: Neighborhood-level tree canopy cover quantification in urban heat exposure studies

**Slug:** `neighborhood-tree-canopy-heat-aggregation`
**Date:** 2026-08-06
**Type:** Literature review (source-heavy, evidence-first)

## Research questions

1. **Metric inventory** — What metrics quantify neighborhood-level tree canopy in urban heat studies? (area-weighted canopy share of district/ward, buffer-based greenness, building/population-weighted means, NDVI/EVI, % tree cover from land cover classification, i-Tree/LiDAR-based canopy)
2. **Standard practice for heat vulnerability indices (HVI)** — How is canopy/green space aggregated in HVIs at district/neighborhood level? Zonal statistics over administrative units vs. buffers vs. population-weighted?
3. **Standard practice for urban heat island (UHI) analysis** — LST–canopy relationships, zonal scales, buffer radii, MAUP sensitivity.
4. **Building-weighted vs. area-weighted** — methodological distinction (weighting by building footprint / resident proxy vs. plain areal share), when each is used, and quantitative differences documented.
5. **Misinterpretations** — What goes wrong when one metric is presented as the other (ecological fallacy, park inflation, dense-district bias, direction of bias in exposure–health associations).

## Scope & sources

- Peer-reviewed literature, ~2009–2026, with classic MAUP background (Openshaw 1984; Fotheringham & Wong 1991) and older HVI roots (Reid et al. 2009).
- Grey literature: EPA/CDC/UKHSA heat vulnerability guidance, city HVI reports (NYC, Portland, Baltimore, London) if needed for "standard practice."
- Databases: alphaXiv/arXiv (limited for applied env-health; use primarily PubMed-adjacent sources via web + alpha semantic search), Google Scholar via web_search, journal pages.
- Methodological anchors: MAUP (Modifiable Areal Unit Problem), ecological fallacy, buffer vs. administrative-unit green space exposure (Labib et al. 2020), dasymetric/building-footprint population weighting.

## Expected sections

1. Summary / key findings
2. Metrics in use: inventory + definitions
3. Aggregation practice in HVIs
4. Aggregation practice in UHI/LST analysis
5. Building-weighted vs. area-weighted: formal difference, examples, quantitative comparisons
6. Misinterpretations and bias directions
7. Consensus, disagreements, gaps
8. Open questions + recommended next steps (incl. a concrete replication/measurement experiment)
9. Sources

## Task ledger

| # | Task | Status |
|---|------|--------|
| T1 | Write plan | done |
| T2 | Search: alpha semantic/keyword (HVI + canopy, LST + canopy, MAUP + green space) | blocked — alphaXiv API unreachable (tool + CLI both "fetch failed"); recorded in provenance |
| T3 | Search: web (HVI methods, buffer vs. area aggregation, building-weighted exposure, population-weighted LST) | done — ~15 query rounds; key sources identified (see draft) |
| T4 | Read key papers (full text where available): HVI reviews (Niu 2021, Reid 2009, Wolf & McGregor 2013), Labib 2020, Song 2024, Garrett 2025, MAUP-heat, population-weighted exposure | done — full texts: Niu 2021, Labib 2020, Song 2024 (local PDF), Garrett 2025; abstracts/snippets for rest |
| T5 | Delegate researcher subagent for wide triage (if sweep warrants) | superseded — direct search sweep achieved wide coverage; skipped to save cycles |
| T6 | Synthesize draft `outputs/.plans/<slug>-draft.md` | done |
| T7 | Verifier: inline citations + URL checks on draft | done — all URLs checked 0 dead; ⚠ metadata resolved; report `-verification.md` |
| T8 | Reviewer: unsupported claims / single-source criticals / logic gaps | done — 1 FATAL + 6 MAJOR + 10 MINOR; report `-review.md` |
| T9 | Fix FATAL issues; re-verify if needed | done — all items fixed in cited draft; grep re-check on disk clean |
| T10 | Deliver `outputs/<slug>.md` + `outputs/<slug>.provenance.md`; verify on disk | done — both files verified present below |

## Verification log

| Check | Result |
|-------|--------|
| Verifier URL sweep (2026-08-06) | 0 dead links; `[BLOCKED]` ScienceDirect ×3 (metadata via CrossRef); 2 `[OK-M]` with marked caveats |
| Reviewer science pass | 1 FATAL (Chen Gini misstatement), 6 MAJOR, 10 MINOR — all fixed |
| Post-fix grep re-check | no residual `0.27`, `per 1000`, `13:6461`, `US/global`, `Tate 2012`, `where greenery sits`, `(SOAs)`; formula normalized; Mermaid added |
| Final files on disk | `outputs/neighborhood-tree-canopy-heat-aggregation.md` (277 lines) + `.provenance.md` present; final doc has no verification-header/appendix noise |
| alphaXiv | BLOCKED (tool + CLI `fetch failed`); noted in provenance |
