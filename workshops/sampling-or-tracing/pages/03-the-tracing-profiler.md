---
title: The tracing profiler
requires: [verify:tracing-written]
---

# The tracing profiler

Run the report under `cProfile`, sorted by the time spent inside each
function.

```{execute}
:id: run-cprofile
:session: shell
:title: Run the report under the tracing profiler
:wait: prompt
python -m cProfile -s tottime gazette/report.py
```

Two things to read. First the report's own last line: it took
several times what it took alone, about four times where this page
was written. Every one of the four million calls paid a small toll,
and the tolls added up to more than the program's own work. Second, the profiler's header, which says
exactly how many calls there were: a little over four million, of
which most were primitive, meaning not recursive. It knows because it
was told about each one.

Then the table, which looks like Tachyon's and is not. The first
column is `ncalls`, the number of times each function was called:
`stem` 164,151 times, `normalise` 415,316 times, the string method
`endswith` 1,312,938 times. Those are counts, not estimates, and a
sampling profiler has no such column, because it never sees a call
happen; it only sees what is on the stack when it looks. `tottime` and
`cumtime` are measured too, with the clock read on the way in and out
of every call, and `percall` divides one by the other, which only
makes sense when you know how many calls there were. Rows are per
function, keyed by the line of its `def`, not per executing line as
Tachyon's are.

Notice too what it counts that Tachyon would not show: the C methods,
`{method 'endswith' of 'str' objects}`, each with its own row and its
own count, because the tracer is told about calls into C as well.

## One profiler, two names

Python 3.15 put its profilers under one package name. Run the same
thing as `profiling.tracing`:

```{execute}
:id: run-tracing
:session: shell
:title: The same profiler under its new name
:wait: prompt
python -m profiling.tracing -s tottime gazette/report.py | head -n 8
```

Same header, same table, same overhead. `profiling.tracing` is
`cProfile`; `cProfile` remains as an alias, and the old pure-Python
`profile` module, which was slower still, is deprecated and goes away
in Python 3.17. Its help text has not caught up yet:

```{execute}
:id: tracing-help
:session: shell
:title: The tracer's help text still says where it came from
:wait: prompt
python -m profiling.tracing --help | head -n 1
```

Finally, keep the tracer's profile in a file, in the `pstats` format
that both profilers write, so the check can read the counts. The
report's last line goes to `traced.txt`, so the check can also set
the time under the tracer beside the time alone, as measured on this
machine.

```{execute}
:id: tracing-to-file
:session: shell
:title: Save the tracing profile to a file
:wait: prompt
python -m profiling.tracing -o tracing.pstats gazette/report.py | tail -n 1 | tee traced.txt
```

```{verify}
:id: tracing-written
:label: tracing.pstats holds exact call counts, and the report took longer to gather them
:trigger: after:tracing-to-file
import pstats
import re
from pathlib import Path

def seconds(path, where):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {where}, which writes it"
    found = re.search(r"Report built in ([\d.]+) seconds", file.read_text(encoding="utf-8"))
    assert found, f"{path} has no time in it; did the report run to the end? Run the {where} again"
    return float(found.group(1))

assert Path("tracing.pstats").exists(), "No tracing.pstats yet: run the command above that writes it"
stats = pstats.Stats("tracing.pstats")
assert stats.total_calls > 1_000_000, (
    f"Only {stats.total_calls:,} calls were recorded; expected millions. Was gazette/report.py the program?"
)
stem_calls = [row[1] for key, row in stats.stats.items() if key[2] == "stem"]
assert stem_calls and stem_calls[0] > 100_000, f"stem was called {stem_calls} times; expected over 100,000"
plain = seconds("plain.txt", "second command on the page before this one")
traced = seconds("traced.txt", "last command above")
assert traced > plain, (
    f"The report took {traced:.2f} seconds under the tracer and {plain:.2f} alone; expected the tracer to slow it down. "
    "Run the second command on the page before this one again, then the last command above"
)
print(f"{stats.total_calls:,} calls recorded; stem was called exactly {stem_calls[0]:,} times. "
      f"On this machine the report took {plain:.2f} seconds alone and {traced:.2f} under the tracer, "
      f"{traced / plain:.1f} times as long")
```
