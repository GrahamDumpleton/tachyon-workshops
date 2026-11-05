---
title: The parent alone
requires: [quiz:predict-the-parent, verify:parent-table]
---

# The parent alone

Run the job runner as it is, with no profiler. It is a module of
the `gazette` package, so it is started with `-m`.

```{execute}
:id: run-jobs
:session: server
:title: Build the digests
:wait: prompt
python -m gazette.jobs
```

A little under three hundred thousand digests, on four processes,
in a few seconds: about three where this page was written, on a
machine with a processor for each, and several times that where
the four have to share one. Now profile it, with the profiler's
defaults. The command is the same with the profiler's words in
front: `run -m gazette.jobs` where Python had `-m gazette.jobs`.

```{quiz}
:id: predict-the-parent
question: The program spends nearly all of its time building digests. What will be at the top of the profiler's table?
options:
  - { text: "`build_digest`, since building digests is what takes the time", explanation: "It is what takes the time, in the four worker processes. The profiler is sampling the process that started them." }
  - { text: "`build_batch`, the job that the pool is given", explanation: "`build_batch` runs in the workers. The process being sampled only hands it over, by name." }
  - { text: "A function that waits, since the process the profiler started only hands out the work and collects the results", correct: true }
  - { text: "Nothing, since the process has no work of its own", explanation: "A process that is waiting still has a stack, and the profiler counts waiting unless told not to." }
explanation: "The profiler samples the process it started, the parent. The parent deals out the batches and then waits for the digests to come back, and wall-clock time, the default, counts waiting."
```

```{execute}
:id: profile-parent
:session: server
:title: Profile the job runner
:wait: prompt
python -m profiling.sampling run -l 6 --no-summary -m gazette.jobs | tee parent.txt
```

Something like this:

```
       nsamples   sample%   tottime (s)    cumul%   cumtime (s)  filename:lineno(function)
      2618/2618      95.9         2.618      95.9         2.618  threading.py:363(Condition.wait)
          33/33       1.2         0.033       1.2         0.033  connection.py:416(Connection._recv)
          26/34       1.0         0.026       1.2         0.034  <frozen importlib._bootstrap>:549(_call_with_frames_removed)
        26/2707       1.0         0.026      99.2         2.707  jobs.py:88(<module>)
            5/5       0.2         0.005       0.2         0.005  jobs.py:82(main)
```

Nearly every sample is in `Condition.wait`, which is the parent
waiting for the next batch of digests to arrive. The few samples in
`jobs.py` are on the lines of `main` that deal the work out and
gather it in. `build_digest`, where the processors' time went, is
not in the table at all.

```{verify}
:id: parent-table
:label: The parent's table is waiting, with no build_digest in it
:trigger: after:profile-parent
import re
from pathlib import Path

file = Path("parent.txt")
assert file.exists(), "No parent.txt yet: run the profiler with the action above, which writes it"
text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
rows = {}
for line in text.splitlines():
    row = re.match(r"\s*\d+/\d+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+\S+:-?\d+\((.+)\)\s*$", line)
    if row:
        rows[row.group(2)] = rows.get(row.group(2), 0.0) + float(row.group(1))
assert rows, "parent.txt has no table in it; did the command fail?"
assert "build_digest" not in rows, (
    "parent.txt has a row for build_digest, which runs in the workers. "
    "Was the profiler run with other options? Run the action above again"
)
top = max(rows, key=rows.get)
assert rows[top] > 50, f"The top row of parent.txt is {top} with {rows[top]:.0f}% of the samples; expected one function, waiting, with most of them"
print(f"{top} has {rows[top]:.0f}% of the parent's samples, and build_digest has no row")
```

This is a true profile of the parent and no help with the program.
Anyone handed it would conclude that the job runner does nothing,
slowly.
