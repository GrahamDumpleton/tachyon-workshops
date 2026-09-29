---
title: Which view?
requires: [verify:flame-written, quiz:what-is-beneath]
---

# Which view?

The table says which lines had the samples. The flame graph says
how the program got to them. Make one from the recording. Nothing
is run again: this is the same twenty seconds, drawn another way.

```{execute}
:id: replay-flame
:session: client
:title: Make a flame graph from the baseline
:wait: prompt
python -m profiling.sampling replay --flamegraph -o before.html baseline.bin
```

```{verify}
:id: flame-written
:label: before.html is written, with the views in it
:trigger: after:replay-flame
:substrate: shell
python -c "from pathlib import Path; f = Path('before.html'); assert f.exists(), 'No before.html yet: run the replay command above'; t = f.read_text(encoding='utf-8', errors='replace'); missing = [n for n in ('dispatch_request', 'search', 'front_page') if n not in t]; assert not missing, 'before.html has no ' + ', '.join(missing) + ' in it; record the baseline again, on the page before'; print('before.html is written, with Flask and the views in it')"
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

There are two towers. The one that starts at `_run_module_as_main`
is the main thread, and ends in `select`, waiting. The one that
starts at `Thread._bootstrap` is every request thread laid over one
another: the standard library's servers, then Werkzeug, then Flask,
down to `dispatch_request`, which calls the view.

Below `dispatch_request` are the views, and one is far wider than
the others together: `search (gazette.web:101)`. The boxes are
labelled with a line as well as a function, so `search` has a box
for each of its lines that was sampled, and line 101 is the one that
matters.

Now look beneath that box, for what `search` called that took the
time.

```{quiz}
:id: what-is-beneath
question: "What is beneath `search (gazette.web:101)` in the flame graph?"
options:
  - { text: "Nothing, or next to nothing: the time is on the line itself", correct: true }
  - { text: "`Cursor.execute`, from the `sqlite3` module", explanation: "`execute` is written in C, and the profiler reads Python frames. A function written in C has no frame, so its time stays on the Python line that called it." }
  - { text: "`render_template`, since building the page is the slow part", explanation: "`render_template` is called on another line of `search`, and its box is a sliver. Building the page costs little here." }
  - { text: "Flask's `dispatch_request`", explanation: "`dispatch_request` is above `search`, not beneath it. It called the view." }
explanation: "Line 101 called nothing that was written in Python. What it called is `sqlite3`, which is C, so the samples stay on the line. The profiler has told you where in your program the time goes, to the line, and cannot see further."
```

## What the profile cannot see

This is the limit of any Python profiler at a database, and it is
worth knowing where it lies.

- The time the database spends on a query is not divided up. It is
  all on the line of Python that ran the query.

- `--native` would not help here. It marks C code that has called
  back into Python, which a query does not do.

- How the database carried out the query, which index it used and
  how many rows it read, is the database's own business, and it has
  tools of its own for that.

What the profiler has said is enough to go on: the time is in
`search`, on one line, and that line talks to the database. The
next page looks at the line.
