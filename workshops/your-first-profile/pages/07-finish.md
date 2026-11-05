---
title: Finish
requires: [quiz:what-time-is]
---

# Finish

You ran a program under a sampling profiler and read what it said.
The profiler looked at the program's call stack a thousand times a
second, from outside, without the program running a line of profiler
code or slowing down, and the table is the tally of what it saw: how
often each line of each function was the one running, and how often
it was somewhere on the stack. Time is that tally multiplied by the
interval between looks. The report's `count_words` was on four
samples in five, on two lines that each walk a long list too often.

One last question, because it is the one idea everything else in
these workshops builds on.

```{quiz}
:id: what-time-is
question: Suppose the table says `count_words` took 1.261 seconds. Where does that number come from?
options:
  - { text: "The profiler timed each call to `count_words` and added the times up", explanation: "That is what a tracing profiler does. Tachyon never times a call and does not know how many there were." }
  - { text: "The program reported it", explanation: "The program never knew it was being profiled. Nothing in `report.py` talks to the profiler." }
  - { text: "The profiler saw `count_words` running in 1,261 samples, taken a millisecond apart", correct: true }
  - { text: "The profiler measured the CPU time of the process and divided it among the functions", explanation: "Closer, but no: nothing is measured and divided. Each sample is attributed to the one line that was running when it was taken, and the counts are the answer." }
explanation: "1,261 samples, one every millisecond, is 1.261 seconds. Every number in the table is a count of samples, or a count multiplied by the interval."
```

Next in these workshops is **Sampling or tracing?**, which profiles the
same report with the tracing profiler Python has always had, `cProfile`,
now also called `profiling.tracing`, and asks what each kind of profiler
is for. Press Finish to go there.
