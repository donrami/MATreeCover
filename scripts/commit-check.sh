#!/usr/bin/env bash
# OR-004 / R-013: refuse to commit while tracked files are modified or staged.
# Usage: commit-check.sh <TagName>
set -euo pipefail

tag="${1:?usage: commit-check.sh <TagName>}"

if [ -n "$(git diff --name-only)" ]; then
    echo "error: unstaged changes present; commit them separately:" >&2
    git diff --name-only | sed 's/^/  /' >&2
    exit 1
fi

if [ -n "$(git diff --cached --name-only)" ]; then
    echo "error: staged changes present; commit them separately:" >&2
    git diff --cached --name-only | sed 's/^/  /' >&2
    exit 1
fi

echo "clean worktree for $tag commit"
