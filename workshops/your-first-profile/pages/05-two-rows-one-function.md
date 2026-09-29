---
title: Two rows, one function
requires: [quiz:two-rows, verify:two-rows-in-file]
---

# Two rows, one function

Look again at the top of the table. `count_words` is there twice:

```
      1261/1261      80.1         1.261      80.1         1.261  report.py:36(count_words)
        290/290      18.4         0.290      18.4         0.290  report.py:34(count_words)
```

If you have used `cProfile`, this is the first thing that looks
wrong. There, a function is one row, keyed by the line its `def` is
on. Here a row is a file, a *line* and a function, and the line is
the one that was executing when the sample was taken. A function
busy on two different lines gets two rows, and so does one that was
waiting on two different lines, which is why `main` can have a row
for line 62 and another for line 61. The summary below the
table adds them back up by function, which is why it can say that
`count_words` has 98% of the direct samples in one line.

Find the two lines in {open}`gazette/report.py`. Line 36 is the
dictionary comprehension that calls `words.count(word)` once for each
distinct word, and `words.count` walks the whole list of a hundred and
sixty thousand words each time. Line 34 is `if word not in unique`,
which walks the list of distinct words once for each of those hundred
and sixty thousand. Both are quadratic, and between them they are the
report: the profiler has not only named the function but pointed at
the lines, and the fifth of these workshops paints those counts onto
the source itself.

```{quiz}
:id: two-rows
question: Why does `count_words` appear on two rows of the table?
options:
  - { text: "The function was called twice", explanation: "It was called once. A sampling profiler does not count calls at all; it counts how often it saw a line running." }
  - { text: "Each row is a line of the function, and samples landed on two of its lines", correct: true }
  - { text: "One row is the function and the other is a nested function of the same name", explanation: "There is no nested function. Look at the line numbers: 34 and 36 are both inside `count_words`." }
  - { text: "The profiler samples each thread separately and there were two threads", explanation: "The report has one thread, and by default only the main thread is sampled anyway." }
explanation: "Each row is a file, a line and a function, and the line is the one running when the sample landed. Two busy lines, two rows; the summary adds them back up."
```

```{verify}
:id: two-rows-in-file
:label: profile.pstats has more than one row for count_words
:trigger: after:profile-to-file; page-enter
import pstats
from pathlib import Path

assert Path("profile.pstats").exists(), "No profile.pstats yet: go back a page and run the command that writes it"
stats = pstats.Stats("profile.pstats")
lines = sorted(key[1] for key in stats.stats if key[2] == "count_words")
assert len(lines) >= 2, f"Only line {lines} of count_words was sampled; a run with more samples would show two"
print(f"count_words was sampled on lines {', '.join(map(str, lines))}")
```
