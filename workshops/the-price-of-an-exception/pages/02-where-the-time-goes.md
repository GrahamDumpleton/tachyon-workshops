---
title: Where the time goes
requires: [verify:wall-profile]
---

# Where the time goes

Start with the profile you know, of all the time that passes, sorted
so that the outer functions come first. The `tee` at the end prints
what the profiler prints and keeps a copy in `wall.txt`, for the
check below and for comparing with the next page.

```{execute}
:id: profile-wall
:session: shell
:title: Profile the date report
:wait: prompt
python -m profiling.sampling run --sort cumtime -l 14 --no-summary gazette/dates.py | tee wall.txt
```

Read the cumulative count, the second number under `nsamples`. The
rows for `_run_module_as_main`, `_run_code` and `<module>` are the
interpreter starting the script and the script's last line, which
are on the stack in every sample, so their count is the number of
samples in the table. Remember roughly what it is. It is lower than
the number the profiler says it captured, because this program calls
small functions so quickly that some samples cannot be read, and
those are left out.

Below them `main`, and then the parsing: `_strptime_datetime_datetime`
is the standard library's `strptime`, with about half the samples,
and `parse_date` appears on three rows, for lines 25, 28 and 30,
which are its three attempts.

Nothing here looks wrong. A program that parses two hundred thousand
dates spends its time parsing dates. The three rows of `parse_date`
are a hint, for someone who knows to wonder why the third attempt has
as many samples as the first, but the table does not say that
anything failed.

```{verify}
:id: wall-profile
:label: wall.txt holds a profile with parse_date in it
:trigger: after:profile-wall
import re
from pathlib import Path

file = Path("wall.txt")
assert file.exists(), "No wall.txt yet: run the command above, which writes it"
text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
kept = [int(n) for n in re.findall(r"^\s*\d+/(\d+)\s.*\(<module>\)\s*$", text, re.MULTILINE)]
assert kept, "wall.txt has no table in it; did the program fail?"
assert "(parse_date)" in text, "Expected parse_date in the table; was gazette/dates.py the program profiled?"
print(f"The table holds {max(kept)} samples, with parse_date among them")
```
