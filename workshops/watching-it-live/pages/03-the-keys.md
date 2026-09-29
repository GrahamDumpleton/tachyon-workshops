---
title: The keys
requires: [verify:live-ended, quiz:paused]
---

# The keys

Live mode is driven from the keyboard, a key for each command. The
actions on this page press the keys for you. You can also click in
the terminal and press them yourself.

**`s` changes the sort.** The table starts sorted by direct time.
Each press moves to the next column, and the bottom line of the
display names it.

```{send-key}
:id: key-sort
:session: shell
:title: Press s, to sort by the next column
:keys: s
```

Sorted by a cumulative column, the top of the table is the chain of
callers, `main`, `rebuild`, `hardest`, that the whole program runs
under, which is the view to start from when you do not know the
program.

**`/` filters.** Type part of a function's or file's name and press
Enter, and only the rows that contain it are shown.

```{send-key}
:id: key-filter
:session: shell
:title: Press / and type count, to show only the rows of count_words
:keys: / c o u n t enter
```

**`c` clears the filter.**

```{send-key}
:id: key-clear
:session: shell
:title: Press c, to show every row again
:keys: c
```

**`x` turns the trend colours off and on.** With them on, as they
are to begin with, a number that has risen since the last update is
green and one that has fallen is red.

```{send-key}
:id: key-trend
:session: shell
:title: Press x, to turn the trend colours off
:keys: x
```

**`t` shows one thread at a time.** The first line changes from
`ALL` to the id of a thread and its place among them, `1/1` for
this program. With several threads the left and right arrows move
between them.

```{send-key}
:id: key-thread
:session: shell
:title: Press t, to show one thread
:keys: t
```

**`p` pauses the display.** The table stops changing so that it can
be read. The sampling does not stop.

```{send-key}
:id: key-pause
:session: shell
:title: Press p, to pause the display
:keys: p
```

```{send-key}
:id: key-resume
:session: shell
:title: Press p again, to let it go
:keys: p
```

**`h` shows the list of keys**, and any key puts it away. Among the
ones not tried here, `r` throws away the counts so far and starts
again, which is how to see what the program is doing *now* as
opposed to on average since the profiler started, and `+` and `-`
change how often the display is redrawn.

```{send-key}
:id: key-help
:session: shell
:title: Press h, for the list of keys
:keys: h
```

```{send-key}
:id: key-help-close
:session: shell
:title: Press h again, to put the list away
:keys: h
```

**`q` leaves.** The profiler stops the program it started and gives
the terminal back.

```{send-key}
:id: key-quit
:session: shell
:title: Press q, to leave live mode
:keys: q
```

Nothing was written. Live mode is for looking, and the profiler
refuses `--live` together with an output format such as
`--flamegraph`. When what you see is worth keeping, run again with
the format you want.

```{verify}
:id: live-ended
:label: Live mode has ended
:trigger: after:key-quit
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
assert not running, 'The profiler is still running in live mode; press q in the terminal, or use the last action above'
print('No profiler is running in live mode')
"
```

```{quiz}
:id: paused
question: The display is paused with `p` for ten seconds while a slow request is handled, and then let go. What has happened to the samples taken during those ten seconds?
options:
  - { text: "They were not taken: pausing stops the profiler", explanation: "Pausing stops the drawing. The profiler goes on sampling." }
  - { text: "They were taken and counted, and the table shows them as soon as it is let go", correct: true }
  - { text: "They were taken and thrown away", explanation: "Only `r`, reset, throws samples away." }
explanation: "`p` freezes what is on the screen so that it can be read. Sampling carries on behind it, and the counts include everything when the display resumes."
```
