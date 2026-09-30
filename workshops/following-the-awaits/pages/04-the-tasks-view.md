---
title: The task's view
requires: [verify:tasks-graph]
---

# The task's view

`--async-aware` changes what the profiler reads at each sample. It
still reads the program's memory from outside, at the same rate.
Instead of walking the thread's stack, it finds asyncio's record of
its tasks and asks which task is running and which task is awaiting
which. From those it builds a stack the program never had: the
running task's coroutines, beneath the task that is waiting for it,
beneath the task waiting for that one. The event loop is left out.

Draw the result as a flame graph, where the shape is easiest to see.

```{execute}
:id: profile-tasks
:session: shell
:title: Profile the crawler by task
:wait: prompt
python -m profiling.sampling run --async-aware --flamegraph -o tasks.html gazette/crawl.py {{ server_port }}
```

```{file-open}
:id: open-tasks
:title: Open tasks.html in the HTML viewer
:path: tasks.html
:factory: HTML Viewer
:area: desk
```

````{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar.
````

Read it from the top, which in this flame graph is the root.

- **The root is `Task-1`**, marked `<task>` where a function would
  have its file. It is not a function. The profiler puts a box like
  this at the start of every task, named as asyncio named the task,
  and `Task-1` is the one `asyncio.run` made for `main`.

- **Beneath it is `main`, twice**, because the box for a function
  carries the line it was on. The wide one is line 88, the call to
  `merge`, with `merge` and `same_story` beneath it as in any flame
  graph. The narrow one is line 85, the `await` of `gather`.

- **Beneath line 85 are the tasks `gather` started**, a thin box each
  for `Task-2` to `Task-21`, with `read_feed` and `parse` beneath.
  Click the narrow `main` to zoom in on them, and the home button in
  the header to come back. The stack reads as the program is written:
  `main` awaits the feeds, this feed was being parsed.

Two things are missing, and both are the point. The six boxes of the
event loop are gone, so the graph starts at your code. And the wait
is gone. Look at the sample count in the sidebar: about five hundred,
from a run that took a thousand and a half. While every task was
waiting, no task was running, and a sample with no running task has
nothing to show. This is `--async-mode running`, the default for
`--async-aware`: only the task that was running when the sample was
taken.

So this view answers "which task is using the processor", which for
the crawler is `Task-1`, merging, by a wide margin. What the tasks
were waiting for is the next page.

```{verify}
:id: tasks-graph
:label: tasks.html starts at the tasks and leaves out the event loop
:trigger: after:profile-tasks
:substrate: shell
test -s tasks.html || { echo "No tasks.html yet: run the --async-aware command above, which writes it"; exit 1; }
grep -q "Task-1 (<task>" tasks.html || { echo "tasks.html has no task markers in it; was it written with --async-aware?"; exit 1; }
grep -q "Selector.select" tasks.html && { echo "tasks.html holds the event loop's select; was it written with --async-aware?"; exit 1; }
grep -q "read_feed" tasks.html && echo "tasks.html holds Task-1 and read_feed, and not the event loop's wait" || { echo "tasks.html does not name read_feed; did the crawler fail? Check that the server is running"; exit 1; }
```
