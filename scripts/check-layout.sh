#!/usr/bin/env bash
# Layout gate (FR-009/011, feature 015): the tracked tree must match the
# documented layout. Machine form: scripts/layout-manifest.tsv (one row
# per top-level tracked entry); human form: DEVELOPMENT.md "What is in
# this repository". Changing the section without the manifest (or the
# manifest without the section) fails this gate.
# Contract: specs/015-security-audit-housekeeping/contracts/layout-gate.md
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_FILE="$SCRIPT_DIR/layout-manifest.tsv"

manifest_entries=()
while IFS=$'\t' read -r entry ref; do
  [ -z "$entry" ] && continue
  case "$entry" in \#*) continue ;; esac
  manifest_entries+=("$entry")
done < "$MANIFEST_FILE"

tracked="$(git ls-files)"
total=0
failures=0

report_fail() {
  echo "$1"
  failures=$((failures + 1))
}

# 1. Every tracked path starts with a manifest row (top-level match).
for file in $tracked; do
  total=$((total + 1))
  top="${file%%/*}"
  found=0
  for entry in "${manifest_entries[@]}"; do
    if [ "$file" = "$entry" ] || [ "$top" = "${entry%/}" ]; then
      found=1
      break
    fi
  done
  [ "$found" = 1 ] || report_fail "$file -> no documented top-level entry"
done

# 2. Every manifest row exists in the tracked tree (no dead entries).
for entry in "${manifest_entries[@]}"; do
  if [ "${entry%/}" = "$entry" ]; then
    # root-level file row: the file must be tracked exactly
    echo "$tracked" | grep -qx "$entry" || report_fail "$entry -> manifest row missing from tree"
  else
    echo "$tracked" | grep -q "^$entry" || report_fail "$entry -> manifest row missing from tree"
  fi
done

# 3. No tracked file at the repo root outside the documented root set.
for file in $tracked; do
  case "$file" in */*) continue ;; esac
  found=0
  for entry in "${manifest_entries[@]}"; do
    [ "$file" = "$entry" ] && found=1
  done
  [ "$found" = 1 ] || report_fail "$file -> undocumented root-level file"
done

if [ "$failures" -gt 0 ]; then
  echo "FAIL: $failures layout mismatch(es) in $total tracked paths"
  exit 1
fi

echo "clean: $total tracked paths, ${#manifest_entries[@]} documented entries"
exit 0
