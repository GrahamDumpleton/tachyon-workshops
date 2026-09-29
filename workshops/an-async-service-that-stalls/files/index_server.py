"""The gazette's index service: which articles mention a word.

It stands in for a service on another machine, a search engine or a
database, that takes a while to answer. The while is a sleep of a
twentieth of a second, since what it would be doing in that time is
not what the workshop is about.

    python index_server.py 8084
"""

import json
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DELAY = 0.05
WORD = re.compile(r"[a-z]+")


def build_index():
    articles = json.loads(Path("data/articles.json").read_text(encoding="utf-8"))
    articles.sort(key=lambda article: (article["date"], article["id"]), reverse=True)
    index = {}
    for article in articles:
        for word in set(WORD.findall(article["body"].lower())):
            index.setdefault(word, []).append(article["id"])
    return index


INDEX = build_index()


class Lookup(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    wbufsize = 65536

    def do_GET(self):
        address = urlparse(self.path)
        word = parse_qs(address.query).get("q", [""])[0].lower()
        if address.path == "/lookup":
            time.sleep(DELAY)
        mentions = INDEX.get(word, [])
        body = json.dumps({"word": word, "count": len(mentions), "newest": mentions[:20]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def log_message(self, format, *args):
        pass


def main(port="8084"):
    server = ThreadingHTTPServer(("127.0.0.1", int(port)), Lookup)
    print(f"The index service is listening on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nThe index service has stopped")


if __name__ == "__main__":
    main(*sys.argv[1:])
