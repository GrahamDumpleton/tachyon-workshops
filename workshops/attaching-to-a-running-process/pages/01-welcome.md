---
title: Welcome
requires: [verify:env-ready]
---

# Attaching to a running process

Every profile in these workshops so far was of a program that the
profiler started. That is fine at a desk, and it is not how trouble
arrives. The service that is misbehaving is already running. It has
been running for a week, it is in the state that matters, and
restarting it under a profiler would put it in another state, if
restarting it is allowed at all.

The profiler does not have to start a program to read it. It reads
a process's memory from outside, and any process will do, given its
number. Two commands work that way.

- **`dump`** takes one reading of the stacks and prints it: what
  every thread is doing at this moment.

- **`attach`** samples as `run` does, a thousand readings a second
  for as long as you say, and writes any of the formats `run`
  writes.

The program is not restarted, not changed, and not told. No code is
added to it and nothing has to be deployed. This is the feature that
people who look after services want most from a profiler.

It is also the one that most machines refuse to an ordinary user,
for a good reason, and this workshop is as much about that as about
the commands. It finds out what this machine allows and carries on
either way.

A *sample* is one reading of a program's stacks. A flame graph
draws many samples as boxes, one for each function, as wide as its
share of them, with the functions it called beneath it.

## The application

{open}`gazette/web.py` is open in the editor: the web site of the
gazette, a small newsroom, written with
[Flask](https://flask.palletsprojects.com/). It has a front page, a
page for each article, a search and a health check. When it starts
it writes the number of its process to a file, `gazette.pid`, as
many services do, so that whatever needs to find the process can.

{open}`load.py` plays the readers, sending two hundred requests a
second from four threads.

## The environment

Create the workshop's environment. It installs Flask, and makes the
`python` in the terminals Python 3.15, the one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15, with the profiler and Flask
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling, flask; from importlib.metadata import version; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling and Flask', version('flask'))"
```
