---
title: Welcome
requires: [verify:env-ready]
---

# Following the awaits

The profiler works by reading a thread's stack: the function that is
running, the function that called it, and so on down to the start of
the program. For most programs that stack is the answer to "what is
the program doing, and on whose behalf".

A program written with `asyncio` breaks that. It has one thread and
many *tasks*, and the thread belongs to the event loop, which runs
one task until it reaches an `await` that cannot finish yet, puts it
aside, and runs another. When nothing can run, the loop waits for
the operating system to say that a connection has data. So the
thread's stack says what the loop is doing. A task that is waiting
for a server is not on the stack at all, and twenty of them waiting
look the same as one.

The profiler has a second way of reading the program for this case,
`--async-aware`, which follows the tasks instead of the thread. This
workshop profiles one asyncio program both ways and reads the
difference.

## The program

{open}`gazette/crawl.py` is open in the editor. The gazette takes
stories from twenty feeds. `main` starts a task for each feed with
`asyncio.gather` and waits for them all. Each task runs `read_feed`,
which waits for one of four connections to come free (a crawler that
opens twenty connections to one server at once is not a polite one),
calls `fetch` to ask the server for a page of RSS, and then `parse`
to turn the page into a list of items. When every task has finished,
`merge` makes one list of them all, dropping an item that tells a
story already in the list.

`fetch`, `read_feed` and `main` are coroutines, written with
`async def`. `parse`, `merge` and the rest are ordinary functions.

{open}`gazette/feeds.py`, in the second tab, is the same program
without `asyncio`, fetching one feed after another. The server is
{open}`slow_server.py`, in the third. It runs on this machine and
waits half a second before each answer, which stands in for the
network and a slow machine at the other end.

## The environment

Create the workshop's environment, which installs nothing and makes
the `python` in the terminals Python 3.15, the one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15 and has the profiler
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling')"
```
