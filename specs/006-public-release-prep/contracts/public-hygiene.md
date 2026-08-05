# Contract: Public Hygiene Scan Gate

Target: `scripts/check-public.sh` + `make check-public` target. Requirement sources: FR-010; SC-003; governance G2.

## Purpose

Make the "no personal data in the public repository" requirement machine-checkable and repeatable. The gate scans **tracked files only** (`git ls-files`), so gitignored directories (`.venv`, `data/`, `dist/`, `.omp/`, `.specify/`, `.spec-workflow/`, `mosaic/`) are structurally excluded.

## Semantics

- Exit `0`: no findings. Output: `clean: N tracked files scanned`.
- Exit `1`: at least one finding. Output: one `file:line: match` line per finding, then a summary count. Nothing else on stdout.
- Every pattern is defined with a comment stating why it is forbidden.
- The gate must never require network access.
- Adding a pattern is a contract change: update this document and the script together.

## Forbidden patterns (regex, applied per tracked file)

| # | Pattern | Rationale |
|---|---------|-----------|
| P1 | `\b/home/[A-Za-z0-9_.-]+/` | Absolute personal home path — leaks the owner's username and machine layout (FR-010) |
| P2 | `\b/Users/[A-Za-z0-9_.-]+/` | macOS equivalent of P1 |
| P3 | `~/.ssh/` | SSH key path reference in public content |
| P4 | `id_ed25519` | Concrete SSH key filename |
| P5 | `BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY` | Embedded private key material |
| P6 | `ghp_[A-Za-z0-9]{20,}` | GitHub personal access token |
| P7 | `sk-[A-Za-z0-9]{20,}` | OpenAI-style secret |
| P8 | `AKIA[0-9A-Z]{16}` | AWS access key id |
| P9 | `zone_id\s*=\s*"[0-9a-f]{32}"` | Real Cloudflare zone id (32 hex chars); only a placeholder like `<your-zone-id>` is allowed |
| P10 | `speckit` (case-insensitive) | Harness-internal workflow command |
| P11 | `\.spec-workflow` | Harness-internal directory |
| P12 | `\.specify` (case-insensitive) | Harness-internal directory |
| P13 | `root@[A-Za-z0-9_.-]+` | SSH root login target in public content |

## Allow-listed (must NOT be flagged)

- `abu-hamad.de` — the owner's public domain; the live map URL is user-required in the README (FR-003) and is the canonical deployment target. The **domain** is public; the **ops details** (registrar, DNS records, hosting IPs, MX/CNAME entries) are not and are scrubbed manually (below).
- Loopback references (`127.0.0.1`, ports `8088`/`8090`) in `validation/` records — harmless local measurement context.
- `MANNHEIM_WORKSPACE` — the env-var name is the sanctioned public mechanism.

## Manually enforced items (not regex-able, verified by review in quickstart.md)

1. `specs/005-host-on-personal-domain/`: real hosting IPs (`191.96.56.91`, `2a02:4780:b:926:0:939:29e4:2`), DNS records (MX `titan.email`, CNAME `mail.hostinger.com`), and registrar details redacted to placeholders; architecture and decisions retained.
2. `scripts/deploy-cf.sh`: owner-infra gates (apex/www host, MX/CNAME checks, blog HTTPS check) parameterized via variables with neutral defaults, documented in DEVELOPMENT.md.
3. README/DEVELOPMENT.md: no prose mention of the owner's private infrastructure beyond the canonical `abu-hamad.de/map/` URL.

## Integration

- `make check-public` runs the script; expected `clean`.
- Runs before any publish step; intended to become a CI job when the repo is public.
- Must not weaken OR-005 (`scripts/check_or005.py`): both gates remain separate and both must pass.
