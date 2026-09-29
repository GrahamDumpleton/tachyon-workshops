"""Build the gazette's search indexes and write them to files.

An index lists, for every word of four letters or more, the articles
it appears in, best match first: the articles that use the word most,
and of those the newest. There is one for the whole paper and one
for each section, author and month, written as compressed JSON,
which is what the search page loads.

Usage: python gazette/index.py [data/articles.json] [indexes]
"""

import json
import os
import re
import sys
import time
import zlib
from datetime import datetime

WORD = re.compile(r"[a-z]{4,}")


def load(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return json.loads(text)


def singular(match):
    word = match.group()
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def count_words(articles):
    postings = {}
    for article in articles:
        text = article["title"].lower() + " " + article["body"].lower()
        text = WORD.sub(singular, text)
        counts = {}
        for word in WORD.findall(text):
            counts[word] = counts.get(word, 0) + 1
        for word, count in counts.items():
            postings.setdefault(word, []).append((article["id"], count, article["date"]))
    return postings


def relevance(posting):
    article, count, date = posting
    published = datetime.strptime(date, "%Y-%m-%d")
    return (-count, -published.toordinal(), article)


def rank(postings):
    index = {}
    for word, found in postings.items():
        best = sorted(found, key=relevance)
        index[word] = [article for article, count, date in best]
    return index


def write(index, path):
    document = json.dumps(index, sort_keys=True).encode("utf-8")
    packed = zlib.compress(document)
    with open(path, "wb") as f:
        f.write(packed)
    return len(packed)


def build_index(articles, path):
    postings = count_words(articles)
    index = rank(postings)
    return len(index), write(index, path)


def groups(articles):
    found = {"all": articles}
    for article in articles:
        for name in (article["section"], article["author"], article["date"][:7]):
            found.setdefault(name.lower().replace(" ", "-"), []).append(article)
    return found


def main(source="data/articles.json", target="indexes"):
    started = time.perf_counter()
    articles = load(source)
    os.makedirs(target, exist_ok=True)
    words = size = 0
    found = groups(articles)
    for name, chosen in found.items():
        indexed, packed = build_index(chosen, f"{target}/{name}.json.gz")
        words += indexed
        size += packed
    print(f"Wrote {len(found)} indexes to {target}: {words} words in {size} bytes")
    print(f"Indexes built in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
