---
title: Following the children
requires: [verify:probe-ran, verify:jobs-profiled, verify:worker-to-read, quiz:why-so-many]
---

# Following the children

**`--subprocesses`** has the profiler watch for processes that the
program starts. When a new one appears, and it is a Python process,
the profiler starts another profiler for it, with the same options,
and that one watches for children in its turn. Every Python process
descended from the one you started is profiled, each by a profiler
of its own, up to a hundred at a time. Processes that are not
Python, a shell or a compiler, are left alone.

## Who may read the children

There is a catch, and it is the operating system's, not the
profiler's. A process may read another process's memory only when
it is allowed to, and on Linux the kernel's usual rule, a setting
called `ptrace_scope` at 1, is that a process may read its own
descendants and nothing else. That is why `run` always works: the
profiler starts the program, so the program is its child. But the
profiler started for a worker is not the worker's ancestor. It is a
sibling of the program, and it *attaches* to the worker from
outside, which the usual rule refuses. Where the setting is 0, and
in a container on Docker Desktop, whose kernel has no such rule,
every child is followed. On most Linux machines, and on most
hosted ones, the children are refused, one by one, and the profiler
that was refused says nothing: only the parent's file is written.

The way to find out what this machine allows is to try. The action
starts a small Python program in the background, one that the
profiler did not start, runs `dump` against it, and keeps only
whether that worked: `yes` or `no`. The answer is kept for the rest
of the workshop.

```{execute-capture}
:id: probe-attach
:title: Find out whether the profiler may read a process it did not start
:capture: can_attach
python -c "import time; time.sleep(5)" & pid=$!; sleep 0.5; if python -m profiling.sampling dump $pid >/dev/null 2>&1; then echo yes; else echo no; fi; kill $pid; wait $pid 2>/dev/null; true
```

```{verify}
:id: probe-ran
:label: The machine has answered
:trigger: after:probe-attach
:substrate: shell
test "$CAN_ATTACH" = yes -o "$CAN_ATTACH" = no && echo "This machine answers: $CAN_ATTACH" || { echo "No answer yet: run the action above"; exit 1; }
```

````{when} can_attach == "yes"
On this machine the answer is **yes**: a profiler may read a
process it did not start, so `--subprocesses` follows every child.
````

````{when} can_attach == "no"
On this machine the answer is **no**, which is the usual answer on
Linux. `--subprocesses` will follow none of the children here, and
the page shows what that looks like, and then what it would have
found, from a machine that allowed it.
````

## Profile the job runner and its children

Run the job runner under the profiler with `--subprocesses`. The
profiler says so each time it starts on a child, and each profiler
writes a file of its own. No `-o` is given, because one name will
not do for several files: each is called `flamegraph_<pid>.html`,
where the *pid* is the number the operating system gave the
process.

```{execute}
:id: profile-jobs
:session: server
:title: Profile the job runner and the processes it starts
:wait: prompt
python -m profiling.sampling run --subprocesses --flamegraph -m gazette.jobs
```

Move the files to a directory of their own, and list them.

```{execute}
:id: move-jobs
:session: server
:title: Move the flame graphs to jobs/ and list them
:wait: prompt
mkdir -p jobs && mv flamegraph_*.html jobs/ && ls -l jobs
```

```{verify}
:id: jobs-profiled
:label: The flame graphs in jobs/ are what this machine allows
:trigger: after:move-jobs
import os
from pathlib import Path

answer = os.environ.get("CAN_ATTACH", "")
assert answer in ("yes", "no"), "The machine has not been asked yet: run the action under 'Who may read the children' first"
files = sorted(Path("jobs").glob("flamegraph_*.html"))
assert files, "There are no flame graphs in jobs/ yet: run the two actions above, in order"
workers = [file for file in files if "build_digest" in file.read_text(encoding="utf-8", errors="replace")]
if answer == "yes":
    assert len(files) >= 5, (
        f"There are {len(files)} flame graphs in jobs/; expected one for the parent and one for each of four workers at least. "
        "Was the profiler run with --subprocesses? Run the two actions above again"
    )
    assert len(workers) >= 3, (
        f"{len(workers)} of the {len(files)} flame graphs in jobs/ have build_digest in them; expected the four workers' to. "
        "Run the two actions above again"
    )
    print(f"{len(files)} flame graphs in jobs/, {len(workers)} of them of workers building digests")
else:
    assert not workers, (
        f"{len(workers)} of the flame graphs in jobs/ have build_digest in them, so a worker was followed after all; "
        "the machine answered no, so run the action under 'Who may read the children' again"
    )
    print(f"{len(files)} flame graph in jobs/, the parent's, with no build_digest in it: this machine refused the children, as it said it would")
```

````{when} can_attach == "yes"
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

```{file-open}
:id: open-worker
:title: Open worker.html in the HTML viewer
:path: worker.html
:factory: HTML Viewer
:area: desk
```
````

````{when} can_attach == "no"
## What the children would have shown

One file, and it is the parent's: the profile you already have,
nearly every sample waiting. Nothing was printed about the
four workers, the profilers started for them having been refused
in silence. That silence is the thing to remember about
`--subprocesses`: a run that writes fewer files than the program
had processes has been refused, and the parent's file alone is the
misleading profile of the last page, not a profile of the program.

On a machine that allows it, the same command writes seven files
for this program, and a worker's is shipped with the workshop,
made there. Open it.

```{file-open}
:id: open-worker-example
:title: Open worker-example.html in the HTML viewer
:path: worker-example.html
:factory: HTML Viewer
:area: desk
```
````

```{verify}
:id: worker-to-read
:label: There is a worker's flame graph to read
:trigger: action
import os
from pathlib import Path

answer = os.environ.get("CAN_ATTACH", "")
assert answer in ("yes", "no"), "The machine has not been asked yet: run the action under 'Who may read the children' first"
name = "worker.html" if answer == "yes" else "worker-example.html"
file = Path(name)
if answer == "yes":
    assert file.exists(), "No worker.html yet: run the copy command above"
else:
    assert file.exists(), "worker-example.html is missing; restart the workshop to get it back"
text = file.read_text(encoding="utf-8", errors="replace")
assert "build_digest" in text and "_process_worker" in text, (
    f"{name} is not the flame graph of a pool worker" + ("; run the copy command above again" if answer == "yes" else "; restart the workshop to get it back")
)
if answer == "yes":
    print("worker.html is the flame graph of one of the pool's workers")
else:
    print("This machine refuses the children; worker-example.html is a worker's flame graph made where they were allowed")
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
  This is where the time went, and it is an ordinary flame
  graph of an ordinary function, to be read and acted on as any
  other.

The sidebar's **Duration** is a little less than the program's,
since the worker was started after the program was.

```{quiz}
:id: why-so-many
question: On a machine that allows it, this program, with a pool of four workers, gives the profiler seven files to write. One is the parent's and four are the workers'. What are the other two?
options:
  - { text: "Workers that were started and given nothing to do", explanation: "The pool starts as many workers as it was asked for, four, and all four were given batches." }
  - { text: "Processes that `multiprocessing` starts for its own purposes, which are Python processes too", correct: true }
  - { text: "The profilers, which are Python programs themselves", explanation: "The profilers are children of the profiler you started, not of the program, and a profiler does not profile itself." }
  - { text: "The same worker profiled twice, since the profilers overlap", explanation: "A process has one number for as long as it lives, and each file is named by it." }
explanation: "On Linux, `multiprocessing` starts a server process from which the workers are forked, and another that keeps track of shared resources. Both are Python processes descended from the program, so both are profiled. Their files show them waiting."
```
