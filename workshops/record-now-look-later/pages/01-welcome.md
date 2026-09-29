---
title: Welcome
requires: [verify:env-ready]
---

# Record now, look later

Each time you have asked the profiler for a view so far, it has run
the program again: once for the table, again for the flame graph,
again for the heatmap. That is fine for a report that takes two
seconds and can be run at will. It is no use for the run you cannot
repeat: the job that was slow last night and is quick this morning,
the service in production that you may watch for thirty seconds, the
test in CI that fails one time in fifty. And it is awkward when the
profile is for someone else, who will have their own idea of how to
look at it.

The profiler's answer is to separate the two jobs. *Record* the
samples in a compact binary file, which is quick and needs no
decision about what you want to see. *Replay* the file later, as
often as you like and wherever you like, into any of the views. This
workshop records one profile and looks at it six ways.

## The program

{open}`gazette/report.py` is the report from the first of these
workshops. It counts the words in the gazette's two thousand
articles, and its `count_words` has a quadratic mistake on line 36
that takes a second and a half. The mistake is already found. The
subject here is the profile.

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
