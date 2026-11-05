---
title: All the time that passes
requires: [verify:wall-profile]
---

# All the time that passes

The profiler's default mode is `wall`, short for wall-clock: time as
a clock on the wall measures it. In this mode every sample is kept,
whatever the thread was doing when it was taken. A thread that is
blocked waiting for a server is still somewhere in the program, on
the line that made the request, and the profiler samples it sitting
there a thousand times a second. So waiting shows in the profile as
time, in the function that waited.

Every profile you have made in these workshops so far was in this
mode, since it is what the profiler uses when `--mode` is not given.
Now profile the feed reader in it, with the mode named on the command
line so that it can be compared with the next page's. The `| tee
wall.txt` at the end is not part of the profiler: it prints the
profiler's output as usual and also keeps a copy in `wall.txt`, which
the check below reads.

```{execute}
:id: profile-wall
:session: shell
:title: Profile the feed reader in wall-clock mode
:wait: prompt
python -m profiling.sampling run --mode wall -l 8 --no-summary gazette/feeds.py {{ server_port }} | tee wall.txt
```

The first row has most of the samples, and it is not in the feed
reader at all: `socket.py`, `SocketIO.readinto`, the standard
library's read from a network connection. It is where `fetch` ends
up. `fetch` calls `urlopen`, which goes down through a dozen
functions of `urllib` and `http.client` to the line that asks the
operating system for the server's reply and blocks until it comes.
Its time column is the four seconds of waiting you knew about, and
its share is those four seconds out of the whole run.

The second row is `same_story`, and below it `merge`, `keywords` and
the rest share what is left. Together they are the program's own
work. Where this page was written the read had nearly nine tenths
of the samples and `same_story` under a tenth. On a slower machine
the work takes longer and the waiting does not, so the read's share
is smaller and `same_story`'s larger, in the same order.

This is the table to read when the question is how long the program
takes from start to finish, since a user waiting for the merged feed
waits through all of it. What it does not say is which of these rows
were the processor's doing. The read from the socket and the
comparison of keywords are both just rows with a count.

```{verify}
:id: wall-profile
:label: In wall-clock time the read from the socket has more samples than the program's own work
:trigger: after:profile-wall
import re
from pathlib import Path

def shares(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command} command above, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    rows = {}
    for line in text.splitlines():
        row = re.match(r"\s*\d+/\d+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+\S+:-?\d+\((.+)\)\s*$", line)
        if row:
            rows[row.group(2)] = rows.get(row.group(2), 0.0) + float(row.group(1))
    assert rows, f"{path} has no table in it; did the feed reader fail? Check that the server is running"
    return rows

wall = shares("wall.txt", "--mode wall")
waiting = wall.get("SocketIO.readinto", 0.0)
working = wall.get("same_story", 0.0)
assert waiting > 0, (
    "wall.txt has no row for the read from the socket, SocketIO.readinto. "
    "Was it written with --mode wall, by the command above?"
)
assert waiting > working, (
    f"The read from the socket has {waiting:.0f}% of the samples in wall.txt and same_story has {working:.0f}%; "
    "expected the read to have more. Is the feed server the one this workshop started?"
)
print(f"On this machine {waiting:.0f}% of the samples are in the read from the socket "
      f"and {working:.0f}% in same_story")
```
