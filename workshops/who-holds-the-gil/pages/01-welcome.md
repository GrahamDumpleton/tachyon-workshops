---
title: Welcome
requires: [verify:env-ready, verify:no-faster]
---

# Who holds the GIL?

The work was slow, so you split it between four threads, and it is
exactly as slow as before. It is one of the oldest disappointments in
Python, and the reason for it has a name, the global interpreter lock,
or GIL. What it needs is a profiler that can see every thread and say
what each was doing: running, waiting for something, or waiting for
its turn. This workshop points one at a program where threads do not
help and at one where they do, and reads the difference.

## The program

{open}`gazette/digest.py` is open in the editor. A digest is what a
front page shows of an article: its opening sentence, its keywords,
and how long it takes to read. The gazette prints twelve regional
editions and each has digests of its own, so there are twenty four
thousand to build. `main` shares the articles between four threads,
each running `worker`, and starts a fifth, `report_progress`, which
writes how far they have got to a log file every few milliseconds.
Then it waits for them to finish.

## The environment

Create the workshop's environment, which installs nothing and makes
the `python` in the terminal Python 3.15, the one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15 and has the profiler
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling')"
```

## The disappointment

The program takes the number of threads as its argument. Run it with
one, then with four, and compare the last line of each.

```{execute}
:id: run-one-thread
:session: shell
:title: Build the digests on one thread
:wait: prompt
python gazette/digest.py 1 | tee one-thread.txt
```

```{execute}
:id: run-four-threads
:session: shell
:title: Build the digests on four threads
:wait: prompt
python gazette/digest.py 4 | tee four-threads.txt
```

Much the same time, give or take a little, and that is so on any
machine: four threads finish no sooner than one, however many
processors are standing idle. The check prints your two times.

```{verify}
:id: no-faster
:label: Four threads built the digests no sooner than one
:trigger: after:run-four-threads
import re
from pathlib import Path

def seconds(path):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run both commands above"
    found = re.search(r"in ([\d.]+) seconds", file.read_text(encoding="utf-8"))
    assert found, f"{path} has no time in it; did the program finish?"
    return float(found.group(1))

one, four = seconds("one-thread.txt"), seconds("four-threads.txt")
assert four > one / 2, (
    f"Four threads took {four} seconds and one took {one}: on this Python threads do help. "
    "Is this a free-threaded build of Python?"
)
print(f"One thread: {one} seconds. Four threads: {four} seconds")
```
