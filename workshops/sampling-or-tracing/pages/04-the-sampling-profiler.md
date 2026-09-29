---
title: The sampling profiler
requires: [verify:sampling-written]
---

# The sampling profiler

Now the same report under Tachyon, saving the profile so the check
can read it, and then again to the terminal so you can read it.

```{execute}
:id: run-sampling-file
:session: shell
:title: Run the report under the sampling profiler, saving the profile
:wait: prompt
python -m profiling.sampling run -o sampling.pstats gazette/report.py | tail -n 1
```

```{execute}
:id: run-sampling
:session: shell
:title: And again, with the table in the terminal
:wait: prompt
python -m profiling.sampling run -l 8 --no-summary gazette/report.py
```

The report's last line is back to a fifth of a second. The profiler
was watching the whole time, and the program never knew: nothing in
the process was told about a call, nothing read a clock, nothing ran
that the program did not run alone. That is the trade, and its other
side is on the table. There is no `ncalls`. The profiler saw
`normalise` on the stack in a few dozen of its two hundred samples
and can say it was the busiest function; it cannot say it was called
415,316 times, or even that it was called more than once. And there
are only two hundred samples, because the program ran for a fifth of
a second, so the percentages are rough: a function on nine samples
against one on ten is a tie, and the ranks below the top few could
swap on another run.

The error rate is higher here than on the first workshop's report,
anything from a few percent to a fifth depending on the machine and
the run, because a program that enters and leaves a function every
few microseconds changes its stack under the profiler's read more
often; the next of these workshops explains why and what to do
about it. The profile is still sound; it only rests on fewer samples.

```{verify}
:id: sampling-written
:label: sampling.pstats holds a profile with no slowdown and no call counts
:trigger: after:run-sampling-file
import pstats
from pathlib import Path

assert Path("sampling.pstats").exists(), "No sampling.pstats yet: run the first command above, which writes it"
stats = pstats.Stats("sampling.pstats")
assert stats.total_tt < 0.6, (
    f"The profile covers {stats.total_tt:.2f} seconds; the report should take well under half a second "
    "under the sampling profiler. Was the tracing profiler used by mistake?"
)
functions = {key[2] for key in stats.stats}
assert "normalise" in functions or "stem" in functions or "tokenise" in functions, (
    "None of the report's word functions were sampled; was gazette/report.py the program?"
)
print(f"{stats.total_tt:.2f} seconds of samples, and the word functions are in the profile")
```

```{hint}
:title: Why the first workshop's report would not have shown this
Under `cProfile` the first workshop's report would have run at nearly
full speed, because its time was inside one call to `list.count` that
ran for milliseconds, and a tracer charges per call, not per
millisecond. The tracer's overhead depends on how many calls a
program makes, not on how long it runs, and this version of the
report makes four million.
```
