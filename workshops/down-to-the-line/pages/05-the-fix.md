---
title: The fix
requires: [verify:fixed, verify:hot-line-gone]
---

# The fix

`seen` exists so that `sections[entry]` can be set to zero the first
time an entry turns up. A `Counter` does that itself: a key that is
not there counts as zero. The function already uses one for `counts`.
Make `sections` a `Counter` too, and the list, the search and the
three lines that needed them go.

```{file-write}
:id: write-fix
:title: Replace report.py with the version that uses a Counter
:path: gazette/report.py
:from: fixed/report.py
:open: true
```

```{verify}
:id: fixed
:label: report.py counts sections with a Counter and has no list to search
:trigger: after:write-fix
:substrate: shell
grep -q "sections = Counter()" gazette/report.py && ! grep -q "not in seen" gazette/report.py && echo "count_words no longer searches a list" || { echo "gazette/report.py still has the seen list; click the action above to replace it"; exit 1; }
```

Read the new `count_words` in the editor: the loop now ends with
three lines, which build the entry and count it twice. Then draw the
heatmap again, into a directory of its own so the first one is kept.

```{execute}
:id: profile-after
:session: shell
:title: Profile the fixed report and write a second heatmap
:wait: prompt
python -m profiling.sampling run --heatmap -o heatmap-after gazette/report.py
```

The report is the same, word for word, and was built in a small
fraction of the time it took before. Put the two heatmap
pages for `report.py` one above the other: the first action makes
room by shrinking the terminal, the second brings back the page from
before, and the third opens the page from the new heatmap beneath
it. Two pages in one place would not do, since the viewer loads a
page again each time its tab is brought to the front, and you would
lose your place with every switch.

```{layout}
:id: make-room
:title: Make room for two pages
:name: compare
```

```{file-open}
:id: open-before-page
:title: Bring back the heatmap page for report.py as it was
:path: heatmap/file_0000.html
:factory: HTML Viewer
:area: desk
```

```{file-open}
:id: open-after-page
:title: Open the heatmap page for the fixed report.py below it
:path: heatmap-after/file_0000.html
:factory: HTML Viewer
:area: bottom
```

Both pages are called `file_0000.html`. The one above is the program
as it was, with the `seen` list in `count_words`; the one below is
the fixed program. Scroll each to `count_words`.

Before, one red line had nearly every sample and the rest were pale.
After, the colour is spread along the loop, with the lines that
count, test and split each taking a share. There is still a red
line, because the colour is relative and some line is always the
hottest in the file. Read its number: a few dozen samples at most,
where line 40 had well over a thousand. A program many times as
quick gave the profiler that many fewer samples, so expect the
numbers to move more between runs than they did. A profile like this one, with the
time shared between lines that each do a little necessary work, is
what a program with nothing left to fix looks like.

```{verify}
:id: hot-line-gone
:label: No line of the fixed report has most of the samples
:trigger: after:profile-after
import re
from pathlib import Path

def self_counts(path):
    page = Path(path)
    assert page.exists(), f"No {path} yet: run the --heatmap command above it"
    text = page.read_text(encoding="utf-8")
    assert "gazette/report.py - Heatmap" in text, f"{path} is not the page for gazette/report.py"
    counts = [int(re.sub(r"\D", "", n)) for n in re.findall(r'title="Self: ([^,"]*), Total:', text)]
    assert counts, f"{path} has no lines with samples"
    return counts

before = self_counts("heatmap/file_0000.html")
after = self_counts("heatmap-after/file_0000.html")
assert max(before) > 0.6 * sum(before), (
    "The first heatmap has no line with most of the samples; "
    "was it written before report.py was replaced?"
)
assert sum(after) < 0.5 * sum(before), (
    "The second heatmap has as many samples as the first; "
    "replace report.py with the action above, then profile it again"
)
print(f"Before, one line had {max(before) / sum(before):.0%} of the samples; "
      f"after, the whole file has {sum(after) / sum(before):.0%} as many")
```
