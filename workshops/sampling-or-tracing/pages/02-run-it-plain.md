---
title: Run it plain
requires: [quiz:how-much-slower]
---

# Run it plain

Run the report with no profiler, twice, so you know its time. Its
last line says how long it took, measured by the program itself from
its first line to its last. The second run keeps that line in
`plain.txt`, for the checks on later pages to compare with.

```{execute}
:id: run-plain
:session: shell
:title: Run the report without a profiler
:wait: prompt
python gazette/report.py
```

```{execute}
:id: run-plain-again
:session: shell
:title: And again, to see the time is steady
:wait: prompt
python gazette/report.py | tail -n 1 | tee plain.txt
```

A fraction of a second, and much the same each time. How large a
fraction depends on the machine: a fifth of a second where this page
was written, and three times that on a busy shared server. So the
number to remember is your own. Everything in this workshop is
measured against the time you have just seen, not against a figure
on a page.

Now a prediction. The tracing profiler is told about every call and
return, four million times for this program, and does a little work
each time: look up the function's record, read the clock, add the
time to the caller's account. How much longer will the report take
under it?

```{quiz}
:id: how-much-slower
question: Under the tracing profiler, `cProfile`, how long do you expect this report to take, beside the time it took alone?
options:
  - { text: "About the same: profilers are designed to be cheap", explanation: "A tracing profiler cannot be cheap on a program of many small calls: it does work for every one of them." }
  - { text: "A little longer, a quarter as long again or so", explanation: "More than that. Four million notifications, each a small piece of work, come to more than the program's own work." }
  - { text: "Several times as long", correct: true }
  - { text: "A hundred times as long or more", explanation: "Not that bad: the tracer is C code and each notification is quick. Several times slower is the usual damage on call-heavy code." }
explanation: "Several times as long, on any machine: both times scale with the machine, so the ratio holds where the seconds do not. The next page measures it. The overhead is per call, so it is worst on programs like this one, made of millions of tiny calls, and mild on a program whose time is in a few long calls."
```
