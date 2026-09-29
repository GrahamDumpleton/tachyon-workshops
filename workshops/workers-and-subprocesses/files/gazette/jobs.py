"""Build a digest of every article, on a pool of four processes.

Usage: python -m gazette.jobs [workers] [data/articles.json]

A digest is what a front page shows of an article: its opening
sentence, its five keywords, and how long it takes to read. The
gazette prints twelve regional editions, and each has digests of its
own, since a keyword that is the name of the region says nothing to
the people who live there.

The archive is twelve years of the gazette, and the articles in the
data file stand in for each year's. They are dealt out in batches,
and each batch is a job for the pool. Four processes have an
interpreter each, so four batches are worked on at once.
"""

import json
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor

EDITIONS = (
    "north", "south", "east", "west", "city", "coast",
    "valley", "islands", "capital", "border", "highlands", "harbour",
)
YEARS = 12
BATCH = 50
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


def build_batch(articles):
    """The job a worker is given: the digests of one batch of articles."""
    return [build_digest(article, edition) for article in articles for edition in EDITIONS]


def main(workers="4", path="data/articles.json"):
    count = int(workers)
    started = time.perf_counter()
    articles = load_articles(path) * YEARS
    batches = [articles[n:n + BATCH] for n in range(0, len(articles), BATCH)]
    digests = []
    with ProcessPoolExecutor(max_workers=count) as pool:
        for batch in pool.map(build_batch, batches):
            digests.extend(batch)
    print(f"Built {len(digests)} digests in {len(batches)} batches on {count} "
          f"{"process" if count == 1 else "processes"} in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
