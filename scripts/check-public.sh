#!/usr/bin/env bash
# Public hygiene gate (FR-010 / SC-003): scan tracked files for personal
# paths, credentials, and internal tooling references.
# Contract: specs/006-public-release-prep/contracts/public-hygiene.md
set -uo pipefail

# Tracked files that must quote the forbidden strings to do their job
# (see "Exemptions" in the contract). Add/remove only together with the
# contract document.
EXEMPT_FILES=(
  '.gitignore'
  'specs/006-public-release-prep/contracts/public-hygiene.md'
  'scripts/check-public.sh'
)

patterns=(
  # P1: absolute Linux home path — leaks the owner's username and machine layout.
  # No leading \b: /home is always preceded by a non-word char (quote, space,
  # backtick), so a word boundary would never exist.
  '/home/[A-Za-z0-9_.-]+/'
  # P2: absolute macOS home path
  '/Users/[A-Za-z0-9_.-]+/'
  # P3: SSH key path reference
  '~/.ssh/'
  # P4: concrete SSH key filename
  'id_ed25519'
  # P5: embedded private key material
  'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'
  # P6: GitHub personal access token
  'ghp_[A-Za-z0-9]{20,}'
  # P7: OpenAI-style secret
  'sk-[A-Za-z0-9]{20,}'
  # P8: AWS access key id
  'AKIA[0-9A-Z]{16}'
  # P9: real Cloudflare zone id (32 hex chars); only a placeholder is allowed
  'zone_id[[:space:]]*=[[:space:]]*"[0-9a-f]{32}"'
  # P10: harness-internal workflow command
  'speckit'
  # P11: harness-internal directory
  '\.spec-workflow'
  # P12: harness-internal directory
  '\.specify'
  # P13: SSH root login target
  'root@[A-Za-z0-9_.-]+'
)

files="$(git ls-files)"
total=0
findings=0

for file in $files; do
  exempt=0
  for e in "${EXEMPT_FILES[@]}"; do
    [ "$file" = "$e" ] && exempt=1
  done
  [ "$exempt" = 1 ] && continue

  total=$((total + 1))
  for pat in "${patterns[@]}"; do
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      echo "$line"
      findings=$((findings + 1))
    done < <(grep -nE "$pat" "$file" 2>/dev/null | sed "s|^|$file:|")
  done
done

if [ "$findings" -gt 0 ]; then
  echo "FAIL: $findings finding(s) in $total tracked file(s)"
  exit 1
fi

echo "clean: $total tracked files scanned"
exit 0
