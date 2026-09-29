---
title: Finish
requires: [quiz:which-program]
---

# Finish

Three questions to ask of a profile of a program with threads, and
what answers each.

- **Which threads am I looking at?** By default, the main thread
  only, which in a program that hands its work to threads is a
  thread that waits. `-a` samples every thread, and its sample counts
  are per thread, so they add up to several times the length of the
  run.

- **What was each thread doing?** The flame graph of an `-a` profile
  has a thread filter in its sidebar, and runtime statistics that
  say how much of the time the thread held the GIL, had released it,
  or was waiting for it. A thread that mostly waits for the GIL is
  in a queue.

- **Is the work Python, or C without the GIL?** `--mode gil` keeps
  the samples of the thread holding the GIL and `--mode cpu` those
  of threads on a processor. High in both is Python, and threads
  take turns. High in CPU and low in GIL is C with the lock
  released, and threads run at once.

```{quiz}
:id: which-program
question: A service resizes images on a pool of eight threads. Profiled with `-a`, the CPU mode and GIL mode tables look alike, with `resize` at nine tenths of the samples in each and about one sample kept for every millisecond of the run. What does that say?
options:
  - { text: "`resize` runs in C with the GIL released, so the eight threads are working at once", explanation: "Then GIL mode would have almost no samples of it, and CPU mode would have up to eight for every millisecond." }
  - { text: "`resize` holds the GIL while it works, so the eight threads take turns and the pool does the work of one thread", correct: true }
  - { text: "The threads are waiting for the network", explanation: "A waiting thread is neither on a processor nor holding the GIL, and would be missing from both tables." }
  - { text: "The profiler lost most of the samples", explanation: "It kept what there was to keep. One thread at a time was running, so there was one sample to keep at each instant." }
explanation: "High in both modes is work done while holding the GIL. One thread at a time can do it, so both modes have about one sample for each millisecond, and the fix is processes or a library that releases the lock."
```

Next in these workshops is **The price of an exception**, on the
last of the four modes. Press Finish to go there.
