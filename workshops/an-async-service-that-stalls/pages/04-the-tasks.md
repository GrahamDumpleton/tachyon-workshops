---
title: The tasks
requires: [verify:tasks-written, quiz:which-async-mode]
---

# The tasks

The flame graph showed the thread. Half of its height was the
loop's own machinery and the layers of uvicorn and Starlette, which
are the same for every request. **`--async-aware`** asks the
profiler to follow the *tasks* in place of the thread: for each
sample it finds the task that is running and the chain of coroutines
that task is in, and leaves the loop out.

Profile the site that way, as a table this time. The `| tee
tasks.txt` belongs to the shell, and keeps a copy of what is printed
for the check. As before, click the first action, and the second as
soon as the first has a tick.

```{execute}
:id: start-tasks
:session: server
:title: Start the web site under the profiler, following tasks
:wait: 3s
python -m profiling.sampling run --async-aware -d 15 -l 8 --no-summary -m uvicorn gazette.asgi:app --port {{ server_port }} | tee tasks.txt
```

```{execute}
:id: load-tasks
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }}
```

```{verify}
:id: tasks-written
:label: The table of tasks has related at the top
:trigger: after:load-tasks
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import re, sys, time
from pathlib import Path

file = Path("tasks.txt")
rows = {}
for _ in range(25):
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8", errors="replace")) if file.exists() else ""
    for line in text.splitlines():
        row = re.match(r"\s*\d+/\d+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+\S+:-?\d+\((.+)\)\s*$", line)
        if row:
            rows[row.group(2)] = rows.get(row.group(2), 0.0) + float(row.group(1))
    if rows:
        break
    time.sleep(1)
else:
    sys.exit("tasks.txt has no table in it yet. The profiler prints it when its fifteen seconds are up: start the web site with the first action, then send the requests")
share = rows.get("related", 0.0)
if share < 50:
    sys.exit(f"related has {share:.0f}% of the samples in tasks.txt; expected most of them. Were the requests sent while the site was being profiled? Start it again, and send the requests straight after")
print(f"related has {share:.0f}% of the samples in which a task was running")
CHECK
```

The table is at the end of the server's log, in the terminal on the
left. Its rows are lines of coroutines and of the functions they
called, and nearly all of the samples are on line 44 of `related`.
The loop's own frames are gone, `select` with them: a sample taken
while no task was running has no task to be counted against, so the
percentages are of the time *some task was running*.

This is the same finding as the flame graph's, stated by task. In a
service with many kinds of task, some started by requests and some
by the application for its own purposes, it is the quicker way to
the one that is running too long.

## Two things to know

**The async-aware flame graph is no use for a server.** It has a
tower for each task, by name, and uvicorn starts a task with a name
of its own for every request, so the graph is thousands of towers
each too thin to draw. The table adds the tasks together.

**`--async-mode all` answers another question.** Async-aware
profiling counts only the running task unless told otherwise. With
`--async-mode all` it counts every task at every sample, the parked
ones as well. The rows at the top are then the places where tasks
wait, inside asyncio and the libraries, and `related` is far down
the table, being one task among hundreds.

```{quiz}
:id: which-async-mode
question: An asyncio service is slow, and you want to know what is holding up the event loop. Which do you use?
options:
  - { text: "`--async-aware`, which counts the task that is running", correct: true }
  - { text: "`--async-aware --async-mode all`, which counts every task", explanation: "That shows what tasks are waiting for. Tasks that are waiting do not hold the loop. The one that is running does." }
  - { text: "`--mode cpu --async-aware`, to leave the waiting out", explanation: "The profiler refuses that combination. Async-aware profiling already leaves out the samples in which no task was running." }
  - { text: "`-a`, to see every thread", explanation: "The loop has one thread, and every task runs on it. Other threads are not where the tasks are." }
explanation: "What holds the loop is, by definition, what is running on it. `--async-mode all` is for the other question, what is everyone waiting for, which is the one to ask when the loop is idle and requests are slow all the same."
```
