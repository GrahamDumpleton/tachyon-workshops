# Tachyon workshops

[![Launch on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GrahamDumpleton/tachyon-workshops/main?urlpath=lab)
[![Open in GitHub Codespaces](https://img.shields.io/badge/launch-codespaces-579ACA?logo=github&logoColor=white)](https://codespaces.new/GrahamDumpleton/tachyon-workshops?quickstart=1)
[![test](https://github.com/GrahamDumpleton/tachyon-workshops/actions/workflows/test.yml/badge.svg)](https://github.com/GrahamDumpleton/tachyon-workshops/actions/workflows/test.yml)

Nothing to install: start the workshops on
[mybinder.org](https://mybinder.org/v2/gh/GrahamDumpleton/tachyon-workshops/main?urlpath=lab)
with no account, or in
[GitHub Codespaces](https://codespaces.new/GrahamDumpleton/tachyon-workshops?quickstart=1)
with a GitHub account (see [Launch on Binder](#launch-on-binder) and
[Launch on Codespaces](#launch-on-codespaces) below). Or run them
[in a container](#run-in-a-container) with nothing installed but
Docker, which is also how to run them on a Mac.

Guided, hands-on workshops for
[Tachyon](https://docs.python.org/3.15/library/profiling.sampling.html),
the statistical sampling profiler that arrived in Python 3.15 as the
`profiling.sampling` module. A sampling profiler does not instrument
your program: it reads the call stack of a running process from the
outside, a thousand times a second, and counts what it finds, so the
program runs at full speed and never knows it is being watched. The
first collection teaches the profiler itself: what a sample is and why
taking one costs nothing, how to read the table, the flame graph and
the heatmap it produces, how to choose between wall, CPU, GIL and
exception time, what it shows of threads, async code, native code and
the garbage collector, how to look down to the bytecode, how to compare
two profiles, and how to watch a program live. The second points it at
the programs people run: a Flask application under load, a slow
endpoint found and fixed, an async service that stalls, worker
processes, a test suite, a process that is already running, and a
profile carried from production to your desk.

The workshops run on
[jupyterlab-workshop](https://github.com/GrahamDumpleton/jupyterlab-workshop),
a JupyterLab extension that shows the instructions in a side panel with
clickable actions that drive the session, and checks what you have done
as you go. Each workshop is a directory of a `workshop.yaml` manifest
and Markdown pages, and ships the program it profiles; the profiler's
flame graphs and heatmaps open in JupyterLab beside the program. See
[OUTLINE.md](OUTLINE.md) for the design of the collections.

## The collections

The repository holds two collections and is laid out for more. Each
collection is a course: its workshops are numbered in the order to take
them, and the Finish dialog of each offers the next. A
[catalog](catalog.json) names every collection, so one URL offers them
all. The fourteen workshops of the fundamentals collection and the
seven of the applications collection are written and tested; the
design of every one is in [OUTLINE.md](OUTLINE.md), and its status
table records where each stands.

### Profiling with Tachyon

Fourteen workshops, a little under four hours in total, in the order
to take them. Each is self-contained, so you can start anywhere, but
they build.

**What a sampling profiler is**

1. **Your first profile** (`your-first-profile`, 15 minutes). Run the
   profiler on a small report generator and read the table it prints:
   what a sample is, why time is samples multiplied by an interval, and
   which of the report's functions is eating it.

2. **Sampling or tracing?** (`sampling-or-tracing`, 15 minutes). A
   tidier version of the report, made of four million small calls,
   under cProfile, now `profiling.tracing`, and under Tachyon: exact
   counts against estimates, a program four times slower under the
   tracer and unchanged under the sampler, and which to reach for when.

3. **Reading a process from the outside** (`reading-a-process-from-outside`,
   15 minutes). How the profiler sees inside another process without
   running any code in it, why that needs permission and what this
   machine allows, why the profiler and the program must be the same
   Python, what the error rate and `--blocking` mean, and what the
   rate and duration options do.

**Reading the pictures**

4. **Reading a flame graph** (`reading-a-flame-graph`, 15 minutes).
   The interactive flame graph the profiler writes, open in a tab
   beside the program: what width means, what depth means, zooming,
   search and the sidebar, on a page renderer whose hot function has
   several callers, and the collapsed stacks text the picture is drawn
   from.

5. **Down to the line** (`down-to-the-line`, 15 minutes). The heatmap:
   sample counts painted onto the source, self against total time,
   the one line that costs more than the rest of the file, and the
   same file after the fix.

6. **Record now, look later** (`record-now-look-later`, 15 minutes).
   Capture a profile once in the binary format and replay it as a
   table, a flame graph, a heatmap, a Firefox Profiler file, JSON
   lines and a pstats file, and read what each holds and is for.

**Choosing what to measure**

7. **Waiting or working?** (`waiting-or-working`, 15 minutes). A
   feed reader that fetches from a slow local server and then
   computes, in wall-clock and in CPU mode: how the two views
   disagree, and what the disagreement says about the fix.

8. **Who holds the GIL?** (`who-holds-the-gil`, 20 minutes). Threads:
   why the default view shows only a thread that is waiting, what
   `-a` shows, the per-thread view of the flame graph, GIL mode, and
   hashing threads that release the GIL and do run at once.

9. **The price of an exception** (`the-price-of-an-exception`,
   15 minutes). Exception mode on a date parser that tries one format
   after another: how much of its time is spent under an exception,
   why raising is the small part of it, and the profile after the
   fix.

10. **Following the awaits** (`following-the-awaits`, 15 minutes). An
    asyncio crawler profiled as the event loop's stack and then with
    async-aware profiling as tasks and awaits: which task is running,
    what the tasks that are not running are waiting for, and the
    options that cannot be combined with it.

**Looking closer**

11. **Native code and the collector** (`native-code-and-the-collector`,
    20 minutes). The `<native>` marker, which shows where C code
    stands between two Python functions, on a search index whose sort
    calls back into Python, and the `<GC>` marker for the garbage
    collector, on a graph full of cycles: what each marks and what it
    leaves out.

12. **Down to the bytecode** (`down-to-the-bytecode`, 15 minutes).
    Opcode-level profiling in the heatmap: which bytecode instructions
    run under a line, what the specialising interpreter made of them,
    and what changes when one function is given objects of eight
    classes.

13. **Did the fix work?** (`did-the-fix-work`, 20 minutes). A baseline
    recording, a fix, a second change, and the differential flame
    graph of each: what the colours mean, why they compare shares and
    not times, what noise looks like, and which profile to compare
    with.

14. **Watching it live** (`watching-it-live`, 15 minutes). The
    terminal interface, `top` for one process, driven from the
    keyboard, and then how many samples are enough: the rate and
    duration options and the statistics that say whether the profiler
    kept up.

### Tachyon on real applications

Seven workshops, a little over two hours in total, in the order to
take them. Each runs a realistic program in one terminal and drives
it from a second, with the profiler between them.

1. **A Flask application under load** (`a-flask-application-under-load`,
   20 minutes). Profile the development server for a fixed time while
   a load generator sends it requests: why a server needs a duration,
   a load and every thread, the two towers of its flame graph, and
   wall-clock against CPU time.

2. **The slow endpoint** (`the-slow-endpoint`, 20 minutes). Record a
   baseline under load, find the view with the flame graph and the
   line with the heatmap, replace a query in a loop with one query,
   and prove the fix with a second recording, in tables and in a
   differential flame graph.

3. **An async service that stalls** (`an-async-service-that-stalls`,
   25 minutes). A Starlette service under uvicorn whose searches
   slow down when articles are read: the event loop's thread in a
   flame graph, the tasks in an async-aware table, a fix with a
   thread that does not work and why, and one with a process pool
   that does.

4. **Workers and subprocesses** (`workers-and-subprocesses`,
   15 minutes). A job runner on a process pool, whose own profile is
   all waiting, and gunicorn with three workers, profiled with
   `--subprocesses`: a file for each process, how to tell them
   apart, and why a machine may refuse to follow the children.

5. **Profiling a test suite** (`profiling-a-test-suite`, 15 minutes).
   The profiler around `python -m pytest`: the tests and the fixtures
   in the flame graph, the heatmap of `conftest.py`, and three fixes
   to three common habits.

6. **Attaching to a running process** (`attaching-to-a-running-process`,
   15 minutes). `dump` and `attach` on a server that was started
   without the profiler, where the machine allows it, with shipped
   examples where it does not, and what the permission rules and the
   choices are.

7. **A profile from production** (`a-profile-from-production`,
   20 minutes). Record a service in the binary format, twice, a fix
   apart, replay the recordings as a flame graph and as JSON lines,
   and compare them in a notebook with a table and a chart.

## Launch on Binder

[mybinder.org](https://mybinder.org) is a free public service that
builds this repository into a temporary JupyterLab and runs it for you
in the browser, so there is nothing to install. To start, click this
link:

**[Launch the workshops on Binder](https://mybinder.org/v2/gh/GrahamDumpleton/tachyon-workshops/main?urlpath=lab)**

The badge at the top of this page opens the same link. Building and
starting the session takes a minute or two. When JupyterLab appears, the
workshops are listed in its workshop browser under their collection,
numbered in the order to take them, and the Finish dialog of each
offers the next. A workshop sets up an environment of its own when it
opens, so its first step takes a moment; the image carries the wheels,
so the install does not wait on PyPI.

Opening a workshop locally shows a dialog asking you to trust it, since
its actions run code on your machine. On Binder that dialog is removed:
the session is a container of its own, created for you and discarded
when you are done, and at no time is anything done on your machine.
`binder/Dockerfile`, which Binder builds the session from, installs a
settings override that marks the checkout's workshops as trusted, turns
off editing, subscribes to the checkout's own collection indexes, and
names `binder/welcome.md` as the message shown when the session starts,
which says what the workshops are and how to end the session.

The same override turns on reporting to the workshops' own analytics
service, which each collection's index names as its sink, so a session
reports which pages, actions and checks happened and when, and it can
be seen where the workshops are clear and where they are not. Sessions
are anonymous, and the events never carry notebook contents, cell
output, terminal output or form answers; the welcome message says that
progress is reported before you start.

Binder sessions are temporary: anything you do in one is gone when it
ends, so finish a workshop in the session you started it in. When you
are done with the session, whether you finished a workshop or not, shut
it down rather than closing the browser tab, so the resources go back to
Binder for other users. The Finish dialog at the end of a workshop has a
button for this, and so does JupyterLab's File menu, under "Shut Down".

## Launch on Codespaces

[GitHub Codespaces](https://github.com/features/codespaces) builds this
repository into a container of your own in the cloud and opens it in VS
Code in the browser. It needs a GitHub account, and the codespace uses
your account's Codespaces allowance: personal accounts get a monthly
amount of use at no cost, beyond which GitHub charges for it or stops
it. Unlike a Binder session, a codespace is kept until you delete it. To
start, click this link:

**[Launch the workshops on Codespaces](https://codespaces.new/GrahamDumpleton/tachyon-workshops?quickstart=1)**

The Codespaces badge at the top of this page opens the same link. If you
already have a codespace for this repository, the link offers to resume
it rather than create another.

Creating the codespace takes a few minutes. VS Code opens first, with
`.devcontainer/welcome.md` open in it, while `.devcontainer/setup.sh`
installs Python 3.15, JupyterLab and the extension from
`binder/requirements.txt`, as `binder/Dockerfile` does, and
`.devcontainer/start.sh` starts JupyterLab in the background. When
JupyterLab is ready, VS Code shows a notification that the application
on port 8888 is available: click Open in Browser to open JupyterLab in
a new tab. If the notification has gone, open the address of the port
labelled JupyterLab from VS Code's Ports panel. The tab is not opened
by itself, because browsers block a tab nobody clicked for. From there
the workshop browser lists the workshops in order, as on Binder, and
`setup.sh` installs the same settings override as `binder/Dockerfile`,
with two differences: it names `.devcontainer/welcome.md` as the
message shown when JupyterLab starts, and it does not mark the
workshops as trusted.

On Binder the trust dialog is removed, because the session is an
anonymous container that is thrown away when you are done. A codespace
is yours, tied to your GitHub account, so opening a workshop shows the
trust dialog: what the workshop will do, which here is to create an
environment, write files, run commands in a terminal and run cells in
a notebook, and how far to trust it. Choose Trust to let its actions
run as intended; Restricted asks before changing files or running code.
You are asked once for each workshop, and again only if it changes.
`.devcontainer/start.sh` also starts JupyterLab without the codespace's
GitHub credentials: the `GITHUB_TOKEN` variable is removed from its
environment and git is given no credential helper, so nothing a
workshop runs is handed a token for your account. That narrows what
workshop code can reach; it does not sandbox it.

JupyterLab in the codespace asks for no token, because the forwarded
port is private: only you, signed in to GitHub, can reach it. Leave the
port's visibility as Private. Made public, it would let anyone with its
address run code in your codespace.

A codespace stops by itself after a period of inactivity and keeps your
work, and starting it again from
[github.com/codespaces](https://github.com/codespaces) starts JupyterLab
again with it. A stopped codespace still uses your storage allowance, so
delete it there when you have finished with the workshops.

## Run in a container

The profiler reads another process's memory, which Linux allows a user
to do to processes they start, and macOS and Windows do not without
root or administrator rights. So the workshops run on Linux, and on a
Mac or a Windows machine the way to run them is in a Linux container.
The repository carries a `container/Dockerfile` for that: Python 3.15,
JupyterLab, the extension and a non-root user, with the checkout
mounted so the workshops and everything they write are in your
checkout. With Docker installed:

```
git clone https://github.com/GrahamDumpleton/tachyon-workshops
cd tachyon-workshops
docker build -t tachyon-workshops -f container/Dockerfile .
docker run --rm --init -it -p 127.0.0.1:8888:8888 -e JUPYTER_TOKEN=tachyon \
    -v "$PWD":/home/learner/tachyon-workshops tachyon-workshops
```

Then open `http://127.0.0.1:8888/?token=tachyon`. JupyterLab starts in
the workshop browser with the workshops listed under their collections,
in order, and the trust dialog appears when a workshop opens, since
this is your container. The image's settings start the workshop
browser whichever JupyterLab URL you open; the root URL also carries
the catalog and collections into the session, as `just lab` does
locally. Podman runs the same commands. With
[just](https://just.systems) installed, `just container-build` and
`just container-lab` are the same two steps.

The published `ghcr.io/grahamdumpleton/jupyterlab-workshop` image is
not used here, because its JupyterLab runs on an older Python and each
workshop's environment is built from the Python JupyterLab runs on; the
profiler and the program it profiles must both be Python 3.15.

## Run locally

You need Python 3.15 and [uv](https://docs.astral.sh/uv/), and a Linux
machine: on macOS JupyterLab starts, but every profiler step fails for
want of permission to read another process, and the workshops say so.
Clone the repository, install the environment and start JupyterLab from
the checkout:

```
git clone https://github.com/GrahamDumpleton/tachyon-workshops
cd tachyon-workshops
uv sync --no-dev
uv run jupyter lab --config=jupyter_lab_config.py
```

Python 3.15 is named because each workshop builds its own environment
from the Python JupyterLab runs on, and the profiler is part of 3.15.
uv installs it if it is missing. Without uv, the environment comes from
the requirements file Binder uses:

```
python3.15 -m venv .venv && source .venv/bin/activate
pip install -r binder/requirements.txt
jupyter lab --config=jupyter_lab_config.py
```

Run from the checkout, the workshops appear under Installed in the
workshop browser, because they sit in the `workshops` directory the
extension looks in by default. The config file opens JupyterLab at
`http://localhost:8888/lab?catalog=catalog.json&collection=collections/fundamentals/collection.json&collection=collections/applications/collection.json`,
which adds both collections for the session, so the workshops are
grouped under each collection's heading, numbered in the order to take
them, and adds the catalog. Without the link the workshops are listed
in directory order. From the browser, open a workshop, or go straight
to one with `http://localhost:8888/lab?workshop=workshops/<name>`.
Outside Binder the trust dialog appears when a workshop opens; it lists
what the workshop's pages are allowed to do.

Or clone nothing: install the extension as a uv tool, with the `lab`
extra bringing JupyterLab along, and launch it on the catalog by URL,
with a directory of your own to keep the workshops in:

```
uv tool install --python 3.15 "jupyterlab-workshop[lab]"
jupyter-workshop launch --root ~/training --catalog https://raw.githubusercontent.com/GrahamDumpleton/tachyon-workshops/main/catalog.json
```

The same in one line, installing nothing that stays:

```
uvx --python 3.15 --from "jupyterlab-workshop[lab]" jupyter-workshop launch --root ~/training --catalog https://raw.githubusercontent.com/GrahamDumpleton/tachyon-workshops/main/catalog.json
```

They start JupyterLab on a free port with `~/training` as its root and
open the workshop browser with the catalog added, which offers each
collection to subscribe to; each workshop is installed from this
repository into `~/training/workshops` as you open it, and stays there
for the next launch. To land with a collection's workshops already
listed, give its index instead, and repeat `--collection` to list
several in that order:

```
jupyter-workshop launch --root ~/training --collection https://raw.githubusercontent.com/GrahamDumpleton/tachyon-workshops/main/collections/fundamentals/collection.json
```

## Subscribe from your own JupyterLab

With the extension installed anywhere, on Python 3.15 and Linux,
subscribe to the catalog and every collection here is offered in the
workshop browser, with Subscribe on each; subscribe to a collection and
its workshops are offered under Available, with Install fetching each
from this repository. In the browser, choose "Collections…" and enter
the raw URL of the catalog on the Catalogs tab, or of a collection's
index on the Collections tab:

```
https://raw.githubusercontent.com/GrahamDumpleton/tachyon-workshops/main/catalog.json
https://raw.githubusercontent.com/GrahamDumpleton/tachyon-workshops/main/collections/fundamentals/collection.json
https://raw.githubusercontent.com/GrahamDumpleton/tachyon-workshops/main/collections/applications/collection.json
```

## What is in the repository

```
workshops/
  <name>/                a workshop: workshop.yaml, requirements.txt and pages/*.md,
                         and files/ holding the program it profiles; every
                         collection's workshops sit here side by side
catalog.json             names every collection, by relative path; written by `just index`
collections/
  fundamentals/
    collection.json      the index of the fundamentals collection, in the order to take
                         it, written by `just index`; its id never changes
  applications/
    collection.json      the index of the applications collection, likewise
reference/jupyterlab-workshop
                         a git submodule of jupyterlab-workshop at the pinned release,
                         the full documentation and source of the workshop format
pyproject.toml           the uv project: JupyterLab and the extension on Python 3.15,
                         with the authoring tools in the dev group
binder/                  the Binder image: a Dockerfile on python:3.15-rc-slim, since
                         repo2docker does not yet know 3.15, the locked runtime
                         dependencies exported from uv.lock by `just requirements`
                         that it installs, and the welcome message a Binder session
                         opens with; the Dockerfile fills the wheelhouse and writes
                         JupyterLab's settings
.devcontainer/           the Codespaces container: Python 3.15 installed with uv, the
                         same requirements installed with pip, the wheelhouse and
                         settings, a script that starts JupyterLab on port 8888, and the
                         welcome message VS Code opens
container/               the Dockerfile for running and testing the workshops in a Linux
                         container, which is how they run on a Mac
.github/workflows/       CI: test.yml lints the catalog, every collection and every
                         workshop, and self-tests every workshop, on each push
jupyter_lab_config.py    opens a local JupyterLab on the catalog and every collection,
                         so the workshops are listed under each collection in order;
                         `just lab` and the container pass it to jupyter lab
Justfile                 the common tasks, and the order of each collection; run `just`
                         to list them
.mcp.json                the MCP server configuration for AI agent clients
AGENTS.md                guidance for AI agents writing workshops here
OUTLINE.md               the design of the collections: the workshops, what each
                         covers, and where each stands
```

Each workshop is self-contained and can be copied out on its own.

## Writing and checking workshops

`just install` sets up the environment: it syncs uv, fetches the
reference submodule, downloads the browser the self-test drives, and
links the authoring skill shipped in the jupyterlab-workshop package
into `.claude/skills`.

```
just new <name>              scaffold a workshop under workshops/
just lint                    lint the catalog, every collection index and every workshop
just render <name>           render a workshop to HTML
just test <name>             self-test one workshop in a JupyterLab of its own (Linux)
just index                   write or refresh every collection index and the catalog
just container-build         build the Linux image the workshops run and test in
just container-lab           JupyterLab in the container, with this checkout mounted
just container-test <name>   self-test one workshop in the container
just container-test-slow <name>   the same, on one processor at half speed
```

The order of a collection is the list of workshop names in the
Justfile, which `just index` passes to `jupyter workshop index` one by
one; a new workshop is added there, in its place, as well as to
OUTLINE.md and the list above. On a Mac the self-test runs in the
container, since the profiler cannot read another process there.

Learners run the workshops on machines slower than the one a page was
written on, and sometimes with a single processor, so no page, quiz
or check depends on how long anything took where it was written.
`just container-test-slow` stands in for such a host, and a workshop
is tested there as well as unthrottled.

## Updating the release

jupyterlab-workshop is pinned once, in `pyproject.toml`. `just bump
<version>` moves the pin, relocks, rewrites `binder/requirements.txt`,
relinks the skill and moves the `reference/jupyterlab-workshop`
submodule to the same release tag. Binder builds a fresh image for the
new commit, a codespace created after it installs the new release (an
existing codespace keeps the one it was created with), the container
image picks it up on the next `just container-build`, and CI tests the
workshops against the new release.

The Python the workshops teach is whatever 3.15 release uv, conda-forge
and the `python:3.15` image provide. Until 3.15.0 is published that is
the latest release candidate, and the profiler requires the profiler
and the profiled program to be the same release exactly, which they
always are here because both are the workshop environment's
interpreter.
