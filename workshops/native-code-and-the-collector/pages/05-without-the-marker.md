---
title: Without the marker
requires: [quiz:where-they-go, verify:nogc-profile]
---

# Without the marker

`--no-gc` tells the profiler not to add the marker. It changes
nothing about the program, where the collector runs exactly as
before, and nothing about which samples are taken.

```{quiz}
:id: where-they-go
question: With `--no-gc`, what happens to the samples that were in the `<GC>` row?
options:
  - { text: "They are dropped, and the table has that many fewer samples", explanation: "Every sample is kept. The option removes a marker from the stack, not the sample." }
  - { text: "They are counted on the lines the collector interrupted, which look that much slower", correct: true }
  - { text: "They move to a row for the `gc` module", explanation: "The collector is part of the interpreter, in C. The `gc` module is a way of talking to it and is not what runs." }
explanation: "The marker sits on top of the line that was running when the collector started. Without it, that line is the top of the stack and takes the sample."
```

```{execute}
:id: profile-nogc
:session: shell
:title: Profile the graph builder without the collector's marker
:wait: prompt
python -m profiling.sampling run --no-gc -l 8 --no-summary gazette/graph.py | tee nogc.txt
```

The `<GC>` row is gone and a row has come up the table in its
place: `Link.__init__`, which was far down before. Making a `Link`
is what most often sets the collector off, so that is where most of
its samples go when there is no marker to put them under.

Neither table is wrong. With the marker, a row's count is the time
the line took to do its own work. Without it, a row's count is the
time that passed on the line, the collector's included, which is
what the program's user waited for. Use `--no-gc` when you want the
profile to have the shape of your code alone, or to compare with a
profile from a tool that has no such marker.

```{verify}
:id: nogc-profile
:label: Without the marker the collector's samples are on the lines it interrupted
:trigger: after:profile-nogc
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
    assert rows, f"{path} has no table in it; did the graph builder fail?"
    return rows

rows = shares("nogc.txt", "--no-gc command")
assert "build_graph" in rows, "The table has no row for build_graph; was the program gazette/graph.py?"
assert "<GC>" not in rows, "nogc.txt has a row for <GC>; was it written with --no-gc?"
print("The table has no <GC> row; "
      f"Link.__init__ has {rows.get('Link.__init__', 0.0):.0f}% of the samples")
```
