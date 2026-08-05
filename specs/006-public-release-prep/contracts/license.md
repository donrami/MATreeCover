# Contract: License and Credits

Targets: `LICENSE` (new, repo root), README credits + license sections, `src/site/attribution.html` (alignment). Requirement sources: FR-004, FR-005, FR-006, FR-007, FR-011; SC-002, SC-005, SC-007. Legal grounding: research in `research.md` (section B), full citations in `local://ref-license.md`.

## 1. Project license file (`LICENSE`)

- Standard MIT License text (SPDX `MIT`).
- Copyright line: `Copyright (c) 2026 <owner>`. Default holder: the owner's GitHub handle `donrami`; confirm the exact name at implementation time.
- **Reference notice preservation (mandatory)**: the MIT terms require the reference copyright and permission notice to be included in copies. Append to `LICENSE`:

  ```text
  Portions of this project reproduce CityTreeCover
  (https://github.com/jcscaptures/CityTreeCover).
  Copyright (c) 2026 Jakob Schultz
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
  [remaining MIT permission text verbatim]
  ```

- README license section must state "MIT" and link `./LICENSE` (FR-006); the statement and the file must agree (FR-007, SC-005).

## 2. Reference project credit (README credits section, FR-004)

Must appear in the README credits section, exactly this information:

- Name: **CityTreeCover**
- Link: `https://github.com/jcscaptures/CityTreeCover`
- License: MIT
- One sentence on the relationship: this map reproduces CityTreeCover's presentation for Mannheim.
- No claims beyond the verified facts in `research.md` (e.g. do not state the reference has a LICENSE file — it does not; the notice is preserved per its README-declared MIT terms).

## 3. Data source credits (README + in-app, FR-005)

Required credit strings (verified against official sources in `research.md`):

| Provider | Credit string | Required links |
|----------|---------------|----------------|
| LGL (buildings, boundary) | `Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0` | `https://www.govdata.de/dl-de/by-2-0` (license text) |
| basemap.de (base map) | `© GeoBasis-DE / BKG (2026) dl-de/by-2-0` — with `(Daten verändert)` appended where derived data was modified | `https://www.bkg.bund.de` (source note), `https://www.govdata.de/dl-de/by-2-0` (license) |

- Both strings satisfy dl-de/by-2-0 §2: provider name, license annotation (`dl-de/by-2-0`), license-text reference.
- README credits and `src/site/attribution.html` must name the same providers and reference project (FR-011, SC-007).

## 4. In-app attribution alignment (`src/site/attribution.html`)

- Current state (verified): lists LGL with `dl-de/by-2-0`, basemap.de, and CityTreeCover (MIT).
- Change: replace the bare `basemap.de` entry with the official credit string `© GeoBasis-DE / BKG (Jahr des letzten Datenbezugs) dl-de/by-2-0` with the govdata link. Keep the LGL line and the CityTreeCover line unchanged.
- The attribution panel must keep working in the German UI (text stays German, matching the app).

## 5. Consistency checks

- `grep -F "CityTreeCover" README.md` and `grep -F "CityTreeCover" src/site/attribution.html` both match (FR-011).
- `grep -F "dl-de/by-2-0" README.md src/site/attribution.html` both match (FR-005).
- `grep -i "MIT" LICENSE` and README license statement agree (SC-005).
- LICENSE copyright lines present: project owner + `Jakob Schultz`.
