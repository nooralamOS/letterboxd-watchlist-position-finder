#!/usr/bin/env python3
"""HTTP server for the Letterboxd watchlist position finder."""

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from find import fetch_all_films, score

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))

# Cache
_films: list[dict] = []
_films_lock = threading.Lock()
_ready = threading.Event()  # set once the first load completes


def _load():
    global _films
    try:
        films = fetch_all_films(verbose=False)
        with _films_lock:
            _films = films
        print(f"Cache ready — {len(films)} films.")
    except Exception as e:
        print(f"Cache load error: {e}")
    finally:
        _ready.set()


def _get_films() -> list[dict]:
    _ready.wait()
    with _films_lock:
        return _films


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._serve_file("index.html", "text/html; charset=utf-8")
        elif parsed.path == "/api/search":
            q = parse_qs(parsed.query).get("q", [""])[0].strip()
            self._handle_search(q)
        elif parsed.path == "/api/status":
            with _films_lock:
                count = len(_films)
            self._send_json({"ready": _ready.is_set(), "count": count})
        else:
            self._send(404, "text/plain", b"Not found")

    def _handle_search(self, query):
        if not query:
            self._send_json({"error": "No query"})
            return
        try:
            films = _get_films()
        except Exception as e:
            self._send_json({"error": str(e)})
            return

        results = []
        for i, film in enumerate(films, 1):
            s = score(film, query)
            if s > 0:
                results.append((i, film, s))

        if not results:
            self._send_json({"error": "not found"})
            return

        results.sort(key=lambda x: -x[2])
        best = results[0][2]
        shown = [r for r in results if r[2] == best] if best >= 2 else results
        data = [{"position": pos, "name": film["name"], "slug": film["slug"]}
                for pos, film, _ in shown]
        self._send_json({"results": data})

    def _serve_file(self, filename, content_type):
        path = os.path.join(DIR, filename)
        try:
            with open(path, "rb") as f:
                data = f.read()
            self._send(200, content_type, data)
        except FileNotFoundError:
            self._send(404, "text/plain", b"Not found")

    def _send_json(self, data):
        body = json.dumps(data).encode()
        self._send(200, "application/json", body)

    def _send(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    threading.Thread(target=_load, daemon=True).start()
    server = ThreadingHTTPServer(("localhost", PORT), Handler)
    print(f"Open http://localhost:{PORT}  (loading watchlist cache…)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
