# An async service that stalls

Find what is holding up an asyncio web service with Tachyon: a
Starlette application under uvicorn whose searches slow down when
articles are being read, though a search does nothing different.
The event loop's thread in a flame graph, the tasks in an
async-aware table, a fix with a thread that does not work and why,
and one with a process pool that does.

About twenty-five minutes, in three JupyterLab terminals with the
flame graphs opened beside them. The third of the **Tachyon on real
applications** workshops; it assumes you can read a flame graph and
have met `async` and `await`.
