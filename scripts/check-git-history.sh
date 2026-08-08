#!/usr/bin/env bash
# Full-git-history secret scan gate (FR-001/002/003, feature 015).
# Scans every commit's tree plus all commit messages against the shared
# pattern set (scripts/public-patterns.txt). A finding is allowed only
# when an exemption row exists in scripts/history-exemptions.tsv:
#   <pattern-id> TAB <commit-sha> TAB <path> TAB <disposition-ref>
# where path is `(message)` for commit-message findings and
# disposition-ref names a dispositioned finding in the audit report.
# Contracts: specs/015-security-audit-housekeeping/contracts/secrets-scan.md
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERN_FILE="$SCRIPT_DIR/public-patterns.txt"
EXEMPTIONS_FILE="$SCRIPT_DIR/history-exemptions.tsv"
REPORT_FILE="verification/security-audit-2026-08-08.md"

mapfile -t patterns < <(grep -vE '^[[:space:]]*(#|$)' "$PATTERN_FILE")
mapfile -t pattern_ids < <(grep -oE '^# P[0-9]+' "$PATTERN_FILE" | awk '{print $2}')
alternation="$(IFS='|'; echo "${patterns[*]}")"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
raw="$tmpdir/raw.tsv"          # commit TAB path TAB lineno TAB content
triples="$tmpdir/triples.tsv"  # pattern TAB commit TAB path (deduped)
: > "$raw"
: > "$triples"

# --- scan every commit's tree ---
while read -r commit; do
  [ -z "$commit" ] && continue
  # git grep on a commit prefixes each hit with "<commit>:"; strip that
  # prefix and re-emit as tab-separated commit/path/line/content.
  git grep -nIE "$alternation" "$commit" 2>/dev/null \
    | sed -E "s|^$commit:([^:]*):([0-9]+):(.*)$|$commit\t\1\t\2\t\3|" >> "$raw" || true
done < <(git rev-list --all)

# --- scan commit messages ---
while IFS= read -r -d '' commit; do
  IFS= read -r -d '' subject || break
  IFS= read -r -d '' body || break
  line=1
  while IFS= read -r msg_line; do
    if printf '%s' "$msg_line" | grep -qE "$alternation"; then
      printf '%s\t(message)\t%s\t%s\n' "$commit" "$line" "$msg_line" >> "$raw"
    fi
    line=$((line + 1))
  done < <(printf '%s\n%s' "$subject" "$body")
done < <(git log --all --format='%H%x00%s%x00%b%x00')

commits_scanned="$(git rev-list --all | wc -l | tr -d ' ')"
open=0
exempted=0

# attribute patterns and check exemptions per finding line
while IFS=$'\t' read -r commit path lineno content; do
  matched=()
  for i in "${!patterns[@]}"; do
    if printf '%s' "$content" | grep -qE "${patterns[$i]}"; then
      matched+=("${pattern_ids[$i]}")
      printf '%s\t%s\t%s\n' "${pattern_ids[$i]}" "$commit" "$path" >> "$triples"
    fi
  done

  missing=()
  for pid in "${matched[@]}"; do
    row="$(printf '%s\t%s\t%s\t' "$pid" "$commit" "$path")"
    if ! grep -qF -- "$row" "$EXEMPTIONS_FILE" 2>/dev/null; then
      missing+=("$pid")
    fi
  done

  if [ "${#missing[@]}" -gt 0 ]; then
    echo "$commit:$path:$lineno: $content  (missing exemptions: ${missing[*]})"
    open=$((open + 1))
  else
    exempted=$((exempted + 1))
  fi
done < "$raw"

# --- stale exemptions: rows matching no actual finding ---
stale=0
if [ -f "$EXEMPTIONS_FILE" ]; then
  while IFS=$'\t' read -r pid commit path ref; do
    [ -z "$pid" ] && continue
    case "$pid" in \#*) continue ;; esac
    row="$(printf '%s\t%s\t%s' "$pid" "$commit" "$path")"
    if ! grep -qFx -- "$row" "$triples"; then
      echo "stale exemption: $pid $commit $path"
      stale=$((stale + 1))
    fi
    if [ -z "${ref:-}" ] || ! grep -q "| $ref |" "$REPORT_FILE" 2>/dev/null; then
      echo "orphaned exemption: $pid $commit $path -> $ref (no finding in audit report)"
      stale=$((stale + 1))
    fi
  done < "$EXEMPTIONS_FILE"
fi

if [ "$open" -gt 0 ] || [ "$stale" -gt 0 ]; then
  echo "FAIL: $open open finding(s), $stale stale/orphaned exemption(s) in $commits_scanned commits"
  exit 1
fi

echo "clean: $commits_scanned commits scanned, $exempted exempted findings, 0 open"
exit 0
