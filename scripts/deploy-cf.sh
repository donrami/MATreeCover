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

case "${1:-}" in
  manifest) cmd_manifest ;;
  storage-check) cmd_storage_check ;;
  prepare-assets) cmd_prepare_assets ;;
  "") cmd_manifest; cmd_storage_check ;;
  *) die "unknown subcommand: $1 (expected: manifest | storage-check | prepare-assets)" ;;
esac
