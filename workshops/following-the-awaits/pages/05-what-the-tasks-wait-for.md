---
title: What the tasks wait for
requires: [quiz:what-they-wait-for, verify:waiting-profile]
---

# What the tasks wait for

A task that is not running is suspended at an `await`, and asyncio
knows which one, since it has to resume the task there. With
`--async-mode all` the profiler records, at each sample, the running
task if there is one and every suspended task as well, each with the
chain of awaits that ends at the line where it stopped.

Before running it, a prediction. The crawler spends about a second
with its tasks waiting. There are two places in `read_feed` a task
can wait: for one of the four connections, and then in `fetch` for
the server.

```{quiz}
:id: what-they-wait-for
question: Counting every task in every sample, where do the crawler's tasks spend most of their waiting?
options:
  - { text: "Waiting for the server's reply, since the server is what is slow", explanation: "Only four tasks at a time are waiting for the server. The rest are waiting to be one of the four." }
  - { text: "Waiting for a connection to come free, since at most four tasks have one and the rest are in the queue", correct: true }
  - { text: "About equally in both", explanation: "A task waits a fifth of a second for the server once it has a connection. A task at the back of the queue waits four times that for the connection." }
explanation: "At the start four tasks have connections and sixteen are queued. The server's delay is what makes the queue slow, and the queue is where most of the tasks are, most of the time."
```

```{execute}
:id: profile-waiting
:session: shell
:title: Profile every task, running or not
:wait: prompt
python -m profiling.sampling run --async-aware --async-mode all -l 8 --no-summary gazette/crawl.py {{ server_port }} | tee waiting.txt
```

The counts need reading with care. The profiler took about sixteen
hundred samples, as before, and the table adds up to more than
thirteen thousand, because a sample of sixteen waiting tasks counts
sixteen times, once for each. The time columns are multiplied the
same way: eight seconds in the first row, in a program that ran for
one and a half. They are task-seconds, the time tasks spent there
added over the tasks. The percentages are shares of that total.

- **`Semaphore.acquire`**, about two thirds. It is the `async with
  connections` in `read_feed`: tasks waiting for one of the four
  connections.

- **`StreamReader._wait_for_data`**, about three tenths. It is the
  `await reader.read()` in `fetch`: tasks waiting for the server.

- **`main`**, a few percent, on line 88. It is the merge, the only
  row here that is work. In this mode a task is shown by its
  coroutines alone, so `merge` and `same_story`, which are ordinary
  functions called by `main`, are not listed, and their samples are
  counted on the line of `main` that called them. The view of the
  last page is the one for work.

The loop's view said the program waited for a second. This one says
what for: mostly for a turn, not for the server. That changes what
is worth trying. Raising the limit from four connections would
shorten the queue, if the server's owner does not mind, where nothing
the crawler can do makes the server itself answer sooner.

Now the same as a picture.

```{execute}
:id: graph-waiting
:session: shell
:title: Draw every task as a flame graph
:wait: prompt
python -m profiling.sampling run --async-aware --async-mode all --flamegraph -o waiting.html gazette/crawl.py {{ server_port }}
```

```{command}
:id: open-waiting
:title: Open waiting.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/waiting.html", "factory": "HTML Viewer" }
```

Beneath `main` on line 85 there is a box for each of the twenty
tasks, and its width is how long that task was alive. The four
narrowest got a connection at once and were done in a fifth of a
second. The widest waited through four rounds before their turn.
Under each wide one, the box that takes most of the width is the
wait for a connection and the thin one at its right is the wait for
the server, the same width in every task.

```{verify}
:id: waiting-profile
:label: Most of the waiting is for a connection, and the rest for the server
:trigger: after:graph-waiting
import re
from pathlib import Path

def shares(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command} command above, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    rows = {}
    for line in text.splitlines():
        row = re.match(r"\s*\d+/\d+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+\S+:-?\d+\((.+)\)\s*$", line)
        if row:
            rows[row.group(2)] = rows.get(row.group(2), 0.0) + float(row.group(1))
    assert rows, f"{path} has no table in it; did the crawler fail? Check that the server is running"
    return rows

waiting = shares("waiting.txt", "--async-mode all")
queue = waiting.get("Semaphore.acquire", 0.0)
server = waiting.get("StreamReader._wait_for_data", 0.0)
assert queue > 0 and server > 0, (
    "waiting.txt has no rows for Semaphore.acquire and StreamReader._wait_for_data; "
    "was it written with --async-aware --async-mode all?"
)
assert queue > server, (
    f"The wait for a connection has {queue:.0f}% and the wait for the server {server:.0f}%; "
    "expected the connection to be the larger"
)
graph = Path("waiting.html")
assert graph.exists(), "No waiting.html yet: run the second command above, which draws the flame graph"
assert "Semaphore.acquire" in graph.read_text(encoding="utf-8"), (
    "waiting.html does not hold the wait for a connection; was it written with --async-mode all?"
)
print(f"Of the tasks' time, {queue:.0f}% was waiting for a connection and {server:.0f}% for the server")
```
