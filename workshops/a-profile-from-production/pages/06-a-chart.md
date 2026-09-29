---
title: A chart
requires: [verify:chart-drawn, verify:pstats-read, quiz:chart-or-graph]
---

# A chart

A table of ten rows can be read. A chart can be read from across
the room, and put in a report for people who will never open a
flame graph. The next cell draws the same ten functions as bars,
Monday's and Friday's side by side.

```{cell-insert}
:id: insert-chart
:title: Add a cell that draws the chart, and run it
:path: analysis.ipynb
:tags: [chart]
:run: true
import matplotlib.pyplot as plt

names = hottest[::-1]
places = range(len(names))
figure, axes = plt.subplots(figsize=(9, 5))
axes.barh([place + 0.2 for place in places], [monday[name] / 1000 for name in names], height=0.4, label="Monday")
axes.barh([place - 0.2 for place in places], [friday[name] / 1000 for name in names], height=0.4, label="Friday")
axes.set_yticks(list(places), names)
axes.set_xlabel("seconds of thread time, in twenty seconds of load")
axes.set_title("The gazette's web site, before and after the fix")
axes.legend()
figure.tight_layout()
figure.savefig("chart.png", dpi=100)
plt.show()
```

```{verify}
:id: chart-drawn
:label: The chart is drawn, and saved as chart.png
:substrate: learner-kernel
:path: analysis.ipynb
:trigger: after:insert-chart
from pathlib import Path as _Path
if "figure" not in globals():
    print("The cell that draws the chart has not run: click the action above")
elif not _Path("chart.png").exists():
    print("The chart was drawn and not saved; run the cell again")
else:
    print(f"The chart has {len(figure.axes[0].patches)} bars, and is saved as chart.png")
"figure" in globals() and _Path("chart.png").exists() and len(figure.axes[0].patches) == 2 * len(hottest)
```

Scroll down in the notebook to see it. The longest bar is Monday's
`search`, and beside it Friday's is a stub. Every other pair is
near enough equal. That is the whole week's work, in a picture that
needs no explaining.

The cell also saved the chart as `chart.png`, which is the form a
report wants. And since it is a few lines of Python with two file
names in it, the same lines can be run as a script against every
night's recording, with last night's beside it, and made to
complain when a bar grows.

## The standard library's way

The profiler's default format, pstats, is the one Python's
profilers have always written, and the standard library reads it.
`replay` writes it from a recording like any other format.

```{execute}
:id: replay-pstats
:session: client
:title: Write Monday in the pstats format
:wait: prompt
python -m profiling.sampling replay --pstats -o monday.pstats monday.bin
```

```{cell-insert}
:id: insert-pstats
:title: Add a cell that reads it with pstats, and run it
:path: analysis.ipynb
:tags: [pstats]
:run: true
import pstats

stats = pstats.Stats("monday.pstats")
stats.sort_stats("tottime").print_stats(5)
rows = len(stats.stats)
```

```{verify}
:id: pstats-read
:label: The notebook has read monday.pstats
:substrate: learner-kernel
:path: analysis.ipynb
:trigger: after:insert-pstats
if "stats" not in globals():
    print("The cell that reads monday.pstats has not run: run the command above, then click the action")
else:
    print(f"monday.pstats has {rows} rows, one for each line that was sampled")
"stats" in globals() and rows > 0
```

The first lines of what it prints are in the words of a profiler
that counts calls, which this one does not, so pass over them. The
table is the one the profiler prints in a terminal, five rows of
it: samples in the first column, seconds in the second, a row for
each *line*, with `search` on line 101 at the top. It took three
lines to get, and tools that were written for Python's older
profilers can read the same file.

```{quiz}
:id: chart-or-graph
question: What does the flame graph of a recording tell you that the chart made from its JSON lines cannot?
options:
  - { text: "How many seconds each function took", explanation: "Both have that. The chart has it as a number on an axis, which is easier to read off." }
  - { text: "By what path the program reached each function: what called it, and what that was called by", correct: true }
  - { text: "Which functions changed between two recordings", explanation: "The chart shows that better, as pairs of bars in seconds." }
  - { text: "Which thread each sample came from", explanation: "Neither of these two shows that, though the flame graph has a filter for it. It is not what sets them apart." }
explanation: "The JSON lines hold counts for each frame, already added up, and the stacks they came from are gone. The flame graph keeps the stacks, so it can show that `search` was reached through Flask from a request thread. Use the chart to say how much, and the flame graph to say where."
```
