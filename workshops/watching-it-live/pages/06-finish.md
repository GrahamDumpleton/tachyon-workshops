---
title: Finish
requires: [quiz:which-tool]
---

# Finish

Live mode, and the numbers behind every profile.

- **`--live`** is the table kept up to date, with a header for the
  state of the sampling and of the threads. `s` sorts, `/` filters
  and `c` clears, `t` and the arrows choose a thread, `p` pauses,
  `r` starts the counts again, `h` lists the keys and `q` leaves.
  It writes nothing, and takes no output format.

- **`-r`** is how many samples a second and **`-d`** for how many
  seconds. Their product is the number of samples, and the doubt in
  a percentage shrinks with the square root of it.

- **`--realtime-stats`** shows whether the profiler is achieving
  the rate asked for. When it is not, sample for longer.

This is the last of the **Profiling with Tachyon** workshops. They
began with one command and a table, and have been through every
output the profiler has, the table, the flame graph, the heatmap,
the files for other tools, and every choice of what to sample:
modes, threads, tasks, markers, instructions. The habit under all
of it is the one from the first workshop. A profile is a count of
where the program was found when it was looked at, so ask how it
was looked at and how often before believing what it says.

```{quiz}
:id: which-tool
question: A colleague says a worker process "seems to go quiet every few minutes". Which of the profiler's views is the one to reach for first?
options:
  - { text: "A flame graph of an hour's run, to see the whole picture", explanation: "An hour added together hides what happens for a few seconds every few minutes." }
  - { text: "Live mode, watched until it goes quiet, with `r` to start the counts again when it does", correct: true }
  - { text: "A heatmap with `--opcodes`, for the most detail", explanation: "Detail about instructions is no help in finding when and where the worker stops." }
explanation: "Something that comes and goes needs a view that moves with it. Live mode shows what the program is doing now, and resetting the counts when the quiet begins leaves a table of the quiet alone."
```

**Tachyon on real applications** is where to go next. Press Finish
for what is there.
