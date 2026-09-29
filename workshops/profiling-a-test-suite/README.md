# Profiling a test suite

Find out where a slow test suite spends its time, with Tachyon
around pytest: a recording of the whole run, the flame graph with
the tests and the fixtures in it, the heatmap of `conftest.py`, and
three fixes to three common habits, a fixture rebuilt for every
test, a sleep where a join would do, and a file parsed once for each
case.

About fifteen minutes, in a JupyterLab terminal with the flame
graphs and the heatmap opened beside it. The fifth of the **Tachyon
on real applications** workshops; it assumes you can read a flame
graph and a heatmap, and have used pytest.
