---
title: Welcome
requires: [verify:env-ready]
---

# Native code and the collector

The profiler reads Python's stack: one frame for each Python function
that has been called and has not returned. Two things that take time
in a Python program have no frame there.

One is **native code**, which is what the profiler calls anything not
written in Python: the built-in functions, the parts of the standard
library written in C, extension modules. When your function calls
`sorted` or `zlib.compress`, the interpreter runs C code, and no
Python frame is made for it.

The other is the **garbage collector**, the part of the interpreter
that finds objects which refer to each other and to which nothing
else refers, and frees them. Nothing calls it. It runs when the
program has made enough new objects, in the middle of whatever line
made the last one.

For each the profiler can add a marker to the stacks it records, a
box in the flame graph and a row in the table that stands for no
function: `<native>` and `<GC>`. This workshop looks at what each
marks and, as important, what it does not.

## The programs

{open}`gazette/index.py` is open in the editor. It builds the search
indexes for the gazette's site: for every word, the articles that use
it, best match first. `count_words` finds the words of each article,
`rank` sorts each word's articles with `relevance` as the key, and
`write` turns the index into JSON and compresses it. It does that
for the whole paper and again for every section, author and month.

{open}`gazette/graph.py`, in the tab beside it, builds the graph
behind the "related stories" box: a `Story` for each article and a
`Link` for each pair that share three keywords. It is the subject of
the second half of the workshop.

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
