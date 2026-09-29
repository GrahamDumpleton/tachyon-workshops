# Welcome to the Tachyon workshops

These are guided, hands-on workshops on
[Tachyon](https://docs.python.org/3.15/library/profiling.sampling.html),
the sampling profiler that arrived in Python 3.15 as
`profiling.sampling`, in two collections. **Profiling with Tachyon**
is about the profiler itself: what a sample is and why taking one costs
the program nothing, how to read the table, the flame graph and the
heatmap it produces, how to choose between wall, CPU, GIL and exception
time, what it shows of threads, async code, native code and the garbage
collector, how to compare two profiles, and how to watch a program
live. **Tachyon on real applications** points the profiler at the
programs people run: a Flask application under load, a slow endpoint
found and fixed, an async service that stalls, worker processes, a
test suite, a process that is already running, and a profile carried
from production to your desk. Each one takes a question you might have
and has you answer it by doing it, in this JupyterLab, with the
workshop checking your work as you go. The workshop browser lists each
collection's workshops in the order to take them; open the first, and
the Finish dialog at the end of each offers the next.

Each workshop sets up an environment of its own when it opens, so the
first page asks you to create that environment and takes a moment. You
never have to type code or commands. Every command and every cell
arrives by clicking the action beside the step that explains it, so
your attention goes on reading and predicting rather than on typing.
The profiler's flame graphs and heatmaps open in a pane beside the
instructions, not in another browser tab.

This session runs on [mybinder.org](https://mybinder.org), a free public
service, and it is temporary: anything you do here is gone when the
session ends, so finish a workshop in the session you started it in.
When you are done, whether you finished a workshop or not, shut the
session down rather than closing the browser tab, so the resources go
back to Binder for other users. The Finish dialog has a button for
this, and so does the File menu, under "Shut Down".

As you work through a workshop, its progress is reported to the
workshops' own analytics service: which pages you visited, which
actions you clicked and what the checks found, and when. That is how
it can be seen where the workshops are clear and where they are not.
The session is anonymous, so nothing in what is reported identifies
you. Nothing you type is sent, nor the notebooks you make, the output
of cells or commands, or the answers you give to forms, only which
step happened and when.
