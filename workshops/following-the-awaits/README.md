# Following the awaits

Profile a program written with `asyncio`, a crawler that fetches
twenty feeds at once, first as the event loop's stack and then with
Tachyon's async-aware profiling, which follows the tasks: what each
view shows, what the tasks that are not running are waiting for, and
which options cannot be combined with it.

About fifteen minutes, in two JupyterLab terminals, one for a local
feed server and one for the profiler, with the flame graphs opened
beside them. The tenth of the **Profiling with Tachyon** workshops;
it assumes you can read the profiler's table and a flame graph, and
have written or read a little `asyncio`.
