---
title: Another process
requires: [verify:pool-written, verify:pooled-written, verify:search-recovered]
---

# Another process

A process has an interpreter of its own, and a lock of its own. Work
handed to another process does not compete with the loop for
anything but a processor, and the machine has several.

```{file-write}
:id: write-pool
:title: Replace asgi.py with the version that uses a pool of processes
:path: gazette/asgi.py
:from: pooled/asgi.py
:open: true
```

Two things have changed in {open}`gazette/asgi.py`. At the bottom,
`lifespan` starts a `ProcessPoolExecutor` of four workers when the
application starts, and shuts it down when the application stops.
And `article` hands the rendering to it:

```python
    loop = asyncio.get_running_loop()
    page = await loop.run_in_executor(request.app.state.workers, render_article, number)
```

`render_article` takes the number of an article, and not the
article, because what is passed to another process has to be sent
to it, and a number is cheap to send. Each worker loaded the
articles for itself when it started.

```{verify}
:id: pool-written
:label: asgi.py hands render_article to a pool of processes
:trigger: after:write-pool
:substrate: shell
python -c "from pathlib import Path; t = Path('gazette/asgi.py').read_text(encoding='utf-8'); assert 'ProcessPoolExecutor' in t and 'run_in_executor' in t, 'gazette/asgi.py has no pool of processes: click the action above to replace it'; print('gazette/asgi.py hands render_article to a pool of processes')"
```

Profile it as you did at first: the main thread, in wall-clock
time. Click the first action, and the second as soon as the first
has a tick.

```{execute}
:id: start-pooled
:session: server
:title: Start the web site under the profiler
:wait: 3s
python -m profiling.sampling run -d 15 --flamegraph -o pooled.html -m uvicorn gazette.asgi:app --port {{ server_port }}
```

```{execute}
:id: load-pooled
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }} | tee pooled.txt
```

```{verify}
:id: pooled-written
:label: pooled.html is written, of the site with the pool
:trigger: after:load-pooled
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

if "ProcessPoolExecutor" not in Path("gazette/asgi.py").read_text(encoding="utf-8"):
    sys.exit("gazette/asgi.py has no pool of processes. Replace it with the first action on this page, then profile again")
file = Path("pooled.html")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No pooled.html yet. The profiler writes it when its fifteen seconds are up: start the web site, then send the requests")
time.sleep(1)
text = file.read_text(encoding="utf-8", errors="replace")
missing = [name for name in ("_run_once", "run_in_executor") if name not in text]
if missing:
    sys.exit("pooled.html has no " + ", ".join(missing) + " in it, so the site served no articles while it was profiled. Start it again, and send the requests straight after")
print("pooled.html is written, of the site with the pool of processes")
CHECK
```

```{verify}
:id: search-recovered
:label: A search is quicker again
:trigger: after:load-pooled
:timeout: 40s
import re
import time
from pathlib import Path

def median(path, page, command):
    file = Path(path)
    for _ in range(10):
        if file.exists() and re.search(rf"^{page}\s", file.read_text(encoding="utf-8"), re.M):
            break
        time.sleep(1)
    assert file.exists(), f"No {path} yet: run the {command}, which writes it"
    row = re.search(rf"^{page}\s+(\d+)\s+([\d.]+) ms", file.read_text(encoding="utf-8"), re.M)
    assert row, f"{path} has no row for {page}; was the web site running when load.py was run? Start it and run the command again"
    return float(row.group(2))

together = median("together.txt", "search", "second load.py command on the second page")
pooled = median("pooled.txt", "search", "load.py command above")
assert pooled < together * 0.85, (
    f"A search took {together:.0f} ms while the loop was blocked and takes {pooled:.0f} ms now; expected a good deal less. "
    "Was gazette/asgi.py replaced before the site was started? Run the three actions above again, in order"
)
print(f"A search took {together:.0f} ms while the loop was blocked and takes {pooled:.0f} ms with the pool")
```

`load.py` has the answer the readers care about. In the run this
page was written from, a search took 52 milliseconds, which is what
it took with no articles being read at all, and an article took 10
where it had taken 35. The site also served more than twice as many
requests in the same time, since `load.py` sends the next request
when the last is answered. That was on a machine with processors to
spare. On a server that allows the site a single processor, the
four worker processes and the loop share it, and a search comes
back sooner than it did without getting all the way back.

```{file-open}
:id: open-pooled
:title: Open pooled.html in the HTML viewer
:path: pooled.html
:factory: HTML Viewer
:area: desk
```

The loop is a loop again. The box above `select` is the wide one,
and the one above `Handle._run` is the tasks taking their short
turns: reading requests, passing work to the pool, sending replies.

`related` is not in the graph at all. It ran, thousands of times,
in four processes that the profiler was not watching, since it
samples the process it started and no other unless asked. How to
ask is the subject of the next of these workshops.
