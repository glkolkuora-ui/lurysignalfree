#!/usr/bin/env python3
"""Serve o Lury Sinais (arquivos estáticos) na porta do Railway."""
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PORT = int(os.environ.get("PORT", "8080"))
HOST = os.environ.get("HOST", "0.0.0.0")


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/health", "/healthz"):
            body = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()


if __name__ == "__main__":
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Lury Sinais em http://{HOST}:{PORT}/", flush=True)
    httpd.serve_forever()
