---
title: The same Python
requires: [quiz:why-same-version]
---

# The same Python

Reading memory is only useful if you know its layout. The profiler
knows where a Python 3.15 interpreter keeps its runtime state, its
threads and its frames, and how each of those structures is laid out,
because it was built from the same source. A 3.14 process lays them
out differently, so the profiler that ships with 3.15 can read only a
3.15 process, and the documentation states the rule: the profiler and
the program must be the same minor version, and while either is a
pre-release, alpha, beta or release candidate, the same release
exactly, since the layout can still change between candidates.

In these workshops that is always so, because the profiler and the
program are the same `python`, the one in the workshop's environment.
On your own machine it is the thing to check first when the profiler
says it cannot read a process: `python -m profiling.sampling` must be
the same Python as the one running the program.

See what happens against a process that is not Python at all. `sleep`
is a small C program; start it in the background and ask the profiler
for its stack. The `$!` is the shell's name for the process it just
started.

```{execute}
:id: dump-sleep
:session: shell
:title: Ask for the stack of a process that is not Python
:wait: prompt
sleep 30 & python -m profiling.sampling dump $!; kill $!
```

The profiler reports that it failed to find the `PyRuntime` section in
the process: it looked for the interpreter's runtime structure in the
program's memory and found none, because there is none. A Python of
another version fails in the same place with a message naming the
version mismatch. The `kill` at the end stops the `sleep`, which
would otherwise sit in the background for half a minute.

```{quiz}
:id: why-same-version
question: Why must the profiler and the program it reads be the same Python version?
options:
  - { text: "Because the profiler imports the program's modules and would get the wrong ones", explanation: "The profiler imports nothing from the program. It never runs code in the program's process, or the program's code in its own." }
  - { text: "Because the layout of the interpreter's state in memory differs between versions, and the profiler reads that memory directly", correct: true }
  - { text: "Because Python refuses to let processes of different versions talk to each other", explanation: "Processes of different versions talk all the time, over pipes and sockets. The profiler does not talk to the program at all; it reads its memory." }
  - { text: "It need not be: the rule is only advice", explanation: "It is a hard rule. A mismatched profiler reads the wrong offsets and reports an error, or worse, garbage." }
explanation: "The profiler reads raw memory and interprets it using the layout of its own version's interpreter, so the program must have the same layout: the same minor version, and the same exact release while either is a pre-release."
```
