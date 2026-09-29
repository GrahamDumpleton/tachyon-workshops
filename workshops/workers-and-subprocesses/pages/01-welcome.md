---
title: Welcome
requires: [verify:env-ready]
---

# Workers and subprocesses

One process runs Python on one processor at a time, so a program
with a lot to compute starts more processes and shares the work out.
A job runner does it with a pool. A web server does it with
workers. Either way, the program you start is not the one that does
the work. It starts the ones that do, and waits for them.

The profiler samples a process: the one it started, or the one it
was pointed at. It reads that process's memory and no other. So
what does it show of a program whose work is somewhere else, and
how do you get it to look there?

A *sample* is one reading of a process's stack, and the profiler
takes a thousand a second. A flame graph draws the samples as
boxes, one for each function, as wide as its share of the samples,
with the functions it called beneath it.

## The programs

{open}`gazette/jobs.py` is open in the editor. It builds the
*digests* of the gazette's archive: for each article, and for each
of the twelve regional editions, the opening sentence, five keywords
and a reading time. `build_digest` makes one. The articles are
dealt out in batches of fifty, and each batch is a job,
`build_batch`, handed to a `ProcessPoolExecutor` of four processes.

{open}`gazette/web.py` is the gazette's web site, written with
Flask. Later in the workshop it is served by
[gunicorn](https://docs.gunicorn.org/), a server of the kind used
in production, which starts a number of worker processes and shares
the requests among them.

## The environment

Create the workshop's environment. It installs Flask and gunicorn,
and makes the `python` in the terminals Python 3.15, the one with
the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15, with the profiler, Flask and gunicorn
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling, flask, gunicorn; from importlib.metadata import version; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling, Flask', version('flask'), 'and gunicorn', version('gunicorn'))"
```
