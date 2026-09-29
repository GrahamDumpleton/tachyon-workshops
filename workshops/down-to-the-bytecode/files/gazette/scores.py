"""Score the gazette's articles against each reader's interests.

Every article gets a score for every reader: the weight the reader
gives its section, plus a little for each of the reader's words the
article uses, less a penalty that grows with the article's age. The
best for each reader goes at the top of their front page.

Usage: python gazette/scores.py [one-class|by-section] [data/articles.json]

With "one-class", every article is an Article. With "by-section",
each is an instance of the class for its section.
"""

import json
import re
import sys
import time
from datetime import date

WORD = re.compile(r"[a-z]{5,}")
TODAY = date(2026, 9, 29)
READERS = 2500


class Article:
    desk = "news"

    def __init__(self, record):
        self.id = record["id"]
        self.title = record["title"]
        self.section = record["section"]
        self.age = (TODAY - date.fromisoformat(record["date"])).days
        self.words = frozenset(WORD.findall(record["body"].lower()))
        self.length = len(record["body"])


class Business(Article):
    desk = "city"


class Culture(Article):
    desk = "arts"


class Local(Article):
    desk = "metro"


class Politics(Article):
    desk = "lobby"


class Science(Article):
    desk = "science"


class Sport(Article):
    desk = "sport"


class Technology(Article):
    desk = "science"


class Weather(Article):
    desk = "metro"


SECTIONS = {
    "Business": Business, "Culture": Culture, "Local": Local,
    "Politics": Politics, "Science": Science, "Sport": Sport,
    "Technology": Technology, "Weather": Weather,
}


class Reader:
    def __init__(self, number, sections, vocabulary):
        self.number = number
        self.weights = {
            section: 1 + (number * 7 + place * 3) % 5
            for place, section in enumerate(sections)
        }
        self.words = frozenset(
            vocabulary[(number * 13 + n * 17) % len(vocabulary)] for n in range(8)
        )


def score(reader, article):
    total = reader.weights.get(article.section, 0) * 10
    for word in reader.words:
        if word in article.words:
            total += 3
    total -= article.age // 7
    if article.length > 650:
        total += 1
    return total


def best_for(reader, articles):
    best = None
    highest = -1
    for article in articles:
        points = score(reader, article)
        if points > highest:
            best, highest = article, points
    return best, highest


def load(path, how):
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    if how == "by-section":
        return [SECTIONS[record["section"]](record) for record in records]
    return [Article(record) for record in records]


def main(how="one-class", path="data/articles.json"):
    started = time.perf_counter()
    articles = load(path, how)
    sections = sorted({article.section for article in articles})
    vocabulary = sorted(set().union(*(article.words for article in articles[:200])))
    total = 0
    for number in range(READERS):
        reader = Reader(number, sections, vocabulary)
        best, points = best_for(reader, articles)
        total += points
    classes = len({type(article) for article in articles})
    print(f"Scored {len(articles)} articles of {classes} "
          f"{'class' if classes == 1 else 'classes'} for {READERS} readers")
    print(f"Scores computed in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
