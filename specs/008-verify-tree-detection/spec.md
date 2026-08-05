# Feature Specification: Verify Tree Detection Quality

**Feature Branch**: `008-verify-tree-detection`
**Created**: 2026-08-05
**Status**: Draft
**Input**: User description: "we need to check the verifiability" — in the context of a discussion about how well the tree-detection model (trained on Erlangen imagery, reused unchanged) detects trees on Mannheim DOP20 imagery. The model author reports that his own cross-city transfer test (Erlangen → Bamberg) was significantly worse, citing lower image contrast, different sun angle, and few training data. The map's per-building tree-cover values rest on that detection, so we need verifiable evidence of how well the detection works in Mannheim before the published numbers can be trusted.

## Clarifications

### Session 2026-08-05

- Q: What is the detection measured against? → A: Structured visual inspection (Q1, option C). Sampled patches are reviewed with the production tree layer overlaid on the Mannheim orthophotos; each patch is rated against documented criteria. Findings are qualitative ratings with notes; no numeric precision/recall metrics are computed.
- Q: Where do the results live? → A: Repository report only (Q2, option A). The published site is not changed: no transparency note, no verification page.
- Q: What happens if detection quality is poor? → A: No threshold and no gating (Q3, option A). The feature delivers the report; any map changes or disclaimers are separate follow-up decisions after the owner reviews the findings.

## Scope

### Goal

Verifiable evidence of how well the reused tree-detection model recognizes trees on Mannheim aerial imagery — the basis of every building value on the published map. The evidence is produced by a structured visual inspection: a documented sample of imagery patches, reviewed with the detected-tree layer overlaid, rated against fixed criteria, summarized per district, and written up so a reviewer can repeat the inspection from the report alone.

### In Scope

- A documented, reproducible sample of Mannheim aerial-imagery patches, covering all districts with buildings in proportion to the city.
- A structured visual inspection of each sampled patch with the production tree layer overlaid on the aerial imagery: a rating per patch against documented criteria (detection correct / over-detection / under-detection) plus a note.
- A per-district summary of findings, flagging districts where detection looks unreliable.
- A written verification report in the repository: date, method, sample design, inspection criteria, per-patch ratings, per-district findings, comparison with the model author's cross-city warning, limitations.
- The check reviews the model output and imagery exactly as used for the published map; nothing is re-run or changed.

### Out of Scope

- Numeric detection metrics computed against labeled ground truth (precision, recall, agreement) — visual inspection chosen instead (Q1).
- Retraining, fine-tuning, or replacing the model.
- Re-running inference on Mannheim imagery or changing any published map data, building values, tree layer, or legend.
- Changing the detection threshold or any other inference setting used for the published map.
- Any change to the published site (transparency note or verification page) — repository report only (Q2).
- Pass/fail gating of the published map or remediation of weak districts — decided separately after the owner reviews the findings (Q3).
- Automated, continuous re-verification over time.
- Any new tracking, accounts, or server-side infrastructure; the site stays static.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Owner Carries Out a Structured Visual Inspection (Priority: P1)

The owner selects a documented sample of Mannheim imagery patches, opens each one with the detected-tree layer overlaid on the aerial photo, and rates what is visible: does the detection match the trees on the ground, does it flag things that are not trees, does it miss real canopy? The ratings and notes are recorded and written up in a report.

**Why priority**: This is the entire feature. The published map's credibility rests on detection quality, and the model author's own cross-city test warns that transfer can be poor. The inspection is the verifiable evidence.

**Independent Test**: Carry out the inspection end to end on the documented sample. Every sampled patch has a recorded rating and note, and the report summarizes the findings.

**Acceptance Scenarios**:

1. **Given** the production tree layer and the Mannheim orthophotos, **When** the owner carries out the inspection, **Then** each sampled patch receives a rating against the documented criteria and a note.
2. **Given** the inspection sample, **When** the owner opens a patch, **Then** the detected-tree layer is shown over the aerial imagery of the same area — the same visual comparison the map's Bäume toggle offers.
3. **Given** the inspection is complete, **When** the owner reads the report, **Then** it documents the sample size, how the sample was chosen, the inspection criteria, and the limitations, so a reviewer can repeat the inspection from the report alone.
4. **Given** the inspection is complete, **When** the owner re-checks a subset of the patches, **Then** the ratings match the recorded ones, or the divergence is documented.

### User Story 2 - Owner Sees Findings Per District (Priority: P1)

The Reddit discussion highlighted extreme differences between Mannheim districts — from leafy residential areas to almost treeless industrial zones. The owner needs to know whether those extremes reflect reality or are artifacts of weak detection in some image conditions.

**Why priority**: District differences are the map's most striking message. If the differences are partly detection artifacts, the map misleads; the inspection separates signal from artifact as far as visual review allows.

**Independent Test**: Complete the inspection with per-district reporting. Every district with buildings appears in the findings with its own sample size, and districts where detection looks unreliable are flagged.

**Acceptance Scenarios**:

1. **Given** the inspection sample covers the city, **When** the owner views the findings, **Then** every district with buildings appears with its own findings and sample size.
2. **Given** the district findings, **When** detection in a district looks unreliable, **Then** the report flags that district explicitly.
3. **Given** a flagged district, **When** the owner reads the report, **Then** the report states whether the district's map values are trustworthy, overstated, or understated, as far as the inspection allows.
4. **Given** the inspection sample, **When** the owner reviews how the sample was chosen, **Then** the selection is documented and covers districts in proportion to the city, not a convenience sample.

### User Story 3 - Owner Keeps the Findings in the Repository (Priority: P2)

The verification results live in the project repository as a readable report. The owner can point to it when asked how well the map's values were checked; the public site stays exactly as it is.

**Why priority**: "Verifiability" means the claim is backed by evidence anyone can inspect. The repository report is that evidence, and keeping the site untouched preserves the small, quiet character of the project (Q2).

**Independent Test**: Locate the report in the repository, read it, and confirm the published site is unchanged.

**Acceptance Scenarios**:

1. **Given** the inspection is complete, **When** the owner looks for the results, **Then** the report lives in the project repository, is readable, and names its own date, method, and findings.
2. **Given** the report exists, **When** the owner opens the published map page, **Then** nothing on the site has changed: no transparency note, no verification page, no new requests.
3. **Given** the report exists, **When** the owner reads it, **Then** it contains the inspection findings and the comparison with the model author's cross-city warning.

### Edge Cases

- Degenerate predictions: patches where the tree layer is empty or covers everything must be noted and disclosed, not silently excluded.
- Small districts: districts with very few buildings get few sample patches; the report must state that their findings are not conclusive.
- Sample coverage: districts with no imagery or no buildings are listed as such, not omitted silently.
- Boundary/halo areas: imagery near the city edge may include areas outside Mannheim; the report defines what counts as "in Mannheim" for sampling.
- Inspection uncertainty: judging ambiguous imagery (shadows, low contrast — the exact condition the model author warned about) is a single-inspector judgment; the report states this as a limitation.
- Re-inspection divergence: if a re-check of a subset does not reproduce the ratings, the report documents the divergence rather than reporting only the first pass.
- Reference comparison unavailable: if the model author's cross-city numbers are not published, the comparison is qualitative and named as such.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The verification MUST inspect a documented, randomly selected sample of Mannheim aerial-imagery patches, using the production tree layer and the underlying orthophotos exactly as used for the published map.
- **FR-002**: Each sampled patch MUST be rated against documented criteria — detection correct, over-detection, or under-detection — with a note recording what was seen.
- **FR-003**: The inspection MUST produce findings per district, with each district's sample size stated; districts whose detection looks unreliable MUST be flagged.
- **FR-004**: The sample selection MUST be reproducible (documented selection rule and fixed seed) and MUST cover all districts with buildings, in proportion to their share of the city.
- **FR-005**: The verification MUST NOT re-train the model, MUST NOT re-run inference, and MUST NOT change any published map data, building values, tree layer, or legend.
- **FR-006**: The findings MUST be delivered as a written report in the repository: date, method, sample design, inspection criteria, per-patch ratings, per-district findings, and limitations, sufficient for a reviewer to repeat the inspection.
- **FR-007**: The report MUST document the comparison with the model author's reported cross-city transfer problem (Erlangen-trained model on unfamiliar cities), qualitative if comparable numbers are not published.
- **FR-008**: The report MUST disclose degenerate predictions, small-sample districts, boundary areas, inspection uncertainty, and any re-inspection divergence instead of excluding or hiding them.
- **FR-009**: The verification MUST NOT gate or change the published map based on its findings; the findings and any recommended follow-up are recorded in the report for the owner to decide separately.
- **FR-010**: The verification MUST NOT change the published site in any way; the results live exclusively in the repository report.

### Key Entities *(include if feature involves data)*

- **Verification Sample**: the set of aerial-imagery patches selected for inspection; defined by its selection rule, stratification (by district), size, and seed. The unit everything is measured on.
- **Inspection Criteria**: the documented rating definitions (detection correct, over-detection, under-detection) and the rules for applying them to a patch.
- **Inspection Findings**: the per-patch ratings and notes plus the per-district summary, including flagged districts.
- **Verification Report**: the written deliverable in the repository — date, method, sample design, inspection criteria, findings, comparison with the reference transfer problem, and limitations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The inspection covers a documented sample spanning every district with buildings, in proportion to the city.
- **SC-002**: Every sampled patch has a recorded rating and note; the report summarizes the ratings across the sample.
- **SC-003**: The report documents sample size, selection rule, inspection criteria, and limitations; a reviewer who reads only the report can repeat the inspection.
- **SC-004**: Every district with buildings appears in the findings with its own sample size; districts where detection looks unreliable are flagged.
- **SC-005**: The report explicitly states whether the extreme differences between districts reflect real tree-cover differences or detection artifacts, within the limits of visual inspection.
- **SC-006**: Zero changes to published map data, building values, tree layer, legend, site pages, or controls; existing smoke checks pass unchanged.
- **SC-007**: The comparison with the model author's cross-city transfer warning is documented in the report (qualitative, since no comparable numbers are published).
- **SC-008**: The report discloses degenerate predictions, small samples, boundary areas, inspection uncertainty, and any re-inspection divergence.

## Assumptions

- Evidence first: this feature delivers the inspection and its report, not remediation. Any map changes or disclaimers are separate follow-up decisions (Q3).
- Ground truth is a structured visual inspection by the project owner as single inspector (Q1). Findings are qualitative ratings with notes; no numeric precision/recall metrics are computed.
- The check uses the production result as-is: the reused Erlangen-trained model, the published inference settings (1024-pixel patches, 64-pixel overlap, 0.5 detection threshold), the published tree layer, and the Mannheim DOP20 orthophotos.
- The inspection sample targets on the order of 100 patches, finalized in planning, stratified by district and by tree-cover value range.
- The inspection runs without a GPU; it reviews existing artifacts (orthophotos and the published tree layer).
- The model author's Erlangen → Bamberg transfer numbers are not published; the comparison is qualitative.
- The published site is untouched (Q2): no transparency note, no verification page, no new requests, no tracking.
- The verification is a one-time check, not a recurring process.

## Dependencies Evidence

- Detection model: the reused CityTreeCover weights (DeepLabV3+, trained by Jakob Schultz on Erlangen aerial imagery), stored at `data/archive/mannheim-project/models/best_deeplabv3plus.pth`; reference project: https://github.com/jcscaptures/CityTreeCover (MIT, credited in repo LICENSE).
- Production inference settings as stated in the motivating discussion and specs/001: 1024-pixel patches, 64-pixel overlap, 0.5 detection threshold, run on RunPod against Mannheim DOP20 orthophotos (20 cm resolution).
- The published tree layer is the same visual comparison the map page's Bäume toggle offers: detected trees over aerial imagery.
- Pipeline and artifacts that can feed the inspection: `src/pipeline/` (canopy, trees, values, publish); validation events recorded in `validation/event.log.jsonl`.
- Published map: https://abu-hamad.de/map/ (static, no build, strict Content-Security-Policy `script-src 'self'`); site sources in `src/site/`.
- Repository: https://github.com/donrami/MATreeCover (public). Existing smoke tests in `tests/` and `acceptance/` must remain green (SC-006).
- Motivating risk: the model author reports his own cross-city test (Erlangen-trained weights on Bamberg DOP20) was significantly worse — lower contrast, different sun angle, few training data — which is the explicit reason verifiability must be checked for Mannheim.
