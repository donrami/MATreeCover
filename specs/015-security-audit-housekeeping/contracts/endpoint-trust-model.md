# Contract: RunPod Endpoint Trust Model

Target: `src/endpoint/server.py`, `scripts/runpod-deploy.sh`, DEVELOPMENT.md ("Canopy-mask inference on RunPod"). Requirement source: FR-007; OR-003.

## Purpose

Document what the canopy-mask inference endpoint exposes, what it trusts, what it validates, and what runs with what privileges — and record the high-severity fixes made by the audit.

## Exposure path

- The endpoint is `POST /infer` (plus `GET /health`) on a RunPod pod, port 8000.
- The only supported access path is the owner's SSH tunnel: `ssh -L 8000:localhost:8000 <host>`, then requests to `http://127.0.0.1:8000/infer`. There is no public route.
- **Fix (HIGH)**: the server now binds `127.0.0.1` by default instead of `0.0.0.0`. The tunnel targets the pod's own localhost, so loopback binding does not break the documented workflow and removes exposure to the pod's network interface (RunPod can expose TCP ports to the internet when configured). A `BIND_ADDR` environment variable exists for deliberate pod-internal access.
- The endpoint never runs locally (OR-003); `runpod-infer` refuses to run without `MANNHEIM_RUNPOD_ENDPOINT`.

## Input validation

| Input | Validation | Response on failure |
|-------|------------|---------------------|
| HTTP method / path | only `POST /infer`, `GET /health` | 404 |
| JSON body parse | must be valid JSON | 400 |
| `model` | must equal `deepLabV3plus-resnet34` (`MODEL_ID`) | 400 |
| `threshold` | optional; numeric and in `(0, 1)` | 400 |
| `Content-Length` | **Fix (MEDIUM)**: requests over 1 MiB rejected with 413 before any read | 413 |
| runtime errors | `EndpointError` and unexpected exceptions mapped | 500 with error message |
| `inputs` | accepted for contract compatibility; **not used** — inference always processes the whole `TILE_ROOT`. Documented, no code change. | — |

The 413 cap bounds memory use from the HTTP layer; banded tiled inference (`_tile_meta` / VRT build) already bounds GPU/CPU memory. All heavy work happens under a global lock, so concurrent requests serialize.

## Privileges and trust boundaries

- What runs: `server.py` under the pod user, reading `TILE_ROOT` (imagery tiles), `WEIGHTS_PATH` (`best_deeplabv3plus.pth`), `BOUNDARY_PATH`; writing the mask + metadata JSON to `OUT_DIR`.
- Trusted inputs (owner-supplied): the model weights (reused reference checkpoint, MIT), the imagery tiles, the boundary file. The endpoint treats them as trusted by design.
- Untrusted inputs: network requests. Validation table above is the full boundary; with loopback binding the only reachable network is the owner's tunnel.
- Secrets: the SSH key never enters the pod through this project; `runpod-deploy.sh` copies only `server.py` and the boundary file, and prints the tunnel command with the key *path*, never key material. Pod-side `server.log` stays on the pod.

## Accepted risks (recorded in the audit report)

| Risk | Severity | Reason for acceptance |
|------|----------|-----------------------|
| No authentication on `/infer` | LOW | Loopback-only after the bind fix; single owner; token auth would add key management for no threat-model gain. |
| Inference runs for hours, serialized by a global lock | LOW | Owner-only workload; parallelism would multiply GPU memory (OR-002 spirit). |
| Unpinned pod dependencies (`pip install segmentation-models-pytorch rasterio`) | LOW | Fixed by pinning resolved versions in `runpod-deploy.sh` (audit change). |

## Regression constraint

The bind and size-cap changes must not alter inference behavior: same model, same threshold handling, same mask output. `tests/endpoint/` covers threshold parsing; new tests cover the bind default and the 413 cap. Inference itself is only runnable on a pod (OR-003) and is verified by the existing parity workflow (quickstart S8).
