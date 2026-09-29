---
title: Finish
requires: [verify:server-stopped, quiz:what-to-record]
---

# Finish

Both servers stopped when their twenty seconds were up. Make sure
of it before leaving.

```{verify}
:id: server-stopped
:label: Nothing is left listening on the port
:trigger: page-enter
:substrate: shell
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=2)" 2>/dev/null && { echo "The site still answers on port $SERVER_PORT. Wait for its twenty seconds to end, or click in the server terminal and press Ctrl-C, then check again"; exit 1; } || echo "Nothing is listening on port $SERVER_PORT"
```

## From a host to a chart

- **Record in the binary format**, with `run` or `attach`, for a
  fixed time. It costs the least and keeps the most.

- **Record the same way every time**: the same options, the same
  length, the same kind of load.

- **Copy the file, and keep it.** Next month's question will be
  whether things were always like this.

- **Replay at the desk**: `--flamegraph` to look, `--jsonl` for a
  program to read, `--pstats` for the standard library and the
  tools built on it, `--diff-flamegraph` to colour one recording by
  another.

- **Put the numbers in a notebook** when the question is how much,
  and in a script when it is asked every night.

A step further is to record all the time: a profiler beside each
service, sampling at a low rate for a minute in every ten, and
sending its recordings somewhere to be kept. That is called
continuous profiling, and everything it is made of is on this page.

```{quiz}
:id: what-to-record
question: "You have ten minutes on a production host, and a service that is slow. You do not yet know whether you will want a flame graph, a heatmap or a table. What do you record?"
options:
  - { text: "`--flamegraph`, since it shows the most", explanation: "A flame graph is a picture of the samples, added up. A heatmap cannot be made from it afterwards, nor a comparison." }
  - { text: "`--binary`, and decide at the desk", correct: true }
  - { text: "All three, in three runs", explanation: "That takes three times as long on the host, and gives three profiles of three different minutes." }
  - { text: "`--jsonl`, since a program can read it", explanation: "The JSON lines hold counts already added up by frame. The stacks are gone, so no flame graph can be made from them." }
explanation: "The binary recording holds every sample, so every other format can be made from it, as often as you like and wherever you like. It is also the cheapest for the profiler to write, which matters on a host that is already struggling."
```

That is the last of **Tachyon on real applications**. Press Finish
for a summary of where you have been and two places to go next.
