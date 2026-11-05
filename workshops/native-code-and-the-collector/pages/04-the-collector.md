---
title: The collector
requires: [verify:gc-profile]
---

# The collector

Python frees most objects the moment the last reference to them
goes. That cannot free a group of objects which refer to each other:
each still has a reference, from another of the group, though
nothing outside can reach any of them. Finding those is the job of
the garbage collector, and it does it by looking through the
objects that can hold references, lists, dictionaries, instances,
and working out which can still be reached.

It runs when the program has made enough new objects of that kind
since it last ran, whatever the program was doing at the time. So
its cost lands on the lines that make objects, in proportion to how
many they make and how many objects there are to look through.

Open {open}`gazette/graph.py`. It could have been written to give
the collector work. Every `Story` has a list of its `Link`s and
every `Link` refers to its two `Story`s, so the whole graph is
objects referring to each other, two hundred thousand links of
them. And `main` builds the graph eight times over, for the paper
as it stood on each of the last eight days, letting go of each
graph as it builds the next. Only the collector can free them.

The profiler marks the collector's samples without being asked.

```{execute}
:id: profile-gc
:session: shell
:title: Profile the graph builder
:wait: prompt
python -m profiling.sampling run -l 8 --no-summary gazette/graph.py | tee gc.txt
```

The program's last line says how many times the collector ran:
about eighteen hundred, in the few seconds the program took. The
count is much the same on any machine, since the collector is set
off by the number of objects made and not by the clock.

In the table, near the top, is a row with `~` for its file, `0` for
its line and `<GC>` for its function. It stands for samples taken
while the collector was running. It has between a tenth and a
quarter of the samples, and its two counts are equal, since the collector
calls nothing of yours.

Like `<native>`, it is a marker added to the stack, on top of the
line the collector interrupted. In a flame graph it would be a box
beneath `Link.__init__` and beneath line 70 of `build_graph`, the
two places in this program that make the most objects. That is
worth having: it says which lines are paying for the collector, and
those are the lines to change if the collector is the problem.

```{verify}
:id: gc-profile
:label: The table has a row for the collector
:trigger: after:profile-gc
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

rows = shares("gc.txt", "command")
assert "build_graph" in rows, "The table has no row for build_graph; was the program gazette/graph.py?"
assert rows.get("<GC>", 0.0) > 1, (
    "The table has no row for <GC>, or nearly nothing in it; run the command as it is written, with no --no-gc"
)
print(f"{rows['<GC>']:.0f}% of the samples were taken while the collector was running")
```
