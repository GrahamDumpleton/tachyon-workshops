---
title: Finish
requires: [verify:server-stopped, quiz:dump-or-attach]
---

# Finish

Stop the web site, which has been running since the second page.
The action sends it the interrupt that Ctrl-C would.

```{interrupt}
:id: stop-server
:session: server
:title: Stop the web site
```

```{verify}
:id: server-stopped
:label: The web site has stopped
:trigger: after:stop-server
:substrate: shell
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=2)" 2>/dev/null && { echo "The site still answers on port $SERVER_PORT; stop it with the action above"; exit 1; } || echo "Nothing is listening on port $SERVER_PORT"
```

## The two commands

- **`dump <pid>`** prints the stack of the main thread, once.
  **`dump -a <pid>`** prints every thread's. It is for a program
  that is stuck, or to see at a glance what a busy one is doing.

- **`attach <pid>`** samples a running program as `run` samples one
  it started, with the same options and the same formats. `-d`
  says for how long, and the program carries on afterwards.
  `attach --live` gives the live display, and `attach --subprocesses`
  follows the program's children.

- **The profiler and the program must be the same version of
  Python.** With `run` they always are. With `attach` it is for you
  to see to: use the interpreter that the service runs on.

- **The kernel decides** whether either may read the process, and
  the way to find out is to try a `dump`.

```{quiz}
:id: dump-or-attach
question: "A web service answers, and slowly since this morning. It has been up for three weeks and the team will not restart it without a reason. The machine allows attaching. What do you run?"
options:
  - { text: "`dump -a`, once", explanation: "One reading says where each thread is at one moment. A service that is slow and not stuck is in many places, and you want to know the share of each." }
  - { text: "`attach -a -d 30 --flamegraph`, while it is being slow", correct: true }
  - { text: "`run -a -d 30 --flamegraph`, with the service's start command", explanation: "That starts a second copy of the service, fresh, which is not the one that has been slow since this morning." }
  - { text: "`attach` with no `-d`, left running until the service is restarted", explanation: "That samples until somebody stops it, which may be weeks, for a question that thirty seconds would answer." }
explanation: "Slow is a question of shares, which needs many samples, and the process to sample is the one that is slow. Thirty seconds of `attach` with every thread gives the flame graph of the service as it is now, and leaves it running."
```

Next in these workshops is **A profile from production**, the last
of them, which carries a recording from the machine that made it to
a notebook and a chart. Press Finish to go there.
