---
title: The sampling profiler
requires: [verify:sampling-written]
---

# The sampling profiler

Now the same report under Tachyon, saving the profile so the check
can read it, and then again to the terminal so you can read it. The
first command shows the last four lines of what was printed: the
report's time, then the profiler's own account of what it captured.

```{execute}
:id: run-sampling-file
:session: shell
:title: Run the report under the sampling profiler, saving the profile
:wait: prompt
python -m profiling.sampling run -o sampling.pstats gazette/report.py | tee sampled.txt | tail -n 4
```

```{execute}
:id: run-sampling
:session: shell
:title: And again, with the table in the terminal
:wait: prompt
python -m profiling.sampling run -l 8 --no-summary gazette/report.py
```

The report's last line is back to about what it was alone. The
profiler was watching the whole time, and the program never knew:
nothing in the process was told about a call, nothing read a clock,
nothing ran that the program did not run alone. That is the trade,
and its other side is on the table. There is no `ncalls`. The
profiler saw `normalise` on the stack in a good share of its samples
and can say it was among the busiest functions; it cannot say it was
called 415,316 times, or even that it was called more than once. And
there are only a few hundred samples, one for each millisecond the
program ran, so the percentages are rough: a function on nine
samples against one on ten is a tie, and the ranks below the top few
could swap on another run.

The profiler is a process of its own, so what it costs the program
is a share of the machine, not a toll on each call. With a processor
to spare that is nothing. On a server that gives you a single
processor the two take turns, and the report may take a little
longer than it did alone, still nowhere near what the tracer cost.
The check below sets your three times side by side.

The error rate is higher here than on the first workshop's report,
anything from a few percent to a fifth depending on the machine and
the run, because a program that enters and leaves a function every
few microseconds changes its stack under the profiler's read more
often; the next of these workshops explains why and what to do
about it. The profile is still sound; it only rests on fewer samples.

```{verify}
:id: sampling-written
:label: sampling.pstats holds a profile, and the report ran at about its own speed
:trigger: after:run-sampling-file
import pstats
import re
from pathlib import Path

def seconds(path, where):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {where}, which writes it"
    found = re.search(r"Report built in ([\d.]+) seconds", file.read_text(encoding="utf-8"))
    assert found, f"{path} has no time in it; did the report run to the end? Run the {where} again"
    return float(found.group(1))

assert Path("sampling.pstats").exists(), "No sampling.pstats yet: run the first command above, which writes it"
stats = pstats.Stats("sampling.pstats")
assert stats.total_calls < 1_000_000, (
    f"sampling.pstats holds {stats.total_calls:,} calls, so it was written by the tracing profiler. "
    "Run the first command above, which uses profiling.sampling"
)
functions = {key[2] for key in stats.stats}
assert "normalise" in functions or "stem" in functions or "tokenise" in functions, (
    "None of the report's word functions were sampled; was gazette/report.py the program?"
)
plain = seconds("plain.txt", "second command on the page called Run it plain")
traced = seconds("traced.txt", "last command on the page before this one")
sampled = seconds("sampled.txt", "first command above")
assert sampled < (plain + traced) / 2, (
    f"The report took {sampled:.2f} seconds under the sampling profiler, {plain:.2f} alone and {traced:.2f} under the tracer; "
    "expected the sampled run to be much nearer the time alone. Run the first command above again, "
    "since another program may have had the processor"
)
print(f"The word functions are in the profile. On this machine the report took {plain:.2f} seconds alone, "
      f"{traced:.2f} under the tracer and {sampled:.2f} under the sampling profiler")
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
