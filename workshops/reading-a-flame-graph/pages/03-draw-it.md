---
title: Draw it
requires: [verify:flamegraph-written]
---

# Draw it

`--flamegraph` writes the profile as an interactive flame graph in a
single self-contained HTML file, with everything it needs inside it,
so it can be mailed, attached to an issue or opened years later. `-o`
names the file.

```{execute}
:id: profile-flamegraph
:session: shell
:title: Profile the renderer and write a flame graph
:wait: prompt
python -m profiling.sampling run --flamegraph -o flamegraph.html gazette/pages.py
```

The profiler's last lines say how many samples the graph holds and
where it was saved. Open it in JupyterLab's HTML viewer. It opens as
a tab beside the terminal, below `pages.py`, so the program, the
picture and this page are all in view; the terminal is the tab next
to it when you need it again.

```{command}
:id: open-flamegraph
:title: Open flamegraph.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/flamegraph.html", "factory": "HTML Viewer" }
```

```{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar and the graph appears. Nothing in the file
reaches the network: the profiler inlines everything, including the
D3 library it draws with.
```

```{verify}
:id: flamegraph-written
:label: flamegraph.html exists and holds the renderer's functions
:trigger: after:profile-flamegraph
:substrate: shell
test -s flamegraph.html && grep -q format_date flamegraph.html && grep -q render_archive flamegraph.html && echo "flamegraph.html holds format_date and render_archive" || { echo "flamegraph.html is missing or does not name the renderer's functions; run the --flamegraph command above"; exit 1; }
```
