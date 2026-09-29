"""Fetch the gazette's feeds at the same time, parse them and merge them.

The feeds are fetched with asyncio, one task for each, so the waits
for the server overlap, with no more than four connections open to
the server at a time. The feeds overlap too, since agencies sell
the same story to several of them, so merging drops an item that
tells a story already in the list.

Usage: python gazette/crawl.py [port]
"""

import asyncio
import re
import sys
import time
import xml.etree.ElementTree as ElementTree
from datetime import datetime

FEEDS = 20
CONNECTIONS = 4
WORD = re.compile(r"[a-z]+")


async def fetch(port, path):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    request = f"GET {path} HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n"
    writer.write(request.encode("ascii"))
    await writer.drain()
    reply = await reader.read()
    writer.close()
    await writer.wait_closed()
    headers, _, body = reply.partition(b"\r\n\r\n")
    status = headers.split(b"\r\n", 1)[0].decode("ascii")
    if " 200 " not in status:
        raise RuntimeError(f"{path}: {status}")
    return body


def keywords(text, count=5):
    seen = {}
    for word in WORD.findall(text.lower()):
        if len(word) > 6:
            seen[word] = seen.get(word, 0) + 1
    ranked = sorted(seen, key=lambda word: (-seen[word], word))
    return ranked[:count]


def parse(document):
    items = []
    for item in ElementTree.fromstring(document).iter("item"):
        body = item.findtext("description")
        items.append({
            "id": int(item.findtext("guid")),
            "title": item.findtext("title"),
            "section": item.findtext("category"),
            "date": datetime.strptime(item.findtext("pubDate"), "%Y-%m-%d"),
            "keywords": keywords(body),
        })
    return items


async def read_feed(port, number, connections):
    async with connections:
        document = await fetch(port, f"/feeds/{number}.xml")
    return parse(document)


def same_story(item, other):
    shared = set(item["keywords"]) & set(other["keywords"])
    return len(shared) == 5 and item["section"] == other["section"]


def merge(feeds):
    merged = []
    for items in feeds:
        for item in items:
            if not any(same_story(item, other) for other in merged):
                merged.append(item)
    return sorted(merged, key=lambda item: (item["date"], item["id"]), reverse=True)


async def main(port="8072"):
    started = time.perf_counter()
    connections = asyncio.Semaphore(CONNECTIONS)
    feeds = await asyncio.gather(
        *(read_feed(int(port), number, connections) for number in range(FEEDS))
    )
    items = merge(feeds)
    latest = items[0]
    print(f"Merged {len(items)} items from {len(feeds)} feeds")
    print(f"Latest: {latest['title']} ({latest['date']:%d %B %Y}), "
          f"keywords {', '.join(latest['keywords'])}")
    print(f"Feeds read in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:]))
