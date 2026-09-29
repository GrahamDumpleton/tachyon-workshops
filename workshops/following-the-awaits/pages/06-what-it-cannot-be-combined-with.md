---
title: What it cannot be combined with
requires: [verify:refused, quiz:which-view]
---

# What it cannot be combined with

Async-aware profiling builds its stacks from asyncio's tasks and not
from the thread, and several of the profiler's other options are
about the thread. The profiler refuses the combination. Try one: CPU
mode, which keeps the samples in which the thread was on a
processor.

```{execute}
:id: try-cpu
:session: shell
:title: Ask for async-aware profiling in CPU mode
:wait: prompt
python -m profiling.sampling run --async-aware --mode cpu gazette/crawl.py {{ server_port }} 2>&1 | tee refused.txt
```

The crawler was not run. The profiler checked its options first and
stopped with "Options --mode=cpu are incompatible with
--async-aware". The options it refuses alongside `--async-aware` are
these.

- **`--mode cpu`, `--mode gil` and `--mode exception`**. The modes
  choose samples by the state of the thread, and only wall-clock
  mode, the default, is allowed. `--async-mode running` does part of
  what CPU mode does, by leaving out the time when no task was
  running.

- **`-a`**, which samples every thread. Async-aware profiling reads
  the tasks of one event loop.

- **`--native` and `--no-gc`**, which add and remove the markers for
  C code and the garbage collector, the subject of the next of these
  workshops.

There is one requirement as well. The program must have imported
`asyncio` by the time the profiler looks for its tasks. With `run`,
a program that imports it at the top, as nearly all do, is ready
before its first task exists.

```{verify}
:id: refused
:label: The profiler refused CPU mode with async-aware profiling
:trigger: after:try-cpu
:substrate: shell
test -s refused.txt || { echo "No refused.txt yet: run the command above, which writes it"; exit 1; }
grep -q "incompatible with --async-aware" refused.txt && echo "The profiler refused: $(grep -o 'Options .* are incompatible with --async-aware' refused.txt)" || { echo "refused.txt does not hold the profiler's refusal; run the command above as it is written"; exit 1; }
```

## Which view, when

You have three views of one asyncio program.

- **No option** gives the thread's stack. Your functions are in it
  when they run, under the loop's, and all waiting is the loop's
  `select`. It is the view every other option works with, and it is
  enough when the question is where the processor's time goes.

- **`--async-aware`** gives the running task's stack of awaits. It
  is the one for "which task, started by whom, is using the
  processor", in a service with many kinds of task.

- **`--async-aware --async-mode all`** adds the suspended tasks. It
  is the one for "what is everything waiting for", and its counts
  are per task, not per sample.

```{quiz}
:id: which-view
question: An asyncio service handles a thousand connections and its replies have become slow. The profiler with no options shows 95% of the samples in the event loop's `select`. What does that say, and what should be run next?
options:
  - { text: "The event loop is slow, so profile with `--native` to see inside `select`", explanation: "`select` is the loop waiting because no task can run. It is not slow; it has nothing to do." }
  - { text: "The service is nearly always waiting, not working, so run `--async-aware --async-mode all` to see which awaits the tasks are suspended at", correct: true }
  - { text: "The service is nearly always waiting, so run `--async-aware --mode cpu` to see the work that remains", explanation: "The profiler refuses that combination. And with 5% of the time spent working, the work is not what makes the replies slow." }
  - { text: "Nothing: the samples in `select` should be ignored, and the other 5% is the profile", explanation: "The replies are slow and the processor is idle, so whatever the tasks are waiting for is the cause. The 5% cannot be." }
explanation: "A loop that is nearly always in `select` has tasks that are nearly always suspended. Where they are suspended, a database call, a lock, a queue, another service, is what `--async-mode all` records."
```
