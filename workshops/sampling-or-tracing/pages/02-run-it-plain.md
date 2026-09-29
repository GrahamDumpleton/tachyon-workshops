---
title: Run it plain
requires: [quiz:how-much-slower]
---

# Run it plain

Run the report with no profiler, twice, so you know its time. Its
last line says how long it took, measured by the program itself from
its first line to its last.

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
python gazette/report.py | tail -n 1
```

About a fifth of a second, the same each time. Now a prediction. The
tracing profiler is told about every call and return, four million
times for this program, and does a little work each time: look up the
function's record, read the clock, add the time to the caller's
account. How much longer will the report take under it?

```{quiz}
:id: how-much-slower
question: Under the tracing profiler, `cProfile`, how long do you expect this report to take?
options:
  - { text: "About the same, a fifth of a second: profilers are designed to be cheap", explanation: "A tracing profiler cannot be cheap on a program of many small calls: it does work for every one of them." }
  - { text: "A little longer, a quarter of a second or so", explanation: "More than that. Four million calls at a fraction of a microsecond each is more than the program's own work." }
  - { text: "Several times longer, most of a second", correct: true }
  - { text: "A minute or more", explanation: "Not that bad: the tracer is C code and each notification costs a fraction of a microsecond. Several times slower is the usual damage on call-heavy code." }
explanation: "About four times longer, on most machines. The next page measures it. The overhead is per call, so it is worst on programs like this one, made of millions of tiny calls, and mild on a program whose time is in a few long calls."
```
