#!/usr/bin/env python3
"""Serve local Wavacity assets with headers required for SharedArrayBuffer."""

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class WavacityHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        # Wavacity needs cross-origin isolation for SharedArrayBuffer.
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Wavacity static server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()

    handler = lambda *h_args, **h_kwargs: WavacityHandler(
        *h_args, directory=args.directory, **h_kwargs
    )
    server = ThreadingHTTPServer((args.host, args.port), handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
