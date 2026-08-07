# CHANGELOG

## 2026-08-08 — popup comparative context (013)
- Building popup: headline tree-share value ("Baumanteil im 60-m-Umkreis"), 30 % threshold badge ("erreicht"/"verfehlt"), district and city comparison lines with signed pp delta and assessment word, metric footnote.
- District popup: name header, mean headline, rank "Platz X von 38", quartile band badge, city comparison, existing building-count and below-30 % lines kept, metric footnote.
- Rank/quartile computed client-side once at map load from the full 38-district set with deterministic tie-break; graceful degradation when data is missing (building without value, district without mean, stale city stats).
- Visual hierarchy header → headline → badge → context → footnote, color always paired with a text label, mobile fit via internal scroll and width clamp at 360 px. Interaction model unchanged (FR-015).

## 2026-08-06 — tree-canopy-30-heat literature review
- Wrote plan to outputs/.plans/tree-canopy-30-heat.md.
- Verified primary sources: Konijnendijk 2023 (3-30-300; 30% rests on Astell-Burt & Feng health evidence, Ziter 40% cited for heat), NGBS ICC 700-2020 (≥30% building-wall shading, primary PDF), Ziter 2019 PNAS (≥40% threshold), Iungman 2023 Lancet (30% target → 0.4°C, 2644 deaths), Ouyang 2020 (20–30% efficiency optimum), Li 2023 Nanjing (25–45% by building height), Ettinger 2024 (no threshold), Krayenhoff 2021 (0.3°C/10%), Zaerpour 2025 (SUHI 2× overestimate; −1.5°C at +30%).
- Researcher subagent brief: outputs/tree-canopy-30-heat-research-1.md (39 items; low-confidence items excluded from final).
- Draft: outputs/tree-canopy-30-heat.md; chart: outputs/tree-canopy-30-heat-cooling.png.
- Next: verifier pass on citations/URLs, reviewer pass, provenance file.
- 2026-08-06: verifier + reviewer passes done (0 dead URLs, 0 FATAL). Fixed: BMWSB Hitzeschutzstrategie 2025 adopts Iungman 30% (German lineage added), Astell-Burt graded-gradient nuance, Venter 6-fold SUHI, Kalkstein scenario bounds, EU NRL wording, NGBS credit framing, provenance file created. Final artifacts verified on disk.
