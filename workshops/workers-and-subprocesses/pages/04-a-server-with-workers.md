---
title: A server with workers
requires: [verify:server-up, verify:site-profiled, verify:site-to-read, quiz:threads-or-processes]
---

# A server with workers

Flask's development server serves each request on a thread. A
production server such as gunicorn starts a number of worker
*processes* before any request arrives, each with the application
loaded, and the workers take turns to accept connections. The
process you start is the *arbiter*: it starts the workers, replaces
any that die, and serves nothing itself.

So gunicorn is the job runner over again: a parent that waits, and
children that work.

```
python -m profiling.sampling run --subprocesses -d 20 --flamegraph -m gunicorn --no-control-socket -w 3 -b 127.0.0.1:{{ server_port }} gazette.web:app
```

**`-m gunicorn`** and everything after it is gunicorn and its
options: three workers, the address to listen on, and the
application, `app` in `gazette/web.py`. `--no-control-socket` keeps
gunicorn from making a socket for its own management in your home
directory, outside the workshop. **`-d 20`** samples for twenty
seconds and then stops the server. **`--subprocesses`** follows the
workers, where the machine allows it; where it does not, the
arbiter's file is still written, since the arbiter is the process
the profiler started.

There is no `-a`. A gunicorn worker of the ordinary kind serves its
requests on its main thread, one at a time.

The two actions go together. Click the first, and the second as
soon as the first has a tick. The second sends requests until the
server stops answering.

```{execute}
:id: start-site
:session: server
:title: Start gunicorn under the profiler, for twenty seconds
:wait: 3s
python -m profiling.sampling run --subprocesses -d 20 --flamegraph -m gunicorn --no-control-socket -w 3 -b 127.0.0.1:{{ server_port }} gazette.web:app
```

```{verify}
:id: server-up
:label: The site answers
:trigger: after:start-site
:substrate: shell
python -c "import urllib.request; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=5).read().decode(); assert 'ok' in body; print('The site answered its health check:', body.strip())" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT. If the twenty seconds are up, that is as it should be: start the server again and click Check straight away. If it stopped at once with 'Address already in use', see the hint"; exit 1; }
```

```{execute}
:id: load-site
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }}
```

```{hint}
:title: If the port is already in use
gunicorn gives up after a few tries with "Can't connect to" the
address when something else on the machine has port
{{ server_port }}. Click the gear button in the header of this panel
to open the Variables dialog, change `server_port` to another
number, such as 8095, and run the actions again.
```

When the server has stopped and the profiler has said where it
saved the last of the flame graphs, move them to a directory of
their own and list them.

```{execute}
:id: move-site
:session: server
:title: Move the flame graphs to site/ and list them
:wait: prompt
mkdir -p site && mv flamegraph_*.html site/ && ls -l site
```

```{verify}
:id: site-profiled
:label: The flame graphs in site/ are what this machine allows
:trigger: after:move-site
import os
from pathlib import Path

answer = os.environ.get("CAN_ATTACH", "")
assert answer in ("yes", "no"), "The machine has not been asked yet: go back to the last page and run the action under 'Who may read the children'"
files = sorted(Path("site").glob("flamegraph_*.html"))
assert files, "There are no flame graphs in site/ yet: start gunicorn, send the requests, and when the server has stopped run the action above"
texts = [file.read_text(encoding="utf-8", errors="replace") for file in files]
workers = [text for text in texts if "dispatch_request" in text]
arbiters = [text for text in texts if "dispatch_request" not in text and "Arbiter" in text]
assert arbiters, "None of the flame graphs in site/ is the arbiter's. Run the actions above again, in order"
if answer == "yes":
    assert len(workers) >= 3, (
        f"{len(workers)} of the {len(files)} flame graphs in site/ have requests in them; expected the three workers' to. "
        "Were the requests sent while the server was being profiled? Run the actions above again, in order"
    )
    print(f"{len(files)} flame graphs in site/: the arbiter's, and {len(workers)} of workers serving requests")
else:
    assert not workers, (
        f"{len(workers)} of the flame graphs in site/ have requests in them, so a worker was followed after all; "
        "the machine answered no on the last page, so run the action under 'Who may read the children' again"
    )
    print(f"{len(files)} flame graph in site/, the arbiter's: this machine refused the workers, as it did the pool's")
```

````{when} can_attach == "yes"
Four files: the arbiter and three workers. Copy the arbiter's and
one worker's to names of their own. The arbiter's is the one with
no request in it.

```{execute}
:id: copy-site
:session: server
:title: Copy the arbiter's flame graph and one worker's
:wait: prompt
cp "$(grep -L dispatch_request site/flamegraph_*.html | head -1)" arbiter.html && cp "$(grep -l dispatch_request site/flamegraph_*.html | head -1)" web-worker.html
```

```{file-open}
:id: open-arbiter
:title: Open arbiter.html in the HTML viewer
:path: arbiter.html
:factory: HTML Viewer
:area: desk
```

The arbiter is one column with no branches, ending in
`Arbiter.wait_for_signals`. For twenty seconds it waited to be told
that a worker had died or that it was time to stop.

```{file-open}
:id: open-web-worker
:title: Open web-worker.html in the HTML viewer
:path: web-worker.html
:factory: HTML Viewer
:area: desk
```
````

````{when} can_attach == "no"
One file, the arbiter's, and it is a true profile of the arbiter:
copy it to a name of its own and open it.

```{execute}
:id: copy-arbiter
:session: server
:title: Copy the arbiter's flame graph
:wait: prompt
cp "$(ls site/flamegraph_*.html | head -1)" arbiter.html
```

```{file-open}
:id: open-arbiter-only
:title: Open arbiter.html in the HTML viewer
:path: arbiter.html
:factory: HTML Viewer
:area: desk
```

The arbiter is one column with no branches, ending in
`Arbiter.wait_for_signals`. For twenty seconds it waited to be told
that a worker had died or that it was time to stop. Every request
was served by a worker, and the workers were refused, so this is
all the profiler could write here. A worker's flame graph, made on
a machine that allowed it, under the same load, is shipped with the
workshop. Open it.

```{file-open}
:id: open-web-worker-example
:title: Open web-worker-example.html in the HTML viewer
:path: web-worker-example.html
:factory: HTML Viewer
:area: desk
```
````

```{verify}
:id: site-to-read
:label: There is the arbiter's flame graph and a worker's to read
:trigger: action
import os
from pathlib import Path

answer = os.environ.get("CAN_ATTACH", "")
assert answer in ("yes", "no"), "The machine has not been asked yet: go back to the last page and run the action under 'Who may read the children'"
arbiter = Path("arbiter.html")
assert arbiter.exists(), "No arbiter.html yet: run the copy command above"
assert "dispatch_request" not in arbiter.read_text(encoding="utf-8", errors="replace"), "arbiter.html has requests in it, so it is a worker; run the copy command above again"
name = "web-worker.html" if answer == "yes" else "web-worker-example.html"
worker = Path(name)
if answer == "yes":
    assert worker.exists(), "No web-worker.html yet: run the copy command above"
else:
    assert worker.exists(), "web-worker-example.html is missing; restart the workshop to get it back"
assert "dispatch_request" in worker.read_text(encoding="utf-8", errors="replace"), f"{name} has no requests in it" + ("; run the copy command above again" if answer == "yes" else "; restart the workshop to get it back")
if answer == "yes":
    print("arbiter.html is the arbiter and web-worker.html is one of its workers")
else:
    print("arbiter.html is the arbiter; this machine refused the workers, and web-worker-example.html is one made where they were allowed")
```

The worker is where the site is. Three things to see.

- **The top of the tower is the arbiter's.** `Arbiter.run`,
  `spawn_workers`, `spawn_worker`: the worker was *forked* from the
  arbiter, which copies the process as it stands, stack included.
  The worker's own life begins at `Worker.init_process`.

- **Below `SyncWorker.run` the tower divides** into
  `SyncWorker.wait`, the worker waiting for a connection, and
  `accept`, `handle` and `handle_request`, the worker serving one.
  Beneath those are Flask and the views you know, with `search` the
  widest.

- **It is one worker of three.** Its samples are its own, a third
  or so of the site's work. The other two files have the same shape
  and much the same widths. To say what the *site* spent on
  searches, the three have to be added up, which the profiler does
  not do for you.

```{quiz}
:id: threads-or-processes
question: "The development server needed `-a` and gave one flame graph. gunicorn needed `--subprocesses` and, where the machine allows it, gives four. Why the difference?"
options:
  - { text: "gunicorn is faster, so there is more to draw", explanation: "How much there is to draw depends on the samples. The number of files depends on the number of processes." }
  - { text: "The development server serves requests on threads of one process, and gunicorn on processes of their own, and the profiler writes a profile for each process", correct: true }
  - { text: "`--subprocesses` splits a flame graph by view, one file for each", explanation: "Each file has all the views in it. The files are one for each process." }
  - { text: "`-a` cannot be used with gunicorn", explanation: "It can, and would sample every thread of the arbiter. The workers are other processes, which `-a` does not reach." }
explanation: "Threads share a process, and `-a` samples all the threads of the process being profiled, into one profile. Processes share nothing, and each is profiled by a profiler of its own, into a file of its own. A server that uses both, several workers with several threads each, needs both options."
```
