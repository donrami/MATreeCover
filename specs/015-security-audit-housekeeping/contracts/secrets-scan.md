# Contract: Secrets Scan (tracked files + git history)

Target: `scripts/check-public.sh`, `scripts/check-git-history.sh`, `scripts/public-patterns.txt`, `scripts/history-exemptions.tsv`; make targets `check-public`, `check-history`. Requirement sources: FR-001, FR-002, FR-003, FR-011; SC-001, SC-007.

## Purpose

Prove, from a committed scan, that no credential, personal path, or private key material exists in the tracked tree or anywhere in git history, and keep that state enforced going forward. Supersedes and extends the feature-006 contract (`specs/006-public-release-prep/contracts/public-hygiene.md`), which is updated in the same change.

## Pattern source of truth

All patterns live in `scripts/public-patterns.txt`: one extended regular expression per line, each preceded by a `# P<n> — rationale` comment. Both gates read this file. This contract and the feature-006 contract document pattern IDs and rationale only — regexes are never quoted in markdown, so contract files need no hygiene exemption.

Pattern inventory: P1–P19 (existing, feature 006/014) plus P20–P32 added by this audit:

| ID | Class |
|----|-------|
| P1–P19 | As documented in the updated feature-006 contract (home paths, SSH keys, GitHub/OpenAI/AWS/Cloudflare credentials, harness-internal references). P9's zone-id rule is now enforced from the shared file, fixing a script/contract drift. |
| P20 | GitHub fine-grained PAT |
| P21 | Cloudflare API token (assignment form) |
| P22 | Cloudflare X-Auth-Email / X-Auth-Key |
| P23 | AWS secret access key |
| P24 | AWS temporary session key |
| P25 | npm token |
| P26 | Slack token / webhook |
| P27 | Stripe live key |
| P28 | Google API key |
| P29 | PGP private key block |
| P30 | PuTTY private key |
| P31 | netrc-style machine/login/password |
| P32 | desktop path fragment (personal machine layout) |

Rule (FR-003): adding, removing, or changing a pattern is a contract change — update this contract (or the feature-006 contract) and the pattern file in the same commit. The gates must stay green on the audited tree.

## Gate: tracked files (`check-public.sh`)

- Scans `git ls-files` output; every pattern from the shared file, applied per file.
- Exemptions (narrow, documented, in `EXEMPT_FILES`): `.gitignore`, `scripts/check-public.sh`, `scripts/public-patterns.txt` — files whose purpose is to quote the forbidden strings.
- Exit 0: `clean: N tracked files scanned`. Exit 1: one `file:line: match` per finding, then a summary count.
- Never requires network access. Shell-only, grep-based.

## Gate: git history (`check-git-history.sh`)

- For every commit in `git rev-list --all`, runs `git grep -nIE '<all patterns as one alternation>' <commit>` over the commit's tree. Scans commit messages too (`git log --all --format='%H%x00%s%x00%b'`).
- A finding is allowed only if an exemption row exists in `scripts/history-exemptions.tsv` for **every** pattern the finding matches:

  ```text
  <pattern-id>\t<commit-sha>\t<path>\t<disposition-ref>
  ```

  `path` is `(message)` for commit-message findings; `disposition-ref` names the dispositioned finding (F1, F2, ...) in `verification/security-audit-2026-08-08.md`.
- Exit 0: `clean: N commits scanned, M exempted findings, 0 open`. Exit 1: every unexempted finding listed as `commit:path:line: match`, plus stale exemptions (rows matching nothing) and orphaned rows (references to nonexistent report findings).
- Semantics: history is never rewritten (spec assumption); the gate enforces forward prevention — a future commit that adds a secret fails until a dispositioned exemption exists.
- Expected runtime on this repo: under 60 s (89 commits, ~272 files).

## Dispositions (FR-002)

Every finding must end in exactly one disposition, recorded in the audit report:

| Disposition | Evidence required |
|-------------|-------------------|
| `remediated` | The credential was or is live; rotation performed; the secret is unusable. |
| `never-live` | Evidence the value never reached a live service (e.g. placeholder, test fixture, example). |
| `accepted-risk` | Reason plus owner sign-off (name + date). |

SC-001: zero findings without a disposition; no live credential remains usable.

## Allow-listed (never flagged)

- `abu-hamad.de` — the owner's public domain, required in README and deploy gates.
- Loopback references (`127.0.0.1`, `localhost`) in docs and validation records.
- `MANNHEIM_WORKSPACE`, `RUNPOD_HOST`, `SSH_KEY`, `BIND_ADDR` — sanctioned env-var names.
- Container paths under `/workspace/mannheim/...` — pod-internal layout, documented in DEVELOPMENT.md, not personal data.

## Synthetic regression test (SC-007)

`tests/acceptance/test_public_hygiene.py` creates a tracked-looking temp file containing each pattern and asserts `check-public.sh` fails with that file and pattern named. This keeps every pattern live: a pattern that stops matching is a test failure.
