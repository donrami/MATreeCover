# Evidence: Story Wording Approved (T006)

**Feature**: First-Visit Story Modal
**Task**: T006, final story wording approval (merge gate, FR-015)
**Date**: 2026-08-05
**Status**: APPROVED

## Decision

The user approved the German story copy in
`specs/007-first-visit-story/contracts/story-content.md`.

T003 must implement that copy verbatim in `src/site/index.html`.

No further approval is required at merge time.

## FR-015 mechanical gates (run 2026-08-05)

- Em-dashes: 0. Pass.
- En-dashes: 0. Pass.
- Hyphens only inside compounds. Pass. Compounds: `60-m-Umkreis`,
  `60-m-Umkreises`, `SPIEGEL-Artikel`.
- Required elements FR-002 and FR-003 present. Pass. Map origin,
  heatwave context, central value, both links.
- Story length: 131 words. Pass, short story.

## Link text convention

The SPIEGEL link text is the article title. It is "Hitze in Europa:
Wie gut Stadtbäume vor extremer Wärme schützen". This follows required
element 2 in the contract and tasks T003 and T010. The string `[Zum
SPIEGEL-Artikel]` in the normative copy block is schematic shorthand.
It is not the literal link text.

## Constraint

Any phrasing deviation from the approved copy voids this approval.
The user must re-approve before merge.
