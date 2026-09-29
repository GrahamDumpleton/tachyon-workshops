---
title: Sorting and trimming
requires: [quiz:numbers-move]
---

# Sorting and trimming

The table is sorted by direct samples and shows fifteen rows, which
is right for finding a hot spot and wrong for reading a program's
shape, since the rows that hold the shape, the outer functions with
no direct samples, sink to the bottom or off it. Two options change
that. `--sort cumtime` orders by cumulative time, so the outermost
functions come first and the table reads like the call tree from the
root down; `-l` limits the rows; and `--no-summary` drops the legend
and the three lists, which you know how to read now.

```{execute}
:id: profile-sorted
:session: shell
:title: The six outermost rows, by cumulative time
:wait: prompt
python -m profiling.sampling run --sort cumtime -l 6 --no-summary gazette/report.py
```

Now the first rows are the interpreter's `_run_code` and
`_run_module_as_main`, the script's `<module>` line and `main` on
line 62, each with nearly every sample in its cumulative count and
almost none direct, and `count_words` arrives fifth, the first row
where the two counts agree. The other sort keys are `nsamples` (the
default), `tottime`, `sample-pct`, `cumul-pct`, `nsamples-cumul` and
`name`.

## The numbers move

Compare this run's first line, and its counts, with the run two pages
back. The sample count is different, the count on every row differs
by a few or a few dozen, and a row with one direct sample there may
have none here. This is not the profiler being careless. A sample is a
glance at a random instant, and two sets of sixteen hundred glances
agree on the proportions and not on the counts, the way two polls
agree on who is ahead and not on the exact percentage. `count_words`
is about four fifths of both runs; whether it is 79% or 81% is noise.
More samples agree better: a longer run, or a higher sampling rate,
which the last of these workshops turns into arithmetic.

So the habit for reading a sampling profile is to read shapes and
ranks, not counts, and it is the habit these workshops follow: every
check reads which functions appear and how they rank, and never an
exact number.

```{quiz}
:id: numbers-move
question: Two runs of the profiler on the same program give `count_words` 1,261 samples and then 1,288. What should you conclude?
options:
  - { text: "The second run was slower and the program should be investigated", explanation: "Twenty-seven samples in sixteen hundred is under two percent, which is the ordinary difference between two sets of random glances." }
  - { text: "Nothing: both say `count_words` has about four fifths of the time, which is the finding, and the counts are noise", correct: true }
  - { text: "The profiler is unreliable and the tracing profiler should be used instead", explanation: "The tracer would give the same call counts each time, but it would also slow the program four-fold, as the next workshop shows. Sampling is reliable about proportions, not counts." }
  - { text: "The first run missed 27 samples because of its error rate", explanation: "Discarded samples are not the reason; the runs took slightly different times and the glances fell at different instants. The error rate is a separate matter, for the third workshop." }
explanation: "Sampling profiles agree on shapes and ranks, not on counts. Read the proportion and the ranking, and treat a few percent of difference between runs as the noise it is."
