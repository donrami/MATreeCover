#!/usr/bin/env bash
# Deploy the canopy-mask inference endpoint to a RunPod pod and start it.
#
# Prereqs: the imagery tiles and best_deeplabv3plus.pth already on the pod
# (e.g. `rsync -a .../mosaic/extract/ root@HOST:/workspace/mannheim/mosaic/extract/`),
# pod reachable over the direct-TCP SSH port.
#
# Usage: scripts/runpod-deploy.sh [host] [port] [ssh_key]
#   host    ssh target, default root@HOST_IP
#   port    ssh port, default 40092
#   key     identity file, default ~/.ssh/id_ed25519
#
# Prints the tunnel + endpoint commands to run `runpod-infer` locally.
set -euo pipefail

HOST="${1:-root@HOST_IP}"
PORT="${2:-40092}"
KEY="${3:-$HOME/.ssh/id_ed25519}"

SSH=(ssh -p "$PORT" -i "$KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=20)
SCP=(scp -P "$PORT" -i "$KEY" -o StrictHostKeyChecking=accept-new)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="${MANNHEIM_WORKSPACE:-/home/mainuser/Desktop/MATreeCover/data/archive/workspace}"

"${SSH[@]}" "$HOST" "mkdir -p /workspace/mannheim/src/endpoint /workspace/mannheim/mosaic /workspace/mannheim/models"
"${SCP[@]}" "$REPO_ROOT/src/endpoint/server.py" "$HOST:/workspace/mannheim/src/endpoint/server.py"
"${SCP[@]}" "$WS/boundary_buffered.geojson" "$HOST:/workspace/mannheim/boundary_buffered.geojson"

"${SSH[@]}" "$HOST" 'bash -s' <<'REMOTE'
set -euo pipefail
PIP="pip install -q --break-system-packages"
python3 -c "import segmentation_models_pytorch" 2>/dev/null || $PIP segmentation-models-pytorch
python3 -c "import rasterio" 2>/dev/null || $PIP rasterio
python3 - <<'PY'
import torch, rasterio, segmentation_models_pytorch
print("deps ok; torch", torch.__version__, "cuda", torch.cuda.is_available())
PY
test -f /workspace/mannheim/models/best_deeplabv3plus.pth || { echo "weights missing on pod"; exit 1; }
pkill -f "src/endpoint/server.py" 2>/dev/null || true
sleep 1
cd /workspace/mannheim
nohup python3 -u src/endpoint/server.py > server.log 2>&1 &
sleep 4
cat /workspace/mannheim/server.log 2>/dev/null || true
REMOTE

echo
echo "=== tunnel ==="
echo "ssh -p $PORT -i $KEY -N -L 8000:localhost:8000 $HOST"
echo
echo "=== run ==="
echo "MANNHEIM_RUNPOD_ENDPOINT=http://127.0.0.1:8000/infer python -m src.pipeline.cli runpod-infer"
