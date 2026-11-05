---
title: Welcome
requires: [verify:env-ready]
---

# Down to the line

A profile that says "the time is in `count_words`" is an answer when
`count_words` is three lines long. When it is twenty, it is the start
of a second question: which of the twenty? The table can answer, since
its rows are lines, but it answers as a list of line numbers to look
up one at a time. The *heatmap* answers on the source itself: the
profiler writes your program out as a web page with the number of
samples beside every line and the line coloured by that number, cold
to hot, so the slow line is the one you cannot miss.

It is the view to reach for when you know the file and want the line.
The flame graph is the other way round: you know the program is slow
and want the path that made it so.

## The program

{open}`gazette/report.py` is open in the editor. It prints a report
over the gazette's two thousand articles: the ten most common words,
and the most common word in each section. All the counting happens in
one function, `count_words`, which for every article joins the title
to the body, lowercases it, strips the punctuation, splits it into
words, skips the stop words and the numbers, and counts what is left
twice, once for the whole paper and once for the article's section.
Read it. It takes seconds, nearly two where this page was written
and more on a slower machine, which is far too long for a hundred
and eighty thousand words, and one of its lines is the reason.

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
