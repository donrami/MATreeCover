# Provenance — Neighborhood-level tree canopy cover quantification in urban heat exposure studies

**Slug:** `neighborhood-tree-canopy-heat-aggregation`
**Date:** 2026-08-06
**Deliverable:** `outputs/neighborhood-tree-canopy-heat-aggregation.md`

## 1. Date and run context

- Literature review conducted and finalized on 2026-08-06 in `/home/mainuser/Desktop/MATreeCover`.
- Gathering: web searches (`web_search`, ~15 query rounds, 6 results/query) + full-text fetches (`fetch_content`, `get_search_content`) + one local PDF (Song et al. 2024) parsed from `/home/mainuser/Downloads/do-greenspaces-really-reduce-heat-health-impacts-evidence-for-different-vegetation-types-and-distanc.md`.

## 2. Sources consulted vs. accepted vs. rejected

- **URLs/records consulted:** ~70 distinct sources identified across search rounds (peer-reviewed papers, systematic reviews, conference contribution, operational HVI documentation, GIS toolchain docs, preprints, data repositories).
- **Accepted into the review:** 60 sources listed in Section 9 of the deliverable. All were URL-checked by the verifier agent on 2026-08-06: **0 dead links**; a small number flagged `[BLOCKED]` (ScienceDirect bot wall) with metadata confirmed via CrossRef, and two `[OK-M]` entries retain explicitly marked unverified details (National US HVI "55,267 tracts" figure; Lancet Planetary Health 2025 full author list).
- **Rejected / not used:** search hits that were off-topic, duplicates, or insufficiently documented: e.g., generic i-Tree marketing pages beyond the method docs (only i-Tree Canopy method page and UK ward guide accepted), a KipHub mirror of Wolf & McGregor (rejected in favor of the Durham repository record), an SSRN preprint on green provision (rejected in favor of the peer-reviewed Nature Communications series), non-archival slide decks, and paywalled pages whose claims could not be checked (claims from those were not included).
- **Tool-level blocked capability:** alphaXiv API (both the `alpha_search` tool and the `alpha` CLI) returned `fetch failed` for every query on 2026-08-06. No alphaXiv-sourced papers are in this review; coverage relies on publisher/PMC/repository pages. Recorded as a gap, not silently ignored.

## 3. Verification status

- **Verifier pass (subagent `verifier`):** every URL in the Sources section loaded/verified; metadata items previously flagged ⚠ were resolved against source pages and CrossRef records. Material corrections: Singapore scale/buffer study is **Zhang & Tan 2019** (IJERPH 16(4):578), not "Labib et al. 2020"; Baltimore study is **Ibebuchi & Abu 2026** in *World* 7(1):6, not *Urban Science*; Paris metric-comparison study is **Aboudrar-Méda & Falchetta 2026** in *Environ. Res.: Infrastruct. Sustain.* 6(2):021001, not *Environ. Res.: Health*; Chen et al. 2022 Global North Gini **0.24** (Nat Commun 13:4636); Huang et al. 2025 coefficient is **per 10,000 persons/km²/decade**; UGCoP greenspace DOI corrected to 10.1016/j.ufug.2023.127972; PNAS Nexus year corrected to 2024.
- **Reviewer pass (subagent `reviewer`):** science review found 1 FATAL (summary misstated Chen et al. Gini as a supply-vs-exposure contrast — fixed to the correct within-city exposure-inequality reading), 6 MAJORs (configuration-vs-provision decomposition misread; densification directional claim overstatement; BWB formula normalization + asymptote; three unsourced parentheticals; dangling Tate citation; Baltimore 13–15%→12–14%), and 10 MINORs (definitions at first use, quote splice, zombie "US/" fragment, "(SOAs)" gloss, canopy-consensus hedging, park-inflation hedging, Baltimore statistics annotation, Mermaid taxonomy diagram added). All FATAL/MAJOR and MINOR items were fixed in a single editing pass; the fixed file was re-checked on disk (grep verification: no residual "0.27", "per 1000", "13:6461", "US/global", "Tate 2012", "where greenery sits", "(SOAs)").
- **Remaining explicitly marked caveats in the deliverable:** `[BLOCKED]`/`[OK-M]` entries noted above; the alphaXiv gap; park-cooling claims attributed to single sources where that is the case.
- No experimental results were generated; §8 recommends a head-to-head aggregation experiment as a next step (not run here — data/scope beyond a literature review).

## 4. Intermediate research files used

| File | Role |
|---|---|
| `outputs/.plans/neighborhood-tree-canopy-heat-aggregation.md` | Plan, task ledger, verification log |
| `outputs/.plans/neighborhood-tree-canopy-heat-aggregation-draft.md` | Pre-verification synthesis draft |
| `outputs/.plans/neighborhood-tree-canopy-heat-aggregation-cited.md` | Cited draft after verifier pass and reviewer-fix pass |
| `outputs/.plans/neighborhood-tree-canopy-heat-aggregation-verification.md` | Verifier report (per-URL status, metadata resolutions) |
| `outputs/.plans/neighborhood-tree-canopy-heat-aggregation-review.md` | Reviewer report (FATAL/MAJOR/MINOR findings) |
| `/home/mainuser/Downloads/do-greenspaces-really-reduce-heat-health-impacts-evidence-for-different-vegetation-types-and-distanc.md` | Full text of Song et al. 2024 (Environment International 191:108950) |
| `outputs/neighborhood-tree-canopy-heat-aggregation.md` | **Final deliverable** (this run's canonical artifact) |
| `outputs/neighborhood-tree-canopy-heat-aggregation.provenance.md` | This file |

## 5. Reuse notes

- Any quantitative claim in the deliverable traces to the URL listed next to it in Section 9 or to the local Song et al. PDF; claims sourced only from abstracts are labeled "(per the paper's abstract)".
- Two figures in the deliverable come from sources with internal discrepancies (Baltimore decile 12–14% vs 13–15%; Huang et al. percentages 74.7%/56.8%); both are annotated in the text.
