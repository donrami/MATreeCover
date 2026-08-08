#!/usr/bin/env bash
# Public hygiene gate (FR-010 / FR-003): scan tracked files for personal
# paths, credentials, and internal tooling references.
# Patterns: scripts/public-patterns.txt (single source of truth, P1-P32).
# Contracts: specs/006-public-release-prep/contracts/public-hygiene.md and
# specs/015-security-audit-housekeeping/contracts/secrets-scan.md
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERN_FILE="$SCRIPT_DIR/public-patterns.txt"

# Tracked files that must quote the forbidden strings to do their job
# (see "Exemptions" in the contract). Add/remove only together with the
# contract documents.
EXEMPT_FILES=(
  '.gitignore'
  'scripts/check-public.sh'
  'scripts/public-patterns.txt'
)

# Patterns come from the shared file: one ERE per line, '#' comments allowed.
# They are applied as a single alternation per file (fast path); a line is
# reported once even when it matches several patterns.
mapfile -t patterns < <(grep -vE '^[[:space:]]*(#|$)' "$PATTERN_FILE")
alternation="$(IFS='|'; echo "${patterns[*]}")"

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
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    echo "$line"
    findings=$((findings + 1))
  done < <(grep -nE "$alternation" "$file" 2>/dev/null | sed "s|^|$file:|")
done

if [ "$findings" -gt 0 ]; then
  echo "FAIL: $findings finding(s) in $total tracked file(s)"
  exit 1
fi

echo "clean: $total tracked files scanned"
exit 0
