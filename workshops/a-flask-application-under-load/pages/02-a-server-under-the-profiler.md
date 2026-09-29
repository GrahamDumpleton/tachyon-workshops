---
title: A server under the profiler
requires: [quiz:why-all-threads, verify:server-up, verify:wall-written]
---

# A server under the profiler

Without the profiler, the site would be started with Flask's
development server like this:

```
python -m flask --app gazette.web run --port {{ server_port }}
```

To profile it, the same words go after the profiler's own:

```
python -m profiling.sampling run -a -d 20 --flamegraph -o wall.html -m flask --app gazette.web run --port {{ server_port }}
```

Three of the profiler's options do the work here.

**`-m flask`** runs a module, as `python -m flask` does, where
`run` would otherwise expect the path of a script. Everything after
the module's name belongs to the module, so `--app` and `--port` are
Flask's. Whatever you start with `python -m something`, you can
profile with `python -m profiling.sampling run -m something`.

**`-d 20`** is the duration, in seconds. The profiler samples for
twenty seconds, stops the server, and writes the flame graph. Nobody
has to stop the server at the right moment.

**`-a`** samples all the threads of the program. Without it the
profiler samples the main thread alone. Flask's development server
hands every request to a thread of its own, which is started for the
request and ends with it.

```{quiz}
:id: why-all-threads
question: Suppose the `-a` were left out. What would the flame graph of the server show?
options:
  - { text: "The same picture, with fewer samples", explanation: "The samples that would be missing are all of one kind: those of the threads that serve the requests." }
  - { text: "The views, since they are where the time goes", explanation: "The views run on the request threads, which are not sampled without `-a`." }
  - { text: "The main thread waiting for connections, and nothing of the requests", correct: true }
  - { text: "Nothing, since the main thread exits once the server has started", explanation: "The main thread stays for as long as the server runs. It is the one that accepts each connection." }
explanation: "The main thread of the development server accepts connections and starts a thread for each. The views run on those threads, so a profile of the main thread alone is a profile of waiting."
```

## Start it, then send the requests

The two actions below go together. The first starts the server
under the profiler, and its twenty seconds begin at once. The second
sends the requests, and carries on until the server stops answering.
Read to the end of this section, then click the first, and click the
second as soon as the first has a tick.

```{execute}
:id: start-wall
:session: server
:title: Start the server under the profiler, for twenty seconds
:wait: 3s
python -m profiling.sampling run -a -d 20 --flamegraph -o wall.html -m flask --app gazette.web run --port {{ server_port }}
```

```{verify}
:id: server-up
:label: The site answers
:trigger: after:start-wall
:substrate: shell
python -c "import urllib.request; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=5).read().decode(); assert 'ok' in body; print('The site answered its health check:', body.strip())" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT. If the twenty seconds are up, that is as it should be: start the server again and click Check straight away. If it stopped at once with 'Address already in use', see the hint"; exit 1; }
```

```{execute}
:id: load-wall
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }}
```

```{hint}
:title: If the port is already in use
The server stops at once with "Address already in use" when something
else on the machine has port {{ server_port }}. Click the gear button
in the header of this panel to open the Variables dialog, change
`server_port` to another number, such as 8091, and run the actions
again. The commands on every page use the number you set.
```

```{hint}
:title: If load.py says that nothing answers
The twenty seconds were over before the requests began, and the
profile that was written is of a server with nothing to do. Click
the first action again, and the second straight after it.
```

The terminal on the left fills with the server's log, a line for each
request. When the twenty seconds are up the profiler stops the
server and says where it wrote the flame graph, and in the terminal
on the right `load.py` finds the server gone and prints what it
saw, something like this:

```
The server stopped answering after 17.1 seconds.
3423 requests in 17.1 seconds from 4 readers
page        requests      median     slowest
front           1035      7.1 ms     31.3 ms
article         1698      1.1 ms     10.7 ms
search           359     86.8 ms    202.2 ms
health           331      6.8 ms     34.6 ms
```

Your times will differ, with the machine, with the disk the
database is on, and from one run to the next. The order will be the
same. An article takes a millisecond or two, and a search many times
as long as any other page.

```{verify}
:id: wall-written
:label: wall.html is written, and has the requests in it
:trigger: after:load-wall
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

file = Path("wall.html")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No wall.html yet. The profiler writes it when its twenty seconds are up: start the server with the first action, then send the requests")
time.sleep(1)
text = file.read_text(encoding="utf-8", errors="replace")
missing = [name for name in ("process_request_thread", "dispatch_request", "search", "front_page") if name not in text]
if missing:
    sys.exit("wall.html has no " + ", ".join(missing) + " in it, so the server served no requests while it was profiled. Start the server again, and send the requests straight after")
print("wall.html is written, with the request threads, Flask and the views in it")
CHECK
```
