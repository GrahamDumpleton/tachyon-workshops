---
title: Following the children
requires: [verify:jobs-profiled, verify:worker-copied, quiz:why-so-many]
---

# Following the children

**`--subprocesses`** has the profiler watch for processes that the
program starts. When a new one appears, and it is a Python process,
the profiler starts another profiler for it, with the same options,
and that one watches for children in its turn. Every Python process
descended from the one you started is profiled, each by a profiler
of its own, up to a hundred at a time. Processes that are not
Python, a shell or a compiler, are left alone.

```{execute}
:id: profile-jobs
:session: server
:title: Profile the job runner and the processes it starts
:wait: prompt
python -m profiling.sampling run --subprocesses --flamegraph -m gazette.jobs
```

The profiler says so each time it starts on a child, and each
profiler writes a file of its own. No `-o` was given, because one
name will not do for several files: each is called
`flamegraph_<pid>.html`, where the *pid* is the number the operating
system gave the process. Move them to a directory of their own, and
list them.

```{execute}
:id: move-jobs
:session: server
:title: Move the flame graphs to jobs/ and list them
:wait: prompt
mkdir -p jobs && mv flamegraph_*.html jobs/ && ls -l jobs
```

```{verify}
:id: jobs-profiled
:label: There is a flame graph for each process, and the workers' have build_digest
:trigger: after:move-jobs
from pathlib import Path

files = sorted(Path("jobs").glob("flamegraph_*.html"))
assert files, "There are no flame graphs in jobs/ yet: run the two actions above, in order"
workers = [file for file in files if "build_digest" in file.read_text(encoding="utf-8", errors="replace")]
assert len(files) >= 5, (
    f"There are {len(files)} flame graphs in jobs/; expected one for the parent and one for each of four workers at least. "
    "Was the profiler run with --subprocesses? Run the two actions above again"
)
assert len(workers) >= 3, (
    f"{len(workers)} of the {len(files)} flame graphs in jobs/ have build_digest in them; expected the four workers' to. "
    "Run the two actions above again"
)
print(f"{len(files)} flame graphs in jobs/, {len(workers)} of them of workers building digests")
```

## Which file is which

Seven files, for a program with a pool of four. The numbers say
nothing of what each process was, only the order they were started
in, so the way to tell the files apart is by what is in them. One
of the workers will do, since the four did the same work. Find one
by a function that only a worker runs, and copy it to a name of its
own.

```{execute}
:id: copy-worker
:session: server
:title: Copy a worker's flame graph to worker.html
:wait: prompt
cp "$(grep -l syllables jobs/flamegraph_*.html | head -1)" worker.html
```

```{verify}
:id: worker-copied
:label: worker.html is the flame graph of a worker
:trigger: after:copy-worker
:substrate: shell
python -c "from pathlib import Path; f = Path('worker.html'); assert f.exists(), 'No worker.html yet: run the copy command above'; t = f.read_text(encoding='utf-8', errors='replace'); assert 'build_digest' in t and '_process_worker' in t, 'worker.html is not the flame graph of a worker; run the copy command above again'; print('worker.html is the flame graph of one of the pool\'s workers')"
```

```{command}
:id: open-worker
:title: Open worker.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/worker.html", "factory": "HTML Viewer" }
```

````{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar. If the tab is blank though the file is trusted,
close the tab and click the action again.
````

This is the profile the program deserved. Read it downward.

- The first boxes are `multiprocessing` starting the worker, and
  `_process_worker` from `concurrent.futures`, the loop in which a
  worker takes a job, runs it and sends back the result.

- `build_batch` is the job, and nearly as wide as the graph.

- Beneath it `build_digest` has a box for each of its lines that
  was sampled, and beneath those are `syllables` and `keywords`.
  This is where the three seconds went, and it is an ordinary flame
  graph of an ordinary function, to be read and acted on as any
  other.

The sidebar's **Duration** is a little less than the program's,
since the worker was started after the program was.

```{quiz}
:id: why-so-many
question: The pool has four workers, and the profiler wrote seven files. One is the parent's. What are the other two?
options:
  - { text: "Workers that were started and given nothing to do", explanation: "The pool starts as many workers as it was asked for, four, and all four were given batches." }
  - { text: "Processes that `multiprocessing` starts for its own purposes, which are Python processes too", correct: true }
  - { text: "The profilers, which are Python programs themselves", explanation: "The profilers are children of the profiler you started, not of the program, and a profiler does not profile itself." }
  - { text: "The same worker profiled twice, since the profilers overlap", explanation: "A process has one number for as long as it lives, and each file is named by it." }
explanation: "On Linux, `multiprocessing` starts a server process from which the workers are forked, and another that keeps track of shared resources. Both are Python processes descended from the program, so both are profiled. Their files show them waiting."
```
