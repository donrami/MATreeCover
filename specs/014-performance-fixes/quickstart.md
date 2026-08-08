# Quickstart — Performance Fixes (spec 014)

Validation guide. Run the scenarios in order. Each scenario is pass/fail and maps to the spec's success criteria.

Prerequisites: Python 3.11 venv (make bootstrap), tippecanoe >= 2.x, nginx, system Chromium, Node 22 for Lighthouse. All verified present on this machine.

## S1 — Local bundle serves correctly

```text
make publish
nginx -c <repo>/scripts/nginx-map.conf  (or serve dist/ on 127.0.0.1:8088, Range-capable)
```

Expected: the page loads, the map renders, the console shows no 404 for scripts, styles, geojson, or favicon. The dist/manifest.json contains the `hashed_assets` map. Every reference in index.html, main.js, and style.json resolves to an existing file (contracts/hashed-bundle.md).

Maps to: FR-002, FR-010, US3.

## S2 — Cold and warm load measurement

Headless Chromium with CDP, cleared cache, throttle 25 Mbps / 50 ms (method of validation/perf-budget.json).

```text
run the committed perf harness (scripts/perf-measure.sh, added by this feature)
```

Expected cold load: LCP under 2.0 s, TTFB under 100 ms, CLS 0 (SC-001, SC-002 lab values, median of 3).

Expected warm load (second navigation, no cache clear): same-origin transfer under 100 KB. Previously fetched pmtiles ranges served from browser cache with zero network bytes (SC-003).

Maps to: SC-001, SC-003, FR-015.

## S3 — Lighthouse scores

```text
npx lighthouse http://127.0.0.1:8088/ --preset=desktop --output=json --output-path=/tmp/lh-desktop.json
npx lighthouse http://127.0.0.1:8088/ --output=json --output-path=/tmp/lh-mobile.json   (mobile default)
```

Expected (median of 3 runs): mobile score at least 85, TBT under 1.5 s, LCP under 2.0 s. Desktop score not below 81, TBT under 500 ms (SC-001, SC-002).

Maps to: SC-001, SC-002.

## S4 — Interaction latency

Run the interaction probe against the served bundle: popup open, zoom in, zoom out, trees toggle on/off, district click, panel render, surface toggle. Five runs each, cold reload between runs.

Expected: all 8 interactions within the 2 s budget. Desktop median at or below the current 123 ms (SC-005).

Maps to: SC-005, FR-014.

## S5 — Geometry parity (rebuilt buildings.pmtiles)

```text
make pmtiles-buildings   # with the new -S 10 --simplify-only-low-zooms flags
```

Run the parity script (added by this feature):

1. Feature-count parity per tile at z10-z13 against the current archive.
2. Property parity (value, has_value) on sampled tiles.
3. Screenshot parity at z10, z12, z14, z16, z18 (initial view + fixed cameras).
4. SC-005 image sanity suite: `python -m pytest tests/ -k sanity` or the repo's image-sanity target.
5. Value recalc unchanged: `python -m src.pipeline.cli values` comparison shows no drift.

Expected: all five gates pass. If screenshot parity fails, lower the scale per contracts/low-zoom-simplification.md.

Maps to: SC-006, FR-005, FR-006.

## S6 — Full regression suite

```text
.venv/bin/python -m pytest tests/
bash scripts/check-public.sh        # FR-010
make check-or005                    # OR-005
```

Expected: all tests pass, check-public clean, OR-005 clean.

Maps to: SC-007, FR-011, FR-012, FR-013.

## S7 — Deploy and edge checks

```text
bash scripts/deploy-cf.sh prepare-assets
bash scripts/deploy-cf.sh upload-data     # pmtiles with the new cache metadata
npx wrangler deploy --config workers/map/wrangler.local.toml
bash scripts/deploy-cf.sh verify          # FR-013 gate
```

Then:

```text
curl -sI https://abu-hamad.de/map/main-<hash>.js          # cache-control: public, max-age=31536000, immutable
curl -sI https://abu-hamad.de/map/                         # cache-control: public, max-age=0, must-revalidate
curl -s -H 'Range: bytes=0-1023' https://abu-hamad.de/map/buildings.pmtiles -D - -o /dev/null   # 206, cache-control with max-age
repeat the range request, compare cf-cache-status           # HIT expected; if MISS, record and adjust SC-004 (browser-only fallback)
curl -sI https://abu-hamad.de/map/favicon.svg              # HTTP 200
```

Expected: all gates pass, headers match the directive table in contracts/cache-headers.md, favicon returns 200 (SC-008).

Maps to: SC-004, SC-007, SC-008, FR-001, FR-003, FR-012.

## Validation record

After S2-S7, update `validation/perf-budget.json` and `validation/live-perf.json` with the new measurements, following the existing record format.
