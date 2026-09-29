"""Print a word-count report over the gazette's articles.

Usage: python -m gazette.report [data/articles.json]
"""

import json
import string
import sys
import time

STOP_WORDS = {
    "the", "of", "and", "to", "in", "a", "is", "that", "for", "it", "on",
    "with", "as", "was", "at", "by", "from", "be", "this", "have", "are",
    "or", "an", "not", "its", "their", "which", "than", "them", "there",
}


def load_articles(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tokenise(text):
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return [word for word in text.split() if word not in STOP_WORDS]


def count_words(articles):
    words = []
    for article in articles:
        words.extend(tokenise(article["body"]))
    unique = []
    for word in words:
        if word not in unique:
            unique.append(word)
    return {word: words.count(word) for word in unique}


def most_common(counts, n=10):
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:n]


def render(articles, counts, top):
    lines = [f"The Gazette: {len(articles)} articles, {sum(counts.values())} words"]
    lines.append("")
    lines.append("Most common words")
    for word, count in top:
        lines.append(f"  {word:<12} {count:>6}")
    by_section = {}
    for article in articles:
        by_section[article["section"]] = by_section.get(article["section"], 0) + 1
    lines.append("")
    lines.append("Articles by section")
    for section, count in sorted(by_section.items()):
        lines.append(f"  {section:<12} {count:>6}")
    return "\n".join(lines)


def main(path="data/articles.json"):
    started = time.perf_counter()
    articles = load_articles(path)
    counts = count_words(articles)
    top = most_common(counts)
    print(render(articles, counts, top))
    print(f"\nReport built in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
