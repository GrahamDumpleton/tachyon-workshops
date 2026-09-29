---
title: Tests and fixtures
requires: [verify:flame-written, quiz:setup-or-call]
---

# Tests and fixtures

Make the flame graph from the recording, and open it.

```{execute}
:id: replay-flame
:session: shell
:title: Make a flame graph from the recording
:wait: prompt
python -m profiling.sampling replay --flamegraph -o before.html before.bin
```

```{verify}
:id: flame-written
:label: before.html is written, with the tests and the fixtures in it
:trigger: after:replay-flame
:substrate: shell
python -c "from pathlib import Path; f = Path('before.html'); assert f.exists(), 'No before.html yet: run the replay command above'; t = f.read_text(encoding='utf-8', errors='replace'); missing = [n for n in ('pytest_runtest_call', 'pytest_runtest_setup', 'test_a_refresh_of_nothing', 'conftest') if n not in t]; assert not missing, 'before.html has no ' + ', '.join(missing) + ' in it; record the test run again, on the page before'; print('before.html is written, with the tests and the fixtures in it')"
```

```{command}
:id: open-flame
:title: Open before.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/before.html", "factory": "HTML Viewer" }
```

````{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar. If the tab is blank though the file is trusted,
close the tab and click the action again.
````

## Finding your own code

The graph is tall, and most of its height is not yours. pytest is
built of *hooks*, each called through the same three functions of
a library called pluggy, `HookCaller.__call__`, `_hookexec` and
`_multicall`, so those three come round again and again on the way
down. The functions named `pytest_` between them are the stages of
a run, and they are worth reading: `pytest_cmdline_main`, the run;
`pytest_runtestloop`, the loop over the tests;
`pytest_runtest_protocol`, one test.

To find your own code among this, click in the **Search
functions** box at the top of the graph, and type `test_`. Every box
whose name has `test_` in it keeps its colour and the rest fade.
That catches pytest's own `pytest_runtest_` functions as well, which
is no harm, since they are the landmarks.

## Two branches

Below `pytest_runtest_protocol` the graph divides in two, and the
two halves are about the same width.

- **`pytest_runtest_call`** is the tests themselves. At the bottom
  of it are the test functions. Two are very wide,
  `test_counts_are_there_after_a_refresh` and
  `test_a_refresh_of_nothing`, a fifth of the whole run each. One
  more has a width worth noticing,
  `test_printed_date_of_an_article`, with `load_articles` beneath
  it. The other fifteen test functions are too thin to have names.

- **`pytest_runtest_setup`** is what happens before each test, which
  is mostly its fixtures being made. Follow it down through
  `pytest_fixture_setup` and it ends in `db`, in `conftest.py`, with
  `build` from `gazette/store.py` beneath it.

```{quiz}
:id: setup-or-call
question: "Nearly half of the run is under `pytest_runtest_setup`. What does that say about the suite?"
options:
  - { text: "That pytest is slow to start", explanation: "Starting pytest, importing it and finding the tests, is the narrow part at the edge of the graph. Setup is what is done before each test." }
  - { text: "That nearly half of the time goes on getting ready to run tests, and not on running them", correct: true }
  - { text: "That half of the tests are failing in their setup", explanation: "Every test passed. A fixture that works and is slow looks like this." }
  - { text: "That the tests of the database are slow", explanation: "The tests of the database are among the thin ones under `pytest_runtest_call`. What is slow is what is made for them beforehand." }
explanation: "A test's time is the fixtures it asks for and then the test. `--durations` reports the two apart, and a reader looking for slow tests sees fifteen quick ones. The flame graph adds the fifteen setups together, and they are the widest thing in it."
```
