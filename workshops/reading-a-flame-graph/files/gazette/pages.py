"""Render the gazette's index and archive pages as HTML.

Usage: python gazette/pages.py [data/articles.json]
"""

import html
import json
import sys
import time
from datetime import datetime


def load_articles(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def format_date(iso_date):
    parsed = datetime.strptime(iso_date, "%Y-%m-%d")
    return parsed.strftime("%A %d %B %Y")


def excerpt(body, words=30):
    return " ".join(body.split()[:words]) + "..."


def summary(article):
    return (
        f"<article><h2>{html.escape(article['title'])}</h2>"
        f"<p class=\"byline\">{html.escape(article['author'])}, "
        f"<time datetime=\"{article['date']}\">{format_date(article['date'])}</time></p>"
        f"<p>{html.escape(excerpt(article['body']))}</p></article>"
    )


def render_index(articles, count=100):
    latest = sorted(articles, key=lambda a: a["date"], reverse=True)[:count]
    return "<main>" + "".join(summary(a) for a in latest) + "</main>"


def render_archive(articles):
    days = sorted({format_date(a["date"]) for a in articles}, key=lambda d: d[-4:] + d)
    pages = {}
    for day in days:
        published = [a for a in articles if format_date(a["date"]) == day]
        pages[day] = f"<h1>{day}</h1>" + "".join(summary(a) for a in published)
    return pages


def render_sections(articles):
    pages = {}
    for article in articles:
        pages.setdefault(article["section"], []).append(summary(article))
    return {section: "".join(parts) for section, parts in pages.items()}


def render_authors(articles):
    pages = {}
    for article in articles:
        pages.setdefault(article["author"], []).append(summary(article))
    return {author: "".join(parts) for author, parts in pages.items()}


def main(path="data/articles.json"):
    started = time.perf_counter()
    articles = load_articles(path)
    index = render_index(articles)
    archive = render_archive(articles)
    sections = render_sections(articles)
    authors = render_authors(articles)
    pages = 1 + len(archive) + len(sections) + len(authors)
    print(f"Rendered {pages} pages: the index, {len(archive)} days, "
          f"{len(sections)} sections and {len(authors)} authors.")
    print(f"Pages rendered in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
