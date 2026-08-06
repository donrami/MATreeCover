# Plan: Evidence behind the "~30% tree shade around buildings" heat guideline

Slug: `tree-canopy-30-heat`
Date: 2026-08-06

## Research questions
1. Where does the "~30% canopy/shade around buildings" figure come from?
   - The 3-30-300 rule (Konijnendijk 2023), city canopy targets, other building/planning guidelines (check German-language angle too).
2. What empirical studies test canopy-cover thresholds for cooling?
   - Air temperature (Ziter 2019; Venter 2020; Jenerette/Harlan), surface temperature, thermal comfort (PET/UTCI), heat-related mortality (Iungman 2023).
3. How strong is the evidence that *shade* (vs transpiration) drives human thermal-comfort benefits?
4. What are the caveats? Nonlinearity, climate/context dependence, nighttime warming, irrigation, measurement units (2D canopy vs 3D shade), modeled vs observed mortality, rule is a heuristic.

## Source types
- Peer-reviewed papers via alphaXiv search + direct fetches (Springer/PNAS/Lancet/PMC abstracts).
- Web: guideline documents (EPA, WHO, American Forests, city plans), 3-30-300 adoption articles, German-language guidelines (30% Verschattung).
- Time period: ~2001–2026, with foundational older studies (Akbari 2001; Harlan 2006).

## Expected sections
1. Summary
2. Origins of the 30% figure
3. Canopy thresholds for cooling (observational + modeling)
4. Shade and human thermal comfort
5. Health impact assessments (30% → mortality)
6. Threshold synthesis: what the evidence actually supports
7. Caveats and disagreements
8. Open questions
9. Sources

## Task ledger
- [x] Plan written
- [x] Gather: key papers verified (Konijnendijk full text; Ziter; Iungman; Krayenhoff; Ouyang; Li; Ettinger; Yang; Wang 2020 ISPRS; Ren; Coutts; Klemm; Sanusi; Sinha; Kalkstein; Chi; Song; Croeser; Owen; Zaerpour; Astell-Burt & Feng; NGBS primary text)
- [x] Gather: rule-origin / guideline sources (3-30-300 origin paper, NGBS ICC 700-2020, EPA compendium, American Forests, WHO 2017, German UBA/BGL angle)
- [x] Synthesize draft -> outputs/tree-canopy-30-heat.md (37.6 KB) + chart outputs/tree-canopy-30-heat-cooling.png + researcher brief outputs/tree-canopy-30-heat-research-1.md
- [x] Cite: verifier pass (47 URLs, 0 dead; 16 fixes applied) -> verifier-report.md
- [x] Review: reviewer pass (0 FATAL; 4 MAJOR + minors fixed; incl. BMWSB 30% finding) -> reviewer-report.md
- [x] Deliver outputs/tree-canopy-30-heat.md + outputs/tree-canopy-30-heat.provenance.md (both verified on disk 2026-08-06)

## Verification log
- Konijnendijk 2023: full text read (PDF + Springer HTML). 30% justified via Astell-Burt & Feng (2019a,b; 2020); Ziter cited as >=40% for cooling; 300m via WHO 2017; arid caveat: 30% vegetation. VERIFIED.
- Astell-Burt & Feng 2019 JAMA Netw Open: abstract read. Canopy >=30% vs 0-9%: distress OR 0.69 (0.54-0.88); fair/poor health OR 0.67 (0.57-0.80); grass >=30% worse (OR 1.47/1.71). VERIFIED.
- Ziter 2019 PNAS: abstract+significance. >=40% canopy for substantial daytime cooling; nonlinear; block scale 60-90 m; night: canopy limited. VERIFIED.
- Iungman 2023 Lancet (NOT Lancet Planet Health; corrected): 93 cities; UHI +1.5C; 6700 deaths (4.33% summer); 30% cover -> 0.4C (0.0-1.3); 2644 deaths (1.84% summer) = ~39% of UHI deaths. VERIFIED.
- NGBS ICC 700-2020 primary PDF (sips.org): 'Summer shading... minimum of 30% of building walls... 10am east, noon south, 3pm west, summer solstice, 5 years after planting'. VERIFIED (grep of full PDF).
- Ouyang 2020 Build Environ 174:106772: 20-30% TCR efficiency optimum, logarithmic. VERIFIED (S2 abstract + ADS + secondary).
- Ren 2022 J For Res: 13/35/75% cover; PET>35C: 64%/11%/0%. VERIFIED (S2 abstract + journal page).
- Ettinger 2024 Sci Rep: linear, no threshold; 2.57C variation; ~5x risk at 0% vs 100%. VERIFIED (S2 abstract).
- Yang 2022 ERL / Wang 2020 ISPRS numbers (0.063 / 0.168 C per 1%): VERIFIED via search + S2 abstracts.
- Krayenhoff 2021: VCE ~0.3C per 0.10 canopy; 146 studies. VERIFIED.
- Zaerpour 2025 npj: SUHI 8.9 vs CUHI 4.6; +10/20/30% -> -0.8/-1.1/-1.5C; TC explains 57% variance. VERIFIED (full text fetched).
- Croeser 2024 Nat Commun 15:9333: full text fetched; Singapore ~75% / Seattle ~45% pass 30%; 'bare minimum'; tree size finding. VERIFIED.
- Li 2023 Nanjing thresholds 45/30/25% by 33/54/100 m height: VERIFIED via SSRN + bishtref record (S2 DOI 404; cited via SSRN + B&E DOI).
- Cohen: Bowler 2010 (0.94C parks) NOT used in final draft (kept in research notes).
- Research-1.md claims marked medium/low confidence (Ecologica Sinica; Douala; Liu 2021; Sydney) NOT used in final draft.
- PENDING verifier: all URLs resolve; citation metadata (authors/year/journal) match; NGBS section number sanity.

## Verification log
- (to be filled: each strong claim → source + status)

- 2026-08-06 16:18: final disk check OK: review (235 lines, 43.9 KB), provenance, chart, both agent reports, plan all present. Reviewer MAJOR findings (BMWSB German lineage, provenance pointer, Iungman rationale, Astell-Burt gradient) all addressed. New URLs (BMWSB, DUH, IÖW, EC, Ecologica) return HTTP 200.
