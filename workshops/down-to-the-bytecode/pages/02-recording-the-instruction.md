---
title: Recording the instruction
requires: [verify:refused, verify:heatmap-written]
---

# Recording the instruction

Ask for the instructions along with the profiler's usual table.

```{execute}
:id: try-table
:session: shell
:title: Ask for opcodes with the table
:wait: prompt
python -m profiling.sampling run --opcodes gazette/scores.py 2>&1 | tee refused.txt
```

The profiler refuses, and the program was not run. A row of the
table is a line of a function, with no room for what is beneath
it, so `--opcodes` is accepted only with the outputs that have
somewhere to put the instructions: the heatmap, the flame graph, the
gecko and binary files, and live mode.

```{verify}
:id: refused
:label: The profiler refused opcodes with the table
:trigger: after:try-table
:substrate: shell
test -s refused.txt || { echo "No refused.txt yet: run the command above, which writes it"; exit 1; }
grep -q "opcodes is only compatible with" refused.txt && echo "The profiler refused: --opcodes is only compatible with some outputs" || { echo "refused.txt does not hold the profiler's refusal; run the command above as it is written"; exit 1; }
```

The heatmap is the one to use, since an instruction belongs to a
line and the heatmap is the profile laid over the source.

```{execute}
:id: profile-heatmap
:session: shell
:title: Record a heatmap with opcodes
:wait: prompt
python -m profiling.sampling run --opcodes --heatmap -o heatmap gazette/scores.py one-class
```

The heatmap is a directory of pages, one for each source file, and
`file_0000.html` is the file with the most samples, which is
`scores.py`.

```{command}
:id: open-heatmap
:title: Open the heatmap of scores.py in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/heatmap/file_0000.html", "factory": "HTML Viewer" }
```

````{hint}
:title: If the page has no colours or the buttons do nothing
JupyterLab does not run the scripts in an HTML file until it is
trusted. On Binder, in a codespace and in the workshops' container
the viewer trusts HTML files by default; on your own JupyterLab click
the **Trust HTML** button in the viewer's toolbar.
````

Scroll to `score`, on line 88. It is where nearly all of the samples
are, and the hottest line in it is 91, the test of a word against
the article's words, with half of the samples or so.

```{verify}
:id: heatmap-written
:label: The heatmap's page for scores.py has instructions in it
:trigger: after:profile-heatmap
:substrate: shell
test -s heatmap/file_0000.html || { echo "No heatmap/file_0000.html yet: run the --heatmap command above, which writes it"; exit 1; }
grep -q "scores.py" heatmap/file_0000.html || { echo "heatmap/file_0000.html is not the page for scores.py; was the program gazette/scores.py?"; exit 1; }
grep -q "LOAD_ATTR" heatmap/file_0000.html && echo "The page for scores.py holds LOAD_ATTR and the other instructions" || { echo "The page has no instructions in it; was the heatmap written with --opcodes?"; exit 1; }
```
