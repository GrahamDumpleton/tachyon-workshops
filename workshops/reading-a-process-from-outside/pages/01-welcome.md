---
title: Welcome
requires: [verify:env-ready]
---

# Reading a process from the outside

The first two of these workshops said that Tachyon watches a program
from outside and never runs any code inside it. This one says how,
because everything else about the profiler follows from the mechanism:
what it needs permission for, why it insists on a matching Python, why
some samples are thrown away, and what it costs to stop that.

A running Python program keeps its state in memory: the interpreter's
runtime structure, each thread's state, and for each thread a chain of
frames, one per function call in progress, each recording the code
object and the line being executed. The profiler finds that runtime
structure in the other process's memory and reads its way along the
chain, exactly as the interpreter would to print a traceback, only in
a different process. On Linux the read is the `process_vm_readv`
system call; on macOS it is `task_for_pid` and the Mach memory calls;
on Windows, `ReadProcessMemory`. The program is not paused, not
signalled and not asked. It runs on, and a thousand times a second
another process glances at its memory.

That is why the overhead is nothing the program can measure, and why
the first workshop's report ran in the same time with and without the
profiler. It is also why this workshop is Linux only: on macOS,
reading another process's memory needs root or a debugger entitlement
that an ordinary Python does not have, so the workshops run where an
ordinary user can do it.

## The programs

Two programs from the gazette are open in the editor.
{open}`gazette/report.py` is the word-count report from the first
workshop, slow in `count_words`. {open}`gazette/stream.py` counts
pairs of adjacent words by pulling the articles through a chain of
generators, and is here because generators change the stack quickly,
which matters on the fourth page.

## The environment

Create the workshop's environment, which installs nothing and makes
the `python` in the terminal Python 3.15.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15 and has the profiler
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling')"
```
