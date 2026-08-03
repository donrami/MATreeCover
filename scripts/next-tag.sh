#!/usr/bin/env bash
# OR-004 / R-013: next monotonic tag number for a tag family (Spec/Plan/Slice/Milestone).
# Counts existing `Family-NN:` trailer lines in the git log; prints only the number.
set -euo pipefail

family="${1:?usage: next-tag.sh <Family>}"

count=$(git log --format='%B' 2>/dev/null | grep -cE "^${family}-[0-9]+:" || true)
printf '%02d\n' "$((count + 1))"
