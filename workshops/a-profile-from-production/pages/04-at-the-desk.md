---
title: At the desk
requires: [verify:flame-written, verify:lines-written, quiz:what-replay-needs]
---

# At the desk

`replay` reads a recording and writes it out in another format. It
runs nothing, and needs neither the program nor the machine the
recording was made on.

## Something to look at

The first thing to do with a recording is to look at it.

```{execute}
:id: replay-flame
:session: client
:title: Make a flame graph of Monday
:wait: prompt
python -m profiling.sampling replay --flamegraph -o monday.html monday.bin
```

```{verify}
:id: flame-written
:label: monday.html is written, with the views in it
:trigger: after:replay-flame
:substrate: shell
python -c "from pathlib import Path; f = Path('monday.html'); assert f.exists(), 'No monday.html yet: run the replay command above'; t = f.read_text(encoding='utf-8', errors='replace'); missing = [n for n in ('dispatch_request', 'search', 'front_page') if n not in t]; assert not missing, 'monday.html has no ' + ', '.join(missing) + ' in it; record Monday again, on the second page'; print('monday.html is written, with Flask and the views in it')"
```

```{file-open}
:id: open-flame
:title: Open monday.html in the HTML viewer
:path: monday.html
:factory: HTML Viewer
:area: desk
```

````{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar. If the tab is blank though the file is trusted,
close the tab and click the action again.
````

Two towers, the main thread waiting in `select` and the request
threads, with Werkzeug and Flask above the views and `search` by far
the widest of them. Hold the mouse over a box and the tooltip shows
the line of source it stands for. That comes from the source files,
read when the flame graph was made, so on a desk that does not have
the program's source the boxes are there and the lines of source are
not.

## Something for a program to read

A picture is for a person. To compare two recordings with a program
of your own you want numbers, and `--jsonl` writes them, as *JSON
lines*: a file of records, one to a line, each a JSON object.

```{execute}
:id: replay-lines
:session: client
:title: Write both recordings as JSON lines
:wait: prompt
python -m profiling.sampling replay --jsonl -o monday.jsonl monday.bin && python -m profiling.sampling replay --jsonl -o friday.jsonl friday.bin
```

```{verify}
:id: lines-written
:label: monday.jsonl and friday.jsonl are written
:trigger: after:replay-lines
import json
from pathlib import Path

for name in ("monday.jsonl", "friday.jsonl"):
    file = Path(name)
    assert file.exists(), f"No {name} yet: run the replay command above"
    kinds = [json.loads(line)["type"] for line in file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert "agg" in kinds and "end" in kinds, f"{name} is not a whole profile; run the replay command above again"
print("monday.jsonl and friday.jsonl are written, a few records each")
```

The file has five kinds of record, told apart by their `type`.

- **`meta`** comes first and gives the time between samples, in
  millionths of a second.

- **`string_table`** holds every name and every path once, each
  with a number.

- **`frame_table`** holds the *frames*. A frame is a line of a
  function: the number of its name, the number of its path, and the
  line.

- **`agg`** holds the counts. For each frame, `self` is the samples
  in which that line was running, and `cumulative` adds the samples
  in which it was waiting for something it had called.

- **`end`** comes last and gives the total.

The tables may be split over several records, so a reader gathers
them all before looking anything up. There are no stacks in the
file. The counts are already added up by frame, so it can say how
much time a function had, and cannot say by what path the program
reached it. That is the flame graph's to say.

```{quiz}
:id: what-replay-needs
question: A colleague sends you `tuesday.bin`, recorded on a host you have never seen. What do you need in order to make a flame graph from it?
options:
  - { text: "Access to the host, since the profiler reads the process's memory", explanation: "Recording reads the process. Replaying reads the file, and the process may be long gone." }
  - { text: "The program that was recorded, installed and running", explanation: "`replay` runs nothing. With the program's source files to hand the tooltips can show lines of source, and that is all they add." }
  - { text: "Python 3.15 and the file", correct: true }
  - { text: "The `.pstats` file that was written beside it", explanation: "Nothing is written beside it. The binary recording holds every sample, and `replay` can write the pstats form from it if you want one." }
explanation: "A recording is complete in itself. `python -m profiling.sampling replay` with a format and the file is all it takes, on any machine with the same version of Python."
```
