---
title: Which one, when
requires: [quiz:which-tool]
---

# Which one, when

Two profilers, two trades. The tracer knows everything and the program
pays for the knowledge; the sampler knows what it saw and the program
pays nothing. The documentation for the sampling profiler ends with
advice on which to use, and it comes down to three cases.

**Reach for the tracer** when the program runs for less than a second
or so, since a sampler gets too few glances at it to say much; when
you need exact call counts, to prove a function is called once per
request and not once per item, say; and when the cost is in a few
calls that each take a while, so the per-call toll is small. It is
also the one to use when the profile must be reproducible run to run,
since it counts rather than samples.

**Reach for the sampler** when the program runs for a while, minutes
or hours or forever, as a service does; when it must not slow down,
because it is in production or because the slowdown would change the
answer; when it is made of many small calls, which is exactly when the
tracer's toll is highest and its distortion worst, since the small
functions are charged proportionally more; and when you cannot or
would rather not restart it, which the next of these workshops takes
up.

**Reach for neither** when the question is whether one way of writing
a line is a few percent faster than another. That is a
micro-benchmark, and `timeit` runs the line millions of times and
reports the best of several rounds, which no profiler's noise can
match.

The distortion deserves a sentence, because it is the subtle one.
The tracer's toll is per call, so a program's cheap, frequently called
functions carry more of it than its expensive, rarely called ones, and
the profile shifts toward the cheap ones: `tokenise` and `normalise`
look relatively costlier under the tracer than they are. The sampler
has no per-call toll, so what it shows is in proportion.

```{quiz}
:id: which-tool
question: A web service handles requests a little slower than it did last month. Nobody knows why. Which profiler, and why?
options:
  - { text: "The tracer, because a service is a long-running program and the tracer sees everything", explanation: "Long-running is the sampler's case. The tracer would slow every request several times over, and the profile it gave would be of a service that had been slowed down." }
  - { text: "`timeit`, on each request handler in turn", explanation: "`timeit` compares two ways of writing a few lines. It cannot tell you where a service spends its time." }
  - { text: "The sampler, because it costs the service nothing and a service runs long enough to give plenty of samples", correct: true }
  - { text: "Neither: profilers are for scripts, and services need logging", explanation: "Logging says what happened; a profile says where the time went. The sampler was built for exactly this case." }
explanation: "A running service is the sampling profiler's home ground: it runs long enough for tens of thousands of samples, and the profiler's cost to it is nothing, so the profile is of the service as it really runs."
```
