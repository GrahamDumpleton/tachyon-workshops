---
title: Welcome
requires: [verify:env-ready]
---

# Reading a flame graph

The table from the first workshop names the function where the time
goes. It cannot say how the program got there. A function called from
three places gets one set of rows, and the table has no column for
"and most of that was when `render_archive` called it". A flame graph
is the picture that has that column: every path the program took,
side by side, with the width of each proportional to the time spent
on it. Brendan Gregg drew the first ones in 2011 from exactly the kind
of stack samples Tachyon takes, and the profiler writes one as a
single HTML file that you open and read.

## The program

{open}`gazette/pages.py` is open in the editor. It renders the
gazette as HTML: an index of the hundred latest articles, an archive
page for every day of the year, a page per section and a page per
author, nearly three hundred pages from two thousand articles. Every
page is built from `summary`, which formats one article, and
`summary` calls `format_date` to turn an ISO date into "Monday 05
January 2026". `render_archive` also calls `format_date` on its own,
to sort the articles into days. Read the four `render_` functions;
each is a few lines, and one of them is the reason the program takes
longer than it should.

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
