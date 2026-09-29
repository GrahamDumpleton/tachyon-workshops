---
title: Threads that help
requires: [verify:faster, verify:checksums-graph]
---

# Threads that help

{open}`gazette/checksums.py`, in the tab beside the digest builder,
has the same shape: `main` shares the work between four threads and
waits. The work is different. Each of the gazette's six thousand
subscribers downloads a copy of the archive stamped with their
number, and `checksum` computes the SHA-256 of each stamped copy with
`hashlib`. The archive is 1.7 megabytes, so that is ten gigabytes to
hash.

Run it with one thread, then with four.

```{execute}
:id: checksums-one-thread
:session: shell
:title: Make the checksums on one thread
:wait: prompt
python gazette/checksums.py 1 | tee checksums-one.txt
```

```{execute}
:id: checksums-four-threads
:session: shell
:title: Make the checksums on four threads
:wait: prompt
python gazette/checksums.py 4 | tee checksums-four.txt
```

Three or four times quicker, on a machine with four processors
free. These threads help.

```{verify}
:id: faster
:label: Four threads made the checksums sooner than one
:trigger: after:checksums-four-threads
import re
from pathlib import Path

def seconds(path):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run both commands above"
    found = re.search(r"in ([\d.]+) seconds", file.read_text(encoding="utf-8"))
    assert found, f"{path} has no time in it; did the program finish?"
    return float(found.group(1))

one, four = seconds("checksums-one.txt"), seconds("checksums-four.txt")
assert four < one, (
    f"Four threads took {four} seconds and one took {one}. "
    "Threads can only help here on a machine with more than one processor to give"
)
print(f"One thread: {one} seconds. Four threads: {four} seconds")
```

Draw every thread, as you did for the digest builder.

```{execute}
:id: profile-checksums
:session: shell
:title: Profile every thread and draw a flame graph
:wait: prompt
python -m profiling.sampling run -a --flamegraph -o checksums.html gazette/checksums.py
```

```{command}
:id: open-checksums-graph
:title: Open checksums.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/checksums.html", "factory": "HTML Viewer" }
```

The same two columns: the main thread in `Thread.join` on the right,
and the workers on the left, all four in `checksum` on line 25, the
call to `update` that does the hashing. Scroll the sidebar to
**Runtime Stats**, with the filter on All Threads or on any worker.

- **GIL Held**, under one percent.

- **Waiting GIL**, under one percent.

- **GIL Released**, all the rest.

Nobody is queueing, because nobody wants the lock. `hashlib` is C,
and when it is given more than a couple of kilobytes to hash it
releases the GIL, hashes, and takes the GIL back to return the
answer. While it hashes, the thread needs nothing from the
interpreter, and four threads hash on four processors at once.

```{verify}
:id: checksums-graph
:label: checksums.html holds the four workers in checksum
:trigger: after:profile-checksums
:substrate: shell
test -s checksums.html && grep -q checksum checksums.html && grep -q "Thread._bootstrap" checksums.html && echo "checksums.html holds checksum, under Thread._bootstrap" || { echo "checksums.html is missing or has no worker threads in it; run the command above, which has -a"; exit 1; }
```
