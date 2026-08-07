# Verification report — `neighborhood-tree-canopy-heat-aggregation`

**Draft verified:** `outputs/.plans/neighborhood-tree-canopy-heat-aggregation-draft.md`
**Cited draft (deliverable):** `outputs/.plans/neighborhood-tree-canopy-heat-aggregation-cited.md`
**Verifier:** Feynman verifier agent · **Date:** 2026-08-06

Method: every URL in the draft's Sources section (plus inline DOIs) was loaded with `fetch_content` (with CrossRef/journal records as fallback for paywalled/blocked pages; web_search used for targeted metadata). Status legend: **OK** = resolves to the cited work and content matches; **OK-M** = URL/metadata confirmed but a specific numeric detail is unverified; **SUSPECT** = loads but content does not match the claim; **DEAD** = does not load; **BLOCKED** = page blocked to fetchers (metadata confirmed via second source).

---

## 1. URL status table

### HVI reviews & constructions
| URL | Status | Notes |
|---|---|---|
| https://pmc.ncbi.nlm.nih.gov/articles/PMC8531084/ | OK | Niu et al. 2021, Curr Clim Change Rep 7(3):87–97. Verified 13 studies, 8/13 census units, 11/13 PCA/FA, 5/13 hazard-exposure factors, weak validation, He et al. 2019 500 m grid. |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC2801183/ | OK | Reid et al. 2009, EHP 117(11):1730–1736. |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC3346770/ | OK | Reid et al. 2012, EHP 120(5):715–720. |
| https://durham-repository.worktribe.com/output/1467115/ | OK-M | Repository landing page loads; Wolf & McGregor 2013, Weather Clim Extremes 1:59–68 (DOI 10.1016/j.wace.2013.07.004) confirmed via Niu 2021 and Bao 2015 reference lists. |
| https://www.mdpi.com/1660-4601/12/7/7220 | OK | Bao, Li & Yu 2015, IJERPH 12(7):7220–7234. ⚠ resolved: first author Junzhe Bao. |
| https://www.mdpi.com/1996-1073/15/19/6998 | OK | "Understanding Urban Heat Vulnerability Assessment Methods: A PRISMA Review", Energies 15(19):6998. |
| https://a816-dohbesp.nyc.gov/IndicatorPublic/data-features/hvi/ | OK-M | Page loads (JS-heavy). "Median neighborhood green space ≈ 25%" not confirmed from page → UNVERIFIED. |
| https://doee.dc.gov/…/Methodology%20Report_Update%2005.11.22web_0.pdf | OK | DC Heat Exposure Index methodology PDF loads. |
| https://www.planning.nsw.gov.au/…/heat-vulnerability-urban-tree-canopy-cover-levels-greater-sydney-councils-goc.pdf | OK | NSW Greater Sydney HVI/canopy product loads. |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC9744626/ | OK-M | "Residential and Race/Ethnicity Disparities in Heat Vulnerability in the United States" loads. "55,267 tracts" figure UNVERIFIED. |

### UHI aggregation & MAUP
| URL | Status | Notes |
|---|---|---|
| https://data.mendeley.com/datasets/x9mv4krnm2/3 | OK | Chakraborty, Hsu, Sheriff & Manya; "spatial mean of pixels intersecting the census tract" confirmed verbatim. |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC8149665/ | OK | Hsu, Sheriff, Chakraborty, Manya 2021, Nat Commun 12:2721. ⚠ resolved (author order per journal record: Hsu first). |
| https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2021EF002016 | OK | Benz & Burney 2021, Earth's Future 9(7):e2021EF002016. |
| https://www.mdpi.com/1660-4601/19/19/12314 | OK | Johnson 2022, IJERPH 19(19):12314. |
| https://doi.org/10.1093/pnasnexus/pgae176 | OK | Liu & Smith-Greenaway, PNAS Nexus 3(5):pgae176, **2024** (draft said 2023). Population-weighted tract-level exposure confirmed. |
| https://www.sciencedirect.com/science/article/abs/pii/S2210670724005729 | BLOCKED | ScienceDirect bot wall. Metadata resolved via CrossRef/other sources: **Deng, Liu, Feng & Xiong 2024, Sustain Cities Soc 114:105747** (DOI 10.1016/j.scs.2024.105747). "87 cities, 12 scales" detail UNVERIFIED. |
| https://link.springer.com/article/10.1007/s10980-026-02339-6 | OK | Zhang et al. 2026, Landscape Ecology 41(5):77. ⚠ resolved: authors Huina Zhang et al.; 3×3 km optimal unit and green-space ratio q=0.641 confirmed (web_search). |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC6462107/ | OK | Ziter et al. 2019, PNAS 116(15):7575–7580. |
| https://www.mdpi.com/2073-445X/13/11/1741 | OK | Ralls, Polyakov & Shandas 2024, Land 13(11):1741. ⚠ resolved; 10/30/60/90 m scales confirmed. |
| https://www.mdpi.com/2073-445X/14/8/1686 | OK | Grace, Bolleter, Barghchi & Lund 2025, Land 14(8):1686. ⚠ resolved (year 2025, not 2026); ΔTs 10–15 °C vs ΔTa ≈ 2 °C claims confirmed. |
| https://learn.arcgis.com/en/projects/map-and-analyze-the-urban-heat-island-effect/ | OK | Esri tutorial loads. |
| https://gdal.org/en/latest/programs/gdal_raster_zonal_stats.html | OK | GDAL zonal-stats docs load. |
| https://www.mdpi.com/2072-4292/15/7/1783 | OK | Wang, Zhang & Yu 2023, Remote Sensing 15(7):1783 (Beijing subdistrict LST). |

### Population-weighted exposure & equity
| URL | Status | Notes |
|---|---|---|
| https://www.nature.com/articles/s41467-022-32258-4 | OK | Chen, Wu, Song, Webster, Xu & Gong 2022, Nat Commun **13:4636** (draft's 13:6461 wrong). Ecological-fallacy quote verbatim. Gini: Global South **0.47**, Global North **0.24** (draft's 0.27 wrong). Provision 21.93% of variance (~22% in draft ✓). |
| https://www.nature.com/articles/s41467-023-41620-z | OK | Wu, Chen, Webster, Xu & Gong 2023, Nat Commun 14:6460. |
| https://www.nature.com/articles/s41467-024-51355-0 | OK | Li et al. 2024, Nat Commun 15:7108. |
| https://www.nature.com/articles/s41467-023-38596-1 | OK | Massaro et al. 2023, Nat Commun 14:2903. |
| https://www.nature.com/articles/s41598-025-96045-z | OK | Huang, Stone Jr., Guan & Liang 2025, Sci Rep 15:13860. ⚠ resolved. **Correction:** coefficient is 0.5 K/decade per **10,000** persons/km²/decade density decline (draft's "per 1000" 10× off; "±0.04" not found in the paper text and removed). |
| https://link.springer.com/article/10.1140/epjds/s13688-026-00627-4 | OK | Martinez, Argota Sánchez-Vaquerizo & Mahajan 2026, EPJ Data Science 15:25. ⚠ resolved. |
| https://www.mdpi.com/2673-4060/7/1/6 | OK | **Journal is *World* 7(1):6 (ISSN 2673-4060), NOT *Urban Science*.** Ibebuchi & Abu 2026. All Baltimore numbers (47–51→13–15%, 3.4–4.1×, ρ=−0.51/−0.503) confirmed. |
| https://www.mdpi.com/2220-9964/8/6/286 | OK | "Measuring Urban Greenspace Distribution Equity…", IJGI 8(6):286. |
| https://www.mdpi.com/2073-445X/14/1/132 | OK | Land 14(1):132 multi-scale exposure/equality paper. |
| https://www.sciopen.com/article/10.1007/s12273-024-1180-z | OK | Zhong, Zhao, Ren, Teng & Zhang 2024, **Building Simulation** 17(11):1933–1949. ⚠ resolved (journal guess confirmed). |
| https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249715 | OK | McDonald et al. 2021, PLoS ONE 16(4):e0249715 (title/author list confirmed via CrossRef references). |
| https://www.nature.com/articles/s42949-024-00150-3 | OK | McDonald et al. 2024, npj Urban Sustainability 4:18. |
| https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0122051 | OK | Schwarz et al. 2015, PLoS ONE 10(4):e0122051. |

### Greenspace measurement methods
| URL | Status | Notes |
|---|---|---|
| https://pmc.ncbi.nlm.nih.gov/articles/PMC6406785/ | OK (SUSPECT resolved) | **Authors are Liqing Zhang & Puay Yok Tan, IJERPH 16(4):578, 2019 — the draft's "Labib et al. 2020" attribution is wrong.** All claims (3 metrics, circular/nested/network buffers, 50–2800 m, strongest 400–1600 m) match this paper. |
| https://link.springer.com/article/10.1186/s12942-025-00425-7 | OK | Garrett et al. 2025, IJHG 24:37. 8–10% built-up; Kendall τ 0.56–0.89; "overestimate non-built-up overall" confirmed. |
| https://ij-healthgeographics.biomedcentral.com/counter/pdf/10.1186/s12942-018-0149-5.pdf | OK-M | Laatikainen, Hasanzadeh & Kyttä 2018, IJHG 17:29. ⚠ resolved. Draft's specific "green space–wellbeing significant only with individualized models" result **UNVERIFIED** (paper is a methods review comparing activity-space vs residence-based models; the specific significance claim not confirmed). |
| https://epub.ub.uni-muenchen.de/131805/1/PIIS2542519625002487.pdf | OK-M | *The Lancet Planetary Health* 9(11), Nov 2025 (confirmed via Lancet issue page + repository records). PDF text not extractable; full author list **UNVERIFIED**. |
| https://jech.bmj.com/content/65/10/853 | OK | Mitchell, Astell-Burt & Richardson 2011, JECH 65(10):853–858. |
| https://www.sciencedirect.com/science/article/pii/S0013935122024823 | BLOCKED | ScienceDirect bot wall. Resolved: de la Iglesia Martinez & Labib 2023, Environ. Res. (DOI 10.1016/j.envres.2022.115155). |
| https://www.mdpi.com/2073-445X/14/3/517 | OK | Lee, Chamberlain & Park 2025, Land 14(3):517. ⚠ resolved. |
| https://ual.sg/publication/2025-ufug-greenery-exposure/2025-ufug-greenery-exposure.pdf | OK | Liu, Lu & Biljecki 2025, UFUG methodological review. |
| https://www.mdpi.com/1660-4601/15/9/1841 | OK | Kwan 2018, IJERPH 15(9):1841 (NEAP). |
| https://www.sciencedirect.com/science/article/pii/S1618866723001437 | OK | Liu, Kwan & Yu 2023, UFUG 85:127972. **Correct DOI is 10.1016/j.ufug.2023.127972** — the draft's inline 10.1016/j.ufug.2023.127933 belongs to a different paper (Wolf-Jacobs et al., green-gentrification review) and was corrected. |
| https://www.sciencedirect.com/science/article/pii/S0277953625005209 | BLOCKED | Resolved via CrossRef: Liu, Kwan, Song, Yu & Cui 2025, Soc Sci Med 379:118190. |
| https://canopy.itreetools.org/ | OK | Loads. |
| https://cdn.forestresearch.gov.uk/…/canopy_cover_webmap_user_guide_-_updated_march_2021.pdf | OK | Loads. |

### Heat–canopy/greenspace health
| URL | Status | Notes |
|---|---|---|
| https://escholarship.org/content/qt53v4h0ph/qt53v4h0ph.pdf | OK-M | Graham et al. 2016, UFUG 20 (DOI 10.1016/j.ufug.2016.08.005). <5% vs >5% ≈5× calls and ~80% reduction confirmed (abstract + secondary summaries). "~15× vs >70%" **UNVERIFIED**. |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC10510815/ | OK | Song et al. 2023, EHP 131(9):097007. All RR/p values confirmed verbatim. |
| https://researchonline.lshtm.ac.uk/id/eprint/4673664/1/Song-etal-2024-…pdf | OK | Full text downloaded and checked. Environ Int 191:108950; optimal ≈1000 m; RR ratios 1.424 (NDVI), 1.191 (total), 1.227 (forest); "marked difference" confirmed. Local copy saved. |
| https://iopscience.iop.org/article/10.1088/2634-4505/ae75a1 | OK (SUSPECT resolved) | Aboudrar-Méda & Falchetta 2026, **Environmental Research: Infrastructure and Sustainability** 6(2):021001 (NOT Environ. Res.: Health). 18.5/16/14% and "reverse their sign" quote confirmed. |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC7287541/ | OK | O'Brien, Gridley, Trlica, Wang & Shrivastava 2020, AJPH 110(7):994–1001. 38% within-tract variance and no independent tract-average LST effect confirmed. |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC7103759/ | OK | Murage et al. 2020, Environ Int 134:105292. |
| https://bmjopen.bmj.com/content/14/9/e081632 | OK | BMJ Open 14(9):e081632 (title confirmed via CrossRef refs). |
| https://ecoevorxiv.org/repository/view/8204/ | OK | "Greenspace modifies the associations between heat and mortality: A systematic review and meta-analysis of observational studies" (preprint). |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC4455581/ | OK | Chuang & Gober 2015, EHP 123(6):606–612. |
| https://pubmed.ncbi.nlm.nih.gov/36088684/ | OK | Choi et al. 2022, eBioMedicine 84:104251 (confirmed via Song 2023 ref list). |
| https://digitalcommons.odu.edu/…/viewcontent.cgi?article=1086&context=vmasc_pubs | OK-M | Zamponi et al. 2023, Ecological Modelling 483:110445. URL resolves; PDF text not extractable this session. |

### Ecological fallacy / theory
| URL | Status | Notes |
|---|---|---|
| https://pmc.ncbi.nlm.nih.gov/articles/PMC4209486/ | OK | Wakefield, "Spatial Aggregation and the Ecological Fallacy", Ch. 30, Handbook of Spatial Epidemiology. Content verified. |
| https://www.annualreviews.org/content/journals/10.1146/annurev.publhealth.29.020907.090821 | OK | Morgenstern 2008, "Ecologic Studies Revisited", Annu Rev Public Health 29:37–52. |

**Dead links: 0.** All URLs resolved.

---

## 2. ⚠ metadata resolutions (per the task list)

1. **Niu et al. 2021 (HVI systematic review)** — ✅ CONFIRMED. First author **Yanlin Niu**; *Current Climate Change Reports* 7(3):87–97, published online 2021-04-27; DOI 10.1007/s40641-021-00173-3. Full author list: Niu, Li, Gao, Liu, Xu, Vardoulakis, Yue, Wang, Liu.
2. **Chen et al. 2022 (Nat Commun)** — ✅ CONFIRMED. Authors **Bin Chen, Shengbiao Wu, Yimeng Song, Chris Webster, Bing Xu, Peng Gong**; *Nat Commun* **13, 4636** (2022) — the draft's "13:6461" was wrong. Also corrected Gini 0.47/0.24.
3. **"Declining urban density…" Sci Rep 2025** — ✅ CONFIRMED. Authors **Kangning Huang, Brian Stone Jr., ChengHe Guan, Jiayong Liang**; Sci Rep **15, 13860** (2025). Title actually reads "…surface heat extremes", not "…SUHI".
4. **"Not your mean green" EPJ Data Science 2026** — ✅ CONFIRMED. Authors **Jenny Martinez, Javier Argota Sánchez-Vaquerizo, Sachit Mahajan**; EPJ Data Science **15:25**, published 2026-02-09.
5. **"Canopy Cover, Deprivation, and Cancer-Risk Burdens" /7/1/6** — ✅ CONFIRMED with correction. Journal is **World** 7(1):6 (not *Urban Science*); authors **Chibuike Chiedozie Ibebuchi, Itohan-Osa Abu**; 2026.
6. **Labib et al. 2020 IJERPH 16(4):578** — ❌ ATTRIBUTION CORRECTED. The Singapore study is **Zhang, L. & Tan, P.Y. (2019)**, IJERPH 16(4):578. (S.M. Labib's relevant 2020 papers are different articles: Environ. Res. 180:108869; Comput. Environ. Urban Syst. 82:101501.)
7. **"Methodological guidance for selecting buffers…"** — ✅ PARTLY CONFIRMED. Journal confirmed as **The Lancet Planetary Health, 9(11), November 2025** (PII S2542519625002487). Full author list UNVERIFIED (PDF not extractable).
8. **IOP 10.1088/2634-4505/ae75a1** — ✅ CONFIRMED with correction. Journal is **Environmental Research: Infrastructure and Sustainability** 6(2):021001; authors **Armande Aboudrar-Méda, Giacomo Falchetta**; 2026.
9. **"Urban Heat Islets" PMC7287541** — ✅ CONFIRMED. **O'Brien, Gridley, Trlica, Wang & Shrivastava**, Am J Public Health 110(7):994–1001, 2020.
10. **"Unpacking Park Cool Island Effects" Land 14(8):1686** — ✅ CONFIRMED. **Grace, Bolleter, Barghchi & Lund, 2025** (not 2026).
11. **"Spatial Aggregation and the Ecological Fallacy" PMC4209486** — ✅ CONFIRMED. Chapter 30 of the *Handbook of Spatial Epidemiology* (Wakefield, J.).
12. **"Capturing exposure…" IJHG 2018** — ✅ CONFIRMED. **Tiina E. Laatikainen, Kamyar Hasanzadeh, Marketta Kyttä**; IJHG 17:29 (2018).
13. **"Tackling the modifiable areal unit problem" SCS 2024** — ✅ CONFIRMED. **H. Deng, K. Liu, J. Feng, Y. Xiong**; Sustain Cities Soc **114:105747** (2024).
14. **GBA sciopen 10.1007/s12273-024-1180-z** — ✅ CONFIRMED. Journal **Building Simulation** 17(11):1933–1949; authors **Zhong X., Zhao L., Ren P., Teng Y., Zhang X.**; 2024.
15. **Hsu et al. 2021 Nat Commun (PMC8149665)** — ✅ CONFIRMED. **Hsu, Sheriff, Chakraborty, Manya**; Nat Commun **12:2721** (2021).
16. **Bao et al. 2015 IJERPH 12(7):7220** — ✅ CONFIRMED. **Junzhe Bao, Xudong Li, Chuanhua Yu**, IJERPH 12(7):7220–7234.

---

## 3. Claims that could not be fully verified (flagged UNVERIFIED in the cited draft)

1. NYC DOHMH HVI "median neighborhood green space ≈ 25%" — not in the fetched page content.
2. National US HVI "55,267 tracts" — not confirmed from the PMC article content fetched.
3. Deng et al. 2024 SCS "87 cities, 12 scales" — ScienceDirect blocked; metadata confirmed but these specific figures not independently verified.
4. Graham et al. 2016 "~15× vs >70%" — not confirmed (5× and ~80% claims were).
5. Laatikainen et al. 2018 Helsinki specific significance result — not confirmed from the paper text checked.
6. Lancet Planetary Health 2025 buffer-guidance full author list — PDF text not extractable; journal/issue/year confirmed.
7. Inline parentheticals with no source entry in the research files: "ICUC12 microclimate study"; "Boston CEE 2025 10.1038/s43247-025-02462-3"; "2SFCA cooling-equity studies" — kept but explicitly marked **UNVERIFIED** (not silently dropped). Recommend either verifying these sources or deleting the parentheticals.

## 4. Substantive corrections applied to the cited draft

- Baltimore study journal: *Urban Science* → **World** 7(1):6 (Ibebuchi & Abu 2026).
- Singapore study attribution: "Labib et al. 2020" → **Zhang & Tan 2019** (IJERPH 16(4):578).
- Paris study journal: *Environ. Res.: Health* → **Environmental Research: Infrastructure and Sustainability** 6(2):021001.
- Chen et al. 2022: Nat Commun **13:4636** (was 13:6461); Global North Gini **0.24** (was 0.27).
- Sci Rep 2025 SUHI claim: coefficient is **0.5 K/decade per 10,000 persons/km²/decade** (was "per 1000"); removed unsupported "±0.04".
- UGCoP inline DOI: **10.1016/j.ufug.2023.127972** (was the wrong 10.1016/j.ufug.2023.127933).
- PNAS Nexus year: **2024** (was 2023).
- Demystifying NDVI: confirmed as de la Iglesia Martinez & Labib 2023 (DOI 10.1016/j.envres.2022.115155).
- Added missing sources: Mears et al. 2020, Browning & Lee 2017, Browning et al. 2024, Reid et al. 2017, Kwan 2012 (all traceable in body text).

## 5. Artifacts

- Song et al. 2024 full text downloaded and verified; local copy saved outside the repository.
- No local copy of Song et al. 2024 was found at the path hinted in the draft; the draft's "(local copy…)" note was resolved via the LSHTM repository PDF.
