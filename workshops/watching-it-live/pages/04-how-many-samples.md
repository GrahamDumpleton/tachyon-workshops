---
title: How many samples?
requires: [quiz:how-sure, verify:rate-profile]
---

# How many samples?

In live mode you watched the percentages jump about for the first
second and then settle. A profile is an estimate made from samples,
and like a poll it is as good as the number of people asked. Take
a function that has 5% of the samples.

- With **a thousand samples**, its true share is probably somewhere
  between three and a half and six and a half percent.

- With **a hundred thousand samples**, it is within a seventh of a
  percent of 5%.

A hundred times the samples for a tenth of the doubt, which is how
estimates from samples always go: the doubt shrinks with the square
root of their number. The profiler's documentation works the same
case with rounder figures, 3% to 7% and half a percent either way.

Two options set how many there
are. **`-r`** is the sampling rate, a thousand a second unless you
say otherwise, written as `5000`, `5k` or `5khz`. **`-d`** is the
duration, the number of seconds to sample for, after which the
profiler stops the program it started. Without it the profiler
samples until the program ends.

```{quiz}
:id: how-sure
question: A profile of a thousand samples shows `parse` with 6% and `validate` with 5%. What can be said about which of them takes longer?
options:
  - { text: "`parse` takes longer, by a fifth", explanation: "Each of those figures could be a percent and a half out either way. The order of two rows this close is not known." }
  - { text: "Nothing yet: with a thousand samples the two shares are within each other's doubt, and a longer profile is needed to tell them apart", correct: true }
  - { text: "They take the same time, since the difference is within the error", explanation: "Within the error means the profile cannot tell, not that they are equal." }
explanation: "At a thousand samples a share of 5% could be a percent and a half out either way. To rank two functions a percent apart takes tens of thousands. Whether it matters which is first is another question: the function with 60% is not in doubt."
```

Profile the program for five seconds at five thousand samples a
second. It is told to run for eight, and the profiler stops it at
five. With `-o` the profile goes to a file and no table is printed.

```{execute}
:id: profile-rate
:session: shell
:title: Take twenty-five thousand samples
:wait: prompt
python -m profiling.sampling run -r 5khz -d 5 -o rate.pstats gazette/loop.py 8
```

The profiler reports how many samples it captured and in how long:
twenty-five thousand in five seconds, the rate times the duration,
or somewhat fewer on a busy machine where it could not keep to the
rate, which the next page looks at. At twenty-five thousand a row
with 5% is known to within about a quarter of a percent, by the
same arithmetic.

For nearly every purpose the usual rate is enough and the duration
is what to think about. A profile is for finding the function with
a third of the time, not for telling 5% from 6%, and a few thousand
samples find it. The case for more samples is a program with many
small functions and no large one, or a comparison of two profiles.

```{verify}
:id: rate-profile
:label: rate.pstats holds five seconds of samples at 5 kHz
:trigger: after:profile-rate
import pstats
from pathlib import Path

assert Path("rate.pstats").exists(), "No rate.pstats yet: run the command above, which writes it"
stats = pstats.Stats("rate.pstats")
samples = max(row[1] for row in stats.stats.values())
assert samples < 27000, (
    f"rate.pstats holds {samples} samples; expected 25,000 at most. "
    "Was it recorded with -r 5khz -d 5?"
)
assert samples > 6000, (
    f"rate.pstats holds {samples} samples; expected far more than five seconds at the usual rate would give. "
    "Was it recorded with -r 5khz -d 5?"
)
print(f"rate.pstats holds {samples} samples" if samples > 20000 else
      f"rate.pstats holds {samples} samples where 25,000 were asked for: on this machine the profiler "
      "could not keep to 5 kHz, which the next page is about")
```
