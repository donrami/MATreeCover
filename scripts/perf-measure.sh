#!/usr/bin/env bash
# Perf measurement harness (feature 014). Cold/warm load + interactions + optional Lighthouse.
# Usage: bash scripts/perf-measure.sh <url> [--out-dir <dir>] [--lighthouse 0|1]
set -euo pipefail

URL="${1:?usage: perf-measure.sh <url> [--out-dir <dir>] [--lighthouse 0|1]}"
OUT_DIR=""
LH=0
while [ $# -gt 1 ]; do
  case "$2" in
    --out-dir) OUT_DIR="$3"; shift 2 ;;
    --lighthouse) LH="$3"; shift 2 ;;
    *) shift ;;
  esac
done

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME_PATH:-/usr/bin/chromium}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="${OUT_DIR:-$ROOT/validation/perf-runs/$STAMP}"
mkdir -p "$OUT_DIR"

echo "== perf-measure: $URL -> $OUT_DIR (chrome $CHROME)"

node "$ROOT/scripts/perf-probe.mjs" --url "$URL" --out "$OUT_DIR/probe.json" --chrome "$CHROME"

if [ "$LH" = "1" ]; then
  echo "== lighthouse mobile"
  npx -y lighthouse "$URL" --output=json --output-path="$OUT_DIR/lh-mobile.json" \
    --chrome-path="$CHROME" --chrome-flags="--headless=new --no-sandbox --disable-dev-shm-usage" --quiet || true
  echo "== lighthouse desktop"
  npx -y lighthouse "$URL" --preset=desktop --output=json --output-path="$OUT_DIR/lh-desktop.json" \
    --chrome-path="$CHROME" --chrome-flags="--headless=new --no-sandbox --disable-dev-shm-usage" --quiet || true
  if [ -f "$OUT_DIR/lh-mobile.json" ]; then
    jq -r '"mobile score=\(.categories.performance.score*100|floor) LCP=\(.audits["largest-contentful-paint"].displayValue) TBT=\(.audits["total-blocking-time"].displayValue) CLS=\(.audits["cumulative-layout-shift"].displayValue)"' "$OUT_DIR/lh-mobile.json"
  fi
  if [ -f "$OUT_DIR/lh-desktop.json" ]; then
    jq -r '"desktop score=\(.categories.performance.score*100|floor) LCP=\(.audits["largest-contentful-paint"].displayValue) TBT=\(.audits["total-blocking-time"].displayValue)"' "$OUT_DIR/lh-desktop.json"
  fi
fi

echo "== probe summary"
jq -r '"cold: LCP=\(.cold.lcp_ms)ms TTFB=\(.cold.ttfb_ms)ms sameOriginKB=\(.cold.sameOriginKB) | warm: sameOriginKB=\(.warm.sameOriginKB) | interactions: zoom_in=\(.interactions.zoom_in)ms zoom_out=\(.interactions.zoom_out)ms trees=\(.interactions.trees_toggle)ms popup=\(.interactions.popup)ms"' "$OUT_DIR/probe.json"
echo "done: $OUT_DIR"
