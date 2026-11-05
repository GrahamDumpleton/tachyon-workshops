---
title: Which line?
requires: [quiz:which-line, verify:heatmap-written]
---

# Which line?

Every sample the profiler takes records, for each function on the
stack, the line that function had reached. The table keeps that, which
is why one function can fill several of its rows. The heatmap keeps it
too and puts each count where it belongs, beside the line.

Before it does, predict. Look at the loop in `count_words` in
{open}`gazette/report.py`, lines 29 to 44. Each of these lines runs
for every article or for every word, and one of them takes most of
the run.

```{quiz}
:id: which-line
question: Which line of `count_words` has most of the samples?
options:
  - { text: "Line 33, `text = text.translate(punctuation)`, which rewrites every character of every article", explanation: "It does, once per article, in C. Two thousand articles are a few milliseconds of work." }
  - { text: "Line 34, `for word in text.split():`, since splitting makes a new string for every word", explanation: "Splitting is one call per article and quick. The loop it feeds runs a hundred and eighty thousand times, so look at what each turn of the loop does." }
  - { text: "Line 40, `if entry not in seen:`, which searches a list", correct: true }
  - { text: "Line 43, `sections[entry] += 1`, since it updates a dictionary for every word", explanation: "A dictionary finds its key in one step however large it grows. The line that takes longer as the program goes on is the one that searches a list." }
explanation: "`seen` is a list, and `in` on a list compares the entry with every item until it finds it. There are about seven and a half thousand different entries, so each of a hundred and eighty thousand words costs thousands of comparisons."
```

Now have the profiler draw it. `--heatmap` writes a directory of web
pages, and `-o` names the directory.

```{execute}
:id: profile-heatmap
:session: shell
:title: Profile the report and write a heatmap
:wait: prompt
python -m profiling.sampling run --heatmap -o heatmap gazette/report.py
```

The report prints as usual, since the profiler only watches. Then the
profiler's own lines: how many samples it took, and that the heatmap
was written to `heatmap/` with an index and three source files
analysed. Three, for a program of one file, because the profiler
records every function on the stack and some of those are in the
standard library. The next page opens the index and shows which.

```{verify}
:id: heatmap-written
:label: The heatmap has an index and a page for report.py
:trigger: after:profile-heatmap
:substrate: shell
test -s heatmap/index.html && grep -q "gazette/report.py - Heatmap" heatmap/file_0000.html && echo "heatmap/ holds index.html and a page for gazette/report.py" || { echo "heatmap/index.html or the page for report.py is missing; run the --heatmap command above"; exit 1; }
```
