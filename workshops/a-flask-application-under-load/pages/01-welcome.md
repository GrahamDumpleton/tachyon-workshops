---
title: Welcome
requires: [verify:env-ready]
---

# A Flask application under load

The programs you have profiled so far were scripts: they started,
did their work and ended, and the profiler watched from start to
end. A web application is a different kind of program, in three ways
that change how it is profiled.

- **It never finishes.** A server runs until it is stopped, so there
  is no end for the profiler to wait for. You say how long to watch.

- **It does nothing until asked.** A server with no requests is
  asleep, and a profile of it shows sleep. Something has to send
  requests while the profiler watches, and the profile is a profile
  of *those* requests.

- **It does many small things, not one large one.** The question is
  seldom "why does the program take a minute" and usually "which
  kind of request costs the most".

The profiler is the one you know. It reads the stack of every thread
of the program from outside, a thousand times a second, and each
reading is a *sample*. A flame graph draws the samples as boxes, one
for each function, as wide as its share of the samples, with the
functions it called beneath it.

## The application

{open}`gazette/web.py` is open in the editor: the web site of the
gazette, a small newsroom, written with
[Flask](https://flask.palletsprojects.com/). It has four pages.

- `/`, the front page, with the twenty newest articles.

- `/article/<number>`, one article.

- `/search?q=<word>`, the articles that mention a word.

- `/health`, which says the site is up, for whatever is monitoring
  it.

The two thousand articles are kept in a sqlite database, which the
application builds from `data/articles.json` the first time it
starts. Each function with `@app.route` above it is a *view*: Flask
calls it when a request for that address arrives.

{open}`load.py` plays the readers. It sends requests from four
threads at a steady pace, two hundred a second between them, in the
proportions a news site sees: of every ten, three for the front
page, five for an article, one search and one health check.

## The environment

Create the workshop's environment. It installs Flask, and makes the
`python` in the terminals Python 3.15, the one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15, with the profiler and Flask
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling, flask; from importlib.metadata import version; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling and Flask', version('flask'))"
```
