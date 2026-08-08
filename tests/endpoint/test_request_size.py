"""Feature 015: endpoint request-size cap (T018, FR-007).

Content-Length above 1 MiB must be rejected with 413 before any body
read; non-numeric lengths fall into the 400 path. The 413/400 paths
never touch inference, so they are exercised against a live server.
"""

from __future__ import annotations

import http.client
import json
import socket
import threading
from pathlib import Path

from src.endpoint.server import MAX_REQUEST_BYTES, EndpointServer


def _start_server(tmp_path: Path):
    server = EndpointServer(
        ("127.0.0.1", 0), tmp_path, tmp_path, tmp_path, tmp_path
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, thread, host, port


def test_oversized_request_rejected_with_413(tmp_path: Path) -> None:
    server, thread, host, port = _start_server(tmp_path)
    try:
        conn = http.client.HTTPConnection(host, port, timeout=10)
        body = b"x" * (MAX_REQUEST_BYTES + 1)
        conn.request("POST", "/infer", body=body, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 413
        payload = json.loads(resp.read())
        assert "too large" in payload.get("error", "")
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_exact_cap_is_allowed_to_parse(tmp_path: Path) -> None:
    """A body at exactly the cap passes the size gate and reaches JSON
    parsing (which fails with 400 for non-JSON) — the cap is not off by
    one, and the check fires before any read on oversized bodies."""
    server, thread, host, port = _start_server(tmp_path)
    try:
        conn = http.client.HTTPConnection(host, port, timeout=10)
        body = b" " * MAX_REQUEST_BYTES  # valid size, invalid JSON
        conn.request("POST", "/infer", body=body, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 400
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_non_numeric_content_length_rejected_400(tmp_path: Path) -> None:
    server, thread, host, port = _start_server(tmp_path)
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.sendall(
            b"POST /infer HTTP/1.1\r\nHost: localhost\r\n"
            b"Content-Length: not-a-number\r\n\r\n"
        )
        data = sock.recv(4096)
        sock.close()
        assert b" 400 " in data.split(b"\r\n", 1)[0]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
