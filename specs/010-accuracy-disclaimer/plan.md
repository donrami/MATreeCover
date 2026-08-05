# Implementation Plan: Accuracy Disclaimer on the Site

**Branch**: `010-accuracy-disclaimer` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

## Summary

One static HTML section on the attribution page (`src/site/attribution.html`): a German disclaimer stating the tree-cover values are automated estimates from aerial imagery, detection is imperfect, and the values are indicative — no district names, no site architecture change. The deployed copy (`dist-assets/attribution.html`) is synced. The map data stays at the 0.5 threshold (009 decision, recorded in `verification/report.md`).

## Technical Context

**Language/Version**: Vanilla HTML (German, `lang="de"`), dark theme matching the existing attribution page. No JS, no build step, no dependencies.

**Testing**: Mechanical checks only (this is static content): no district names, no em/en-dashes, section present; existing pytest suites untouched (no pipeline/data change); `make check-public` clean.

**Constraints**: CSP `script-src 'self'` (pure HTML is fine); site copy convention (no em/en-dash, hyphens only in compounds — same bar as 007); FR-004 zero district names; FR-005 no map/legend/value/tree-layer changes.

## Constitution Check

No constitution file; gates from repo governance + spec: FR-005/FR-006 (no map or network changes — one static HTML file), FR-010 (`check-public` clean — new content is public-safe), OR-004 (one commit per slice).

## Structure

```text
src/site/attribution.html    # + "Genauigkeit der Baumwerte" section (the only source change)
dist-assets/attribution.html # synced deployed copy
specs/010-accuracy-disclaimer/{spec,plan,tasks}.md
```

## Complexity Tracking

None — a single static text section; no abstractions, no new files beyond the spec docs.
