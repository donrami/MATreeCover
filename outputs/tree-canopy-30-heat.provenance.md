# Provenance — tree-canopy-30-heat

**Slug:** `tree-canopy-30-heat`
**Date:** 2026-08-06
**Topic:** Scientific evidence underlying the guideline that ~30% of a building's surroundings should be shaded by trees against heat.

## Deliverables
- `outputs/tree-canopy-30-heat.md` — final literature review (canonical artifact)
- `outputs/tree-canopy-30-heat.provenance.md` — this file
- `outputs/tree-canopy-30-heat-cooling.png` — figure embedded in the review (matplotlib; data from refs 6, 9, 10, 11, 12, 13 of the review)
- `outputs/tree-canopy-30-heat-research-1.md` — researcher subagent evidence brief (39 candidate items; low/medium-confidence items excluded from the final review unless re-verified)
- `outputs/tree-canopy-30-heat-verifier-report.md` — verifier subagent URL/citation audit (0 broken URLs; 16 fixes, all applied)
- `outputs/tree-canopy-30-heat-reviewer-report.md` — reviewer subagent evidence audit (0 FATAL; 4 MAJOR + minors, all applied)
- `outputs/.plans/tree-canopy-30-heat.md` — plan + task ledger + verification log
- `notes/s2_abstracts.json`, `notes/s2_abstracts2.json` — Semantic Scholar abstract pulls
- `/tmp/konijn.pdf` (downloaded Konijnendijk 2023 full text), `/tmp/ngbs.pdf` (ICC 700-2020 NGBS full text) — primary-source parses (grep-verified)

## Sources consulted (44 unique URLs in final review)
All 44 URLs in the final Sources section were checked by the verifier subagent: **0 dead links**; bot-blocked pages (PNAS, IOP ×3, ScienceDirect ×3, Science.org, EHP, SSRN, ICC platform, Elsevier captcha ×2) were confirmed via Crossref/Semantic Scholar/repository records. Five URLs added after the verifier pass (BMWSB, DUH, IÖW Steckbrief, EC news, Acta Ecologica Sinica) were spot-checked by the author (HTTP status above) and independently inspected by the reviewer subagent.

## Verification status per core claim
| Claim | Status | Evidence |
|---|---|---|
| NGBS (ICC 700-2020) requires ≥30% of building walls shaded by planting (10 am east / noon south / 3 pm west, summer solstice, 5 yrs after planting) | VERIFIED (primary text) | sips.org NGBS 2020 PDF, grep of full document |
| 3-30-300 rule: 3 trees / 30% neighbourhood canopy / 300 m park | VERIFIED (primary text) | Konijnendijk 2023, J For Res 34:821-830 (full PDF) |
| Konijnendijk justifies 30% via Astell-Burt & Feng (health), cites Ziter ≥40% for heat, 300 m via WHO | VERIFIED (primary text) | Konijnendijk 2023 full text, verbatim quotes in review |
| Astell-Burt & Feng 2019: canopy ≥30% vs 0-9% → OR 0.69 distress / 0.67 poor health; graded gradient, no step at 30% | VERIFIED (full text) | JAMA Netw Open 2(7):e198209 (PubMed/PMC full text; gradient values from reviewer full-text check) |
| Ziter 2019: ≥40% canopy for substantial daytime cooling, nonlinear, block scale, weak at night | VERIFIED (abstract + PMC full text) | PNAS 116(15):7575-7580; PMC6462107 |
| Iungman 2023: 93 cities; UHI +1.5 °C; 6,700 deaths (4.33%); 30% cover → 0.4 °C, 2,644 deaths (1.84%) ≈ 39% of UHI deaths | VERIFIED (abstract; arithmetic checked) | Lancet 401(10376):577-589; PMID 36736334; 2644/6700 = 39.5% |
| Ouyang 2020: 20-30% TCR efficiency optimum, logarithmic | VERIFIED | Build Environ 174:106772 (S2/ADS + secondary) |
| Li 2023 Nanjing: max effective TCC 45/30/25% by 33/54/100 m buildings | VERIFIED | Build Environ 233:110100 (Crossref; SSRN preprint 4288180) |
| Ettinger 2024: linear cooling, no threshold, ~5× risk 0% vs 100% | VERIFIED (abstract) | Sci Rep 14:3266 |
| Yang 2022: 0.063 °C/1% (0.087 summer, ~0.007 night); Wang 2020: 0.168 °C/1% (0.040-0.574) | VERIFIED | ERL 17:034029; ISPRS JPRS 159:78-89 |
| Krayenhoff 2021: ≈0.3 °C per 0.10 canopy; 146 studies | VERIFIED (abstract) | ERL 16:053007 |
| Zaerpour 2025: +10/20/30% → −0.8/−1.1/−1.5 °C; SUHI 8.9 vs CUHI 4.6 °C; TC 57% variance | VERIFIED (full text) | npj Urban Sustain 5:92 |
| Coutts 2016 UTCI class drop; Klemm 2015 Tmrt −1 K no air-T effect; Ren 2022 PET 64/11/0%; Sanusi PAI; Middel shade sensation | VERIFIED (abstracts/full text per reviewer + researcher) | refs 18-22 |
| Aboelata & Sodoudi 2020 Cairo: trees can warm low-density districts ~3 K (humidity) | VERIFIED (abstract) | Build Environ 168:106490 |
| Sinha 2022 +10% → up to ~22% Phoenix; Kalkstein 2022 ~1 in 4 heat-wave deaths (8-29% per event) | VERIFIED (abstract + reviewer full-text check) | JEM 301:113751; IJB 66:911-925 |
| Chi 2025: HR 0.979/IQR; aggregation 0.831 vs fragmentation 1.073; Song 2023 eye-level greenery RR 1.103 vs 0.943 | VERIFIED (abstracts) | Lancet Planet Health 9(3); EHP 131(9) |
| Croeser 2024: 2.5M buildings, 8 cities; Singapore ~75%, Seattle ~45% pass 30%; Owen 2024: 10-18.4% footprint conversion | VERIFIED (full text / abstract) | Nat Commun 15:9333; UFUG 98:128393 |
| European 3-30-300: 862 cities; <15% meet all three; 21% none | VERIFIED (full text) | Nat Commun 17:4846 (2026) |
| BMWSB Hitzeschutzstrategie 2025 propagates 30% canopy citing Iungman 2023 | VERIFIED (full PDF, reviewer-parsed) | bmwsb.bund.de PDF |
| EPA compendium: no universal %; Annapolis 50% documented | VERIFIED (full PDF) | EPA ch. 2 PDF |
| American Forests withdrew universal 40% (2017); biome baselines 40/20/15 | VERIFIED | americanforests.org article |
| Venter 2021: SUHI overestimates CUHI ~6× by day (1.45 vs 0.26 °C) | VERIFIED (abstract + reviewer) | Sci Adv 7:eabb9569 |
| WHO 2017: ≤300 m / ≥1 ha green space | VERIFIED | WHO Europe publication |

## Sources rejected / excluded from final review
- Bowler et al. 2010 (park cooling 0.94 °C): verified but not central; excluded to keep focus on canopy/shade thresholds (in researcher notes).
- Douala NDVI breakpoint, Liu et al. turning-point, Sydney heatwave-mortality, Warsaw 3-30-300 (medium/low confidence per researcher): excluded.
- Verifier-flagged mismatches in earlier draft (EPA Austin/Phoenix/TreeVitalize percentages; "≥40%" Venter phrasing; Akbari 20-50% claim; EU NRL 10% minimum; grün-in-die-stadt 15 °C attribution): all corrected in final.
- The claim that the 30% figure in Iungman was "chosen for policy tractability" (unverifiable paraphrase): replaced with the authors'/EC rationale (established benchmark adopted by many cities).

## Open items / limitations
- Iungman et al. methods (exposure–response functional form) not inspected at methods level (paywalled); review states the exposure–response function is applied over modeled reductions, without asserting linearity.
- Ziter's threshold (40%) rests on one mid-size US city; multi-city air-temperature threshold studies are absent (noted in Open Questions).
- Mortality figures (Iungman, Sinha, Kalkstein) are scenario/modeled, not observational (flagged in text).
- NGBS section numbers for editions other than 2020 not verified.
- Research brief items marked low/medium confidence were not promoted to the final review.

## Verification chain
1. Author: primary-source retrieval (Konijnendijk PDF, NGBS PDF, abstracts via Semantic Scholar/PubMed/PMC/Nature/Springer) — 2026-08-06
2. `researcher` subagent: breadth sweep (39 items) → outputs/tree-canopy-30-heat-research-1.md
3. `verifier` subagent: 47 URLs + Crossref metadata audit → 0 dead, 16 fixes applied → outputs/tree-canopy-30-heat-verifier-report.md
4. `reviewer` subagent: adversarial evidence audit + independent spot checks → 0 FATAL, 4 MAJOR fixed → outputs/tree-canopy-30-heat-reviewer-report.md
5. Author: final on-disk verification of all deliverables.
