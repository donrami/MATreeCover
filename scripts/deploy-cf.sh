#!/usr/bin/env bash
# Cloudflare deployment for the Mannheim tree-cover map
# (specs/005-host-on-personal-domain/contracts/deployment.md §3).
#
# Slice 1 (tasks.md T004): configuration, logging, and the bundle
# identity manifest + R2 free-tier storage check. Later slices add
# the data upload step (T009), the FR-013/FR-014 gates (T010), and
# the full publish/verify/rollback flow (US5).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER_DIR="$REPO_ROOT/workers/map"
DIST_DIR="$REPO_ROOT/dist"
ARCHIVE_DIR="$REPO_ROOT/dist-archive"
BUCKET="matreecover-data"
KEEP_RELEASES=3

# R2 free tier (research R-012): 10 GB-month storage.
R2_FREE_STORAGE_BYTES=$((10 * 1024 * 1024 * 1024))

# Owner-infra continuity gate (FR-014): the DNS records checked by
# `verify-dns` belong to the owner's email/blog services and are NOT
# committed. Source scripts/deploy-cf.env (gitignored) or set the
# MATREECOVER_* env vars. Without configuration the continuity
# checks are skipped with a loud warning (see DEVELOPMENT.md).
if [ -f "$REPO_ROOT/scripts/deploy-cf.env" ]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/scripts/deploy-cf.env"
fi
MX1="${MATREECOVER_MX1:-}"
MX2="${MATREECOVER_MX2:-}"
SPF_INCLUDE="${MATREECOVER_SPF_INCLUDE:-}"
AUTOCONFIG_CNAME="${MATREECOVER_AUTOCONFIG_CNAME:-}"
AUTODISCOVER_CNAME="${MATREECOVER_AUTODISCOVER_CNAME:-}"

log() { printf '[deploy-cf] %s\n' "$*"; }
die() { printf '[deploy-cf] ERROR: %s\n' "$*" >&2; exit 1; }

require_dist() {
  [[ -d "$DIST_DIR" ]] || die "dist/ missing — run 'make publish' first"
  [[ -f "$DIST_DIR/index.html" ]] || die "dist/index.html missing — run 'make publish' first"
}

# Identity manifest (contracts/deployment.md §3.2): sorted file
# list, per-file sha256, file count, total bytes.
cmd_manifest() {
  require_dist
  local count total
  count=$(cd "$DIST_DIR" && find . -type f | wc -l)
  total=$(cd "$DIST_DIR" && find . -type f -printf '%s\n' | awk '{s += $1} END {print s + 0}')
  log "bundle: $count files, $total bytes"
  cd "$DIST_DIR" && find . -type f -print0 | sort -z | xargs -0 sha256sum
}

# Stage the Worker's assets directory: a filtered copy of dist/
# without the three data files (> 25 MiB asset limit, served from
# R2 by US2). Byte-identical copies of every served file (SC-007).
cmd_prepare_assets() {
  require_dist
  local dst="$REPO_ROOT/dist-assets"
  rm -rf "$dst" && mkdir -p "$dst"
  rsync -a \
    --exclude buildings.pmtiles \
    --exclude trees.pmtiles \
    --exclude buildings.geojson \
    "$DIST_DIR/" "$dst/"
  log "assets staged: $(find "$dst" -type f | wc -l) files -> $dst"
}

# R2 free-tier storage check (contracts/deployment.md §3.3).
cmd_storage_check() {
  require_dist
  local data_bytes
  data_bytes=$(du -sb \
    "$DIST_DIR/buildings.pmtiles" \
    "$DIST_DIR/trees.pmtiles" \
    "$DIST_DIR/buildings.geojson" 2>/dev/null | awk '{s += $1} END {print s + 0}')
  log "data files: $data_bytes bytes (R2 free tier: $R2_FREE_STORAGE_BYTES bytes)"
  (( data_bytes < R2_FREE_STORAGE_BYTES )) || die "data size exceeds the R2 free-tier storage limit"
  log "storage check PASS"
}

# Upload the three data files to R2 (contracts/hosting-config.md
# §2, deployment.md §3.4): atomic per object, correct content-type
# and cache headers. Interrupted uploads leave the previous object
# intact (FR-010).
cmd_upload_data() {
  require_dist
  local entries=(
    "buildings.pmtiles application/vnd.pmtiles public, max-age=86400, stale-while-revalidate=604800, no-transform"
    "trees.pmtiles application/vnd.pmtiles public, max-age=86400, stale-while-revalidate=604800, no-transform"
    "buildings.geojson application/geo+json no-cache"
  )
  local entry key ctype ccache
  for entry in "${entries[@]}"; do
    read -r key ctype ccache <<< "$entry"
    [[ -f "$DIST_DIR/$key" ]] || die "missing $DIST_DIR/$key — run 'make publish' first"
    log "uploading $key ($ctype, $ccache)"
    npx --yes wrangler@4 r2 object put "$BUCKET/$key" \
      --file "$DIST_DIR/$key" \
      --content-type "$ctype" \
      --cache-control "$ccache" \
      --remote
  done
  log "data upload complete"
}

# FR-013 gate (contracts/hosting-config.md §3, quickstart Scenario 6):
# DNS, canonical redirects, Range 206, cache headers, certificate.
# Exits non-zero on the first failing check. Run before declaring a
# deployment successful.
cmd_verify() {
  local base="https://abu-hamad.de" out fails=0
  # Edge pinning: resolve via 1.1.1.1 (verified current) so the
  # maintainer's local resolver cache cannot false-fail the gate.
  local ip edge
  ip=$(dig @1.1.1.1 +short abu-hamad.de A | head -1)
  [ -n "$ip" ] || die "cannot resolve abu-hamad.de via 1.1.1.1"
  edge="--resolve abu-hamad.de:443:$ip --resolve www.abu-hamad.de:443:$ip"
  pass() { log "PASS: $1"; }
  fail() { log "FAIL: $1"; fails=$((fails + 1)); }

  dig @1.1.1.1 +short abu-hamad.de NS | grep -q cloudflare.com && pass "NS @1.1.1.1 -> Cloudflare" || fail "NS @1.1.1.1"
  if dig @9.9.9.9 +short abu-hamad.de NS | grep -q cloudflare.com; then
    pass "NS @9.9.9.9 -> Cloudflare"
  else
    log "WARN: NS @9.9.9.9 not yet propagated (resolver cache; settles within 24 h of the NS change — confirm via 1.1.1.1 and the registry)"
  fi

  out=$(curl -s $edge -o /dev/null -w '%{http_code}' "$base/map/")
  [ "$out" = "200" ] && pass "/map/ serves 200" || fail "/map/ serves $out"
  out=$(curl -s $edge -D - -o /dev/null "$base/map" | grep -i '^location:' | tr -d '\r')
  [ "$out" = "location: https://abu-hamad.de/map/" ] && pass "/map -> /map/ (single 301)" || fail "/map location: $out"
  out=$(curl -s $edge -D - -o /dev/null "https://www.abu-hamad.de/map/" | grep -i '^location:' | tr -d '\r')
  [ "$out" = "location: https://abu-hamad.de/map/" ] && pass "www /map/ -> canonical" || fail "www /map/ location: $out"

  # SC-002 (feature 016, Clarifications 2026-08-09): plain-HTTP requests
  # to the canonical form must 301 to https via the worker scheme
  # redirect (zone-level Always Use HTTPS is not enabled).
  # HTTP/1.1 responses carry "Location:" (capital), HTTP/2 "location:";
  # normalize to lower case before comparing (same normalization the
  # existing https checks rely on via HTTP/2).
  out=$(curl -s -D - -o /dev/null "http://abu-hamad.de/map/" | grep -i '^location:' | tr -d '\r' | tr 'A-Z' 'a-z')
  [ "$out" = "location: https://abu-hamad.de/map/" ] && pass "http /map/ -> https /map/ (single 301)" || fail "http /map/ location: $out"
  out=$(curl -s -D - -o /dev/null "http://abu-hamad.de/map/impressum" | grep -i '^location:' | tr -d '\r' | tr 'A-Z' 'a-z')
  [ "$out" = "location: https://abu-hamad.de/map/impressum" ] && pass "http /map/impressum -> https (single 301)" || fail "http /map/impressum location: $out"
  out=$(curl -s -D - -o /dev/null "http://abu-hamad.de/map/robots.txt" | grep -i '^location:' | tr -d '\r' | tr 'A-Z' 'a-z')
  [ "$out" = "location: https://abu-hamad.de/map/robots.txt" ] && pass "http /map/robots.txt -> https (single 301)" || fail "http /map/robots.txt location: $out"

  out=$(curl -s $edge -D - -o /dev/null -H 'Range: bytes=0-1023' "$base/map/buildings.pmtiles")
  local expected_size
  expected_size=$(stat -c %s "$DIST_DIR/buildings.pmtiles" 2>/dev/null || echo 0)
  echo "$out" | grep -q '206' && echo "$out" | grep -qi "content-range: bytes 0-1023/$expected_size" \
    && pass "Range 206 with correct Content-Range" || fail "Range: $(echo "$out" | grep -iE '^(HTTP|content-range)' | tr -d '\r')"
  out=$(curl -s $edge -D - -o /dev/null -H 'Range: bytes=0-1023' "$base/map/buildings.pmtiles" | grep -i 'cache-control' | tr -d '\r')
  echo "$out" | grep -q 'max-age=86400' && echo "$out" | grep -qi 'no-transform' \
    && pass "pmtiles cache-control ($out)" || fail "pmtiles cache-control: $out"
  out=$(curl -s $edge -D - -o /dev/null "$base/map/" | grep -i 'cache-control' | tr -d '\r')
  [ -n "$out" ] && pass "cache-control present ($out)" || fail "no cache-control on /map/"

  echo | timeout 10 openssl s_client -servername abu-hamad.de -connect "$ip:443" 2>/dev/null \
    | openssl x509 -noout -checkhost abu-hamad.de >/dev/null 2>&1 && pass "cert valid for apex" || fail "cert check apex"
  echo | timeout 10 openssl s_client -servername www.abu-hamad.de -connect "$ip:443" 2>/dev/null \
    | openssl x509 -noout -checkhost www.abu-hamad.de >/dev/null 2>&1 && pass "cert valid for www" || fail "cert check www"

  # Feature 015 (contracts/security-headers.md, FR-004/FR-005): security
  # headers on the index response and on a 206 range response; the CSP
  # header must be present; unknown data-looking keys answer 404.
  out=$(curl -s $edge -D - -o /dev/null "$base/map/")
  echo "$out" | grep -qi 'content-security-policy' && echo "$out" | grep -qi 'x-content-type-options: nosniff' \
    && echo "$out" | grep -qi 'x-frame-options: deny' && echo "$out" | grep -qi 'strict-transport-security' \
    && pass "security headers on /map/" || fail "security headers on /map/"
  out=$(curl -s $edge -D - -o /dev/null -H 'Range: bytes=0-1023' "$base/map/buildings.pmtiles")
  echo "$out" | grep -qi 'x-content-type-options: nosniff' \
    && pass "security headers on 206 range response" || fail "security headers on 206 range response"
  out=$(curl -s $edge -o /dev/null -w '%{http_code}' "$base/map/nonexistent-data-key.pmtiles")
  [ "$out" = "404" ] && pass "unknown data key -> 404" || fail "unknown data key -> $out"

  [ "$fails" -gt 0 ] && die "$fails FR-013 gate(s) failed"
  log "FR-013 gate PASS"
}

# FR-014 gate (contracts/dns-https.md §5, quickstart Scenario 7): the
# Hostinger email and blog DNS records survive the migration. The
# email send/receive test is manual (quickstart Scenario 7).
cmd_verify_dns() {
  local out fails=0 configured=0
  pass() { log "PASS: $1"; }
  fail() { log "FAIL: $1"; fails=$((fails + 1)); }

  # Owner-infra checks run only when configured (deploy-cf.env or
  # MATREECOVER_* vars); the canonical map domain checks above are
  # unconditional because the domain is public.
  [ -n "$MX1$MX2$SPF_INCLUDE$AUTOCONFIG_CNAME$AUTODISCOVER_CNAME" ] && configured=1
  if [ "$configured" -eq 0 ]; then
    log "WARN: owner-infra DNS continuity checks skipped (no MATREECOVER_* config; see DEVELOPMENT.md)"
    return 0
  fi

  out=$(dig +short abu-hamad.de MX | sort)
  echo "$out" | grep -q "10 $MX1." && echo "$out" | grep -q "20 $MX2." \
    && pass "MX $MX1/$MX2 (10/20)" || fail "MX: $out"
  out=$(dig +short abu-hamad.de TXT)
  echo "$out" | grep -q "include:$SPF_INCLUDE" && pass "SPF includes $SPF_INCLUDE" || fail "SPF: $out"
  out=$(dig +short autoconfig.abu-hamad.de CNAME)
  [ "$out" = "$AUTOCONFIG_CNAME." ] && pass "autoconfig -> $AUTOCONFIG_CNAME" || fail "autoconfig: $out"
  out=$(dig +short autodiscover.abu-hamad.de CNAME)
  [ "$out" = "$AUTODISCOVER_CNAME." ] && pass "autodiscover -> $AUTODISCOVER_CNAME" || fail "autodiscover: $out"
  curl -sf -o /dev/null "https://abu-hamad.de/" && pass "blog loads over HTTPS" || fail "blog HTTPS load"

  [ "$fails" -gt 0 ] && die "$fails FR-014 gate(s) failed"
  log "FR-014 gate PASS (email send/receive test is manual — quickstart Scenario 7)"
}

case "${1:-}" in
  manifest) cmd_manifest ;;
  storage-check) cmd_storage_check ;;
  prepare-assets) cmd_prepare_assets ;;
  upload-data) cmd_upload_data ;;
  verify) cmd_verify ;;
  verify-dns) cmd_verify_dns ;;
  "") cmd_manifest; cmd_storage_check ;;
  *) die "unknown subcommand: $1 (expected: manifest | storage-check | prepare-assets | upload-data | verify | verify-dns)" ;;
esac
