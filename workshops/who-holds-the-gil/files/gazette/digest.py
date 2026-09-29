"""Build a digest of every article, on four threads.

Usage: python gazette/digest.py [threads] [data/articles.json]

A digest is what a front page shows of an article: its opening
sentence, its five keywords, and how long it takes to read. The
gazette prints twelve regional editions, and each has digests of its
own, since a keyword that is the name of the region says nothing to
the people who live there.
"""

import json
import re
import sys
import threading
import time

EDITIONS = (
    "north", "south", "east", "west", "city", "coast",
    "valley", "islands", "capital", "border", "highlands", "harbour",
)
WORD = re.compile(r"[a-z]+")


def load_articles(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def keywords(words, edition, count=5):
    seen = {}
    for word in words:
        if len(word) > 6 and word != edition:
            seen[word] = seen.get(word, 0) + 1
    return sorted(seen, key=lambda word: (-seen[word], word))[:count]


def syllables(word):
    total = 0
    previous = False
    for letter in word:
        vowel = letter in "aeiouy"
        if vowel and not previous:
            total += 1
        previous = vowel
    return max(total, 1)


def build_digest(article, edition):
    body = article["body"]
    words = WORD.findall(body.lower())
    return {
        "id": article["id"],
        "edition": edition,
        "opening": body.split(". ")[0] + ".",
        "keywords": keywords(words, edition),
        "minutes": max(1, round(len(words) / 230)),
        "syllables": sum(syllables(word) for word in words),
    }


def worker(articles, digests, progress):
    for article in articles:
        for edition in EDITIONS:
            digests.append(build_digest(article, edition))
        progress["done"] += 1


def report_progress(progress, total, finished, path="progress.log"):
    with open(path, "w", encoding="utf-8") as log:
        while not finished.wait(0.005):
            log.write(f"{progress['done']} of {total}\n")
            log.flush()


def main(threads="4", path="data/articles.json"):
    count = int(threads)
    started = time.perf_counter()
    articles = load_articles(path)
    digests = []
    progress = {"done": 0}
    finished = threading.Event()
    reporter = threading.Thread(
        target=report_progress, args=(progress, len(articles), finished), name="reporter")
    reporter.start()
    workers = [
        threading.Thread(target=worker, args=(articles[n::count], digests, progress), name=f"worker-{n}")
        for n in range(count)
    ]
    for thread in workers:
        thread.start()
    for thread in workers:
        thread.join()
    finished.set()
    reporter.join()
    print(f"Built {len(digests)} digests on {count} {"thread" if count == 1 else "threads"} "
          f"in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
