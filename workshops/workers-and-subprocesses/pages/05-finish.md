---
title: Finish
requires: [verify:server-stopped, quiz:what-it-follows]
---

# Finish

gunicorn stopped when its twenty seconds were up, and its workers
with it. Make sure of it before leaving.

```{verify}
:id: server-stopped
:label: Nothing is left listening on the port
:trigger: page-enter
:substrate: shell
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=2)" 2>/dev/null && { echo "The site still answers on port $SERVER_PORT. Wait for its twenty seconds to end, or click in the server terminal and press Ctrl-C, then check again"; exit 1; } || echo "Nothing is listening on port $SERVER_PORT"
```

## When to reach for it

Whenever the process you start is not the one that does the work:

- a `ProcessPoolExecutor` or a `multiprocessing.Pool`,

- a server that starts workers, such as gunicorn, or uvicorn with
  `--workers`,

- a test runner that spreads the tests over processes,

- a script that runs other Python scripts with `subprocess`.

The sign that you need it is the one you saw: a profile that is all
waiting, of a program that is plainly busy.

## What to expect of it

- **A file for each process**, named by its number. Tell them apart
  by what is in them.

- **More files than you counted on**, since libraries start
  processes of their own.

- **No total.** Each file is one process. What the whole program
  spent on a function is the sum over the files.

- **No live view.** `--live` takes over the terminal, and one
  terminal cannot show several profilers, so the profiler refuses
  the two together.

- **Descendants only.** The profiler follows the processes that the
  program it started goes on to start. A process that was already
  running, started by something else, is another matter, and the
  subject of a later workshop.

```{quiz}
:id: what-it-follows
question: "A nightly job is a Python script that runs `pg_dump` to copy a database, then starts three Python scripts with `subprocess` to process the copy. It is profiled with `--subprocesses`. How many profiles are written?"
options:
  - { text: "One, since `subprocess` is not `multiprocessing`", explanation: "The profiler looks for new processes descended from the program, however they were started." }
  - { text: "Four: the script and the three Python scripts it starts", correct: true }
  - { text: "Five: the script, `pg_dump` and the three Python scripts", explanation: "`pg_dump` is not a Python program. The profiler finds no Python in it and leaves it alone." }
  - { text: "Three: only the children are profiled", explanation: "The process the profiler started is profiled as it always is. `--subprocesses` adds its descendants." }
explanation: "Every Python process descended from the one the profiler started gets a profiler, and the one it started has its own. A process that is not Python is ignored. The time the job spends waiting for `pg_dump` shows in the script's own profile, as waiting."
```

Next in these workshops is **Profiling a test suite**, which points
the profiler at pytest. Press Finish to go there.
