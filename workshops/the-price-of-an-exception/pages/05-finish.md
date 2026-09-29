---
title: Finish
requires: [quiz:what-it-counts]
---

# Finish

Exception mode keeps the samples taken while a thread has an active
exception: one on its way up the stack, or one caught and being
handled in an `except` block, with everything that block calls. It
measures time under an exception, and it does not count exceptions.

That makes it a detector for one thing, a path meant to be rare that
has become common. The date parser raised nearly three hundred
thousand exceptions and the raising was a small part of the cost.
The rest was the attempts that failed and the work done after them,
and half the run turned out to be inside handlers.

None of this is an argument against exceptions or against asking
forgiveness. A `try` that succeeds is free, and an exception taken
one time in a thousand costs nothing you will ever measure. Reach
for this mode when a program that leans on exceptions is slower than
it should be, and let the share of samples say whether they are the
reason.

```{quiz}
:id: what-it-counts
question: A cache lookup is written as `try` and `except KeyError`, and the handler computes the missing value, which takes a millisecond. In exception mode the handler has 80% of the samples. What does that tell you?
options:
  - { text: "Raising `KeyError` is slow, and the lookup should test with `in` first", explanation: "The raise takes a fraction of a microsecond. Testing first would move the millisecond of computing out of the handler and leave it just as long." }
  - { text: "Most of the run is spent computing values inside the handler, so most lookups miss, and the cache is not doing its job", correct: true }
  - { text: "The program raised many more exceptions than it should", explanation: "The mode does not count exceptions. One exception with a slow handler gives the same profile as a thousand with quick ones." }
  - { text: "Nothing: time inside an `except` block is not counted", explanation: "It is counted, along with everything the block calls. That is most of what the mode finds in practice." }
explanation: "The mode measures time with an exception active, and here that time is the computing done after a miss. A handler with most of the samples means the miss is the common case, so the thing to fix is why the cache misses."
```

Next in these workshops is **Following the awaits**, which profiles a
program written with `asyncio`. Press Finish to go there.
