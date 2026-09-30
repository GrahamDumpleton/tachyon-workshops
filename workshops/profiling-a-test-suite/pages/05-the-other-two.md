---
title: The other two
requires: [quiz:what-is-the-sleep-for, verify:tests-fixed, verify:suite-quicker]
---

# The other two

Two things were wide under `pytest_runtest_call`.

## A sleep where a join would do

{open}`tests/test_refresh.py` has the two widest tests of the
suite, and they do next to nothing. Each starts a `Refresher`, which
counts words on a thread, and then:

```python
    refresher.start()
    time.sleep(1)
    assert refresher.counts["council"] > 1000
```

```{quiz}
:id: what-is-the-sleep-for
question: "The count takes a few hundredths of a second. Why did the flame graph show a whole second in each of these tests?"
options:
  - { text: "Counting the words is slower under the profiler", explanation: "The profiler reads the program from outside and adds nothing to it. The count takes what it always takes." }
  - { text: "The test waits a second whether or not the count has finished, and the profiler counts waiting", correct: true }
  - { text: "The thread was not sampled, so its time was given to the test", explanation: "The thread was not sampled, since `-a` was not given. Time is never moved from one thread to another. The second is the test's own." }
  - { text: "`time.sleep` is written in C", explanation: "It is, which is why the samples are on the test's line and there is no box for `sleep` beneath it. That does not make the second any longer." }
explanation: "The sleep is a guess at how long the thread will take, made generous so that the test does not fail on a slow machine. The test pays the whole guess every time. Waiting for the thread itself, with `join`, takes as long as the thread takes and no longer, and cannot be too short."
```

## A file parsed for every case

{open}`tests/test_dates.py` checks the printed date of a hundred
articles, as one test with a hundred cases. Each case begins:

```python
    article = store.load_articles()[number]
```

which reads and parses the whole file of two thousand articles to
look at one of them. There is a fixture that holds the articles
already, and since the last page it is made once.

## Both fixes

```{file-write}
:id: write-refresh
:title: Replace test_refresh.py with the version that joins the thread
:path: tests/test_refresh.py
:from: fixed/tests/test_refresh.py
:open: true
```

```{file-write}
:id: write-dates
:title: Replace test_dates.py with the version that asks for the fixture
:path: tests/test_dates.py
:from: fixed/tests/test_dates.py
:open: true
```

```{verify}
:id: tests-fixed
:label: The tests join the thread and ask for the articles
:trigger: after:write-dates
:substrate: shell
python -c "from pathlib import Path; r = Path('tests/test_refresh.py').read_text(encoding='utf-8'); d = Path('tests/test_dates.py').read_text(encoding='utf-8'); assert 'refresher.join' in r and 'time.sleep' not in r, 'tests/test_refresh.py still sleeps: click the first action above to replace it'; assert 'load_articles' not in d, 'tests/test_dates.py still loads the articles for every case: click the second action above to replace it'; print('tests/test_refresh.py joins the thread, and tests/test_dates.py asks for the articles fixture')"
```

Run the suite once more, and make its flame graph.

```{execute}
:id: record-after
:session: shell
:title: Run the tests under the profiler
:wait: prompt
python -m profiling.sampling run --binary -o after.bin -m pytest -q | tee pytest-after.txt
```

```{execute}
:id: replay-after
:session: shell
:title: Make a flame graph of the quicker suite
:wait: prompt
python -m profiling.sampling replay --flamegraph -o after.html after.bin
```

```{verify}
:id: suite-quicker
:label: Every test passes, in less than half the time
:trigger: after:replay-after
import re
from pathlib import Path

def verdict(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command}, which writes it"
    text = re.sub(r"\x1b\[[0-9;]*m", "", file.read_text(encoding="utf-8"))
    found = re.search(r"(\d+) passed in ([\d.]+)s", text)
    assert found and " failed" not in text, f"pytest did not say that every test passed in {path}. Look at what it printed in the terminal"
    return int(found.group(1)), float(found.group(2))

count, before = verdict("pytest-before.txt", "first command of the second page")
again, after = verdict("pytest-after.txt", "first command above")
assert again == count, f"{again} tests passed this time and {count} before; the same tests should have been run"
assert after < before / 2, (
    f"The run took {before:.1f} seconds before and {after:.1f} now; expected less than half. "
    "Were the three files replaced before the tests were run? Click the file actions on this page and the last, then run the tests again"
)
assert Path("after.html").exists(), "No after.html yet: run the replay command above"
print(f"{count} tests passed in {after:.1f} seconds, where they took {before:.1f}")
```

Put the first flame graph and this one one above the other, to see
what changed. The first action makes room by shrinking the terminal.

```{layout}
:id: make-room
:title: Make room for two graphs
:name: compare
```

```{file-open}
:id: open-before-again
:title: Bring back before.html
:path: before.html
:factory: HTML Viewer
:area: desk
```

```{file-open}
:id: open-after
:title: Open after.html below it
:path: after.html
:factory: HTML Viewer
:area: bottom
```

In the run this page was written from, the 118 tests took a fifth
of a second, against 4.4 to begin with. The graph has changed
shape. `pytest_runtest_protocol`, the tests and their fixtures, is
no longer nearly all of it. The rest, which was a sliver at the
edge, is pytest getting started: importing itself and the tests,
and rewriting the tests' `assert` statements, which it does so that
a failure can say what the values were. Under setup there is one
`build`, the database being made once, and the tests themselves are
a few thin columns.

What is left is a database that has to be built and the cost of
running pytest at all. That is the sign to stop.
