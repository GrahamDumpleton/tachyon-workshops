# Tachyon workshops: outline

The design of the collections in this repository: how they are
organised, what each workshop covers, its name and format, and the
decisions that cut across all of them. It is a living document. Read it
before adding a workshop, and update it when one is added, changed or
dropped: the status table at the end records where each workshop
stands, and the open questions section shrinks as they are settled.

## What this repository is

Guided JupyterLab workshops for
[Tachyon](https://docs.python.org/3.15/library/profiling.sampling.html),
the statistical sampling profiler added to Python 3.15 as the
`profiling.sampling` module, in collections that are each a course of
their own. The first collection, **Profiling with Tachyon**, is
fourteen workshops on the profiler itself: what a sample is and why
taking one costs the profiled program nothing, how to read the table,
the flame graph and the heatmap it writes, how to choose what to
measure, what it shows of threads, async code, native code, the garbage
collector and the bytecode, how to compare two profiles, and how to
watch a program live. The second, **Tachyon on real applications**, is
seven workshops that point the profiler at the kinds of program people
run and want to understand: a Flask application under load, a slow
endpoint, an async service, worker processes, a test suite, a process
already running, and a profile carried away from production. The
collections share this repository's tooling and nothing else: each has
its own index, id, numbering and audience.

The point of both collections is understanding as much as technique.
Most Python developers have never profiled anything, or have run
cProfile once, been alarmed by how slow it made things, and stopped.
Tachyon changes what profiling costs, and the workshops exist to
explain why that is, what "sampling" means, what a sampling profiler
can and cannot tell you, and what the pictures it draws are saying,
with the flag that produces each picture arriving after the reason to
want it. Every workshop opens with the question a developer would
actually have ("why is this slow?", "is it waiting or working?", "which
thread has the interpreter?") and only then reaches for the profiler.

The fundamentals collection assumes Python and a terminal, nothing
about profiling. The applications collection assumes what the first
three fundamentals workshops teach, a sample, the table and the flame
graph, and restates it in a sentence where it matters, so it can be
taken on its own by anyone who has run the profiler once. The
applications collection is the one that answers "what would this look
like on my service?", which is the question that makes people try a
profiler, so it earns its place as a separate course rather than a
tail on the first.

Out of scope, deliberately: the deterministic profiler beyond the one
comparison in workshop 2, since `profiling.tracing` is cProfile under a
new name and well covered elsewhere; micro-benchmarking with `timeit`;
memory profiling, which Tachyon does not do; the undocumented Python
API of `profiling.sampling.sample` (see "Topics the fundamentals
collection leaves out"); and anything that needs root, a capability or
a change to a kernel setting, which rules out the attach and dump
commands on most hosts (see workshop 6 of the applications collection
for how far they are taken).

## Source material

The subject is part of Python, so there is no subject submodule. The
authorities, read at the release the workshops teach, never from
memory:

- [profiling.sampling](https://docs.python.org/3.15/library/profiling.sampling.html):
  the module page. The commands `run`, `attach`, `dump` and `replay`;
  the sampling options (`-r`, `-d`, `-a`, `--realtime-stats`,
  `--native`, `--no-gc`, `--opcodes`, `--async-aware`,
  `--subprocesses`, `--blocking`); the modes (`--mode` wall, cpu, gil,
  exception, and `--async-mode` running or all); the output formats
  (pstats, collapsed, flame graph, differential flame graph, gecko,
  heatmap, JSONL, binary); live mode and its keys; how time is
  estimated and what sampling efficiency means; the platform
  requirements and the version rule.

- [profiling](https://docs.python.org/3.15/library/profiling.html),
  [profiling.tracing](https://docs.python.org/3.15/library/profiling.tracing.html)
  and [pstats](https://docs.python.org/3.15/library/pstats.html), for
  workshop 2 and for every check that loads a `.pstats` file.

- [What's New In Python 3.15](https://docs.python.org/3.15/whatsnew/3.15.html)
  and [PEP 799](https://peps.python.org/pep-0799/), for why the
  `profiling` package exists, why a sampling profiler was added to the
  standard library, the claim of up to a million samples a second, and
  the credit to Pablo Galindo and László Kiss Kollár.

- The module's source in the installed interpreter,
  `Lib/profiling/sampling/`: `sample.py` (the `SampleProfiler` class,
  the `sample()` function and the command line), the collectors, and
  the `_remote_debugging` C module that reads the other process's
  memory. The `--help` of each subcommand is the list of options for
  the release actually installed, which is what a page must match.

- For the applications collection, the documentation of
  [Flask](https://flask.palletsprojects.com/) and Werkzeug's
  development server (threaded by default),
  [Starlette](https://www.starlette.io/) and
  [uvicorn](https://www.uvicorn.org/),
  [gunicorn](https://docs.gunicorn.org/) and its worker model, and
  [pytest](https://docs.pytest.org/).

- For the mechanism, Linux `process_vm_readv(2)` and `ptrace(2)`, the
  Yama LSM's `ptrace_scope` documented in the kernel's
  `Documentation/admin-guide/LSM/Yama.rst`, and Apple's
  `task_for_pid` and the `com.apple.security.cs.debugger` entitlement,
  each linked from workshop 3 for the reader who wants more.

What was checked on 2026-09-29, against Python 3.15.0rc2 in a
`python:3.15-rc-slim` container as a non-root user, and is relied on
below:

- `run` works with no privilege at all, including with every
  capability dropped, because the profiler is the parent of the
  program it runs. `attach` and `dump` against a process the profiler
  did not start also worked in that container, because Docker
  Desktop's kernel has no Yama LSM; on a stock Linux with
  `ptrace_scope` 1 they would not, and the docs say so.

- The pstats table's rows are keyed by file, line and function, where
  the line is the one executing when the sample was taken, so one
  function appears on several rows (`busy.py:5(hot)` and
  `busy.py:4(hot)`), while the summary sections aggregate by function.
  cProfile's rows are keyed by the function's definition line. Workshop
  1 explains this, since it is the first thing a cProfile user will
  ask about. To be checked again on 3.15.0 final.

- `--opcodes` is refused with the pstats output: "only compatible with
  --live, --gecko, --flamegraph, --diff_flamegraph, --heatmap,
  --binary". Workshop 12 uses the flame graph and the heatmap.

- `--mode=exception` on a parser that catches `ValueError` in a loop
  attributed nine tenths of its samples to the `return int(s)` line.

- With `-a`, wall mode showed a sleeping thread and `Thread.join` at a
  quarter of the samples each, CPU mode showed only the spinning
  threads, and GIL mode showed the spinning threads and one sample of
  the sleeper.

- `--async-aware` on an `asyncio.gather` crawler produced `<task>`
  frames named `Task-1`, `Task-2` and so on, with the coroutine's
  frames beneath them and none of the event loop's.

- `--subprocesses` on a `multiprocessing` pool wrote
  `profile_<pid>.pstats` for each child and the parent's table was
  almost entirely `selectors.py:_PollLikeSelector.select`, that is,
  waiting.

- The flame graph is one self-contained HTML file of about 600 KB with
  D3 inlined and no external fetches; the heatmap is a directory with
  `index.html` and one `file_NNNN.html` per source file; the gecko file
  defaults to `profile_<pid>.json`; the collapsed file to
  `collapsed_<pid>.txt`; the binary format is zstd compressed and
  `replay` prints a progress bar; `--jsonl` writes `meta`,
  `string_table`, `frame_table` and sample records.

- `--diff-flamegraph baseline.bin` writes an HTML file like the plain
  flame graph.

- Every output the docs describe was produced without error except
  `--live`, which needs a terminal and was not tried headless.

- On Python 3.15.0rc2: JupyterLab 4.6.4 and jupyterlab-workshop 0.13.0
  install and run; Flask 3.1.3, Starlette 1.7.0, uvicorn 0.54.0, httpx,
  requests, gunicorn, waitress, pytest's dependencies, numpy 2.5.3,
  sqlalchemy 2.1.1, matplotlib 3.11.2, pandas 3.0.6 and playwright
  1.63.0 all have wheels; pydantic-core has none, not even a
  pre-release, so pydantic and FastAPI do not install.

## Shape of the fundamentals collection

One ordered collection, in four movements, with no visible break
between them: the collection is numbered straight through and each
Finish dialog offers the next.

**What a sampling profiler is** (1 to 3). A first profile and how to
read the table; sampling against tracing; how the profiler reads a
process from outside and what follows from that. After these three the
learner can profile any script, read the result, and explain to a
colleague why it cost nothing.

**Reading the pictures** (4 to 6). The flame graph, the heatmap, and
the record-and-replay workflow with every output format. After these
the learner can turn a profile into the picture that answers their
question and keep the profile for later.

**Choosing what to measure** (7 to 10). Wall against CPU, threads and
the GIL, exceptions, and async code. This is where the profiler stops
being a hot-spot finder and starts answering questions about the shape
of a program.

**Looking closer** (11 to 14). Native frames and the garbage collector,
the bytecode, the differential flame graph, and live mode with the
statistics of how many samples are enough. The learner leaves knowing
everything the profiler can be asked, and how far to trust the answer.

Ten to twenty minutes each, about three and a half hours in total.
Each workshop is self-contained and ships whatever program it needs,
so it can be taken on its own, even though the order is the order to
take them in.

## Naming

Directory names are short kebab-case phrases naming the question, not
the mechanism, with no numeric prefix. The collection index carries the
order, and unnumbered names stay stable as workshops are inserted,
split or moved. Titles are sentence case and read as what the learner
will do.

Names are unique across every collection in this repository, because
all workshops share the one `workshops/` directory the extension
lists, and distinct from the names in the decorator, wrapt and
wrapture workshops, because a learner may have several of those
subscribed in one JupyterLab and the browser matches a local directory
to a collection by name. Taken by the wrapture workshops, which are
the closest neighbours (they trace Flask applications and find slow
code by tracing): `analysing-a-trace`, `finding-slow-code`,
`live-tracing`, `testing-web-requests`, `tracing-flask`,
`watching-a-service-over-time`, `zero-code-tracing`, and the rest of
that repository's names. Taken by the decorator workshops:
`your-first-decorator`, `caching-results`, and the rest. Taken by the
wrapt workshops: `your-first-wrapt-decorator`, `keeping-state`,
`synchronising-calls`, `wrapping-async-functions`, and the rest. The
titles here also avoid those repositories' titles, so "Where the time
goes", the wrapture title for `finding-slow-code`, is not reused.

## The fundamentals workshops

### 1. `your-first-profile`: Your first profile

Where does my program spend its time?

Start with the program, not the profiler. The learner has
`gazette/report.py` open beside the terminal: it loads a few thousand
articles from a shipped JSON file, counts words, finds the most common
ones, and prints a short report, and it takes a couple of seconds
longer than seems right. The welcome page says what a profiler is for,
and that there are two kinds: one that instruments the program and
counts every call, and one that watches from outside and looks at the
call stack many times a second. Tachyon is the second kind, and this
page says in three sentences what a sample is (the call stack at one
instant, every function that was on it), that the default is a thousand
a second, and that a function that is running most of the time will be
found on most of the samples. Then `python gazette/report.py` on its
own, so the learner has a time to compare against.

Then the command: `python -m profiling.sampling run gazette/report.py`.
Before it runs, a quiz: which of `load_articles`, `count_words`,
`most_common` or `render` do you expect to be hot? Then the table. The
page reads it column by column: "Captured 2,300 samples in 2.3 seconds"
is the sampling working; `nsamples` is direct over cumulative, and the
page says what each means with the row for `main` (zero direct, all
cumulative) as the example; `sample%` and `tottime` are the same fact
twice, since time is samples multiplied by the interval; `cumul%` and
`cumtime` are the time a function was anywhere on the stack. The hot
row is `count_words`, on the line that does `words.count(w)` inside a
loop, which is quadratic, and the page says so. Then the summary
sections: hot spots, indirect calls, call magnification, each in a
sentence.

Then the thing a cProfile user asks first: why does `count_words`
appear on two rows? Because each row is a file, a line and a function,
and the line is the one that was executing when the sample landed, so
a function with two busy lines has two rows. The summary sections
aggregate by function. The page says this was checked on 3.15.0rc2 and
points at the heatmap workshop as the place the per-line view comes
into its own.

Then `-l 5` and `--sort cumtime`, to show the table is sortable and
trimmable, and the ordinary shape of a call tree read from the bottom.
Then a second run, and the numbers are different: the page says why,
in one paragraph that the whole collection leans on (a sample is a
random glance; two sets of glances agree on the proportions and not on
the counts; more samples agree better), and says that checks in these
workshops look at which functions are where, never at counts.

The finish says what the learner can now do, names **Sampling or
tracing?** as next, and points at the pstats section of the module
docs.

- Format: terminal and files. Ships `gazette/report.py`,
  `gazette/__init__.py` and `data/articles.json`. Checks: a `shell`
  check that the run wrote nothing (the default prints to the
  terminal), then a `kernel` check on a second run with
  `-o profile.pstats`, loading it with `pstats.Stats` and asserting
  that `count_words` has more total time than `render`.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 2. `sampling-or-tracing`: Sampling or tracing?

When should I use this profiler and when the old one?

The same report generator, first under `python -m cProfile -s cumtime
gazette/report.py`, then under `python -m profiling.tracing`, which is
the same module under the name PEP 799 gave it, and the page says that
`cProfile` is now an alias and the old pure-Python `profile` module is
going away in 3.17. The tracing table has exact call counts, `ncalls`,
and the page dwells on that column for a moment: the deterministic
profiler knows `words.count` was called 48,000 times because it was
told about every one of them. Then the cost of being told: the run took
noticeably longer under the tracer, and the page has the learner time
both with `time` in front of the command. A quiz before the timing:
how much slower will the traced run be, a few percent, half again, or
several times? The honest answer on this program is measured and pasted
in; the page explains that the overhead depends on how many calls a
program makes, not how long it runs, so a program of many tiny calls
suffers most, and that the overhead also distorts, since the cheap
functions get proportionally more expensive.

Then Tachyon on the same program with `time` in front, and the run is
as fast as it was with no profiler at all, which is the point of the
collection. The page explains why in terms the learner already has: the
program never runs any profiler code; a second process reads its stack
from outside. The trade: no call counts, estimates not measurements,
and nothing at all from a program that runs for less time than a few
samples take. The page gives the docs' rule of thumb: the tracing
profiler for a short script, for exact counts, and for a unit test
that asserts a function was called once; `timeit` for differences of a
few percent; the sampling profiler for anything that runs for a while,
for production, and for anything where the overhead would change the
answer.

Closes by naming the three tools and the question each answers, and
sends the learner to **Reading a process from the outside** to see how
the second process manages it.

- Format: terminal and files. Ships the same `gazette` package. Checks:
  a `shell` check that a `-o tracing.prof` run under
  `profiling.tracing` produced a file `pstats` can load with an
  `ncalls` for `count_words`, and a `kernel` check on the sampling run's
  `.pstats` that the same function is the hottest.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 3. `reading-a-process-from-outside`: Reading a process from the outside

How can one process see the call stack of another, and what does that
cost me?

The mechanism, plainly. The profiler finds the target's interpreter
state in its memory and walks the frames the way the interpreter would,
reading the memory with `process_vm_readv` on Linux, `task_for_pid` on
macOS and `ReadProcessMemory` on Windows, and the target is never
paused and never runs a line of profiler code. That is why the version
rule exists: the profiler knows the layout of a 3.15 interpreter and
nothing else, so profiler and program must be the same minor version,
and while 3.15 is a release candidate the same release exactly. The
page shows the rule failing safely: `python3 -m profiling.sampling run`
with the host's other Python where there is one, or the message the
profiler gives, pasted in, where there is not.

Then `dump`, the one-shot form of the same read: start
`gazette/report.py` in the background from the terminal with `&`, and
run `python -m profiling.sampling dump $!` against it. Here the
platform matters, and the page says so before the command: on Linux a
process may read the memory of a process it started, and any other
process of its own user only where the kernel's Yama `ptrace_scope` is
0 or the profiler has `CAP_SYS_PTRACE`; the shell started the report,
not the profiler, so this is the second case. An `execute-capture`
before the command probes it (a `dump` of a throwaway child of the
shell, exit status captured into `can_attach`), and a `when` on the
result gives one of two pages: the dump's output, a traceback-style
stack with "main thread, has GIL, on CPU" in its header, read line by
line; or the same output shipped as a file and shown, with the
explanation of why this host refused, what `ptrace_scope` 1 means
(the Ubuntu default; parents only), and that `run` never hits this
because the profiler is the parent. The page says outright that these
workshops never change the kernel setting or use `sudo`, and that on
macOS even `run` needs root or a debugger entitlement, which is why
the workshops are Linux only.

Then what the read costs the profiler rather than the program: the
"Error rate" line. A stack read while the target is changing it can
be inconsistent, and the profiler throws such a sample away; the rate
is the share thrown away. `--blocking` pauses the target for each
sample and drives it to zero at the cost of slowing the target, and
the page runs both on a generator-heavy variant of the report to show
the rate move, with the docs' advice to use blocking only at long
intervals. `--realtime-stats` shows the achieved rate against the
asked-for rate, and the page explains "missed samples" as the
profiler falling behind, which is normal under load and does not
invalidate the profile.

Closes with the three rules the mechanism gives: same Python, parent or
permission, and estimates from whatever samples survived. Next is
**Reading a flame graph**.

- Format: terminal and files. Ships `gazette/report.py` and a
  `gazette/stream.py` variant that drives the report through
  generators, plus `dump-example.txt` for the branch where dump is
  refused. Checks: `shell` checks that the probe ran and set the
  variable, that the dump output (or the shipped example) was read,
  and that the `--blocking` run's `.pstats` exists.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 4. `reading-a-flame-graph`: Reading a flame graph

The table says which function is hot; how do I see the path that got
there?

A program whose table is ambiguous on purpose: `gazette/pages.py`
renders an index page and an archive page, and both call `format_date`
through different paths, so the table shows `format_date` with a high
cumulative time and cannot say which caller is responsible. The page
says this is what flame graphs are for, and gives their history in two
sentences (Brendan Gregg's `flamegraph.pl` over collapsed stacks, which
`--collapsed` still writes for it) before running
`python -m profiling.sampling run --flamegraph -o flamegraph.html
gazette/pages.py`.

The flame graph opens in the pane beside the terminal, with `url-open`
on its `/files/` URL, so the page can walk it: every box is a function
on the stack, its width is the share of samples it was on, the boxes
above it are what it called, and the root at the bottom is the whole
program. Read the widths for `render_index` against
`render_archive`, then find `format_date` twice, once above each, and
the answer to the question is which of the two boxes is wider. Then
the interactions, each as a short step: hover for the tooltip with the
source context, click a box to zoom into its subtree and the crumb
trail to come back, the search field with a function name and with
`pages.py:42`, and the sidebar: total samples, sampling efficiency, the
thread statistics (GIL held, released, waiting, GC), the hot spots
list. The theme toggle and the SVG export get a sentence.

Then `--collapsed`, the text form the flame graph is built from: one
line per unique stack, `main;render_index;format_date 312`, read
aloud, and the note that this is the format every flame graph tool
accepts, so a profile from Tachyon can go into speedscope or
`flamegraph.pl` unchanged.

Closes with what the flame graph adds to the table (the path) and what
it does not (the order in time, which the gecko format has, workshop
6). Next is **Down to the line**.

- Format: terminal and files, with a results pane. Ships
  `gazette/pages.py`, `gazette/__init__.py`, `data/articles.json` and
  `templates/`. Checks: a `shell` check that `flamegraph.html` exists
  and contains both `render_index` and `format_date`; a `shell` check
  that the collapsed file has a line beginning with the `main;` path
  to `format_date`; a `ui` check that a pane named `results` is open.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 5. `down-to-the-line`: Down to the line

I know which function; which line?

The report generator's `count_words` again, or rather a version in
which the function is long enough that "it is `count_words`" is not an
answer: it lowercases, strips punctuation, splits, filters stop words
and counts, in twenty lines, and one of those lines is the problem.
The page recalls that the table already keys rows by line, and that
this is the view where that pays off, then runs
`python -m profiling.sampling run --heatmap -o heatmap
gazette/report.py` and opens `heatmap/index.html` in the pane.

The index page first: files grouped as project, standard library and
site-packages with aggregate counts, and the page says why the
standard library is there (the profiler saw `json` and `collections`
on the stack too) and why the learner's file is at the top. Click
through to `report.py`: the source with each line coloured cool to
hot, the minimap on the right, and the one line burning. A quiz before
the click: which line? Then the two colouring modes, self time and
total time, and why the `for` line is hot in total and cool in self.
Then the callers and callees arrows on a line, to walk from the hot
line to who called the function. Then the cold-code filter to see only
lines that were ever sampled. The link icon on a line number gives a
URL that names the line, for pasting into an issue.

Then the fix, as a `file-write` of the corrected `count_words` using a
`Counter`, and a second heatmap into `heatmap-after`, and the same file
without the hot line, which is the payoff: the picture of the problem
and the picture of its absence, side by side in two tabs of the pane.

Closes by saying when to reach for the heatmap (you know the file) and
when for the flame graph (you know the symptom), and that workshop 13
shows how to compare two profiles properly. Next is **Record now, look
later**.

- Format: terminal and files, with a results pane. Ships the `gazette`
  package with the long `count_words`. Checks: `shell` checks that
  `heatmap/index.html` and a `file_*.html` naming `report.py` exist,
  and that after the fix `heatmap-after/` exists and the learner's
  `report.py` contains `Counter`.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 6. `record-now-look-later`: Record now, look later

Can I keep a profile and decide later how to look at it?

The situation: a run you cannot repeat, a colleague who wants the
profile, a CI job that should keep one. The binary format is the
answer, and the page runs `--binary -o report.bin` on the report
generator and reads the output: samples written, bytes before and
after zstd, and the size of the file, a few kilobytes for a couple of
thousand samples. Then `replay` four times from the one file: to the
table, to a flame graph, to a heatmap and to a gecko file, each
opened or read as the earlier workshops taught, and the page makes the
point that the profiler did the cheap part once and every picture came
afterwards, which is also why recording is faster than rendering while
sampling.

Then the two formats not yet met. The gecko file, `profile.json`, is
what the Firefox Profiler reads; the page opens the JSON in the editor
and finds the threads, the markers (GIL, CPU, GC) and the samples, and
says what the Firefox Profiler adds (a timeline, so the order of events
in time, which no flame graph has) and how to load it there later,
with the link but without opening the site, since the file never
leaves the machine either way. Then `--jsonl`, the format for programs:
`meta`, `string_table`, `frame_table` and sample records, one JSON
object a line, and a twelve-line Python script, shipped, that reads it
and prints the ten hottest frames, to show it is that simple.

Then the pstats file from workshop 1 as the fifth output: `pstats.Stats`
loads what `-o profile.pstats` wrote, `sort_stats('cumulative')` and
`print_stats(5)` work, and the page notes this is the interface every
existing pstats tool speaks.

Closes with a table of the eight outputs, what each is for and what it
cannot do. Next is **Waiting or working?**.

- Format: terminal and files, with a results pane. Ships the `gazette`
  package and `hottest.py`, the JSONL reader. Checks: `shell` checks
  that `report.bin` exists and that the replayed `flamegraph.html`,
  `heatmap/index.html` and `profile.json` exist, a `kernel` check that
  `profile.json` parses as JSON with a `threads` key, and a `shell`
  check that `hottest.py` prints `count_words` in its first three
  lines.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 7. `waiting-or-working`: Waiting or working?

My program is slow, but is it computing or waiting?

The first workshop of the movement about choosing what to measure, and
the one that introduces `--mode`. The program is `gazette/feeds.py`:
it fetches twenty feed pages from a local web server that the page
starts first in a second terminal (a shipped `http.server` handler that
answers slowly, standing in for a slow upstream), parses each, and
merges them. Wall-clock mode, the default, shows most of the time in
`fetch` under `urllib`, in `socket.recv`; the page explains that wall
mode counts every sample, whatever the thread was doing, so a thread
blocked on a socket is sampled sitting there, and that is what
end-to-end latency looks like.

A quiz: in CPU mode, what happens to `fetch`? Then `--mode=cpu`, and
`fetch` all but vanishes while `parse` and `merge` fill the table. The
page explains that CPU mode keeps only samples where the thread was
running on a processor, so waiting disappears, and then states the
rule the docs give: high in wall and low in CPU is I/O bound, and the
fix is concurrency (threads, async, a pool), not a faster algorithm;
high in both is CPU bound, and the fix is the algorithm. The learner
now has a diagnosis for the feed program, and the finish page of
workshop 10 acts on it.

Closes by listing the four modes and saying that GIL and exception
modes are the next two workshops. The server is stopped with
`interrupt` before the finish. Next is **Who holds the GIL?**.

- Format: two terminals and files, with a results pane. Ships
  `gazette/feeds.py` and `slow_server.py`. Variables: `server_port`,
  a number defaulting to 8071, described as the port to change if it
  is taken. Checks: a `shell` check that the server answers on the
  port, and `kernel` checks on `wall.pstats` and `cpu.pstats` that
  `fetch`'s share of samples is larger in wall than in cpu.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 8. `who-holds-the-gil`: Who holds the GIL?

I added threads and it got no faster; what are they doing?

`gazette/digest.py` builds digests of the articles on four threads,
each thread taking a quarter of the articles, and a fifth thread that
writes progress to a log every few milliseconds. The page runs the
profiler with defaults, and the table is almost empty: a few samples
in `Thread.join`. A quiz first: what will the default run show? The
answer is the lesson: the profiler samples the main thread only unless
told otherwise, and the main thread here is waiting for the workers.
Then `-a`, and the workers appear, and the flame graph with `-a` shows
the per-thread dropdown, which the page uses to look at one worker,
then all.

Then the GIL. The page explains it in a paragraph a learner who has
only heard of it can follow: one thread runs Python bytecode at a
time; a thread waiting for the GIL is not running; C code and I/O
release it. Then `--mode=gil`, which keeps only samples where the
thread held the GIL, and the sidebar's thread statistics in the flame
graph: GIL held, GIL released, waiting for the GIL. The four workers
show as taking turns, and the page says that this is why four threads
of pure-Python work took as long as one.

Then the counterexample, which is why this workshop is twenty minutes.
`gazette/checksums.py` hashes the article bodies with `hashlib.sha256`
on four threads; `hashlib` releases the GIL for large buffers, so in
CPU mode the four threads are all busy and in GIL mode they are nearly
absent. The page states the rule from the docs: low in GIL mode and
high in CPU mode means the work is in C with the GIL released, and
threads help; high in both means the work is Python and threads do not.
A sentence points at the free-threaded build as where this changes,
without going there.

Closes with the three questions (`-a` or not, which thread, who holds
the GIL) and what each mode showed. Next is **The price of an
exception**.

- Format: terminal and files, with a results pane. Ships
  `gazette/digest.py`, `gazette/checksums.py` and the data. Checks:
  `kernel` checks that the default run's `.pstats` has fewer than a
  tenth of the samples of the `-a` run's, that the `-a` GIL-mode
  `.pstats` for `digest.py` names `build_digest`, and that for
  `checksums.py` the CPU-mode file has several times the samples of
  the GIL-mode file.

- Requires: nothing beyond the standard library.

- Length: 20 minutes.

### 9. `the-price-of-an-exception`: The price of an exception

Exceptions are cheap in Python now, aren't they?

`gazette/dates.py` parses the dates in the article metadata, which
come in three formats, by trying each `strptime` in turn and catching
`ValueError`, which is idiomatic and fine when most dates are in the
first format, and here two thirds of them are in the third. The page
sets out what exception mode measures, exactly as the docs do: samples
taken while the thread has an active exception, which means while one
is propagating and while an `except` block runs, and not a `finally`
on the normal path. Then `--mode=exception`, and the table shows the
`strptime` calls inside the `try` and the `except` line as where the
program spends the time it spends in a raised state, and how many
samples that was against the wall-mode run before it: the share is the
price.

A quiz before the run: a tenth, a third or two thirds of the samples?
Then the fix, as a `file-write`: check the format with a cheap test
before calling `strptime`, or try the common format first, and the
exception-mode run again with a small fraction of the samples. The
page is careful to say what the docs say: this mode is for finding
exception-based control flow that has become hot, in parsers, in
`StopIteration`-driven iteration in older code, in "ask forgiveness"
lookups on a miss-heavy path, and not an argument against exceptions.

Closes with the mode's rule (it counts time under an exception, not
exceptions) and hands on to **Following the awaits**.

- Format: terminal and files. Ships `gazette/dates.py` and a data file
  with dates in three formats. Checks: `kernel` checks that the
  exception-mode `.pstats` names `parse_date` and has more than a
  quarter of the samples of the wall-mode file before the fix, and
  less than a tenth after.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 10. `following-the-awaits`: Following the awaits

My async program's profile is all event loop; where is my code?

The feed fetcher from workshop 7 rewritten with `asyncio` and a
gather of twenty fetches against the same slow local server,
`gazette/crawl.py`, and the profiler run on it with defaults. The
table and the flame graph are `_run_once`, `select`, `Handle._run`
and `Task.__step`, with `fetch` a thin slice, because the raw frames
of an asyncio program are the loop's, and a coroutine is only on the
stack while it runs between two awaits. The page explains that in a
paragraph before showing the fix.

Then `--async-aware`, and the page explains what the profiler does
differently: instead of the C stack of frames it walks the task graph,
so each sample is attributed to the task that was running and the
chain of awaits that led there, with a synthetic `<task>` frame naming
each task where a function frame would be. The flame graph now has
`Task-1` at the root with `main` above it, twenty `Task-N` boxes with
`fetch` above each, and the loop nowhere. The page names the default
`--async-mode=running`, which keeps only the task on the CPU, and runs
`--async-mode=all` to include the tasks parked on an await, so the
picture becomes what the program is waiting on, which for a crawler
is the whole story. Then the restrictions, listed as the docs list
them: no `--native`, no `--no-gc`, no `-a`, no cpu or gil mode with
async-aware profiling, and the requirement that `asyncio` be imported
in the target before sampling starts, which `run` satisfies.

Closes by returning to workshop 7's diagnosis: the async fetcher is
the concurrency fix, and the wall-mode run shows the twenty fetches
overlapping in a fraction of the time. The server is stopped before
the finish. Next is **Native code and the collector**.

- Format: two terminals and files, with a results pane. Ships
  `gazette/crawl.py` and `slow_server.py`. Variables: `server_port`,
  default 8072. Checks: a `shell` check that the server answers,
  `kernel` checks that the default run's `.pstats` names `_run_once`
  and the async-aware run's does not, and a `shell` check that the
  async-aware flame graph contains `<task>`.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 11. `native-code-and-the-collector`: Native code and the collector

Some of my time is in C and some is in the garbage collector; can the
profiler show either?

Two questions, one workshop, because the two special frames are
introduced together in the docs and are the same idea: a synthetic
frame the profiler inserts to mark something the Python stack cannot
show. First native code. `gazette/index.py` builds a search index:
`json.loads` on a large document, `re.finditer` over article bodies,
`sorted` with a key function, and a `zlib.compress` of the result.
With defaults, the time in each C function is attributed to the Python
line that called it, and the page says that is often what you want.
Then `--native`, and `<native>` frames appear above `json.loads` and
`zlib.compress` in the flame graph, so the learner can see how much of
`build_index`'s time was inside C rather than in the Python around it,
and the `sorted` key function shows as Python called from `<native>`
called from Python, which the page walks. The page is careful that
`<native>` is a marker, not a C stack: the profiler does not unwind C
frames.

Then the collector. `gazette/graph.py` builds a graph of article
cross-references with cycles, in bulk, and the profiler's default run
already shows `<GC>` frames, because GC frames are on by default; the
page explains what a `<GC>` frame means (a sample taken while the
cyclic collector was running, attributed to whatever line the
collector interrupted), why the collector runs (allocations of
container objects since the last collection), and how much of the
graph build it took. Then `--no-gc` to hide them and see the program's
own shape, and `gc.freeze()` at the top of the build as a `file-write`
to show the `<GC>` frames shrink, with the page saying plainly that
this is a demonstration of what the frames measure and not advice.

Closes with the two markers, when each is on by default, and what each
attributes to. Next is **Down to the bytecode**.

- Format: terminal and files, with a results pane. Ships
  `gazette/index.py`, `gazette/graph.py` and the data. Checks: `shell`
  checks that the `--native` flame graph contains `&lt;native&gt;` or
  `<native>` (whichever the HTML holds, to be verified) and the
  default `graph.py` flame graph contains `<GC>`, and a `kernel` check
  that the `--no-gc` `.pstats` names no `<GC>` frame.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 12. `down-to-the-bytecode`: Down to the bytecode

The interpreter specialises my code as it runs; can I see what it did?

Background first, since most readers will not know it: since 3.11 the
interpreter rewrites hot bytecode instructions into specialised
versions on the evidence of what it has seen, `LOAD_ATTR` becoming
`LOAD_ATTR_INSTANCE_VALUE` when the attribute has always been an
instance attribute, `BINARY_OP` becoming `BINARY_OP_ADD_INT`, and
falls back when the evidence changes. `--opcodes` records which
instruction was executing at each sample, and the page says up front
that it is only meaningful with the flame graph, the heatmap, gecko,
binary and live outputs, since the table has no room for it (the
profiler refuses the combination, with the message pasted in).

`gazette/scores.py` computes a relevance score for each article with
a small `Article` class, in two versions: one where every article is
an `Article`, and one where a tenth are `dict`s handled by the same
function, so the attribute access cannot specialise. `--opcodes
--flamegraph` on the first, hovering the hot box shows the bytecode
breakdown tooltip with specialised names; on the second, the same
function's tooltip shows the generic `LOAD_ATTR` and a lower
specialisation share. `--opcodes --heatmap` on the same line opens the
expandable bytecode panel under the hot line with each instruction's
share and its specialisation percentage, which is the clearest view.

The page keeps the lesson modest, as the docs do: this is for people
tuning a hot loop, and for understanding why two similar functions
differ; for most programs the algorithm matters and the bytecode does
not. Closes by naming the specialising interpreter's docs. Next is
**Did the fix work?**.

- Format: terminal and files, with a results pane. Ships
  `gazette/scores.py` and `gazette/scores_mixed.py`. Checks: `shell`
  checks that the two flame graphs exist and that the heatmap's file
  page for `scores.py` contains `LOAD_ATTR`.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 13. `did-the-fix-work`: Did the fix work?

I changed the code; how do I show it got faster, and where?

Workshops 5 and 9 each showed a before and an after by eye. This one
does it properly. Record a baseline of the report generator in the
binary format, `--binary -o baseline.bin`, then apply the `Counter`
fix to `count_words` as a `file-write`, then
`--diff-flamegraph baseline.bin -o diff.html` on the changed program,
and open it. The page reads the colours as the docs define them: red
for functions that took more direct time than in the baseline, blue
for less, darker for a bigger change, grey for unchanged, purple for
functions that are new. `count_words` is deep blue, `Counter.update`
and the C code behind it are purple, and everything else is grey. Then
the elided stacks toggle: call paths that disappeared entirely, which
here is the quadratic inner loop, shown on their own.

A second change makes a regression on purpose, an accidental `sorted`
inside the loop in `render`, and a second diff against the same
baseline shows `render` red while `count_words` stays blue, which is
the case the tool exists for: one change fixed one thing and broke
another, and the diff says both.

The page then gives the discipline in a paragraph: record a baseline
before changing anything, keep it, compare after every change, and
compare like with like (same data, same duration, same mode). Since
samples vary, the page shows two baselines diffed against each other,
mostly grey with faint colour, so the learner knows what noise looks
like before trusting a signal.

Closes with the record, change, compare loop. Next is **Watching it
live**.

- Format: terminal and files, with a results pane. Ships the `gazette`
  package with the slow `count_words`, plus `count_words_fixed.py` and
  `render_regressed.py` as the two `file-write` bodies. Checks: `shell`
  checks that `baseline.bin`, `diff.html` and `diff2.html` exist and
  that the learner's `report.py` has the fix.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 14. `watching-it-live`: Watching it live

Can I watch where a program is spending its time while it runs?

`--live` is `top` for one Python process, and the page starts it on a
long-running variant of the report generator that loops over the
articles for thirty seconds: `python -m profiling.sampling run --live
gazette/loop.py` in the terminal. The interface fills the terminal:
the header with the three hottest functions, the sampling efficiency
and the thread status line, and the table below with the sort column
marked. The page walks the keys with `send-key` actions: `s` to cycle
the sort, `/` to filter to `count`, `c` to clear, `t` to toggle the
per-thread view, `p` to pause the display while sampling continues,
`x` for the trend arrows, `h` for help, and `q` to leave, with the
final frozen display still navigable. The page notes that live mode
takes no output format and needs a terminal of at least sixty
columns, and that on Windows there is no live mode.

Then the second subject, which fits here because live mode makes it
visible: how many samples are enough. `-r` sets the rate, `-d` the
duration, and the page gives the docs' arithmetic: ten seconds at ten
kilohertz is a hundred thousand samples, and a function at five
percent of them is known to within half a percent; a thousand samples
and the same function could be anywhere from three to seven. Then
`--realtime-stats` alongside a high rate to watch the achieved rate
fall short of the asked-for rate on a busy machine, and the page says
what to do about it (a longer duration, not a higher rate). A quiz on
the arithmetic before the numbers are shown.

Closes the collection: the profiler's every mode and output has been
seen, the learner knows what a sample is, what the pictures mean and
how far to trust them, and **Tachyon on real applications** is where
to go next, starting with **A Flask application under load**. The
finish names the module docs as the reference.

- Format: terminal and files. Ships `gazette/loop.py` and the data.
  Checks: a `ui` or `shell` check that the live session ran (the
  terminal's scrollback holds the header text, or the process exited
  on `q`), and a `kernel` check on a `-r 5khz -d 5 -o rate.pstats` run
  that its sample count is within a plausible band of 25,000.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

## Topics the fundamentals collection leaves out

The Python API. `profiling.sampling.sample.sample(pid, collector,
...)`, `SampleProfiler` and `dump_stack` exist, are importable, and
make it possible to drive the profiler from a notebook against a child
process with a collector of one's own. None of it is in the module's
documentation, so it is not taught. If 3.15.1 or 3.16 documents it, a
notebook workshop that profiles a subprocess from a cell and plots the
collector's output belongs here, after workshop 6.

`--subprocesses` is left to the applications collection, where a worker
pool gives it a reason. `attach` is left to that collection too, since
it needs a program that is already running and a permission that most
hosts refuse. The free-threaded build is a sentence in workshop 8 and
no more, since the workshops run one interpreter build. Profiling a
module with `run -m` is a sentence in workshop 1 and the whole of
applications workshop 5. The gecko format's timeline view is described
and not driven, because the Firefox Profiler is a web site the
workshop would have to open in a new tab. Memory profiling is not what
Tachyon does.

## Shape of the applications collection

One ordered collection of seven workshops, each a kind of program:
a WSGI application, that application's slow endpoint, an ASGI service,
worker processes, a test suite, a process already running, and a
profile from a service somewhere else. The first two are a pair, the
diagnosis and the fix, and are written together. Fifteen to twenty
minutes each, about two hours in total. Each is self-contained: the
Flask application is shipped with each of the workshops that use it,
and each restates in a sentence what a sample and a flame graph are.

Every workshop here runs the program in one terminal and drives it
from a second, with the profiler wrapped around the program in the
first (`run -d <seconds>`, so the profile is written when the duration
ends without anyone stopping the server) and the flame graph or
heatmap opening in a pane. The load comes from a shipped `load.py`
that sends a few hundred requests with `urllib` on a handful of
threads, so the pages do not depend on `curl` for load, though `curl`
is used for single requests where the response is the point.

## The applications workshops

### 1. `a-flask-application-under-load`: A Flask application under load

What does a profile of a web application look like, and what should I
expect to see in it?

The `gazette` newsroom behind Flask, `gazette/web.py`: an index page,
an article page, a search endpoint over the word index, and a health
check, with a sqlite database built from the articles on first start.
The welcome page says what is different about profiling a server (it
never finishes, so a duration is needed; it does nothing until asked,
so load is needed; and the interesting time is per request, not
total), and starts it under the profiler in the first terminal with
`python -m profiling.sampling run -a -d 20 --flamegraph -o
flamegraph.html -m flask --app gazette.web run --port {{ server_port }}`,
explaining `-m` for a module and `-a` because the development server
handles each request on a thread, which a quiz asks the learner to
predict the consequence of.

Then `load.py` from the second terminal for fifteen seconds, then a
wait for the profiler to write, then the flame graph in the pane. The
page reads a server's flame graph for a reader who has only seen a
script's: the main thread is the accept loop, mostly waiting; the
worker threads each show the same shape, Werkzeug's handler, Flask's
dispatch, the view; the search view is wider than the others. The
per-thread dropdown lets the learner look at one request thread. Then
the same with `--mode=cpu`, and the accept loop vanishes, and the page
says which view to use for "what is the server doing" (wall) and
"where is the CPU going" (cpu).

Closes by naming what a request costs in the picture and hands to
**The slow endpoint**, which is the same application with a question.
Both servers are stopped, or have exited on their duration, before the
finish.

- Format: two terminals and files, with a results pane. Ships the
  `gazette` package with `web.py`, `templates/`, `load.py` and the
  data. Variables: `server_port`, default 8081. Checks: `shell` checks
  that the server answers `/health` on the port during the run, that
  `flamegraph.html` exists and contains `search` and `werkzeug`, and
  that the cpu-mode file exists.

- Requires: `flask` pinned to the release checked (3.1.3 on
  2026-09-29).

- Length: 20 minutes.

### 2. `the-slow-endpoint`: The slow endpoint

One endpoint is slow; how do I find the line and prove the fix?

The same application, and the search endpoint is the slow one because
`search` looks up each matching article with its own `SELECT`, the
classic query in a loop. The workshop is the fundamentals collection's
tools applied in order: the flame graph from a `-d 20` run under load
to see `search` wide and `sqlite3.Cursor.execute` under it many times;
the heatmap of `web.py` to find the `for` loop with the `execute` in
it; the fix as a `file-write`, one query with an `IN` clause; a second
run under the same load, and a differential flame graph against the
first run's binary capture with `search` in blue and the `execute`
path elided. The page is explicit about comparing like with like: same
`load.py`, same duration, same mode, and a baseline recorded in the
binary format so the diff has something to diff against.

The page also shows the profile's limits honestly: the time the query
took inside sqlite's C code is a `<native>` marker at best, and the
database's own view of the query (its plan) is not the profiler's
business; the profiler says where in the Python the time went, which
was enough here.

Closes with the loop the fundamentals collection ended on, record,
change, compare, now on a service. Next is **An async service that
stalls**.

- Format: two terminals and files, with a results pane. Ships the
  `gazette` package with the slow `search`, `search_fixed.py` as the
  `file-write` body, `load.py` and the data. Variables: `server_port`,
  default 8082. Checks: `shell` checks that `baseline.bin`,
  `heatmap/index.html` and `diff.html` exist and that the learner's
  `web.py` contains the `IN` query; a `kernel` check on the two
  `.pstats` files that `search`'s cumulative share fell.

- Requires: `flask`.

- Length: 20 minutes.

### 3. `an-async-service-that-stalls`: An async service that stalls

My async service is slow under load and the CPU is idle; what is
blocking the loop?

The newsroom as an ASGI service, `gazette/asgi.py`, on Starlette under
uvicorn, with the search endpoint awaiting a slow upstream (the local
slow server again, through `httpx`) and one endpoint, the article
page, that renders with a synchronous call that takes a few
milliseconds of CPU, the mistake every async service makes once. Under
load the whole service stalls while that call runs, and the page has
the learner see it before explaining it: `load.py` against the search
endpoint alone reports one latency; against both endpoints together
the search latency jumps, though search did nothing different.

Then the profiler with `--async-aware -d 20 --flamegraph` around
`uvicorn` (`run -m uvicorn gazette.asgi:app --port {{ server_port }}`),
and the flame graph shows tasks: the search tasks are nearly all
waiting (`--async-mode=all` to see them parked), and the article
tasks hold the loop in `render_article`. The page explains the event
loop's rule (one task runs at a time and runs until it awaits), why a
blocking call in one task delays every other, and the two fixes (make
the call await something, or hand it to a thread with
`asyncio.to_thread`), and applies the second as a `file-write`, then
profiles again to show the article tasks' frames now under a worker
thread and the search latency back where it was. FastAPI is named as
the framework most readers would have used here, with the reason it is
not (no pydantic-core wheels for 3.15 yet) and the note that the
profile of a FastAPI service looks the same, since it is Starlette
underneath.

Closes with the rule for reading an async service's profile: look at
what is running, not at what is waiting, and reach for
`--async-mode=all` when the question is what everyone is waiting for.
Next is **Workers and subprocesses**.

- Format: two terminals and files, with a results pane. Ships
  `gazette/asgi.py`, `slow_server.py`, `load.py`, `templates/` and the
  data, plus `render_fixed.py`. Variables: `server_port`, default 8083,
  and `upstream_port`, default 8084. Checks: `shell` checks that both
  servers answer, that the async-aware flame graph contains `<task>`
  and `render_article`, and that the learner's `asgi.py` contains
  `to_thread`.

- Requires: `starlette`, `uvicorn`, `httpx`, pinned to the releases
  checked.

- Length: 20 minutes.

### 4. `workers-and-subprocesses`: Workers and subprocesses

My program does its work in child processes; how do I profile those?

Two shapes of the same problem. First a job runner:
`gazette/jobs.py` builds the digests of workshop 8 on a
`ProcessPoolExecutor` of four workers. The profiler with defaults sees
the parent, and the parent's table is nearly all
`selectors.select`, waiting on its children, which a quiz predicts.
Then `--subprocesses`, and the page explains what the profiler does:
it notices each Python child as it appears, starts a profiler for it
with the same options, and writes one output per process,
`profile_<pid>.pstats` or `flamegraph_<pid>.html`, up to a hundred at
once, recursively through grandchildren. The learner opens one worker's
flame graph and sees `build_digest`, and the page says how to tell the
processes apart (the pid in the file name, and the command line each
shows in its root frame).

Then gunicorn: the Flask newsroom under `gunicorn -w 3` for a fixed
duration, with `--subprocesses`, under load, and four flame graphs,
the arbiter mostly sleeping and three workers each serving a share of
the requests. The page uses this to say what a production WSGI server
looks like to the profiler compared with the development server of
workshop 1 (processes rather than threads, and so no GIL between
workers), and that `--live` is not available with `--subprocesses`
because one terminal cannot show several profilers.

Closes with when to reach for `--subprocesses` (pools, `multiprocessing`,
pre-fork servers, anything that shells out to Python) and what it does
not do (follow a process it did not start; that is workshop 6). Next
is **Profiling a test suite**.

- Format: two terminals and files, with a results pane. Ships
  `gazette/jobs.py`, `gazette/web.py` and its templates, `load.py` and
  the data. Variables: `server_port`, default 8085. Checks: `shell`
  checks that at least three `flamegraph_*.html` files exist after
  each run and that one of the job runner's contains `build_digest`.

- Requires: `flask`, `gunicorn`.

- Length: 15 minutes.

### 5. `profiling-a-test-suite`: Profiling a test suite

My tests take four minutes; where does the time go?

A test suite for the newsroom, `tests/`, with pytest, and a few of the
tests slow for the usual reasons: one rebuilds the sqlite database in
a function-scoped fixture that should be session-scoped, one sleeps
waiting for a thread it could join, one parses the whole article file
for each of forty parametrised cases. `python -m profiling.sampling run
-m pytest tests -q` with `--flamegraph`, and the flame graph is pytest's
machinery with the tests above it; the page shows the search box with
`test_` to find them, and the three slow ones wide. The heatmap of
`conftest.py` finds the fixture. The fixes are three `file-write`s,
and the suite runs again under the profiler in a fraction of the time.

The page uses `-m` to make the general point: anything you run as
`python -m something` can be run as `python -m profiling.sampling run
-m something`, with its arguments after it, which covers test runners,
management commands, linters and build tools. It also says why the
tracing profiler is the wrong tool here (a test suite is many small
calls, so the tracer's overhead is at its worst and changes what is
slow).

Closes with the habit: profile the suite once a release and keep the
binary. Next is **Attaching to a running process**.

- Format: terminal and files, with a results pane. Ships the `gazette`
  package, `tests/` and `conftest.py`, and the three fixed files.
  Checks: `shell` checks that the flame graph contains `test_` and
  `conftest`, that the fixed `conftest.py` says `scope="session"`, and
  a `kernel` check that the second run's `.pstats` has under half the
  samples of the first.

- Requires: `pytest`, `flask`.

- Length: 15 minutes.

### 6. `attaching-to-a-running-process`: Attaching to a running process

The service is already running; can I profile it without restarting
it?

The headline feature of the profiler, and the one most hosts refuse to
an ordinary user, so this workshop is honest about both. The welcome
page explains why attach is the feature production people want (no
restart, no code change, no deploy, a profile of the process that is
misbehaving right now) and then the permission model, fully: on Linux
the kernel's Yama `ptrace_scope` decides, and at its common setting of
1 a process may read only its descendants, so `attach` to a service
started by systemd or a shell fails with a permission error, and the
ways round it (`ptrace_scope` 0, `CAP_SYS_PTRACE` on the profiler's
binary, or root) are each an administrator's decision the workshop
will not make; on macOS `task_for_pid` needs root or a debugger
entitlement; on Windows, `SeDebugPrivilege`. In a container the
container's kernel decides, and Docker Desktop's has no Yama at all,
so attach works there for the same user; on Binder and in a codespace
it depends on the node.

Then the probe: the Flask newsroom is started in the second terminal
without the profiler, and an `execute-capture` runs `dump` against a
throwaway child of the shell and stores whether it succeeded. Two
tracks follow. Where attach is allowed: `dump {{ pid }}` for a
snapshot of the running server's stacks with `--all-threads`, then
`attach --live {{ pid }}` for twenty seconds while `load.py` runs, then
`attach -d 15 --flamegraph -o attached.html {{ pid }}`, and the page
points out that the server was never restarted and never knew. Where
it is refused: the page shows the error the profiler gives, shipped as
a file, walks a shipped flame graph captured by attach elsewhere, and
shows the fallback that always works, which is to have started the
service under `run -d` in the first place, or to profile a child of
your own shell. The pid comes from the server's own output, captured
into a variable, so the learner never types one.

Closes with the decision the reader will face at work: ask the
administrator for `CAP_SYS_PTRACE` on a profiling host, or arrange to
start services under `run`. Next is **A profile from production**.

- Format: two terminals and files, with a results pane. Ships the
  `gazette` package with `web.py`, `load.py`, the data,
  `attach-refused.txt` and `attached-example.html`. Variables:
  `server_port`, default 8086; captures `can_attach` and `server_pid`.
  Checks: `shell` checks that the probe ran and set `can_attach`, that
  the server answered, and, on the allowed track, that `attached.html`
  exists and contains `search`; on the refused track, that the example
  was opened.

- Requires: `flask`.

- Length: 15 minutes.

### 7. `a-profile-from-production`: A profile from production

How do I get a profile from a machine I cannot look at, and compare it
with last week's?

The record and replay workflow of the fundamentals collection, on a
service, with the addition the user asked for: a notebook that turns
two profiles into a chart. The newsroom runs under `run -d 20 --binary
-o monday.bin` with `load.py`, then again after the search fix of
workshop 2 as `friday.bin`, standing in for two captures from a
production host, each a few tens of kilobytes. The page explains the
operational shape: the profiler captures in the binary format because
it is the cheapest to write and the smallest to copy, the file is
copied off the host, and every picture is made at the desk with
`replay`. A `replay --flamegraph` of each opens in the pane, and
`replay --jsonl` writes the two profiles as JSON lines.

Then the notebook, created by the page on the workshop's kernel: a
cell that loads both JSONL files, resolves the string and frame
tables, and totals samples per function; a cell that prints the ten
hottest functions of each as a table; and a cell that draws a
horizontal bar chart with matplotlib, the two captures side by side
per function, so the search endpoint's fall from Monday to Friday is a
bar that shrank. The page says what the chart adds to the differential
flame graph of workshop 2 (numbers, a shape you can put in a report,
and a script you can run in CI against every nightly capture) and what
it loses (the paths). A final cell loads the `.pstats` form of one
capture with `pstats.Stats` to show the standard library route to the
same numbers.

Closes the collection: the reader has profiled a WSGI application, an
ASGI service, worker processes and a test suite, knows what attach
needs, and has a profile pipeline from a host to a chart. The finish
names the module docs and the Firefox Profiler as the two places to go
next.

- Format: two terminals and files, then a notebook, with a results
  pane. Ships the `gazette` package, `search_fixed.py`, `load.py` and
  the data. Variables: `server_port`, default 8087. Checks: `shell`
  checks that `monday.bin`, `friday.bin` and both JSONL files exist;
  `learner-kernel` checks that the notebook's totals name `search` in
  both captures with the Friday count lower, and that a figure was
  drawn (a name the cell assigns).

- Requires: `flask`, `matplotlib`.

- Length: 20 minutes.

## Topics the applications collection leaves out

FastAPI, until pydantic-core publishes wheels for Python 3.15; workshop
3 uses Starlette and says why, and swapping the service to FastAPI when
the wheels exist is a change to that workshop's requirements and
imports alone. Django, because a Django project is more files than a
workshop can ask a learner to read, and its profile looks like Flask's
with more frames. Celery and other task queues, because a broker is a
service the workshop would have to run. Profiling under JupyterLab's
own kernel (a notebook cell that profiles itself) is not possible with
this profiler, since the kernel would have to be attached to and the
kernel is not a child of anything the learner runs; the notebook in
workshop 7 analyses profiles rather than making them. Continuous
profiling in production, sampling for minutes at low rates from a
sidecar, is described in workshop 7's finish and not built.

## Later collections

A third collection is not designed. Candidates, for when the first two
have shipped and the analytics say whether people reach the end:

- **Reading profiles of the standard library**: the profiler pointed
  at `json`, `re`, `pickle`, `sqlite3` and `asyncio` themselves, one
  workshop each, as a way of learning how they work.

- **The Python API**, if it is documented in a later release: driving
  the profiler from a notebook with collectors of one's own.

- **Profiling in CI**: a GitHub Actions workflow that captures a binary
  profile of a test suite on every push and diffs it against the
  default branch's.

## Decisions that cut across the workshops

**Python 3.15, and the release candidate until 3.15.0 ships.** The
profiler is part of 3.15 and of nothing earlier, so the project
requires 3.15 (`requires-python = ">=3.15"`, `.python-version` 3.15),
JupyterLab runs on it, and every workshop's environment is built from
it. On 2026-09-29 the newest release is 3.15.0rc2, and the profiler
requires that profiler and target be the same release exactly while
either is a pre-release, which they always are here because both are
the environment's interpreter. JupyterLab 4.6.4 and jupyterlab-workshop
0.13.0 were checked to install and run on it. When 3.15.0 is published,
uv, conda-forge and the `python:3.15` image move to it, and every page
whose output was pasted from rc2 is checked again.

**Linux only.** The profiler reads another process's memory, which
macOS refuses without root, a debugger entitlement or SIP off, and
Windows without administrator rights. The user does not run the
profiler on their own Mac, and no workshop asks a learner to escalate,
so every manifest declares `platforms: [linux]`, the hosted images are
Linux, and a `container/Dockerfile` gives a Mac a Linux JupyterLab to
run and test the workshops in with the checkout mounted. Within Linux,
`run` works for any user because the profiler is the parent of the
program; `attach` and `dump` against a process the profiler did not
start work only where `ptrace_scope` is 0 or the kernel has no Yama
(Docker Desktop), so the two workshops that use them probe first and
branch, and never change the setting.

**No subject submodule.** The subject is the standard library, whose
docs are online and whose source is in the installed interpreter.
AGENTS.md says where.

**An environment per workshop, even when it installs nothing.** The
extension builds a workshop's environment from the server's Python and
puts it first on the PATH of every terminal and behind every kernel the
workshop uses. That is what guarantees `python` in a page is 3.15 on
every host, so every workshop declares one, with a `requirements.txt`
that is empty for the standard library workshops and pins Flask,
Starlette, uvicorn, httpx, gunicorn, pytest or matplotlib for the
others. Nothing the workshops profile is in `pyproject.toml` or the
Binder requirements.

**Terminal and files is the format, with a pane for the pictures.**
The profiler is a command line tool and its output is text in a
terminal or HTML in a file, so a workshop is a shipped program open in
the editor, one or two terminals below it, and a named area beside
them that `url-open` fills with the flame graph or heatmap at its
`/files/` URL, so the page, the command and the picture are on screen
together, which is what the user asked for in place of a separate
browser tab. Two workshops end in a notebook (fundamentals 6 in
spirit, applications 7 in fact), created by the page on the workshop's
kernel, for the analysis that a notebook does better than a terminal:
loading the JSONL and drawing a chart. No workshop is notebook-only,
because the profiler cannot be driven from a cell in a documented way
and cannot profile the kernel it runs in.

**Servers are started under the profiler with a duration.** A server
never finishes, and a learner should not have to stop one at the right
moment, so every server is started as `run -d <seconds> ...` and
writes its profile when the duration ends; a second terminal drives it
with a shipped `load.py` (a few hundred requests on a few threads with
`urllib`) and `curl` for single requests. Every server is stopped with
`interrupt`, or has exited on its duration, before the page that
started it ends, and listens on `127.0.0.1` on a port held in a
`number` variable with a default, so it can be moved if taken.

**A recurring cast: the gazette.** Every program the workshops profile
is a piece of a small newsroom: `gazette/report.py` (a word-count
report over a few thousand articles), `pages.py` (rendering index and
archive pages), `feeds.py` and `crawl.py` (fetching feeds from a slow
local server, synchronously and with asyncio), `digest.py` and
`checksums.py` (threads), `dates.py` (parsing dates), `index.py` and
`graph.py` (a search index and a cross-reference graph), `scores.py`
(relevance scoring), `loop.py` (a long-running variant), `web.py` (the
Flask application), `asgi.py` (the Starlette service), `jobs.py` (a
process pool), and `tests/`. The data is one shipped `articles.json` of
a few thousand generated articles, the same file in every workshop
that needs it, so the numbers are comparable across workshops. Each
workshop ships only the modules it uses. The slow parts are mistakes
people make (a quadratic count, a query in a loop, a blocking call in
a coroutine, a function-scoped fixture, exceptions on the common path),
never a sleep labelled slow, and waits are real waits on a local
server.

**Background before the flag.** Every workshop opens with the question
and the situation, explains what the profiler will measure and why
that answers the question, and only then gives the command. A flag is
never shown without a sentence on what it changes about what is
measured. The reader of these workshops is assumed to have never
profiled anything, and to want to understand the tool, not only use
it.

**Numbers are proportions, and checks never count.** Sampling output
varies between runs, so pages describe rankings and shares (about
three quarters, the widest box, nearly absent) with the run pasted in
as an example and labelled as one, and the first workshop says why.
Checks load the `.pstats` file the run wrote with `pstats.Stats`, or
read the collapsed, JSONL or HTML file, and assert which functions
appear and how they rank, with margins wide enough that a slow CI
runner passes; a check never re-runs the profiler, and never asserts an
exact count. Time-based assertions (the traced run is slower) compare
two measurements made on the same machine in the same page.

**Prediction before execution.** Where the result is surprising, which
in this subject is often (the default thread view is empty, the wall
and CPU views disagree, the async view is all event loop, the
deterministic profiler is that much slower), a `quiz` asks before the
command runs. The self-test answers quizzes correctly.

**Learners never type code or commands.** Every command is an `execute`
action, every file change a `file-write`, every notebook cell a
`cell-insert`, so the attention goes on reading and predicting.

**Self-test.** A workshop is done when `just lint` is clean and the
self-test is green on Linux: `just test <name>` on a Linux machine or
in CI, `just container-test <name>` on the Mac. The self-test builds
the workshop's environment as a learner's session would, so it also
proves the requirements install on 3.15.

## Collections and the repository

**Two collections, one repository, one catalog.** The fundamentals and
applications collections are different courses with different
starting points, so each is a collection of its own, numbered from
one, with its own id, description and Finish sequence, and each can be
subscribed to or linked alone. They share the tooling, the reference
submodule, the images and CI, which is the reason for one repository.
A `catalog.json` at the root names both by relative path, so one URL
offers them all.

**Layout.** Every workshop of every collection sits directly under
`workshops/`, because the extension lists only the directories
directly under its one workshops directory; which collection a
workshop belongs to is recorded in the indexes alone. Each index lives
in `collections/<name>/collection.json`.

**Order.** The order of a collection is the list of workshop names in
the Justfile, which the `index-<collection>` recipe passes to
`jupyter workshop index` one by one. A name whose directory does not
exist yet is skipped, so the index can be refreshed while a collection
is being written.

**Ids.** `grahamdumpleton.me/tachyon/fundamentals` and
`grahamdumpleton.me/tachyon/applications`: the product, then the
course, leaving room for more under the prefix. An id is the
collection's identity to the analytics service and must never change,
so both are settled here, before any workshop is written.

**Binder, Codespaces, the container and local runs.** The Binder and
Codespaces settings subscribe to each collection's index by relative
path and disable opening other directories, subscribing and author
mode, as the sibling repositories do. Binder gets Python 3.15 through
`binder/environment.yml` on conda-forge, because repo2docker's
`runtime.txt` stops at 3.14; the pip requirements are the locked set
`just requirements` exports beside it. Codespaces gets it through uv's
Python installer in `setup.sh`, on the plain Ubuntu dev container
image, because no `devcontainers/python:3.15` image exists yet; both
are to be replaced by the plain `python-3.15` and `python:3.15` forms
when those exist, and neither has been built yet (see Open questions).
The container image in `container/` is `python:3.15-rc-slim` with the
same requirements, the self-test browser and a non-root user, and the
checkout mounted; it is the way the workshops are run and tested on a
Mac, and `just container-lab` starts it. A local `just lab` works on
Linux and starts on macOS, where every profiler step then fails, and
the README says so.

The Binder session forces trust because it is anonymous and thrown
away; the codespace and the container do not, because they belong to
the learner. Both hosted images set `analytics.report` to `always` so
that, once each collection's index carries an analytics block naming
the sink and its token, progress is reported without asking; until
then the setting reports nothing. Issuing the token is the user's step
(see Open questions). Every welcome message says progress is reported
and what is never sent.

**CI.** `.github/workflows/test.yml` lints the catalog, every collection
index and every workshop, and self-tests every workshop, on each push,
on `ubuntu-latest`, which is the platform the learners get. The
runner's `ptrace_scope` is not relied on: the two workshops that attach
probe and branch, so the refused track is what CI exercises.

## Extension features the workshops use

The patterns settled from the extension's documentation in
`reference/jupyterlab-workshop/docs`, so each workshop does not
rediscover them.

**Environment first.** The welcome page opens with `environment-create`,
so the learner sees the environment being made and every terminal and
kernel of the session runs on the workshop's Python; the manifest
declares `install-packages`, `environment` with
`requirements: requirements.txt`, and `kernel: workshop-<name>`.

**Terminal pages.** A command is one `execute` action into a named
terminal with `:wait:` set (`prompt` for a command that finishes, a
number of seconds for a server), followed by a check. Servers run in
`terminal:server` and load in `terminal:client`; a single-terminal
workshop uses `terminal:shell`. `interrupt` stops a server. `:cwd:` and
paths resolve against `work/`. The manifest sets `PAGER: cat`,
`PYTHONUNBUFFERED: "1"` and `PYTHONDONTWRITEBYTECODE: "1"` in `env`,
declares `curl` under `requires.tools` where a page uses it, and holds
each port in a `number` variable.

**The results pane.** The layout names an area `results` beside the
terminals, empty at first, and `url-open` with `:pane: results` opens
the flame graph or heatmap there at its `/files/` URL, which Jupyter
serves with a `sandbox allow-scripts` policy, so the inlined D3 runs.
The built-in `workspace` variable is the learner's `work/` directory
relative to the JupyterLab root, so the URL is
`files/{{ workspace }}/flamegraph.html` whatever the root is; whether
it must be written relative or absolute to survive a base URL prefix
(Binder serves JupyterLab under `/user/<name>/`) is an open question.
A layout of a file on top and terminals below, with the results area
as a column beside them, is the one every terminal workshop declares.

**Probes and tracks.** Where a page's outcome depends on the host
(attach allowed or not), an `execute-capture` early on the page stores
the result in a variable, and `when` directives give the two tracks,
each ending in a check that reads the same variable, so lint sees a
page that always has something checkable.

**Checks read files.** The `shell` substrate for "the file exists and
contains this name", the `kernel` substrate for loading a `.pstats`
file with `pstats.Stats` or a JSONL file with `json` and asserting on
ranks, and `learner-kernel` for the notebook in applications 7. No
check runs the profiler.

**Notebook pages**, where used, keep the wrapt workshops' rules: created
by `notebook-create` on the workshop's kernel, one `cell-insert` per
step with a tag and `:run: true`, checked by `learner-kernel` reading a
name the cell assigned.

## Known blockers

None found in the extension yet; this section records them as the
first workshop is written. Outside the extension:

- pydantic-core has no wheels for Python 3.15 (checked 2026-09-29,
  release and pre-release), so FastAPI cannot be installed on Binder or
  in the container, and applications workshop 3 uses Starlette.

- No `mcr.microsoft.com/devcontainers/python:3.15` image and no
  repo2docker `runtime.txt` support for 3.15 (checked 2026-09-29), hence
  the `environment.yml` and uv arrangements above.

## Open questions

- **The `/files/` URL of a written flame graph.** The built-in
  `workspace` variable is the learner's `work/` directory relative to
  the JupyterLab root (`docs/platforms.md`), so the flame graph's URL
  is `files/{{ workspace }}/flamegraph.html`. Still to check in the
  first workshop: whether `url-open` resolves a relative URL against
  the page or the base URL, since Binder serves JupyterLab under
  `/user/<name>/` and an absolute `/files/...` would miss that prefix;
  whether the flame graph's theme toggle, which uses local storage,
  works inside the sandboxed iframe; and whether the heatmap's
  per-file links resolve inside it. The fallback is JupyterLab's own
  HTML viewer (`file:` in the layout or an `{open}` link, with a Trust
  HTML click). Settled by the first workshop written.

- **Binder and Codespaces builds.** Neither `binder/environment.yml`
  with `python=3.15` on conda-forge nor the uv-installed 3.15 in
  `.devcontainer/setup.sh` has been built. Both are to be tried once
  the repository is on GitHub, before the first workshop is announced.

- **Analytics.** No token has been issued. When the user issues one
  (`workshop-analytics token issue --name tachyon-workshops --label
  deployment=tachyon-workshops`), it goes in a `collection.yaml`
  beside each collection's index so `just index` copies the block in,
  as the wrapt workshops now do with one token for every collection
  and deployment.

- **Live mode in the self-test.** Workshop 14 drives a curses interface
  with `send-key`; whether the self-test's terminal is wide enough and
  the keys land reliably is to be found out when it is written. If
  not, the page keeps the key walk as prose over a shipped screenshot
  and the checks cover the rate and duration run.

- **The per-line rows of the pstats table.** Checked on rc2; to be
  checked again on 3.15.0 final before workshop 1's text is trusted.

## Status

The writing order is the fundamentals collection's order: the first
workshop settles the manifest, the environment step, the terminal
layout with the results pane, the `/files/` URL question and the
`pstats`-reading checks, and each later one adds one idea to a format
that already works. Workshops 3 and applications 6 share the probe and
tracks pattern and are written with it in mind; 5 and 13 share the
`count_words` fix; 7 and 10 share the slow server. Applications 1 and
2 are written together, since 2 is 1 with a question.

| # | Workshop | Status |
|---|----------|--------|
| 1 | `your-first-profile` | Planned |
| 2 | `sampling-or-tracing` | Planned |
| 3 | `reading-a-process-from-outside` | Planned |
| 4 | `reading-a-flame-graph` | Planned |
| 5 | `down-to-the-line` | Planned |
| 6 | `record-now-look-later` | Planned |
| 7 | `waiting-or-working` | Planned |
| 8 | `who-holds-the-gil` | Planned |
| 9 | `the-price-of-an-exception` | Planned |
| 10 | `following-the-awaits` | Planned |
| 11 | `native-code-and-the-collector` | Planned |
| 12 | `down-to-the-bytecode` | Planned |
| 13 | `did-the-fix-work` | Planned |
| 14 | `watching-it-live` | Planned |

| # | Workshop | Status |
|---|----------|--------|
| 1 | `a-flask-application-under-load` | Planned |
| 2 | `the-slow-endpoint` | Planned |
| 3 | `an-async-service-that-stalls` | Planned |
| 4 | `workers-and-subprocesses` | Planned |
| 5 | `profiling-a-test-suite` | Planned |
| 6 | `attaching-to-a-running-process` | Planned |
| 7 | `a-profile-from-production` | Planned |

Setting up the repository, on 2026-09-29, touched: the Justfile
(both collections' variables, lists and `index-<collection>` recipes,
and the `container-*` recipes), `pyproject.toml` and `uv.lock` on
Python 3.15, `binder/` (with `environment.yml` in place of
`runtime.txt`), `.devcontainer/` (the Ubuntu base image and uv),
`container/Dockerfile`, `.github/workflows/test.yml`,
`jupyter_lab_config.py`, both collection stubs, the catalog, the
welcome messages, the README, AGENTS.md and this file. Adding a third
collection touches the same places, plus the `finish` text of the last
workshop of the collection before it.

Planned means designed here and not yet written. Written means the
pages exist and lint is clean. Done means `just test <name>` is green
on Linux and the entry is in the index and the README.
