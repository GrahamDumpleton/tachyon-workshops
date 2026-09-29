---
title: Finish
requires: [quiz:red-box]
---

# Finish

The loop is record, change, compare.

- **Record a baseline before changing anything**, with `--binary`,
  and keep it. `run --diff-flamegraph baseline.bin` profiles the
  program and compares. `replay --diff-flamegraph baseline.bin`
  compares a second recording.

- **Compare like with like.** The same data, the same sampling rate,
  the same mode, and a rate high enough for the shorter of the two
  runs.

- **Compare with the profile just before the change**, so that the
  change is all that differs and the runs are of similar length.

- **Read the colour with the width.** Blue is less direct time, red
  more, grey the same, purple new. A strong colour on a box with
  few samples of its own is noise.

- **The colours compare shares.** The baseline is scaled to the
  length of the new run, and the times in the tooltips are scaled
  with it. For the times themselves, `replay` each recording as a
  table.

Where a differential flame graph has stacks that were in the
baseline and are in the new profile no longer, its sidebar has a
switch, Differential and Elided, and the second shows those stacks
alone.

```{quiz}
:id: red-box
question: After a change that made a job take four minutes where it took twenty, the differential flame graph against the old profile shows `write_output`, which was not changed, in dark red. What is the most likely reason?
options:
  - { text: "The change slowed `write_output` down, and it should be looked at next", explanation: "It may deserve a look as the largest part of what is left. The colour alone does not say it is slower than it was." }
  - { text: "`write_output` takes as long as it did, and that is five times the share of a run a fifth as long", correct: true }
  - { text: "The two profiles were recorded at different sampling rates", explanation: "The profiler allows for the rates. It is the lengths of the runs that the scaling is about." }
explanation: "The baseline is scaled to the new run before the comparison, so a function that did not change gains share when the run gets shorter. Print both recordings as tables to compare the times."
```

Next in these workshops is **Watching it live**, the last of them,
which profiles a program while it runs and asks how many samples
are enough. Press Finish to go there.
