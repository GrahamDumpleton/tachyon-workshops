---
title: Where the processor went
requires: [verify:cpu-written, quiz:which-mode]
---

# Where the processor went

The graph you have is in *wall-clock* time, the profiler's default:
every sample counts, whether the thread was computing or waiting.
That is why the main thread, asleep in `select` for nearly all of
the twenty seconds, has a tower at all.

`--mode cpu` keeps only the samples in which the thread was on a
processor. Profile the server again that way, under the same load.
As before, click the first action, and the second as soon as the
first has a tick.

```{execute}
:id: start-cpu
:session: server
:title: Start the server under the profiler, in CPU mode
:wait: 3s
python -m profiling.sampling run -a -d 20 --mode cpu --flamegraph -o cpu.html -m flask --app gazette.web run --port {{ server_port }}
```

```{execute}
:id: load-cpu
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }}
```

```{verify}
:id: cpu-written
:label: cpu.html is written, and has the requests in it
:trigger: after:load-cpu
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

file = Path("cpu.html")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No cpu.html yet. The profiler writes it when its twenty seconds are up: start the server with the first action, then send the requests")
time.sleep(1)
text = file.read_text(encoding="utf-8", errors="replace")
missing = [name for name in ("process_request_thread", "dispatch_request", "search") if name not in text]
if missing:
    sys.exit("cpu.html has no " + ", ".join(missing) + " in it, so the server served no requests while it was profiled. Start the server again, and send the requests straight after")
if not Path("wall.html").exists():
    sys.exit("cpu.html is written, but there is no wall.html to compare it with. Go back a page and make it")
print("cpu.html is written, with the request threads, Flask and the views in it")
CHECK
```

```{command}
:id: open-cpu
:title: Open cpu.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/cpu.html", "factory": "HTML Viewer" }
```

The tower of the main thread has all but gone. It is a sliver at
one edge, the little computing the main thread does to start a
thread for each connection. The requests have the graph to
themselves.

Look at the sidebar too. **Total Samples** is far smaller than the
wall-clock graph's, for the same twenty seconds and the same load.
The samples that are missing were of threads that were not on a
processor: the main thread asleep, and request threads waiting, for
a file, for the network, or for their turn to run Python.

Within the requests the picture has hardly changed. Line 101 of
`search` is still most of it, so the searches are not only slow to
arrive, they are where the processor's time goes.

## Which to use

The two graphs answer different questions about a server.

- **Wall-clock time** answers "what is the server doing?". It is the
  view for a server that is slow while the machine is idle, because
  it shows what the threads are waiting for.

- **CPU time** answers "where is the processor going?". It is the
  view for a server that is busy, and for working out what a
  request costs to compute, since the waiting is removed.

```{quiz}
:id: which-mode
question: A Flask service answers slowly. The machine's processors are nearly idle, and the service calls two other services for each request. Which profile do you make first?
options:
  - { text: "Wall-clock time, with `-a`", correct: true }
  - { text: "CPU time, with `-a`", explanation: "With the processors idle there is little CPU time to show. The waits, which are the problem, would be removed from the picture." }
  - { text: "Wall-clock time, without `-a`", explanation: "Without `-a` only the main thread is sampled, and the requests are served on other threads." }
  - { text: "Either, since both show the same functions", explanation: "They show the same functions only when the time goes on computing. Here it goes on waiting, which CPU mode drops." }
explanation: "Slow with idle processors means waiting, and wall-clock time is the mode that counts waiting. The calls to the other services will be the wide boxes."
```
