---
title: Keeping up
requires: [verify:rate-profile]
---

# Keeping up

A sample every millisecond is the default, and the first workshop's
sixteen hundred samples were enough to put `count_words` at four
fifths of the run beyond doubt. Two options change how many samples
you get. `-r` sets the rate, as a number of samples per second or
with a suffix (`10khz`, `10k`), and `-d` limits how long the profiler
samples for, in seconds, after which it stops whether or not the
program has finished. Try both on the report: five thousand samples a
second for one second.

```{execute}
:id: profile-rate
:session: shell
:title: Sample five times faster, for one second only
:wait: prompt
python -m profiling.sampling run -r 5khz -d 1 -l 3 --no-summary -o rate.pstats gazette/report.py
```

The report runs on to its end, since the profiler only stopped
sampling, but the header says a second and five thousand samples,
and the table is the same shape as before with three times the
samples behind it. The rate you ask for and the rate you get are not
always the same: reading a stack takes time, and at high rates on a
busy machine the profiler falls behind. `--realtime-stats` prints the
achieved rate while it runs, so you can see.

```{execute}
:id: realtime-stats
:session: shell
:title: Watch the achieved sampling rate as it runs
:wait: prompt
python -m profiling.sampling run --realtime-stats -l 3 --no-summary gazette/report.py
```

A line updates in place while the report runs, with the rate in hertz,
the interval it works out to, and the slowest and fastest intervals
seen. At a kilohertz it keeps up; at a hundred kilohertz on a laptop
it would not, and the header's `Captured` line would then say fewer
samples than the rate and duration promise. Nothing is wrong when
that happens. The samples that were taken are still a fair selection
of instants; there are just fewer of them, and the last of these
workshops turns "how many is enough" into arithmetic.

```{verify}
:id: rate-profile
:label: rate.pstats holds about a second of samples at 5 kHz
:trigger: after:profile-rate
import pstats
from pathlib import Path

assert Path("rate.pstats").exists(), "No rate.pstats yet: run the 5 kHz command above"
stats = pstats.Stats("rate.pstats")
total = stats.total_tt
assert 0.6 < total < 1.4, (
    f"rate.pstats accounts for {total:.2f} seconds; expected about one second, "
    "the duration -d 1 asked for. Was -d 1 on the command?"
)
print(f"{total:.2f} seconds of samples, as -d 1 asked")
```

```{hint}
:title: What the check reads
Every row's time in a pstats file is samples multiplied by the
interval, so adding up the direct time of every row gives the length
of time the samples cover. With `-d 1` that is about a second,
whatever the rate.
```
