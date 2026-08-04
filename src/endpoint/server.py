"""RunPod canopy-mask inference endpoint (FR-025 / OR-003).

Owner-supplied HTTP endpoint for ``python -m src.pipeline.cli runpod-infer``:

    POST /infer  {"model": "deepLabV3plus-resnet34", "inputs": [...]}
    -> 200 image/tiff   canopy mask (uint8 0/1, EPSG:25832, 0.2 m GSD)

The inference replicates the CityTreeCover reference implementation
(https://github.com/jcscaptures/CityTreeCover, DeepLabV3Inference.py):
``smp.DeepLabV3Plus(encoder_name="resnet34", encoder_weights=None,
in_channels=3, classes=1)``, 1024x1024 patches with 64 px overlap, inputs
normalized by /255, sigmoid threshold at 0.5, maximum-confidence seam
reconciliation, banded streaming to bound memory (OR-002 spirit).

Environment:
  TILE_ROOT      dir containing dop20rgb_*.tif (default: /workspace/mannheim/mosaic/extract)
  WEIGHTS_PATH   best_deeplabv3plus.pth (default: /workspace/mannheim/models/best_deeplabv3plus.pth)
  BOUNDARY_PATH  boundary_buffered.geojson for the coverage metric (optional)
  OUT_DIR        write mask + meta sidecar (default: parent of TILE_ROOT)
  PORT           listen port (default: 8000)

Standard library only for the HTTP layer; torch / segmentation-models-pytorch
/ rasterio / numpy / shapely are imported lazily inside the inference path.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MODEL_ID = "deepLabV3plus-resnet34"
PATCH_PX = 1024
OVERLAP_PX = 64
THRESHOLD = 0.5
GSD_M = 0.2

# CityTreeCover reference preprocessing (`A.Normalize()` defaults):
# (x/255 - mean) / std per channel, ImageNet statistics.
NORM_MEAN = (0.485, 0.456, 0.406)
NORM_STD = (0.229, 0.224, 0.225)

TILE_GLOB = "dop20rgb_*.tif"


def _env_path(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser()


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


class EndpointError(RuntimeError):
    """Raised when the inference cannot run; HTTP layer maps to 500."""


# --------------------------------------------------------------------------
# VRT construction (pure Python, no gdal CLI on the pod)
# --------------------------------------------------------------------------

def _tile_meta(path: Path) -> tuple[str, tuple[float, float, float, float]]:
    """Return (name, (minx, miny, maxx, maxy)) for one tile."""
    import rasterio
    with rasterio.open(path) as src:
        w, h, t = src.width, src.height, src.transform
        return (
            path.name,
            (t.c, t.f + t.e * h, t.c + t.a * w, t.f),
        )


def _fmt(v: float) -> str:
    """Decimal formatting that GDAL's VRT parser accepts."""
    return f"{v:.6f}".rstrip("0").rstrip(".")


def build_vrt(tile_dir: Path, vrt_path: Path) -> tuple[int, int, tuple[float, float, float, float]]:
    """Write a mosaic VRT over ``tile_dir``; return (width, height, (minx, maxy)).

    Canvas is the union bbox of all tiles on the 0.2 m grid. Tile cells are
    aligned to km multiples, so all offsets are exact pixel multiples.
    """
    import rasterio
    tiles = sorted(tile_dir.glob(TILE_GLOB))
    if not tiles:
        raise EndpointError(f"no {TILE_GLOB} tiles under {tile_dir}")
    metas = [_tile_meta(t) for t in tiles]
    minx = min(m[1][0] for m in metas)
    maxx = max(m[1][2] for m in metas)
    miny = min(m[1][1] for m in metas)
    maxy = max(m[1][3] for m in metas)
    width = round((maxx - minx) / GSD_M)
    height = round((maxy - miny) / GSD_M)
    vrt_path.parent.mkdir(parents=True, exist_ok=True)
    rel = os.path.relpath(tile_dir, vrt_path.parent)
    # Block hints from the first tile (source files are uniform).
    with rasterio.open(tiles[0]) as probe:
        block_w, block_h = probe.block_shapes[0]
    templates = []
    for name, (tminx, tminy, tmaxx, tmaxy) in metas:
        x_off = round((tminx - minx) / GSD_M)
        y_off = round((maxy - tmaxy) / GSD_M)
        w = round((tmaxx - tminx) / GSD_M)
        h = round((tmaxy - tminy) / GSD_M)
        templates.append(
            f'    <SimpleSource>\n'
            f'      <SourceFilename relativeToVRT="1">{rel}/{name}</SourceFilename>\n'
            f'      <SourceBand>{{band}}</SourceBand>\n'
            f'      <SourceProperties RasterXSize="{w}" RasterYSize="{h}" '
            f'DataType="Byte" BlockXSize="{block_w}" BlockYSize="{block_h}" />\n'
            f'      <SrcRect xOff="0" yOff="0" xSize="{w}" ySize="{h}" />\n'
            f'      <DstRect xOff="{x_off}" yOff="{y_off}" xSize="{w}" ySize="{h}" />\n'
            f'    </SimpleSource>'
        )
    bands = []
    for band, interp in ((1, "Red"), (2, "Green"), (3, "Blue")):
        blocks = "\n".join(t.format(band=band) for t in templates)
        bands.append(
            f'  <VRTRasterBand dataType="Byte" band="{band}">\n'
            f'    <ColorInterp>{interp}</ColorInterp>\n'
            f'{blocks}\n'
            f'  </VRTRasterBand>'
        )
    xml = (
        f'<VRTDataset rasterXSize="{width}" rasterYSize="{height}">\n'
        f'  <SRS>EPSG:25832</SRS>\n'
        f'  <GeoTransform>{_fmt(minx)}, {_fmt(GSD_M)}, 0.0, '
        f'{_fmt(maxy)}, 0.0, {_fmt(-GSD_M)}</GeoTransform>\n'
        + "\n".join(bands)
        + "\n</VRTDataset>\n"
    )
    vrt_path.write_text(xml, encoding="utf-8")
    return width, height, (minx, maxy)


# --------------------------------------------------------------------------
# Inference (banded tiled streaming, parity with the reference)
# --------------------------------------------------------------------------

def _load_model(weights_path: Path, device: str):
    import torch
    import segmentation_models_pytorch as smp  # type: ignore

    model = smp.DeepLabV3Plus(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=1,
    )
    if not weights_path.exists():
        raise EndpointError(f"weights not found: {weights_path}")
    state = torch.load(weights_path, map_location="cpu")
    if not isinstance(state, dict) or "state_dict" in state:
        state = state.get("state_dict", state)
    if "model" in state and isinstance(state["model"], dict):
        state = state["model"]
    model.load_state_dict(state)
    return model.to(device).eval()


def _coverage_ratio(boundary_path: Path, tile_dir: Path) -> float | None:
    """Fraction of the buffered boundary covered by tile footprints (shapely)."""
    if not boundary_path.exists():
        return None
    try:
        import json as _json
        from shapely.geometry import box, shape
        from shapely.ops import unary_union

        data = _json.loads(boundary_path.read_text(encoding="utf-8"))
        geom = shape(data["features"][0]["geometry"])
        tiles = sorted(tile_dir.glob(TILE_GLOB))
        import re
        cells = set()
        for t in tiles:
            m = re.search(r"_(\d+)_(\d+)_\d_bw_\d+\.tif$", t.name)
            if m:
                e, n = int(m.group(1)), int(m.group(2))
                cells.add(box(e * 1000, n * 1000, (e + 1) * 1000, (n + 1) * 1000))
        if not cells:
            return None
        covered = geom.intersection(unary_union(list(cells))).area
        return covered / geom.area
    except Exception:
        return None


def run_inference(tile_dir: Path, weights_path: Path, boundary_path: Path, out_dir: Path) -> dict:
    """Run the banded DeepLabV3+ inference; write mask + meta; return meta."""
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    if not torch_cuda_ok():
        raise EndpointError("CUDA unavailable on this pod")
    import torch

    device = "cuda"
    vrt_path = out_dir / "canopy_mosaic.vrt"
    width, height, (origin_x, origin_y) = build_vrt(tile_dir, vrt_path)
    model = _load_model(weights_path, device)
    weights_sha = hashlib.sha256(weights_path.read_bytes()).hexdigest()
    t0 = time.time()

    with rasterio.open(vrt_path) as src:
        if src.width != width or src.height != height:
            raise EndpointError("VRT canvas mismatch")
        out_transform = from_origin(origin_x, origin_y, GSD_M, GSD_M)
        n_patches = 0
        with rasterio.open(
            out_dir / "canopy_prediction_mask.tif",
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=1,
            dtype="uint8",
            transform=out_transform,
            crs="EPSG:25832",
            compress="deflate",
            tiled=True,
            blockxsize=512,
            blockysize=512,
        ) as dst:
            v_step = PATCH_PX - OVERLAP_PX
            for r0 in range(0, height, v_step):
                r1 = min(r0 + PATCH_PX, height)
                band_h = r1 - r0
                strip = src.read([1, 2, 3], window=((r0, r1), (0, width)))
                canvas = np.zeros((band_h, width), dtype=np.float32)
                for c0 in range(0, width, v_step):
                    c1 = min(c0 + PATCH_PX, width)
                    patch = strip[:, :, c0:c1].astype(np.float32) / 255.0
                    for ch in range(3):
                        patch[ch] = (patch[ch] - NORM_MEAN[ch]) / NORM_STD[ch]
                    ph, pw = patch.shape[1], patch.shape[2]
                    pad_h = (-ph) % 16
                    pad_w = (-pw) % 16
                    if pad_h or pad_w:
                        patch = np.pad(
                            patch, ((0, 0), (0, pad_h), (0, pad_w)), mode="reflect"
                        )
                    tensor = torch.from_numpy(patch).unsqueeze(0).to(device)
                    with torch.no_grad():
                        logits = model(tensor)
                        probs = torch.sigmoid(logits).squeeze().cpu().numpy()
                    mask = probs[:band_h, : c1 - c0]
                    canvas[:, c0:c1] = np.maximum(canvas[:, c0:c1], mask)
                    n_patches += 1
                write_from = 0 if r0 == 0 else OVERLAP_PX
                band_out = (canvas[write_from:band_h] >= THRESHOLD).astype(np.uint8)
                dst.write(band_out, 1, window=((r0 + write_from, r1), (0, width)))

    duration_s = time.time() - t0
    coverage = _coverage_ratio(boundary_path, tile_dir)
    meta = {
        "model": MODEL_ID,
        "crs": "EPSG:25832",
        "ground_sampling_distance_m": GSD_M,
        "canvas": {"width_px": width, "height_px": height, "origin": [origin_x, origin_y]},
        "n_patches": n_patches,
        "threshold": THRESHOLD,
        "patch_size_px": PATCH_PX,
        "overlap_px": OVERLAP_PX,
        "coverage_buffered_boundary": coverage,
        "weights_sha256": weights_sha,
        "duration_s": round(duration_s, 1),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (out_dir / "canopy_prediction_mask.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    return meta


def torch_cuda_ok() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


# --------------------------------------------------------------------------
# HTTP layer
# --------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    server: "EndpointServer"  # type: ignore[name-defined]

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.split("?")[0] == "/health":
            self._send_json(200, {"status": "ok", "model": MODEL_ID})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path.split("?")[0] != "/infer":
            self._send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": f"bad json: {exc}"})
            return
        if payload.get("model") != MODEL_ID:
            self._send_json(400, {"error": f"model must be {MODEL_ID}"})
            return
        try:
            meta = self.server.run_inference_once(payload.get("inputs", []))
        except EndpointError as exc:
            self._send_json(500, {"error": str(exc)})
            return
        except Exception as exc:  # noqa: BLE001 - report and fail the request
            self._send_json(500, {"error": f"{type(exc).__name__}: {exc}"})
            return
        mask = (self.server.out_dir / "canopy_prediction_mask.tif").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/tiff")
        self.send_header("Content-Length", str(len(mask)))
        self.send_header("X-Canopy-N-Patches", str(meta["n_patches"]))
        self.end_headers()
        self.wfile.write(mask)


class EndpointServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, addr: tuple[str, int], tile_dir: Path, weights_path: Path,
                 boundary_path: Path, out_dir: Path) -> None:
        super().__init__(addr, _Handler)
        self.tile_dir = tile_dir
        self.weights_path = weights_path
        self.boundary_path = boundary_path
        self.out_dir = out_dir
        self._lock = threading.Lock()

    def run_inference_once(self, inputs: list) -> dict:
        with self._lock:
            return run_inference(self.tile_dir, self.weights_path, self.boundary_path, self.out_dir)


def main() -> None:
    tile_dir = _env_path("TILE_ROOT", "/workspace/mannheim/mosaic/extract")
    weights = _env_path("WEIGHTS_PATH", "/workspace/mannheim/models/best_deeplabv3plus.pth")
    boundary = _env_path("BOUNDARY_PATH", "/workspace/mannheim/boundary_buffered.geojson")
    out_dir = _env_path("OUT_DIR", str(tile_dir.parent))
    port = _env_int("PORT", 8000)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[endpoint] TILE_ROOT={tile_dir} WEIGHTS_PATH={weights} OUT_DIR={out_dir} PORT={port}", flush=True)
    print(f"[endpoint] CUDA available: {torch_cuda_ok()}", flush=True)
    server = EndpointServer(("0.0.0.0", port), tile_dir, weights, boundary, out_dir)
    print(f"[endpoint] listening on 0.0.0.0:{port} (POST /infer, GET /health)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
