---
title: The diagnosis
requires: [quiz:which-fix]
---

# The diagnosis

Two tables of one program, and the rule for reading them together is
short.

- A function that is **high in wall-clock time and low or absent in
  CPU time** is waiting: for the network, a disk, a lock, a sleep.
  Making its code quicker does nothing, because its code is not what
  is taking the time. The fix is to wait less, by doing several
  waits at once with threads or `asyncio`, by keeping connections
  open, by caching the answer, or by not asking.

- A function that is **high in both** is working. The processor is
  busy in it, and the fix is the ordinary one: a better algorithm, a
  better data structure, less work.

The feed reader has one of each. The read from the socket is the
first kind, four seconds of waiting that twenty requests made one
after another add up to. Made at the same time, the twenty would
take little longer than one. `same_story` is the second kind: `merge`
compares every new item with every item it has kept, more than a
million comparisons, and an index of the stories already seen would
replace them all.

Which to fix first is what the wall-clock table is for: whichever
has the larger share of it. Here the waiting is most of the run and
the comparison a small part, on any machine, so the requests come
first. **Following the awaits**, later in these workshops, fetches
the same feeds with `asyncio` and profiles that.

The modes do not need two runs on the same footing to be useful. If
you only want to know where the processor's time goes, in a program
that also sleeps or polls, CPU mode alone gives a table with the
waiting already removed.

```{quiz}
:id: which-fix
question: A report generator takes forty seconds. In wall-clock mode `run_query`, which sends SQL to a database on another machine, has 90% of the samples. In CPU mode it has 2%. What should be tried first?
options:
  - { text: "Rewrite `run_query` to build its SQL strings more efficiently", explanation: "Its code is on the processor for 2% of the profile. However quick it is made, the wait for the database remains." }
  - { text: "Move the report generator to a machine with a faster processor", explanation: "The processor is idle for most of the forty seconds. A faster one would be idle sooner." }
  - { text: "Look at what is being waited for: the queries, how many there are, and whether they can be fewer, quicker or made at once", correct: true }
  - { text: "Profile again at a higher sampling rate, since the two modes disagree", explanation: "They do not disagree. They measure different things, and the difference between them is the finding." }
explanation: "High in wall-clock time and nearly absent in CPU time means waiting, here for the database. The time is in the queries, so that is where to look: fewer of them, an index on the database's side, or several at once."
```
