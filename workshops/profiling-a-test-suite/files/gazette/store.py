"""The gazette's articles in a sqlite database, with an index of their words."""

import json
import re
import sqlite3

WORD = re.compile(r"[a-z]+")
COLUMNS = "id, title, author, section, date, body"


def load_articles(path="data/articles.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build(path, articles):
    """Make the database at path, holding the articles and the index."""
    db = sqlite3.connect(path)
    db.execute(
        "CREATE TABLE articles (id INTEGER PRIMARY KEY, title TEXT, author TEXT,"
        " section TEXT, date TEXT, body TEXT)"
    )
    db.execute("CREATE TABLE words (word TEXT, article_id INTEGER)")
    for article in articles:
        db.execute(
            "INSERT INTO articles VALUES (:id, :title, :author, :section, :date, :body)",
            article,
        )
        words = set(WORD.findall(article["body"].lower()))
        db.executemany(
            "INSERT INTO words VALUES (?, ?)",
            [(word, article["id"]) for word in words],
        )
    db.execute("CREATE INDEX words_by_word ON words (word)")
    db.commit()
    db.close()


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    return db


def article(db, number):
    return db.execute(f"SELECT {COLUMNS} FROM articles WHERE id = ?", (number,)).fetchone()


def newest(db, count=20):
    return db.execute(
        f"SELECT {COLUMNS} FROM articles ORDER BY date DESC, id DESC LIMIT ?", (count,)
    ).fetchall()


def in_section(db, section):
    return db.execute(
        f"SELECT {COLUMNS} FROM articles WHERE section = ? ORDER BY date DESC, id DESC",
        (section,),
    ).fetchall()


def mentioning(db, word, count=20):
    return db.execute(
        "SELECT a.id, a.title, a.author, a.section, a.date, a.body"
        " FROM words AS w JOIN articles AS a ON a.id = w.article_id"
        " WHERE w.word = ? ORDER BY a.date DESC, a.id DESC LIMIT ?",
        (word.lower(), count),
    ).fetchall()


def mentions(db, word):
    return db.execute("SELECT count(*) FROM words WHERE word = ?", (word.lower(),)).fetchone()[0]
