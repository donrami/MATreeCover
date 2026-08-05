# Contract: Story Content (German)

**Feature**: First-Visit Story Modal |
**Branch**: `007-first-visit-story`
**Source of truth**: `src/site/index.html` (static markup).

## Purpose

Fix the modal's German story copy: the four required elements
(FR-002), the central-value sentence (FR-003), and the two working
reference links that open in a new tab (FR-006). Content is static
HTML shipped with the page — never fetched at runtime (FR-011).

## Required elements (FR-002, FR-003)

1. **Map origin**: how the map came to be — the SPIEGEL article,
   the CityTreeCover reference project, and this Mannheim
   replication approach.
2. **SPIEGEL article link**: link text carries the article title
   "Hitze in Europa: Wie gut Stadtbäume vor extremer Wärme schützen".
3. **CityTreeCover link**: link text names the reference project.
4. **Heatwave context**: why tree cover matters in the June/July
   2026 heatwave in Germany.
5. **Central value (FR-003)**: one or two sentences stating that
   buildings are colored by the average tree cover in their 60-m
   surroundings — matching the legend text already on the page
   ("Durchschnittlicher Baumanteil im 60-m-Umkreis").

## Link targets (verified resolving, HTTP 200, 2026-08-05)

| Link | URL | Attributes |
|---|---|---|
| SPIEGEL article | `https://www.spiegel.de/wissenschaft/natur/hitze-in-europa-wie-gut-stadtbaeume-vor-extremer-waerme-schuetzen-a-9a0b26e5-f8ae-4fa5-a897-2f2b026f5226` | `target="_blank" rel="noopener"` |
| CityTreeCover | `https://github.com/jcscaptures/CityTreeCover` | `target="_blank" rel="noopener"` |

Both links open in a new tab; the map tab is never navigated away
(FR-006). `rel="noopener"` prevents the new tab from reaching the
opener.

## Facts and their sources

| Fact | Source |
|---|---|
| City trees measurably protect against extreme heat; streets in many European cities exceed 40 °C; cities have too little green; planting more trees alone is not enough | SPIEGEL article, 2026-07-29 (title, description; verified live) |
| Roughly 30% of the 60-m surroundings should be shaded (Croeser, Rahman & Ghosh, 2026) | CityTreeCover README, citing the SPIEGEL article |
| CityTreeCover emerged from reading the SPIEGEL article and was built during the July 2026 heatwave in Germany | CityTreeCover README |
| This map replicates the approach for Mannheim | Feature spec (map's own origin) |

## Normative copy (German)

> **Wie diese Karte entstanden ist**
>
> Jedes Gebäude ist nach dem durchschnittlichen Baumanteil in seinem
> 60-m-Umkreis eingefärbt: Je grüner, desto mehr Bäume in der
> Umgebung.
>
> Im Juli 2026 berichtete der SPIEGEL, wie gut Stadtbäume vor
> extremer Hitze schützen: Rund 30 Prozent des 60-m-Umkreises sollten
> beschattet sein. Aus der Lektüre entstand das Referenzprojekt
> CityTreeCover, das Gebäude nach dem Baumanteil ihrer Umgebung
> einfärbt. Diese Karte überträgt die Idee auf Mannheim.
>
> Im Juni und Juli 2026 erlebte Deutschland eine Hitzewelle. In
> dicht bebauten Vierteln wird es besonders heiß. Bäume sind der
> natürliche Schatten der Stadt. Diese Karte zeigt, wo Bäume fehlen:
> Rote und orange Gebäude stehen in Umgebungen mit wenig Schatten.
>
> [Zum SPIEGEL-Artikel] · [Zum Referenzprojekt CityTreeCover]

Implementation may adjust phrasing, but must keep every required
element and both link targets; the copy stays short (spec: "short
story") and German.

## Invariants

- Content is static markup inside `index.html`; zero network
  requests (FR-011); no inline scripts (CSP `script-src 'self'`).
- Copy exists only on the map page; `attribution.html` carries no
  modal markup or content (FR-012).
- Links never navigate the map tab away (FR-006).
- Copy quality (FR-015): natural human-sounding German prose, no
  AI-typical phrases, no em-dash (—) or en-dash (–); hyphens only
  inside compounds. Final wording requires user approval.
