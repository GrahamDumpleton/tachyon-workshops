---
title: Welcome
requires: [verify:env-ready]
---

# Your first profile

A program is taking longer than it should, and you want to know where
the time goes. That is the question a profiler answers, and this
workshop answers it for one small program with Tachyon, the profiler
that arrived in Python 3.15 as the `profiling.sampling` module.

There are two kinds of profiler. The first instruments the program: it
hooks every function call and return, counts them and times them, and
the program runs slower while it does. Python has had one of those for
decades, as `cProfile`. The second kind never touches the program. It
looks at the program's call stack from the outside, many times a
second, and keeps a tally of what it sees. Tachyon is the second kind.

Each look is a *sample*: the call stack at one instant, that is, every
function that was in the middle of running at that moment, from the
top-level script down to the function doing the work. Tachyon takes a
thousand samples a second unless told otherwise. A function that is
running most of the time is found on most of the samples, and a
function that finishes in a microsecond is hardly found at all. That
one idea is the whole of this workshop, and the table on the next
pages is what a thousand samples a second add up to.

## The program

{open}`gazette/report.py` is open in the editor. It belongs to a small
newsroom, the gazette, and it prints a report over two thousand
articles in `data/articles.json`: the most common words and the
number of articles in each section. It has four functions worth
knowing: `load_articles` reads the JSON, `count_words` counts every
word, `most_common` sorts the counts, and `render` builds the text.
Take a minute to read it. It is short, and nothing in it is a trick,
but one part of it is slower than it looks.

## The environment

The workshop first sets up an environment of its own, so that the
`python` in the terminal below the editor is Python 3.15, the one with
the profiler in it. Nothing is installed into it. Click the step to
create it; it takes a moment.

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

```{hint}
:title: If the check fails
The environment is created by the step above; click it again if it
did not finish, which does no harm. The check runs the environment's
`python` and asks it to import `profiling.sampling`, which only a
Python 3.15 has. The banner at the top of this panel offers the same
step on every page.
```
