---
title: For the tools you have
requires: [verify:pstats-loaded]
---

# For the tools you have

Python has had profilers for thirty years, and the file they write,
the one the `pstats` module reads, is what the tools built around
them expect: viewers, converters, scripts in your own repository
that somebody wrote in 2015. The sampling profiler writes that file
too. Its default output is called pstats for this reason, and with
`-o` the table goes to a file in that format in place of the
terminal.

```{execute}
:id: replay-pstats
:session: shell
:title: Replay the recording as a pstats file
:wait: prompt
python -m profiling.sampling replay -o profile.pstats report.bin
```

Load it the way a pstats file has always been loaded, sort by
cumulative time, and print five rows.

```{execute}
:id: load-pstats
:session: shell
:title: Read profile.pstats with the pstats module
:wait: prompt
python -c "import pstats; pstats.Stats('profile.pstats').sort_stats('cumulative').print_stats(5)"
```

It is the `pstats` module's own report, in the layout it has always
had, and it works. Read it knowing where the numbers came from. The
first column is headed `nsamples` where a traced profile says
`ncalls`, because the sampling profiler has no idea how often a
function was called; it has the number of samples the function was
in. The header's count of "function calls" is a count of samples for
the same reason, and the per-call columns divide by it and mean
nothing. The times are samples multiplied by the interval, as they
were in the profiler's own table. An existing tool will read this
file without complaint, and it is for you to remember that a
function it shows with a count of 1,253, say, was seen 1,253 times,
and may have been called once.

```{verify}
:id: pstats-loaded
:label: profile.pstats loads with pstats and count_words dominates
:trigger: after:replay-pstats
import pstats
from pathlib import Path

assert Path("profile.pstats").exists(), "No profile.pstats yet: run the replay command above, which writes it"
stats = pstats.Stats("profile.pstats")
total = stats.total_tt
count_words = sum(row[2] for key, row in stats.stats.items() if key[2] == "count_words")
assert total > 0.2, f"The profile holds only {total:.2f} seconds of samples; did the report run to the end when it was recorded?"
assert count_words > 0.5 * total, f"count_words has {count_words / total:.0%} of the time; expected most of it"
print(f"{count_words / total:.0%} of {total:.2f} seconds is in count_words")
```
