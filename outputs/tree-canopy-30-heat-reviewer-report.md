# Reviewer Report — `tree-canopy-30-heat.md` (evidence behind the ~30% tree shade/canopy guideline)

**Reviewed:** 2026-08-06 · **Mode:** adversarial evidence audit (verification pass) + venue-style review
**Files inspected:** `outputs/tree-canopy-30-heat.md`, `outputs/tree-canopy-30-heat-verifier-report.md`, `outputs/tree-canopy-30-heat-research-1.md`, `outputs/tree-canopy-30-heat-cooling.png` (exists)
**Independent re-verification performed:** Iungman et al. 2023 (Europe PMC abstract), Astell-Burt & Feng 2019 (PMC full text), Kalkstein et al. 2022 (PMC full text), Chi et al. 2025 (PubMed/abstract), Sinha et al. 2022, Owen et al. 2024, Aboelata & Sodoudi 2020 (ADS abstract), Venter et al. 2019/2020 (Oslo), Rahman et al. 2020, Ettinger et al. 2024, plus German-language sources: BMWSB *Hitzeschutzstrategie* (full PDF parsed), presseportal.de release (BGL/"Grün in die Stadt"), SZ 3-30-300 piece, TUM/IÖW *Steckbrief Bäume als Hitzeschutz*.

---

## Headline

The review is **strong, well-hedged, and internally consistent on its core claims**, and the verifier's fixes are almost all genuinely applied (Ziter 2016 ✓, EPA bullet ✓, EU NRL ✓, Venter 6-fold ✓, synthesis-table 1.9–5 °C ✓, orphans re-cited ✓, up.codes relabelled ✓, Akbari reworded ✓). The **Iungman-derived numbers are computed and stated correctly** (0.4 °C, 2,644 deaths, 1.84%, ≈39%: 2,644/6,700 = 39.5%). I found **no FATAL factual errors**. However, four MAJOR issues remain — the most consequential being that the draft's German-language bullet is contradicted by the German federal government's own heat-protection strategy, which *does* propagate a 30% canopy figure (citing Iungman), and the draft promises a provenance file that does not exist.

---

## Findings

### FATAL
None. (The items below that come closest — M1 and M2 — are fixable in a few lines and do not invalidate the review's central thesis.)

### MAJOR

- **[M1] The §1c "German-language guidance" bullet is incomplete and now factually contradicted by the German federal strategy.**
  - Quote: *"German-language guidance (e.g., Umweltbundesamt; TUM/ioew "Bäume als Hitzeschutz" fact sheets) emphasises large-crown trees and shade rather than a fixed 30% share"*
  - Problem: The German Federal Ministry for Housing, Urban Development and Building (BMWSB), in its *Hitzeschutz – Eine Handlungsstrategie für die Stadtentwicklung und das Bauwesen* (Feb 2025), states verbatim: *"Forschungsergebnisse zeigen, dass eine Bedeckung durch Baumkronen von 30 % die Mortalität von Menschen in diesem Siedlungsbereich bei Hitze relevant reduziert (The Lancet, Januar 2023: www.eurekalert.org/news-releases/978104)"* — i.e., the federal strategy explicitly propagates the **30% canopy figure** and anchors it to Iungman et al. 2023. The Deutsche Umwelthilfe *Hitze-Check* (2025/2026) likewise applies ≥30% *Baumbeschirmung* as the science-based *Richtwert* across German cities. The statement "rather than a fixed 30% share" is therefore only true of UBA/TUM-IÖW material, not of German guidance as a whole. This is also exactly the German-language alternative interpretation the parent asked about.
  - Fix: Rewrite the German bullet to distinguish three strands: (i) UBA/TUM-IÖW guidance that avoids a fixed number (as currently stated, and now citable — see m6); (ii) the federal BMWSB strategy that adopts Iungman's 30% as a mortality-relevant target; (iii) DUH *Hitze-Check* applying 30% *Baumbeschirmung* as its standard. Add the BMWSB strategy to Sources. Optionally add one line to §6 for end users: *"If you met the figure in a German planning/policy context, it is usually Iungman's 30% scenario transmitted via the BMWSB Hitzeschutzstrategie or DUH Hitze-Check, i.e. the 3-30-300/Iungman lineage — not wall shading."*

- **[M2] The verification note promises a provenance file that does not exist.**
  - Quote: *"Verification note: all quantitative claims above were checked against abstracts or full texts retrieved during this review (see provenance file)."*
  - Problem: `outputs/` contains no file named or identifiable as a provenance file. The raw evidence table (`tree-canopy-30-heat-research-1.md`) exists but is never referenced. For an evidence-audit deliverable, a dangling pointer to an audit trail is an integrity gap.
  - Fix: Either (a) point the note at `tree-canopy-30-heat-research-1.md` explicitly, (b) create a real provenance file listing per-claim sources, or (c) delete the clause.

- **[M3] The Iungman methodological claim "the exposure–response is assumed linear over the modeled range" is not verifiable from the cited material, and "chosen for policy tractability" mis-describes the paper's stated rationale.**
  - Quote (§2.4): *"30% was the intervention scenario (chosen for policy tractability), not a threshold derived from data; the exposure–response is assumed linear over the modeled range."*
  - Problem: The Lancet abstract (fetched) reports the scenario and the results but says nothing about a linear exposure–response assumption; the paper is paywalled and this claim was not checked at methods level. The 30% rationale is also mis-cited: the paper's actual rationale (per the authors' own communications and the EC/ISGlobal summaries) is that **30% is an established benchmark already recommended by other studies and adopted by many cities** — "policy tractability" is a paraphrase that should not be presented as the paper's reason.
  - Fix: Verify against the paper's methods; if confirmed, add a methods citation (e.g., "Iungman et al. 2023, methods, apply a linear approximation of the temperature–mortality exposure–response function"). Otherwise soften to "applies a temperature–mortality exposure–response function over the modelled temperature reduction". Reword the rationale clause to "chosen because 30% is an established canopy benchmark adopted by many cities."

- **[M4] Synthesis-table cell "Astell-Burt & Feng 2019 … Yes — the actual origin of 30%" overclaims relative to the body, and the anchor study's own gradient is omitted (missing counter-evidence).**
  - Quote (§3 table): *"Astell-Burt & Feng 2019 (JAMA Netw Open) | 3 Australian cities | Mental/general health | ≥30% canopy vs 0–9%: OR 0.67–0.69 | Yes — the actual origin of 30%"*
  - Problem: (a) The body is careful (§2.4: "rests mainly on health-epidemiology evidence"; "30% here is the top exposure category boundary… not a statistically identified breakpoint"), but the table's "the actual origin of 30%" presents the causal-historical claim as settled. (b) In A&B&F's own data the association is a **graded gradient, not a step at 30%**: descriptive incident-distress prevalence is 4.60% (0–9% canopy), 3.78% (10–19%), 2.85% (20–29%), 2.43% (≥30%) (Table 1 of the paper, verified in full text), and the adjusted OR for 20–29% is ≈0.70 — statistically indistinguishable from the ≥30% OR of 0.69. A reader could come away thinking the study found a breakpoint at 30%; it found a monotone benefit across the whole range.
  - Fix: Soften the cell to "Yes — the health-epidemiological basis Konijnendijk cites for 30%"; add one clause to §2.4 noting benefits are already apparent at 20–29% in that study (this *strengthens* the review's "30% is a benchmark, not a threshold" thesis).

### MINOR

- **[m1] Bottom-line "surface temperature overstates air-temperature effects ~2×" understates the body's own range.**
  - Quote (Bottom line): *"surface temperature overstates air-temperature effects ~2×"*
  - Problem: 2× is Zaerpour's single-city ratio (8.9/4.6 °C); Venter et al. 2021's daytime mean is ≈6× and §4 caveat 3 says "~2–10×". The bottom line should match the body's spread.
  - Fix: "…overstates air-temperature effects by roughly 2× (up to ~6× by day, Venter 2021)…" or "~2–6×".

- **[m2] Kalkstein figures lack scenario/event qualification.**
  - Quote (§2.4): *"aggressive tree + albedo scenarios cool 1–2.5 °C and could prevent roughly 1 in 4 heat-wave deaths (18–29% per heat event), from a baseline urban tree cover of ~16.6%."*
  - Problem: Full text (verified) shows event-specific reductions of **8–29%** across the four scenarios; the 18–29% band corresponds only to the most aggressive scenario (case 4: 18%, 18%, 29% across three events). Temperature reductions are "mostly in the range of 1–2 °C", "sometimes exceeding 2.5 °C", and the discussion cites 2–3 °C at the hottest times of day. Baseline 16.6% ✓ and "~1 in 4" ✓.
  - Fix: "…could prevent roughly 1 in 4 heat-wave deaths (event-specific reductions of ~8–29%; up to 29% in the most aggressive scenario)…" and "cool ~1–2 °C (up to ~2.5–3 °C at the hottest times)".

- **[m3] Astell-Burt grass OR range mixes two different outcomes/designs.**
  - Quote (§2.4): *"≥30% grass was associated with worse outcomes (OR 1.47–1.71)"*
  - Problem: 1.47 is the OR for *incident* fair/poor general health; 1.71 is the OR for *prevalent* psychological distress (verified in full text). Presenting them as one range conflates two estimates.
  - Fix: "…worse outcomes (OR 1.47 for incident poor health; OR 1.71 for prevalent distress)".

- **[m4] In-text year for the sleep study disagrees with the Sources entry.**
  - Quote (§2.4): *"Astell-Burt & Feng 2019, SSM Popul Health"* vs Sources #3: "SSM Popul Health **2020**;10:100497".
  - Fix: Align in-text to 2020 (online Dec 2019).

- **[m5] NGBS wording in the Bottom line overstates the code's status and scope.**
  - Quote (Bottom line): *"the US National Green Building Standard (ICC 700) requires trees (or other shading) to cover ≥30% of building walls on the summer solstice"*
  - Problem: The quoted provision (§1a) is "Summer shading **by planting**" and it is a **landscaping credit**, not a baseline requirement of the code. "(or other shading)" is not in the quoted text.
  - Fix: "…as a landscaping credit requires planting that shades ≥30% of building walls…".

- **[m6] "TUM/ioew 'Bäume als Hitzeschutz' fact sheets" are named in §1c but have no Sources entry.**
  - Problem: The fact sheet exists (IÖW 2023/2025, Feder & Welling, *Steckbrief: Bäume als Hitzeschutz. Strategisch pflanzen und Bestand erhalten*, ioew.de) — verified — but it is neither cited nor linked.
  - Fix: Add to Sources, or drop the institution names.

- **[m7] "Verifier issue #11" (the 15 °C advocacy claim) is actually supported — close it out rather than leaving the record ambiguous.**
  - Quote (§1c): *"in its press materials, claims canopy can cut 'felt temperature' by up to 15 °C"*
  - Problem: The verifier flagged this as unsupported because the grun-in-die-stadt.de landing page says only "mehrere Grad Celsius". However, the **presseportal release cited in Sources #43** (BGL/"Grün in die Stadt", 14 Aug 2025) states verbatim: *"Ein hoher Kronendachanteil … reduziert die gefühlte Temperatur um bis zu 15 Grad"*. The claim is therefore correct as sourced. Note the fix was NOT applied, but should not be applied as the verifier suggested — instead, tighten the sentence to name the press release explicitly.
  - Fix: "…the BGL/'Grün in die Stadt' press release (2025) claims canopy can cut 'felt temperature' by up to 15 °C…". Consider also noting the SZ *Sonderausgabe* repeats the figure (which the draft already cites as Source #44).

- **[m8] Adopter-cities claim now rests only on promotional German press.**
  - Quote (§1b): *"German press coverage names Malmö, Utrecht and, in Germany, Essen and Munich among municipalities drawing on the rule in their climate strategies."*
  - Problem: Verified — the SZ *Sonderausgabe* piece does name exactly these cities, and the BGL press release names Barcelona/Malmö/Utrecht. But both are promotional/soft content, not the Konijnendijk paper (which names Barcelona, Bristol, Canberra, Seattle, Vancouver). The draft's attribution "German press coverage" is accurate, but a one-clause caveat would prevent a reader treating Essen/Munich as peer-reviewed adopters.
  - Fix (optional): append "(promotional press claims; not verified in Konijnendijk 2023 or city official plans)".

- **[m9] Open Questions could acknowledge the 229-city LST threshold study sitting in the raw evidence table.**
  - Quote (§5): *"no equivalent multi-city, multi-climate observational air-temperature threshold study exists"*
  - Problem: As written (air-temperature) the claim is defensible, but the supporting research file contains a 229-global-city LST piecewise-regression threshold study (Acta Ecologica Sinica 2024: FTC thresholds 19%/45%/30%/55%/23% by climate) that would *support* the review's context-dependence argument and pre-empt the objection that "thresholds are only ever single-city".
  - Fix (optional): cite it as an LST-based counterpoint, or explicitly scope the Open Question to air-temperature studies.

---

## Findings on the specific questions asked

1. **Unsupported/over-claimed statements & numbers without sources:** No remaining unanchored quantitative claims found in the body beyond the items above (the two "unsupported" flags from the verifier — 15 °C and adopter cities — are each now traceable to a cited source; see m7/m8). One methodological claim (M3, linearity) is unverified against the source.

2. **Logical gaps / missing counter-evidence:** The strongest missing counter-evidence is the A&B&F graded gradient at 20–29% (M4). Also, the review argues "thresholds are context-dependent" but omits the multi-city LST threshold evidence it already collected (m9). The German-policy counter-evidence to "German guidance avoids a fixed 30%" is missing (M1).

3. **Zombie sections / orphan references:** No orphan sources remain (Battisti, Venter-Oslo now cited). Reverse problem exists instead: TUM/IÖW named without a source (m6) and a promised-but-missing provenance file (M2). The figure PNG exists and its plotted values match §2.1.

4. **Single-source findings presented as settled:** Generally handled well (Ziter 40% is explicitly contrasted with Ettinger/Yang; Ouyang flagged for replication; Iungman flagged as a scenario). Residual: "the actual origin of 30%" (M4) and the unqualified "18–29% per heat event" (m2).

5. **"Two lineages" framing:** **Fair and well-hedged** ("(at least) two distinct lineages"). The distinction between NGBS wall-shading (energy) and 3-30-300 canopy (health) is real and correctly drawn; the draft also correctly refuses to let either lineage claim a physical optimum. The main gaps: (a) the German policy lineage (BMWSB + DUH + advocacy press) that transmits Iungman's 30% is treated only as "advocacy" and not as a third propagation path (M1); (b) an explicit note on "where the user most likely met this number depending on their context (US building code vs European neighbourhood target vs German policy)" is missing; (c) the mermaid diagram already shows a third branch (city canopy targets) that the Bottom line collapses into the two-lineage framing — harmless given the "(at least)" hedge, but a three-way structure in the Bottom line would match the diagram.

6. **Internal consistency:** 
   - Bottom line vs body: consistent on all substantive claims (30% span 20–45%, 2/8 cities, Iungman numbers, NGBS vs 3-30-300). Nits: "~2×" (m1), "trees (or other shading)" (m5).
   - Synthesis table vs §2: agree on every row after the earlier 0.9→1.9 °C fix; Yang/Wang "30% → ~1.9–5 °C LST" is arithmetically correct (0.063×30 = 1.89; 0.168×30 = 5.04). Only the A&B&F "actual origin" cell (M4) is stronger than the body.
   - **Iungman-derived numbers: CORRECT.** Verified against the Lancet abstract: 1.5 °C mean UHI warming ✓; 6,700 deaths / 4.33% ✓; 0.4 °C (range 0.0–1.3) ✓; 2,644 deaths / 1.84% ✓; "≈39% of UHI-attributable deaths" = 2,644/6,700 = 39.5% ✓; the bottom line's "≈2,600 (≈39%)" ✓.

---

## Questions for authors

- [Q1] What is the end user's most likely context for having met "~30% tree shade/canopy around buildings"? If German-speaking (the UBA/TUM/SZ/Grün-in-die-Stadt material suggests it), M1's fix is mandatory before delivery; if US code-facing, the NGBS lineage dominates.
- [Q2] Should the provenance file exist as a deliverable, or should the verification note point to `tree-canopy-30-heat-research-1.md`?
- [Q3] Can the Iungman methods be checked for the linear exposure–response claim (paywalled paper, open supplement)?
- [Q4] Do you want to keep the (unapplied) verifier fix #11 as-is given the 15 °C claim is now confirmed in the cited press release?

## Verdict

**Pass with major revisions.** The review is accurate on every number I re-verified, honestly hedged about what 30% is and is not, and internally consistent on its central thesis. It would be acceptable as a policy-facing evidence review for a planning/architecture audience after M1–M4 are addressed; M1 in particular should be fixed before delivery if the audience is German. Confidence in the numerics: high (all spot-checked values matched the primary sources); confidence in completeness: moderate (German-policy and Iungman-methods gaps).

## Revision plan (prioritized)

1. **M1** — rewrite the German bullet; add BMWSB *Hitzeschutzstrategie* (and optionally DUH *Hitze-Check*) to §1c and Sources; add a "where you met 30%" context note to §6.
2. **M2** — link or create the provenance file, or delete the clause.
3. **M3** — verify the linearity claim against Iungman methods; fix "policy tractability" wording.
4. **M4** — soften the table cell; add the 20–29% gradient clause in §2.4.
5. **m1–m6** — apply the small precision fixes (all single-line edits).
6. **m7/m8** — leave the 15 °C claim but attribute it to the press release; add the promotional-press caveat for Essen/Munich (optional).

---

## Inline Annotations

> "German-language guidance (e.g., Umweltbundesamt; TUM/ioew "Bäume als Hitzeschutz" fact sheets) emphasises large-crown trees and shade rather than a fixed 30% share" (§1c)
**[M1] MAJOR:** Contradicted by the BMWSB *Hitzeschutz – Eine Handlungsstrategie für die Stadtentwicklung und das Bauwesen* (2025), which states "eine Bedeckung durch Baumkronen von 30 % die Mortalität … bei Hitze relevant reduziert (The Lancet, Januar 2023)". The DUH *Hitze-Check* likewise applies ≥30% *Baumbeschirmung* as its standard. Fix: split the German guidance into (i) UBA/TUM-IÖW (no fixed number), (ii) BMWSB federal strategy (adopts Iungman's 30%), (iii) DUH/green-industry advocacy; add sources.

> "all quantitative claims above were checked against abstracts or full texts retrieved during this review (see provenance file)" (verification note)
**[M2] MAJOR:** No provenance file exists in `outputs/`. Either reference `tree-canopy-30-heat-research-1.md`, create the file, or drop the clause.

> "30% was the intervention scenario (chosen for policy tractability), not a threshold derived from data; the exposure–response is assumed linear over the modeled range" (§2.4)
**[M3] MAJOR:** The linearity claim is not in the abstract and was not methods-checked; the paper's stated rationale for 30% is that it is an established benchmark adopted by many cities, not "policy tractability". Verify against methods or soften; reword the rationale.

> "Astell-Burt & Feng 2019 (JAMA Netw Open) | … | Yes — the actual origin of 30%" (§3 table)
**[M4] MAJOR:** Stronger than the body ("rests mainly on health-epidemiology evidence"). In the full text, the association is graded (distress incidence 4.60% → 3.78% → 2.85% → 2.43% across 0-9/10-19/20-29/≥30% canopy; adjusted OR for 20–29% ≈ 0.70 vs 0.69 for ≥30%). No breakpoint at 30% even in the anchor study. Soften the cell and add the 20–29% clause.

> "surface temperature overstates air-temperature effects ~2×" (Bottom line)
**[m1] MINOR:** Zaerpour's 2× is the low end; Venter 2021 is ~6× by day and §4 caveat 3 says 2–10×. Harmonise.

> "aggressive tree + albedo scenarios cool 1–2.5 °C and could prevent roughly 1 in 4 heat-wave deaths (18–29% per heat event), from a baseline urban tree cover of ~16.6%" (§2.4)
**[m2] MINOR:** Verified against the full text: 16.6% and "~1 in 4" are exact; but event-specific reductions range 8–29% across scenarios, with 18–29% only for the most aggressive case; temperatures are "mostly 1–2 °C", "sometimes exceeding 2.5 °C". Add scenario/event qualification.

> "≥30% grass was associated with worse outcomes (OR 1.47–1.71)" (§2.4)
**[m3] MINOR:** 1.47 is incident general health, 1.71 is prevalent distress — two different outcomes/designs. State per-OR.

> "Astell-Burt & Feng 2019, SSM Popul Health" (§2.4)
**[m4] MINOR:** Sources list the same study as SSM Popul Health 2020;10:100497. Align in-text.

> "the US National Green Building Standard (ICC 700) requires trees (or other shading) to cover ≥30% of building walls on the summer solstice" (Bottom line)
**[m5] MINOR:** §1a correctly calls this a "landscaping credit" and the quoted text says "Summer shading by planting"; "(or other shading)" and "requires" overstate. Tighten.

> "in its press materials, claims canopy can cut 'felt temperature' by up to 15 °C" (§1c)
**[m7] MINOR (resolution):** The verifier's "unsupported" flag is wrong on the merits — the cited presseportal release (BGL/"Grün in die Stadt", 14 Aug 2025) states verbatim "reduziert die gefühlte Temperatur um bis zu 15 Grad". Keep the claim; attribute it to the press release explicitly.

> "German press coverage names Malmö, Utrecht and, in Germany, Essen and Munich among municipalities drawing on the rule in their climate strategies" (§1b)
**[m8] MINOR:** Verified — the SZ *Sonderausgabe* names exactly these cities and the BGL release names Barcelona/Malmö/Utrecht. Both are promotional press; a one-clause caveat would prevent over-reading.

> "no equivalent multi-city, multi-climate observational air-temperature threshold study exists" (§5)
**[m9] MINOR:** Accurate as scoped (air temperature), but the raw evidence table contains a 229-city LST threshold study (Acta Ecologica Sinica 2024, 19–55% by climate) that would strengthen the context-dependence argument — consider citing or scoping explicitly.

> "Iungman et al. 2023 (Lancet) … cool cities by a mean 0.4 °C and prevent ≈2,600 (≈39%) of summer UHI-attributable deaths" (Bottom line)
**[✓ VERIFIED]** Matches the Lancet abstract (0.4 °C, 2,644 [95% CI 2,444–2,824] deaths, 1.84% of summer deaths); 2,644/6,700 = 39.5% ≈ 39%. All Iungman-derived numbers in §2.4 are correct.

---

## Sources (independently inspected during this review)

- Iungman et al. 2023, Lancet 401:577–589 — abstract: https://europepmc.org/article/MED/36736334 ; PMID 36736334
- Astell-Burt & Feng 2019, JAMA Netw Open 2(7):e198209 — full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC6661720/
- Kalkstein et al. 2022, Int J Biometeorol 66:911–925 — full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC9042982/
- Chi et al. 2025, Lancet Planet Health 9(3):e186–e195 — abstract: https://pubmed.ncbi.nlm.nih.gov/40120625/ ; https://sciensano.be/sites/default/files/chi_et_al_2025_lancet_planet_health_residential_tree_canopy_configuration.pdf
- Sinha et al. 2022, J Environ Manage 301:113751 — abstract: https://research.fs.usda.gov/treesearch/63422 ; https://www.rti.org/publication/variation-estimates-heat-related-mortality-reduction-due-tree-cover-us-cities
- Owen et al. 2024, UFUG 98:128393 — https://nora.nerc.ac.uk/id/eprint/537535/ ; https://doi.org/10.1016/j.ufug.2024.128393
- Aboelata & Sodoudi 2020, Build Environ 168:106490 — abstract: https://ui.adsabs.harvard.edu/abs/2020BuEnv.16806490A/abstract
- Venter, Krog & Barton, Sci Total Environ 709:136193 (2020, online 2019) — https://climahealth.info/resource-library/linking-green-infrastructure-to-urban-heat-and-human-health-risk-mitigation-in-oslo-norway/
- Rahman et al. 2020, Build Environ 170:106606 (meta-analysis; 4.15 vs 0.44 g·m⁻²·min⁻¹ transpiration over grass vs paved pits) — https://minerva-access.unimelb.edu.au/server/api/core/bitstreams/ebbb62f1-806d-4960-94af-f37dcd102889/content
- Ettinger et al. 2024, Sci Rep 14:3266 (32.2 °C = 90 °F WA threshold; ~5× risk at 0% vs 100%) — https://www.nature.com/articles/s41598-024-51921-y
- BMWSB. Hitzeschutz – Eine Handlungsstrategie für die Stadtentwicklung und das Bauwesen (2025) — https://www.bmwsb.bund.de/SharedDocs/downloads/DE/publikationen/stadtentwicklung/hitzeschutzstrategie.pdf (full PDF parsed locally; 30%-canopy–mortality sentence with Lancet/Jan 2023 citation confirmed)
- BGL/"Grün in die Stadt" press release (14 Aug 2025), "bis zu 15 Grad" felt-temperature claim — https://www.presseportal.de/pm/117960/6096923
- SZ Sonderausgabe, "Wie die 3-30-300-Regel Städte widerstandsfähiger macht" (names Malmö, Utrecht, Essen, Munich) — https://www.sueddeutsche.de/sonderthemen/bayern/wie-die-3-30-300-regel-staedte-widerstandsfaehiger-macht-257148
- IÖW/TUM Steckbrief "Bäume als Hitzeschutz. Strategisch pflanzen und Bestand erhalten" (Feder & Welling) — https://www.ioew.de/fileadmin/user_upload/BILDER_und_Downloaddateien/Publikationen/2025/Steckbrief__Baeume_als_Hitzeschutz._Strategisch_pflanzen_und_Bestand_erhalten.pdf
- DUH Hitze-Check (≥30% Baumbeschirmung Richtwert; only ~5 of 190+ cities pass) — https://www.duh.de/informieren/natur-und-umwelt-vor-ort/hitzecheck/
- Iungman 30% rationale (established benchmark adopted by cities) — https://environment.ec.europa.eu/news/increasing-tree-coverage-30-european-cities-could-reduce-deaths-linked-urban-heat-island-effect-2023-06-21_en
