"""Variant for workshop 3: the report driven through generators."""
import json, string, sys, time
PUNCTUATION = str.maketrans("", "", string.punctuation)

def articles(path):
    with open(path, encoding="utf-8") as f:
        yield from json.load(f)

def words(articles):
    for article in articles:
        for raw in article["body"].split():
            yield raw.lower().translate(PUNCTUATION)

def pairs(words):
    previous = None
    for word in words:
        if previous is not None:
            yield previous, word
        previous = word

def main(path="data/articles.json"):
    started = time.perf_counter()
    counts = {}
    for _ in range(6):
        for pair in pairs(words(articles(path))):
            counts[pair] = counts.get(pair, 0) + 1
    top = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:3]
    print(top)
    print(f"Pairs counted in {time.perf_counter() - started:.1f} seconds")

if __name__ == "__main__":
    main(*sys.argv[1:])
