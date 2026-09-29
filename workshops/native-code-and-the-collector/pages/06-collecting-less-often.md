---
title: Collecting less often
requires: [verify:changed, verify:once-profile]
---

# Collecting less often

To see what the marker measures, take most of the collector's work
away and profile again. This is a demonstration, and not advice. The
change tells the collector not to run by itself while the graphs are
built, and runs it by hand once for each graph, when the graph is
finished with and everything in it is ready to be freed.

```{file-write}
:id: write-change
:title: Replace graph.py with a version that collects once for each graph
:path: gazette/graph.py
:from: fixed/graph.py
:open: true
```

```{verify}
:id: changed
:label: graph.py turns the collector off and runs it by hand
:trigger: after:write-change
:substrate: shell
grep -q "gc.disable()" gazette/graph.py && grep -q "gc.collect()" gazette/graph.py && echo "graph.py calls gc.disable() and gc.collect()" || { echo "gazette/graph.py is not the changed version; run the action above"; exit 1; }
```

The change is in `main`: `gc.disable()` before the loop, and at the
end of each turn of it `del` to let go of the graph and
`gc.collect()`, on line 89, to free it.

```{execute}
:id: profile-once
:session: shell
:title: Profile the changed graph builder
:wait: prompt
python -m profiling.sampling run -l 12 --no-summary gazette/graph.py | tee once.txt
```

The collector ran about twenty times and not eighteen hundred, and
the program is quicker by around half a second. Before, each of
those runs looked through the graph as it grew and found nearly
nothing to free, since the graph being built was all still in use.

Now find the row for line 89 of `main` in the table you have. That
line is `gc.collect()` and nothing else, so every sample on it was
taken while the collector ran. If the marker worked as described,
the table would say so in two ways.

- There would be a `<GC>` row, with about as many samples as line
  89 has in its second count.

- Line 89 would have next to nothing in its first count, which is
  the samples in which the line was the top of the stack, and
  nearly everything in its second, which also counts those with
  something on top of it. With the marker on top, the line is not
  the top.

What you have depends on the run. Often there is no `<GC>` row at
all, and the two counts of line 89 are equal, something like
`418/418`: a quarter of the run spent in the collector, and not one
sample of it marked. Other runs mark some, and then there is a
`<GC>` row and the first count is smaller than the second by that
many. On the release these workshops use the marker is left off
many of the collector's samples, and sometimes all of them.

The same will have been true of the first table. Its `<GC>` row
held the samples that were marked, and the rest of the collector's
samples were counted on line 70 and the other lines it
interrupted, as though those lines had been slow themselves.

So read `<GC>` as the least the collector took. When the row is
large the collector is certainly a cost. When it is small or
missing, the collector may still be one, and the way to find out is
the one used here: change how often it runs, and measure the
program.

As for the change itself, turning the collector off is safe only
where you know when the garbage is made and collect it yourself, as
this `main` does. The better fix for a program like this is not to
build eight graphs where one, added to each day, would do.

```{verify}
:id: once-profile
:label: The changed program was profiled, and the collector ran far less often
:trigger: after:profile-once
import re
from pathlib import Path

file = Path("once.txt")
assert file.exists(), "No once.txt yet: run the command above, which writes it"
text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
ran = re.search(r"the collector ran (\d+) times", text)
assert ran, "once.txt does not say how often the collector ran; did the graph builder fail?"
before = re.search(r"the collector ran (\d+) times", Path("gc.txt").read_text(encoding="utf-8")) if Path("gc.txt").exists() else None
assert int(ran.group(1)) < 200, (
    f"The collector ran {ran.group(1)} times; expected a few dozen. Replace graph.py with the action above and profile again"
)
print(f"The collector ran {ran.group(1)} times"
      + (f", where before it ran {before.group(1)}" if before else ""))
```
