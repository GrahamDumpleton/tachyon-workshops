---
title: Welcome
requires: [verify:env-ready]
---

# A profile from production

The machine that has the problem is seldom the machine you would
choose to study it on. A production host has no browser to open a
flame graph in, nowhere to put a directory of heatmap pages, and
people who would rather you did not stay long. And one profile is
rarely enough: the question is usually whether this week is worse
than last.

The profiler is built for that. It can *record* on one machine and
draw on another.

- **On the host**, record in the binary format. It is the cheapest
  to write, since the profiler does no more than store what it
  reads, and the file is small.

- **Copy the file** to wherever you work.

- **At the desk**, `replay` turns the recording into any of the
  formats, as often as you like: a flame graph to look at, a table
  to read, or data for a program of your own.

This workshop does all three, with two recordings of one web site
a week apart, and ends with a notebook that draws them side by
side. It has one machine to work with, so the recordings are made
here, and the copying is left to your imagination.

A *sample* is one reading of a program's stacks, and the profiler
takes a thousand a second. A flame graph draws the samples as boxes,
one for each function, as wide as its share of them.

## The application

{open}`gazette/web.py` is open in the editor: the web site of the
gazette, a small newsroom, written with
[Flask](https://flask.palletsprojects.com/), with a front page, a
page for each article, a search and a health check. Its search is
slow, for a reason that an earlier workshop found: it asks the
database for each matching article with a query of its own, a
thousand queries for one search.

{open}`load.py` plays the readers. It sends two hundred requests a
second from four threads, at a fixed pace, so the site is sent the
same requests however quickly it answers.

## The environment

Create the workshop's environment. It installs Flask, and
matplotlib for the chart, and makes the `python` in the terminals
and behind the notebook Python 3.15, the one with the profiler.
matplotlib is a large package, so this takes a little longer than
usual.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15, with the profiler, Flask and matplotlib
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling, flask, matplotlib; from importlib.metadata import version; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling, Flask', version('flask'), 'and matplotlib', matplotlib.__version__)"
```
