---
title: All the threads
requires: [verify:all-threads]
---

# All the threads

`-a`, or `--all-threads`, has the profiler read the stack of every
thread in the process at each sample. Ask for a flame graph this
time, the picture of every call path with the width of each box its
share of the samples, since it can do something the table cannot:
show the threads apart.

```{execute}
:id: profile-all
:session: shell
:title: Profile every thread and draw a flame graph
:wait: prompt
python -m profiling.sampling run -a --flamegraph -o digest.html gazette/digest.py
```

```{command}
:id: open-digest-graph
:title: Open digest.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/digest.html", "factory": "HTML Viewer" }
```

```{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted. On Binder, in a codespace and in the workshops' container
the viewer trusts HTML files by default; on your own JupyterLab click
the **Trust HTML** button in the viewer's toolbar.
```

The graph has the root at the top, and beneath it two columns where
every graph so far had one. The narrow one on the right starts at
`_run_module_as_main` and is the main thread: `main`, then
`Thread.join`, the whole of the table from the last page. The wide
one starts at `Thread._bootstrap`, which is where every thread made
by `threading` begins, and holds the other five threads laid on top
of each other: `worker` and beneath it `build_digest`, `keywords` and
`syllables`, and to the right of `worker`, `report_progress`.

The profile summary in the sidebar on the left counts three or four
times as many samples as the run had milliseconds. Each time the
profiler looked, it read six stacks, and each is a sample. The error
rate is also much higher than you have seen, a fifth or a quarter,
because these threads call small functions thousands of times a
second and a stack that is changing can fail to read. The samples
that were kept are sound.

## One thread at a time

Scroll the sidebar down to **Thread Filter**, below the runtime
statistics, and open the list: All Threads, and six threads by
number. The first is the main thread and the second is the one
writing the progress log. Choose the third, which is a worker.

The graph is now that thread alone, one column from
`Thread._bootstrap` down to `syllables`. Above the filter, **Runtime
Stats** has changed with it, and says what this thread was doing when
it was sampled:

- **GIL Held**, about a quarter of the time.

- **Waiting GIL**, about three quarters.

- **GIL Released**, next to nothing.

The thread spent three quarters of its life waiting for something
called the GIL. Choose each of the other three workers and they say
the same. Four threads, each running a quarter of the time: that is
one thread's worth of running between them.

Now choose the second thread in the list, the one writing the
progress log. It has almost nothing to do, a line to write every
five milliseconds, and it spent most of its time waiting for the GIL
too. A thread with little work can be kept from it by threads with a
lot, which is what a service that has stopped answering while it is
busy often turns out to be.

Set the filter back to All Threads. The next page says what they
were all queueing for.

```{verify}
:id: all-threads
:label: digest.html holds the workers' threads as well as the main thread
:trigger: after:profile-all
:substrate: shell
test -s digest.html && grep -q build_digest digest.html && grep -q "Thread._bootstrap" digest.html && echo "digest.html holds build_digest, under Thread._bootstrap" || { echo "digest.html is missing or has no worker threads in it; run the command above, which has -a"; exit 1; }
```
