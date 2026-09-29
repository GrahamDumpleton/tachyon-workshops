---
title: A snapshot
requires: [verify:snapshot-read, quiz:what-a-dump-is-for]
---

# A snapshot

`dump` reads the stacks once and prints them, as a traceback is
printed when a program fails, only the program has not failed and
carries on. With `-a` it prints every thread's.

````{when} can_attach == "yes"
A server with nothing to do has one thread, waiting. Give it
something to do first. The action sends requests for ten seconds,
from the terminal on the right.

```{execute}
:id: load-for-dump
:session: client
:title: Send requests for ten seconds
:wait: 1s
python load.py {{ server_port }} 10
```

Now the snapshot, in the middle terminal, while the requests are
arriving. `$(cat gazette.pid)` belongs to the shell, and puts the
number of the process where the command wants it. The `| tee
dump.txt` keeps a copy.

```{execute}
:id: dump-server
:session: shell
:title: Dump the stacks of the running web site
:wait: prompt
python -m profiling.sampling dump -a $(cat gazette.pid) | tee dump.txt
```

Scroll up to the start of what it printed.
````

````{when} can_attach == "no"
This machine does not allow it, so read a snapshot that was taken
where it was allowed, of this same web site under the same load.
It is shipped with the workshop as {open}`dump-example.txt`, and the
command that made it was this:

```
python -m profiling.sampling dump -a $(cat gazette.pid)
```

`$(cat gazette.pid)` belongs to the shell, and puts the number of
the process where the command wants it.
````

## Reading it

There is a block for each thread, and each begins with a line that
says which thread it is and what state it was in:

```
Stack dump for PID 105730, thread 106156 (has GIL, on CPU; most recent call last):
```

Then the frames, the oldest first and the most recent last, as in
a traceback. The snapshot this page was written from had two
threads in it.

- One was serving a request, and its last frame was this:

  ```
    File "gazette/web.py", line 101, in search
      row = db.execute(ARTICLE, (mention["article_id"],)).fetchone()
  ```

- The other was the main thread, marked `idle`, and its last frame
  was `select`, waiting for a connection.

Yours will differ, since a snapshot is a moment: there may be more
request threads or none, and in other views. If there is one, the
odds are that it is in `search`, on that line, for the same reason
that the widest box of a flame graph is the likeliest place for any
one sample to land.

```{verify}
:id: snapshot-read
:label: There is a snapshot of the web site to read
:trigger: action
import os
import re
from pathlib import Path

answer = os.environ.get("CAN_ATTACH", "")
assert answer in ("yes", "no"), "The machine has not been asked yet: go back a page and run the action under 'Ask the machine'"
if answer == "yes":
    file = Path("dump.txt")
    assert file.exists(), "No dump.txt yet: run the two actions above, in order"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    assert "Stack dump for PID" in text and "serve_forever" in text, (
        "dump.txt is not a snapshot of the web site. Is the site still running, in the terminal on the left? "
        "Start it from the page before, then run the actions above again"
    )
    threads = len(re.findall(r"^Stack dump", text, re.M))
    print(f"dump.txt is a snapshot of the web site, with {threads} {'thread' if threads == 1 else 'threads'} in it")
else:
    text = Path("dump-example.txt").read_text(encoding="utf-8")
    assert "Stack dump for PID" in text, "dump-example.txt is not as it was shipped; restart the workshop to get it back"
    print("This machine does not allow a snapshot; dump-example.txt is one taken where it was allowed")
```

```{quiz}
:id: what-a-dump-is-for
question: A service has stopped answering. Its process is still there, using no processor time. What is the first thing to ask of it?
options:
  - { text: "A flame graph of a minute, with `attach`", explanation: "A program that is stuck is in one place for the whole minute. Sixty thousand samples would say what one says." }
  - { text: "A `dump -a`, to see where every thread is", correct: true }
  - { text: "A restart, since a stuck process cannot be read", explanation: "A stuck process is the easiest of all to read, since nothing in it is moving. And a restart throws away the only evidence." }
  - { text: "A profile in CPU mode, to leave the waiting out", explanation: "Waiting is all there is. CPU mode would leave out everything." }
explanation: "One reading of every thread's stack says which lock, which socket or which queue each is waiting on, and that is usually the whole answer. `dump` takes a fraction of a second and needs no decision about how long to sample."
```
