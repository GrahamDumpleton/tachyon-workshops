---
title: The fix
requires: [verify:fixed, verify:nothing-raised]
---

# The fix

What the profile found is not that exceptions are slow. Raising one
and catching it was a small part of what it measured. It found two
other things.

The first is work that was thrown away. A date from the wire
agencies is parsed three times, and the first two attempts do most
of the work of parsing before they find that the text does not fit.
That cost is in the ordinary profile too, spread over `strptime`
where it cannot be told from useful work.

The second is where the useful work happens: in the handlers, which
were written for the unusual case and are the usual one. That is
what this mode is for. The profiler's documentation suggests it for
code that uses exceptions to steer, and the places to suspect are
parsers that try formats in turn, lookups that catch `KeyError` on
data where most keys are missing, conversions that catch
`ValueError`, and loops driven by `StopIteration` in older code. In
each the pattern is sound and the question is only how often the
exception is taken. A large share of samples under an exception says
"often".

Here the fix is to look before parsing. The three formats cannot be
mistaken for each other: one has hyphens, one has slashes, and one
has neither.

```{file-write}
:id: write-fix
:title: Replace dates.py with a version that chooses the format first
:path: gazette/dates.py
:from: fixed/dates.py
:open: true
```

```{verify}
:id: fixed
:label: parse_date chooses the format without a try
:trigger: after:write-fix
:substrate: shell
grep -q 'if "-" in text' gazette/dates.py && ! grep -q "except ValueError" gazette/dates.py && echo "parse_date chooses the format from the text" || { echo "gazette/dates.py still has the chain of attempts; click the action above to replace it"; exit 1; }
```

Read the new `parse_date` in the editor, then profile it as before,
in exception mode.

```{execute}
:id: profile-fixed
:session: shell
:title: Profile the fixed date report, keeping the samples under an exception
:wait: prompt
python -m profiling.sampling run --mode exception --sort cumtime -l 14 --no-summary gazette/dates.py | tee fixed.txt
```

The report is the same, and the last line of it says the dates were
parsed in a little over half the time. Then the profiler says it
captured several hundred samples and that none were collected: it
looked at the program five hundred times and never once found an
exception active. There is no table because there is nothing to put
in it.

A date that fits none of the formats still raises `ValueError`, from
`strptime`, as it should. The exception is back to meaning that
something is wrong.

```{verify}
:id: nothing-raised
:label: The fixed report spends next to no time under an exception
:trigger: after:profile-fixed
import re
from pathlib import Path

def kept(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command} command, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    assert "Captured" in text, f"{path} has no profile in it; did the program fail?"
    counts = [int(n) for n in re.findall(r"^\s*\d+/(\d+)\s.*\(<module>\)\s*$", text, re.MULTILINE)]
    return max(counts, default=0)

wall = kept("wall.txt", "first")
after = kept("fixed.txt", "last")
assert after < 0.1 * wall, (
    f"{after} samples under an exception after the fix, against {wall} in the first profile; "
    "expected next to none. Replace gazette/dates.py with the action above and profile it again"
)
print(f"{after} samples under an exception after the fix")
```
