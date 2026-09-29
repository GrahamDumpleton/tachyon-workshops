---
title: Monday
requires: [verify:server-up, verify:monday-recorded]
---

# Monday

It is Monday, and the search is slow. Before anyone changes
anything, somebody with access to the host records twenty seconds
of the site at work.

```
python -m profiling.sampling run -a -d 20 --binary -o monday.bin -m flask --app gazette.web run --port {{ server_port }}
```

**`-m flask`** and what follows start the site. **`-d 20`** samples
for twenty seconds, then stops the server and writes the file.
**`-a`** samples every thread, since Flask's development server
serves each request on a thread of its own. **`--binary`** writes
the recording.

On a real host the site would be running already, and the recording
would be made with `attach` and the number of its process, with the
same options. `run` is used here so that the workshop works on
machines that do not allow attaching.

The two actions go together. Click the first, and the second as
soon as the first has a tick. The second sends requests until the
server stops answering.

```{execute}
:id: start-monday
:session: server
:title: Record the site for twenty seconds
:wait: 3s
python -m profiling.sampling run -a -d 20 --binary -o monday.bin -m flask --app gazette.web run --port {{ server_port }}
```

```{verify}
:id: server-up
:label: The site answers
:trigger: after:start-monday
:substrate: shell
python -c "import urllib.request; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=5).read().decode(); assert 'ok' in body; print('The site answered its health check:', body.strip())" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT. If the twenty seconds are up, that is as it should be: start the server again and click Check straight away. If it stopped at once with 'Address already in use', see the hint"; exit 1; }
```

```{execute}
:id: load-monday
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }} | tee load-monday.txt
```

```{hint}
:title: If the port is already in use
The server stops at once with "Address already in use" when something
else on the machine has port {{ server_port }}. Click the gear button
in the header of this panel to open the Variables dialog, change
`server_port` to another number, such as 8097, and run the actions
again. The commands on every page use the number you set.
```

```{hint}
:title: If load.py says that nothing answers
The twenty seconds were over before the requests began, and the
recording is of a server with nothing to do. Click the first action
again, and the second straight after it.
```

```{verify}
:id: monday-recorded
:label: monday.bin is recorded, of the site under load
:trigger: after:load-monday
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

file = Path("monday.bin")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No monday.bin yet. The profiler writes it when its twenty seconds are up: start the server with the first action, then send the requests")
time.sleep(1)
load = Path("load-monday.txt")
if not load.exists() or "search" not in load.read_text(encoding="utf-8"):
    sys.exit("monday.bin is written, but load.py sent no requests while it was recorded. Start the server again, and send the requests straight after")
print(f"monday.bin is recorded, {file.stat().st_size // 1024} KB for twenty seconds of every thread")
CHECK
```

## How little there is to copy

The check says how large the file is: a hundred or two hundred
kilobytes, for twenty seconds of every thread of a busy server, at
a thousand samples a second. The profiler said how, in the server's
terminal, under **Binary Encoding**: a sample that is the same as
the one before is stored as a repeat, most of the others as their
difference from the one before, and the whole is compressed.

That is small enough to send by any means there is, and to keep.
A recording made every night costs a few megabytes a month.
