---
title: Finish
requires: [quiz:what-only-tracer-knows]
---

# Finish

You have run one program under both of Python's profilers and read
both tables. `cProfile`, now also `profiling.tracing`, is told about
every call, so it knows exact counts and exact times and the program
pays a toll for every call, several times its own running time for
this one. Tachyon glances at the stack from outside a thousand times a
second, so it estimates from what it saw, knows nothing of how many
calls there were, and costs the program next to nothing. Short
program or exact counts, the tracer; long-running, production or
call-heavy, the sampler; a few percent between two lines, `timeit`.

```{quiz}
:id: what-only-tracer-knows
question: Which of these can the tracing profiler report and the sampling profiler cannot?
options:
  - { text: "Which function used the most time", explanation: "Both report that; the sampler estimates it from how often the function was seen, and for a program that runs a while the estimate is close." }
  - { text: "The exact number of times a function was called", correct: true }
  - { text: "Which line of a function the time was spent on", explanation: "That one is the other way round: the sampler's rows are per executing line, and the tracer's are per function." }
  - { text: "Time spent in C code called from Python", explanation: "The tracer lists C methods as rows of their own. The sampler attributes their time to the Python line that called them by default, and shows them as native frames when asked; a later workshop covers that." }
explanation: "Call counts need every call to be observed, which only the tracer does. The sampler sees the stack a thousand times a second and can never know how many calls happened between looks."
```

Next in these workshops is **Reading a process from the outside**,
which explains how the sampler reads another process's stack, why it
needs permission to read a process it did not start, and what the
error rate means. Press Finish to go there.
