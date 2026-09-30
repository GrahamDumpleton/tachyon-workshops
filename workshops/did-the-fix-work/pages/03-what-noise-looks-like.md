---
title: What noise looks like
requires: [quiz:two-runs, verify:noise-graph]
---

# What noise looks like

Before comparing the program with a changed one, compare it with
itself. Sampling gives different counts every run, so two profiles
of the same program differ a little, and it is worth knowing what
"a little" looks like before trusting a difference.

`--diff-flamegraph` takes the baseline to compare with, and the
profiler runs the program, samples it, and draws the comparison.

```{quiz}
:id: two-runs
question: The same program is profiled twice and the second profile is drawn compared with the first. What will the differential flame graph look like?
options:
  - { text: "Every box grey, since nothing changed", explanation: "Nothing changed in the program. The samples are not the same ones, though, and a function with very few samples can double or vanish by chance." }
  - { text: "The wide boxes grey, and some narrow ones in strong colours", correct: true }
  - { text: "Every box coloured, since no two runs are alike", explanation: "A function with thousands of samples changes by a percent or so between runs, which is too little to colour." }
explanation: "A box is coloured by the change in its direct samples in proportion to what it had. Seventeen thousand samples that become seventeen thousand and fifty are grey. One sample that becomes none is a change of a hundred percent."
```

```{execute}
:id: profile-noise
:session: shell
:title: Compare the program with itself
:wait: prompt
python -m profiling.sampling run -r 10khz --diff-flamegraph baseline.bin -o noise.html gazette/report.py
```

```{file-open}
:id: open-noise
:title: Open noise.html in the HTML viewer
:path: noise.html
:factory: HTML Viewer
:area: desk
```

````{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar.
````

The shape is the flame graph of the new profile: widths are the new
run's samples. The colour of each box is the comparison.

- **Grey** is little or no change.
- **Blue** is less time than in the baseline, darker for a bigger
  change.
- **Red** is more time, darker for a bigger change.
- **Purple** is a function that was not in the baseline at all.

`count_words` is nearly the whole width, and grey. Above it, `main`
and the boxes over it are likely to be coloured, and strongly. They
are the noise. Hold the mouse over one and read the tooltip, which
has the box's direct time in the baseline and now. For `main` both
are a millisecond or less: a handful of samples caught it between
calls in one run and fewer, or more, in the other.

Two things to take from this, for every differential flame graph.

- **The colour is about direct time**, the samples in which the
  function itself was running, and not the time of what it called.
  `main` is on the stack for the whole run and has next to no time
  of its own.

- **Colour without width means nothing.** A strongly coloured box
  that is narrow, or that is wide only because of what is beneath
  it, has few samples of its own, and a few samples either way is
  chance. Look for colour on boxes that are wide at the bottom of
  their stack.

```{verify}
:id: noise-graph
:label: noise.html compares the program with its baseline
:trigger: after:profile-noise
:substrate: shell
test -s noise.html || { echo "No noise.html yet: run the --diff-flamegraph command above, which writes it"; exit 1; }
grep -q "baseline_samples" noise.html || { echo "noise.html is not a differential flame graph; was it written with --diff-flamegraph baseline.bin?"; exit 1; }
grep -q count_words noise.html && echo "noise.html is a comparison with the baseline, and holds count_words" || { echo "noise.html does not name count_words; was the program gazette/report.py?"; exit 1; }
```
