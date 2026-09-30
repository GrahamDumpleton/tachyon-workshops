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

- On Python 3.15.0rc2: JupyterLab 4.6.4 and jupyterlab-workshop 0.15.0
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
`gazette/report.py` open above the terminal: it loads two thousand
articles from a shipped JSON file, counts words, finds the most common
ones, and prints a short report, and it takes a second and a half,
longer than seems right. The welcome page says what a profiler is for,
and that there are two kinds: one that instruments the program and
counts every call, and one that watches from outside and looks at the
call stack many times a second. Tachyon is the second kind, and this
page says in a paragraph what a sample is (the call stack at one
instant, every function that was on it), that the default is a
thousand a second, and that a function that is running most of the
time will be found on most of the samples. Then `python
gazette/report.py` on its own, so the learner has a time to compare
against, and a quiz predicting which of `load_articles`,
`count_words`, `most_common` or `render` is hot.

Then the command: `python -m profiling.sampling run gazette/report.py`.
The page reads the header ("Captured 1582 samples in 1.58 seconds",
the rate, the error rate, which it names and hands to workshop 3) and
asks in a quiz which function is on the top row. Then the table column by column, with the rows for `count_words`
(`1261/1261`) and `main` on line 62 (`2/1577`) as the examples, and a
hint for the reader whose table has `main` on line 61 instead, or
both: `main` has a row per sampled line too, and the default sort by
direct samples can drop the line-62 row below the fifteen shown (a
first reader found exactly this). Each page runs the profiler at most
once, since three runs across two pages read as repetition: `nsamples` is direct over cumulative;
`sample%` and `tottime` are the same fact twice, since time is samples
multiplied by the interval, and the profiler never timed anything;
`cumul%` and `cumtime` are the time a function was anywhere on the
stack. Then the three summary lists (hot spots, indirect calls, call
magnification) in a sentence each, and `-o profile.pstats` to keep the
table in a file that `pstats` reads, which is how the checks work.

Then the thing a cProfile user asks first: why does `count_words`
appear on two rows? Because each row is a file, a line and a function,
and the line is the one that was executing when the sample landed, so
a function with two busy lines has two rows: line 36, the dictionary
comprehension calling `words.count(word)` (four fifths), and line 34,
`word not in unique` (a fifth), both quadratic. The summary sections
aggregate by function. The page points at workshop 5 as where the
per-line view comes into its own.

Then `--sort cumtime -l 6 --no-summary`, so the table reads from the
root down with `main` line 62 near the top, and the learner sees it is
sortable and trimmable; and, since this run's numbers differ from the
first's, the page says
why, in the paragraph the whole collection leans on (a sample is a
random glance; two sets of glances agree on the proportions and not
on the counts; more samples agree better), and says that checks in
these workshops look at which functions are where, never at counts.

The finish quiz asks where "1.261 seconds" came from. The finish text
names **Sampling or tracing?** as next and points at the pstats
section of the module docs.

- Format: terminal and files. Ships `gazette/report.py`,
  `gazette/__init__.py` and `data/articles.json`. Seven pages. The
  runs that print to the terminal are followed by quizzes; the runs
  with `-o` are checked with `kernel` checks that load the file with
  `pstats.Stats` and assert that `count_words` has most of the direct
  time and appears on more than one line; the sorted run and the
  variability lesson end in a quiz. Written and tested 2026-09-29: the report takes 1.6 seconds
  and the checks read 99% of the direct time in `count_words`.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 2. `sampling-or-tracing`: Sampling or tracing?

When should I use this profiler and when the old one?

Not the first workshop's report but a tidier one, because the first
workshop's report showed no tracer overhead at all when it was tried:
its time was inside a thousand calls to `list.count`, and a tracer
charges per call. So this workshop's `gazette/report.py` is the same
report written the way a tidy program would be, with a function per
word (`normalise`, `is_stop_word`, `stem`, `record`), phrase pairs,
and a reading-ease score that counts syllables one letter at a time:
four million small calls in a fifth of a second. The learner runs it
plain twice, predicts the slowdown in a quiz, then runs
`python -m cProfile -s tottime gazette/report.py`: the report's own
last line says 0.7 seconds against 0.2, and the header says 4.2
million calls. The page reads `ncalls` (`stem` 164,151, `normalise`
415,316, `str.endswith` 1.3 million), says these are counts and not
estimates, and notes the rows for C methods and the per-`def` keying.
Then `python -m profiling.tracing`, the same profiler under the name
PEP 799 gave it, with `cProfile` kept as an alias and `profile` going
in 3.17; its `--help` still says `Usage: cProfile.py`, which the page
shows. The page explains that the overhead depends on how many calls a
program makes, not how long it runs, and that it distorts, since the
cheap functions carry proportionally more of it.

Then Tachyon on the same program, and the report's last line is back
to a fifth of a second, which is the point of the collection. The
table has no `ncalls`, only two hundred samples, and an error rate
higher than the first workshop's (a few percent to a fifth, by
machine), which the page names and hands to workshop 3. A hint
says why the first workshop's report would not have shown the
overhead.

Then the docs' rule of thumb as a page: the tracer for a short
program, for exact counts, for a program whose cost is in a few long
calls, and for reproducibility; the sampler for anything that runs a
while, for production, for call-heavy programs where the tracer's toll
is highest and its distortion worst, and for a process you would
rather not restart; `timeit` for differences of a few percent. A quiz
on a slow web service closes it, and the finish quiz asks what only
the tracer can report (call counts).

- Format: terminal and files. Ships the tidy `gazette/report.py` and
  the data. Six pages. Checks: a `kernel` check on `tracing.pstats`
  that over a million calls were recorded and `stem` over 100,000
  times, and a `kernel` check on `sampling.pstats` that the samples
  cover under 0.6 seconds (no slowdown) and name the word functions.
  Written and tested 2026-09-29.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 3. `reading-a-process-from-outside`: Reading a process from the outside

How can one process see the call stack of another, and what does that
cost me?

The mechanism, plainly. The profiler finds the interpreter's runtime
structure in the target's memory and walks the frames the way the
interpreter would to print a traceback, reading the memory with
`process_vm_readv` on Linux, `task_for_pid` on macOS and
`ReadProcessMemory` on Windows; the target is never paused and never
runs a line of profiler code. That is why the overhead is nothing and
why the workshops are Linux only. From the mechanism follows the
version rule: the profiler knows the layout of a 3.15 interpreter and
nothing else, so profiler and program must be the same minor version,
and the same release exactly while either is a pre-release. The page
shows the rule failing safely by dumping a `sleep` process: "Failed
to find the PyRuntime section", since no other Python is on the
hosts. A quiz asks why the versions must match.

Then `dump`, the one-shot form of the same read, and the permission
model in full: Yama's `ptrace_scope`, 1 by default (descendants
only), 0 for any process of the user, `CAP_SYS_PTRACE` and root; why
`run` never hits it (the profiler is the parent). An
`execute-capture` probes the host by dumping a short-lived child of
the shell and stores `yes` or `no` in `can_attach`, and a `when` block
for each answer follows. On `yes` (Docker Desktop, or `ptrace_scope`
0) the learner starts the report in the background and dumps its
stack, and the page reads the header ("main thread, has GIL, on CPU;
most recent call last") and the frames down to line 36 of
`count_words`. On `no` the same output is shipped as
`dump-example.txt` and read, with the explanation of what refused it
and a pointer to applications workshop 6 for what an administrator
can do. The page says outright that these workshops never change the
setting or use `sudo`. A quiz asks who may read whom at the default
setting.

Then what the read costs the profiler rather than the program: the
error rate. `gazette/stream.py` counts pairs of adjacent words through
three generators, so frames are entered and left tens of thousands of
times a second, and its error rate is several times the report's
under 1%, by how much depending on the host (see Known blockers), so
the page has the learner compare the two lines and quotes no number. `--blocking` pauses the target for each sample and brings
it to a percent or two at the program's expense, with the docs' advice
to use it only at long intervals and only when the stacks change too
fast. Then `-r 5khz -d 1` and `--realtime-stats`: the rate asked for,
the rate achieved, and what missed samples mean.

Closes with the three rules the mechanism gives: same Python, parent
or permission, and estimates from whatever samples survived. The
finish quiz diagnoses a colleague's permission error. Next is
**Reading a flame graph**.

- Format: terminal and files. Ships `gazette/report.py`,
  `gazette/stream.py` and `dump-example.txt`, and the data. Six pages.
  The checks that gate the probe page are a `shell` check that
  `can_attach` is set and a quiz, so the page is checkable on either
  track; the later pages load `stream.pstats`,
  `stream-blocking.pstats` and `rate.pstats` with `pstats.Stats` and
  assert the generator functions are present and the `-d 1` profile
  covers about a second. Written and tested 2026-09-29, on the `yes`
  track in the container; the `no` track is what CI on
  `ubuntu-latest` will exercise.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 4. `reading-a-flame-graph`: Reading a flame graph

The table says which function is hot; how do I see the path that got
there?

A program whose table is ambiguous on purpose: `gazette/pages.py`
renders an index of the hundred latest articles, an archive page per
day (271 of them), a page per section and a page per author. Every
page is built from `summary`, which calls `format_date`;
`render_archive` also calls `format_date` for every article for every
day, to find the day's articles, which is half a million calls against
`summary`'s six thousand. The table shows `format_date` with three
quarters of the samples and cannot say which caller is responsible,
and a quiz asks the learner to predict. The page says the flame graph
is what has that column, gives its history in two sentences (Brendan
Gregg, 2011, drawn from stack samples), and runs
`--flamegraph -o flamegraph.html`.

The flame graph opens in JupyterLab's HTML viewer, beside `pages.py`
and above the terminal, through a `file-open` action with the HTML
Viewer factory and the `desk` area (see Known blockers for why not
`url-open`), and a hint says to click Trust HTML on a JupyterLab that
does not trust files by default. Then the page walks it, as Tachyon draws it, which is
root at the top with callees beneath (`.inverted(true)` in the
graph's script; the first draft described the classic bottom-up
layout from memory and a first reader caught it): every box is a
function on the stack, its width is the share of samples it was on,
and its colour is the same share on the heat scale shown in the
sidebar's Heat Map section, from three fifths or more down to under
one percent. Follow the hot colour down through `main` to
`render_archive`, find `format_date` directly beneath it, as two
boxes for its two lines, and again beneath the narrow `summary`, and
the answer to the question is which is wider, which is where the fix
goes: in the caller, not in `format_date`. Then the interactions as a
short list: hover for the tooltip (total and self time, percentage,
source), click to zoom and the house button to reset, search by
function name or `pages.py:19`, the sidebar on the left (View Mode
with module names or file paths and the inverted graph, Profile
Summary, Hotspots, Runtime Stats, Heat Map), and the export,
documentation and theme buttons. A
quiz asks which `format_date` box is wider and what that means.

Then `--collapsed -o stacks.txt`, the text the graph is drawn from:
one line per distinct stack, `tid:<n>;` then `file:function:line`
frames from the root outwards, a space and the count; `sort -k 2 -n
-r | head -n 3` shows the wide column as text, about half the samples
kept, through `render_archive` to
`format_date`. It is the format every flame graph tool accepts, and
the smallest useful record of a profile.

Closes with what the flame graph adds to the table (the path) and what
it does not (the order in time, which the gecko format has, workshop
6). The finish quiz asks when the graph says something the table does
not. Next is **Down to the line**.

- Format: terminal and files, with the flame graph in an HTML viewer
  tab. Ships `gazette/pages.py`, `gazette/__init__.py` and
  `data/articles.json`; no templates, the HTML is built with f-strings
  and `html.escape`. Six pages. Checks: `shell` checks that
  `flamegraph.html` exists and names `format_date` and
  `render_archive`, and that `stacks.txt` has a line with
  `render_archive` before `format_date`; quizzes on the caller and the
  wider box. Written and tested 2026-09-29; the graph was also opened
  in a real JupyterLab in the container with Playwright and drew its
  boxes in the trusted viewer. The program takes 1.6 seconds and its
  error rate can reach 40% or more, since `strptime` builds and tears
  down frames quickly, which the page names in a sentence without
  promising a figure.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 5. `down-to-the-line`: Down to the line

I know which function; which line?

`gazette/report.py` in a version whose `count_words` is twenty lines
long, so that "it is `count_words`" is not an answer: for every
article it joins title and body, lowercases, strips punctuation,
splits, skips stop words and numbers, and counts each word twice,
once for the paper with a `Counter` and once for the article's
section with a dictionary and a list, `seen`, that it searches to
learn whether an entry is new. The search, `if entry not in seen:` on
line 40, is nearly every sample of a run of about two seconds. A quiz
asks which line before anything is run, then
`run --heatmap -o heatmap gazette/report.py`.

The index first, opened in the HTML viewer: the cards for the run,
and the files grouped as Project Files and Standard Library, with
why `json` is there, and why the count against a file is about three
times the number of samples (it sums the file's lines, and a sample
counts towards every line of the file on its stack). Then the page
for `report.py`, opened by an action of its own as
`heatmap/file_0000.html`, since pages are numbered from the file with
the most samples: the Self and Total columns, the one red line and
the minimap, that the colour is relative to the hottest line of the
file, the Self Time and Total Time switch (line 77, the call in
`main`, is cold in self and hot in total), the Hot Only switch, and
the caller and callee arrows, which in the viewer can be read by
hovering and not followed.

Then the fix, as a `file-write` that copies `fixed/report.py` from
the workshop directory (a `Counter` for the sections, the list and
its three lines gone), a second heatmap into `heatmap-after`, and the
same page in a second tab: the colour spread along the loop, a red
line still there because some line is always the hottest, and its
number a dozen or two where line 40 had well over a thousand.

Closes by saying when to reach for the heatmap (you know the file)
and when for the flame graph (you know the symptom), and that
workshop 13 compares two profiles properly. Next is **Record now,
look later**.

- Format: terminal and files, with the heatmap pages in HTML viewer
  tabs; the lower area is 0.55 of the height since the heatmap is
  what is read. Ships `gazette/report.py`, `data/articles.json` and,
  outside `files/`, `fixed/report.py`. Six pages, `write-files` added
  to the capabilities. Checks: a `shell` check that the index exists
  and `file_0000.html` is the page for `report.py`; a `shell` check
  that the fix is in place; a `kernel` check that reads the `Self:`
  counts from both pages and asserts that one line had more than
  three fifths of the samples before and that the whole file has
  under half as many after. Written and tested 2026-09-29, with both
  heatmaps looked at in a real JupyterLab in the container.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 6. `record-now-look-later`: Record now, look later

Can I keep a profile and decide later how to look at it?

The situation: a run you cannot repeat, a colleague who wants the
profile, a CI job that should keep one. The page runs
`--binary -o report.bin` on the report of workshop 1 and reads what
the profiler says about the recording (a few dozen records for
sixteen hundred samples, since a repeated stack is written as a
repeat) and `ls -l` shows a file of under three kilobytes. Then
`replay` three times from the one file, to the table, a flame graph
and a heatmap, each opened in the viewer, with the point that nothing
ran but the profiler and that the three views agree sample for
sample. A quiz asks what the replays ran.

Then the formats for other tools. `--gecko`: `profile.json` opened in
JupyterLab's JSON viewer (`file-open` with the `JSON` factory),
where the learner finds the thread's `samples` with a time for each,
the `markers` for GIL, CPU, code type, exception and GC state, and
the shared string table; the Firefox Profiler is linked, not opened.
`--jsonl`: five lines on a profile this small, `meta`, `string_table`,
`frame_table`, `agg` and `end`; the format holds counts per frame,
self and cumulative, not samples or stacks, which the first design
had wrong. The shipped `hottest.py` reads it in seventeen lines and
prints the ten hottest frames. Then the pstats file, loaded with
`pstats.Stats` and printed with `print_stats(5)`, with what to
remember when an old tool reads it: the counts are samples, not
calls.

Closes with a list of the eight outputs, what each is for and what
it cannot do. The finish quiz is the production job that cannot be
repeated. Next is **Waiting or working?**.

- Format: terminal and files, with viewer tabs. Ships the `gazette`
  package with workshop 1's `report.py`, `data/articles.json` and
  `hottest.py`. Seven pages. Checks: `shell` checks that `report.bin`
  exists, that the replayed `flamegraph.html` and `heatmap/index.html`
  exist, and that `hottest.py` prints `count_words` in its first
  three lines; `kernel` checks that `profile.json` parses with a
  thread of samples and that `profile.pstats` loads with
  `count_words` dominant. Written and tested 2026-09-29.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 7. `waiting-or-working`: Waiting or working?

My program is slow, but is it computing or waiting?

The first workshop of the movement about choosing what to measure,
and the one that introduces `--mode`. `gazette/feeds.py` fetches
twenty pages of RSS from a local server, parses each (ElementTree, a
date and five keywords per item) and merges them, dropping an item
that tells a story already in the list, which `same_story` decides by
comparing keyword sets, item against every item kept. The server is
the shipped `slow_server.py`, a `ThreadingHTTPServer` on `127.0.0.1`
that sleeps a twentieth of a second before each answer; the page says
the sleep is a stand-in for a distant server and that the program
fetching cannot tell the difference. It is started in a terminal of
its own, to the right of the one the profiler runs in, and stopped
with `interrupt` on the finish page.

Wall-clock mode, run with `--mode wall` spelt out: two thirds of the
samples in `socket.py`, `SocketIO.readinto`, where `fetch` ends up,
and a quarter in `same_story`. A quiz asks what CPU mode does to the
first row. `--mode cpu`: the read from the socket is gone, the table
holds a third as many samples, `same_story` has three quarters of
them, and the page says that a percentage is always a share of what
the mode kept. Then the rule the docs give: high in wall and absent
in CPU is waiting, and the fix is concurrency or asking less; high
in both is work, and the fix is the algorithm. The feed reader has
one of each, the wall-clock table says which to fix first, and
workshop 10 acts on it.

Closes by listing the four modes. Next is **Who holds the GIL?**.

- Format: two terminals side by side below the files, no pictures.
  Ships `gazette/feeds.py`, `slow_server.py` and `data/articles.json`.
  Variables: `server_port`, a number defaulting to 8071. Six pages.
  Each profiler command ends in `| tee wall.txt` or `| tee cpu.txt`,
  so one run gives the learner the table and the check a file; the
  `kernel` checks strip the colour codes, read the rows, and assert
  that the socket read has more than a third of the samples in wall
  and under a third of that share in CPU, and that `same_story`'s
  share rose. `shell` checks, in Python with `urllib`, that the
  server answers and later that it has stopped. Written and tested
  2026-09-29.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 8. `who-holds-the-gil`: Who holds the GIL?

I added threads and it got no faster; what are they doing?

`gazette/digest.py` builds a digest of every article for each of the
gazette's twelve regional editions, twenty four thousand in all, on
four threads, with a fifth writing progress to a log every five
milliseconds. It takes the number of threads as an argument, and the
welcome page runs it with one and with four: the same time. A quiz,
then the default profile: nine tenths of the samples in
`Thread.join`. The first design said the table would be almost
empty; it is full, of a thread that is waiting, since wall-clock
mode counts waiting, and the lesson is the same: the profiler samples
the main thread unless told otherwise.

Then `-a` with `--flamegraph`: two columns beneath the root, the main
thread and, under `Thread._bootstrap`, the other five. The sidebar's
Thread Filter picks a worker, and Runtime Stats says it held the GIL
a quarter of the time and waited for it three quarters; the thread
writing the log, with almost nothing to do, waited nine tenths of the
time. Then the GIL in three paragraphs, and `-a --mode gil`: only
the workers' code, and about one sample kept for each look, since
one thread holds the GIL at a time.

Then the counterexample. `gazette/checksums.py` stamps a copy of the
archive for each of six thousand subscribers and hashes it with
SHA-256 on four threads: three seconds on one thread, under one on
four. Its flame graph's Runtime Stats say GIL released, nearly all of
the time. A quiz, then `-a --mode cpu` and `-a --mode gil`: thousands
of samples of `checksum` against a dozen. The rule from the docs:
high in CPU and low in GIL is C with the GIL released, and threads
help; high in both is Python, and they take turns. A sentence on the
free-threaded build.

Closes with the three questions (which threads, what was each doing,
is the work Python or C) and a quiz on a pool of image resizers. Next
is **The price of an exception**.

- Format: terminal and files, with two flame graphs in viewer tabs.
  Ships `gazette/digest.py`, `gazette/checksums.py` and
  `data/articles.json`. Seven pages. Checks read files written with
  `tee`: the two timings on each of the welcome and checksum pages,
  that the default table has `Thread.join` and none of the workers'
  functions, that the GIL-mode table has `build_digest` and next to
  no `Thread.join`, and that `checksum` has more than five times the
  samples in CPU mode that it has in GIL mode; `shell` checks that
  each flame graph names the workers' function under
  `Thread._bootstrap`. The checksum page's timing check needs a host
  with more than one processor free. Written and tested 2026-09-29.

- Requires: nothing beyond the standard library.

- Length: 20 minutes.

### 9. `the-price-of-an-exception`: The price of an exception

My code asks forgiveness, not permission; what does that cost when
most of the input needs forgiving?

`gazette/dates.py` reads fifty thousand filings, each with four
dates written the way of the desk that filed it: `2026-03-14` from
the newsroom, `14/03/2026` from the archive, `14 March 2026` from the
wire agencies, who file two thirds of them. `parse_date` tries the
first format, and in the `except ValueError` tries the second, and in
that one's `except` uses the third, which was fine when nearly every
filing was the newsroom's. The data is `data/filings.csv.gz`,
generated once from the articles with a fixed seed, half a megabyte
compressed.

The wall-clock profile, sorted by cumulative time: nothing looks
wrong, a program that parses dates spends its time parsing dates.
Then what exception mode measures, as the docs say it: samples taken
while an exception is propagating or an `except` block is running,
and everything that block calls, and not a `finally` on the normal
path. A quiz (none, a tenth, a half, all), then `--mode exception`:
about half the samples, and among `parse_date`'s lines the second and
third attempts, which are inside the handlers, lead on direct
samples.

The finding is not the one the first design expected. Raising and
catching is a small part of the cost: measured on its own, a failing
attempt spends under a tenth of its time with the exception raised.
The cost is the failed attempts, which show in the ordinary profile
as `strptime`, and the work done inside handlers, which is what the
mode finds. So the page says the mode detects a path meant to be
rare that has become common, and lists where the docs suggest
looking. The fix, a `file-write` from `fixed/dates.py`, chooses the
format from the text (a hyphen, a slash or neither); the report takes
a little over half the time, and the exception-mode run says "No
samples were collected".

Closes with the mode's rule (it measures time under an exception,
and does not count exceptions), that none of this is an argument
against exceptions, and a quiz on a cache whose handler has most of
the samples. Next is **Following the awaits**.

- Format: terminal and files. Ships `gazette/dates.py`,
  `data/filings.csv.gz` and, outside `files/`, `fixed/dates.py`. Five
  pages, with `write-files`. Checks read the three tables kept with
  `tee` and compare the cumulative count of the `<module>` row, which
  is the number of samples in a table: more than a quarter as many
  under an exception as in wall-clock time before the fix, and under
  a tenth after. Written and tested 2026-09-29.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 10. `following-the-awaits`: Following the awaits

My async program's waiting is all in the event loop; whose is it?

The feed fetcher from workshop 7 rewritten with `asyncio`,
`gazette/crawl.py`: a task for each of twenty feeds, started with
`gather`, with a semaphore that allows four connections to the server
at a time, since a crawler that opens twenty at once is not a polite
one. The server is workshop 7's with a delay of a fifth of a second.
The page first runs the synchronous `feeds.py` and then the crawler,
unprofiled, four and a half seconds against one and a half.

The default profile is not, as first designed, all event loop. The
coroutines that run are in it, beneath six frames of `asyncio`, and
`same_story` has its quarter as it did in workshop 7. What the loop
has is the waiting: two thirds of the samples in
`EpollSelector.select`, one row for the waits of every task, with
nothing to say whose or for what. The page asks for that prediction
in a quiz first.

Then `--async-aware` as a flame graph, and the page explains what the
profiler does differently: it reads asyncio's record of its tasks and
builds the stack from the chain of awaits, with a `<task>` marker
naming each task. The root is `Task-1`, `main` is beneath it twice
(a box carries its line), and the tasks `gather` started are beneath
the line that awaits them. The loop is gone and so is the waiting: a
third of the samples remain, since `--async-mode running`, the
default, records only the task that was running.

Then `--async-mode all`, as a table and as a flame graph. Every
suspended task is recorded at the await where it stopped, a sample
counts once for each task in it, so the table adds up to eight times
the samples and its times are task-seconds. Two thirds of the tasks'
time is in `Semaphore.acquire`, the queue for a connection, and three
tenths in `StreamReader._wait_for_data`, the server: the crawler
waits mostly for a turn. In this mode a running task is shown by its
coroutines alone, so `merge` is counted on the line of `main` that
called it.

Then the restrictions, with one tried (`--mode cpu`, refused with the
message quoted): no `--mode` but wall, no `-a`, no `--native`, no
`--no-gc`. Exception mode is refused too, which the docs' list of
restrictions leaves out and the option's own entry includes. The
server is stopped on the finish page. Next is **Native code and the
collector**.

- Format: two terminals and files, the flame graphs in the HTML
  viewer. Ships `gazette/crawl.py`, `gazette/feeds.py`,
  `slow_server.py` and the data. Variables: `server_port`, default
  8072. Checks: a `shell` check that the server answers, `kernel`
  checks that read the tables kept with `tee` (the loop's `select`
  leads the default run, the semaphore leads the all-tasks run), and
  `shell` checks that the async-aware flame graph holds `Task-1` and
  not the loop's `select`.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 11. `native-code-and-the-collector`: Native code and the collector

Some of my time is in C and some is in the garbage collector; can the
profiler show either?

Two questions, one workshop, because the two special frames are
introduced together in the docs and are the same idea: a marker the
profiler adds to a stack for something that has no Python frame.

First native code. `gazette/index.py` builds search indexes, for the
whole paper and for each section, author and month: `count_words`
with a regular expression whose `sub` calls `singular` for every
word, `rank` with `sorted` and a key function, `relevance`, that
parses a date with `datetime.strptime`, and `write` with `json.dumps`
and `zlib.compress`. With defaults, time in a C function is counted
on the Python line that called it, and the page shows that on the
line that compresses and says it is usually what you want.

Then `--native` as a flame graph. On rc2 the marker is not what the
design assumed (see Known blockers): a `<native>` frame is added
where the stack passes through C code to reach a Python function, and
nowhere else. So it appears between `rank` and `relevance` (that is
`sorted`), between `relevance` and the standard library's
`_strptime` (`datetime.strptime` is C and calls Python), and between
`count_words` and `singular`, and not beneath `write`, whose time in
`zlib.compress` stays on the line. The page asks for that prediction
in a quiz and is plain that the marker names no C function and
measures no C time. What it is good for is a function that is
running with no call to it in sight.

Then the collector. `gazette/graph.py` builds the graph behind the
"related stories" box, a `Story` for each article and a `Link` for
each pair that share three keywords, eight times over for the paper
as it stood on each of the last eight days, letting each graph go as
the next is built. The graphs are cycles, so only the collector frees
them, and the program reports how many times it ran (about eighteen
hundred). The default table has a `<GC>` row with a tenth to a
quarter of the samples. `--no-gc` removes the marker and the samples
move to the lines the collector interrupted, mostly
`Link.__init__`.

The demonstration is not `gc.freeze()`, which made no difference
here, but a `file-write` that turns the collector off while the
graphs are built and runs it by hand once for each: twenty
collections, and half a second saved in two and a bit. The page says
it is a demonstration and what the better fix would be. It also
shows, on the line that is `gc.collect()` and nothing else, that many
of the collector's samples do not get the marker on this release (see
Known blockers), so `<GC>` is to be read as the least the collector
took.

Next is **Down to the bytecode**.

- Format: terminal and files, the flame graph in the HTML viewer.
  Ships `gazette/index.py`, `gazette/graph.py` and the data, with the
  changed `graph.py` under `fixed/`. Checks: `kernel` checks on the
  tables kept with `tee` (rows for `write` and `relevance`; a `<GC>`
  row with the marker and none without; the collector's count in the
  changed program's output), and a `shell` check that the `--native`
  flame graph holds `"<native>"`, which is how the HTML stores it.

- Requires: nothing beyond the standard library.

- Length: 20 minutes.

### 12. `down-to-the-bytecode`: Down to the bytecode

The interpreter specialises my code as it runs; can I see what it did?

Background first, since most readers will not know it: the
interpreter rewrites instructions that have run a few times into
specialised forms on the evidence of what it met, `LOAD_ATTR`
becoming `LOAD_ATTR_INSTANCE_VALUE`, `BINARY_OP` becoming
`BINARY_OP_ADD_INT`, each with a check that falls back to the general
way when it fails. `--opcodes` records the instruction executing at
each sample. The page tries it with the table first and quotes the
refusal, which lists the outputs it is accepted with.

`gazette/scores.py` scores every article for each of 2,500 readers
in a small function, `score`, and makes its articles in one of two
ways, chosen on the command line: `one-class`, every article an
`Article`, or `by-section`, each an instance of one of eight
subclasses that differ in a class attribute. One file and not the
two first planned, so that both heatmaps are of the same source and
the same lines.

`--opcodes --heatmap` on the first, and the page reads the panel
under the hot line: `CONTAINS_OP_SET`, `LOAD_ATTR_INSTANCE_VALUE`,
and the superinstruction that has no badge. The `for` over a
frozenset is plain `FOR_ITER`, which has specialised forms for lists,
tuples, ranges and generators only, and floor division is plain
`BINARY_OP`, and the page says neither is a fault.

Then the second form. Unprofiled it takes a third longer. The design
expected the instructions to lose their specialisation. They do not:
the names, the badges and the share specialised are the same, and
the samples on `LOAD_ATTR_INSTANCE_VALUE` are several times what
they were, because the profiler reads the instruction that is in the
bytecode and cannot see its check fail. So the lesson is that the
name says what the interpreter chose and the samples say whether the
choice is paying.

The flame graph's tooltip is named on the finish page and not
driven. The lesson is kept modest, as the docs keep it: work from
the top, and the instruction is the last view to need. Next is **Did
the fix work?**.

- Format: terminal and files, the heatmap pages in the HTML viewer.
  Ships `gazette/scores.py` and the data. Checks: a `shell` check on
  the refusal, a `shell` check that the heatmap's page for
  `scores.py` holds `LOAD_ATTR`, and a `kernel` check that reads the
  `data-bytecode` attributes of both heatmaps and expects the
  attribute loads to have more samples, for every hundred on the
  membership test, with eight classes than with one.

- Requires: nothing beyond the standard library.

- Length: 15 minutes.

### 13. `did-the-fix-work`: Did the fix work?

I changed the code; how do I show it got faster, and where?

The report generator of workshops 1 and 5 with a second stage,
`hardest`, which scores every article for how hard it is to read
(`reading_ease`, `syllables`), so that the program has something
left to profile when `count_words` is fixed. Everything is recorded
at `-r 10khz`, because the fixed program runs for a tenth of a
second, and the page says why the rate is chosen for the shortest
run and used for all.

A baseline in the binary format, replayed as a table. Then the
program compared with itself, `run --diff-flamegraph baseline.bin`,
so the learner sees noise before trusting a signal: the wide box
grey, and `main` and the frames above it in strong colours from a
sample or two, which gives the two rules the page states (the colour
is about direct time, and colour without width means nothing).

Then the fix as a `file-write`, a recording of the fixed program,
and `replay --diff-flamegraph baseline.bin -o diff.html fixed.bin`.
`count_words` is blue. Everything the fix did not touch is red, and
the tooltip says `syllables` took three milliseconds before and forty
now, when it took forty both times. The profiler scales the baseline
to the length of the new run before it compares (see Known
blockers), so the colours compare shares of a run. The page asks for
that prediction in a quiz, explains it, says when it is the right
comparison, and prints the two tables for the times themselves.

The second change makes a regression on purpose: `hardest` sorts its
scores each time one is added. It is compared with the recording
made just before it, `fixed.bin`, where it shows as one red function
among grey ones, with the functions beside it pale blue from the
same scaling in the other direction. Against the first baseline it
would have been one more red box, which is the case for the
discipline the page closes on: compare each change with the profile
made just before it, recorded the same way.

The elided switch is named on the finish page and not driven, since
these programs lose no stacks worth showing. Next is **Watching it
live**.

- Format: terminal and files, the flame graphs in the HTML viewer.
  Ships `gazette/report.py` and the data, with the two later
  versions under `fixed/` and `regressed/`. Checks: `kernel` checks
  on the replayed tables (`count_words` leads the baseline and loses
  its lead), `shell` checks that the learner's `report.py` has each
  change, that the recordings exist and that each HTML file is a
  differential flame graph.

- Requires: nothing beyond the standard library.

- Length: 20 minutes.

### 14. `watching-it-live`: Watching it live

Can I watch where a program is spending its time while it runs?

`--live` is `top` for one Python process. `gazette/loop.py` rebuilds
the report of workshop 13 over and over for as many seconds as it is
told, and the page starts it for two minutes under `run --live`. It
is one file, because under `run` a script's own directory is not on
the import path (see Known blockers). The page walks the header
(samples and achieved rate, efficiency, what the threads were doing,
the top three) and the table.

The keys are pressed with `send-key` actions, one each: `s` for the
sort, `/` with `count` and Enter to filter, `c` to clear, `x` for
the trend colours (which are on to begin with), `t` for one thread,
`p` to pause and again to resume, `h` for the list of keys, and `q`
to leave, which stops the program too. The page notes that live mode
takes no output format and needs sixty columns and `curses`.

Then how many samples are enough. The arithmetic for a function with
5% of the samples, worked properly (a percent and a half either way
at a thousand samples, a seventh of a percent at a hundred
thousand), with the docs' rounder figures named. `-r 5khz -d 5 -o
rate.pstats`, and then `--realtime-stats` at twenty kilohertz, with
the line it keeps up to date explained. The container keeps up at a
hundred kilohertz, so the page does not promise a shortfall: it says
what to compare and what to do when the rate achieved falls short,
which is to sample for longer.

Closes the collection and points at **Tachyon on real applications**.

- Format: terminal and files, the terminal with most of the height.
  Ships `gazette/loop.py` and the data. Checks: `shell` checks that
  a profiler is running in live mode after the start and is not
  after `q`, by reading `/proc`, a `kernel` check that `rate.pstats`
  holds between 12,000 and 27,000 samples, and a `kernel` check on
  the statistics run's output kept with `tee`.

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
diagnosis and the fix, and were written together. Fifteen to
twenty-five minutes each, a little over two hours in total. Each is
self-contained: the Flask application is shipped with each of the
workshops that use it, and each restates in a sentence what a sample
and a flame graph are.

Every workshop that profiles a server runs it in one terminal and
drives it from a second, with the profiler wrapped around the server
in the first (`run -d <seconds>`, so the profile is written when the
duration ends without anyone stopping the server) and the flame graph
or heatmap opening in the HTML viewer. The load comes from a shipped
`load.py`, which sends requests with `urllib` from four threads at a
fixed pace, two hundred a second in all, until a time is up or the
server stops answering. The pace is fixed so that two recordings made
before and after a fix are of the same load. The start and the load
are two actions placed together, with the explanation before them,
since the duration begins when the first is clicked; the check that
follows waits for the profile to be written.

## The applications workshops

### 1. `a-flask-application-under-load`: A Flask application under load

What does a profile of a web application look like, and what should I
expect to see in it?

The `gazette` newsroom behind Flask, `gazette/web.py`: a front page,
an article page, a search over the word index, and a health check,
with a sqlite database, `data/gazette.db`, built from the articles on
first start. The welcome page says what is different about profiling
a server (it never finishes, so a duration is needed; it does nothing
until asked, so load is needed; and it does many small things, so the
question is which kind of request costs the most). The second page
explains `run -a -d 20 --flamegraph -o wall.html -m flask --app
gazette.web run --port {{ server_port }}`, with `-m` for a module and
`-a` because the development server handles each request on a
thread, which a quiz asks the learner to predict the consequence of,
and then starts it and sends the load.

The third page reads a server's flame graph for a reader who has only
seen a script's. It has two towers, found by the name in the top box,
since which is the wider depends on how busy the server was: the main
thread, which is the accept loop ending in `select`, and the request
threads laid over one another, the standard library's servers, then
Werkzeug and Flask, then the views. The boxes are labelled with a
line, and `search` on the line of its query is far wider than the
rest. The Thread Filter is described as it is on this server, a list
of thousands, since the development server starts a thread for each
request. The fourth page profiles again with `--mode cpu`: the main
thread's tower all but goes, the total falls, and the page says which
view answers "what is the server doing" (wall) and "where is the
processor going" (cpu).

Closes by setting the table `load.py` prints, the view from outside,
beside the flame graph, the view from inside, and hands to **The slow
endpoint**. Both servers have exited on their duration before the
finish, which a check confirms.

- Format: two terminals and files, with the flame graphs in the HTML
  viewer. Ships the `gazette` package with `web.py` and `templates/`,
  `load.py` and the data. Variables: `server_port`, default 8081.
  Checks: a `shell` check that the server answers `/health` after it
  starts, `shell` checks that wait for `wall.html` and `cpu.html` and
  look for the request threads, Flask and the views in them, and a
  check that nothing is left listening.

- Requires: `flask` pinned to the release checked (3.1.3 on
  2026-09-29).

- Length: 20 minutes.

### 2. `the-slow-endpoint`: The slow endpoint

One endpoint is slow; how do I find the line and prove the fix?

The same application, and the search endpoint is the slow one because
`search` looks up each matching article with its own `SELECT`, the
classic query in a loop, a thousand queries for a search on a common
word. The workshop is the fundamentals collection's tools applied in
order, all from one recording: a baseline under load with `--binary`,
replayed as a table; the flame graph, to see `search` wide with
nothing beneath it, since sqlite is C and its time stays on the
Python line that called it; the heatmap of `web.py`, to find the loop
with the `execute` in it; the fix as a `file-write`, one query with a
`JOIN`, an `ORDER BY` and a `LIMIT`; a second recording under the
same load; and the proof three ways, what the readers saw, the two
tables, and a differential flame graph.

The differential flame graph has `search` blue and nearly everything
else red, the main thread's `select` included, because the fixed
server's threads were busy for less time in all and the profiler
scales the baseline before comparing. The page says so, with a quiz,
and sends the learner to the tables for the amounts. The page on the
flame graph is explicit about the profile's limits: the time inside
sqlite is not divided up, `--native` would add nothing since a query
does not call back into Python, and how the database carried out the
query is the database's business.

The heatmap's pages are numbered by how many samples each file had,
so the number of the page for `web.py` differs between machines. The
workshop finds it by its title and copies it to `heatmap-web.html`.

Closes with the loop the fundamentals collection ended on, record,
change, compare, now on a service, and names `front_page` as the next
to look at. Next is **An async service that stalls**.

- Format: two terminals and files, with the flame graphs and the
  heatmap in the HTML viewer. Ships the `gazette` package with the
  slow `search`, `fixed/web.py` as the `file-write` source, `load.py`
  and the data. Variables: `server_port`, default 8082. Checks:
  `shell` checks that wait for `baseline.bin` and `fixed.bin`, that
  the heatmap page is `web.py`'s, that the learner's `web.py` has the
  `JOIN`, and that `diff.html` is a comparison; `kernel` checks on the
  two tables that `search` has the most samples of any view before,
  and less than half its share after.

- Requires: `flask`.

- Length: 20 minutes.

### 3. `an-async-service-that-stalls`: An async service that stalls

My async service is slow under load and the machine is idle; what is
blocking the loop?

The newsroom as an ASGI service, `gazette/asgi.py`, on Starlette under
uvicorn. The search endpoint awaits an index service,
`index_server.py`, through `httpx`; the service takes a twentieth of a
second to answer, with a sleep as the honest stand-in. The article
page lists the five articles most like the one shown, which it finds
by comparing the article's words with every other article's, some
hundredth of a second of computing with no `await` in it. The page has
the learner see the stall before explaining it: `load.py` against the
search endpoint alone reports one latency; with articles being read
as well the search latency doubles, though a search did nothing
different.

Then the profiler with its defaults around uvicorn (`run -d 15
--flamegraph -m uvicorn gazette.asgi:app`), since the loop's thread is
the main thread. Under `_run_once` the tower divides into `select`,
the loop waiting, and `Handle._run`, the loop at work, and the second
is four times the first, with `related` beneath it. A quiz asks where
`search` is, which is nearly nowhere: the request that suffers is the
one that waits. The next page profiles with `--async-aware` as a
table, which says the same by task, and explains two things found in
writing: the async-aware flame graph is no use for a server, and
`--async-mode all` answers another question.

The fix is in two steps, because the first one everybody reaches for
does not work. `asyncio.to_thread` moves `render_article` to a thread,
and the search latency hardly changes, since the thread and the loop
share the interpreter's lock; the flame graph with `-a` shows the
work under the pool's threads and the sidebar shows a quarter of the
samples waiting for the GIL. A `ProcessPoolExecutor` started in the
application's lifespan, with `run_in_executor`, gives the loop back:
the search latency returns to what it was alone, and `related` is no
longer in the profile at all, which hands to the next workshop.
FastAPI is named as the framework most readers would have used, with
the reason it is not.

Closes with the rule for reading an async service's profile: look at
what is running, not at what is slow. Next is **Workers and
subprocesses**.

- Format: three terminals and files, with the flame graphs in the
  HTML viewer. Ships `gazette/asgi.py`, `index_server.py`, `load.py`
  (eight readers, one request after another, three articles for every
  search) and the data, plus `threaded/asgi.py` and `pooled/asgi.py`.
  Variables: `server_port`, default 8083, and `upstream_port`, default
  8084. Checks: `shell` checks that both servers answer and that both
  are stopped, that the flame graphs have the functions each page
  describes, and that the async-aware table has `related` at the top;
  `kernel` checks on what `load.py` printed that a search slowed when
  articles were read and recovered with the pool.

- Requires: `starlette`, `uvicorn`, `httpx`, pinned to the releases
  checked (1.7.0, 0.54.0 and 0.28.1 on 2026-09-29).

- Length: 25 minutes.

### 4. `workers-and-subprocesses`: Workers and subprocesses

My program does its work in child processes; how do I profile those?

Two shapes of the same problem. First a job runner:
`gazette/jobs.py` builds digests of the archive on a
`ProcessPoolExecutor` of four workers. The profiler with defaults sees
the parent, and the parent's table is nearly all `Condition.wait`,
waiting for its children, which a quiz predicts. Then
`--subprocesses`, and the page explains what the profiler does: it
notices each Python child as it appears, starts a profiler for it
with the same options, and writes one output per process,
`flamegraph_<pid>.html`, up to a hundred at once, through
grandchildren. Then the catch: each child is read by a profiler that
did not start it, a sibling of the program that attaches from
outside, which the kernel's usual ptrace scope refuses, and the
refused profiler says nothing. So the page probes first, as the
attaching workshop does, with `dump` against a background process,
and branches on `can_attach`. Where it is allowed, the run writes
seven files for a pool of four: the parent, the four workers, and
the two processes `multiprocessing` starts for itself on Linux,
which a quiz asks about. The files are told apart by what is in
them, so the page finds a worker's by a function only a worker runs
and copies it to `worker.html`. Where it is refused, the same
command is run and writes the parent's file alone, which the page
names as the sign of a refusal, and a worker's graph made in the
container is shipped as `worker-example.html`.

Then gunicorn: the Flask newsroom under `gunicorn -w 3` for twenty
seconds, with `--subprocesses`, under load, and four flame graphs,
the arbiter asleep in `wait_for_signals` and three workers each
serving a share of the requests on its main thread (on the refused
track the arbiter's alone, which is real, and a shipped
`web-worker-example.html`). The top of a
worker's tower is the arbiter's frames, since the worker was forked
from it. The page uses this to say what a production WSGI server
looks like to the profiler compared with the development server of
workshop 1 (processes and not threads, so `--subprocesses` and not
`-a`), and that no total over the processes is made for you.

Closes with when to reach for `--subprocesses` and what to expect of
it, that `--live` is refused with it, that it follows descendants
only, and that it follows them only where attaching is allowed. Next
is **Profiling a test suite**.

- Format: two terminals and files, with the flame graphs in the HTML
  viewer. Ships `gazette/jobs.py`, `gazette/web.py` and its
  templates, `load.py`, the data, and `worker-example.html` and
  `web-worker-example.html` for the refused track. Variables:
  `server_port`, default 8085; `can_attach`, captured by the probe.
  Checks: a `kernel` check on the parent's table; `kernel` checks
  that the flame graphs moved to `jobs/` and `site/` are what the
  answer allows, one per process with the workers' having
  `build_digest` or requests in them where attaching is allowed, and
  the parent's or arbiter's alone where it is not; `kernel` checks
  that there is a worker's graph to read on either track.

- Requires: `flask`, `gunicorn` (26.2.0 on 2026-09-29).

- Length: 15 minutes.

### 5. `profiling-a-test-suite`: Profiling a test suite

My tests are slow; where does the time go?

A test suite for the newsroom, `tests/`, with pytest: 118 tests of a
small store, a date formatter and a word count made on a thread,
which take four or five seconds for three of the usual reasons. The
`db` fixture builds the sqlite database for every test that asks for
it; two tests sleep for a second waiting for a thread they could
join; and a test with a hundred parametrised cases parses the whole
article file for each. `run --binary -o before.bin -m pytest -q`
records the run, and the flame graph from it is pytest's machinery
with two branches beneath, `pytest_runtest_call` with the tests and
`pytest_runtest_setup` with their fixtures, each about half. The page
shows the search box with `test_` to find the learner's own code. The
heatmap of `conftest.py`, found by its title, shows the fixture's
line. The fixes are three `file-write`s, the fixture's scope first
and then the other two together, with a run after each, and the suite
ends at a fifth of a second.

The page uses `-m` to make the general point: anything you run as
`python -m something` can be run as `python -m profiling.sampling run
-m something`, with its arguments after it. It also says, in a quiz,
why the tracing profiler is the wrong tool here.

A `pytest.ini` is shipped so that pytest takes the workspace as its
root and keeps its cache there, and not in whatever directory above
it has a `pyproject.toml`.

Closes with the three habits and how to read a test run, and the
suggestion to profile the suite once a release and keep the
recording. Next is **Attaching to a running process**.

- Format: terminal and files, with the flame graphs and the heatmap
  in the HTML viewer. Ships the `gazette` package (`store.py`,
  `dates.py`, `refresh.py`), `tests/` with `conftest.py`,
  `pytest.ini`, the data, and the three fixed files under
  `fixed/tests/`. Checks: `kernel` checks on what pytest printed,
  that every test passed and that the run was shorter after the first
  fix and under half after all three; `shell` checks on the flame
  graph, the heatmap page and the replaced files.

- Requires: `pytest` (9.1.1 on 2026-09-29).

- Length: 15 minutes.

### 6. `attaching-to-a-running-process`: Attaching to a running process

The service is already running; can I profile it without restarting
it?

The headline feature of the profiler, and the one most hosts refuse to
an ordinary user, so this workshop is honest about both. The welcome
page explains why attach is the feature production people want (no
restart, no code change, no deploy, a profile of the process that is
misbehaving right now). The second page gives the permission model:
on Linux the kernel's Yama `ptrace_scope` decides, and at its common
setting of 1 a process may read only its descendants; on macOS and
Windows reading another process needs privilege; in a container the
host's kernel decides, and Docker Desktop's has no Yama at all.

Then the probe: an `execute-capture` runs `dump` against a throwaway
child of the shell and stores whether it succeeded, and the Flask
newsroom is started in the first terminal without the profiler. The
probe comes before the server is started, since a capture made while
a terminal is busy takes a minute to return (see Known blockers).
Two tracks follow. Where attach is allowed: `dump -a` for a snapshot
of the running server's stacks while `load.py` runs, then `attach -a
-d 15 --flamegraph -o attached.html` under load, and a check that the
server is the process it was and still answers. Where it is refused:
the shipped `dump-example.txt` and `attached-example.html`, made by
the same commands in the container, and the message the profiler
prints when refused, shipped as `attach-refused.txt`, with the advice
not to follow its suggestions on a machine that is not yours to
decide for. The pid comes from a file the application writes when it
starts, `gazette.pid`, read in the command with `$(cat gazette.pid)`,
so the learner never types one.

A page for both tracks sets out the choices where attach is refused:
root, `ptrace_scope` 0, `CAP_SYS_PTRACE` on a copy of the interpreter
kept for profiling, each an administrator's decision the workshop
will not make, and the two arrangements that need none, starting the
service under `run` or reproducing the problem where you may. Next is
**A profile from production**.

- Format: three terminals and files, with the flame graph in the
  HTML viewer. Ships the `gazette` package with `web.py`, `load.py`,
  the data, `dump-example.txt`, `attach-refused.txt` and
  `attached-example.html`. Variables: `server_port`, default 8086;
  captures `can_attach`. Checks: a `shell` check that the probe
  answered; `kernel` checks that read `can_attach` and look at the
  learner's `dump.txt` and `attached.html` on the allowed track and
  at the shipped examples on the refused one; `shell` checks that the
  server answers, is the same process after attaching, and is stopped
  at the end.

- Requires: `flask`.

- Length: 15 minutes.

### 7. `a-profile-from-production`: A profile from production

How do I get a profile from a machine I cannot look at, and compare it
with last week's?

The record and replay workflow of the fundamentals collection, on a
service, with a notebook that turns two profiles into a chart. The
newsroom runs under `run -a -d 20 --binary -o monday.bin` with
`load.py`, then again after the search fix of workshop 2 as
`friday.bin`, standing in for two captures from a production host,
each a hundred kilobytes or so. The pages explain the operational
shape: the profiler captures in the binary format because it is the
cheapest to write and small enough to copy, the file is copied off
the host, and every picture is made at the desk with `replay`, which
needs the file and Python and nothing else. A `replay --flamegraph`
of Monday opens in the viewer, and `replay --jsonl` writes the two
profiles as JSON lines, whose five kinds of record the page
describes.

Then the notebook, created by the page on the workshop's kernel: a
cell that loads both JSONL files, resolves the string and frame
tables, and totals the samples of each function; a cell that prints
Monday's ten hottest functions beside what they came to on Friday, in
seconds; and a cell that draws a horizontal bar chart with
matplotlib, the two captures side by side, and saves it as
`chart.png`. The page says what the chart adds to the differential
flame graph of workshop 2 (seconds and not shares, a shape you can
put in a report, and a script you can run against every nightly
capture) and what it loses (the paths). A final cell loads the
`.pstats` form of one capture with `pstats.Stats` to show the
standard library route to the same numbers.

Closes the collection: the reader has profiled a WSGI application, an
ASGI service, worker processes and a test suite, knows what attach
needs, and has a way from a recording to a chart. The finish names
the module docs and the Firefox Profiler as the two places to go
next, and the last page describes continuous profiling in a
paragraph.

- Format: two terminals and files, then a notebook, with the flame
  graph in the HTML viewer. Ships the `gazette` package,
  `fixed/web.py`, `load.py` and the data. Variables: `server_port`,
  default 8087. Checks: `shell` checks that wait for `monday.bin` and
  `friday.bin`; a `kernel` check that both JSONL files are whole;
  `learner-kernel` checks that the notebook's totals have `search` in
  both captures with Friday's under half of Monday's, that the chart
  was drawn and saved, and that the pstats file was read.

- Requires: `flask`, `matplotlib` (3.11.2 on 2026-09-29).

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
sidecar, is described on workshop 7's last page and not built.

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
0.15.0 were checked to install and run on it. When 3.15.0 is published,
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

**Terminal and files is the format, with the pictures beside the
program.** The profiler is a command line tool and its output is text
in a terminal or HTML in a file, so a workshop is a shipped program
open in the editor, one or two terminals below it, and the flame graph
or heatmap opened in JupyterLab's HTML viewer beside the program, in
the top row of the layout (not, as first planned, a `url-open` pane;
see Known blockers), so the page, the command and the picture are in
one window, which is what the user asked for in place of a separate
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
with a shipped `load.py` (requests sent with `urllib` from a few
threads, at a fixed pace where two recordings are to be compared).
Every server is stopped with `interrupt`, or has exited on its
duration, before the page that started it ends, and listens on
`127.0.0.1` on a port held in a `number` variable with a default, so
it can be moved if taken.

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
`binder/Dockerfile`, built from `python:3.15-rc-slim` with the locked
requirements `just requirements` exports beside it, because
repo2docker refuses any Python it has no frozen base environment for
and it has them only up to 3.14; a `python=3.15` in `environment.yml`
fails before conda-forge, which does carry 3.15.0rc2, is asked. The
Dockerfile carries the overrides a `postBuild` would have written,
since repo2docker ignores every other file once a Dockerfile is
present, and gives the image the shape Binder needs: user `jovyan`
with uid 1000, the repository in its home directory, `notebook` for
the `jupyter notebook` command BinderHub starts the container with,
under `tini`. It was built and run with BinderHub's command locally
on 2026-09-30, with a workshop driven through its first pages, before
the first Binder build. Codespaces gets 3.15 through uv's Python
installer in `setup.sh`, on the plain Ubuntu dev container image,
because no `devcontainers/python:3.15` image exists yet. Both revert
to the plain forms, `environment.yml` with `python=3.15` (or
`runtime.txt`) and `python:3.15`, once repo2docker and the dev
container images know 3.15 (see Open questions).
The container image in `container/` is `python:3.15-rc-slim` with the
same requirements, the self-test browser and a non-root user, and the
checkout mounted; it is the way the workshops are run and tested on a
Mac, and `just container-lab` starts it. A local `just lab` works on
Linux and starts on macOS, where every profiler step then fails, and
the README says so.

The Binder session forces trust because it is anonymous and thrown
away; the codespace and the container do not, because they belong to
the learner. Both hosted images set `analytics.report` to `always`,
and each collection's index carries an analytics block naming the
sink and its token (see Open questions for the token's term), so
progress is reported without asking. Every welcome message says
progress is reported and what is never sent.

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

**The pictures.** A flame graph or heatmap written into `work/` is
opened with a `file-open` action, `:factory: HTML Viewer` and
`:area: desk`, which puts it in the top row of the layout beside the
program, at the full width of the main area, with the terminals
below. Every layout names its top row `desk` and gives the terminal
row two fifths, so the picture has the larger share. Two pictures a
learner compares are stacked, not tabs, because the viewer loads its
file again whenever its tab comes to the front: the page applies a
`compare` layout whose terminal row is a quarter, brings the first
picture back into `desk`, and opens the second with `:area: bottom`
(down-to-the-line page 5, down-to-the-bytecode page 4,
a-flask-application-under-load page 4, profiling-a-test-suite page
5). The images trust HTML files by default so the graph's inlined D3
runs; a `hint` beside the action tells a learner on their own
JupyterLab to click Trust HTML. See Known blockers for why not a
`url-open` pane.

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

In the extension, found writing the first four workshops:

- **`url-open` takes only an http or https URL** (checked in the lint
  rule and again at run time in `packages/labextension/src/actions/url.ts`),
  and nothing tells a page the browser-facing base URL, so a flame
  graph written into `work/` cannot be opened in a `url-open` pane at
  its `/files/` URL. The workshops open it in JupyterLab's own HTML
  viewer instead. Until jupyterlab-workshop 0.15.0 that took a
  `command` action running `docmanager:open` with the HTML Viewer
  factory, which landed as a tab beside whichever widget was last
  active, a terminal, and in a layout of terminal columns was too
  narrow to read; since 0.15.0 `file-open` takes `:factory:`, and the
  workshops open every picture with `file-open`, `:factory: HTML
  Viewer` and `:area: desk`, into the named top row. The viewer
  runs a file's scripts only when the file is trusted, so the Binder,
  Codespaces and container images set
  `@jupyterlab/htmlviewer-extension:plugin` `trustByDefault` to true
  in their overrides, and the page tells a learner on their own
  JupyterLab to click Trust HTML. Checked with Playwright in the
  container on 2026-09-29: with the override the viewer's iframe has
  `allow-same-origin allow-scripts allow-popups` and the graph draws
  with no console errors. The viewer is the format; a `url-open` pane
  at the `/files/` URL would only be worth having for the next item.
  Workshop 5 made the same check for the heatmap, a directory of
  pages, and found the next item.

- **Links inside an HTML file do not work in the HTML viewer.** The
  viewer shows a file from a blob URL in a sandboxed frame, so a
  relative link has nothing to be relative to. Checked with
  Playwright in the container on 2026-09-29: following a file name
  in the heatmap's index ends in the server's "403 Forbidden,
  blocking request from unknown origin" inside the tab, and the
  caller and callee arrows on a heatmap page do nothing, because the
  script that handles them fails to build a URL. Everything else in
  the heatmap works: the switches, the tooltips on the arrows, the
  folders of the index. So workshop 5 opens each heatmap page with
  an action of its own (`heatmap/index.html`, then
  `heatmap/file_0000.html`, which is the file with the most samples)
  and tells the learner the arrows can be read and not followed.
  An action that opened a workspace file at its `/files/` URL in a
  pane, rather than from a blob, would fix this.

Outside the extension:

- pydantic-core has no wheels for Python 3.15 (checked 2026-09-29,
  release and pre-release), so FastAPI cannot be installed on Binder or
  in the container, and applications workshop 3 uses Starlette.

- No `mcr.microsoft.com/devcontainers/python:3.15` image, and no
  repo2docker support for 3.15 by any route (`runtime.txt` and
  `environment.yml` both end at the frozen base environments it ships,
  up to 3.14; checked 2026-09-29 and confirmed by the first Binder
  build on 2026-09-30), hence the `binder/Dockerfile` and uv
  arrangements above.

- **The error rate depends on the host, so pages never quote one.**
  On 3.15.0rc2 call-heavy programs lose many samples, because a stack
  that changes every few microseconds is often mid-change when read,
  but how many varies more with where the program runs than with the
  program. Measured on 2026-09-29 in the container on Docker Desktop,
  five or six runs each: the generator pipeline of workshop 3 lost 33
  to 39% under the image's own Python or an environment on the
  container's filesystem, and 1 to 20% under an environment on the
  checkout mounted from macOS, which is what a learner in
  `just container-lab` gets; workshop 2's report 15 to 22% against 4
  to 18%; workshop 4's renderer 45 to 48% against 1 to 42%. The
  report of workshop 1 is under 1% everywhere, and `--blocking` is 1
  to 2% everywhere. Why the filesystem under the environment matters
  is not known; the first draft of workshop 3 quoted 40% from the
  author's runs and a first reader saw 7%. So pages say "higher than
  the report's", give a range, and have the learner compare two lines
  they can see; Binder and Codespaces, with no mounted filesystem,
  will probably show the higher figures. Worth checking again on
  3.15.0 final.

- **Exception mode misses handlers that run inside a generator**, on
  3.15.0rc2. `parse_date`, with its second and third attempts inside
  `except` blocks, had about half the samples in exception mode when
  called from a plain loop and under 2% when called from a generator
  expression in the same loop, the first draft of workshop 9's
  program. A generator has an exception state of its own, and the
  profiler reads the thread's (`Modules/_remote_debugging/threads.c`
  checks the embedded `exc_state` and does not follow `exc_info`). A
  script of six cases confirmed it and showed that coroutines are
  missed the same way, so the mode sees next to nothing in an asyncio
  program, which workshop 10 should keep in mind. The shipped program
  calls `parse_date` from a plain loop. Reported to CPython on
  2026-10-01 as [gh-158539](https://github.com/python/cpython/issues/158539);
  when it is fixed, this note goes and the loop can be a generator
  expression again if the page reads better that way.

- **The profiler colours its table whether or not it is writing to a
  terminal**, so a table kept with `tee` has the escape codes in it
  and checks that read one strip them first.

- **`-o` with the default format writes the file and prints no
  table**, so a page that wants the learner to read the table and
  the check to read a file would have to run the program twice.
  Workshops 7, 8 and 9 end the command in `| tee name.txt` and have
  the check read the text, one run for both. Workshops 1, 2 and 6
  keep their `.pstats` checks, where the file is the subject.

Found writing workshops 10 to 14, all on 3.15.0rc2 and all to be
checked again on 3.15.0 final:

- **`--native` marks only C code that stands between two Python
  frames.** The docs say the frames "indicate when Python has called
  into C code". The profiler adds one where the frame chain holds an
  entry frame, which is where C code has called back into the
  interpreter (`Modules/_remote_debugging/frames.c`), so a key
  function under `sorted` gets a marker and `zlib.compress`, which
  calls no Python, gets none, and its time stays on the calling
  line. Workshop 11 teaches the marker as it is.

- **The `<GC>` marker misses some of the collector's samples** unless
  `--blocking` is given. In a program that called `gc.collect()` on a
  line of its own, 52 of 213 samples on that line had the marker
  without `--blocking` and 154 of 218 with it. A first reader's run
  of workshop 11 marked none of 418, and had no `<GC>` row at all,
  so the page describes that case first. A collection that
  follows samples of a different stack is marked in full. The
  profiler's frame cache is the likely cause, since a sample whose
  stack has not changed is served from the cache, and not confirmed.
  Workshop 11 shows it and tells the learner to read `<GC>` as the
  least the collector took. `gc.freeze()`, which the design used for
  its demonstration, made no difference to the graph builder.

- **The differential flame graph compares shares, and labels them as
  times.** The baseline's counts are multiplied by the new profile's
  total time over the baseline's before anything is compared
  (`stack_collector.py`, `_convert_to_flamegraph_format`), so after a
  fix that makes a program fourteen times quicker every function the
  fix left alone is red, and its tooltip gives a "Baseline Self" a
  fourteenth of what it was. Workshop 13 is built around this: it
  compares each change with the recording made just before it, and
  prints tables for the times.

- **A fixed program can be too quick to profile at the usual rate.**
  The report takes a tenth of a second once fixed, a hundred samples
  at a thousand a second. Workshop 13 records everything at
  `-r 10khz`, which the container sustains (it sustains a hundred
  kilohertz on this program).

- **A specialised instruction keeps its name when its check fails.**
  With objects of eight classes the attribute loads in workshop 12
  are still sampled as `LOAD_ATTR_INSTANCE_VALUE`, with several times
  the samples, so the share specialised that the heatmap reports does
  not fall. The design had expected plain `LOAD_ATTR`.

- **Under `run`, a script's own directory is not on the import
  path.** `python sub/script.py` has `sub` as `sys.path[0]`; under
  `python -m profiling.sampling run sub/script.py` it is the working
  directory, and `sys.argv[0]` is absolute. A script that imports a
  module beside it fails under the profiler and not without it.
  Workshop 14's program is one file for that reason, and the
  applications collection, whose programs are packages, should run
  them from the package's parent or with `-m`.

- **`--mode exception` is refused with `--async-aware`**, with the
  other two modes. The docs' section on restrictions names only cpu
  and gil; the entry for `--mode` names all three.

- **`--subprocesses` follows children only where `attach` is
  allowed, and is silent where it is not.** The child monitor
  (`_child_monitor.py`) profiles each new child by spawning
  `python -m profiling.sampling attach <pid>` as a separate process,
  with its stderr sent to `/dev/null`. That profiler is a sibling of
  the program, not an ancestor of the child, so under Yama's
  `ptrace_scope` 1, the usual Linux setting and the GitHub runner's,
  the kernel refuses it as it refuses any attach, and only the
  parent's file is written, with nothing said. Found on 2026-09-30
  when the first CI run of the repository failed the workers
  workshop, which had passed in the container, whose kernel has no
  Yama. The workshop now probes with `dump` first and branches, as
  the attaching workshop does. Already reported upstream as
  [gh-155031](https://github.com/python/cpython/issues/155031),
  "Permission error on subprocesses are not propagated back to the
  user", open since 2026-08-01 with a pull request linked, so the
  refusal may be reported rather than swallowed in a later release;
  the docs still do not say the option needs attach permission.

Found writing the applications collection, on 3.15.0rc2 and
jupyterlab-workshop 0.13.0:

- **An `execute-capture` takes a minute while a terminal is busy.**
  With a server running in a workshop terminal, a capture of `echo
  yes` took 60 seconds in the self-test to return, and under a
  second with no server running. The command itself ran in a tenth
  of a second. A `shell` check in the same place returned at once, so
  it is the capture, or what follows it, that waits; the cause was
  not established. Workshop 6 makes its probe before it starts the
  server. Worth reporting to the extension.

- **The number of a heatmap page depends on the machine.** The pages
  are numbered by how many samples each file had, frameworks
  included, so the page for the application's own file is
  `file_0006.html` on one run and another number on the next.
  Workshops 2 and 5 find the page by its title with `grep -l` and
  copy it to a name of its own.

- **The async-aware flame graph is no use for a server.** Each task
  is a root of its own, by name, and uvicorn starts a task for every
  request, so the graph of fifteen seconds has thousands of towers
  too thin to draw and shows next to nothing. The async-aware table
  adds the tasks together and is what workshop 3 uses. With
  `--async-mode all` the table's top rows are the places tasks wait
  inside asyncio and the libraries, and the blocking function is far
  down it.

- **`asyncio.to_thread` does not cure a call that computes.** The
  design had the blocking call moved to a thread and the latency
  restored. Measured, a search took 55 ms alone, 111 ms with the loop
  blocked, 100 ms with the call on a thread and 52 ms with it in a
  pool of processes. Workshop 3 teaches both steps.

- **How slow a query in a loop is depends on the disk.** With the
  sqlite database in the checkout mounted from macOS, a search of a
  thousand queries took 40 to 100 ms; on the container's own disk,
  which is what the self-test and Binder have, 6 to 10 ms. An
  in-memory database made the loop too cheap to find. The load asks
  for common words so that the search is the widest view on either,
  and pages give the order of the views and not their times.

- **The differential flame graph of a fixed server is red nearly
  everywhere**, the idle main thread included, for the reason
  workshop 13 of the fundamentals collection found: the baseline is
  scaled to the newer recording's total. Workshop 2 explains it and
  uses tables for the amounts.

- **The development server's Thread Filter has thousands of
  entries**, one for each request's thread. Workshop 1 says so
  and reads the threads added together.

- **MarkupSafe has no wheel for Python 3.15** (checked 2026-09-29).
  pip builds it from source, and without a compiler it installs with
  its pure Python fallback, so Flask installs and works in the
  container, a little slower at escaping.

- **gunicorn 26 makes a control socket under the home directory**,
  `~/.gunicorn/gunicorn.ctl`, unless given `--no-control-socket`,
  which workshop 4 gives.

- **Several workers importing the application at once raced to build
  the database.** `web.py` now builds into a scratch file named for
  the process and moves it into place.

- **pytest takes the nearest directory with a `pyproject.toml` as its
  root**, which for a workspace inside this checkout is the
  checkout, and would keep its cache there. Workshop 5 ships a
  `pytest.ini`.

- **The profiler's message when refused suggests `sudo` and turning
  `ptrace_scope` off.** Workshop 6 ships the message, and tells the
  learner to do neither on a machine that is not theirs to decide
  for.

## Open questions

- **Binder and Codespaces builds.** The first Binder build, on
  2026-09-30, failed in repo2docker with "Python version 3.15 on
  linux-64 is not supported!", which is repo2docker's list of frozen
  base environments and not conda-forge; `binder/Dockerfile` replaced
  `environment.yml` and `postBuild` the same day and is to be tried on
  mybinder.org. When repo2docker ships a 3.15 lock, go back to the
  conda route and delete the Dockerfile. The Codespaces build has not
  been tried.

- **Analytics.** Settled on 2026-09-30. Both collection indexes carry
  an `analytics` block naming the sink the wrapt and decorator
  workshops report to, `https://workshop-analytics.grumpys.work/events`,
  and one ingest token for both collections, issued to
  `tachyon-workshops` and expiring 2027-09-21, as the wrapt workshops
  share one token. The block lives in the index itself, which `just
  index` keeps when it regenerates the file. Before the token expires,
  issue another (`just token-issue --name tachyon-workshops --expires
  <date>` in the analytics repository) and paste it into both indexes.

- **Live mode in the self-test.** Settled by workshop 14: `send-key`
  reaches the curses interface in the self-test's terminal, and `q`
  ends it, which the check confirms by finding no profiler in
  `/proc`. What the self-test cannot see is the display itself.

- **The per-line rows of the pstats table.** Checked on rc2; to be
  checked again on 3.15.0 final before workshop 1's text is trusted.

## Status

The writing order is the fundamentals collection's order: the first
workshop settled the manifest (an environment with an empty
`requirements.txt`, `terminal`, `kernel-exec` and `install-packages`,
the program above a `shell` terminal at two fifths), the
`environment-create` first step with a `shell` check that `python` is
3.15, and the `pstats`-reading `kernel` checks; the fourth settled how
a flame graph is shown. Each later one adds one idea to a format that
already works. The applications collection was written in its own
order, the Flask application and its load generator first, since
five of the seven use them. Both collections are complete.

| # | Workshop | Status |
|---|----------|--------|
| 1 | `your-first-profile` | Done |
| 2 | `sampling-or-tracing` | Done |
| 3 | `reading-a-process-from-outside` | Done |
| 4 | `reading-a-flame-graph` | Done |
| 5 | `down-to-the-line` | Done |
| 6 | `record-now-look-later` | Done |
| 7 | `waiting-or-working` | Done |
| 8 | `who-holds-the-gil` | Done |
| 9 | `the-price-of-an-exception` | Done |
| 10 | `following-the-awaits` | Done |
| 11 | `native-code-and-the-collector` | Done |
| 12 | `down-to-the-bytecode` | Done |
| 13 | `did-the-fix-work` | Done |
| 14 | `watching-it-live` | Done |

| # | Workshop | Status |
|---|----------|--------|
| 1 | `a-flask-application-under-load` | Done |
| 2 | `the-slow-endpoint` | Done |
| 3 | `an-async-service-that-stalls` | Done |
| 4 | `workers-and-subprocesses` | Done |
| 5 | `profiling-a-test-suite` | Done |
| 6 | `attaching-to-a-running-process` | Done |
| 7 | `a-profile-from-production` | Done |

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
