---
title: A baseline
requires: [verify:baseline-recorded]
---

# A baseline

A comparison needs something to compare with, recorded *before* the
change, since afterwards the program that made it is gone. Record
the report generator as it is.

```{execute}
:id: record-baseline
:session: shell
:title: Record the baseline
:wait: prompt
python -m profiling.sampling run -r 10khz --binary -o baseline.bin gazette/report.py
```

Two options there need a reason.

**`--binary`** writes the profile in the profiler's own compact
format, which is the only one a comparison can be made against. It
keeps every sample, so the same file can also be turned into a
table, a flame graph or a heatmap later with `replay`, as often as
you like.

**`-r 10khz`** takes ten thousand samples a second where the
profiler would otherwise take one thousand. The program takes nearly
two seconds now, and a thousand a second is plenty for that. Once
fixed it will take a tenth of a second or so, which at a thousand a
second is about a hundred samples, too few to say anything about
the smaller functions. Profiles that are to be compared should be
made the same way, so the rate is chosen for the shortest of them
and used for all.

Now read the baseline as a table. `replay` does not run the program.
It reads the recording. The `| tee baseline.txt` belongs to the
shell, and keeps a copy of the table for the check below.

```{execute}
:id: replay-baseline
:session: shell
:title: Print the baseline as a table
:wait: prompt
python -m profiling.sampling replay -l 6 --no-summary baseline.bin | tee baseline.txt
```

One row has more than nine tenths of the samples: line 44 of
`count_words`, the search of the list. Below it, with a fiftieth,
is `syllables`. Note the time beside `syllables`, in the `tottime`
column: a little under four hundredths of a second. It will matter
later.

```{verify}
:id: baseline-recorded
:label: baseline.bin is recorded, and count_words has most of its samples
:trigger: after:replay-baseline
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

assert Path("baseline.bin").exists() and Path("baseline.bin").stat().st_size > 0, (
    "No baseline.bin yet: run the first command above, which records it"
)
rows = shares("baseline.txt", "replay command")
share = rows.get("count_words", 0.0)
assert share > 60, (
    f"count_words has {share:.0f}% of the baseline's samples; expected most of them. "
    "Was the baseline recorded before gazette/report.py was changed? Restart the workshop to begin again"
)
print(f"baseline.bin is recorded; count_words has {share:.0f}% of its samples")
```
