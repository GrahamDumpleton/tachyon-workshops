---
title: The loop's view
requires: [quiz:what-the-stack-holds, verify:loop-profile]
---

# The loop's view

Profile the crawler as you would any program, with no options that
know about `asyncio`. Before you do, predict what the table's first
row will be. About a second of the run is spent waiting for the
server, and in the program that fetched the feeds in turn that
second would be in the standard library's read from a socket, called
by `fetch`.

```{quiz}
:id: what-the-stack-holds
question: In the crawler's profile, where will the second spent waiting for the server be?
options:
  - { text: "In `fetch`, on the line that awaits the reply, since that is where each task waits", explanation: "That is where each task waits. A task that is waiting has been put aside by the event loop, and is not on the thread's stack, which is what the profiler reads." }
  - { text: "In a function of the event loop, since the loop is what the thread is running when every task is waiting", correct: true }
  - { text: "Nowhere: waiting tasks are not running, so the samples are dropped", explanation: "The profiler's default mode keeps every sample, whatever the thread was doing. The thread was somewhere." }
  - { text: "In `main`, which is waiting for `gather` to finish", explanation: "`main` is a task too, and is put aside like the others while it waits." }
explanation: "When no task can run, the event loop asks the operating system which connections have data and blocks until one has. The thread is in the loop, so that is where the samples are."
```

```{execute}
:id: profile-loop
:session: shell
:title: Profile the crawler
:wait: prompt
python -m profiling.sampling run -l 8 --no-summary gazette/crawl.py {{ server_port }} | tee loop.txt
```

The first row, with about two thirds of the samples, is
`selectors.py`, `EpollSelector.select`. It is the event loop's wait:
the one place in an asyncio program where the thread blocks, until
any of the connections the loop is watching has something to read.
The second row is `same_story`, the comparison `merge` makes, with
about a quarter.

Everything in this table is true, and the second row is as useful as
it would be in any program. The first row is where this view runs
out. It says the program waited for a second. It does not say which
tasks were waiting, how many, or for what, because the loop waits on
behalf of all of them at once, in one call. In the program that
fetched in turn, the wait was in a function called by `fetch`, and
the stack said so. Here `fetch` is not on the stack while it waits.

The functions of yours that do appear, `same_story`, `keywords`,
`parse`, were running, and if you drew this profile as a flame graph
you would find them beneath six boxes of `asyncio`: `run`,
`Runner.run`, `run_until_complete`, `run_forever`, `_run_once` and
`Handle._run`, which is the loop running a task for one step. Which
task is not recorded there either.

```{verify}
:id: loop-profile
:label: The event loop's wait has the most samples
:trigger: after:profile-loop
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
    assert rows, f"{path} has no table in it; did the crawler fail? Check that the server is running"
    return rows

loop = shares("loop.txt", "profiling")
waiting = max((share for name, share in loop.items() if name.endswith("Selector.select")), default=0.0)
assert waiting > 35, (
    f"The event loop's select has {waiting:.0f}% of the samples in loop.txt; expected most of them. "
    "Is the feed server the one this workshop started?"
)
print(f"{waiting:.0f}% of the samples are in the event loop's wait, "
      f"{loop.get('same_story', 0.0):.0f}% in same_story")
```
