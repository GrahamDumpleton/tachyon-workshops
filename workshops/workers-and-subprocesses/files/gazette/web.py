"""The gazette's web site, a Flask application.

Four pages: the front page, an article, a search over the word
index, and a health check. The articles are kept in a sqlite
database, data/gazette.db, which is built from data/articles.json
the first time the application starts.

    flask --app gazette.web run --port 8081
"""

import json
import os
import re
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, render_template, request

DATA = Path("data")
DATABASE = DATA / "gazette.db"
WORD = re.compile(r"[a-z]+")

COLUMNS = "id, title, author, section, date, body"
NEWEST = f"SELECT {COLUMNS} FROM articles ORDER BY date DESC, id DESC LIMIT 20"
ARTICLE = f"SELECT {COLUMNS} FROM articles WHERE id = ?"
MENTIONS = "SELECT article_id FROM words WHERE word = ?"

app = Flask(__name__)


def build_database():
    """Load the articles and an index of their words into sqlite."""
    articles = json.loads((DATA / "articles.json").read_text(encoding="utf-8"))
    scratch = DATABASE.with_suffix(f".{os.getpid()}.tmp")
    scratch.unlink(missing_ok=True)
    db = sqlite3.connect(scratch)
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
    scratch.replace(DATABASE)


def database():
    """The connection of the request being served, opened on first use."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_database(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def summary(body, length=160):
    """The start of an article, cut at the end of a word."""
    if len(body) <= length:
        return body
    return body[:length].rsplit(" ", 1)[0] + "..."


@app.route("/")
def front_page():
    newest = database().execute(NEWEST).fetchall()
    return render_template("front.html", articles=newest, summary=summary)


@app.route("/article/<int:number>")
def article(number):
    row = database().execute(ARTICLE, (number,)).fetchone()
    if row is None:
        abort(404)
    paragraphs = [text + "." for text in row["body"].split(". ") if text]
    return render_template("article.html", article=row, paragraphs=paragraphs)


@app.route("/search")
def search():
    word = request.args.get("q", "").strip().lower()
    db = database()
    found = []
    for mention in db.execute(MENTIONS, (word,)).fetchall():
        row = db.execute(ARTICLE, (mention["article_id"],)).fetchone()
        found.append(row)
    found.sort(key=lambda row: (row["date"], row["id"]), reverse=True)
    newest = found[:20]
    return render_template("search.html", word=word, count=len(found), articles=newest, summary=summary)


@app.route("/health")
def health():
    count = database().execute("SELECT count(*) FROM articles").fetchone()[0]
    return {"status": "ok", "articles": count}


if not DATABASE.exists():
    build_database()
