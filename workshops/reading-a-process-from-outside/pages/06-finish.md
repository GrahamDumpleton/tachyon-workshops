---
title: Finish
requires: [quiz:three-rules]
---

# Finish

The mechanism explains the rules. The profiler reads the interpreter's
frames out of another process's memory, so it must know that memory's
layout, and the profiler and the program must be the same Python. The
kernel decides who may read whose memory, so `run`, where the profiler
is the program's parent, works everywhere, and `attach` and `dump`
against a process you did not start work only where the setting
allows it. And a read made while the program is changing its stack is
sometimes inconsistent and thrown away, which the error rate counts,
and `--blocking` prevents by stopping the program for each read, at a
cost the program pays. Between the rate, the duration and the error
rate, you know how many samples a profile rests on.

```{quiz}
:id: three-rules
question: A colleague's `python -m profiling.sampling attach 4242` fails with a permission error on their Ubuntu laptop. What is the most likely reason?
options:
  - { text: "The process 4242 is running a different Python version", explanation: "A version mismatch gives a message about the version, or about a missing runtime section, not a permission error." }
  - { text: "The kernel's `ptrace_scope` is 1, so the profiler may only read processes it started, and 4242 is not one of them", correct: true }
  - { text: "The profiler needs `--blocking` to attach", explanation: "`--blocking` changes how each sample is taken, not whether the read is allowed." }
  - { text: "Tachyon cannot attach to running processes on Linux", explanation: "It can, where the kernel allows the read: with `ptrace_scope` 0, the capability, or as root." }
explanation: "On a default Ubuntu `ptrace_scope` is 1 and a process may read only its descendants. Starting the program under `run` makes the profiler its parent, which is why `run` never has this problem."
```

Next in these workshops is **Reading a flame graph**, which draws the
table as a picture and answers what the table cannot: which path
through the program led to the hot function. Press Finish to go
there.
