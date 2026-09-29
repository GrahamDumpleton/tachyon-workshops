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
and has you answer it by doing it, in JupyterLab, with the workshop
checking your work as you go. The workshop browser lists each
collection's workshops in the order to take them; open the first, and
the Finish dialog at the end of each offers the next.

Each workshop sets up an environment of its own when it opens, so the
first page asks you to create that environment and takes a moment. You
never have to type code or commands. Every command and every cell
arrives by clicking the action beside the step that explains it. The
profiler's flame graphs and heatmaps open in a pane beside the
instructions, not in another browser tab.

This session runs in a GitHub codespace, which opens in VS Code in the
browser. JupyterLab starts in the background, which takes a minute or
so the first time, and VS Code then shows a notification that the
application on port 8888 is available. Click its Open in Browser button
to open JupyterLab in a new tab. If the notification has gone, open the
Ports panel in VS Code and open the address of the port labelled
JupyterLab.

Leave the JupyterLab port's visibility as Private. JupyterLab here asks
for no password or token, because a private port can only be reached by
you, signed in to GitHub. Making the port public, or visible to an
organization, would let anyone who has its address run code in your
codespace.

As you work through a workshop, its progress is reported to the
workshops' own analytics service: which pages you visited, which
actions you clicked and what the checks found, and when. That is how
it can be seen where the workshops are clear and where they are not.
Nothing in what is reported identifies you or your codespace. Nothing
you type is sent, nor the notebooks you make, the output of cells or
commands, or the answers you give to forms, only which step happened
and when.

When you open a workshop, JupyterLab shows what it will do in this
codespace, which here is to create an environment, write files, run
commands in a terminal and run cells in a notebook, and asks you how
far to trust it. Choose Trust to let its actions run as the workshop
intends. Restricted asks before changing files or running code. You are
asked once for each workshop, and again only if it changes. The
workshops are not trusted for you, because the codespace is yours, tied
to your GitHub account. For the same reason JupyterLab runs without the
GitHub token the codespace holds for your account, so nothing a
workshop runs, and nothing it installs, is handed it.

The codespace belongs to your GitHub account and uses your monthly
Codespaces allowance while it runs. It is not temporary: your work is
kept when you close the tabs, and the codespace stops by itself after a
period of inactivity. You can resume it later from
[github.com/codespaces](https://github.com/codespaces), and JupyterLab
starts again with it. When you have finished with the workshops, delete
the codespace there too, so it no longer uses your storage allowance.
