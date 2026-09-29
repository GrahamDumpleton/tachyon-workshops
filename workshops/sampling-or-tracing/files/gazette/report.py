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
PUNCTUATION = str.maketrans("", "", string.punctuation)


def load_articles(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


SUFFIXES = ("ings", "ing", "edly", "ed", "es", "s", "ly")


def normalise(word):
    return word.lower().translate(PUNCTUATION)


def is_stop_word(word):
    return word in STOP_WORDS or len(word) < 2


def stem(word):
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def tokenise(text):
    words = []
    for raw in text.split():
        word = normalise(raw)
        if not is_stop_word(word):
            words.append(stem(word))
    return words


def record(counts, words):
    for word in words:
        counts[word] += 1


def pairs(words):
    result = []
    previous = None
    for word in words:
        if previous is not None:
            result.append(previous + " " + word)
        previous = word
    return result


def count_words(articles):
    counts = Counter()
    phrases = Counter()
    for article in articles:
        words = tokenise(article["body"])
        record(counts, words)
        record(phrases, pairs(words))
    return counts, phrases


VOWELS = "aeiouy"


def syllables(word):
    count = 0
    previous_was_vowel = False
    for letter in word:
        is_vowel = letter in VOWELS
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def reading_ease(text):
    sentences = max(text.count("."), 1)
    words = [normalise(raw) for raw in text.split()]
    words = [word for word in words if word]
    total_syllables = sum(syllables(word) for word in words)
    return 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (total_syllables / len(words))


def reading_ease_by_section(articles):
    scores = {}
    for article in articles:
        scores.setdefault(article["section"], []).append(reading_ease(article["body"]))
    return {section: sum(values) / len(values) for section, values in scores.items()}


def by_section(articles):
    sections = Counter()
    for article in articles:
        sections[article["section"]] += 1
    return sections


def render(articles, counts, phrases, sections, ease):
    lines = [f"The Gazette: {len(articles)} articles, {counts.total()} words", ""]
    lines.append("Most common words")
    for word, count in counts.most_common(10):
        lines.append(f"  {word:<12} {count:>6}")
    lines.append("")
    lines.append("Most common phrases")
    for phrase, count in phrases.most_common(5):
        lines.append(f"  {phrase:<20} {count:>6}")
    lines.append("")
    lines.append("Articles and reading ease by section")
    for section, count in sorted(sections.items()):
        lines.append(f"  {section:<12} {count:>6} {ease[section]:>8.1f}")
    return "\n".join(lines)


def main(path="data/articles.json"):
    started = time.perf_counter()
    articles = load_articles(path)
    counts, phrases = count_words(articles)
    sections = by_section(articles)
    ease = reading_ease_by_section(articles)
    print(render(articles, counts, phrases, sections, ease))
    print(f"\nReport built in {time.perf_counter() - started:.2f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
