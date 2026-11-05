---
title: Welcome
requires: [verify:env-ready]
---

# Profiling a test suite

A test suite is a program like any other, and it is the program a
developer runs most. When it takes minutes, people run it less, and
then not at all until the last moment. A slow suite is nearly always
slow for a few reasons repeated many times, and they are seldom in
the code being tested. They are in how the tests are set up.

pytest can list the slowest tests for you, with `--durations`. That
says *which* tests are slow. It does not say *why*, and it cannot
see a cost that is spread thinly over every test. A profile of the
whole run can.

A *sample* is one reading of the program's stack, and the profiler
takes a thousand a second. A flame graph draws the samples as boxes,
one for each function, as wide as its share of the samples, with
the functions it called beneath it. A heatmap writes the samples
beside the lines of the source.

## The suite

The gazette, a small newsroom, has a package of three modules and a
suite of 118 tests for them, in four files that are open in the
editor.

- {open}`tests/conftest.py` holds the *fixtures*, the things tests
  ask for by naming them as arguments: `articles`, the gazette's two
  thousand articles, and `db`, a sqlite database holding them.

- {open}`tests/test_store.py` tests the database: fifteen tests,
  each of which asks for `db`.

- {open}`tests/test_refresh.py` tests a word count that is made on a
  thread in the background.

- {open}`tests/test_dates.py` tests how dates are printed, on a
  hundred of the articles.

Every test passes. The suite takes several seconds, four or five
where this page was written and more on a slower machine, which is
long for 118 tests that do very little, and would be minutes if the
gazette had the thousands of tests a real project has.

## The environment

Create the workshop's environment. It installs pytest, and makes
the `python` in the terminal Python 3.15, the one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15, with the profiler and pytest
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling, pytest; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling and pytest', pytest.__version__)"
```
