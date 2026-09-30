---
title: A thread is not enough
requires: [verify:thread-written, quiz:predict-the-thread, verify:threads-written]
---

# A thread is not enough

The rule is that a task must not hold the loop, and there are two
ways to keep it. One is to make the slow call await something, which
suits a call that waits, for a file or a network. The other is to
hand the call to something else and await *that*. `related` does not
wait for anything. It computes. So it has to be handed over.

The first thing most people reach for is a thread.
`asyncio.to_thread` runs a function on a thread from a pool and
gives back something to await, so the loop is free while the
function runs.

```{file-write}
:id: write-thread
:title: Replace asgi.py with the version that uses a thread
:path: gazette/asgi.py
:from: threaded/asgi.py
:open: true
```

One line of `article` has changed, line 76:

```python
    page = await asyncio.to_thread(render_article, number)
```

```{verify}
:id: thread-written
:label: asgi.py hands render_article to a thread
:trigger: after:write-thread
:substrate: shell
python -c "from pathlib import Path; t = Path('gazette/asgi.py').read_text(encoding='utf-8'); assert 'asyncio.to_thread(render_article' in t, 'gazette/asgi.py does not call asyncio.to_thread: click the action above to replace it'; print('gazette/asgi.py hands render_article to a thread')"
```

```{quiz}
:id: predict-the-thread
question: With `render_article` on a thread of its own, what will the median time of a search be under the same load?
options:
  - { text: "Back to a little over fifty milliseconds, since the loop is free", explanation: "The loop is free of `related` and not free to run. It needs the interpreter's lock to run any Python, and the thread computing `related` has it." }
  - { text: "Much what it was, about twice that, since the thread and the loop cannot both run Python at once", correct: true }
  - { text: "Worse than before, by several times, since threads are slow to start", explanation: "The threads come from a pool and are started once. Starting them is not what costs." }
  - { text: "Nothing will be served, since Starlette does not allow threads", explanation: "Starlette is content with threads, and uses a pool of them itself for views that are not coroutines." }
explanation: "In the ordinary build of Python one thread runs Python at a time, the one that holds the global interpreter lock. A thread that is computing gives the lock up only when asked, and then only every few thousandths of a second. The loop has been moved out of the way of the work and still has to queue behind it."
```

Profile it with every thread sampled, since there is now more than
one that matters. **`-a`** does that. Click the first action, and
the second as soon as the first has a tick.

```{execute}
:id: start-threads
:session: server
:title: Start the web site under the profiler, all threads
:wait: 3s
python -m profiling.sampling run -a -d 15 --flamegraph -o threads.html -m uvicorn gazette.asgi:app --port {{ server_port }}
```

```{execute}
:id: load-threads
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }} | tee threaded.txt
```

```{verify}
:id: threads-written
:label: threads.html is written, with render_article on a worker thread
:trigger: after:load-threads
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

if "asyncio.to_thread(render_article" not in Path("gazette/asgi.py").read_text(encoding="utf-8"):
    sys.exit("gazette/asgi.py does not call asyncio.to_thread. Replace it with the first action on this page, then profile again")
file = Path("threads.html")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No threads.html yet. The profiler writes it when its fifteen seconds are up: start the web site, then send the requests")
time.sleep(1)
text = file.read_text(encoding="utf-8", errors="replace")
missing = [name for name in ("_worker", "render_article", "_run_once") if name not in text]
if missing:
    sys.exit("threads.html has no " + ", ".join(missing) + " in it, so the site served no articles while it was profiled. Start it again, and send the requests straight after")
load = Path("threaded.txt")
if not load.exists() or "search" not in load.read_text(encoding="utf-8"):
    sys.exit("threads.html is written, but load.py sent no requests while it was made. Start the web site again, and send the requests straight after")
print("threads.html is written, with render_article under a worker thread")
CHECK
```

Look first at what `load.py` printed. In the run this page was
written from a search took 100 milliseconds, against 111 before the
change and 55 with no articles at all. The fix has done next to
nothing for the readers.

```{file-open}
:id: open-threads
:title: Open threads.html in the HTML viewer
:path: threads.html
:factory: HTML Viewer
:area: desk
```

The graph has two towers now.

- The one that starts at `Thread._bootstrap` is the pool's threads
  laid over one another. Most of its width is `_worker` with
  nothing beneath it, threads waiting to be given work. The rest
  is `_worker` above `render_article` and `related`: the work has
  moved, as it was meant to.

- The one that starts at `_run_module_as_main` is the main thread,
  the loop. `related` is gone from it. And still the box above
  `Handle._run` is wider than the one above `select`: the loop
  spends more time in the middle of running tasks than waiting for
  something to do, though the tasks have little left to compute.

The sidebar says what it is doing there. Under **Runtime Stats**,
**Waiting GIL** is a quarter or so of all the samples, where in a
profile of the service as it was it would be nothing. Those are
samples of a thread that was ready to run Python and was waiting for
the lock. The loop, with a request to answer, is one of them, and
wall-clock time counts its wait against whatever line it had
reached.

`asyncio.to_thread` is the right fix for a call that *waits*, a
library that reads a file or talks to a database without `await`,
because a thread that is waiting gives up the lock. For a call that
computes, it moves the problem.
