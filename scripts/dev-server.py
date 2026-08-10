#!/usr/bin/env python3
"""Range-aware static server for local feature 018 verification.

Drop-in for ``python3 -m http.server``: same CLI, plus real byte-range
support (``Accept-Ranges: bytes`` and ``206 Partial Content``), which
PMTiles requires to read tile ranges from ``.pmtiles`` archives.

Usage::

    python3 scripts/dev-server.py [PORT] --directory DIR

Not for production. Bind only to 127.0.0.1.
"""

from __future__ import annotations

import http.server
import os
import socketserver
import sys
from pathlib import Path


class _RangedFile:
    """File-like wrapper that limits reads to a single range slice."""

    def __init__(self, fp, length: int) -> None:
        self._fp = fp
        self._remaining = length

    def read(self, n: int = -1) -> bytes:
        if self._remaining <= 0:
            return b""
        if n < 0 or n > self._remaining:
            n = self._remaining
        chunk = self._fp.read(n)
        self._remaining -= len(chunk)
        return chunk

    def close(self) -> None:
        self._fp.close()


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler that honors Range: bytes=… requests.

    Falls back to the full-file response when no Range is requested.
    Handles single-range requests; multi-range is rejected with 416
    (PMTiles only ever issues single ranges).
    """

    def send_head(self):  # type: ignore[override]
        path = self.translate_path(self.path)
        if not Path(path).is_file():
            self.send_error(404, "File not found")
            return None
        try:
            fs = Path(path).stat().st_size
            raw = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        range_header = self.headers.get("Range")
        last_modified = self.date_time_string(Path(path).stat().st_mtime)

        if range_header is None:
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Length", str(fs))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Last-Modified", last_modified)
            self.end_headers()
            return raw

        if not range_header.startswith("bytes="):
            raw.close()
            self.send_error(400, "Invalid Range header")
            return None
        spec = range_header[len("bytes=") :]
        if "," in spec:
            raw.close()
            self.send_error(416, "Multi-range not supported")
            return None
        start_s, _, end_s = spec.partition("-")
        if start_s == "" and end_s == "":
            raw.close()
            self.send_error(400, "Invalid Range spec")
            return None
        if start_s == "":
            length = int(end_s)
            if length <= 0 or length > fs:
                raw.close()
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{fs}")
                self.end_headers()
                return None
            start = fs - length
            end = fs - 1
        else:
            start = int(start_s)
            end = int(end_s) if end_s else fs - 1
        if start >= fs or end >= fs or start > end:
            raw.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{fs}")
            self.end_headers()
            return None
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Content-Range", f"bytes {start}-{end}/{fs}")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Last-Modified", last_modified)
        self.end_headers()
        raw.seek(start)
        return _RangedFile(raw, end - start + 1)


def main() -> None:
    port = 8899
    args = sys.argv[1:]
    if args and args[0].isdigit():
        port = int(args[0])
        args = args[1:]
    if "--directory" in args:
        idx = args.index("--directory")
        if idx + 1 < len(args):
            os.chdir(Path(args[idx + 1]).resolve())
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), RangeHTTPRequestHandler) as httpd:
        print(f"[dev-server] http://127.0.0.1:{port} serving {Path.cwd()}", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[dev-server] stopped", flush=True)


if __name__ == "__main__":
    main()
