---
title: Welcome
requires: [verify:env-ready]
---

# An async service that stalls

An asyncio service is built to wait. It serves thousands of
connections on one thread, because at any moment nearly all of them
are waiting, for a database, for another service, for the reader's
next request, and a task that is waiting costs nothing. When such a
service is slow, the usual complaint is an odd one: the machine is
not busy, the services it calls are answering as quickly as ever,
and still requests that should take a twentieth of a second take
twice that.

This workshop finds out why, on a service that does exactly that.

## The rule of the event loop

An asyncio program has one *event loop*, on one thread, and the
loop runs one task at a time. A task runs until it reaches an
`await` that has to wait, and only then does the loop move on to
another. Nothing interrupts a task. While one is computing, every
other task is stopped, whether or not what it was waiting for has
arrived.

So a call that takes ten milliseconds and never awaits holds up
every request in the service for ten milliseconds. That is called
*blocking the loop*.

## The application

{open}`gazette/asgi.py` is open in the editor: the web site of the
gazette, a small newsroom, written with
[Starlette](https://www.starlette.io/) and served by
[uvicorn](https://www.uvicorn.org/). It has three pages.

- `/search?q=<word>` asks the gazette's index service which
  articles mention the word, with `await`, and lists them. The index
  service is another program, {open}`index_server.py`, which takes a
  twentieth of a second to answer. It stands in for a search engine
  or a database on another machine, and its delay is a sleep, since
  what it would be doing in that time is not the subject here.

- `/article/<number>` is one article, with the five articles most
  like it listed beneath.

- `/health` says the site is up.

{open}`load.py` plays the readers: eight of them, each asking for one
page after another, three articles for every search.

Many readers will know [FastAPI](https://fastapi.tiangolo.com/)
better than Starlette. FastAPI is built on Starlette, and a profile
of a FastAPI service has the same shape as the ones you are about to
see. It is not used here because one of the packages it needs has
not yet been released for Python 3.15.

## The environment

Create the workshop's environment. It installs Starlette, uvicorn
and httpx, and makes the `python` in the terminals Python 3.15, the
one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15, with the profiler and the packages
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling, starlette, uvicorn, httpx; from importlib.metadata import version; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling, Starlette', version('starlette'), 'and uvicorn', version('uvicorn'))"
```
