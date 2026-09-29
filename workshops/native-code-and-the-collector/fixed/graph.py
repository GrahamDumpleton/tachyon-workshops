"""Build the graph of cross-references between the gazette's articles.

Two articles are linked when they share three or more of their
keywords. Every article holds its links and every link holds the two
articles it joins, which is what the "related stories" box on an
article's page walks. The graph is built for the paper as it stood
at the end of each of the last eight days.

Usage: python gazette/graph.py [data/articles.json] [days]
"""

import gc
import json
import re
import sys
import time

WORD = re.compile(r"[a-z]{7,}")
SHARED = 3


class Story:
    def __init__(self, article):
        self.id = article["id"]
        self.title = article["title"]
        self.section = article["section"]
        self.keywords = keywords(article["body"])
        self.links = []

    def related(self):
        return [link.other(self) for link in self.links]


class Link:
    def __init__(self, first, second, shared):
        self.first = first
        self.second = second
        self.shared = shared
        first.links.append(self)
        second.links.append(self)

    def other(self, story):
        return self.second if story is self.first else self.first


def keywords(text, count=12):
    seen = {}
    for word in WORD.findall(text.lower()):
        seen[word] = seen.get(word, 0) + 1
    ranked = sorted(seen, key=lambda word: (-seen[word], word))
    return frozenset(ranked[:count])


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_graph(stories):
    using = {}
    for story in stories:
        for word in story.keywords:
            using.setdefault(word, []).append(story)
    links = []
    for story in stories:
        shared = {}
        for word in story.keywords:
            for other in using[word]:
                if other.id < story.id:
                    shared.setdefault(other, []).append(word)
        for other, words in shared.items():
            if len(words) >= SHARED:
                links.append(Link(story, other, words))
    return links


def main(path="data/articles.json", days="8"):
    started = time.perf_counter()
    articles = load(path)
    dates = sorted({article["date"] for article in articles})
    gc.disable()
    for date in dates[-int(days):]:
        stories = [Story(article) for article in articles if article["date"] <= date]
        links = build_graph(stories)
        busiest = max(stories, key=lambda story: len(story.links))
        print(f"{date}: {len(stories)} articles, {len(links)} links, "
              f"most related {busiest.title[:30]!r} with {len(busiest.links)}")
        del stories, links, busiest
        gc.collect()
    gc.enable()
    collections = sum(generation["collections"] for generation in gc.get_stats())
    print(f"Graphs built in {time.perf_counter() - started:.1f} seconds, "
          f"in which the collector ran {collections} times")


if __name__ == "__main__":
    main(*sys.argv[1:])
