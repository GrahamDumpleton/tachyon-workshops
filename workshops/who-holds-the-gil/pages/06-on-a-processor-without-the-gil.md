---
title: On a processor, without the GIL
requires: [quiz:cpu-and-gil, verify:cpu-not-gil]
---

# On a processor, without the GIL

The flame graph's statistics are one way to see it. Two modes, side
by side, are the other, and work with any output. CPU mode keeps the
samples of threads that were running on a processor. GIL mode keeps
the samples of threads that held the GIL. For Python code the two
agree, because a thread running Python holds the GIL. Predict what
they say about the checksums.

```{quiz}
:id: cpu-and-gil
question: For the four threads hashing in `checksum`, what will CPU mode and GIL mode show?
options:
  - { text: "`checksum` heavy in both, since it is where all the work is", explanation: "That is what Python code looks like, and what the digest builder would show. The hashing runs without the GIL." }
  - { text: "`checksum` heavy in CPU mode and all but absent in GIL mode", correct: true }
  - { text: "`checksum` absent from both, since the profiler cannot see into C code", explanation: "The profiler sees the Python function that called into C, `checksum`, and knows whether the thread was on a processor and whether it held the GIL." }
  - { text: "`checksum` heavy in GIL mode and absent in CPU mode", explanation: "That would be a thread that holds the GIL without running, which does not happen for long: a thread that blocks lets the GIL go." }
explanation: "The threads are busy on a processor, so CPU mode keeps their samples, and busy in C with the GIL released, so GIL mode discards them."
```

```{execute}
:id: checksums-cpu
:session: shell
:title: Profile every thread in CPU mode
:wait: prompt
python -m profiling.sampling run -a --mode cpu -l 4 --no-summary gazette/checksums.py | tee checksums-cpu.txt
```

```{execute}
:id: checksums-gil
:session: shell
:title: Profile every thread in GIL mode
:wait: prompt
python -m profiling.sampling run -a --mode gil -l 4 --no-summary gazette/checksums.py | tee checksums-gil.txt
```

In CPU mode, line 25 of `checksum` has thousands of samples, close to
four for every millisecond the program ran, and its time column is
the seconds of processor time the four threads used between them,
three or four times what the clock measured. In GIL mode the same
line has a dozen or two. The two tables are of the same program
doing the same thing, and they differ by a factor of hundreds.

That is the rule, and it is the one the profiler's documentation
gives:

- **High in CPU mode and low in GIL mode**: the work is in C with the
  GIL released. Threads help, up to the number of processors.

- **High in both**: the work is Python. Threads take turns, and more
  of them make nothing quicker. Use processes, or move the work into
  a library that releases the GIL, or do less.

Python also comes in a free-threaded build, which has no GIL and in
which the digest builder's four threads would run at once. It is a
different build of the interpreter with costs of its own, and these
workshops use the ordinary one.

```{verify}
:id: cpu-not-gil
:label: checksum is heavy in CPU mode and nearly absent in GIL mode
:trigger: after:checksums-gil
import re
from pathlib import Path

def samples(path, mode):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the --mode {mode} command above, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    assert "Captured" in text, f"{path} has no profile in it; did the program fail?"
    rows = re.findall(r"^\s*(\d+)/\d+\s+[\d.]+\s.*\((.+)\)\s*$", text, re.MULTILINE)
    return sum(int(count) for count, name in rows if name == "checksum")

cpu = samples("checksums-cpu.txt", "cpu")
gil = samples("checksums-gil.txt", "gil")
assert cpu > 200, f"checksum has only {cpu} samples in CPU mode; was the program profiled with -a?"
assert cpu > 5 * gil, (
    f"checksum has {cpu} samples in CPU mode and {gil} in GIL mode; expected far fewer with the GIL. "
    "Were the two files written by the two commands above?"
)
print(f"checksum: {cpu} samples on a processor, {gil} holding the GIL")
```
