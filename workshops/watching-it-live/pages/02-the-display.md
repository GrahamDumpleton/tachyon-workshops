---
title: The display
requires: [verify:live-running]
---

# The display

Start the program under the profiler in live mode. It is told to
run for two minutes, which is time enough for this page and the
next. If it finishes before you do, the display stops growing and
says so, and everything but the counting still works.

```{execute}
:id: start-live
:session: shell
:title: Profile the program in live mode
:wait: 3s
python -m profiling.sampling run --live gazette/loop.py 120
```

```{hint}
:title: If the terminal shows an error and not a display
Live mode needs a terminal at least sixty columns wide and twelve
lines tall. Make the JupyterLab window wider, or drag the edge of
the instructions panel to give the terminal more room, and run the
action again. It also needs the `curses` module, which Python has on
Linux and macOS and not on Windows.
```

The display fills the terminal. From the top:

- **The first line** has the process id of the program, the thread
  being shown (`ALL` of them), how long the profiler has been
  running, and the sampling interval, 1000 microseconds, which is
  the usual thousand samples a second.

- **Samples** is the count so far and the rate achieved, with a bar
  that compares it with the rate asked for.

- **Efficiency** is the share of attempts to read the stack that
  succeeded.

- **Threads** says what the sampled threads were doing: holding the
  GIL, not holding it, waiting for it, handling an exception, or
  interrupted by the garbage collector. This program computes all
  the time in one thread, so nearly all of its samples are "on
  gil".

- **Top 3** names the three rows with the most direct samples.

- **The table** is the one you know, a row for each line of each
  function that has been sampled. The arrow in the header marks the
  column it is sorted by.

Watch it for a few seconds. The counts rise by a thousand a second
between them. The percentages moved about in the first second and
have now nearly stopped, with `syllables` at about a third. That
settling is the subject of the second half of this workshop.

```{verify}
:id: live-running
:label: The profiler is running in live mode
:trigger: after:start-live
:substrate: shell
python -c "
import glob
running = []
for path in glob.glob('/proc/[0-9]*/cmdline'):
    try:
        words = open(path, 'rb').read().split(b'\0')
    except OSError:
        continue
    if b'profiling.sampling' in words and b'--live' in words:
        running.append(path.split('/')[2])
assert running, 'No profiler is running in live mode; start it with the action above'
print('The profiler is running in live mode, as process', running[0])
"
```
