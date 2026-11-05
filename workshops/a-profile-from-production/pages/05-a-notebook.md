---
title: A notebook
requires: [verify:profiles-loaded, verify:table-printed]
---

# A notebook

A notebook is a good place to ask questions of a profile, since
each question is a few lines and the answer stays on the page
beneath it. The action makes one, on the workshop's Python, with a
heading in it, and opens it above the terminals.

```{notebook-create}
:id: create-notebook
:title: Create the notebook
:path: analysis.ipynb
:area: desk
- markdown: |
    # The gazette, Monday and Friday

    Two recordings of the web site under the same load, before and
    after the search was fixed.
```

## Load the two profiles

The first cell reads a file of JSON lines and gives back the
samples of each function. It gathers the tables of names and
frames, adds up the `self` counts of each frame, and then puts
together the frames that are lines of one function, since the
question is about functions. A function is named with its file, as
`search (web.py)`, so that two of the same name in different files
stay apart.

```{cell-insert}
:id: insert-load
:title: Add a cell that loads the two profiles, and run it
:path: analysis.ipynb
:tags: [load]
:run: true
import json
from collections import Counter
from pathlib import Path


def load(path):
    """Read a profile written as JSON lines: the samples of each function, and the total."""
    strings, frames, samples, total = {}, {}, Counter(), 0
    with open(path, encoding="utf-8") as lines:
        for line in lines:
            record = json.loads(line)
            if record["type"] == "string_table":
                for entry in record["strings"]:
                    strings[entry["str_id"]] = entry["value"]
            elif record["type"] == "frame_table":
                for entry in record["frames"]:
                    frames[entry["frame_id"]] = entry
            elif record["type"] == "agg":
                for entry in record["entries"]:
                    samples[entry["frame_id"]] += entry["self"]
            elif record["type"] == "end":
                total = record["samples_total"]
    functions = Counter()
    for frame_id, count in samples.items():
        frame = frames[frame_id]
        name = strings[frame["func_str_id"]]
        module = Path(strings[frame["path_str_id"]]).name
        functions[f"{name} ({module})"] += count
    return functions, total


monday, monday_total = load("monday.jsonl")
friday, friday_total = load("friday.jsonl")
print(f"Monday: {monday_total} samples in {len(monday)} functions")
print(f"Friday: {friday_total} samples in {len(friday)} functions")
```

```{verify}
:id: profiles-loaded
:label: The notebook has both profiles, with search in each
:substrate: learner-kernel
:path: analysis.ipynb
:trigger: after:insert-load
if "monday" not in globals() or "friday" not in globals():
    print("The cell that loads the profiles has not run: click the action above")
elif not monday.get("search (web.py)") or not friday.get("search (web.py)"):
    print("One of the profiles has no samples in search, so it was recorded with no requests arriving. Record it again, on the second or third page")
else:
    print(f"Monday has {monday_total} samples and Friday {friday_total}, with search in both")
"monday" in globals() and "friday" in globals() and bool(monday.get("search (web.py)")) and bool(friday.get("search (web.py)"))
```

Friday has fewer samples than Monday, for the same twenty
seconds. With `-a` every thread is sampled for as long as it lives,
and on Friday the threads that served searches lived for a fraction
of the time.

## The ten hottest, side by side

A sample is a thousandth of a second of one thread's time, so
samples divided by a thousand are seconds. The next cell takes
Monday's ten hottest functions and prints each beside what it came
to on Friday.

```{cell-insert}
:id: insert-table
:title: Add a cell that prints the ten hottest functions, and run it
:path: analysis.ipynb
:tags: [table]
:run: true
hottest = [name for name, count in monday.most_common(10)]
print(f"{'function':<42}{'Monday':>10}{'Friday':>10}")
for name in hottest:
    print(f"{name:<42}{monday[name] / 1000:>8.1f} s{friday[name] / 1000:>8.1f} s")
```

```{verify}
:id: table-printed
:label: search took less of Friday than of Monday
:substrate: learner-kernel
:path: analysis.ipynb
:trigger: after:insert-table
if "hottest" not in globals():
    print("The cell that prints the table has not run: click the action above")
elif not friday["search (web.py)"] < monday["search (web.py)"] / 2:
    print(f"search has {monday['search (web.py)']} samples on Monday and {friday['search (web.py)']} on Friday; expected less than half as many. Was Friday recorded after web.py was replaced? Record it again, on the third page")
else:
    print(f"search had {monday['search (web.py)'] / 1000:.1f} seconds of Monday and {friday['search (web.py)'] / 1000:.1f} of Friday")
"hottest" in globals() and friday["search (web.py)"] < monday["search (web.py)"] / 2
```

In the run this page was written from, the table began like this:

```
function                                      Monday    Friday
search (web.py)                               32.4 s     2.1 s
_PollLikeSelector.select (selectors.py)       18.6 s    18.4 s
front_page (web.py)                            5.6 s     7.0 s
<GC> (~)                                       1.8 s     0.0 s
health (web.py)                                1.6 s     2.1 s
```

`search` has gone from the top of the list to a small fraction of
what it was, a fifteenth in this run. `select`, the main thread
waiting for connections, is the same in both, as it should be for
two runs of twenty seconds. The other views are much as they were. And `<GC>`, the
garbage collector, has all but gone, which suggests that most of
its work had been clearing up after the loop in `search`, a
thousand rows made for each request and nearly all thrown away.

These are seconds, and not shares of a run. A differential flame
graph compares the two recordings as shares, so that after a fix
which removes many of the samples everything it left alone looks
larger. A
table of your own says what you ask it to.
