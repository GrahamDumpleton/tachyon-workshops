---
title: Profile it
requires: [quiz:hottest-function]
---

# Profile it

Tachyon is run as a module, `python -m profiling.sampling`, with a
command saying what to profile. `run` starts a program and profiles it
from its first line to its last. Everything after the program's name
is passed to the program unchanged, so a script that takes arguments
takes them here too.

```{execute}
:id: profile-report
:session: shell
:title: Run the report under the profiler
:wait: prompt
python -m profiling.sampling run gazette/report.py
```

The report prints exactly as before, in the same time, and then the
profiler prints its own output below it. Read the first three lines
of that output first. These are from the run this page was written
from:

```
Captured 1582 samples in 1.58 seconds
Sample rate: 1000.00 samples/sec
Error rate: 0.44
```

A thousand samples a second, for as long as the program ran, which
here was 1.58 seconds and so about sixteen hundred samples. Your
numbers will differ: a little from one run to the next, because a
sample is a glance at whatever was happening at that instant, and a
good deal from one machine to another, because a slower machine
runs the report for longer and so takes more samples of it. The
first two lines always agree with each other, since the samples are
the seconds multiplied by the rate. The error rate is the
share of samples the profiler threw away because the stack was
changing under it as it read; under one percent is normal, and the
third workshop in these workshops says what it means.

Below the header comes the table, headed `Profile Stats`. Each row is
a line of code the profiler caught running, and the rows are sorted
so that the line caught most often is at the top. Look at the last
column, which names the file, the line and the function, and answer:

```{quiz}
:id: hottest-function
question: Which function is on the top row of the table?
options:
  - { text: "`load_articles`", explanation: "The JSON parser appears far down, in `decoder.py`, with a sample or two." }
  - { text: "`count_words`", correct: true }
  - { text: "`render`", explanation: "`render` has about one sample: formatting a few lines is over before the profiler looks twice." }
  - { text: "`main`", explanation: "`main` is in the table, but with zero direct samples: it was always on the stack and never the function running. The next page explains that column." }
explanation: "`count_words` fills the top rows, with about four samples in five. The next page reads the rest of the row."
```
