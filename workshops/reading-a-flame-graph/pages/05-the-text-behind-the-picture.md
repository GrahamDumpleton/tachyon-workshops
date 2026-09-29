---
title: The text behind the picture
requires: [verify:stacks-written]
---

# The text behind the picture

A flame graph is drawn from a list of stacks with a count against
each, and the profiler can write that list as text. `--collapsed` is
the *collapsed stacks* format that Brendan Gregg's original
`flamegraph.pl` reads and that every flame graph tool since has
accepted: one line per distinct stack, the frames joined with
semicolons from the root outwards, a space, and the number of samples
that had exactly that stack.

```{execute}
:id: profile-collapsed
:session: shell
:title: Write the profile as collapsed stacks
:wait: prompt
python -m profiling.sampling run --collapsed -o stacks.txt gazette/pages.py
```

Look at the few dozen lines, biggest first:

```{execute}
:id: sort-stacks
:session: shell
:title: The three most sampled stacks
:wait: prompt
sort -k 2 -n -r stacks.txt | head -n 3 | cut -c 1-200
```

The first line is the wide column of the graph as text: the thread
id, the interpreter's `_run_module_as_main` and `_run_code` that
started the script, the module line, `main`, `render_archive` on the
line of its comprehension, and `format_date` on its `strptime` line,
then the count, about half of all the samples the profiler kept.
Each frame is `file:function:line`. Every box in the graph is a
prefix shared by some of these lines, and its width is the sum of
their counts.

This file is the one to keep when you want the picture drawn by
something else: `flamegraph.pl stacks.txt > profile.svg`, or drop it
on speedscope. It is also the smallest useful record of a profile,
and readable with `grep` and `sort` when no browser is to hand.

```{verify}
:id: stacks-written
:label: stacks.txt has the render_archive path to format_date
:trigger: after:profile-collapsed
:substrate: shell
test -s stacks.txt && grep -q "render_archive.*format_date" stacks.txt && echo "stacks.txt holds a stack from render_archive to format_date" || { echo "stacks.txt is missing or has no render_archive to format_date stack; run the --collapsed command above"; exit 1; }
```
