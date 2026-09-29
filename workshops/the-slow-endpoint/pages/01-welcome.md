---
title: Welcome
requires: [verify:env-ready]
---

# The slow endpoint

Readers of the gazette say the search is slow. The other pages come
back at once and a search takes long enough to notice. That is all
you have been told, and it is how most performance work begins: one
address, the *endpoint*, and a complaint.

This workshop takes the complaint to a proof, in four steps, each
with the tool that suits it.

1. **Record** the site under load, once, in a form that every later
   picture can be made from.

2. **Find the view** with the flame graph, which shows which part
   of the application the time is under.

3. **Find the line** with the heatmap, which shows the source with
   the samples beside it.

4. **Fix it, record again, and compare**, under the same load, so
   that the difference is the fix and nothing else.

The profiler reads the stack of every thread of the program from
outside, a thousand times a second, and each reading is a *sample*.
A flame graph draws the samples as boxes, as wide as their share. A
heatmap writes them beside the lines of the source.

## The application

{open}`gazette/web.py` is open in the editor: the web site of the
gazette, a small newsroom, written with
[Flask](https://flask.palletsprojects.com/). It has a front page,
a page for each article, a search, and a health check, and keeps its
two thousand articles in a sqlite database with an index of the
words in them. Each function with `@app.route` above it is a *view*,
which Flask calls when a request for that address arrives.

{open}`load.py` plays the readers. It sends two hundred requests a
second from four threads: of every ten, three for the front page,
five for an article, one search and one health check. The pace is
fixed, which matters later: a server that answers more quickly is
sent the same requests, and no more of them.

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
