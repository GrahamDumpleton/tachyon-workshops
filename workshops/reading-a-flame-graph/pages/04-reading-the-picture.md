---
title: Reading the picture
requires: [quiz:wider-box]
---

# Reading the picture

Read the graph from the top. The line at the top names the program's
root, and the first wide box beneath it spans the whole width: every
sample had it on the stack. Beneath each box are the functions it
called, so a column of boxes read downwards is a call path, outermost
call first, and the depth of the graph is how deep the program's calls
went. The classic flame graph is drawn the other way up, with the root
at the bottom and the flames rising; Tachyon draws the root at the
top, which some tools call an icicle graph. It is the same picture.

Width is the fact. A box's width is the share of all samples in which
that function was on the stack at that place in the path, which is
its cumulative time along that path. That is what the table's
cumulative column could not do: `format_date` appears as a box in
several places, once beneath each caller, and each box is as wide as
that caller's share of its time.

Colour repeats the same fact so that it can be seen at a glance. A
box is coloured by its share of all the samples, on the scale in the
Heat Map section at the foot of the sidebar: the hottest colour for
three fifths of the samples or more, cooling through orange and
yellow to pale blue for a box with under one percent.

Follow the hot colour down. `_run_code`, `<module>` and `main` are
the full width, since everything runs inside them. Beneath `main`,
`render_archive` is nearly the whole width, and the slivers at the
right-hand edge are `render_index`, `render_sections` and
`render_authors`. Beneath `render_archive` sits `format_date`, as two
boxes side by side, one for each of its two lines, since a box, like
a row of the table, is a line of a function; the wider is line 19,
the `strptime` call, with the standard library's `_strptime` frames
beneath it. These are the calls `render_archive` makes directly, from
the comprehension that sorts articles into days. At the right of
`render_archive`'s row is a narrow `summary`, with its own thin
`format_date` beneath. That is the answer the table could not give,
and it says where the fix goes: not in `format_date`, which does what
it is asked, but in `render_archive`, which asks half a million times
for what it could work out once.

Now the interactions, each a moment:

- **Hover** over any box for a tooltip with the function, the file
  and line, the total time and self time, its percentage of the
  samples, and a few lines of the source around the line that was
  executing.

- **Click** a box to zoom in, so that box becomes the full width and
  what it called is readable. Click the narrow `summary` box at the
  right of `render_archive`'s row. The house button at the top right
  resets the zoom.

- **Search**, in the field at the top, for `format_date` and every
  box for that function is picked out wherever it is in the graph.
  Search takes `pages.py:19` too, for one line.

- **The sidebar** on the left has the summary. View Mode switches
  the labels between module names and file paths, and switches to the
  *inverted* graph, which starts from the functions that were running
  and hangs their callers beneath them, the other way to ask "who
  called this". Profile Summary has the total samples, the duration,
  the rate and the sampling efficiency, which is the error rate the
  other way up. Hotspots lists the hottest functions, which are the
  table's top rows. Runtime Stats says how often the GIL was held or
  released and how often the garbage collector was running, and Heat
  Map is the key to the colours.

- The other buttons at the top right **export** the graph as SVG,
  open the profiler's documentation, and switch the **theme**.

```{quiz}
:id: wider-box
question: In the graph, `format_date` appears directly beneath `render_archive` and again beneath `summary`. Which is wider, and what does that mean?
options:
  - { text: "Beneath `summary`: rendering the summaries is the cost", explanation: "Look again. The box beneath `summary` is thin, a few percent of the width at most." }
  - { text: "They are the same width: `format_date` costs the same wherever it is called from", explanation: "The cost per call is the same; the width is the number of calls times that cost, and the two callers make very different numbers of calls." }
  - { text: "Directly beneath `render_archive`: most of `format_date`'s time is spent on the calls from the day-sorting comprehension, so the fix belongs in `render_archive`", correct: true }
  - { text: "Neither: the flame graph shows only direct time, and `format_date` has almost none", explanation: "A box's width is cumulative time along its path, which is why callers are wide even when they do no work themselves." }
explanation: "The wide `format_date` boxes sit directly beneath `render_archive`: the comprehension that finds each day's articles calls it for every article, for every day. Group the articles by day once and those boxes disappear."
```
