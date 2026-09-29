---
title: Friday
requires: [verify:fix-written, verify:friday-recorded]
---

# Friday

During the week the search was fixed. The loop of queries became
one query, which has the database join the index of words to the
articles, sort them and stop at twenty.

```{file-write}
:id: write-fix
:title: Replace web.py with Friday's version
:path: gazette/web.py
:from: fixed/web.py
:open: true
:area: desk
```

```{verify}
:id: fix-written
:label: web.py has the fixed search
:trigger: after:write-fix
:substrate: shell
python -c "from pathlib import Path; t = Path('gazette/web.py').read_text(encoding='utf-8'); assert 'JOIN articles' in t and 'for mention in' not in t, 'gazette/web.py still has the loop in search: click the action above to replace it'; print('gazette/web.py has one query where the loop was')"
```

On Friday the same person records the site again, the same way:
the same options, the same twenty seconds, and as near as can be
the same load. Two recordings can be compared only so far as they
were made alike. Here `load.py` sees to the load. In production
nobody chooses the load, so the recordings are made at the same
hour of the same kind of day.

As before, click the first action, and the second as soon as the
first has a tick.

```{execute}
:id: start-friday
:session: server
:title: Record the fixed site for twenty seconds
:wait: 3s
python -m profiling.sampling run -a -d 20 --binary -o friday.bin -m flask --app gazette.web run --port {{ server_port }}
```

```{execute}
:id: load-friday
:session: client
:title: Send requests until the server stops
:wait: prompt
python load.py {{ server_port }} | tee load-friday.txt
```

```{verify}
:id: friday-recorded
:label: friday.bin is recorded, of the fixed site under load
:trigger: after:load-friday
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

if "JOIN articles" not in Path("gazette/web.py").read_text(encoding="utf-8"):
    sys.exit("gazette/web.py still has the loop in search. Replace it with the first action on this page, then record again")
file = Path("friday.bin")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No friday.bin yet. The profiler writes it when its twenty seconds are up: start the server, then send the requests")
time.sleep(1)
load = Path("load-friday.txt")
if not load.exists() or "search" not in load.read_text(encoding="utf-8"):
    sys.exit("friday.bin is written, but load.py sent no requests while it was recorded. Start the server again, and send the requests straight after")
if not Path("monday.bin").exists():
    sys.exit("friday.bin is recorded, but there is no monday.bin to set beside it. Restart the workshop to begin again")
print(f"friday.bin is recorded, {file.stat().st_size // 1024} KB, to set beside monday.bin")
CHECK
```

That is the last time the site is run. Everything from here on is
made from the two files, as it would be on another machine.
