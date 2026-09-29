---
title: Only the time on a processor
requires: [quiz:what-cpu-keeps, verify:cpu-profile]
---

# Only the time on a processor

`--mode cpu` takes the same samples at the same rate and keeps only
those in which the thread was running on a processor. The operating
system knows which threads are running and which are blocked, and
the profiler asks it, for each sample. A sample of a thread that was
asleep, blocked on a read or waiting for a lock is thrown away.

Before running it, predict what that does to the table you have.

```{quiz}
:id: what-cpu-keeps
question: In CPU mode, what happens to the row for the read from the socket, which had two thirds of the samples?
options:
  - { text: "It stays at the top: the profiler samples the same program, so the table is the same", explanation: "The samples are the same. The mode chooses which of them are kept, and a thread blocked on a read is not on a processor." }
  - { text: "It all but vanishes, and the rows below it move up to fill the table", correct: true }
  - { text: "It stays at the top with a smaller count, since reading from a socket takes some processor time", explanation: "It takes a little, to copy the bytes once they have arrived. Nearly all of the time on that line was spent blocked, waiting for them." }
  - { text: "The whole table is empty, since the program was waiting most of the time", explanation: "About a third of the run was computing, and those samples are kept." }
explanation: "A thread waiting for a reply is not on a processor, so its samples are discarded. What remains is the third of the run in which the program was computing."
```

```{execute}
:id: profile-cpu
:session: shell
:title: Profile the feed reader in CPU mode
:wait: prompt
python -m profiling.sampling run --mode cpu -l 8 --no-summary gazette/feeds.py {{ server_port }} | tee cpu.txt
```

The program took as long as before, and the profiler says it
captured about as many samples. The table has a third of them. Add
up the first column, or look at the time columns, which are now in
milliseconds because the numbers are smaller. The rest were taken
while the thread was off the processor, and were dropped.

The read from the socket is gone, or down to a sample or two.
`same_story` is first, with about
three quarters of what is left, then `merge` and the lines of
`keywords`. The row from `importlib` is Python loading modules as the
program starts, which was always there and is now large enough to
make the table.

The percentages have changed their meaning along with the mode. In
the wall-clock table `same_story` had a quarter, of the time that
passed. Here it has three quarters, of the time the program spent on
a processor. Both are true. A percentage in a profile is always a
share of the samples that mode kept.

```{verify}
:id: cpu-profile
:label: In CPU time the read from the socket has gone and same_story leads
:trigger: after:profile-cpu
import re
from pathlib import Path

def shares(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command} command, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    rows = {}
    for line in text.splitlines():
        row = re.match(r"\s*\d+/\d+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+\S+:-?\d+\((.+)\)\s*$", line)
        if row:
            rows[row.group(2)] = rows.get(row.group(2), 0.0) + float(row.group(1))
    assert rows, f"{path} has no table in it; did the feed reader fail? Check that the server is running"
    return rows

wall = shares("wall.txt", "--mode wall")
cpu = shares("cpu.txt", "--mode cpu")
waiting_wall = wall.get("SocketIO.readinto", 0.0)
waiting_cpu = cpu.get("SocketIO.readinto", 0.0)
assert waiting_cpu < waiting_wall / 3, (
    f"The read from the socket has {waiting_cpu:.0f}% of the samples in cpu.txt and {waiting_wall:.0f}% in wall.txt; "
    "expected far less in CPU mode. Was cpu.txt written with --mode cpu?"
)
assert cpu.get("same_story", 0.0) > wall.get("same_story", 0.0), (
    "same_story should have a larger share of the CPU profile than of the wall-clock one"
)
print(f"The read from the socket: {waiting_wall:.0f}% of wall-clock time, {waiting_cpu:.0f}% of CPU time. "
      f"same_story: {wall.get('same_story', 0.0):.0f}% and {cpu.get('same_story', 0.0):.0f}%")
```
