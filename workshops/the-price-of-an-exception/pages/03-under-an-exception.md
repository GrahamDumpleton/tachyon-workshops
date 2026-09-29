---
title: Under an exception
requires: [quiz:how-much, verify:exception-profile]
---

# Under an exception

Along with the stack, the profiler reads from each thread whether it
has an *active exception*, and `--mode exception` keeps only the
samples in which it has. A thread has one in two situations:

- An exception has been raised and is on its way up the stack,
  looking for a handler.

- An `except` block is running. The exception it caught stays active
  until the block ends.

In terms of code:

```python
try:
    value = parse(text)      # not counted, unless it raises
except ValueError:
    value = fallback(text)   # counted: inside the except block
finally:
    log(value)               # not counted: the exception is over
```

Everything called from inside an `except` block counts too, however
deep. A `finally` block counts only while an exception is passing
through it.

So the mode does not count exceptions. It measures time, as every
mode does: the time the program spends with an exception in hand.
Look at `parse_date` again with that in mind, and predict.

```{quiz}
:id: how-much
question: How much of the run will the profiler find under an exception?
options:
  - { text: "Next to none: raising and catching an exception takes microseconds", explanation: "Raising and catching does. What `parse_date` does after catching is the rest of its work, inside the `except` block." }
  - { text: "About a tenth", explanation: "That would fit a file that was mostly the newsroom's. Two thirds of this one needs the third attempt." }
  - { text: "About half", correct: true }
  - { text: "All of it, since every date goes through a `try`", explanation: "Entering a `try` costs nothing and does not make an exception active. Only a date whose first attempt fails has one." }
explanation: "Four filings in five fail the first attempt, and everything `parse_date` does for them afterwards happens inside an `except` block: the second attempt, and for the wire agencies' dates the third. That is most of the parsing, and the parsing is most of the run."
```

```{execute}
:id: profile-exception
:session: shell
:title: Profile the date report, keeping the samples under an exception
:wait: prompt
python -m profiling.sampling run --mode exception --sort cumtime -l 14 --no-summary gazette/dates.py | tee exception.txt
```

The rows for the script's last line and the interpreter that started
it again have the number of samples in the table, and it is around
half of what it was. Half the run had an exception active.

Now the three lines of `parse_date`, and the first number under
`nsamples`, the direct count, which is the samples in which the line
itself was running. Line 30, the third attempt, has the most, and
line 28, the second, comes next. Both are inside `except` blocks.
Line 25, the first attempt, where most of the program's exceptions
are raised, has a handful. It is on the stack in more samples than
that, as its cumulative count shows, for the moment between the
`raise` inside `strptime` and the `except` that catches it. That
moment is short. Measured on its own, an attempt that fails spends
under a tenth of its time with the exception raised, and the rest
finding out that the text does not fit.

```{verify}
:id: exception-profile
:label: A large share of the run is under an exception
:trigger: after:profile-exception
import re
from pathlib import Path

def kept(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command} command, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    assert "Captured" in text, f"{path} has no profile in it; did the program fail?"
    counts = [int(n) for n in re.findall(r"^\s*\d+/(\d+)\s.*\(<module>\)\s*$", text, re.MULTILINE)]
    return max(counts, default=0), text

wall, _ = kept("wall.txt", "first")
under, text = kept("exception.txt", "--mode exception")
assert wall > 0, "wall.txt has no table in it; run the command on the page before"
assert under > 0.25 * wall, (
    f"{under} samples under an exception against {wall} in all; expected about half. "
    "Has gazette/dates.py already been replaced with the fixed version?"
)
assert "(parse_date)" in text, "Expected parse_date in the table"
print(f"{under} samples under an exception, {under / wall:.0%} of the {wall} in the first profile")
```
