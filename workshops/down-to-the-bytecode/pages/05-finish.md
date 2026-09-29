---
title: Finish
requires: [quiz:when-to-use]
---

# Finish

`--opcodes` adds one fact to every sample: the bytecode instruction
the interpreter was executing.

- **Where it is shown.** In the heatmap, as a panel under each
  line. In the flame graph, in the tooltip of a box. In the gecko file as markers, in the binary
  file for `replay`, and in live mode as a panel of its own. Not in
  the table, and the profiler says so.

- **What a name says.** `LOAD_ATTR_INSTANCE_VALUE (LOAD_ATTR)` is
  the general instruction in brackets and what the interpreter made
  of it in front. The name is what the interpreter chose, from what
  it saw there.

- **What the samples say.** How long the program spends on that
  instruction, whether or not the choice suits the values that
  arrive. One function given eight classes kept every name and
  took a third longer.

Keep it for the last step. A profile by function finds the part of
the program that matters, a profile by line finds the loop, and
only then, if the loop is already as simple as it can be and still
too slow, is the instruction the thing to look at.

```{quiz}
:id: when-to-use
question: A nightly job takes two hours, up from twenty minutes a month ago. Nobody knows where the time goes. Which profile should be made first?
options:
  - { text: "A heatmap with `--opcodes`, since it has the most detail", explanation: "Detail about every instruction of a program is no help until you know which part of the program to look at." }
  - { text: "The table or a flame graph, to find which functions have the time, and go further down only in those", correct: true }
  - { text: "None: a job that slowed down sixfold must have lost its specialisation, so the classes should be merged", explanation: "Specialisation is worth tens of percent in a tight loop. A sixfold change is nearly always the data or the algorithm." }
explanation: "Work from the top. Instructions are the finest view the profiler has, and the last to need."
```

Next in these workshops is **Did the fix work?**, which compares
two profiles of one program, before a change and after. Press
Finish to go there.
