---
title: What holds the loop?
requires: [verify:loop-written, quiz:read-the-loop]
---

# What holds the loop?

Everything an asyncio service does, it does on the thread that runs
the event loop, and in uvicorn that is the main thread. So the
profiler's defaults are the right ones: the main thread, in
wall-clock time, which counts waiting as well as computing. A loop
with nothing to do waits, and a loop that is held up is not
waiting, and the difference is what you are looking for.

```
python -m profiling.sampling run -d 15 --flamegraph -o loop.html -m uvicorn gazette.asgi:app --port {{ server_port }}
```

**`-m uvicorn`** runs a module, as `python -m uvicorn` does, and
what follows it is uvicorn's. **`-d 15`** samples for fifteen
seconds, then stops the server and writes the flame graph, since a
server never ends by itself.

The two actions go together. Click the first, and the second as
soon as the first has a tick. The second sends requests until the
server stops answering.

```{execute}
:id: start-loop
:session: server
:title: Start the web site under the profiler, for fifteen seconds
:wait: 3s
python -m profiling.sampling run -d 15 --flamegraph -o loop.html -m uvicorn gazette.asgi:app --port {{ server_port }}
```

```{execute}
:id: load-loop
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }}
```

```{hint}
:title: If load.py says that nothing answers
The fifteen seconds were over before the requests began, and the
profile that was written is of a server with nothing to do. Click
the first action again, and the second straight after it.
```

```{verify}
:id: loop-written
:label: loop.html is written, and has the requests in it
:trigger: after:load-loop
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

file = Path("loop.html")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No loop.html yet. The profiler writes it when its fifteen seconds are up: start the web site with the first action, then send the requests")
time.sleep(1)
text = file.read_text(encoding="utf-8", errors="replace")
missing = [name for name in ("_run_once", "render_article", "related") if name not in text]
if missing:
    sys.exit("loop.html has no " + ", ".join(missing) + " in it, so the site served no articles while it was profiled. Start it again, and send the requests straight after")
print("loop.html is written, with the event loop and the article view in it")
CHECK
```

```{file-open}
:id: open-loop
:title: Open loop.html in the HTML viewer
:path: loop.html
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

## Reading the loop

One tower, since one thread was sampled. The top of it is uvicorn
starting, down to `run_forever`, which is the event loop, and
beneath that `_run_once`, one turn of the loop. There the tower
divides in two, and the two boxes are the two things a loop does.

- **`_run_once` above `select`** is the loop waiting: nothing is
  ready, and it has asked the operating system to wake it when
  something is. In a healthy service this is the wide one.

- **`_run_once` above `Handle._run`** is the loop running a task.
  Everything beneath it is that task, until its next `await`.

Here the second is four times the width of the first. The loop was
running tasks for four fifths of the run. Follow that box down,
through uvicorn and Starlette's layers, and it narrows hardly at
all until it reaches the application: `article`, then
`render_article`, then `related`, on line 44, with about three
quarters of every sample taken.

Look at `related` in {open}`gazette/asgi.py`. To find the five
articles most like this one, it compares the article's words with
those of each of the other two thousand. There is no `await` in it,
and none in `render_article`, which calls it. From the moment
`article` calls `render_article` until the page is built, some
hundredth of a second later, the loop belongs to that one request.

```{quiz}
:id: read-the-loop
question: "Where is `search` in this flame graph, given that a search takes twice as long as it should?"
options:
  - { text: "It is the widest box, since it is the slowest request", explanation: "It is the request that takes longest to come back. It spends that time waiting, and a task that is waiting is not on the loop's stack." }
  - { text: "It is a sliver: a search spends its time waiting, for the index service and for its turn, and a task that is waiting is not on the thread's stack", correct: true }
  - { text: "It is not there, since the profiler samples one request at a time", explanation: "The profiler samples the thread, whatever it is running. A search is on the thread for a fraction of a millisecond at a time." }
  - { text: "It is under `related`, which it calls", explanation: "`search` and `related` have nothing to do with each other in the code. One holds up the other only by having the loop." }
explanation: "The thread's stack shows the task that is running. A search runs for a moment, awaits, and is gone from the stack until the loop comes back to it. The request that suffers is nearly invisible, and the one that causes the suffering is three quarters of the graph. In a profile of an asyncio service, look at what is running."
```
