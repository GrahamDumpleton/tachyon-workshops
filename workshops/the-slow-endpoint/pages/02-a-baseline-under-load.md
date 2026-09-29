---
title: A baseline under load
requires: [verify:server-up, verify:baseline-recorded, verify:before-table]
---

# A baseline under load

Record the site before changing anything. Afterwards the program
that made the recording is gone, and with it the chance to measure
what the fix is to be compared with.

```
python -m profiling.sampling run -a -d 20 --binary -o baseline.bin -m flask --app gazette.web run --port {{ server_port }}
```

**`-m flask`** and what follows it start Flask's development
server, as `python -m flask` would. **`-d 20`** samples for twenty
seconds, then stops the server and writes the file, since a server
never ends by itself. **`-a`** samples every thread, since the
development server serves each request on a thread of its own.

**`--binary`** writes the profiler's own compact format, which
keeps every sample. It is the format to record in when you do not
yet know which picture you want, because `replay` turns it into any
of them afterwards, and it is the only format that a later profile
can be compared against.

## Start it, then send the requests

The two actions go together. The first starts the server, and its
twenty seconds begin at once. The second sends the requests until
the server stops answering. Click the first, and the second as soon
as the first has a tick.

```{execute}
:id: start-baseline
:session: server
:title: Start the server under the profiler, for twenty seconds
:wait: 3s
python -m profiling.sampling run -a -d 20 --binary -o baseline.bin -m flask --app gazette.web run --port {{ server_port }}
```

```{verify}
:id: server-up
:label: The site answers
:trigger: after:start-baseline
:substrate: shell
python -c "import urllib.request; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=5).read().decode(); assert 'ok' in body; print('The site answered its health check:', body.strip())" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT. If the twenty seconds are up, that is as it should be: start the server again and click Check straight away. If it stopped at once with 'Address already in use', see the hint"; exit 1; }
```

```{execute}
:id: load-baseline
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }} | tee load-before.txt
```

```{hint}
:title: If the port is already in use
The server stops at once with "Address already in use" when something
else on the machine has port {{ server_port }}. Click the gear button
in the header of this panel to open the Variables dialog, change
`server_port` to another number, such as 8092, and run the actions
again. The commands on every page use the number you set.
```

```{hint}
:title: If load.py says that nothing answers
The twenty seconds were over before the requests began, and the
recording is of a server with nothing to do. Click the first action
again, and the second straight after it.
```

```{verify}
:id: baseline-recorded
:label: baseline.bin is recorded
:trigger: after:load-baseline
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

file = Path("baseline.bin")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No baseline.bin yet. The profiler writes it when its twenty seconds are up: start the server with the first action, then send the requests")
time.sleep(1)
load = Path("load-before.txt")
if not load.exists() or "search" not in load.read_text(encoding="utf-8"):
    sys.exit("baseline.bin is written, but load.py sent no requests while it was recorded. Start the server again, and send the requests straight after")
print(f"baseline.bin is recorded, {file.stat().st_size // 1024} KB of samples")
CHECK
```

## The complaint, confirmed

`load.py` printed what the readers saw, and kept a copy in
`load-before.txt`. It will be something like this:

```
3407 requests in 17.1 seconds from 4 readers
page        requests      median     slowest
front           1032      7.7 ms     33.9 ms
article         1689      1.1 ms     13.8 ms
search           357    100.6 ms    182.7 ms
health           329      6.9 ms     29.8 ms
```

Your times will differ with the machine and the disk the database
is on. The shape will not: a search takes many times as long as
any other page. The readers are right.

## The recording as a table

`replay` reads a recording and does not run the program. With no
format named it prints the table. The `| tee before.txt` belongs to
the shell, and keeps a copy for later.

```{execute}
:id: replay-before
:session: client
:title: Print the baseline as a table
:wait: prompt
python -m profiling.sampling replay -l 8 --no-summary baseline.bin | tee before.txt
```

The rows are lines of the program, with the function in brackets.
Two stand out. `selectors.py`, `select`, is the main thread waiting
for connections, which is what a server does between requests. And
line 101 of `web.py`, in `search`, has more samples than every other
line of the application together.

```{verify}
:id: before-table
:label: The baseline's table has search above the other views
:trigger: after:replay-before
import re
from pathlib import Path

def shares(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command} above, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    rows = {}
    for line in text.splitlines():
        row = re.match(r"\s*\d+/\d+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+(\S+):-?\d+\((.+)\)\s*$", line)
        if row:
            key = (row.group(2), row.group(3))
            rows[key] = rows.get(key, 0.0) + float(row.group(1))
    assert rows, f"{path} has no table in it; did the command fail?"
    return rows

rows = shares("before.txt", "replay command")
search = rows.get(("web.py", "search"), 0.0)
others = max([share for (file, name), share in rows.items() if file == "web.py" and name != "search"], default=0.0)
assert search > 0, (
    "There is no row for search in before.txt, so the recording has no searches in it. "
    "Record the baseline again, sending the requests straight after starting the server"
)
assert search > others, (
    f"search has {search:.0f}% of the samples and another view has {others:.0f}%; expected search to have the most. "
    "Was gazette/web.py changed before the baseline was recorded? Restart the workshop to begin again"
)
print(f"search has {search:.0f}% of the baseline's samples, the most of any view")
```
