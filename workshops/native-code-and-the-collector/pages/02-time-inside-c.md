---
title: Time inside C
requires: [verify:index-profile]
---

# Time inside C

Profile the index builder with no options. The `| tee index.txt` at
the end belongs to the shell: it prints the profiler's output as
usual and keeps a copy in `index.txt`, which the check below reads.

```{execute}
:id: profile-index
:session: shell
:title: Profile the index builder
:wait: prompt
python -m profiling.sampling run -l 10 --no-summary gazette/index.py | tee index.txt
```

Find the row for `index.py`, line 65, in `write`. It is near the top,
with about a tenth of the samples, and line 65 is this:

```python
    packed = zlib.compress(document)
```

Nearly all of the time on that line is spent inside `zlib.compress`,
which is written in C. There is no row for `zlib.compress`, because a
row is a Python frame and C code does not have one. The samples
taken while it ran found `write` at the top of the stack, stopped on
line 65, and that is how they are counted: against the line that
made the call.

The same goes for `WORD.sub` and `WORD.findall` on lines 40 and 42
of `count_words`, the regular expression engine, and for `json.loads`
and `json.dumps`, most of whose work is done in C.

For nearly every purpose this is what you want. The line is yours,
you can change it, and whether the time went into the call or into
the code around it is usually plain from reading the line. Line 65
does nothing but call `zlib.compress`.

The rows above and below it are a different matter. `relevance`, on
line 51, has more than half of the samples in its `cumul%` column,
and beneath it `_strptime.py`, the standard library's date parser.
`relevance` is the key function that `rank` gives to `sorted`.

```{verify}
:id: index-profile
:label: The table has the compression on line 65 and the sort's key function
:trigger: after:profile-index
import re
from pathlib import Path

file = Path("index.txt")
assert file.exists(), "No index.txt yet: run the command above, which writes it"
text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
rows = set()
for line in text.splitlines():
    row = re.match(r"\s*\d+/\d+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+(\S+):(-?\d+)\((.+)\)\s*$", line)
    if row:
        rows.add(row.group(3))
assert rows, "index.txt has no table in it; did the index builder fail?"
assert "write" in rows, "The table has no row for write; was the program gazette/index.py?"
assert "relevance" in rows, "The table has no row for relevance; was the program gazette/index.py?"
assert not any("native" in name for name in rows), "The table has a <native> row; run the command as it is written, with no --native"
print("The table has rows for write and relevance, and none for the C functions they call")
```
