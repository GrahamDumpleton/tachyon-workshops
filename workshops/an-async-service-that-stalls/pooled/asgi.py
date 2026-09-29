"""The gazette's web site as an ASGI service, on Starlette.

Three pages: an article, with the articles most like it listed
beneath; a search, which asks the gazette's index service which
articles mention a word; and a health check.

    uvicorn gazette.asgi:app --port 8083

The index service is another program, index_server.py, and is looked
for on the port in the environment variable UPSTREAM_PORT.
"""

import asyncio
import contextlib
import html
import json
import os
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import httpx
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

WORD = re.compile(r"[a-z]+")
UPSTREAM = f"http://127.0.0.1:{os.environ.get('UPSTREAM_PORT', '8084')}"

ARTICLES = {
    article["id"]: article
    for article in json.loads(Path("data/articles.json").read_text(encoding="utf-8"))
}
WORDS = {
    number: frozenset(WORD.findall(article["body"].lower()))
    for number, article in ARTICLES.items()
}


def related(article, count=5):
    """The articles whose words are most like this one's."""
    words = WORDS[article["id"]]
    scores = []
    for number, others in WORDS.items():
        if number != article["id"]:
            alike = len(words & others) / len(words | others)
            scores.append((alike, number))
    scores.sort(reverse=True)
    return [ARTICLES[number] for score, number in scores[:count]]


def render_article(number):
    """The page for one article, as HTML."""
    article = ARTICLES[number]
    parts = [f"<h1>{html.escape(article['title'])}</h1>"]
    parts.append(f"<p>{html.escape(article['author'])}, {article['section']}, {article['date']}</p>")
    for sentence in article["body"].split(". "):
        parts.append(f"<p>{html.escape(sentence)}.</p>")
    parts.append("<h2>More like this</h2>")
    for other in related(article):
        parts.append(f"<p><a href='/article/{other['id']}'>{html.escape(other['title'])}</a></p>")
    return "\n".join(parts)


def render_results(word, count, articles):
    """The page of results for a search, as HTML."""
    parts = [f"<p>{count} articles mention <strong>{html.escape(word)}</strong>.</p>"]
    for article in articles:
        parts.append(f"<p><a href='/article/{article['id']}'>{html.escape(article['title'])}</a></p>")
    return "\n".join(parts)


async def article(request):
    number = request.path_params["number"]
    if number not in ARTICLES:
        return HTMLResponse("No such article", status_code=404)
    loop = asyncio.get_running_loop()
    page = await loop.run_in_executor(request.app.state.workers, render_article, number)
    return HTMLResponse(page)


async def search(request):
    word = request.query_params.get("q", "").strip().lower()
    reply = await request.app.state.index.get("/lookup", params={"q": word})
    answer = reply.json()
    newest = [ARTICLES[number] for number in answer["newest"]]
    page = render_results(word, answer["count"], newest)
    return HTMLResponse(page)


async def health(request):
    return JSONResponse({"status": "ok", "articles": len(ARTICLES)})


@contextlib.asynccontextmanager
async def lifespan(app):
    with ProcessPoolExecutor(max_workers=4) as workers:
        async with httpx.AsyncClient(base_url=UPSTREAM, timeout=10) as client:
            app.state.index = client
            app.state.workers = workers
            yield


app = Starlette(
    routes=[
        Route("/article/{number:int}", article),
        Route("/search", search),
        Route("/health", health),
    ],
    lifespan=lifespan,
)
