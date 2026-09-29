---
title: Finish
requires: [quiz:which-marker]
---

# Finish

The profiler reads Python frames, and adds two markers for what has
none.

- **`<native>`** is added with `--native`. It marks the places
  where the stack passes through C code on its way to a Python
  function: a key function called by `sorted`, a callback called by
  a C library, the interpreter starting the program. It names no C
  function and measures no C time. Time in C code that calls no
  Python is counted on the line that called it, with or without
  the option.

- **`<GC>`** is added unless `--no-gc` is given. It marks samples
  taken while the garbage collector was running, on top of the
  line the collector interrupted. `--no-gc` leaves those samples on
  that line. The marker's count is the least the collector took.

Both are there to stop you drawing the wrong conclusion from a
stack that is true and incomplete: that `rank` called `relevance`,
or that making a `Link` is slow in itself.

Neither can be combined with `--async-aware`, which builds its
stacks from asyncio's tasks.

```{quiz}
:id: which-marker
question: A program spends most of its time on one line, `result = matrix.solve(vector)`, where `solve` comes from an extension module written in C and calls no Python. What will `--native` add to the profile?
options:
  - { text: "A `<native>` box beneath that line, as wide as the time spent in `solve`", explanation: "C code that calls no Python leaves nothing for the profiler to find. The time stays on the line." }
  - { text: "The names of the C functions that `solve` calls", explanation: "The profiler does not read the C stack at all. For that a native profiler such as `perf` is the tool." }
  - { text: "Nothing on that line: the time is counted on the line, as it is without the option", correct: true }
explanation: "The marker appears where C code stands between two Python frames. A call into C that never comes back into Python is counted on the line that made it, and the line is where to look."
```

Next in these workshops is **Down to the bytecode**, which records
the instruction the interpreter was executing at each sample. Press
Finish to go there.
