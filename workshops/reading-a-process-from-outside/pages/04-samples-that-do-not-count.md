---
title: Samples that do not count
requires: [verify:stream-profiles, quiz:error-rate]
---

# Samples that do not count

The profiler reads the program's memory while the program is changing
it. Most of the time a stack changes slowly compared with the
microseconds a read takes, and the sample is consistent. Sometimes the
program returns from a function, or calls one, in the middle of the
read, and the chain of frames the profiler has copied no longer makes
sense: a frame points at another that has gone. The profiler cannot
tell what the stack was at that instant, so it throws the sample away
and counts it. The `Error rate` in the profiler's header is that
count as a share of the samples attempted.

For the report it was under one percent, because `count_words` sits
on one line for hundreds of milliseconds. `stream.py` is different:
every word passes through three generators, so frames are entered and
left tens of thousands of times a second. Profile it and read the
error rate.

```{execute}
:id: profile-stream
:session: shell
:title: Profile the generator pipeline
:wait: prompt
python -m profiling.sampling run -l 3 -o stream.pstats gazette/stream.py
```

```{execute}
:id: show-stream
:session: shell
:title: Show the header the run printed to the file's terminal output
:wait: prompt
python -m profiling.sampling run -l 3 --no-summary gazette/stream.py
```

The second command shows what the first did not, since `-o` sends the
table to a file. Compare its `Error rate` line with the report's,
which was under one percent. Here it is several times that at least,
and how much more depends on the machine: a few percent on some, a
third or more on others, and it moves from run to run on the same
one. Whatever it reads, that share of the samples was unreadable and
thrown away. The profile is still valid, because the samples that
survived are still a random selection of instants, only fewer of
them; a lower error rate only means more of the samples you asked
for were kept.

## Stopping the program to look

`--blocking` takes the other path: before each sample the profiler
stops every thread of the program, reads the stack from a frozen
process, and lets it run again. Nothing changes under the read, so
nothing is thrown away.

```{execute}
:id: profile-blocking
:session: shell
:title: Profile it again, pausing the program for each sample
:wait: prompt
python -m profiling.sampling run --blocking -l 3 --no-summary -o stream-blocking.pstats gazette/stream.py
```

```{execute}
:id: show-blocking
:session: shell
:title: The header, with blocking
:wait: prompt
python -m profiling.sampling run --blocking -l 3 --no-summary gazette/stream.py
```

The error rate falls to a percent or two, and stays there from run
to run, where the ordinary run's rate wandered. The cost is the
program's: stopping and starting a process a thousand times a second
is not free, and the program takes longer to finish, which is the
overhead the profiler otherwise avoids. The documentation's advice is
to use `--blocking` only with a long interval between samples, a
millisecond or more, and only when the stacks change so fast that the
ordinary run gives you too few samples to trust: generator pipelines,
deep recursion, tight loops of tiny calls.

```{verify}
:id: stream-profiles
:label: Both profiles of stream.py were written and sampled its generators
:trigger: after:profile-blocking
import pstats
from pathlib import Path

for name in ("stream.pstats", "stream-blocking.pstats"):
    assert Path(name).exists(), f"No {name} yet: run the command above that writes it"
    stats = pstats.Stats(name)
    functions = {key[2] for key in stats.stats}
    assert "words" in functions or "pairs" in functions, (
        f"{name} has none of the generator functions in it; was stream.py the program profiled?"
    )
print("Both profiles hold samples of the generator pipeline")
```

```{quiz}
:id: error-rate
question: "Suppose a run reports an error rate of 40. What does that mean for the profile?"
options:
  - { text: "Four in ten of the table's numbers are wrong", explanation: "None of the table's numbers are wrong. The samples that were kept are all consistent; the ones that were not were thrown away, not counted." }
  - { text: "The program spent 40% of its time in error handling", explanation: "The error rate is the profiler's, not the program's. The `--mode=exception` option, in a later workshop, is the one that measures time under an exception." }
  - { text: "Four in ten samples were unreadable and discarded, so the profile rests on fewer samples than the rate and duration would suggest", correct: true }
  - { text: "The profiler slowed the program down by 40%", explanation: "Without `--blocking` the profiler never slows the program; the failed reads cost the profiler time, not the program." }
explanation: "The rate counts samples the profiler could not read consistently and discarded. The profile is still valid, on fewer samples; `--blocking` keeps them all, at a cost to the program."
```
