---
title: Reading the table
requires: [verify:pstats-written]
---

# Reading the table

The table has six columns. Two rows of the one in your terminal show
what every column means: the row for `count_words` at the top, where
the work is, and the row for `main` on line 62, the line that calls
it. The numbers below are from one run; yours differ in the details
and agree in the shape.

```
       nsamples   sample%   tottime (s)    cumul%   cumtime (s)  filename:lineno(function)
      1261/1261      80.1         1.261      80.1         1.261  report.py:36(count_words)
         2/1577       0.1         0.002      99.7         1.577  report.py:62(main)
```

`nsamples` is two numbers. The first is the *direct* count: the
samples in which this function was the one actually running, at the
top of the stack. The second is the *cumulative* count: the samples in
which it was anywhere on the stack, running or waiting for something
it had called. `count_words` reads `1261/1261`: every time it was on
the stack it was the one running, because it calls nothing slow.
`main` on line 62 reads `2/1577`: it was on the stack for almost every
sample, since line 62 is `counts = count_words(articles)` and
everything slow happens inside that call, and it was the function
running in a sample or two at most, because `main` only calls the
others.

```{hint}
:title: If the main row is not in your table, or there are two
The row says `report.py:62(main)`, a line as well as a function.
`main` has other lines, and each that was sampled has a row of its
own: line 61, `articles = load_articles(path)`, is on the stack for
the few milliseconds the JSON takes to parse and shows a handful of
samples, `0/6` or so. The table is sorted by direct samples, and a
row with none can fall below the fifteen shown, so on some runs the
line-62 row is missing and the line-61 row is there instead. The next
page is about why one function has several rows, and the page after
it sorts the table so the outer functions come first.
```

`sample%` is the direct count as a share of all the samples: four in
five for `count_words`. `tottime` is the same fact in seconds, and
this is the arithmetic the whole profiler rests on: a sample every
millisecond, 1,261 samples, so about 1.261 seconds. The profiler
never timed anything. It counted how often it saw the function and
multiplied by the interval between looks.

`cumul%` and `cumtime` are the cumulative count the same two ways:
the time the function was anywhere on the stack. For `main` that is
nearly the whole run. For a function that does its work by calling
others, the cumulative columns are where its cost shows, and the
direct columns stay near zero.

Below the table, the profiler picks out three kinds of function for
you. *Hot spots* are functions whose direct count is nearly their
cumulative count, which is where the work is: `count_words`. *Indirect
calls* are the opposite, functions almost always on the stack and
rarely running: `main`, and the interpreter's own `_run_code` that
started the script. *Call magnification* is the ratio between the two.
Under a hundred rows this summary is a convenience; with hundreds it
is where to start.

## Keeping the table

The table went to the terminal. Add `-o` and a file name and the
profiler writes the same data to a file instead, in the `pstats`
format that Python's `pstats` module reads, which is how this
workshop checks your work and how the sixth of these workshops keeps
profiles for later.

```{execute}
:id: profile-to-file
:session: shell
:title: Profile the report again, saving the table to a file
:wait: prompt
python -m profiling.sampling run -o profile.pstats gazette/report.py
```

```{verify}
:id: pstats-written
:label: profile.pstats holds a profile in which count_words dominates
:trigger: after:profile-to-file
import pstats
from pathlib import Path

assert Path("profile.pstats").exists(), "No profile.pstats yet: run the command above, which writes it in this directory"
stats = pstats.Stats("profile.pstats")

def direct_time(name):
    return sum(row[2] for key, row in stats.stats.items() if key[2] == name)

total = stats.total_tt
count_words = direct_time("count_words")
assert total > 0.2, f"The profile holds only {total:.2f} seconds of samples; did the report run to the end?"
assert count_words > 0.5 * total, (
    f"count_words has {count_words / total:.0%} of the time in this profile; "
    "expected most of it. Was a different program profiled?"
)
print(f"{count_words / total:.0%} of {total:.2f} seconds is in count_words")
```

```{hint}
:title: What the check reads
The check opens `profile.pstats` with `pstats.Stats`, adds up the
direct time of every row whose function is `count_words`, and expects
it to be more than half the total. It does not run the profiler
itself, and it never looks at an exact count, because the next run
will have a different one.
```
