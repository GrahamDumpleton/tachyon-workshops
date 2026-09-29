---
title: The thread you get
requires: [quiz:default-threads, verify:main-only]
---

# The thread you get

Profile the program the way you have profiled every program so far,
with no options. First predict what the table will show.

```{quiz}
:id: default-threads
question: The program spends its time in `build_digest`, on four threads. What will the profiler's table show, run with no options?
options:
  - { text: "`build_digest` and the functions it calls, with the four threads' samples added together", explanation: "That is what `-a` gives. With no options the profiler does not look at the worker threads." }
  - { text: "Almost nothing but `Thread.join`: the profiler samples the main thread, and the main thread is waiting for the others", correct: true }
  - { text: "One worker thread's share of the work, a quarter of the samples", explanation: "The thread it samples is the main thread, the one the program started in, which does none of the work here." }
  - { text: "An error, since the profiler cannot read a program that has threads", explanation: "It can, and reads this one without complaint. The question is which threads it is asked to look at." }
explanation: "By default the profiler samples the main thread only. Here the main thread starts the workers and waits for them, so the profile is of a thread that is waiting."
```

```{execute}
:id: profile-main
:session: shell
:title: Profile the digest builder with no options
:wait: prompt
python -m profiling.sampling run -l 6 --no-summary gazette/digest.py | tee main.txt
```

Nine tenths of the samples are in `Thread.join`, on a line of
`threading.py`, and most of the rest in `Condition.wait`, which is
the main thread waiting for each new thread to say it has started.
`build_digest` is not in the table, nor any line of `digest.py` but
the last, which calls `main`.

Nothing is wrong with the table. It is a profile of the main thread,
in wall-clock mode, which counts waiting as time. It is just not a
profile of the program. Any program that hands its work to threads
looks like this by default: a web server with a pool of workers, a
downloader, a GUI. If a profile shows a program doing nothing but
wait, and the program is plainly busy, ask which thread you are
looking at.

```{verify}
:id: main-only
:label: The default profile shows the main thread waiting and none of the work
:trigger: after:profile-main
import re
from pathlib import Path

file = Path("main.txt")
assert file.exists(), "No main.txt yet: run the command above, which writes it"
text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
rows = re.findall(r"^\s*\d+/\d+\s+[\d.]+\s.*\((.+)\)\s*$", text, re.MULTILINE)
assert rows, "main.txt has no table in it; did the program fail?"
assert "Thread.join" in rows, "Expected Thread.join in the table; was the program profiled with no options?"
assert "build_digest" not in rows and "syllables" not in rows, (
    "The table has the workers' functions in it, so every thread was sampled; "
    "run the command above, which has no -a"
)
print("The table has Thread.join and none of the workers' functions")
```
