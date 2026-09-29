---
title: Where C stands
requires: [quiz:who-calls-relevance, verify:native-graph]
---

# Where C stands

Look at `rank` in {open}`gazette/index.py`, and at line 58.

```python
        best = sorted(found, key=relevance)
```

`rank` does not call `relevance`. It hands it to `sorted`, and
`sorted`, in C, calls it once for every item. In the profile the
stack reads `rank`, then `relevance`, as though one called the
other, because the C function between them has no frame.

`--native` has the profiler add a box named `<native>` to the stack
wherever it passes through C code to reach a Python function.

```{quiz}
:id: who-calls-relevance
question: With `--native`, where in the flame graph of the index builder will `<native>` boxes appear?
options:
  - { text: "Beneath every line that calls a C function, so beneath `write` for `zlib.compress` as well as beneath `rank` for `sorted`", explanation: "That is what the name suggests. The profiler can mark C code only where a Python frame beyond it shows that something stands between, and `zlib.compress` calls no Python." }
  - { text: "Between `rank` and `relevance`, and anywhere else a C function calls a Python one, and not beneath `write`", correct: true }
  - { text: "Nowhere in this program, since it uses no extension modules", explanation: "Native means not written in Python, and that includes the interpreter's own built-in functions and the C parts of the standard library." }
explanation: "The profiler reads Python's frames, and finds C code by the gap it leaves between two of them. C code that calls no Python leaves no gap to find."
```

```{execute}
:id: profile-native
:session: shell
:title: Draw the index builder with native frames
:wait: prompt
python -m profiling.sampling run --native --flamegraph -o native.html gazette/index.py
```

```{command}
:id: open-native
:title: Open native.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/native.html", "factory": "HTML Viewer" }
```

````{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar.
````

Follow the widest boxes down from `main`.

- **`rank`, `<native>`, `relevance`.** The marker is `sorted`. The
  profiler does not know its name, only that the interpreter left
  Python there and came back into it.

- **`relevance`, `<native>`, `_strptime_datetime_datetime`.** A
  second one, and less expected. `datetime.strptime` is a C method,
  and what it does is call a function of the standard library's
  `_strptime` module, which is written in Python and does the
  parsing. The flame graph shows how much: it is most of the width
  of `relevance`, which is most of the width of `rank`.

- **`count_words`, `<native>`, `singular`**, further right and
  narrow. `WORD.sub` on line 40 calls `singular` for every word it
  finds.

- **`write` has nothing beneath it** but a little of `json`. The
  compression is there, in the width of `write`, as it was in the
  table. It has no marker.

The three boxes at the very top, the root and the pair above
`<module>`, are the interpreter starting the program, which is C
code running Python as well.

So `<native>` is a marker, and not a C stack. It says that C code
stood here. It does not say which C function, how deep the C calls
went, or how long was spent in them as opposed to the Python
beneath. And it appears only where there is Python beneath. The
documentation's description, frames that "indicate when Python has
called into C code", reads as more than that, and on the release
these workshops use the marker is as you see it here.

What it is good for is the question this page began with: a function
is running and nothing in your code calls it. A key function, a
callback given to a C library, a method the interpreter calls for an
operator or an attribute. With the marker the flame graph shows that
the call came through C, and from which of your lines.

```{verify}
:id: native-graph
:label: native.html holds the native marker and the index builder's functions
:trigger: after:profile-native
:substrate: shell
test -s native.html || { echo "No native.html yet: run the --native command above, which writes it"; exit 1; }
grep -q '"<native>"' native.html || { echo "native.html has no <native> frames in it; was it written with --native?"; exit 1; }
grep -q relevance native.html && echo "native.html holds <native> and relevance" || { echo "native.html does not name relevance; was the program gazette/index.py?"; exit 1; }
```
