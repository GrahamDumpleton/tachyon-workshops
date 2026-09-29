"""Print a word-count report over the gazette's articles.

Usage: python gazette/report.py [data/articles.json]
"""

import json
import string
import sys
import time
from collections import Counter

STOP_WORDS = {
    "the", "of", "and", "to", "in", "a", "is", "that", "for", "it", "on",
    "with", "as", "was", "at", "by", "from", "be", "this", "have", "are",
    "or", "an", "not", "its", "their", "which", "than", "them", "there",
}


def load_articles(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def count_words(articles):
    punctuation = str.maketrans("", "", string.punctuation)
    counts = Counter()
    sections = {}
    seen = []
    for article in articles:
        section = article["section"]
        text = article["title"] + " " + article["body"]
        text = text.lower()
        text = text.translate(punctuation)
        for word in text.split():
            if word in STOP_WORDS:
                continue
            if word.isdigit():
                continue
            entry = section + ":" + word
            if entry not in seen:
                seen.append(entry)
                sections[entry] = 0
            sections[entry] += 1
            counts[word] += 1
    return counts, sections


def most_common(counts, n=10):
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:n]


def top_by_section(sections):
    best = {}
    for entry, count in sections.items():
        section, word = entry.split(":")
        if count > best.get(section, ("", 0))[1]:
            best[section] = (word, count)
    return best


def render(articles, counts, top, best):
    lines = [f"The Gazette: {len(articles)} articles, {sum(counts.values())} words"]
    lines.append("")
    lines.append("Most common words")
    for word, count in top:
        lines.append(f"  {word:<12} {count:>6}")
    lines.append("")
    lines.append("Most common word in each section")
    for section, (word, count) in sorted(best.items()):
        lines.append(f"  {section:<12} {word:<12} {count:>6}")
    return "\n".join(lines)


def main(path="data/articles.json"):
    started = time.perf_counter()
    articles = load_articles(path)
    counts, sections = count_words(articles)
    top = most_common(counts)
    best = top_by_section(sections)
    print(render(articles, counts, top, best))
    print(f"\nReport built in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
