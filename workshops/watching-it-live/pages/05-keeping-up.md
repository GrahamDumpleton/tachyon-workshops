---
title: Keeping up
requires: [verify:stats-profile, quiz:more-samples]
---

# Keeping up

A rate is a request. To take a sample the profiler has to read the
program's stack out of its memory, which takes some microseconds,
more for a deep stack or many threads, and if the machine is busy
the profiler may not be given the processor when the next sample is
due. Ask for more than can be done and the samples come late.

`--realtime-stats` shows how the sampling is going while it goes.
Try it at twenty thousand samples a second.

```{execute}
:id: profile-stats
:session: shell
:title: Sample at twenty kilohertz and watch the rate
:wait: prompt
python -m profiling.sampling run -r 20khz -d 5 --realtime-stats -l 5 --no-summary gazette/loop.py 8 2>&1 | tee stats.txt
```

While the program runs, one line is kept up to date. It begins
`Stats:` and gives the rate achieved on average, with the interval
between samples that it amounts to, then the lowest and the highest
rate over any short stretch, and `N`, the samples so far.

When the run is over the usual lines follow, how many samples were
captured and at what rate, and then a block headed Unwinder
Statistics, which is about how the profiler read the stacks: how
often it could reuse what it read for the sample before, and how
many reads of the program's memory it made.

Compare the rate achieved with the rate asked for. On a machine
with a processor to spare the two agree, and the lowest rate is not
far beneath. On a busy one the average falls short. Then the counts
are still sound, since each sample is as good as any other, and
there are fewer of them than you planned for.

If the profiler cannot keep up, asking for a still higher rate
makes it worse. Sample for longer. Ten seconds at a thousand a
second is as many samples as one second at ten thousand, the
profiler has ten times as long to take each, and the program is
seen over ten times as much of its life.

```{verify}
:id: stats-profile
:label: The run reported its statistics, and how many samples it captured
:trigger: after:profile-stats
import re
from pathlib import Path

file = Path("stats.txt")
assert file.exists(), "No stats.txt yet: run the command above, which writes it"
text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", file.read_text(encoding="utf-8", errors="replace"))
assert "Stats:" in text, "stats.txt has no line of statistics in it; was the command run with --realtime-stats?"
captured = re.search(r"Captured ([\d,]+) samples in ([\d.]+) seconds", text)
assert captured, "stats.txt does not say how many samples were captured; did the run finish?"
samples = int(captured.group(1).replace(",", ""))
seconds = float(captured.group(2))
assert samples > 5000, f"Only {samples} samples were captured; was the command run with -r 20khz -d 5?"
print(f"Captured {samples} samples in {seconds} seconds, {samples / seconds:.0f} a second where 20000 were asked for")
```

```{quiz}
:id: more-samples
question: A profile of a service, made with the usual options for ten seconds, has too few samples to rank the functions you care about, and `--realtime-stats` shows the profiler only just keeping up. What should be changed?
options:
  - { text: "The rate, to ten times as many samples a second", explanation: "The profiler is only just keeping up at the rate it has. It would fall short, and take much of a processor doing so." }
  - { text: "The duration, to a hundred seconds", correct: true }
  - { text: "The mode, to CPU mode, which keeps fewer samples", explanation: "Keeping fewer samples is the opposite of what is wanted, and the mode changes what is measured." }
explanation: "Samples are rate times duration, and duration is the one that costs nothing. A longer profile also covers more of what the service does."
```
