---
title: Welcome
requires: [verify:env-ready]
---

# Watching it live

Every profile in these workshops so far was read after the program
had finished. That suits a program that finishes. A service runs
until it is stopped, and what you want to know about it is often
what it is doing now: whether the slow function is slow all the
time or in bursts, what changes when a request comes in, whether it
is doing anything at all.

`--live` is the profiler's answer, and the nearest thing to it is
`top`. Where `top` lists the processes of a machine and keeps the
list up to date, live mode lists the functions of one Python
program, with the counts growing as the samples come in.

The second half of this workshop is about a question that watching
the counts grow makes hard to avoid: how many samples does a
profile need before its percentages can be believed?

## The program

{open}`gazette/loop.py` is open in the editor. The newsroom's
screens show a report over the gazette's articles, the most common
words and the articles hardest to read, and this program keeps it
up to date by rebuilding it as often as the machine allows, several
times a second, for as many seconds as it is told. `rebuild` calls
`count_words`, `hardest` and `render` in turn, and `main` writes
each report to `report.txt`.

## The environment

Create the workshop's environment, which installs nothing and makes
the `python` in the terminal Python 3.15, the one with the profiler.

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
