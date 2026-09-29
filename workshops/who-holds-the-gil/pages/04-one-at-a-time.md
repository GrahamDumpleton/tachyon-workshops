---
title: One at a time
requires: [verify:gil-profile, quiz:why-no-faster]
---

# One at a time

The interpreter that runs Python code keeps a great deal of state,
and the way CPython has always kept that state safe when there are
several threads is a single lock, the *global interpreter lock*. A
thread must hold the GIL to run Python bytecode. There is one GIL, so
one thread runs Python at a time, however many threads there are and
however many processors. The others wait, and every few milliseconds
the thread that holds the lock gives another a turn.

A thread lets go of the GIL when it has no need of the interpreter:
while it waits for a file, a socket or a lock, while it sleeps, and
inside C code that has been written to release it while it works on
data of its own. That is why threads in Python are good for waiting
and no help with computing in Python.

The profiler records, with every sample of every thread, whether the
thread held the GIL at that instant. That is where the flame graph's
statistics came from. `--mode gil` uses it to choose what to keep:
only the samples of a thread that held the GIL.

```{execute}
:id: profile-gil
:session: shell
:title: Profile every thread, keeping the samples that held the GIL
:wait: prompt
python -m profiling.sampling run -a --mode gil -l 10 --no-summary gazette/digest.py | tee gil.txt
```

Every row is a line of `digest.py`, in `build_digest`, `syllables`
and `keywords`. `Thread.join` is gone, since the main thread lets go
of the GIL to wait, and so has `report_progress`, nearly, since
writing a line to a file takes almost no time.

Add up the first column, roughly. It comes to fewer samples than the
profiler says it captured at the top, where with `-a` alone there
were several times as many. At each look there is at most one thread
holding the GIL, so at most one sample to keep. This table is what
the interpreter did with its time, whichever thread it did it on, and
it would look the same with one worker or with forty.

```{verify}
:id: gil-profile
:label: In GIL mode the table has the workers' code and none of the waiting
:trigger: after:profile-gil
import re
from pathlib import Path

file = Path("gil.txt")
assert file.exists(), "No gil.txt yet: run the command above, which writes it"
text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
rows = re.findall(r"^\s*(\d+)/\d+\s+[\d.]+\s.*\((.+)\)\s*$", text, re.MULTILINE)
assert rows, "gil.txt has no table in it; did the program fail?"
names = [name for count, name in rows]
assert "build_digest" in names, "Expected build_digest in the table; was the program profiled with -a and --mode gil?"
waiting = sum(int(count) for count, name in rows if name == "Thread.join")
working = sum(int(count) for count, name in rows if name != "Thread.join")
assert waiting < working / 10, (
    f"Thread.join has {waiting} samples in gil.txt; a thread waiting in join does not hold the GIL. "
    "Was the program profiled with --mode gil?"
)
print(f"{working} samples in the rows shown, all of code that held the GIL")
```

```{quiz}
:id: why-no-faster
question: Why did four threads build the digests no sooner than one?
options:
  - { text: "The machine has only one processor", explanation: "It may have ten. Only one of them at a time can be running this program's Python code." }
  - { text: "Building a digest is Python code, a thread must hold the GIL to run Python code, and there is one GIL", correct: true }
  - { text: "The thread writing the progress log slowed the others down", explanation: "It holds the GIL for a moment every few milliseconds. The workers lose far more time to each other." }
  - { text: "Starting threads is slow", explanation: "Starting five threads takes a few milliseconds of a run that lasts most of a second." }
explanation: "The workers run Python bytecode from start to finish, so each needs the GIL all the time and gets it a quarter of the time. Four threads taking turns do what one would."
```
