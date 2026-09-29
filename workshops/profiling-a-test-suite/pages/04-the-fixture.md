---
title: The fixture
requires: [verify:heatmap-written, verify:fixture-fixed, verify:first-rerun]
---

# The fixture

The flame graph says the time is in `db`. The heatmap shows the
fixture with the samples beside its lines. Make one from the same
recording.

```{execute}
:id: replay-heatmap
:session: shell
:title: Make a heatmap from the recording
:wait: prompt
python -m profiling.sampling replay --heatmap -o heatmap before.bin
```

A heatmap is a directory with a page for every source file that had
a sample, more than a hundred here, nearly all of them pytest's.
The pages are numbered by how many samples each file had, so find
the one for `conftest.py` by its title, and copy it to a name of its
own.

```{execute}
:id: copy-heatmap
:session: shell
:title: Copy the page for conftest.py to heatmap-conftest.html
:wait: prompt
cp "$(grep -l 'tests/conftest.py - Heatmap' heatmap/file_*.html)" heatmap-conftest.html
```

```{verify}
:id: heatmap-written
:label: heatmap-conftest.html is the heatmap of conftest.py
:trigger: after:copy-heatmap
:substrate: shell
python -c "from pathlib import Path; f = Path('heatmap-conftest.html'); assert f.exists(), 'No heatmap-conftest.html yet: run the two commands above, in order'; t = f.read_text(encoding='utf-8', errors='replace'); assert 'tests/conftest.py' in t and 'def db' in t, 'heatmap-conftest.html is not the page for tests/conftest.py; run the two commands above again'; print('heatmap-conftest.html is the heatmap of tests/conftest.py')"
```

```{command}
:id: open-heatmap
:title: Open heatmap-conftest.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/heatmap-conftest.html", "factory": "HTML Viewer" }
```

Two lines have the samples. Line 18, `store.build(path, articles)`,
has two thousand or so under **Total**: two seconds of building
databases. Line 11, in `articles`, has a few dozen, for reading the
articles from their file.

Two seconds is not long to build a database of two thousand
articles with an index. It is long to do it fifteen times. Look at
the first line of each fixture:

```python
@pytest.fixture
def db(tmp_path, articles):
```

A fixture declared like this is made afresh for every test that
asks for it, and thrown away afterwards. That is pytest's default,
and the safe one, since no test can spoil what another is given. It
is also why fifteen tests that only *read* the database each wait
for one to be built.

## Build it once

A fixture can be given a *scope*. With `scope="session"` it is made
once, the first time a test asks, and every later test is handed
the same one.

```{file-write}
:id: write-conftest
:title: Replace conftest.py with the version that builds the database once
:path: tests/conftest.py
:from: fixed/tests/conftest.py
:open: true
```

Both fixtures have the scope now. `db` also asks for
`tmp_path_factory` where it asked for `tmp_path`, since `tmp_path`
is a directory for one test and a fixture that outlives a test may
not use it.

```{verify}
:id: fixture-fixed
:label: The fixtures in conftest.py are made once for the session
:trigger: after:write-conftest
:substrate: shell
python -c "from pathlib import Path; t = Path('tests/conftest.py').read_text(encoding='utf-8'); assert t.count('scope=\"session\"') == 2, 'tests/conftest.py does not give both fixtures the session scope: click the action above to replace it'; print('Both fixtures in tests/conftest.py have the session scope')"
```

Run the suite again, under the profiler as before.

```{execute}
:id: record-first
:session: shell
:title: Run the tests again under the profiler
:wait: prompt
python -m profiling.sampling run --binary -o first.bin -m pytest -q | tee pytest-first.txt
```

```{verify}
:id: first-rerun
:label: Every test still passes, and the run is shorter
:trigger: after:record-first
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
again, first = verdict("pytest-first.txt", "command above")
assert again == count, f"{again} tests passed this time and {count} before; the same tests should have been run"
assert first < before * 0.85, (
    f"The run took {before:.1f} seconds before and {first:.1f} now; expected it to be a good deal shorter. "
    "Was tests/conftest.py replaced before the tests were run? Run the two actions above again, in order"
)
print(f"{count} tests passed in {first:.1f} seconds, where they took {before:.1f}")
```

In the run this page was written from the suite went from 4.4
seconds to 2.6. One word, in two places.

A session-scoped fixture is a thing shared, and that is its price.
It suits what tests only read. A test that changed the database
would change it for every test after, and a fixture for tests like
that should stay as it was, or be given back in the state it was
found.
