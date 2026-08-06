# Neighborhood-level tree canopy cover quantification in urban heat exposure studies

**Slug:** `neighborhood-tree-canopy-heat-aggregation` · **Draft date:** 2026-08-06 · **Status:** verified (URLs and metadata checked 2026-08-06)

> **Verification header.** All source URLs were loaded and checked on 2026-08-06. Metadata items previously flagged ⚠ are resolved below and confirmed against the source pages / CrossRef records; unresolved items are marked **UNVERIFIED** with a note (see the appendix *Verification of sources and metadata*, and the companion report `neighborhood-tree-canopy-heat-aggregation-verification.md`). Corrections of substance introduced by verification: (i) the Baltimore TCI study is published in the journal *World* 7(1):6 (Ibebuchi & Abu 2026), not *Urban Science*; (ii) the Singapore scale/buffer study is **Zhang & Tan 2019**, IJERPH 16(4):578 (not "Labib et al. 2020"); (iii) the Paris metric-comparison study is **Aboudrar-Méda & Falchetta 2026** in *Environmental Research: Infrastructure and Sustainability* 6(2):021001 (not *Environ. Res.: Health*); (iv) Chen et al. 2022 report Global North Gini **0.24** (not 0.27), Nat Commun **13:4636** (not 13:6461); (v) Huang et al. 2025 (Sci Rep 15:13860) report ≈0.5 K/decade per **10,000** persons/km²/decade density decline (the draft's "per 1000" was 10× off); (vi) the UGCoP greenspace paper (Liu, Kwan & Yu 2023, UFUG 85:127972) was cited with a wrong DOI in the body (10.1016/j.ufug.2023.127933 belongs to a different paper); (vii) PNAS Nexus pgae176 is Liu & Smith-Greenaway **2024** (not 2023).

---

## 1. Summary / key findings

1. **Two families of metrics dominate the literature, and they answer different questions.** Area-weighted canopy share of a district (canopy area ÷ district area, i.e., a zonal mean of a binary canopy raster) measures *provision* of tree cover on land. Building-weighted or population-weighted means of canopy within buffers (canopy share inside a radius r around each building/residence, averaged with weights) measure *exposure* of people to canopy. The two are routinely conflated, and the conflation is the central methodological hazard in this literature.

2. **For heat vulnerability indices (HVIs) and urban heat island (UHI) mapping at district/neighborhood level, the de facto standard is the area-weighted zonal mean at the administrative unit** (census tract/block group, LSOA/SOA, SA1, ward): vegetation or canopy % per unit, and LST zonal means per unit. This is documented in HVI reviews (Niu et al. 2021, *Current Climate Change Reports* 7(3):87–97; Reid et al. 2009, EHP 117(11):1730–1736; Wolf & McGregor 2013, *Weather and Climate Extremes* 1:59–68), operational HVIs (NYC DOHMH HVI; DC Heat Exposure Index methodology; NSW Greater Sydney HVI/canopy product), and UHI databases/tutorials (US SUHI database; Esri zonal-statistics workflows; Hsu et al. 2021, *Nature Communications* 12:2721).

3. **For individual- and population-level exposure studies, the standard is buffer-based canopy/greenery around residences, with population (or building/address) weighting** — e.g., Song et al. 2024 (*Environment International* 191:108950) used population-weighted greenspace exposure at buffers of 200–4000 m; Mears et al. 2020 (*Health & Place* 62:102284) averaged trees in 100 m buffers per residence within LSOAs (as described in Garrett et al. 2025); Garrett et al. 2025 (*Int J Health Geogr* 24:37) averaged land-cover % in 300 m postcode buffers weighted by domestic delivery addresses; Browning et al. 2024 (*Sci Total Environ* 907:167739) measure the "3-30-300" rule at address level.

4. **The two aggregation methods produce materially different numbers and different rankings**, with documented magnitudes: built-up (non-green) exposure is 8–10% higher when measured with address-weighted buffers than with LSOA area averages (Garrett et al. 2025); population-weighted canopy in Baltimore fell from 47–51% in the least-deprived decile to 13–15% in the most deprived (3.4–4.1× disparity; Ibebuchi & Abu 2026, *World* 7(1):6); population-weighted surface-UHI trends diverge from area-average trends by ≈0.5 K per decade per 10,000 persons/km² per decade decrease in population-weighted density (Huang, Stone Jr., Guan & Liang 2025, *Scientific Reports* 15:13860); greenspace *supply* vs *population-weighted exposure* differ in Gini inequality (0.47 for Global South vs 0.24 for Global North cities), with only ~22% of the exposure disparity attributable to provision itself (21.93% of variance; Chen et al. 2022, *Nature Communications* 13:4636).

5. **Presenting one metric as the other is an ecological-fallacy-class error.** The clearest statement in the literature: "measures of provision (in total or per capita) are often simplistically equated to actual exposure… aggregated unit measures of greenspace total supply or per capita supply produce an ecological fallacy—biased inferences of individual patterns from aggregated data" (Chen et al. 2022). Relatedly, district-level % canopy is inflated by parks and forest patches whose cooling does not reach residents (park cool-island air-temperature effects are small for most parks; Grace, Bolleter, Barghchi & Lund 2025, *Land* 14(8):1686), while building-weighted buffers can under-count the district parks that do provide some cooling. Metric choice can even reverse the sign or significance of heat–health effect estimates (Aboudrar-Méda & Falchetta 2026, *Environ. Res.: Infrastruct. Sustain.* 6(2):021001; Song et al. 2023, *Environ Health Perspect* 131(9):097007).

6. **The field is converging on reporting both** (provision + exposure) and on multi-scale sensitivity analysis (Zhang & Tan 2019, IJERPH 16(4):578; *Lancet Planetary Health* 9(11), 2025 buffer guidance; MAUP analyses, e.g., Zhang et al. 2026, *Landscape Ecology* 41(5):77; Deng, Liu, Feng & Xiong 2024, *Sustainable Cities and Society* 114:105747).

---

## 2. Metrics in use: inventory and definitions

### 2.1 Canopy and greenery metrics found in urban heat studies

| Metric | What it measures | Typical data source | Representative uses in heat studies |
|---|---|---|---|
| % tree canopy cover (area share) | Fraction of land surface covered by tree crowns | Aerial imagery classification (NAIP), LiDAR-derived canopy height models, i-Tree Canopy point sampling, NLCD/USFS tree canopy cover | Toronto heat-related ambulance calls (Graham et al. 2016, *Urban For. Urban Green.* 20:91–99, census-tract canopy); US income–tree-cover disparity (McDonald et al. 2021, PLoS ONE 16(4):e0249715, census blocks); DC Heat Exposure Index; Sydney Greening our City canopy product |
| NDVI / EVI greenness | Spectral greenness (continuous) | Landsat/Sentinel multispectral | HVI exposure and adaptation indicators (Reid et al. 2009 used vegetation cover from satellite imagery); heat–mortality effect modification (Song et al. 2023, EHP 131(9):097007) |
| % greenspace (land use/planimetry) | Area of green land use classes | Land-use maps, cadastral planimetry | Hong Kong heat–mortality (Song et al. 2023/2024); NYC HVI green-space component (tree/grass/shrub cover % of neighborhood) |
| Street-level green view index (GVI) | Eye-level visible greenery | Street-view imagery + deep learning | Paris heat–mortality attenuation (Aboudrar-Méda & Falchetta 2026); Hong Kong eye-level vs overhead (Song et al. 2023) |
| Canopy volume / shade metrics | 3D canopy structure, shade hours | LiDAR/CHM/DSM, 3D city models | Scale-dependent air-temperature effects (Ralls, Polyakov & Shandas 2024, *Land* 13(11):1741); tree-building shade (Ziter et al. 2019 PNAS 116(15):7575–7580 for scale dependence) |

Important caveat: NDVI and % canopy are not interchangeable; NDVI is sensitive to vegetation type and amount nonlinearly (de la Iglesia Martinez & Labib 2023, *Environmental Research*; "Demystifying NDVI"), and canopy vs. vegetation vs. park-area metrics correlate only partially and produce different health associations (Zhang & Tan 2019, IJERPH 16(4):578).

### 2.2 The two aggregation geometries under review

**Area-weighted canopy share of a district (AWD):**

```
CanopyShare(D) = (area of canopy within district D) / (area of D)
```

- Computed as a zonal mean of a binary (or % cover) canopy raster over the administrative unit.
- All land inside D counts equally — residential lots, parks, forests, industrial land, roads, water.
- This is the standard "canopy cover %" of municipal urban forestry (i-Tree Canopy; UK ward-level assessments; NSW suburb-level canopy).

**Building-weighted mean canopy in a buffer (BWB):**

```
For each building b: c(b) = canopy share within buffer(b, r)
BWCanopy(D) = Σ_b w_b · c(b)   with weights w_b ∝ footprint area (or count, or estimated residents)
```

- The unit of exposure is the building (residential footprint as a population proxy), and the *spatial support* is a buffer of radius r rather than the district polygon.
- When weights are population (gridded population, address/delivery-point counts), this is the "population-weighted exposure" family used in environmental-health research (Chen et al. 2022; Garrett et al. 2025; Song et al. 2024; Mears et al. 2020).
- Building-footprint weighting is a *cheap proxy* for population weighting; it is exact only if footprint area is proportional to residents, which fails for offices, warehouses, and large non-residential structures (a documented limitation in the dasymetric population-estimation literature; e.g., Garrett et al. 2025 note that address counts are preferable to area-based proxies).

Key geometric differences:
- AWD includes **all** land in the district; BWB includes **only land within r of buildings**, and excludes (or dilutes) large parks/forests whose canopy lies beyond r — but includes street trees right at residences.
- AWD is insensitive to *where people live inside the district*; BWB is anchored to it.
- As r → large, BWB converges toward a population-weighted AWD; as r → 0, BWB measures canopy immediately adjacent to buildings.

---

## 3. Aggregation practice in heat vulnerability indices (HVIs)

**Documented standard: census/administrative units + area-weighted zonal means, PCA-based index construction.**

- The systematic review of HVI development and validation (Niu et al. 2021, *Current Climate Change Reports* 7(3):87–97, DOI 10.1007/s40641-021-00173-3; PMC8531084) found, across 13 validated HVIs (2010–2020): spatial units are **census tracts, administrative areas, postal codes, or grids**; 8 of 13 used census-based units; PCA/FA was the dominant construction method (11/13); "landscape" (incl. vegetation coverage) was among the top-5 factor categories; but only 5 of 13 used hazard-exposure factors, and validation showed only **weak associations** between HVI and heat health outcomes.
- Reid et al. 2009 (EHP 117(11):1730–1736) — the template HVI: 10 factors (6 census demographics, 2 AC variables, **vegetation cover from satellite images**, diabetes prevalence) mapped to **39,794 census tracts**, factor analysis, summed scores. Green space entered as a tract-level area aggregate (factor 1 combined education/poverty/race/green space).
- Wolf & McGregor 2013 (London, *Weather and Climate Extremes* 1:59–68): 9 census-based proxies for 4,765 census districts (SOAs), PCA. Notably this HVI contained **no green-space component** — an example of the heterogeneity in whether canopy is included at all.
- Operational HVIs use the same geometry: **NYC DOHMH HVI** scores neighborhoods 1–5 using surface temperature, **green space (tree/grass/shrub cover % of the neighborhood)**, AC, and income (median neighborhood green space ≈ 25% — **UNVERIFIED**: the NYC DOHMH page loads but the 25% figure could not be confirmed from the page content); **DC Heat Exposure Index** aggregates tree canopy cover and impervious surface **averaged by census tract**; **NSW Greater Sydney** HVI + canopy cover reported at suburb/LGA level from SA1 data.
- Consequence: in HVI practice, canopy enters as an **area-weighted district share** — a provision metric — and is frequently labeled as a heat-exposure mitigation factor. Population weighting is rare in HVIs (notable exception: He et al. 2019 used a 500 m grid; per Niu et al. 2021).

## 4. Aggregation practice in urban heat island (UHI) analysis

**Documented standard: zonal statistics of LST/SUHI at census or district level; canopy as % cover per unit or per buffer.**

- The US SUHI database (Mendeley x9mv4krnm2; Chakraborty, Hsu, Sheriff & Manya) is explicitly built as "spatial mean of pixels intersecting the census tract" (tract-level zonal means of urban LST and NDVI).
- National-scale UHI-inequality studies use tract-level SUHI zonal means joined to tract demographics (Hsu et al. 2021, *Nat Commun* 12:2721; Benz & Burney 2021, *Earth's Future* 9(7):e2021EF002016; Johnson 2022, IJERPH 19(19):12314; Liu & Smith-Greenaway 2024, *PNAS Nexus* 3(5):pgae176 uses **population-weighted** tract-level exposure).
- Practitioner guidance (Esri "Map and analyze the urban heat island effect"; ArcGIS zonal statistics docs; GDAL raster zonal-stats; R terra `zonal`) all default to **area-weighted means of rasters within polygons** — i.e., the AWD-style aggregation is the toolchain default.
- Scale effects are documented and material: canopy–temperature relationships are scale-dependent (Ziter et al. 2019 PNAS — canopy effects depend on spatial scale and interact with impervious surfaces; Ralls, Polyakov & Shandas 2024, *Land* 13(11):1741 — effects vary across 10–90 m radii; Grace et al. 2025, *Land* 14(8):1686 — park cool-island effects small in air temperature for all but the largest parks). MAUP studies show LST driver rankings and effect sizes change with grid size (Zhang et al. 2026, *Landscape Ecology* 41(5):77, Zhengzhou: optimal unit 3×3 km; green-space ratio q = 0.641; Deng, Liu, Feng & Xiong 2024, *Sustainable Cities and Society* 114:105747: human-related factors more scale-sensitive than natural factors — **UNVERIFIED detail**: the paper's metadata is confirmed but the specific "87 cities, 12 scales" figures could not be read (ScienceDirect blocked) and remain unverified).

---

## 5. Building-weighted vs. area-weighted: where each is standard, and measured differences

### 5.1 Where each is (or should be) standard

| Context | Standard practice | Rationale |
|---|---|---|
| HVI construction at district/neighborhood level | Area-weighted zonal mean (canopy % or NDVI per census unit) | Index units must match census/demographic units; PCA on unit-level indicators; operational comparability |
| UHI mapping (LST/SUHI) at district level | Area-weighted zonal mean of LST per unit | SUHI is a *surface* phenomenon; areal units define the phenomenon; consistent with satellite pixel support |
| Municipal canopy targets and i-Tree assessments | Area-weighted % canopy per city/ward/parcel | Provision metric aligned with land-management accounting |
| Epidemiological exposure (individual or small-area) | Buffer-based canopy/greenery around residences; population/address-weighted | Exposure should reflect where people live/spend time; buffer radius is hypothesis-driven (*Lancet Planetary Health* 9(11), 2025 guidance; Zhang & Tan 2019) |
| Equity / environmental-justice audits | Population-weighted canopy and canopy-weighted Gini | Distributional fairness is about people, not hectares (Martinez, Argota Sánchez-Vaquerizo & Mahajan 2026, *EPJ Data Science* 15:25, "Not your mean green"; Ibebuchi & Abu 2026, *World* 7(1):6; Chen et al. 2022) |

### 5.2 Measured differences between the aggregation families

- **England-wide (Garrett et al. 2025, IJHG 24:37):** replacing LSOA area-% cover with 300 m postcode-buffer % cover weighted by domestic delivery addresses raised built-up exposure by **8–10%** and generally *lowered* non-built-up (incl. woodland) exposure; differences varied by region, urban/rural status, cover type, and LSOA size class. Interpretation: area-level averages "tend to overestimate non-built-up land covers overall" relative to people's actual surroundings.
- **Baltimore (Ibebuchi & Abu 2026, *World* 7(1):6):** population-weighted canopy fell from 47–51% (least-deprived decile) to 13–15% (most-deprived) — a **3.4–4.1× disparity**; area-level canopy–deprivation correlation ρ ≈ −0.51.
- **Global cities (Chen et al. 2022, *Nature Communications* 13:4636):** greenspace exposure Gini for Global South cities (0.47) ≈ 2× Global North (0.24); only ~22% of the spatial disparity in exposure associated with greenspace provision (21.93% of variance), 53.42% jointly with provision × configuration — i.e., **where greenery sits relative to people matters more than how much there is**.
- **US/global SUHI trends (Huang et al. 2025, *Sci Rep* 15:13860):** a decrease of 10,000 persons/km²/decade in population-weighted density is associated with a population-weighted SUHI-extreme trend ≈0.5 K/decade slower than the area-average trend — area averages overstate heat-exposure trends in sprawling cities and understate them under densification.
- **Helsinki (Laatikainen, Hasanzadeh & Kyttä 2018, *Int J Health Geogr* 17:29):** compares individualized/activity-space exposure models with residence-based buffers and administrative units for environmental health research in the Helsinki region and shows exposure estimates and associations differ by model choice. **UNVERIFIED detail:** the draft's specific claim that green space–wellbeing associations "were significant only with individualized residential exposure models; administrative-unit and 500 m buffer versions gave different (null) results" could not be confirmed from the paper text checked; rephrase to what is documented (methodological comparison of activity-space vs. residence-based exposure models).
- **Singapore (Zhang & Tan 2019, IJERPH 16(4):578):** canopy vs. vegetation vs. park-area metrics and buffer type (circular/nested/network) and radius (50–2800 m) all changed which associations were significant; strongest canopy–mental-health associations at medium scales (~400–1600 m).
- **Toronto (Graham et al. 2016, *Urban For. Urban Green.* 20:91–99):** census tracts with <5% canopy had ~5× heat-related ambulance calls vs. >5% cover, and the study suggests raising low-canopy tracts above 5% could reduce calls by ~80% — an example of the *district-share* metric being used as an exposure proxy in a health analysis (and the implied policy conclusion illustrates the risk of over-interpreting an ecological association). **UNVERIFIED detail:** the draft's additional "~15× vs. >70%" comparison could not be independently confirmed from the sources checked.

---

## 6. Misinterpretations when one metric is presented as the other

### 6.1 The supply-vs-exposure ecological fallacy (most common error)
- Stated explicitly by Chen et al. 2022: aggregated provision/supply metrics "produce an ecological fallacy — biased inferences of individual patterns from aggregated data" when equated to exposure. Classic ecological-bias theory: within-unit exposure heterogeneity is unidentifiable from area means (Wakefield, "Spatial Aggregation and the Ecological Fallacy", Ch. 30 of the *Handbook of Spatial Epidemiology*, PMC4209486; Morgenstern 2008, *Annu Rev Public Health* 29:37–52, "Ecologic Studies Revisited").
- Concretely: a district with a large park has high area-% canopy but residents may live in low-canopy blocks; the district value overstates resident canopy. Boston "Urban Heat Islets" (O'Brien, Gridley, Trlica, Wang & Shrivastava 2020, AJPH 110(7):994–1001) showed **38% of LST variation between streets within census tracts** and **no independent effect of tract-average LST** on heat-advisory emergencies — direct evidence that tract-level area means mask the within-tract variation that matters for health.

### 6.2 Park and forest inflation of district canopy
- District % canopy counts parks, forests, riparian corridors, and institutional green land that are far from residences; the building-weighted buffer down-weights them. Two nuances cut both ways:
  - Park cool-island *air-temperature* effects are small for most parks (Grace et al. 2025, *Land* 14(8):1686: surface temperatures 10–15 °C lower in parks but air temperatures essentially unchanged at street level except for the largest park), so counting park canopy in a district "cooling" metric overstates the mitigation residents experience.
  - Conversely, tree clusters can have *non-local* effects — nearby unshaded zones may even heat up (wind blocking, humidity) (**UNVERIFIED**: the "ICUC12 microclimate study" and the "Boston CEE 2025, 10.1038/s43247-025-02462-3" citations in this sentence have no verifiable entries in the research files; they were kept as flagged items, not silently dropped).
- Scale dependence adds another layer: canopy–temperature relationships saturate and interact with impervious surfaces (Ziter et al. 2019), so a single district % hides the configurational information.

### 6.3 Metric non-interchangeability in heat–health analyses
- Hong Kong (Song et al. 2023, EHP 131(9):097007): NDVI vs. % greenspace vs. eye-level street greenery gave different effect modifications of heat–mortality (e.g., RR low-vs-high greenery at 99th pct: NDVI 1.096 vs 0.985, p=0.019; % greenspace 1.068 vs 0.990, p=0.13; eye-level 1.103 vs 0.943, p=0.019).
- Paris (Aboudrar-Méda & Falchetta 2026, *Environ. Res.: Infrastruct. Sustain.* 6(2):021001): GVI, NDVI, and planimetry-based vegetation produced consistently ordered but quantitatively different attenuation estimates (18.5% vs 16% vs 14% for mean daily WBGT), and the authors state metric and weighting choices "can materially alter estimated health burdens and, in some cases, even reverse their sign."
- Hong Kong (Song et al. 2024, *Environment International* 191:108950): area-level and distance-based (population-weighted) greenspace exposures "showed a marked difference" in heat-mortality effect modification under extreme heat for total greenspace and forest land (p < 0.05); optimal buffer ≈1 km (ratio of RRs 1.424 NDVI, 1.227 forest).

### 6.4 Context/geometry errors in the other direction
- Building-weighted buffers can *under*-count district parks that genuinely cool neighborhoods beyond the buffer radius (**UNVERIFIED**: the "2SFCA cooling-equity studies" cited here have no verifiable entries in the research files; flagged, not dropped), and can mis-rank districts when building footprints misrepresent residential population (offices/warehouses with large footprints but no residents). Address/delivery-point weighting (Garrett et al. 2025) and gridded population (Chen et al. 2022; Zhong, Zhao, Ren, Teng & Zhang 2024, *Building Simulation* 17(11):1933–1949) are the recommended fixes.
- Edge effects: administrative-boundary averaging ignores canopy just across the boundary; buffers handle this but introduce radius choice (UGCoP; Kwan 2012, *Ann Assoc Am Geogr* 102(5):958–968; *Lancet Planetary Health* 9(11), 2025 guidance; Mears et al. 2020).
- Mobility: residence-based exposure (whether area- or building-weighted) is itself an approximation; the neighborhood effect averaging problem (NEAP; Kwan 2018, IJERPH 15(9):1841) and mobility-based greenspace studies (Liu, Kwan, Song, Yu & Cui 2025, *Soc Sci Med* 379:118190; UGCoP greenspace, Liu, Kwan & Yu 2023, *Urban Forestry & Urban Greening* 85:127972, DOI 10.1016/j.ufug.2023.127972) show daily mobility attenuates residence-based exposure gradients — relevant when district-level canopy is used as a proxy for personal heat exposure.

### 6.5 What practitioners should report
- Name the metric: "area-weighted canopy share of the district" vs "building/population-weighted mean canopy in a r m buffer" are not the same number and should never be labeled interchangeably.
- Report both when possible, plus the buffer radius and weighting basis; run multi-scale sensitivity (Zhang & Tan 2019; *Lancet Planetary Health* 9(11), 2025; MAUP papers).
- For heat-exposure claims, prefer population-weighted exposure (or building-weighted as an acknowledged proxy) and state the assumption that footprint ≈ residents.

---

## 7. Consensus, disagreements, gaps

**Consensus:**
- Provision metrics (area-weighted %) and exposure metrics (weighted buffer means) are conceptually distinct and empirically divergent (Chen et al. 2022; Garrett et al. 2025; Martinez et al. 2026, EPJ Data Science; Huang et al. 2025, Sci Rep).
- Canopy (trees) is a stronger heat-health-relevant green metric than total vegetation or grass at most scales (Zhang & Tan 2019; Reid, Clougherty, Shmool & Kubzansky 2017, IJERPH 14(11):1411).
- Scale/buffer choice changes results; no single universal radius (Zhang & Tan 2019; *Lancet Planetary Health* 9(11), 2025; Browning & Lee 2017, IJERPH 14(7):675).
- HVI predictive validity is weak and sensitive to unit choice and indicator selection (Niu et al. 2021; Tate 2012-type uncertainty literature).

**Disagreements / open tensions:**
- Whether tract-level area means are "good enough" for health studies: Boston islets says no (within-tract heterogeneity matters); many national HVI/heat-mortality studies continue to use tract/zip means (e.g., Murage et al. 2020 London; Graham et al. 2016 Toronto) with significant results — the disagreement is about bias direction, not existence.
- Direction of bias between AWD and BWB is **configuration-dependent**, not fixed: Garrett et al. 2025 found woodland exposure could be higher under the address-weighted method in some regions and lower in others, and differences varied by LSOA size class. Any claim like "district canopy always overstates residential canopy" is an overstatement; it holds where canopy concentrates in non-residential land, which is the common urban case (parks, forests, industrial zones) but not universal.
- Whether building footprint area is an acceptable population proxy vs. requiring address counts/gridded population (Garrett et al. 2025 discusses both; the answer depends on data availability and the mix of building uses).

**Gaps:**
- Few studies report both AWD and BWB for the *same* district in the *same* heat analysis; direct head-to-head quantification of the two metrics in a heat-exposure or HVI setting is scarce (most comparisons come from greenspace-health and equity literatures).
- No standard nomenclature: "canopy cover", "tree cover", "greenness", "greenspace" are used inconsistently (Lee, Chamberlain & Park 2025, *Land* 14(3):517, construct-based UGS review).
- HVI reviews find vegetation inclusion inconsistent and rarely validated against measured heat exposure (Niu et al. 2021).

---

## 8. Open questions and recommended next steps

1. **Head-to-head measurement (suggested experiment):** for a sample of districts, compute (a) area-weighted canopy share, (b) building-weighted mean canopy in 300 m and 1 km buffers, (c) population-weighted canopy (gridded population or address counts), and quantify rank changes, correlations (expected Kendall τ ≈ 0.56–0.89 per Garrett et al. 2025), and divergence in the tails. Report a table like the one below. This is cheap with OSM building footprints + a canopy raster, and would give the field a citable, quantitative answer to "how different are the two metrics in practice."
2. **Re-run a published HVI** (e.g., Reid-style) with the vegetation factor computed as AWD vs. population-weighted buffer mean and compare index rankings and validation performance.
3. **Adopt dual reporting** in HVI/UHI papers: provision metric for the land surface, exposure metric for people; state weighting and radius.
4. Review whether municipal canopy targets (e.g., "30% canopy by 20XX") should be tracked as *residential-proximity* canopy rather than district share, following the 3-30-300 measurement literature (Browning et al. 2024, *Sci Total Environ* 907:167739).

---

## 9. Sources (URLs verified 2026-08-06; status and resolved metadata annotated)

Legend: **[OK]** = URL loads and content matches the cited claim/metadata. **[OK-M]** = URL/metadata confirmed; specific numeric detail flagged in body is UNVERIFIED. **[BLOCKED]** = page blocked to fetch (metadata confirmed via CrossRef/journal records). **[DEAD]** = does not load. **UNVERIFIED** = could not be confirmed.

**HVI reviews & constructions**
- Niu, Y.; Li, Z.; Gao, Y.; Liu, X.; Xu, L.; Vardoulakis, S.; Yue, Y.; Wang, J.; Liu, Q. (2021) "A Systematic Review of the Development and Validation of the Heat Vulnerability Index: Major Factors, Methods, and Spatial Units", *Current Climate Change Reports* 7(3):87–97, DOI 10.1007/s40641-021-00173-3 — https://pmc.ncbi.nlm.nih.gov/articles/PMC8531084/ **[OK]**
- Reid et al. 2009, "Mapping community determinants of heat vulnerability", *Environ Health Perspect* 117(11):1730–1736 — https://pmc.ncbi.nlm.nih.gov/articles/PMC2801183/ **[OK]**
- Reid et al. 2012, "Evaluation of a Heat Vulnerability Index on Abnormally Hot Days", EHP 120(5):715–720 — https://pmc.ncbi.nlm.nih.gov/articles/PMC3346770/ **[OK]**
- Wolf & McGregor 2013, "The development of a heat wave vulnerability index for London, United Kingdom", *Weather and Climate Extremes* 1:59–68 (DOI 10.1016/j.wace.2013.07.004) — https://durham-repository.worktribe.com/output/1467115/ **[OK-M]** (repository landing page loads; metadata cross-checked via the Niu 2021 and Bao 2015 reference lists)
- Bao, J.; Li, X.; Yu, C. (2015) "The Construction and Validation of the Heat Vulnerability Index, a Review", IJERPH 12(7):7220–7234 — https://www.mdpi.com/1660-4601/12/7/7220 **[OK]** (⚠ resolved: first author Junzhe Bao)
- "Understanding Urban Heat Vulnerability Assessment Methods: A PRISMA Review", *Energies* 15(19):6998 — https://www.mdpi.com/1996-1073/15/19/6998 **[OK]**
- NYC DOHMH Heat Vulnerability Index (green space component) — https://a816-dohbesp.nyc.gov/IndicatorPublic/data-features/hvi/ **[OK-M]** (page loads; "median neighborhood green space ≈ 25%" figure **UNVERIFIED**)
- DC Heat Exposure Index methodology (Cadmus), tract-level canopy averages — https://doee.dc.gov/sites/default/files/dc/sites/ddoe/service_content/attachments/Methodology%20Report_Update%2005.11.22web_0.pdf **[OK]**
- NSW "Heat vulnerability and urban tree canopy cover levels for Greater Sydney" — https://www.planning.nsw.gov.au/sites/default/files/2025-08/heat-vulnerability-urban-tree-canopy-cover-levels-greater-sydney-councils-goc.pdf **[OK]**
- National US HVI at tract level (PCA; redlining) — https://pmc.ncbi.nlm.nih.gov/articles/PMC9744626/ **[OK-M]** (article "Residential and Race/Ethnicity Disparities in Heat Vulnerability in the United States" loads; the draft's "55,267 tracts" figure **UNVERIFIED**)

**UHI aggregation & MAUP**
- US Surface Urban Heat Island database (Chakraborty, Hsu, Sheriff & Manya; tract zonal means) — https://data.mendeley.com/datasets/x9mv4krnm2/3 **[OK]**
- Hsu, A.; Sheriff, G.; Chakraborty, T.; Manya, D. (2021) "Disproportionate exposure to urban heat island intensity across major US cities", *Nature Communications* 12:2721 — https://pmc.ncbi.nlm.nih.gov/articles/PMC8149665/ **[OK]** (⚠ resolved: authors, journal, volume confirmed)
- Benz, S.A.; Burney, J.A. (2021) "Widespread Race and Class Disparities in Surface Urban Heat Extremes Across the United States", *Earth's Future* 9(7):e2021EF002016 — https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2021EF002016 **[OK]**
- Johnson, D.P. (2022) "Population-Based Disparities in U.S. Urban Heat Exposure from 2003 to 2018", IJERPH 19(19):12314 — https://www.mdpi.com/1660-4601/19/19/12314 **[OK]**
- Liu, S.; Smith-Greenaway, E. (2024) "Racial and ethnic minorities disproportionately exposed to extreme daily temperature variation in the United States", *PNAS Nexus* 3(5):pgae176 — https://doi.org/10.1093/pnasnexus/pgae176 **[OK]** (year corrected from 2023 to 2024; population-weighted tract-level exposure confirmed)
- Deng, H.; Liu, K.; Feng, J.; Xiong, Y. (2024) "Tackling the modifiable areal unit problem: enhancing urban sustainability through improved land surface temperature and its influencing factors analysis", *Sustainable Cities and Society* 114:105747 — https://www.sciencedirect.com/science/article/abs/pii/S2210670724005729 **[BLOCKED]** (ScienceDirect bot wall; metadata confirmed via CrossRef/journal records; correct DOI is 10.1016/j.scs.2024.105747; "87 cities, 12 scales" detail UNVERIFIED)
- Zhang, H.; Zhang, J.; Yang, X.; Wang, H.; Qi, R.; Xu, J.; Tian, Y.; Guo, Y.; Bai, H. (2026) "Research on thermal comfort exposure inequality and its influencing factors based on the modifiable areal unit problem: a case study of Zhengzhou", *Landscape Ecology* 41(5):77 — https://link.springer.com/article/10.1007/s10980-026-02339-6 **[OK]** (⚠ resolved; 3×3 km optimal unit and green-space ratio q = 0.641 confirmed)
- Ziter, C.D.; Pedersen, E.J.; Kucharik, C.J.; Turner, M.G. (2019) "Scale-dependent interactions between tree canopy cover and impervious surfaces reduce daytime urban heat during summer", PNAS 116(15):7575–7580 — https://pmc.ncbi.nlm.nih.gov/articles/PMC6462107/ **[OK]**
- Ralls, C.; Polyakov, A.Y.; Shandas, V. (2024) "Scale-Dependent Effects of Urban Canopy Cover, Canopy Volume, and Impervious Surfaces on Near-Surface Air Temperature in a Mid-Sized City", *Land* 13(11):1741 — https://www.mdpi.com/2073-445X/13/11/1741 **[OK]** (⚠ resolved: authors/year; 10–90 m radii confirmed)
- Grace, B.; Bolleter, J.; Barghchi, M.; Lund, J. (2025) "Unpacking Park Cool Island Effects Using Remote-Sensed, Measured and Modelled Microclimatic Data", *Land* 14(8):1686 — https://www.mdpi.com/2073-445X/14/8/1686 **[OK]** (⚠ resolved: authors/year 2025; surface 10–15 °C lower / air essentially unchanged claims confirmed)
- Esri zonal-statistics tutorial (block-group UHI factors) — https://learn.arcgis.com/en/projects/map-and-analyze-the-urban-heat-island-effect/ **[OK]** ; GDAL raster zonal-stats — https://gdal.org/en/latest/programs/gdal_raster_zonal_stats.html **[OK]**
- Wang, X.; Zhang, Y.; Yu, D. (2023) "Exploring the Relationships between Land Surface Temperature and Its Influencing Factors Using Multisource Spatial Big Data: A Case Study in Beijing, China", *Remote Sensing* 15(7):1783 — https://www.mdpi.com/2072-4292/15/7/1783 **[OK]** (Beijing subdistrict/pixel-scale LST confirmed)

**Population-weighted exposure & equity**
- Chen, B.; Wu, S.; Song, Y.; Webster, C.; Xu, B.; Gong, P. (2022) "Contrasting inequality in human exposure to greenspace between cities of Global North and Global South", *Nature Communications* 13:4636 — https://www.nature.com/articles/s41467-022-32258-4 **[OK]** (⚠ resolved: authors/volume/article; Gini 0.47 vs **0.24**; 21.93% provision)
- Wu, S.; Chen, B.; Webster, C.; Xu, B.; Gong, P. (2023) "Improved human greenspace exposure equality during 21st century urbanization", *Nature Communications* 14:6460 — https://www.nature.com/articles/s41467-023-41620-z **[OK]**
- Li, Y.; Svenning, J.-C.; Zhou, W.; et al. (2024) "Green spaces provide substantial but unequal urban cooling globally", *Nature Communications* 15:7108 — https://www.nature.com/articles/s41467-024-51355-0 **[OK]**
- Massaro, E.; Schifanella, R.; Piccardo, M.; Caporaso, L.; Taubenböck, H.; Cescatti, A.; Duveiller, G. (2023) "Spatially-optimized urban greening for reduction of population exposure to land surface temperature extremes", *Nature Communications* 14:2903 — https://www.nature.com/articles/s41467-023-38596-1 **[OK]**
- Huang, K.; Stone, B. Jr.; Guan, C.; Liang, J. (2025) "Declining urban density attenuates rising population exposure to surface heat extremes", *Scientific Reports* 15:13860 — https://www.nature.com/articles/s41598-025-96045-z **[OK]** (⚠ resolved: authors; note the coefficient is 0.5 K/decade per 10,000 persons/km²/decade)
- Martinez, J.; Argota Sánchez-Vaquerizo, J.; Mahajan, S. (2026) "Not your mean green: beyond averages in mapping socio-spatial inequities in urban greenery for smart cities", *EPJ Data Science* 15:25 — https://link.springer.com/article/10.1140/epjds/s13688-026-00627-4 **[OK]** (⚠ resolved: authors/year 2026; Bogotá/Medellín population-weighted canopy and Gini/CCI)
- Ibebuchi, C.C.; Abu, I.-O. (2026) "Threefold Environmental Inequality: Canopy Cover, Deprivation, and Cancer-Risk Burdens Across Baltimore Neighborhoods", *World* 7(1):6 — https://www.mdpi.com/2673-4060/7/1/6 **[OK]** (⚠ resolved: journal is **World** (ISSN 2673-4060), not *Urban Science*; authors/year; 47–51%→13–15%, 3.4–4.1×, ρ≈−0.51 confirmed)
- "Measuring Urban Greenspace Distribution Equity: The Importance of Appropriate Methodological Approaches", IJGI 8(6):286 — https://www.mdpi.com/2220-9964/8/6/286 **[OK]**
- "Multi-Scale Analysis of Urban Greenspace Exposure and Equality: population-enhanced EVI-weighted model", *Land* 14(1):132 — https://www.mdpi.com/2073-445X/14/1/132 **[OK]**
- Zhong, X.; Zhao, L.; Ren, P.; Teng, Y.; Zhang, X. (2024) "Inequalities in urban thermal and greenspace exposures: a case study for China's Greater Bay Area from 2010 to 2020", *Building Simulation* 17(11):1933–1949 — https://www.sciopen.com/article/10.1007/s12273-024-1180-z **[OK]** (⚠ resolved: journal *Building Simulation*; authors/year/volume/pages confirmed)
- McDonald, R.I.; Biswas, T.; Sachar, C.; Housman, I.; Boucher, T.M.; Balk, D.; Nowak, D.; Spotswood, E.; Stanley, C.K.; Leyk, S. (2021) "The tree cover and temperature disparity in US urbanized areas: Quantifying the association with income across 5723 communities", PLoS ONE 16(4):e0249715 — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249715 **[OK]**
- McDonald, R.I.; Biswas, T.; Chakraborty, T.C.; Kroeger, T.; Cook-Patton, S.C.; Fargione, J.E. (2024) "Current inequality and future potential of US urban tree cover for reducing heat-related health impacts", *npj Urban Sustainability* 4:18 — https://www.nature.com/articles/s42949-024-00150-3 **[OK]**
- Schwarz, K.; Fragkias, M.; Boone, C.G.; Zhou, W.; McHale, M.; Grove, J.M.; O'Neil-Dunne, J.; McFadden, J.P.; Buckley, G.L.; Childers, D.; et al. (2015) "Trees grow on money: Urban tree canopy cover and environmental justice", PLoS ONE 10(4):e0122051 — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0122051 **[OK]**

**Greenspace measurement methods (buffer vs. area; scale)**
- Zhang, L.; Tan, P.Y. (2019) "Associations between Urban Green Spaces and Health are Dependent on the Analytical Scale and How Urban Green Spaces are Measured", IJERPH 16(4):578 — https://pmc.ncbi.nlm.nih.gov/articles/PMC6406785/ **[OK]** (⚠ resolved: this is the Singapore n=1000 study, authored by **Liqing Zhang and Puay Yok Tan, 2019** — NOT "Labib et al. 2020")
- Garrett, J.K.; Elliott, L.R.; Lovell, R.; Wheeler, B.W.; Marshall, T.; Kibowski, F.; Phillips, B.B.; Gaston, K.J. (2025) "A novel approach for mapping exposure to land cover at the small statistical geography level", *Int J Health Geogr* 24:37 — https://link.springer.com/article/10.1186/s12942-025-00425-7 **[OK]** (8–10% built-up; Kendall τ 0.56–0.89; "tend to overestimate non-built-up land covers overall")
- Laatikainen, T.E.; Hasanzadeh, K.; Kyttä, M. (2018) "Capturing exposure in environmental health research: challenges and opportunities of different activity space models", *Int J Health Geogr* 17:29 — https://ij-healthgeographics.biomedcentral.com/counter/pdf/10.1186/s12942-018-0149-5.pdf **[OK-M]** (⚠ resolved: authors; specific "green space–wellbeing significant only with individualized models" result **UNVERIFIED**)
- "Methodological guidance for selecting buffers in greenspace–health studies", *The Lancet Planetary Health* 9(11) (November 2025), PII S2542519625002487 — https://epub.ub.uni-muenchen.de/131805/1/PIIS2542519625002487.pdf **[OK-M]** (journal/issue/year confirmed via Lancet issue page and repository records; PDF text not extractable — full author list **UNVERIFIED**)
- Mitchell, R.; Astell-Burt, T.; Richardson, E.A. (2011) "A comparison of green space indicators for epidemiological research", *J Epidemiol Community Health* 65(10):853–858 — https://jech.bmj.com/content/65/10/853 **[OK]** (DOI 10.1136/jech.2010.119172)
- de la Iglesia Martinez, A.; Labib, S.M. (2023) "Demystifying normalized difference vegetation index (NDVI) for greenness exposure assessments and policy interventions in urban greening", *Environmental Research* (PII S0013935122024823; DOI 10.1016/j.envres.2022.115155) — https://www.sciencedirect.com/science/article/pii/S0013935122024823 **[BLOCKED]** (ScienceDirect bot wall; metadata confirmed via repository/CrossRef records)
- Lee, D.H.; Chamberlain, B.; Park, H.Y. (2025) "Toward a Construct-Based Definition of Urban Green Space: A Literature Review of the Spatial Dimensions of Measurement, Methods, and Exposure", *Land* 14(3):517 — https://www.mdpi.com/2073-445X/14/3/517 **[OK]** (⚠ resolved: authors/year 2025)
- Liu, D.; Lu, Y.; Biljecki, F. (2025) "A methodological review of the assessment of urban greenery exposure", *Urban Forestry & Urban Greening* — https://ual.sg/publication/2025-ufug-greenery-exposure/2025-ufug-greenery-exposure.pdf **[OK]**
- Kwan, M.-P. (2018) "The Neighborhood Effect Averaging Problem (NEAP): An Elusive Confounder of the Neighborhood Effect", IJERPH 15(9):1841 — https://www.mdpi.com/1660-4601/15/9/1841 **[OK]**
- Liu, Y.; Kwan, M.-P.; Yu, C. (2023) "The uncertain geographic context problem (UGCoP) in measuring people's exposure to green space using the integrated 3S approach", *Urban Forestry & Urban Greening* 85:127972, DOI 10.1016/j.ufug.2023.127972 — https://www.sciencedirect.com/science/article/pii/S1618866723001437 **[OK]** (⚠ resolved: authors; correct DOI is 10.1016/j.ufug.2023.127972 — the DOI 10.1016/j.ufug.2023.127933 previously cited inline belongs to a different article)
- Liu, Y.; Kwan, M.-P.; Song, L.; Yu, C.; Cui, Y. (2025) "How mobility-based exposure measures may mitigate the underestimation of the association between green space exposures and health", *Social Science & Medicine* 379:118190 — https://www.sciencedirect.com/science/article/pii/S0277953625005209 **[OK-M]** (metadata confirmed via CrossRef; full text ScienceDirect-blocked)
- i-Tree Canopy (area-% method) — https://canopy.itreetools.org/ **[OK]** ; UK ward canopy guide — https://cdn.forestresearch.gov.uk/2018/11/canopy_cover_webmap_user_guide_-_updated_march_2021.pdf **[OK]**

**Heat–canopy/greenspace health**
- Graham, D.A.; Vanos, J.K.; Kenny, N.A.; et al. (2016) "The relationship between neighbourhood tree canopy cover and heat-related ambulance calls during extreme heat events in Toronto, Canada", *Urban For. Urban Green.* 20:91–99 (DOI 10.1016/j.ufug.2016.08.005) — https://escholarship.org/content/qt53v4h0ph/qt53v4h0ph.pdf **[OK-M]** (URL loads; <5% vs >5% ≈5× and ~80% reduction claims confirmed via the abstract and secondary summaries; "~15× vs >70%" **UNVERIFIED**)
- Song, J.; Gasparrini, A.; et al. (2023) "Effect Modifications of Overhead-View and Eye-Level Urban Greenery on Heat–Mortality Associations", *Environ Health Perspect* 131(9):097007 (DOI 10.1289/EHP12589) — https://pmc.ncbi.nlm.nih.gov/articles/PMC10510815/ **[OK]** (all RR values confirmed)
- Song, J.; et al. (2024) "Do greenspaces really reduce heat health impacts? Evidence for different vegetation types and distance-based greenspace exposure", *Environment International* 191:108950 — https://researchonline.lshtm.ac.uk/id/eprint/4673664/1/Song-etal-2024-Do-greenspaces-really-reduce-heat-health-impacts.pdf **[OK]** (verified against the full text; local copy saved at /home/mainuser/Downloads/do-greenspaces-really-reduce-heat-health-impacts-evidence-for-different-vegetation-types-and-distanc.md)
- Aboudrar-Méda, A.; Falchetta, G. (2026) "Urban green space metric choice and weighting matter for assessing cooling benefits for human health", *Environmental Research: Infrastructure and Sustainability* 6(2):021001 — https://iopscience.iop.org/article/10.1088/2634-4505/ae75a1 **[OK]** (⚠ resolved: journal is *Environ. Res.: Infrastruct. Sustain.*, not *Environ. Res.: Health*; 18.5% / 16% / 14% WBGT confirmed)
- O'Brien, D.T.; Gridley, B.; Trlica, A.; Wang, J.A.; Shrivastava, A. (2020) "Urban Heat Islets: Street Segments, Land Surface Temperatures, and Medical Emergencies During Heat Advisories", *Am J Public Health* 110(7):994–1001 — https://pmc.ncbi.nlm.nih.gov/articles/PMC7287541/ **[OK]** (⚠ resolved: authors/journal/year; 38% within-tract variance and no tract-average LST effect confirmed)
- Murage, P.; Kovats, S.; Sarran, C.; Taylor, J.; McInnes, R.; Hajat, S. (2020) "What individual and neighbourhood-level factors increase the risk of heat-related mortality? … London", *Environment International* 134:105292 — https://pmc.ncbi.nlm.nih.gov/articles/PMC7103759/ **[OK]**
- "Health impact of urban green spaces: a systematic review of heat-related morbidity and mortality", *BMJ Open* 14(9):e081632 — https://bmjopen.bmj.com/content/14/9/e081632 **[OK]**
- "Greenspace modifies the associations between heat and mortality: A systematic review and meta-analysis of observational studies" (2025, preprint, ecoevorxiv) — https://ecoevorxiv.org/repository/view/8204/ **[OK]**
- Chuang, W.-C.; Gober, P. (2015) "Predicting Hospitalization for Heat-Related Illness at the Census-Tract Level: Phoenix", EHP 123(6):606–612 — https://pmc.ncbi.nlm.nih.gov/articles/PMC4455581/ **[OK]**
- Choi, H.M.; et al. (2022) "Effect modification of greenness on the association between heat and mortality: a multi-city multi-country study", *eBioMedicine* 84:104251 — https://pubmed.ncbi.nlm.nih.gov/36088684/ **[OK]**
- Zamponi, V.M.; et al. (2023) "Understanding and Assessing Demographic (In)Equity Resulting From Extreme Heat Exposure Due to Lack of Tree Canopies in Norfolk, VA Using Agent-Based Modeling", *Ecological Modelling* 483:110445 — https://digitalcommons.odu.edu/cgi/viewcontent.cgi?article=1086&context=vmasc_pubs **[OK-M]** (URL resolves; PDF content not extractable this session — metadata per draft)

**Ecological fallacy / aggregation theory**
- Wakefield, J. "Spatial Aggregation and the Ecological Fallacy", Ch. 30, *Handbook of Spatial Epidemiology* — https://pmc.ncbi.nlm.nih.gov/articles/PMC4209486/ **[OK]**
- Morgenstern, H. (2008) "Ecologic Studies Revisited", *Annu Rev Public Health* 29:37–52 — https://www.annualreviews.org/content/journals/10.1146/annurev.publhealth.29.020907.090821 **[OK]**

**Supplementary references added during verification** (traceable in the body):
- Mears, M.; Brindley, P.; Jorgensen, A.; Maheswaran, R. (2020) "Population-level linkages between urban greenspace and health inequality: the case for using multiple indicators of neighbourhood greenspace", *Health & Place* 62:102284 (the 100 m buffer-per-residence description is documented in Garrett et al. 2025)
- Browning, M.; Lee, K. (2017) "Within What Distance Does 'Greenness' Best Predict Physical Health? A Systematic Review of Articles with GIS Buffer Analyses across the Lifespan", IJERPH 14(7):675
- Browning, M.H.E.M.; Locke, D.H.; Konijnendijk, C.; Labib, S.M.; Rigolon, A.; Yeager, R.; et al. (2024) "Measuring the 3-30-300 rule to help cities meet nature access thresholds", *Sci Total Environ* 907:167739
- Reid, C.E.; Clougherty, J.E.; Shmool, J.L.; Kubzansky, L.D. (2017) "Is All Urban Green Space the Same? A Comparison of the Health Benefits of Trees and Grass in New York City", IJERPH 14(11):1411
- Kwan, M.-P. (2012) "The Uncertain Geographic Context Problem", *Ann Assoc Am Geogr* 102(5):958–968

**Blocked (tool-level):** alphaXiv API (tool `alpha_search` and CLI `alpha search`) returned "fetch failed" for all queries on 2026-08-06 — no alphaXiv-sourced papers in this review; provenance notes this gap.

---

## Appendix. Verification of sources and metadata (summary)

All checks performed 2026-08-06 (fetch_content / CrossRef / journal records). Detailed per-URL status is in the companion report `neighborhood-tree-canopy-heat-aggregation-verification.md`. Highlights:

- **Dead links found: 0.** All URLs in the Sources section resolved to a live page or PDF.
- **SUSPECT resolved:** Baltimore study is *World* 7(1):6 (not *Urban Science*); Singapore study is Zhang & Tan 2019 (not Labib); Paris study is *Environ. Res.: Infrastruct. Sustain.* (not *Environ. Res.: Health*); UGCoP paper DOI corrected to 10.1016/j.ufug.2023.127972; PNAS Nexus year corrected to 2024; Sci Rep coefficient corrected to per-10,000 persons/km²/decade; Chen et al. Gini corrected to 0.24 and article number to 4636.
- **BLOCKED (metadata confirmed via CrossRef):** ScienceDirect pages for Deng et al. 2024 (SCS), de la Iglesia Martinez & Labib 2023 (Environ. Res.), Liu, Kwan, Song, Yu & Cui 2025 (Soc Sci Med).
- **UNVERIFIED (kept and flagged, not silently dropped):** NYC HVI "median neighborhood green space ≈ 25%"; National-HVI "55,267 tracts"; Deng et al. "87 cities, 12 scales"; Graham et al. "~15× vs >70%"; Laatikainen et al. specific significance claim; Lancet Planetary Health 2025 full author list; "ICUC12 microclimate study" and "Boston CEE 2025" (10.1038/s43247-025-02462-3) and "2SFCA cooling-equity studies" parenthetical citations (no entries in the research files).
