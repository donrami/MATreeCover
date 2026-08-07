# Research: Public Release Preparation

Research date: 2026-08-05. Two research streams: (A) repository public-readiness audit, (B) reference-project and data-license attribution requirements. Full evidence: the audit inventory summarized in section A and the license research in section B (full citations recorded in `contracts/license.md`).

## A. Repository audit — current public-readiness state

Audit method: `git ls-files` + `git grep` over tracked files only (127 files); gitignored dirs (`.venv`, `data/`, `dist/`, harness-internal dirs, `mosaic/`) verified not tracked.

### Findings by severity

| Severity | Count | What |
|----------|-------|------|
| high | 13 | Personal absolute workspace paths in `README.md`, `Makefile`, `scripts/check-prereqs.sh`, `scripts/runpod-deploy.sh`, `src/pipeline/workspace.py`, `tests/conftest.py`, `specs/001/quickstart.md`; the original-workspace path in `specs/001/{spec,plan,research,tasks}.md`; absolute input-spec paths in `specs/001/plan.md`, `specs/002/plan.md`; **no LICENSE file tracked** despite README claiming MIT |
| medium | 10 | README RunPod SSH block (SSH key path, personal port, root host placeholder); `scripts/runpod-deploy.sh` same defaults; `workers/map/wrangler.toml` real Cloudflare `zone_id`; `specs/005` owner ops docs with real hosting IPs and DNS records; `scripts/deploy-cf.sh` hardcoded owner-infra gates; harness-internal workflow references in 11 files across `specs/001..006`; unfilled plan template in `specs/006` |
| low | 8 | Loopback ports 8088/8090 in validation records; commit-hash references; `schultz-web.de` reference link; stale branch guard in Makefile bootstrap; `abu-hamad.de` domain (intentional, owner's public deployment) |

### Verified clean

- No PEM blocks, `ghp_*`/`sk-*`/`AKIA*` tokens, or real `.env` values anywhere in tracked files.
- No TODO/FIXME/HACK markers in `src/`, `workers/`, `scripts/`.
- `validation/event.log.jsonl` contains only subcommand/RSS/exit-code rows with relative input names.
- All README links currently resolve (CityTreeCover repo fetched live on 2026-08-05).

### Decisions from audit

1. **Workspace default strategy**: replace the hardcoded absolute default with a repo-root-relative default (`<repo>/data/archive/workspace`), keeping the `MANNHEIM_WORKSPACE` env override. `workspace.py` resolves against its own file location (robust to cwd), `tests/conftest.py` against the existing `REPO_ROOT`. Locally the archived workspace lives at exactly that relative path, so owner behavior is unchanged. Public readers get a neutral, documented path. All references (Makefile, `check-prereqs.sh`, `runpod-deploy.sh`, `specs/001/quickstart.md`) use the same relative default or the env var.
2. **specs/ sanitize, do not exclude** (per spec A-5): `specs/` is valuable provenance (data lineage, acceptance criteria) and stays public, scrubbed: personal paths → relative/env-var wording; harness-internal workflow references → removed or generic wording; `specs/005` owner ops details (IPs, DNS, registrar) → redacted to placeholders, architecture retained. Spec A-4 holds: history is not rewritten.
3. **`wrangler.toml` zone_id**: replace the real zone id with a placeholder; owner deploys with a gitignored local override (`wrangler.local.toml`, `--config`) documented in DEVELOPMENT.md.
4. **Scan gate**: new `scripts/check-public.sh` + `make check-public` target enforces FR-010 (SC-003) with a documented pattern list and zero-finding exit semantics. Runpod defaults (`KEY`, port) switch to env-var/empty placeholders so the gate can be global.
5. **README dev content**: moves verbatim-but-sanitized into a new `DEVELOPMENT.md` (spec FR-009); nothing is lost.
6. **attribution.html alignment**: bring the in-app basemap.de credit up to the official `© GeoBasis-DE / BKG ... dl-de/by-2-0` string (research B) — small, directly in the "credits given" spirit; FR-011 regression check included.

## B. Reference project and data licenses

### CityTreeCover (reference project)

- Name: **CityTreeCover** (README title "City Tree Cover Visualization"); repo `https://github.com/jcscaptures/CityTreeCover` (public, `main`, resolves).
- Purpose: segments tree canopy from 20 cm DOP20 aerial orthophotos (DeepLabV3Plus/ResNet34), computes per-building tree cover within 60 m (Croeser, Rahman & Ghosh 2026), renders a web map.
- License: **MIT**, declared in the reference README; copyright `Copyright (c) 2026 Jakob Schultz`. The reference has no separate LICENSE file, but its MIT notice requires preserving the copyright + permission notice in copies. → Our LICENSE and credits must carry this notice.
- The repo's existing `src/site/attribution.html` already credits "CityTreeCover (MIT-Lizenz)" — retained and cross-checked against the README credits (FR-011).

### dl-de/by-2-0 (LGL data)

Required source-note elements (§2): provider name as specified by the provider; the annotation "Datenlizenz Deutschland – Namensnennung – Version 2.0" or "dl-de/by-2-0" with a reference to the license text at `www.govdata.de/dl-de/by-2-0`; a reference to the dataset URI. Modifications must be marked, e.g. "(Daten verändert)" (§3). No single mandated string; widely used practical form: `Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0`. Official LGL-BW example: `LGL-BW (2024) Datenlizenz Deutschland - Namensnennung - Version 2.0, www.lgl-bw.de`.

### basemap.de (base map)

Default license CC BY 4.0; **dl-de/by-2-0 explicitly permitted as alternative** (official terms, sgx.geodatenzentrum.de PDF). Required credit under dl-de/by-2-0: `© GeoBasis-DE / BKG (Jahr des letzten Datenbezugs) dl-de/by-2-0`, with the source note linked to `https://www.bkg.bund.de` and the license annotation linked to `https://www.govdata.de/dl-de/by-2-0`; append `(Daten verändert)` when modified. The common "Kartendaten: basemap.de / BKG" phrasing is not an official required string [UNVERIFIED as official]; use the official form.

## C. User-focused README conventions (consolidated decisions)

- English (user decision Q1, spec FR-012). The map UI stays German.
- Structure: one-line pitch → what the map shows (plain language) → live map link **https://abu-hamad.de/map/** (user-required, canonical, trailing slash) → how to read the colors / use the tree toggle → data & methodology note (60 m radius) → credits (reference project + data sources) → license → developer link (DEVELOPMENT.md).
- A map screenshot is recommended in the top half (captured fresh from the live deployment) — aids comprehension more than prose.
- No commands, exit codes, or internal workflow references anywhere in the README (FR-008).
