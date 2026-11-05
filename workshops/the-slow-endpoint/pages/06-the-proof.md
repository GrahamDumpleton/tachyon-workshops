---
title: The proof
requires: [verify:search-fell, verify:diff-written, quiz:why-red]
---

# The proof

There are three ways to see what the fix did, and each says
something the others do not.

## What the readers saw

Print the two tables from `load.py`, before and after.

```{execute}
:id: compare-load
:session: client
:title: Print what the readers saw, before and after
:wait: prompt
cat load-before.txt load-after.txt
```

Much the same number of requests both times, since `load.py` keeps
to a pace, and the search has gone from the slowest page by far to
one among the others, from a tenth of a second to less than a
hundredth in the run this page was written from. This is the number
the readers care about, and no profile is needed for it. It says
that the fix worked and nothing of where.

If the first table has noticeably fewer requests than the second,
this machine is slow enough that the unfixed server could not keep
to the pace, and the readers queued for it. The fixed server was
then sent more in its twenty seconds, which is worth remembering
when you read the comparison below.

## Where the time went

Print the second recording as a table, beside the first.

```{execute}
:id: replay-after
:session: client
:title: Print the fixed server's table
:wait: prompt
python -m profiling.sampling replay -l 8 --no-summary fixed.bin | tee after.txt
```

In the run this page was written from, the rows for `search` were
these, before and after:

```
    29675/31308      46.9        29.675      49.5        31.308  web.py:101(search)
      1918/1918       5.9         1.918       5.9         1.918  web.py:105(search)
```

The third column is time, in seconds. It adds up every thread, so
it can come to more than the twenty seconds of the run. The slow
line had nearly thirty seconds of it, and the line that replaced it
has under two. The rows that were below `search` are still there
with much the time they had: the main thread in `select`, and
`front_page`, which is now the widest of the views and would be the
next to look at.

```{verify}
:id: search-fell
:label: search has a smaller share of the samples than it had
:trigger: after:replay-after
import re
from pathlib import Path

def shares(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command}, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    rows = {}
    for line in text.splitlines():
        row = re.match(r"\s*\d+/\d+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+(\S+):-?\d+\((.+)\)\s*$", line)
        if row:
            key = (row.group(2), row.group(3))
            rows[key] = rows.get(key, 0.0) + float(row.group(1))
    assert rows, f"{path} has no table in it; did the command fail?"
    return rows

before = shares("before.txt", "replay command on the second page").get(("web.py", "search"), 0.0)
after = shares("after.txt", "replay command above").get(("web.py", "search"), 0.0)
assert before > 0, "before.txt has no row for search; record the baseline again, on the second page"
assert after < before / 2, (
    f"search had {before:.0f}% of the samples before and has {after:.0f}% now; expected less than half as much. "
    "Was fixed.bin recorded after gazette/web.py was replaced? Go back a page and record it again"
)
print(f"search had {before:.0f}% of the samples before the fix and has {after:.0f}% after it")
```

## The two recordings, compared

A *differential flame graph* draws the newer recording and colours
each box by how it compares with the same function in the older
one.

```{execute}
:id: replay-diff
:session: client
:title: Compare fixed.bin with baseline.bin
:wait: prompt
python -m profiling.sampling replay --diff-flamegraph baseline.bin -o diff.html fixed.bin
```

```{verify}
:id: diff-written
:label: diff.html is written, a comparison with the baseline
:trigger: after:replay-diff
:substrate: shell
python -c "from pathlib import Path; f = Path('diff.html'); assert f.exists(), 'No diff.html yet: run the replay command above'; t = f.read_text(encoding='utf-8', errors='replace'); assert 'baseline' in t and 'search' in t, 'diff.html is not a comparison of the two recordings; run the replay command above again'; print('diff.html is written, fixed.bin compared with baseline.bin')"
```

```{file-open}
:id: open-diff
:title: Open diff.html in the HTML viewer
:path: diff.html
:factory: HTML Viewer
:area: desk
```

The shape is the fixed server's: `search` is a narrow box among
the views. The colours are the comparison. Blue is less than in the
baseline, red is more, grey is much the same.

`search` is blue, as it should be. A box is coloured by its own
time and not by what is beneath it, so the boxes above `search` do
not turn blue with it. Hold the mouse over `search` and the tooltip
gives its time in both recordings, as the profiler reckons them.

Nearly everything else is red: `front_page`, `health`, the
frameworks, and `select` in the main thread, which did nothing but
wait in either run. None of them was changed.

```{quiz}
:id: why-red
question: The main thread waited in `select` for nearly the whole of both recordings. Why is it red in the comparison?
options:
  - { text: "The fixed server was sent more requests, so the main thread accepted more connections", explanation: "`load.py` keeps to a pace, so the two servers were sent much the same requests. And a main thread with more connections to accept would spend less time waiting, not more." }
  - { text: "The colours compare shares of a recording, and the same wait is a larger share of a recording that has fewer samples", correct: true }
  - { text: "The fix made the main thread slower", explanation: "The fix changed `search`, which runs on the request threads. The main thread's time is the same in both tables." }
  - { text: "Red marks the functions that were not changed", explanation: "Grey is for what is much the same. Red is for a function with more time than in the baseline, as the profiler reckons it." }
explanation: "Before comparing, the profiler scales the baseline to the length of the newer recording, which here shrinks it, since the fixed server's threads were busy for less time in all. Everything the fix left alone then looks larger than it was. Read the colours as shares: blue shrank as a part of the whole, red grew. For the times themselves, read the tables."
```

So the comparison is the quickest way to see *which* functions
changed their part in the whole, and that the one you meant to
change is among them. The tables are where the amounts are.
