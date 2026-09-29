---
title: Welcome
requires: [verify:env-ready]
---

# Sampling or tracing?

Python has had a profiler since before most of its users were born.
`cProfile` is a *tracing* profiler, also called deterministic: the
interpreter tells it about every function call and every return, and
it keeps count and keeps time. Python 3.15 reorganised the profilers
into one `profiling` package, following PEP 799, and `cProfile` is now
also `profiling.tracing`, beside the new sampling profiler,
`profiling.sampling`, that the first workshop used. This workshop
runs one program under both, so you can see what each knows, what
each costs, and which to reach for.

## The program

{open}`gazette/report.py` is the word-count report from the first
workshop, rewritten the way a tidy program would be: the quadratic
counting is gone, and instead every word passes through a function
that lowercases it, a function that drops stop words, a function that
strips its suffix, and a function that records it, and every article
has its reading ease scored by counting the syllables in every word,
one letter at a time. It does more than the first version and does
it in a fifth of a second. What matters for this workshop is how it
does it: in about four million small function calls.

## The environment

Create the workshop's environment, which installs nothing and makes
the `python` in the terminal Python 3.15, with both profilers in it.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15 and has both profilers
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling, profiling.tracing; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling and profiling.tracing')"
```
