"""Feature 015: endpoint bind address trust model (T017, FR-007).

The endpoint must bind loopback by default (SSH-tunnel-only exposure)
and honor a BIND_ADDR override for deliberate pod-internal access.
"""

from __future__ import annotations

import threading
from pathlib import Path

from src.endpoint.server import EndpointServer, _resolve_bind_addr


def test_default_bind_is_loopback(monkeypatch) -> None:
    monkeypatch.delenv("BIND_ADDR", raising=False)
    assert _resolve_bind_addr() == "127.0.0.1"


def test_bind_addr_env_override(monkeypatch) -> None:
    monkeypatch.setenv("BIND_ADDR", "0.0.0.0")
    assert _resolve_bind_addr() == "0.0.0.0"


def test_server_listens_on_loopback_by_default(tmp_path: Path) -> None:
    """A server constructed with the default bind address accepts on
    loopback only (verified via the socket's bound address)."""
    server = EndpointServer(
        (_resolve_bind_addr(), 0), tmp_path, tmp_path, tmp_path, tmp_path
    )
    try:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, _port = server.server_address
        assert host == "127.0.0.1"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
