---
title: For your own scripts
requires: [verify:hottest-ran]
---

# For your own scripts

Sooner or later you want a profile as data: to fail a build when a
function's share doubles, to put a number on a dashboard, to hand
to a program that will summarise it. The HTML is for eyes and the
gecko file is another tool's format. `--jsonl` is the format for
programs: JSON Lines, one JSON object to a line.

```{execute}
:id: replay-jsonl
:session: shell
:title: Replay the recording as JSONL
:wait: prompt
python -m profiling.sampling replay --jsonl -o profile.jsonl report.bin
```

```{execute}
:id: show-jsonl
:session: shell
:title: The start of each line of profile.jsonl
:wait: prompt
cut -c 1-150 profile.jsonl
```

Five lines, and the `type` at the start of each says what it is.
`meta` has the interval between samples, in microseconds.
`string_table` has every file and function name, each with a number.
`frame_table` has the frames, each a file, a function and a line,
with the names given as numbers from the string table. `agg` is the
profile: for each frame, `self`, the samples in which it was running,
and `cumulative`, the samples in which it was on the stack, which are
the two halves of the table's `nsamples` column. `end` says the file
is complete. On a larger profile the tables are split over several
lines of the same type, so a reader takes the lines as they come and
adds to what it has.

{open}`hottest.py`, in the tab beside the report, is such a reader,
and its one function is seventeen lines. It fills a dictionary of
strings and a dictionary of frames, collects the `agg` entries, sorts
them by `self`, and prints the top ten with each count as a share of
the total.

```{execute}
:id: run-hottest
:session: shell
:title: Print the ten hottest lines from the JSONL
:wait: prompt
python hottest.py profile.jsonl
```

Line 36 of `count_words` with about four fifths and line 34 with most
of the rest, as in every other view of this recording. A line can be
listed twice, as one of `tokenise`'s may be: a frame in this format
is a line and the span of columns on it that was running, so a line
that does two things can be two frames.

```{verify}
:id: hottest-ran
:label: The JSONL profile puts count_words at the top
:trigger: after:run-hottest
:substrate: shell
test -s profile.jsonl || { echo "No profile.jsonl yet; run the replay --jsonl command above"; exit 1; }; python hottest.py profile.jsonl | head -n 3 | grep -q count_words && echo "hottest.py reads profile.jsonl and finds count_words at the top" || { echo "hottest.py did not list count_words in its first three lines; was report.bin recorded from gazette/report.py?"; exit 1; }
```
