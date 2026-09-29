---
title: Finish
requires: [quiz:which-view]
---

# Finish

The heatmap is the profile painted onto the source. Its index groups
the files into your own, the standard library's and installed
packages', and each file's page puts two numbers beside every line:
self, the samples in which the line was running, and total, the
samples in which it was on the stack. Colour by self to find the
line that does the work and by total to find the lines that lead to
it, and hide the lines with no samples to see only what ran. The
colour compares the lines of one file with each other, so read the
number before believing the red.

It found the slow line of a twenty line function at a glance, and
after the fix it showed the same function with the time shared out
and a tenth of the samples.

Two heatmaps in two tabs are a comparison made by eye. **Did the fix
work?**, later in these workshops, compares two profiles properly,
in one picture that shows what grew and what shrank.

```{quiz}
:id: which-view
question: A colleague says the nightly report has become slow and that the time is somewhere in `billing/invoices.py`, a file of nine hundred lines. Which view do you ask the profiler for first?
options:
  - { text: "The heatmap, since the file is known and the question is which of its lines", correct: true }
  - { text: "The flame graph, since it is the only view that shows where the time goes", explanation: "It would get there, by way of the path. With the file already known the heatmap is the shorter route, and the flame graph is for when you know the symptom and not the place." }
  - { text: "The table sorted by cumulative time", explanation: "Its rows are lines too, but it shows fifteen of them with line numbers to look up. The heatmap shows all nine hundred lines with the hot ones coloured." }
  - { text: "None of them, since a sampling profiler cannot see single lines", explanation: "Every sample records the line each function on the stack had reached, which is what the heatmap is drawn from." }
explanation: "Reach for the heatmap when you know the file and want the line, and for the flame graph when you know the program is slow and want the path that made it so."
```

Next in these workshops is **Record now, look later**, which records
a profile once and turns it into a table, a flame graph and a heatmap
afterwards. Press Finish to go there.
