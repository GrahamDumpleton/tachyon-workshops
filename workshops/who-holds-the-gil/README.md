# Who holds the GIL?

Profile a program with several threads using Tachyon: why the default
profile shows only a thread that is waiting, what `-a` adds, the flame
graph's view of each thread, and GIL mode, on four threads of Python
that take as long as one and four threads of hashing that do not.

About twenty minutes, in a JupyterLab terminal with the flame graphs
open in tabs beside it. The eighth of the **Profiling with Tachyon**
workshops; it assumes you have run the profiler once and can read its
table, and says what a flame graph is in a sentence.
