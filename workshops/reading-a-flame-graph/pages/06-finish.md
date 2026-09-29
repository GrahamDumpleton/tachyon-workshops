---
title: Finish
requires: [quiz:when-to-draw]
---

# Finish

The table answers "which function"; the flame graph answers "by which
path". Every box is a function on the stack at one place in one path,
its width is the share of samples that path had, its colour says the
same, and the boxes beneath it are what it called. Reading the
renderer's graph from the top found `render_archive` nearly the whole
width and a wide `format_date` beneath it that no other caller could
match, so the fix is in the caller. The collapsed stacks file is the same data as text, one line
per stack, and any flame graph tool will draw it.

```{quiz}
:id: when-to-draw
question: When does the flame graph tell you something the table does not?
options:
  - { text: "When you want exact times: the graph measures and the table estimates", explanation: "Both come from the same samples and both are estimates. Nothing here measures." }
  - { text: "When a hot function is called from several places and you need to know which caller's calls cost the time", correct: true }
  - { text: "Never: the graph is the table drawn as rectangles", explanation: "It is drawn from the same samples, but a table row adds up a function's samples from every path, and the graph keeps the paths apart." }
  - { text: "When the program has more than one thread", explanation: "The graph does have a per-thread view, but so does the table with `-a`. The graph's own advantage is the paths." }
explanation: "The table's row for a function is the sum over every path that reached it. The flame graph keeps the paths side by side, so a function called from several places shows one box per caller, each as wide as that caller's share."
```

Next in these workshops is **Down to the line**, which paints the
samples onto the source code, for when you know the file and want
the line. Press Finish to go there.
