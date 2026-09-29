---
title: Finish
requires: [verify:all-stopped, quiz:which-remedy]
---

# Finish

The web site stopped when its fifteen seconds were up. Stop the
index service, which has been running since the second page. The
action sends it the interrupt that Ctrl-C would.

```{interrupt}
:id: stop-index
:session: index
:title: Stop the index service
```

```{verify}
:id: all-stopped
:label: Nothing is left listening on either port
:trigger: after:stop-index
:substrate: shell
python -c "import os, sys, urllib.request
for name, path in (('SERVER_PORT', '/health'), ('UPSTREAM_PORT', '/lookup?q=council')):
    port = os.environ[name]
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{port}{path}', timeout=2)
    except OSError:
        continue
    sys.exit(f'Something still answers on port {port}. Stop the index service with the action above; the web site stops when its fifteen seconds are up')
print('Nothing is listening on either port')"
```

## Reading an asyncio service

- **Look at what is running, not at what is slow.** The request
  that readers complain of is often one that waits, and a task that
  is waiting is not in the profile. The one that makes it wait is.

- **The main thread in wall-clock time** is the first profile to
  make. Under `_run_once`, `select` is the loop with nothing to do
  and `Handle._run` is the loop at work. A loop that is mostly at
  work is a loop that is being held.

- **`--async-aware`** gives the same by task, without the loop's
  frames, as a table. **`--async-mode all`** counts the parked
  tasks too, for when the loop is idle and the question is what
  everyone is waiting for.

- **A call that waits** can go to a thread. **A call that
  computes** has to go to another process, or be made cheaper, or
  be done ahead of time.

```{quiz}
:id: which-remedy
question: "A coroutine in an asyncio service resizes an uploaded image with a library written in pure Python, which takes a fifth of a second. Every other request stalls while it runs. Which remedy fits?"
options:
  - { text: "Put `await asyncio.sleep(0)` before the call, so that other tasks get a turn", explanation: "They get one turn, before the call. The call still holds the loop for a fifth of a second once it starts." }
  - { text: "`await asyncio.to_thread(resize, image)`", explanation: "That suits a call that waits. This one computes, in Python, so the thread would hold the interpreter's lock and the loop would queue for it." }
  - { text: "Run it in a pool of processes, with `run_in_executor`", correct: true }
  - { text: "Profile with `--async-mode all` to find what the other tasks are waiting for", explanation: "They are waiting for the loop, which no table will name. What is running on the loop is what to look for, and you already know it." }
explanation: "A fifth of a second of computing in Python has to leave the process, or the loop will wait for it one way or another. A pool of processes has an interpreter, and a lock, for each worker."
```

Next in these workshops is **Workers and subprocesses**, which
profiles the processes that the work has just been moved to. Press
Finish to go there.
