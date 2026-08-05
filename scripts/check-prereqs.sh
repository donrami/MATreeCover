#!/usr/bin/env bash
# Prerequisite check for the Mannheim Tree-Cover pipeline (T006).
# Verifies: Python 3.11, tippecanoe >= 2.x on PATH, mannheim workspace readable.
set -euo pipefail

fail=0

echo "== checking prerequisites =="

if ! command -v python3.11 >/dev/null 2>&1; then
    echo "FAIL: python3.11 not found on PATH"
    fail=1
else
    echo "OK: python3.11 ($(python3.11 --version 2>&1))"
fi

if ! command -v tippecanoe >/dev/null 2>&1; then
    echo "FAIL: tippecanoe not found on PATH (needs >= 2.x)"
    fail=1
else
    v=$(tippecanoe --version 2>&1 | awk '{print $2}' | sed 's/^v//')
    major=$(echo "$v" | cut -d. -f1)
    echo "OK: tippecanoe $v"
    if [ "${major:-0}" -lt 2 ]; then
        echo "FAIL: tippecanoe $v < 2.x"
        fail=1
    fi
fi

WS="${MANNHEIM_WORKSPACE:-data/archive/workspace}"
if [ ! -r "$WS/boundary.geojson" ] || [ ! -d "$WS/mosaic/extract" ]; then
    echo "FAIL: mannheim workspace not readable at $WS (need boundary.geojson and mosaic/extract/)"
    fail=1
else
    echo "OK: mannheim workspace readable at $WS"
fi

if [ "$fail" -eq 1 ]; then
    echo "PREREQ CHECK FAILED"
    exit 1
fi
echo "PREREQ CHECK OK"
