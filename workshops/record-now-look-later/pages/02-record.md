---
title: Record
requires: [verify:recorded]
---

# Record

`--binary` writes the samples as they are, in a format of the
profiler's own, and `-o` names the file.

```{execute}
:id: record
:session: shell
:title: Profile the report and record the samples
:wait: prompt
python -m profiling.sampling run --binary -o report.bin gazette/report.py
```

After the report and the usual lines about samples and rate, the
profiler says how the recording went. Under **Binary Encoding** it
counts the records it wrote, and there are a few dozen of them for
well over a thousand samples, because a sample with the same stack
as the one before is written as "the same again", and a program stuck
in one line for a second produces the same stack a thousand times
running. Under **Frame Efficiency**, the frames it wrote against the
frames it did not have to, which is nearly all of them. The last line
gives the file and the number of samples in it.

```{execute}
:id: list-recording
:session: shell
:title: How big is the recording?
:wait: prompt
ls -l report.bin
```

A few kilobytes, for every stack the profiler saw in the whole of
the run. The file is compressed with zstd where Python has it, which
Python 3.15 does unless it was built without; `--compression none`
turns that off. A recording of a busier program, whose stack changes
from one sample to the next, is larger, and still small enough to
attach to an issue.

Recording is also the cheapest way to profile. Any other format has
the profiler building the table or the graph's tree as the samples
arrive; with `--binary` it writes them down and leaves that work for
later. The profiler is a separate process, so none of this was ever a
cost to the program, but a profiler with less to do keeps up with its
sampling rate more easily.

```{verify}
:id: recorded
:label: report.bin holds a recording
:trigger: after:record
:substrate: shell
test -s report.bin && echo "report.bin is $(wc -c < report.bin | tr -d ' ') bytes" || { echo "No report.bin yet; run the --binary command above"; exit 1; }
```
