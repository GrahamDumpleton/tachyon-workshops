# Workers and subprocesses

Profile a program that does its work in other processes, with
Tachyon's `--subprocesses`: a job runner on a pool of four
processes, whose own profile is all waiting, and a web site under
gunicorn with three workers. What the profiler follows, the file it
writes for each process, and how to tell the files apart.

About fifteen minutes, in two JupyterLab terminals with the flame
graphs opened beside them. The fourth of the **Tachyon on real
applications** workshops; it assumes you can read a flame graph.
