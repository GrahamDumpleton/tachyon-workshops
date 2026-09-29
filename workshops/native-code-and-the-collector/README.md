# Native code and the collector

See two things the Python stack cannot show, with the markers
Tachyon adds to it: the `<native>` marker, on a search index whose
sort calls back into Python from C, and the `<GC>` marker, on a graph
of cross-references that gives the garbage collector work to do.
What each marks, what it leaves out, and how far to trust the counts.

About twenty minutes, in a JupyterLab terminal with the flame graph
opened beside it. The eleventh of the **Profiling with Tachyon**
workshops; it assumes you can read the profiler's table and a flame
graph.
