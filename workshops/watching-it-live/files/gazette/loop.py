"""Keep the gazette's report up to date, rebuilding it over and over.

The newsroom's screens show the report, so it is rebuilt as often as
the machine allows for as long as the program runs, and the latest
is written to report.txt.

Usage: python gazette/loop.py [seconds] [data/articles.json]
"""

import json
import re
import string
import sys
import time
from collections import Counter

STOP_WORDS = {
    "the", "of", "and", "to", "in", "a", "is", "that", "for", "it", "on",
    "with", "as", "was", "at", "by", "from", "be", "this", "have", "are",
    "or", "an", "not", "its", "their", "which", "than", "them", "there",
}
VOWELS = re.compile(r"[aeiouy]+")
SENTENCE = re.compile(r"[.!?]+")


def load_articles(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def count_words(articles):
    punctuation = str.maketrans("", "", string.punctuation)
    counts = Counter()
    sections = Counter()
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


def syllables(word):
    return max(1, len(VOWELS.findall(word)))


def reading_ease(text):
    sentences = max(1, len(SENTENCE.findall(text)))
    words = text.split()
    beats = 0
    for word in words:
        beats += syllables(word.lower())
    return 206.835 - 1.015 * len(words) / sentences - 84.6 * beats / len(words)


def hardest(articles, n=3):
    scores = []
    for article in articles:
        scores.append((reading_ease(article["body"]), article["title"]))
    return sorted(scores)[:n]


def render(articles, counts, top, best, hard):
    lines = [f"The Gazette: {len(articles)} articles, {sum(counts.values())} words"]
    lines.append("")
    lines.append("Most common words")
    for word, count in top:
        lines.append(f"  {word:<12} {count:>6}")
    lines.append("")
    lines.append("Most common word in each section")
    for section, (word, count) in sorted(best.items()):
        lines.append(f"  {section:<12} {word:<12} {count:>6}")
    lines.append("")
    lines.append("Hardest to read")
    for ease, title in hard:
        lines.append(f"  {ease:6.1f}  {title[:50]}")
    return "\n".join(lines)


def rebuild(articles):
    counts, sections = count_words(articles)
    top = most_common(counts)
    best = top_by_section(sections)
    hard = hardest(articles)
    return render(articles, counts, top, best, hard)


def main(seconds="30", path="data/articles.json"):
    articles = load_articles(path)
    finish = time.monotonic() + float(seconds)
    passes = 0
    while time.monotonic() < finish:
        report = rebuild(articles)
        with open("report.txt", "w", encoding="utf-8") as f:
            f.write(report + "\n")
        passes += 1
    print(f"Rebuilt the report {passes} times in {seconds} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
