---
title: Finish
requires: [verify:server-stopped, quiz:why-the-loop]
---

# Finish

First, stop the feed server. The action sends it the interrupt that
Ctrl-C would.

```{interrupt}
:id: stop-server
:session: server
:title: Stop the feed server
```

```{verify}
:id: server-stopped
:label: The feed server has stopped
:trigger: after:stop-server
:substrate: shell
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/feeds/0.xml', timeout=2)" 2>/dev/null && { echo "The server still answers on port $SERVER_PORT; stop it with the action above"; exit 1; } || echo "Nothing is listening on port $SERVER_PORT"
```

An asyncio program has one stack and many tasks, and the profiler
can read either.

- **The thread's stack** is what the profiler reads unless told
  otherwise. The work is in it, beneath the event loop. The waiting
  of every task is in one function of the loop, with nothing to say
  whose it is.

- **`--async-aware`** reads the tasks. Each task begins with a
  `<task>` marker carrying its name, and the stack beneath is the
  chain of awaits, across tasks. With the default
  `--async-mode running`, samples with no running task are left out.

- **`--async-mode all`** records the suspended tasks as well, each
  at the await where it stopped. A sample counts once for every
  task in it, so the times are added over the tasks.

The crawler fetched twenty feeds in a third of the time of the
program that fetched them in turn, and the profile of it showed what
is left: half a second of merging, which an index of the stories
already seen would remove, and a queue for connections that is as
long as the limit makes it.

```{quiz}
:id: why-the-loop
question: Why is a task that is waiting for a server not on the stack the profiler usually reads?
options:
  - { text: "The profiler skips frames that belong to coroutines", explanation: "It does not. A coroutine that is running is on the stack like any function, as `read_feed` was." }
  - { text: "At an `await` that cannot finish, the coroutine is suspended and the thread returns to the event loop, so the thread's stack no longer holds it", correct: true }
  - { text: "Each task runs in a thread of its own, and the profiler samples only the main thread", explanation: "Tasks share one thread. That is why only one of them is ever running." }
  - { text: "The task has finished by the time the sample is taken", explanation: "It has not finished. It is kept by the event loop, to be resumed at the same line when the reply arrives." }
explanation: "A suspended coroutine is an object the event loop is holding, not a frame on the thread's stack. Async-aware profiling finds those objects through asyncio's record of its tasks."
```

Next in these workshops is **Native code and the collector**, which
shows two things the Python stack cannot: time inside C code, and
time in the garbage collector. Press Finish to go there.
