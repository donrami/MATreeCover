---
description: "Task list for accuracy-disclaimer feature"
---

# Tasks: Accuracy Disclaimer on the Site

**Input**: Design documents `specs/010-accuracy-disclaimer/`
**Prerequisites**: plan.md, spec.md

- [ ] T001 Add the "Genauigkeit der Baumwerte" section to `src/site/attribution.html` (German; states: values are automated estimates from aerial imagery; detection imperfect — non-tree surfaces can count as tree cover, some trees can be missed; values are indicative, not exact measurement; no district names; no em/en-dash)
- [ ] T002 Sync the deployed copy `dist-assets/attribution.html` from the source
- [ ] T003 Verify: section present, zero district names, zero em/en-dashes (mechanical grep), full pytest suite green, `make check-public` clean, no other site file changed
- [ ] T004 Commit per OR-004 (spec/plan/tasks + slice)
