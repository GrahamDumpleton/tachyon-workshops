"""Serve the gazette's feeds over HTTP, slowly, as a distant server would.

Usage: python slow_server.py [port] [data/articles.json]

Each of the twenty feeds is a page of RSS holding a hundred articles.
The server waits a twentieth of a second before it answers, which
stands in for the network and the machine at the other end.
"""

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from xml.sax.saxutils import escape

FEEDS = 20
DELAY = 0.05


def build_feeds(path):
    with open(path, encoding="utf-8") as f:
        articles = json.load(f)
    size = len(articles) // FEEDS
    feeds = {}
    for number in range(FEEDS):
        items = "".join(
            f"<item><guid>{a['id']}</guid><title>{escape(a['title'])}</title>"
            f"<author>{escape(a['author'])}</author><category>{a['section']}</category>"
            f"<pubDate>{a['date']}</pubDate>"
            f"<description>{escape(a['body'])}</description></item>"
            for a in articles[number * size:(number + 1) * size]
        )
        feeds[f"/feeds/{number}.xml"] = (
            f"<?xml version=\"1.0\"?><rss version=\"2.0\"><channel>"
            f"<title>The Gazette, feed {number}</title>{items}</channel></rss>"
        ).encode("utf-8")
    return feeds


class Handler(BaseHTTPRequestHandler):
    feeds = {}

    def do_GET(self):
        body = self.feeds.get(self.path)
        if body is None:
            self.send_error(404)
            return
        time.sleep(DELAY)
        self.send_response(200)
        self.send_header("Content-Type", "application/rss+xml")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main(port="8071", path="data/articles.json"):
    Handler.feeds = build_feeds(path)
    server = ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)
    print(f"Serving {len(Handler.feeds)} feeds on http://127.0.0.1:{port}/feeds/0.xml, Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main(*sys.argv[1:])
