---
title: Welcome
requires: [verify:env-ready]
---

# Did the fix work?

You profiled a program, found the slow part and changed it. Two
questions follow, and the stopwatch answers only half of the first.
Did the program get quicker, and in the place you meant? And did
the change make anything else slower?

Looking at a profile from before and one from after, side by side,
is how most people answer them, and it is hard on the eyes. The
profiler can do the comparison: given a profile recorded earlier, the
*baseline*, it draws the flame graph of a new profile with every box
coloured by how it compares with the same function in the baseline.
That is a *differential flame graph*.

The colours are easy to misread, and this workshop spends as long on
what they are measured against as on what they are.

## The program

{open}`gazette/report.py` is open in the editor. It prints a report
over the gazette's articles in three parts. `count_words` counts the
words, over all and for each section. `hardest` gives every article
a score for how hard it is to read, from the length of its sentences
and the syllables in its words, which `reading_ease` and `syllables`
work out. `render` lays the report out.

`count_words` has a mistake in it that an earlier workshop found
with the heatmap: it keeps the entries it has seen in a list, `seen`,
and looks through the list for every word. You will fix that, and
then make a second change to `hardest`, comparing profiles at each
step.

## The environment

Create the workshop's environment, which installs nothing and makes
the `python` in the terminal Python 3.15, the one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15 and has the profiler
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling')"
```
