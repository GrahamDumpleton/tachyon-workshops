---
title: Finish
requires: [verify:server-stopped, quiz:what-a-request-costs]
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

## What a request costs

A profile of a server is a total: every request of the twenty
seconds, added together. What you usually want to know is what one
request costs, and the two are joined by how many requests there
were.

- The table from `load.py` is the view from outside: how many
  requests of each kind, and how long a reader waited for each.

- The flame graph is the view from inside: of all the time the
  server's threads spent, the share that went on each kind, and
  where within it.

Here they agree. Searches were a tenth of the requests and most of
the time the requests took, which is what a request that takes many
times as long as the others comes to. When they do not agree, a
page that readers wait a long time for and that has little width in
the graph, the time is going somewhere the profiler is not looking:
in a queue before the request reaches a thread, in the network, or
in another process.

```{quiz}
:id: what-a-request-costs
question: In a profile of a busy server, `render_pdf` is a twentieth of the graph and `list_items` is half. `render_pdf` was called twice a minute and `list_items` five hundred times a second. Which statement is right?
options:
  - { text: "`list_items` is the slow request, and the one readers are waiting for", explanation: "It has the most time in total, from being called so often. Each call may be very quick." }
  - { text: "`render_pdf` costs far more per request, and `list_items` costs far more in total", correct: true }
  - { text: "`render_pdf` does not matter, since it is a twentieth of the graph", explanation: "It does not matter much to the machine. To the reader who asked for the PDF, a request that takes seconds matters." }
  - { text: "The profile is wrong, since a function called twice a minute cannot be a twentieth of the samples", explanation: "It can if each call takes long enough: two calls of a second and a half each are a twentieth of a minute." }
explanation: "Width is total time: the cost of a call multiplied by the number of calls. To make the server cheaper to run, look at `list_items`. To make the slowest page quicker, look at `render_pdf`. The profile cannot tell which you meant, so count the requests as well."
```

You know which view of the gazette is expensive, and not yet why.
Next in these workshops is **The slow endpoint**, which takes the
same application, finds the line and fixes it. Press Finish to go
there.
