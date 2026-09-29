---
title: The suite under the profiler
requires: [verify:before-recorded, quiz:why-not-trace]
---

# The suite under the profiler

The suite is run with `python -m pytest -q`. To profile it, the
profiler's words go in front:

```
python -m profiling.sampling run --binary -o before.bin -m pytest -q
```

**`-m pytest`** runs a module, as `python -m pytest` does, and what
follows it is pytest's. This is general. Whatever you start with
`python -m something`, a test runner, a linter, a framework's
management command, a build tool, you can profile with
`python -m profiling.sampling run -m something`, and its arguments
go after it as they always did.

**`--binary`** records every sample in the profiler's own compact
format. `replay` makes any of the pictures from the recording
afterwards, so the suite is run once and looked at as often as you
like.

The `| tee pytest-before.txt` belongs to the shell. It keeps a copy
of what pytest printed, for comparing later.

```{execute}
:id: record-before
:session: shell
:title: Run the tests under the profiler
:wait: prompt
python -m profiling.sampling run --binary -o before.bin -m pytest -q | tee pytest-before.txt
```

pytest prints its dots and its verdict, 118 passed in four or five
seconds, and then the profiler says what it recorded: a sample for
each thousandth of a second, so between four and five thousand.

```{verify}
:id: before-recorded
:label: before.bin is recorded, of a run in which every test passed
:trigger: after:record-before
import re
from pathlib import Path

file = Path("before.bin")
assert file.exists() and file.stat().st_size > 0, "No before.bin yet: run the tests under the profiler with the action above"
log = Path("pytest-before.txt")
assert log.exists(), "No pytest-before.txt yet: run the tests under the profiler with the action above"
text = re.sub(r"\x1b\[[0-9;]*m", "", log.read_text(encoding="utf-8"))
verdict = re.search(r"(\d+) passed in ([\d.]+)s", text)
assert verdict and " failed" not in text, "pytest did not say that every test passed. Look at what it printed in the terminal; restart the workshop if the tests have been changed"
print(f"before.bin is recorded: {verdict.group(1)} tests passed in {verdict.group(2)} seconds")
```

## Why this profiler

Python has another profiler, the one in `profiling.tracing`, which
records every call a program makes. A test suite is the worst case
for it.

```{quiz}
:id: why-not-trace
question: Why is a profiler that records every function call a poor choice for a test suite?
options:
  - { text: "It cannot profile a module started with `-m`", explanation: "It can. How the program is started is not the difficulty." }
  - { text: "A test run is a very large number of very small calls, so the cost of recording each one is large beside the work, and changes which parts look slow", correct: true }
  - { text: "pytest turns other profilers off while tests run", explanation: "pytest does nothing of the kind." }
  - { text: "It counts only the time in the tests, and the fixtures are left out", explanation: "It records every call, fixtures included. What it adds to each is the trouble." }
explanation: "pytest reaches each test through dozens of small functions, and the tests are small themselves. A cost added to every call falls hardest on code like that, and makes it look slower than code that spends its time in one long call. A sampling profiler adds nothing to the program, so what it shows is how the suite behaves when nobody is looking."
```
