---
title: The fix
requires: [verify:fixed, quiz:colour-of-syllables, verify:fix-compared]
---

# The fix

The fix to `count_words` is to let a `Counter` keep the counts for
each section, as one already does for the counts over all, and to
drop the list.

```{file-write}
:id: write-fix
:title: Replace report.py with the fixed version
:path: gazette/report.py
:from: fixed/report.py
:open: true
```

```{verify}
:id: fixed
:label: count_words no longer keeps a list of what it has seen
:trigger: after:write-fix
:substrate: shell
grep -q "seen" gazette/report.py && { echo "gazette/report.py still has the seen list; run the action above"; exit 1; } || echo "gazette/report.py has no seen list"
```

Record the fixed program as you recorded the baseline, at the same
rate, and keep the recording. It will be the baseline for the next
change.

```{execute}
:id: record-fixed
:session: shell
:title: Record the fixed program
:wait: prompt
python -m profiling.sampling run -r 10khz --binary -o fixed.bin gazette/report.py
```

The report is built in a tenth of a second, where it took nearly
two. So the fix worked, by the stopwatch. Now the comparison.
Nothing but `count_words` was changed. `syllables`, for one, is the
same code doing the same work on the same articles.

```{quiz}
:id: colour-of-syllables
question: In the comparison of the fixed program with the baseline, what colour will `syllables` be?
options:
  - { text: "Grey, since it was not changed and takes as long as it did", explanation: "It does take as long as it did, about four hundredths of a second. The colours do not compare times in that sense." }
  - { text: "Blue, since the program as a whole is quicker", explanation: "A box is compared with the same function in the baseline, not with the program as a whole." }
  - { text: "Red, since it has a far larger share of the run than it had", correct: true }
explanation: "The profiler scales the baseline to the length of the new run before it compares. `syllables` had a fiftieth of a run of two seconds and has three tenths of a run of a tenth of a second, and that is what is coloured."
```

`replay` can draw the comparison from the two recordings, with no
need to run the program again.

```{execute}
:id: compare-fix
:session: shell
:title: Compare the fixed program with the baseline
:wait: prompt
python -m profiling.sampling replay --diff-flamegraph baseline.bin -o diff.html fixed.bin
```

```{file-open}
:id: open-diff
:title: Open diff.html in the HTML viewer
:path: diff.html
:factory: HTML Viewer
:area: desk
```

`count_words` is blue, as it should be. Everything else that has any
width is red: `hardest`, `reading_ease`, `syllables`, the loading of
the articles. Hold the mouse over `syllables`. The tooltip says its
direct time was about three milliseconds in the baseline and is
nearly forty now, up by more than a thousand percent.

You noted its time in the baseline on the second page, and it was
nearly forty milliseconds then too. The three milliseconds is that
figure scaled down. Before comparing, the profiler multiplies every
count in the baseline by the length of the new profile over the
length of the old, here about a fourteenth, so that the two add up
to the same total. What the colours compare, then, is each
function's share of its run.

That is the right comparison when the two runs did different
amounts of work, a server profiled for thirty seconds on Monday and
sixty on Tuesday. It is a misleading one when the change was meant
to make the run shorter and did. The flame graph here is not saying
that the fix made `syllables` slower. It is saying that `syllables`
is now a large part of what is left.

Print the fixed program's table, to have the times themselves.

```{execute}
:id: replay-fixed
:session: shell
:title: Print the fixed program's profile as a table
:wait: prompt
python -m profiling.sampling replay -l 6 --no-summary fixed.bin | tee fixed.txt
```

`syllables` is first, with the same few hundredths of a second it
had in the baseline. The tables are where to compare times. The
differential flame graph is where to compare shapes.

```{verify}
:id: fix-compared
:label: The fixed program is recorded and compared, and count_words has lost its lead
:trigger: after:replay-fixed
import re
from pathlib import Path

def shares(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command} above, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    rows = {}
    for line in text.splitlines():
        row = re.match(r"\s*\d+/\d+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+\S+:-?\d+\((.+)\)\s*$", line)
        if row:
            rows[row.group(2)] = rows.get(row.group(2), 0.0) + float(row.group(1))
    assert rows, f"{path} has no table in it; did the command fail?"
    return rows

for name in ("fixed.bin", "diff.html"):
    assert Path(name).exists() and Path(name).stat().st_size > 0, (
        f"No {name} yet: run the command above that writes it"
    )
assert "baseline_samples" in Path("diff.html").read_text(encoding="utf-8"), (
    "diff.html is not a differential flame graph; was it written with --diff-flamegraph baseline.bin?"
)
before = shares("baseline.txt", "replay command on the second page").get("count_words", 0.0)
after = shares("fixed.txt", "last command").get("count_words", 0.0)
assert after < before - 20, (
    f"count_words has {after:.0f}% of the samples in fixed.txt and had {before:.0f}% in the baseline; "
    "expected far less. Was fixed.bin recorded after report.py was replaced?"
)
print(f"count_words had {before:.0f}% of the baseline's samples and has {after:.0f}% of the fixed program's")
```
