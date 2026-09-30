---
title: Replay
requires: [verify:replayed, quiz:what-replay-runs]
---

# Replay

`replay` takes a recording and an output format, the same formats
and the same options as `run`, and writes what `run` would have
written. With no format it prints the table.

```{execute}
:id: replay-table
:session: shell
:title: Replay the recording as a table of five rows
:wait: prompt
python -m profiling.sampling replay -l 5 --no-summary report.bin
```

The report did not print, and the command took a fraction of a
second where the program takes a second and a half: nothing ran
except the profiler reading its file. The first lines say how many
samples it is replaying, the interval between them and the
compression, and then the table is the one you know, `count_words`
on lines 36 and 34 at the top.

Now the same recording as a flame graph, the picture of every call
path with the width of each box its share of the samples.

```{execute}
:id: replay-flamegraph
:session: shell
:title: Replay the recording as a flame graph
:wait: prompt
python -m profiling.sampling replay --flamegraph -o flamegraph.html report.bin
```

```{file-open}
:id: open-flamegraph
:title: Open flamegraph.html in the HTML viewer
:path: flamegraph.html
:factory: HTML Viewer
:area: desk
```

It opens beside `gazette/report.py`, above the terminal. The graph
has the root at the top and one column beneath it, through `main` to
`count_words`, which is split into two boxes for its two busy lines.
The fourth of these workshops reads a flame graph in full.

And as a heatmap, the source code with the samples painted on each
line.

```{execute}
:id: replay-heatmap
:session: shell
:title: Replay the recording as a heatmap
:wait: prompt
python -m profiling.sampling replay --heatmap -o heatmap report.bin
```

```{file-open}
:id: open-heatmap
:title: Open the heatmap page for report.py
:path: heatmap/file_0000.html
:factory: HTML Viewer
:area: desk
```

Scroll to `count_words`: line 36 is red and line 34 is orange, and
the fifth of these workshops reads the rest. Three views of one run,
which therefore agree with each other exactly, sample for sample.
Three runs of the program never quite do.

```{hint}
:title: If a picture is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted. On Binder, in a codespace and in the workshops' container
the viewer trusts HTML files by default; on your own JupyterLab click
the **Trust HTML** button in the viewer's toolbar.
```

```{quiz}
:id: what-replay-runs
question: What did the three `replay` commands run?
options:
  - { text: "The report, three more times, with the profiler attached", explanation: "The report never printed. `replay` was given a recording, not a program." }
  - { text: "Only the profiler, reading the samples it recorded earlier", correct: true }
  - { text: "The report once, with the three outputs written from that run", explanation: "No program ran at all. The samples came from `report.bin`, recorded on the page before." }
  - { text: "Nothing: the three files were already inside `report.bin`", explanation: "The recording holds samples, not pictures. Each `replay` built its output from them." }
explanation: "`replay` reads the recorded samples and builds the output from them, so the program is not needed, and nor is the machine it ran on."
```

```{verify}
:id: replayed
:label: The recording has been replayed as a flame graph and a heatmap
:trigger: after:replay-heatmap
:substrate: shell
test -s flamegraph.html && grep -q count_words flamegraph.html && test -s heatmap/index.html && echo "flamegraph.html and heatmap/ were both made from report.bin" || { echo "flamegraph.html or heatmap/index.html is missing; run the two replay commands above"; exit 1; }
```
