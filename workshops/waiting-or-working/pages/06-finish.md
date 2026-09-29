---
title: Finish
requires: [verify:server-stopped, quiz:what-wall-counts]
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

The profiler takes the same samples whatever the mode, and the mode
chooses which to keep. There are four.

- **`--mode wall`**, the default, keeps them all. Its table is where
  the time went as a clock measures it, waiting included.

- **`--mode cpu`** keeps the samples in which the thread was on a
  processor. Its table is where the computing went.

- **`--mode gil`** keeps the samples in which the thread held
  Python's global interpreter lock, which is the subject of the next
  of these workshops.

- **`--mode exception`** keeps the samples in which the thread was
  handling an exception, which is the one after.

Wall-clock against CPU is the comparison to make first on any slow
program, because it sorts the program's time into waiting and
working, and the two are fixed in different ways.

```{quiz}
:id: what-wall-counts
question: Why does a function that is blocked, waiting for a reply from a server, have samples at all in wall-clock mode?
options:
  - { text: "Waiting uses the processor, a little at a time", explanation: "A blocked thread uses none. The operating system does not run it until the reply arrives." }
  - { text: "The profiler looks at the thread's stack on a timer, whether or not the thread is running, and a blocked thread still has a stack", correct: true }
  - { text: "The program tells the profiler when it starts and stops waiting", explanation: "The program does not know it is being profiled and tells the profiler nothing." }
  - { text: "The samples are of the server, which is busy preparing the reply", explanation: "The server is another process, and the profiler is reading only the feed reader." }
explanation: "The profiler reads the thread's stack from outside, a thousand times a second, and a thread that is blocked is still on the line that made the request. Wall-clock mode keeps those samples and CPU mode drops them."
```

Next in these workshops is **Who holds the GIL?**, which profiles a
program with several threads and asks which of them is running.
Press Finish to go there.
