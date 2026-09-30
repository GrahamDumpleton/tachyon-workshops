---
title: The hot line
requires: [quiz:total-not-self]
---

# The hot line

The profiler numbers the pages from the file with the most samples,
so `file_0000.html` is `report.py`. Open it.

```{file-open}
:id: open-report-page
:title: Open the heatmap page for report.py
:path: heatmap/file_0000.html
:factory: HTML Viewer
:area: desk
```

This is your program, with two columns of numbers in front of the
code. **Self** is the number of samples in which the line was the one
running. **Total** is the number in which the line was on the stack,
running or waiting for something it had called. They are the table's
direct and cumulative counts, one line at a time. A line with no
numbers and no colour was never seen by the profiler.

Scroll down to `count_words`. Most of its lines are pale blue, with a
handful of samples each. Line 40, `if entry not in seen:`, is red,
and has nearly every sample the profiler took. That is the answer,
and it took no reading of numbers to find: the strip down the
right-hand edge of the page is a map of the whole file, and the one
red mark on it is this line. The search of the list is the cost, as
the quiz on the second page said. The line below it, which appends to
the list, has no samples at all.

The colour is relative. The hottest line in the file is red and the
others are coloured by how they compare with it, along the scale
shown at the top beside **Intensity**. Red says "the most in this
file", and the number beside it says how much that is.

The cards above the code add the file up: the self samples in the
file, the cumulative count, the number of lines that were hit, and
the largest self and total counts on any one line.

## Self time and total time

The page opens coloured by self time, which finds the line doing the
work. Click the **Self Time / Total Time** switch at the top right to
colour by the Total column instead, then scroll to the end of the
file. Line 77, `counts, sections = count_words(articles)` in `main`,
is now as red as line 40, and so is line 85, which calls `main`. Look
at their numbers: almost nothing under Self, and nearly every sample
under Total. They did none of the work and were on the stack while
all of it was done. Self time finds where the time is spent, and
total time finds the way there.

## Only the lines that ran

Click the **Show All / Hot Only** switch beside it. Every line
without a sample is hidden, and what is left is the program as the
profiler saw it, fewer than twenty lines of eighty five, with the path from
the last line of the file through `main` to the loop in
`count_words`. On a file of two thousand lines this is the quickest
way to the few that matter. Click both switches again to put the page
back.

## Who called this

At the right-hand end of every line with samples is a small arrow
pointing up, and on lines that call something, a second arrow
pointing down. Hold the mouse over the up arrow on line 40: it names
the caller of the function the line is in, `main`, and the number of
samples that came that way. The down arrow on line 77 names what that
line called, `count_words`. In a browser, clicking an arrow goes to
the line it names, in whichever file that is. In JupyterLab's viewer
the arrows can only be read, for the reason the last page's hint
gave.

```{quiz}
:id: total-not-self
question: Line 77, `counts, sections = count_words(articles)`, has almost no self samples and nearly all the total samples. What does that say?
options:
  - { text: "The line is slow, and the fix belongs there", explanation: "The line does nothing but make a call. It is red in total time because what it called is slow." }
  - { text: "The line was on the stack, waiting, while something it called did the work", correct: true }
  - { text: "The profiler lost most of the samples for that line", explanation: "Nothing was lost. Self and total count different things: running, and being anywhere on the stack." }
  - { text: "The line ran thousands of times", explanation: "It ran once. The profiler counts how often it saw a line on the stack, which says how long the line was there and not how many times it ran." }
explanation: "Total counts every sample with the line anywhere on the stack. A line that calls a slow function is on the stack for as long as the function takes, so it is hot in total and cold in self."
```
