---
title: Welcome
requires: [verify:env-ready]
---

# Waiting or working?

A program that takes too long is doing one of two things with the
time. It is *working*: the processor is busy running its code, and
the way to make it quicker is to give the processor less to do. Or it
is *waiting*: for a server to answer, a disk to turn up a file, a
lock to come free, and the processor is idle or running somebody
else's program. No amount of tuning makes waiting quicker. The cure
is to wait for several things at once, or to stop asking.

The two call for opposite fixes, so it is the first thing to find out
about a slow program, and most programs do some of each. The profiler
can tell them apart because every sample it takes carries, along with
the stack, what the thread was doing at that instant: on a processor
or not. Its `--mode` option chooses which samples to keep. This
workshop profiles one program in two modes and reads the difference.

## The program

{open}`gazette/feeds.py` is open in the editor. The gazette takes
stories from twenty feeds. For each feed, `main` calls `fetch`, which
asks a server for a page of RSS, and `parse`, which turns the page
into a list of items and picks out five keywords for each. Then
`merge` makes one list of them all. The feeds overlap, since agencies
sell the same story to several of them, so `merge` adds an item only
if no item already in the list tells the same story, which
`same_story` decides by comparing keywords.

The server is {open}`slow_server.py`, in the tab beside it. It runs
on this machine and serves the twenty feeds from the gazette's
articles, and it waits a fifth of a second before each answer. That
pause is a stand-in, and an honest one: it is what a request to a
busy server a long way off costs, and the program fetching the feeds
cannot tell the difference.

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
