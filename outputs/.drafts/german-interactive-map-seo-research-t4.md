# Research Notes T4 — Core Web Vitals 2026 · Caching · E-E-A-T/YMYL (Impressum) · German Local SEO

Context: German static site (static HTML, client-side rendered map, Cloudflare, no analytics) on heat protection ("Hitzeschutz" / heat warnings). Research date: 2026-08-09. Notes only — not the final report. Every claim cites a source number from the Sources section.

---

## Key findings per question

### Q1. Core Web Vitals thresholds 2026 — VERIFIED, unchanged

- Current official thresholds (web.dev, last updated through 2025/2026): **LCP ≤ 2.5 s (good) / > 4.0 s (poor), INP ≤ 200 ms / > 500 ms, CLS ≤ 0.1 / > 0.25**, all evaluated at the **75th percentile** of field page loads [1][2][3].
- Google Search Central doc "Understanding Core Web Vitals and Google search results" (last updated 2025-12-10) confirms the same three metrics and targets [1].
- **INP replaced FID as the responsiveness Core Web Vital on March 12, 2024** (web.dev announcement, verified) [3]. Nothing newer replaced INP.
- No threshold change in 2025/2026 is documented in any primary source found. 2026-specific claims of "INP measurement methodology tightening, CrUX soft-navigation expansion, TTFB promoted as PSI diagnostic" come from **analyst blogs only (secondary, unverified against primary)** [4][5]. The Chrome for Developers soft-navigations doc confirms Chrome is standardizing soft-navigation measurement (APIs shipping around Chrome 151) — a real, primary-verifiable trend, but it does not change thresholds [6].
- CrUX release notes (primary) show ~55.3–56.4% of origins passing all three CWV through mid-2026 — the metric set is stable [7].

### Q2. CWV as a ranking factor — VERIFIED (position, not weight)

- Google (primary): "Core Web Vitals is a set of metrics… This, along with other page experience aspects, **aligns with what our core ranking systems seek to reward**" [1]. Google explicitly documents CWV as used by ranking systems, but "there is **no single page experience signal**" [8][9].
- Since an April 2024 documentation clarification, Google states other page experience aspects (HTTPS, mobile usability, no intrusive interstitials) **do not directly help rankings**; only CWV are directly used [8][9].
- Ranking is evaluated from **field data (CrUX), sitewide, at the 75th percentile**, segmented **mobile vs. desktop** in Search Console's CWV report [2][10].
- John Mueller: CWV "is not going to make your site's rankings jump up" — weight is small; treat as a tie-breaker [11][12]. No confirmed 2025–2026 change in how page experience is weighted; "AI Overviews impact on clicks" is only addressed by third-party studies (DACH local-intent AI Overviews ≈ 10% of queries, self-reported [13]) — no Google-published click data found.

### Q3. HTML caching — not a ranking factor itself; indirect via TTFB→LCP

- **No Google statement found that caching is a ranking factor.** Google (John Mueller, 2017): "we currently don't use TTFB for anything in search/ranking" [14]. TTFB is a *diagnostic*, not a Core Web Vital [15].
- However, web.dev (primary, updated Nov 2025): "high TTFB values add time to the metrics that follow it"; good TTFB ≤ **0.8 s**, poor > 1.8 s [15][16].
- Caching therefore matters *indirectly*: browser/edge caching lowers TTFB → lowers LCP (a Core Web Vital) [15][16] (mechanism = inference drawn from the two primary statements).
- Cloudflare specifics (primary): Browser Cache TTL and Edge Cache TTL settings; Cloudflare honors origin `Cache-Control` unless overridden [17][18]. For static HTML, edge caching the HTML document is exactly the mechanism that removes origin round-trip from TTFB.
- Google's crawling myths page: faster pages → more efficient crawling; speed alone doesn't increase crawl priority for unimportant content [19].

### Q4. E-E-A-T / YMYL for heat-protection content

- YMYL definition (QRG §2.3): content that can affect **health, safety, financial stability, or well-being**. Pre-July-2022 QRG had an explicit **"Health and safety"** category; the 2022 revision reframed YMYL by *types of harm*, including **"YMYL Health or Safety: topics that could harm mental, physical, and emotional health or any form of safety"** [20][21][22].
- Heat protection / heat warnings = health-and-safety adjacent content: DWD (primary, official) frames Hitzewarnungen explicitly as health protection for vulnerable groups (elderly, chronically ill, children) [23][24]. **Inference (evidence-based):** a site publishing heat-protection advice is treated as YMYL-ish by raters; the QRG itself is a PDF — full text **blocked** (see Blocked section), so exact current wording is via secondary quotes [20].
- E-E-A-T: Experience, Expertise, Authoritativeness, Trust; Trust is "the most important member of the E-E-A-T family"; QRG (via TOC and secondary coverage) requires raters to find "who is responsible for the website" and "About Us, Contact" info — missing ownership info lowers ratings on YMYL pages [25][26][27].
- Practical signals for a small German site (from German SEO practitioners, secondary): author bylines, About page, real contact info, citations to official sources (DWD, Umweltbundesamt), HTTPS, Impressum, Datenschutz [27][28][29]. Google's own "Creating helpful, reliable, people-first content" checklist explicitly asks about clear sourcing and author/site background [30].

### Q5. Impressum under DDG (post-DSA) — VERIFIED (legal facts)

- **TMG was replaced by the Digitale-Dienste-Gesetz (DDG) effective 14 May 2024**; Impressum duty is now **§ 5 DDG** (gesetze-im-internet.de, verified full text) [31][32]. Content requirements are materially unchanged vs. old § 5 TMG (only "Telemedien" → "digitale Dienste"); citing "§ 5 TMG" in a live Impressum is outdated and risks Abmahnungen [32][33][34].
- § 5 (1) DDG required items (verified): name + full address; for legal entities additionally legal form, authorized representatives, share capital info if stated; contact details enabling fast electronic contact incl. **email address**; supervisory authority where relevant; commercial register number; professional-chamber details where relevant; **USt-IdNr / Wirtschafts-ID if held**; liquidation notices for AG/KGaA/GmbH; AVMS info [31].
- Impressum must be "leicht erkennbar und unmittelbar erreichbar" (easily recognizable, directly reachable, e.g., linked from every page, max 2 clicks) [31][34].
- Datenschutzerklärung: DSGVO requirement; references to TTDSG should be updated to **TDDDG** (renamed alongside DDG) [32][35].
- **Is Impressum a ranking factor?** No Google statement found confirming it. Evidence-based position: not a confirmed ranking factor, but part of trust/E-E-A-T signals — Mueller (2015 Hangout) discussed Impressum/AGB from Google's view without calling them ranking factors [36]; Google says trust associations/memberships are not direct ranking factors [37]; Mueller: no such thing as a measurable "trust factor" [38]. German SEO sources likewise treat Impressum as a trust/E-E-A-T signal, not a direct factor [27][28][29][39].

### Q6. German local SEO keywords for heat-protection content

- Third-party keyword data (Performance Suite, free-tier; estimates, **not Google-official**): "hitzeschutzfolie für fenster" (difficulty 38, competition 100); "sonnenschutzfolie aussen fenster" ~1,900; "fenster hitzeschutz folie" ~1,900; "sonnenschutzfolie fenster innen" ~710; "hitzeschutz haare" ~2,900; "thermo plissee" ~2,400; "hitzeschutz fenster innen" ~100 [40][41][42].
- The Performance Suite pages list the same 20 German cities (Berlin, München, Köln, Hamburg…) as ranking-keyword locations — weak but consistent evidence that these head terms attract city-level competition [40].
- City+keyword combos ("Hitzeschutz München") are standard local-SEO practice in German SEO literature: Seokratie (Local SEO factors: proximity, Local Pack, NAP, reviews, local keywords, GBP) [43]; SISTRIX local SEO guide [44]; risk of thin "doorway" city pages documented by Seopt/Seokratie — city pages need real local value or they can harm rankings [45][46].
- Seasonal spike: heat-protection search interest peaks in summer; DWD itself notes the longest heat-warning periods (12 days, June 2026) [24][47]. Implication: content should be pre-published in spring — **inference** from the seasonal pattern noted in sources.
- Local signals without analytics: Google Business Profile (incl. service-area profiles), NAP consistency, local landing pages, Bing Places (Bing 13.2% desktop share in DE, Feb 2025 per StatCounter via secondary source; Bing Places for Business relaunched Oct 2025) [48][49][50].

### Q7. Is "heat protection" a LocalBusiness / local-intent topic in Germany?

- Evidence yes, for the *service* side: window-film / Jalousien / Plissee installers operate as classic **service-area businesses**. Real German examples: "Sonnenschutzfolie & Hitzeschutzfolie in München und Umgebung" (city landing page of a film-installation service) [51]; a Sonnenschutz/Hitzeschutz Fachhändler covering "Raum Schwerte und Dortmund" [52].
- Google explicitly supports **Servicegebiet-Betriebe (service-area businesses)** — Handwerker without a storefront get Local Pack visibility via service-area GBP profiles (secondary, practitioner [53]; supported by Google's own Local Services Ads offering for household services in DE [54][55]).
- German trade press (handwerk magazin) confirms local relevance ("Allgemeine Inhalte ohne regionalen Bezug sind kaum relevant") for Handwerksbetriebe in AI/classic search [56].
- Caveat: "Hitzeschutz" as a head term is mixed-intent (window films, blinds, hair protection, tents) [42] — only the window-film/blind/Jalousie segment is clearly LocalBusiness; informational heat-protection-advice content is separate (YMYL/editorial). **Inference** from the keyword mix observed [40][42].

---

## Practical recommendations (evidence trace)

1. **Keep the CWV target simple**: static HTML + Cloudflare edge caching should aim LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at p75 mobile; the client-side map must not push INP > 200 ms (INP is the metric most sites now fail) [1][2][4].
2. **Cache the HTML document at the edge** (Cloudflare Cache Rules / default static caching) to keep TTFB ≤ 0.8 s — TTFB is not a ranking factor but feeds LCP [14][15][17][18].
3. **Publish Impressum per § 5 DDG** (name, address, email, register/USt-IdNr as applicable), link it from every page, and ensure Datenschutzerklärung references TDDDG not TTDSG — legal compliance first, trust signal second [31][32][34].
4. **Build E-E-A-T**: author bylines + About page + citations to DWD (hitzewarnungen.de) and Umweltbundesamt; treat heat-advice pages as health/safety YMYL [23][25][30][47].
5. **Local SEO without analytics**: GBP with service-area setup, NAP consistency, city pages with real local content (avoid doorway pages), Bing Places profile [43][45][48][50][53].
6. **Keyword direction**: target "Hitzeschutzfolie Fenster", "Sonnenschutzfolie", "Hitzeschutz Fenster", "Jalousien/Plissee Hitzeschutz", plus city combos; publish before summer season [40][42][47].

---

## Sources

1. Google Search Central — Understanding Core Web Vitals and Google search results — https://developers.google.com/search/docs/appearance/core-web-vitals
2. web.dev — Web Vitals — https://web.dev/articles/vitals
3. web.dev — Interaction to Next Paint becomes a Core Web Vital on March 12 — https://web.dev/blog/inp-cwv-march-12
4. WebVitals.tools — Core Web Vitals Update 2026 (analyst) — https://webvitals.tools/blog/google-core-web-vitals-update-2026/
5. MonsterMegs — Core Web Vitals Update Explained For 2026 (analyst) — https://monstermegs.com/blog/core-web-vitals-update/
6. Chrome for Developers — Measuring soft navigations — https://developer.chrome.com/docs/web-platform/soft-navigations
7. Chrome for Developers — CrUX Release notes — https://developer.chrome.com/docs/crux/release-notes
8. Search Engine Roundtable — Google Clarifies Page Experience & Core Web Vitals Document — https://www.seroundtable.com/google-clarifies-page-experience-core-web-vitals-37046.html
9. Search Engine Journal — Google Now Says Core Web Vitals Used In Ranking Systems — https://www.searchenginejournal.com/core-web-vitals-google-ranking-systems/511020/
10. Google Search Console Help — Core Web Vitals report — https://support.google.com/webmasters/answer/9205520
11. Search Engine Roundtable — Google: "it's not going to make your site's rankings jump up" (Mueller LinkedIn coverage) — https://www.seroundtable.com/google-clarifies-page-experience-core-web-vitals-37046.html
12. DebugBear — Are Core Web Vitals A Ranking Factor for SEO? — https://www.debugbear.com/docs/core-web-vitals-ranking-factor
13. OpenLens — Google AI-Übersichten in DACH 2026 (self-reported study) — https://openlens.com/blog/de/google-ai-overviews-local-business-2026
14. Search Engine Roundtable — Google Does Not Use Time To First Byte For Search Rankings (2017) — https://www.seroundtable.com/google-time-to-first-byte-24847.html
15. web.dev — Time to First Byte (TTFB) — https://web.dev/articles/ttfb
16. web.dev — Optimize Time to First Byte — https://web.dev/articles/optimize-ttfb
17. Cloudflare Docs — Set Browser Cache TTL — https://developers.cloudflare.com/cache/how-to/edge-browser-cache-ttl/set-browser-ttl/
18. Cloudflare Docs — Origin Cache Control — https://developers.cloudflare.com/cache/concepts/cache-control/
19. Google for Developers — Myths and facts about crawling — https://developers.google.com/crawling/docs/myths-about-crawling
20. PriceWeber — Is Your Website YMYL? (quotes QRG §2.3) — https://priceweber.com/blog/understanding-googles-ymyl-guidelines/
21. Search Engine Journal — Quality Raters Guidelines Update 9/2019 — https://www.searchenginejournal.com/google-quality-raters-guidelines-update-9-6-2019/324813/
22. Marie Haynes — The July 2022 QRG update — https://www.mariehaynes.com/july-2022-qrg-update/
23. Deutscher Wetterdienst — Hitzewarnung (official) — https://www.dwd.de/DE/leistungen/hitzewarnung/hitzewarnung.html
24. Deutscher Wetterdienst — Presse 25.06.2026 (longest early heat-warning period) — https://www.dwd.de/DE/presse/pressemitteilungen/DE/2026/20260625_dwd-warnt-ueber-langen-zeitraum-vor-hitze_news.html
25. Semrush — Google E-E-A-T: What it is & how it affects SEO — https://www.semrush.com/blog/eeat/
26. Search Engine Journal — Google: About Us & Contact Pages Not Important? — https://www.searchenginejournal.com/google-about-us-contact-pages-not-important/512241/
27. INVENTIVO — E-E-A-T SEO konkret umsetzen: Praxis-Guide für KMU — https://www.inventivo.de/blog/seo/e-e-a-t-konkret-umsetzen
28. SE Ranking (DE) — E-E-A-T und YMYL — https://seranking.com/de/blog/google-eeat-ymyl/
29. Rankingmax — E-E-A-T Check: Trust-Signale — https://www.rankingmax.de/e-e-a-t-tool/
30. Google Search Central — Creating Helpful, Reliable, People-First Content — https://developers.google.com/search/docs/fundamentals/creating-helpful-content
31. gesetze-im-internet.de — § 5 DDG (Einzelnorm, verified) — https://www.gesetze-im-internet.de/ddg/__5.html
32. IHK Osnabrück — Handlungsbedarf: DDG ersetzt TMG — https://www.ihk.de/osnabrueck/recht-und-fair-play/aktuelles/ddg-ersetzt-das-tmg-6220008
33. Bundesarchitektenkammer — TMG heißt jetzt DDG - Impressum überprüfen — https://bak.de/tmg-heisst-jetzt-ddg-impressum-ueberpruefen/
34. IHK Koblenz — Impressum: Was muss beachtet werden? — https://www.ihk.de/koblenz/unternehmensservice/recht/rechtsauskuenfte-von-a-z/it-recht/merkblatt-impressum-3462798
35. BMJV — FAQ Impressumspflicht (DDG in Kraft 14.05.2024) — https://www.bmjv.de/SharedDocs/FAQ/DE/FAQ_Database/Onlineplattformen_Schutzregelungen/FAQ-Onlineplattformen_Schutzregelungen-008.html
36. SEO-Portal.de — Google Webmaster Hangout 24.02.2015 (Impressum/AGB topic) — https://www.seo-portal.de/wissenswertes/google-webmaster-hangouts/google-webmaster-hangout-24-02-2015/
37. Search Engine Roundtable — Google: Trust Associations & Memberships Not Direct Ranking Factors — https://www.seroundtable.com/google-trust-associations-memberships-26687.html
38. Search Engine Journal — Does Content or Links Improve Trust with Google? — https://www.searchenginejournal.com/trust-metrics-and-google/424679/
39. Digital Ultras — E-E-A-T: Google Ranking-Faktor 2026 — https://www.digital-ultras.com/offpage-optimierung-grundlagen/eeat-google-ranking/
40. Performance Suite — Keyword "Hitzeschutz fenster innen" — https://www.performance-suite.io/keyword-db/de-de/hitzeschutz-fenster-innen/
41. Performance Suite — Keyword "Hitzeschutzfolie für fenster" — https://www.performance-suite.io/keyword-db/de-de/hitzeschutzfolie-f%C3%BCr-fenster/
42. Performance Suite — Keyword "Dachfenster folieren" (related keyword table) — https://www.performance-suite.io/keyword-db/de-de/dachfenster-folieren/
43. Seokratie — Local SEO: So funktioniert lokale Suchmaschinenoptimierung — https://www.seokratie.de/local-seo-fuer-fortgeschrittene/
44. SISTRIX — Local SEO: Mehr Sichtbarkeit in der Region — https://www.sistrix.de/frag-sistrix/seo-grundlagen/local-seo/
45. SEOPT — Local SEO Landing Pages: Ja oder nein? — https://www.seopt.de/local-seo-landingpages/
46. getSichtbar — Lokale Landing Pages für AI-Sichtbarkeit — https://www.getsichtbar.com/blog/lokale-landing-pages-ai-sichtbarkeit
47. DWD — Thema des Tages: Wann gibt es Hitzewarnungen und warum? — https://www.dwd.de/DE/wetter/thema_des_tages/2026/6/17.html
48. getSichtbar — Bing Copilot & AI-Sichtbarkeit (StatCounter DE desktop share Feb 2025) — https://www.getsichtbar.com/blog/bing-copilot-ai-sichtbarkeit
49. Bing — Bing Places for Business — https://www.bing.com/forbusiness/
50. KI-Q — Local AI Visibility 2026: Bing Places und IndexNow — https://ki-q.de/blog/news/local-ai-visibility-bing-places-indexnow/
51. Folienservice Bayern — Sonnenschutzfolie & Hitzeschutzfolie in München und Umgebung — https://folienservice-bayern.de/produkte/sonnenschutzfolie/
52. eS-FOL — Sonnenschutz und Sichtschutz im Raum Schwerte und Dortmund — https://www.esfol.de/
53. Anika Wachter — Google Business Profile für Handwerker ohne Ladenlokal (Servicegebiet-Betrieb) — https://anikawachter.de/google-business-profile-ohne-ladenlokal-handwerker
54. Google Business — Google Lokale Dienstleistungen (Local Services Ads DE) — https://business.google.com/de/ad-solutions/local-service-ads/
55. Google Local Services Help — Google Lokale Dienstleistungen im Überblick — https://support.google.com/localservices/answer/6224841
56. handwerk magazin — SEO für KI / GEO für Handwerksbetriebe — https://www.handwerk-magazin.de/kuenstliche-intelligenz-bei-der-suche-was-chatgpt-perplexity-co-fuer-die-digitale-sichtbarkeit-von-betrieben-bedeuten-337473/
57. DWD — Hitzewarnsystem (official) — https://www.hitzewarnungen.de/
58. Search Engine Land — Google updates search quality raters guidelines (AI Overview examples, YMYL definitions, Sept 2025) — https://searchengineland.com/google-updates-search-quality-raters-guidelines-adding-ai-overview-examples-ymyl-definitions-461908

---

## Search queries used (web search)

1. Core Web Vitals thresholds 2026 LCP INP CLS
2. Core Web Vitals ranking factor page experience Google 2025
3. Google TTFB 0.8 seconds caching ranking factor Chrome team
4. YMYL health safety Google quality rater guidelines E-E-A-T
5. Impressum Pflichtangaben DDG §5 Digitale-Dienste-Gesetz 2024
6. Impressum TMG DDG Übergang Pflichtangaben Anbieterkennzeichnung
7. Hitzeschutz lokale Suchanfragen Suchvolumen Deutschland SEO
8. Google Business Profile lokale Suchanfragen Handwerker Fensterfolie Jalousien
9. Core Web Vitals changes 2025 2026 INP measurement CrUX methodology update
10. browser caching edge caching HTML ranking factor Google SEO Cloudflare
11. Google quality rater guidelines health and safety YMYL category heat warning
12. Impressum Vertrauen Rankingfaktor Google E-E-A-T deutsche Website SEO
13. Hitzewarnung DWD Suchvolumen Google Trends Sommer
14. SISTRIX lokale Suche Keywords Stadt Suchanfragen lokal SEO 2025
15. Hitzeschutzfolie Fenster Jalousien lokale Dienstleistung SEO SISTRIX Ryte
16. Sonnenschutz Jalousien lokale Suche Google lokale Dienstleistung Suchanfragen
17. John Mueller Impressum ranking factor Google statement trust
18. Bing Places Deutschland lokale Einträge Handwerker SEO
19. Ryte Seokratie lokale SEO Servicedienstleister Stadtseiten Fallstricke
20. "Hitzeschutz" Suchvolumen Keyword Volumen Deutschland
21. "quality rater guidelines" "health and safety" YMYL section 2.3 quote
22. John Mueller Impressum "ranking factor" OR "not used for ranking" quote English Google
23. "Hitzeschutz" Google Trends Saisonalität Sommer Suchanfragen Spitze
24. Google ranking factor 2025 2026 page experience signal list confirmed

---

## Blocked / unverified items

- **Google Search Quality Rater Guidelines full text: BLOCKED (PDF).** The guidelines exist only as PDFs (guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf; services.google.com/fh/files/misc/hsw-sqrg.pdf; ppc.land copy). Per instructions no PDFs were fetched. Exact current §2.3 wording therefore relies on secondary quotes [20] + Search Engine Land's Sept 2025 update summary [58]. RaterHub PDF URL is cited but full text not read.
- **"2026 INP methodology tightening / TTFB promoted in PSI"**: UNVERIFIED against primary; only analyst blogs [4][5]. Primary Chrome sources confirm soft-navigation standardization [6] but no primary statement about INP measurement changes was found.
- **Search volume numbers**: third-party estimates (Performance Suite) [40][41][42]; Google Keyword Planner / SISTRIX keyword DB not directly queried (no credentials). Exact volumes may differ.
- **Omnity/Searchmetrics and OnlineMarketing.de German SEO articles**: not directly located/read; SISTRIX [44], Seokratie [43], SEOPT [45], getSichtbar [46] used instead.
- **AI Overviews click-share impact**: no Google-published data; only self-reported third-party study [13].
- **StatCounter 13.2% Bing desktop share DE**: cited via secondary blog [48]; StatCounter page itself not fetched.

## Coverage status

- Q1 (CWV thresholds): done, primary-verified. Q2 (ranking status): done, primary + press. Q3 (caching): done. Q4 (E-E-A-T/YMYL): done (QRG full text blocked). Q5 (Impressum/DDG): done, primary-verified. Q6 (German local keywords): done, third-party estimates flagged. Q7 (LocalBusiness topic): done, evidence + inference labeled.
- Tasks not completed: none outstanding; QRG PDF and keyword-tool verification are the only gaps (marked above).
