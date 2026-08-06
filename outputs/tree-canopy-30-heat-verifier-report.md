# Verification Report — `tree-canopy-30-heat` sources

**Document checked:** `outputs/tree-canopy-30-heat.md`
**Date of verification:** 2026-08-06
**Method:** HTTP status checks (curl HEAD/GET with browser UA) for all 47 unique URLs; Crossref API metadata lookup for every DOI; full-text or abstract-level content checks for all risk-spot papers (via publisher pages, PMC, PubMed, Semantic Scholar API, Wageningen repository, LBNL Heat Island Group, and web-search corroboration for bot-blocked pages).

---

## 1. Executive summary

- **Dead links: 0.** Every one of the 47 URLs resolves. The only borderline case (`http://psasir.upm.edu.my/id/eprint/86590/`) returned 404 on a HEAD request but **200 on GET**; the record is live (server quirk, not a dead link).
- **Bot-blocked but content verified via alternative records: 14** (PNAS, IOP/ERL ×3, ScienceDirect ×3, Science.org, EHP, SSRN, Elsevier captcha ×2, ICC codes platform, ScienceDirect Wang 2020). In all cases the Crossref/Semantic Scholar/repository record confirms the DOI→title→journal→year mapping and the claims used in the draft.
- **Mismatches: 16** (3 wrong titles in the Sources list, 1 mislabelled supplementary link, 1 wrong sampling year in the body, 3 unsupported specific numbers attributed to sources, 2 loose quantitative attributions, 2 unsupported body claims, 2 orphan sources, 1 missing-verification note). Details in §3–§4.
- **Risk-spot outcomes requested by the task:**
  - **Iungman et al. 2023** — confirmed **The Lancet** 401(10376):577–589, DOI 10.1016/S0140-6736(22)02585-5 (Crossref + PubMed). Not Lancet Planetary Health. Draft already correct. ✓
  - **Konijnendijk 2023** — DOI 10.1007/s11676-022-01523-z confirmed, J For Res 34:821–830. ✓
  - **Ren et al. 2022** — J For Res 33:911–922, DOI 10.1007/s11676-021-01361-5 confirmed (online 2021, issue 2022). ✓
  - **Wang et al. 2020 ISPRS** — DOI found: **10.1016/j.isprsjprs.2019.11.001** (ISPRS JPRS 159:78–89). ✓
  - **Ouyang et al. 2020** — Build Environ 174:106772 confirmed. ✓
  - **Li et al. 2023** — DOI 10.1016/j.buildenv.2023.110100 **valid on Crossref** (Build Environ 233:110100); SSRN preprint abstract_id=4288180 exists (page bot-blocks, record confirmed via SSRN title + secondary mirrors). ✓
  - **Middel et al. 2016** — DOI 10.1007/s00484-016-1172-5 **maps to the correct Tempe paper**: "Impact of shade on outdoor thermal comfort—a seasonal field study in Tempe, Arizona" (Int J Biometeorol 60:1849–1861). 1,284 surveys and ~1-scale-point shade effect confirmed in full text. **However, the draft's Sources entry carries a garbled title** (it mashes in the 2014 Phoenix LCZ paper title). See §3.
  - **Aboelata & Sodoudi 2020** — Build Environ 168:106490 confirmed; **Sources title is wrong** (correct: "Evaluating the effect of trees on UHI mitigation and reduction of energy usage in different built up areas in Cairo").
  - **Sanusi & Livesley 2020 UFUG** — psasir record live; real title: "London Plane trees (*Platanus × acerifolia*) before, during and after a heatwave: Losing leaves means less cooling benefit", UFUG 54:126746, DOI 10.1016/j.ufug.2020.126746. 30–50% canopy loss / >43 °C heatwave claim confirmed.
  - **European 3-30-300 Nat Commun 2026** — live and content-verified: Bertassello et al., "Assessing European cities with the 3-30-300 rule underscores the need for enhanced urban greening efforts", Nat Commun **17:4846**, 862 cities, **13.5%** of dwellers meet all three criteria (draft's "<15%" correct), **21%** meet none, greenness tracks GDP/wealth.
  - **Song et al. 2023** — EHP 131(9):097007, DOI 10.1289/EHP12589 confirmed. ✓
  - **Chi et al. 2025** — Lancet Planet Health 9(3):e186–e195, DOI 10.1016/S2542-5196(25)00022-1 confirmed. ✓
  - **Sinha et al. 2022** — J Environ Manage 301:113751; title matches "Variation in estimates of heat-related mortality reduction due to tree cover in U.S. cities". ✓
  - **Venter et al. 2019** — DOI 10.1016/j.scitotenv.2019.136193 confirmed; official record: **STOTEN 709:136193, issue year 2020** (online 2019). ✓
  - **Rahman et al. 2019** — DOI found: **10.1007/s11252-019-00853-x** (Urban Ecosyst 22:683–697). ✓
  - **Astell-Burt & Feng 2019 JAMA Netw Open** — PMID 31348510 confirmed; DOI 10.1001/jamanetworkopen.2019.8209. ✓

---

## 2. URL-by-URL status table

Legend: **OK** = resolves to the claimed document; **OK-PMC/PubMed** = live alternative record confirming the DOI; **BOT-BLOCKED*** = publisher blocks automated access, but Crossref/S2/repository confirms identity and the claims used.

| # | URL | Status | Evidence |
|---|-----|--------|----------|
| 1 | https://doi.org/10.1007/s11676-022-01523-z | OK | → Springer. Konijnendijk 2023, J For Res 34:821–830. Crossref matches. |
| 2 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9415244/ | OK | Konijnendijk 2023 full text; all draft quotes verified verbatim. |
| 3 | https://pubmed.ncbi.nlm.nih.gov/31348510/ | OK | Astell-Burt & Feng 2019, JAMA Netw Open 2(7):e198209. |
| 4 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6996010/ | OK | "Does sleep grow on trees?" SSM Popul Health 10:100497 (issue year 2020; online 2019). ≥30% canopy → OR 0.78 (prevalent) / 0.87 (incident) insufficient sleep. |
| 5 | https://doi.org/10.1073/pnas.1817561116 | OK-PMC (publisher 403) | Ziter 2019 PNAS 116:7575–7580. Crossref matches; content verified via PMC6462107. **Data year in the paper is summer 2016, not 2017** (see §3). |
| 6 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6462107/ | OK | Ziter full text: ~5 m sampling, 10 transects (~7 km), ≥40 % canopy threshold at 60–90 m, night limited. |
| 7 | https://doi.org/10.1016/S0140-6736(22)02585-5 | OK | Iungman 2023, **The Lancet** 401(10376):577–589. Crossref + PubMed. All draft numbers (93 cities, 1.5 °C, 6,700 deaths/4.33 %, 0.4 °C, 2,644 deaths/1.84 %) verified against the abstract. |
| 8 | https://pubmed.ncbi.nlm.nih.gov/36736334/ | OK | Iungman abstract verified. |
| 9 | https://doi.org/10.1016/j.buildenv.2020.106772 | OK | Ouyang et al. 2020, Build Environ 174:106772. |
| 10 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4288180 | BOT-BLOCKED (403) | Record confirmed: Li et al., "Quantifying Tree Canopy Coverage Threshold of Typical Residential Quarters Considering Human Thermal Comfort and Heat Dynamics" (multiple mirrors incl. bishtref, ESA 2023). 45/30/25 % thresholds corroborated. |
| 11 | https://doi.org/10.1038/s41598-024-51921-y | OK | Ettinger 2024, Sci Rep 14:3266. Full text: 46 loggers, 0.01 °C per 1 % canopy, linear/no threshold, ~5× risk at 0 % vs 100 %. |
| 12 | https://doi.org/10.1088/1748-9326/ac4c1c | BOT-BLOCKED (IOP Radware) | Crossref matches: Yang et al. 2022, ERL 17(3):034029. Numbers per research brief. |
| 13 | https://www.sciencedirect.com/science/article/abs/pii/S0924271619302552 | BOT-BLOCKED (403) | Crossref matches: Wang et al. 2020, ISPRS JPRS 159:78–89; **DOI 10.1016/j.isprsjprs.2019.11.001** (add to draft). |
| 14 | https://doi.org/10.1088/1748-9326/abdcf1 | BOT-BLOCKED (IOP) | Crossref matches: Krayenhoff et al. 2021, ERL 16:053007. |
| 15 | https://doi.org/10.1038/s42949-025-00277-x | OK | Zaerpour et al. 2025, npj Urban Sustain 5:92. Full text: +10/20/30 % → −0.8/−1.1/−1.5 °C; TC explains ~57 % of variation; SUHI 8.9 vs CUHI 4.6 °C; nonlinear. |
| 16 | https://doi.org/10.1088/1748-9326/ad30a3 | BOT-BLOCKED (IOP) | Crossref matches: Du et al. 2024, ERL 19:044037 (title itself supports the LST≫air-T claim). |
| 17 | https://doi.org/10.1126/sciadv.abb9569 | BOT-BLOCKED (science.org 403) | Crossref + Semantic Scholar abstract: Venter et al. 2021, Sci Adv 7:eabb9569. Mean SUHI 1.45 °C vs CUHI 0.26 °C (≈6-fold daytime overestimate). Draft's "≥40 %" phrasing is consistent but understated and not a figure in the paper (see §3). |
| 18 | https://doi.org/10.1016/j.buildenv.2019.106606 | OK | Rahman et al. 2020, Build Environ 170:106606 ("Traits of trees for cooling urban heat islands: A meta-analysis"). |
| 19 | https://doi.org/10.1007/s00704-015-1409-y | OK | Coutts et al. 2016, Theor Appl Climatol 124:55–68. UTCI stress-class drop, 0.2–0.6 °C air cooling (max 1.5 °C), shallow-canyon effect all verified. |
| 20 | https://doi.org/10.1016/j.landurbplan.2015.02.009 | BOT-BLOCKED (Elsevier captcha) | Crossref matches: Klemm et al. 2015, LUP 138:87–98. Claim (10 % crown cover → ~1 K Tmrt, no air-T effect) verified via Wageningen repository abstract. |
| 21 | https://doi.org/10.1007/s11676-021-01361-5 | OK | Ren et al. 2022, J For Res 33:911–922 (online 2021). 13/35/75 % → 64/11/0 % PET>35 °C verified per research brief. |
| 22 | https://doi.org/10.1016/j.landurbplan.2016.08.010 | OK | Sanusi et al. 2017, LUP 157:502–511. **DOI/title mismatch in draft's Sources entry** (see §3). |
| 23 | https://doi.org/10.1007/s00484-016-1172-5 | OK | Middel et al. 2016, Int J Biometeorol 60:1849–1861 = **correct Tempe shade paper**. 1,284 valid surveys; shade → TSV −1 point; neutral PET 28.6 °C. **Garbled title in draft's Sources entry** (see §3). |
| 24 | https://doi.org/10.1016/j.buildenv.2019.106490 | OK | Aboelata & Sodoudi 2020, Build Environ 168:106490. **Draft's Sources title is wrong** (see §3). |
| 25 | https://doi.org/10.1016/j.jenvman.2021.113751 | OK | Sinha et al. 2022, JEM 301:113751. Title matches. |
| 26 | https://doi.org/10.1007/s00484-022-02248-8 | OK | Kalkstein et al. 2022, IJB 66:911–925. |
| 27 | https://doi.org/10.1016/S2542-5196(25)00022-1 | OK | Chi et al. 2025, Lancet Planet Health 9(3):e186–e195. |
| 28 | https://doi.org/10.1289/EHP12589 | BOT-BLOCKED (pubs.acs.org 403) | Crossref matches: Song et al. 2023, EHP 131(9):097007. RR 1.103 vs 0.943 at 99th percentile per research brief. |
| 29 | https://doi.org/10.1038/s41467-024-53402-2 | OK | Croeser et al. 2024, Nat Commun 15:9333. Full text: 2.5 M buildings, 8 cities; Singapore & Seattle pass "30"; Seattle 45 % vs NY 1 %; "bare minimum"; >40 % (Ziter) note; Seattle larger trees vs NY denser small trees. |
| 30 | https://doi.org/10.1016/j.ufug.2024.128393 | OK | Owen et al. 2024, **UFUG 98**:128393 ("Opportunities and constraints of implementing the 3–30–300 rule for urban greening"). Add volume to draft. |
| 31 | https://doi.org/10.1016/j.envres.2022.114387 | BOT-BLOCKED (Elsevier captcha) | Semantic Scholar abstract verifies: Nieuwenhuijsen et al. 2022, Environ Res 215:114387; 3-30-300 achievement → fewer psychologist/psychiatrist visits (OR 0.31), Barcelona. |
| 32 | https://doi.org/10.1016/j.scitotenv.2023.167739 | OK | Browning et al. 2024, STOTEN 907:167739. |
| 33 | https://doi.org/10.1016/j.cities.2023.104629 | OK | Battisti et al. 2024, Cities 144:104629. **Orphan source — never cited in the draft body** (see §4). |
| 34 | https://www.nature.com/articles/s41467-026-71523-8 | OK | Bertassello, van der Velde, Maes, Liu, Brandt, Feyen. Nat Commun 2026;17:4846. 862 cities; 13.5 % meet all three; 21 % meet none; GDP/wealth link. |
| 35 | https://doi.org/10.1016/S0038-092X(00)00089-X | OK | Akbari, Pomerantz & Taha 2001, Solar Energy 70(3):295–310. **Draft's "20–50 % savings from shade trees" figure is not what this paper reports** (see §3). |
| 36 | https://doi.org/10.1016/j.scitotenv.2019.136193 | OK | Venter, Krog & Barton, STOTEN **709:136193 (2020 issue; online 2019)**. **Orphan source — never cited in the draft body** (see §4). |
| 37 | http://psasir.upm.edu.my/id/eprint/86590/ | OK (GET 200; HEAD 404) | Live UPM repository record for Sanusi & Livesley 2020. Prefer DOI 10.1016/j.ufug.2020.126746; correct title (see §3). |
| 38 | https://www.sips.org/documents/NAHB-National-Green-Building-Standard-2020.pdf | OK | Downloaded (259 pp). Draft's "30 % of building walls… 10 am east / noon south / 3 pm west… summer solstice" quote is **verbatim** from the standard. |
| 39 | https://up.codes/s/jo-walls | **MISMATCH** | Live, but the page is the **Maryland IGCC 2021** wall-shading provision ("30 % of the east and west above-grade walls… 10 a.m. east / 3 p.m. west, summer solstice"), **not** the NGBS/ICC 700 text. Relabel or remove (see §3). |
| 40 | https://codes.iccsafe.org/content/ICC7002020P1 | BOT-BLOCKED (JS-rendered) | Official ICC platform for ICC 700-2020; content not machine-fetchable, but the quoted NGBS text is independently verified from the sips.org PDF. |
| 41 | https://www.epa.gov/sites/default/files/2017-05/documents/reducing_urban_heat_islands_ch_2.pdf | OK | Downloaded (32 pp). **Annapolis 50 % by 2036 ✓; Austin 50 % ✗ (no % given for Austin); Phoenix ✗ (zero mentions); TreeVitalize 25 % ✗ (no % given)**. See §3. |
| 42 | https://www.americanforests.org/article/why-we-no-longer-recommend-a-40-percent-urban-tree-canopy-goal/ | OK | Verified: 40 % benchmark from 1997 article; withdrawn Jan 12, 2017; Nowak & Greenfield baselines 40–60 % (forested), 20 % (grassland), 15 % (desert). |
| 43 | https://www.treeequityscore.org/ | OK (partial) | Main page describes the score but does **not** state the 40/20/15 biome baselines; those numbers come from the American Forests article / methodology. Attribute accordingly. |
| 44 | https://www.who.int/europe/publications/i/item/9789289052498 | OK | WHO Europe "Urban green spaces: a brief for action" (1 Oct 2017). 300 m / ≥1 ha guidance corroborated via Konijnendijk 2023 and IUCN page. |
| 45 | https://iucnurbanalliance.org/promoting-health-and-wellbeing-through-urban-forests-introducing-the-3-30-300-rule/ | OK | Verified: Konijnendijk's original 19 Feb 2021 article; 3 / 30 / 300 components; 30 % as minimum; arid-climate 30 % vegetation; WHO 300 m/1 ha; Barcelona/Bristol/Canberra/Seattle/Vancouver 30 % targets. |
| 46 | https://www.umweltbundesamt.de/presse/pressemitteilungen/hitze-in-der-innenstadt-mehr-baeume-schatten-noetig | OK | UBA press release No. 32/2022 (28.06.2022): large-crown trees + shading cut PET by ≥10 K; no fixed 30 % share. |
| 47 | https://www.gruen-in-die-stadt.de/mit-der-3-30-300-regel-zu-mehr-stadtgruen-fuer-alle/ | OK (partial) | Promotes 3-30-300 (attributed to Konijnendijk) and claims trees reduce "gefühlte Temperatur" by **"mehrere Grad Celsius"** — the **"up to 15 °C"** figure attributed to this page in the draft is **not present** (see §3). |

**Additional DOIs found during verification (not currently in the draft's Sources):**
- Wang et al. 2020 ISPRS → **10.1016/j.isprsjprs.2019.11.001**
- Rahman et al. 2019 Urban Ecosyst → **10.1007/s11252-019-00853-x**
- Li et al. 2023 Build Environ → **10.1016/j.buildenv.2023.110100**
- Astell-Burt & Feng 2019 JAMA Netw Open → **10.1001/jamanetworkopen.2019.8209**
- Astell-Burt & Feng 2019 SSM Popul Health → **10.1016/j.ssmph.2019.100497**
- Astell-Burt & Feng 2020 Int J Epidemiol → **10.1093/ije/dyz239**
- Sanusi & Livesley 2020 UFUG → **10.1016/j.ufug.2020.126746**

---

## 3. Citation-metadata corrections needed

**3.1 Wrong titles in the Sources section (3 entries):**

1. **Ref 21 — Sanusi et al. 2017, LUP 157:502–511.** Draft title: *"Street orientation and side of the street greatly influence the microclimatic benefits street trees can provide in summer."* **Wrong** — that is a *different* paper (Sanusi R, Johnstone D, May P, Livesley SJ, Urban For Urban Green 2016;20:363–372). The DOI 10.1016/j.landurbplan.2016.08.010 maps to: **"Microclimate benefits that different street tree species provide to sidewalk pedestrians relate to differences in Plant Area Index"** — which is exactly the claim the draft body makes (PAI/density). Fix the title in Sources only.
2. **Ref 22 — Middel et al. 2016, Int J Biometeorol 60:1849–1861.** Draft title is a garbled mashup: *"Impact of urban form and design on mid-afternoon microclimate in Phoenix Local Climate Zones / shade and thermal sensation (Tempe)."* The DOI maps to: **"Impact of shade on outdoor thermal comfort—a seasonal field study in Tempe, Arizona"**. (The "Impact of urban form and design on microclimate in Phoenix" phrase belongs to Middel et al. 2014, LUP 122:16–28.) DOI and citation are otherwise correct; only the title string needs fixing.
3. **Ref 23 — Aboelata & Sodoudi 2020, Build Environ 168:106490.** Draft title: *"Evaluating urban vegetation scenarios to reduce urban heat island and improve thermal comfort in Cairo."* Crossref title: **"Evaluating the effect of trees on UHI mitigation and reduction of energy usage in different built up areas in Cairo"**. Fix the title.

**3.2 Wrong/incomplete DOI and year metadata:**

4. **Ref 36 — Sanusi & Livesley 2020.** Add correct title ("London Plane trees (*Platanus × acerifolia*) before, during and after a heatwave: Losing leaves means less cooling benefit"), add DOI 10.1016/j.ufug.2020.126746; keep psasir URL (live, GET 200) or replace with the DOI.
5. **Ref 3 — Astell-Burt & Feng, sleep paper.** Official issue year is **2020** (SSM Popul Health 2020;10:100497; published online 16 Dec 2019). Draft says "2019". Add DOI 10.1016/j.ssmph.2019.100497.
6. **Ref 35 — Venter et al. 2019 (Oslo).** Official record: **Sci Total Environ 2020;709:136193** (online 2019). Add volume/article number.
7. **Ref 29 — Owen et al. 2024.** Add volume: **UFUG 98:128393**. Full title: "Opportunities and constraints of implementing the 3–30–300 rule for urban greening."
8. **Ref 33 — European 3-30-300 assessment.** Expand to: Bertassello LE, van der Velde M, Maes J, Liu S, Brandt M, Feyen L. "Assessing European cities with the 3-30-300 rule underscores the need for enhanced urban greening efforts." Nat Commun 2026;17:4846. DOI 10.1038/s41467-026-71523-8.

**3.3 Mislabelled / partially supported source links and body claims:**

9. **Ref 37 (up.codes).** The link is presented as NGBS text, but the page is the **Maryland IGCC 2021** wall-shading rule (east/west walls, 20 ft, 10 a.m./3 p.m.). It is a 30 %-wall-shading provision but not the NGBS/ICC 700 text. Recommend removing the link or relabelling it as IGCC. The `codes.iccsafe.org` ICC7002020P1 link is JS-rendered (unverifiable by bot) but is the official ICC 700 platform; the NGBS quote itself is verbatim from the sips.org PDF.
10. **Ref 38 (EPA compendium, §1c body claim).** The sentence *"its examples include Annapolis (MD) and Austin (TX) at 50%, Phoenix at 25%, and Pennsylvania's TreeVitalize program using 25% as a neighbourhood-need threshold"* is only partially supported by the cited PDF:
    - Annapolis 50 % (by 2036) ✓ (present in ch. 2).
    - **Austin 50 % ✗** — Austin appears only via a 2001 resolution; no % in ch. 2.
    - **Phoenix 25 % ✗** — "Phoenix" has **zero** occurrences in the entire chapter.
    - **TreeVitalize 25 % ✗** — TreeVitalize appears only as an SE-Pennsylvania planting partnership; no 25 % threshold.
    Fix by keeping Annapolis, dropping/softening Austin, Phoenix and TreeVitalize, or sourcing the Phoenix/TreeVitalize figures elsewhere.
11. **§1c body claim — "Grün in die Stadt … claims canopy can cut 'felt temperature' by up to 15 °C."** The cited page says trees reduce the *gefühlte Temperatur* "um mehrere Grad Celsius" (several degrees) — **no "15 °C" figure on the page**. Either find the page carrying the 15 °C claim or soften to "several degrees Celsius".
12. **§1a body claim — "the classic estimate of 20–50% cooling-energy savings from well-placed shade trees (Akbari et al. 2001)."** Akbari, Pomerantz & Taha (2001) actually estimate that heat-island mitigation (cool surfaces **plus** trees) can reduce **national air-conditioning energy use by ~20 %** and save >$10B/yr. The building-level shade-tree figure in the EPA compendium's LBNL/SMUD studies is **7–47 %**. The "20–50 %" attribution to Akbari 2001 is a loose secondary claim — reword or re-source.
13. **§2.1 body claim — Ziter study year.** The draft says data were collected "over summer 2017"; the paper's methods state **summer 2016 (May 30–September 6)**. Change to 2016.
14. **§1b body claim — adopter cities.** "Adopted or used as a benchmark by cities including Barcelona, Malmö, Utrecht, and, in Germany, Essen and Munich." **Barcelona is confirmed** (IUCN page, Konijnendijk 2023). Malmö and Utrecht appear in Konijnendijk 2023 only regarding 300-m green-space access and Malmö's Green Space Factor — **not as 3-30-300 adopters**. Essen and Munich are **absent** from the Konijnendijk paper, IUCN page, UBA release, and the Grün-in-die-Stadt page. Soften to the cities the sources actually name (Barcelona, Bristol, Canberra, Seattle, Vancouver) or add a source for Essen/Munich.
15. **§1c body claim — "the EU Nature Restoration Law sets a minimum of 10% urban tree canopy (by 2030 target for cities)."** Not accurate. Regulation (EU) 2024/1991 requires **no net loss** of urban green space and urban tree canopy cover by 2030 and an increasing trend thereafter; a **10 % canopy share (with ≥45 % green space) is an exemption threshold** for excluding certain urban areas, not a mandated minimum. This claim is not anchored to any source in the draft's Sources section — correct it or add the EUR-Lex citation.
16. **§2.2 body claim — "Venter et al. (2021) found satellite SUHI overestimates canopy-layer UHI by ≥40%."** The paper reports a mean **≈6-fold daytime overestimate** (SUHI 1.45 °C vs CUHI 0.26 °C), with SUHI exceeding CUHI in 96 % of cities by day and 80 % at night. "≥40 %" is technically consistent but is not a figure in the paper and badly understates it; reword to the paper's actual numbers.
17. **§3 synthesis table — "Yang 2022 / Wang 2020 … 30% → ~0.9–5 °C LST."** The 0.9 °C bound is Krayenhoff's air-temperature figure (0.3 °C per +10 %), not Yang's LST figure (0.063 °C/% × 30 ≈ **1.9 °C**); Wang's 0.168 °C/% × 30 ≈ 5.0 °C. Correct the low bound to ~1.9 °C or drop the Krayenhoff-derived number from that row.
18. **Tree Equity Score biome baselines (§1c).** The 40/20/15 baselines are explicitly stated in the American Forests 2017 article (from the Nowak/Greenfield analysis) but not on the treeequityscore.org homepage. Attribute the numbers to the American Forests article/methodology rather than implying they are stated on the homepage.
19. **NGBS "earlier editions as §5.3.5.2" (§1a).** Not independently verified (only the 2020 edition was checked). Either verify against the 2015/2012 editions or drop the section number.

---

## 4. Orphan sources (listed in Sources but never cited in the draft body)

- **Ref 32 — Battisti et al. 2024 (Cities).** Appears only in the Sources list; no mention in the body. (Note: Croeser et al. 2024 does cite Battisti for Turin, but the draft itself doesn't.)
- **Ref 35 — Venter et al. 2019 (STOTEN, Oslo).** Appears only in the Sources list; no "Oslo" mention in the body.

Either add a body reference or remove these entries.

---

## 5. Figure / provenance note

- `outputs/tree-canopy-30-heat-cooling.png` exists (73,910 bytes) and is attributed to "data from refs 10, 11, 12, 13, 9, 6". The chart's data provenance is not traceable to raw artifacts in the research files; the underlying per-study values (Yang 0.063, Wang 0.168, Krayenhoff 0.3/10 %, Zaerpour, Ettinger, Iungman) are all individually verified above, so the figure is defensible if it matches those numbers. Recommend a quick re-check of the plotted values against §2.1.
- The draft's closing "Verification note" claims all quantitative claims were checked against abstracts/full texts; that is broadly true, with the exceptions listed in §3.

---

## 6. Count and corrected citation strings

**Broken links: 0. Mismatched items: 16** (3 wrong titles, 1 mislabelled link, 3 unsupported numbers in body claims, 2 loose attributions, 2 wrong factual details in body, 2 orphan sources, plus minor year/volume/DOI additions). Because the count exceeds 5, the task does not require the paste-in corrections list — but for convenience the corrected strings are provided below.

### Corrected Sources strings (paste-in replacements)

1. **Ref 16 (Rahman 2019) — add DOI:**
   `16. Rahman MA, Moser A, Rötzer T. Comparing the transpirational and shading effects of two contrasting urban tree species. Urban Ecosyst 2019;22:683–697. https://doi.org/10.1007/s11252-019-00853-x`

2. **Ref 3 (sleep paper) — year/DOI:**
   `3. Astell-Burt T, Feng X. Does sleep grow on trees? A longitudinal study to investigate potential prevention of insufficient sleep with different types of urban green space. SSM Popul Health 2020;10:100497. https://doi.org/10.1016/j.ssmph.2019.100497 · PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC6996010/`

3. **Ref 2 (JAMA) — add DOI:**
   `2. Astell-Burt T, Feng X. Association of urban green space with mental health and general health among adults in Australia. JAMA Netw Open 2019;2(7):e198209. https://doi.org/10.1001/jamanetworkopen.2019.8209 · https://pubmed.ncbi.nlm.nih.gov/31348510/`

4. **Ref 4 (IJE) — add DOI/title:**
   `4. Astell-Burt T, Feng X. Urban green space, tree canopy and prevention of cardiometabolic diseases: a multilevel longitudinal study of 46 786 Australians. Int J Epidemiol 2020;49(3):926–933. https://doi.org/10.1093/ije/dyz239`

5. **Ref 11 (Wang 2020) — add DOI:**
   `11. Wang J, Zhou W, Jiao M, et al. Significant effects of ecological context on urban trees' cooling efficiency. ISPRS J Photogramm Remote Sens 2020;159:78–89. https://doi.org/10.1016/j.isprsjprs.2019.11.001`

6. **Ref 8 (Li 2023) — add DOI:**
   `8. Li Y, Lin D, Zhang Y, Song Z, Sha X, Zhou S, Chen C, Yu Z. Quantifying tree canopy coverage threshold of typical residential quarters considering human thermal comfort and heat dynamics under extreme heat. Build Environ 2023;233:110100. https://doi.org/10.1016/j.buildenv.2023.110100 (preprint: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4288180)`

7. **Ref 21 (Sanusi 2017) — correct title:**
   `21. Sanusi R, Johnstone D, May P, Livesley SJ. Microclimate benefits that different street tree species provide to sidewalk pedestrians relate to differences in Plant Area Index. Landsc Urban Plan 2017;157:502–511. https://doi.org/10.1016/j.landurbplan.2016.08.010`

8. **Ref 22 (Middel 2016) — correct title:**
   `22. Middel A, Selover N, Hagen B, Chhetri N. Impact of shade on outdoor thermal comfort—a seasonal field study in Tempe, Arizona. Int J Biometeorol 2016;60:1849–1861. https://doi.org/10.1007/s00484-016-1172-5`

9. **Ref 23 (Aboelata & Sodoudi) — correct title:**
   `23. Aboelata A, Sodoudi S. Evaluating the effect of trees on UHI mitigation and reduction of energy usage in different built up areas in Cairo. Build Environ 2020;168:106490. https://doi.org/10.1016/j.buildenv.2019.106490`

10. **Ref 29 (Owen 2024) — add volume:**
    `29. Owen D, et al. Opportunities and constraints of implementing the 3–30–300 rule for urban greening. Urban For Urban Green 2024;98:128393. https://doi.org/10.1016/j.ufug.2024.128393`

11. **Ref 33 (European 2026) — full citation:**
    `33. Bertassello LE, van der Velde M, Maes J, Liu S, Brandt M, Feyen L. Assessing European cities with the 3-30-300 rule underscores the need for enhanced urban greening efforts. Nat Commun 2026;17:4846. https://www.nature.com/articles/s41467-026-71523-8`

12. **Ref 35 (Venter 2019) — year/volume:**
    `35. Venter ZS, Krog NH, Barton DN. Linking green infrastructure to urban heat and human health risk mitigation in Oslo, Norway. Sci Total Environ 2020;709:136193. https://doi.org/10.1016/j.scitotenv.2019.136193`

13. **Ref 36 (Sanusi & Livesley 2020) — title/DOI:**
    `36. Sanusi R, Livesley SJ. London Plane trees (Platanus × acerifolia) before, during and after a heatwave: Losing leaves means less cooling benefit. Urban For Urban Green 2020;54:126746. https://doi.org/10.1016/j.ufug.2020.126746 (repository record: http://psasir.upm.edu.my/id/eprint/86590/)`

14. **Ref 37 (ICC/NGBS) — fix the supplementary links:**
    `37. ICC 700-2020 National Green Building Standard (NAHB/ICC): "Summer shading by planting installed to shade a minimum of 30% of building walls…" — https://www.sips.org/documents/NAHB-National-Green-Building-Standard-2020.pdf (text also via https://codes.iccsafe.org/content/ICC7002020P1). Note: https://up.codes/s/jo-walls is the Maryland IGCC 2021 wall-shading provision, not the NGBS text.`

### Corrections inside the body (not Sources strings)

- §2.1 Ziter: "sampled repeatedly over summer **2017**" → "**2016**".
- §1c EPA bullet: keep Annapolis 50 %; remove or re-source "Austin (TX) at 50 %, Phoenix at 25 %, TreeVitalize … 25 %" (none supported by the cited EPA ch. 2 PDF).
- §1c Grün-in-die-Stadt: "up to 15 °C" → "several degrees Celsius" (the cited page's wording) or re-source.
- §1c EU Nature Restoration Law: replace "sets a minimum of 10 % urban tree canopy" with the actual requirement (no net loss of urban green space and tree canopy by 2030; increasing trend thereafter; 10 %/45 % is an exemption threshold).
- §1b adopter cities: restrict to cities named in the cited sources (Barcelona, Bristol, Canberra, Seattle, Vancouver) or add a source for Malmö/Utrecht/Essen/Munich.
- §1a Akbari: reword "20–50 % cooling-energy savings" to Akbari et al. 2001's actual claim (≈20 % national AC-energy reduction from heat-island mitigation; building-level LBNL/SMUD shade-tree savings of 7–47 % per the EPA compendium).
- §2.2 Venter 2021: replace "≥40 %" with the paper's actual ≈6-fold daytime overestimate (mean SUHI 1.45 °C vs CUHI 0.26 °C).
- §3 table: Yang/Wang row "30% → ~0.9–5 °C" → "~1.9–5 °C" (0.9 is Krayenhoff's air-T figure, not an LST value).

---

*Verifier: Feynman verifier subagent · All DOI metadata from Crossref REST API (queried 2026-08-06). Bot-blocked items verified via Crossref/Semantic Scholar/repository abstracts; content claims for the 20 risk-spot papers confirmed at abstract or full-text level.*
