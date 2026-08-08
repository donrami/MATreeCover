# Contract: Public Hygiene Scan Gate

Target: `scripts/check-public.sh` + `make check-public` target. Requirement sources: FR-010; SC-003; governance G2. Superseded-and-extended by `specs/015-security-audit-housekeeping/contracts/secrets-scan.md` (feature 015): patterns now live in the shared file `scripts/public-patterns.txt`, read by both the tracked-files gate and the full-history gate.

## Purpose

Make the "no personal data in the public repository" requirement machine-checkable and repeatable. The gate scans **tracked files only** (`git ls-files`), so gitignored directories (`.venv`, `data/`, `dist/`, the harness-local directories, `mosaic/`) are structurally excluded.

## Semantics

- Exit `0`: no findings. Output: `clean: N tracked files scanned`.
- Exit `1`: at least one finding. Output: one `file:line: match` line per finding, then a summary count. Nothing else on stdout.
- The gate must never require network access.
- Adding, removing, or changing a pattern is a contract change: update `scripts/public-patterns.txt`, this document (or the feature-015 secrets-scan contract), and the script's exemption list in the same commit (FR-003).

## Pattern source of truth

All patterns are defined in `scripts/public-patterns.txt`: one extended regular expression per line, each preceded by a `# P<n> — rationale` comment. Both `check-public.sh` and `check-git-history.sh` read this file. Regexes are quoted only there — never in markdown — so contract files need no hygiene exemption. Pattern ids and rationale:

| # | Class | Rationale |
|---|-------|-----------|
| P1 | absolute Linux home path | Leaks the owner's username and machine layout (FR-010) |
| P2 | absolute macOS home path | macOS equivalent of P1 |
| P3 | SSH key path reference | home-directory SSH reference in public content |
| P4 | SSH key filename | concrete key name |
| P5 | embedded private key material | private-key header blocks |
| P6 | GitHub personal access token | classic PAT |
| P7 | OpenAI-style secret | short dash-prefixed credentials |
| P8 | AWS access key id | key id prefix |
| P9 | Cloudflare zone id | real 32-hex zone ids; only a placeholder like the angle-bracket zone id is allowed |
| P10 | harness-internal workflow command | internal tooling reference |
| P11 | harness-internal directory | the workflow directory marker |
| P12 | harness-internal directory | the specify directory marker |
| P13 | SSH root login target | root login host in public content |
| P14 | harness product names | the project codename and the open-source CLI name, case-tolerant |
| P15 | harness-internal URI scheme | the double-slash local scheme — not a real URL scheme |
| P16 | harness literature-search tool | the tool name for literature search (underscore or space form) |
| P17 | harness content-fetch tools | the fetch content / get search content tool names |
| P18 | harness web-search tool | the underscore web search tool name (prose "web search" is allowed) |
| P19 | harness delegated-agent role label | the role label for delegated agents |
| P20–P32 | credential classes added by feature 015 (GitHub fine-grained PAT, Cloudflare API token/header, AWS secret and session keys, npm, Slack, Stripe, Google, PGP, PuTTY, netrc, desktop path fragment) | documented in `specs/015-security-audit-housekeeping/contracts/secrets-scan.md` |

## Allow-listed (must NOT be flagged)

- `abu-hamad.de` — the owner's public domain; the live map URL is user-required in the README and is the canonical deployment target. The **domain** is public; the **ops details** (registrar, DNS records, hosting IPs, MX/CNAME entries) are not.
- Loopback references (`127.0.0.1`, `localhost`) in docs and validation records.
- `MANNHEIM_WORKSPACE`, `RUNPOD_HOST`, `SSH_KEY`, `BIND_ADDR` — sanctioned env-var names.
- Container paths under `/workspace/mannheim/...` — pod-internal layout, documented in DEVELOPMENT.md, not personal data.

## Exemptions (documented, narrow)

The following tracked files are exempt from the scan because they must quote the forbidden strings to do their job:

1. `.gitignore` — its purpose is to exclude the harness-local directories and env files; naming them is the mechanism, not a leak.
2. `scripts/check-public.sh` — the enforcement script (exemption list and gate wiring).
3. `scripts/public-patterns.txt` — the shared pattern file; it quotes the regexes verbatim by design.

All other tracked files, including the planning documents of this feature, avoid quoting the forbidden strings and are scanned normally. The exemption list lives in the script as `EXEMPT_FILES`. Adding or removing an exemption is a contract change: update this document and the script together.

## Manually enforced items (not regex-able, verified by review in quickstart.md)

1. `specs/005-host-on-personal-domain/`: real hosting IPs, DNS records, and registrar details redacted to placeholders; architecture and decisions retained.
2. `scripts/deploy-cf.sh`: owner-infra gates parameterized via variables with neutral defaults, documented in DEVELOPMENT.md.
3. README/DEVELOPMENT.md: no prose mention of the owner's private infrastructure beyond the canonical `abu-hamad.de/map/` URL.

## Integration

- `make check-public` runs the script; expected `clean`.
- Runs before any publish step; intended to become a CI job when the repo is public.
- Must not weaken OR-005 (`scripts/check_or005.py`): both gates remain separate and both must pass.
- `make check-history` (feature 015) applies the same pattern set to the full git history via `scripts/check-git-history.sh`.
