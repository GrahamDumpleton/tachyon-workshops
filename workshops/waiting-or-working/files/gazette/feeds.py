"""Fetch the gazette's feeds, parse them and merge them into one list.

The feeds overlap, since agencies sell the same story to several of
them, so merging drops an item that tells a story already in the list.

Usage: python gazette/feeds.py [port]
"""

import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ElementTree
from datetime import datetime

FEEDS = 20
WORD = re.compile(r"[a-z]+")


def fetch(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read()


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


def main(port="8071"):
    started = time.perf_counter()
    feeds = []
    for number in range(FEEDS):
        document = fetch(f"http://127.0.0.1:{port}/feeds/{number}.xml")
        feeds.append(parse(document))
    items = merge(feeds)
    latest = items[0]
    print(f"Merged {len(items)} items from {len(feeds)} feeds")
    print(f"Latest: {latest['title']} ({latest['date']:%d %B %Y}), "
          f"keywords {', '.join(latest['keywords'])}")
    print(f"Feeds read in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
