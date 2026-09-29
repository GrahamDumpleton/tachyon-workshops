---
title: A snapshot of another process
requires: [verify:probe-ran, quiz:who-may-read]
---

# A snapshot of another process

The `run` command you have used starts the program itself and profiles
it. Two other commands work on a process that is already running:
`attach` profiles it for a while, and `dump` takes one sample and
prints it as a traceback. That is the feature production people want,
a look inside a process that is misbehaving right now without
restarting it, and it is also where the operating system has a say.

Reading another process's memory is what a debugger does, so the
kernel guards it. On Linux the rule comes from the Yama security
module and its `ptrace_scope` setting. At its usual value, 1, which
Ubuntu and most desktop distributions ship, a process may read only
its own *descendants*: the processes it started. At 0 it may read any
process of the same user. Root, or a process granted the
`CAP_SYS_PTRACE` capability, may read anything. That is why `run`
works everywhere: the profiler starts the program, so the program is
its child, and a parent may always read its child. `attach` and
`dump` are aimed at a process the profiler did not start, and whether
they are allowed depends on the setting, which an administrator
controls. These workshops never change it and never use `sudo`.

So first find out what this machine allows. The step below starts a
short-lived Python in the background from the terminal's shell, so it
is the shell's child and not the profiler's, and asks the profiler to
dump it. The answer, `yes` or `no`, is stored as a variable for the
rest of the page.

```{execute-capture}
:id: probe-attach
:title: Find out whether the profiler may read a process it did not start
:capture: can_attach
python -c "import time; time.sleep(5)" & pid=$!; sleep 0.5; if python -m profiling.sampling dump $pid >/dev/null 2>&1; then echo yes; else echo no; fi; kill $pid; wait $pid 2>/dev/null; true
```

```{verify}
:id: probe-ran
:label: The probe has answered
:trigger: after:probe-attach
:substrate: shell
test -n "$CAN_ATTACH" && echo "This machine answers: $CAN_ATTACH"
```

````{when} can_attach == "yes"
On this machine the answer is **yes**, so the profiler may read
another process of your own. That is so inside a container whose
kernel has no Yama module, which is the case for Docker Desktop, and
on a Linux with `ptrace_scope` set to 0. Take a snapshot for real.
Start the report in the background, wait half a second for it to be
busy, and dump its stack.

```{execute}
:id: dump-report
:session: shell
:title: Dump the stack of the running report
:wait: prompt
python gazette/report.py > /dev/null & sleep 0.5; python -m profiling.sampling dump $!; wait
```

Read it from the top. The header names the process and the thread,
says it is the main thread, that it holds the GIL and is on the CPU,
and that the most recent call is last, as a traceback is. Then the
frames: the script's last line calling `main`, `main` calling
`count_words`, and `count_words` on its line 36, the dictionary
comprehension, which is where the first workshop found the time. One
sample, read as a story. `dump --all-threads` does the same for every
thread, and is how to see what a hung program is waiting on.
````

````{when} can_attach == "no"
On this machine the answer is **no**, which is the usual answer on a
Linux desktop or server: `ptrace_scope` is 1, the report would be the
shell's child and not the profiler's, and the kernel refuses the read
with a permission error. Nothing is wrong with the profiler or the
program. The same command on a machine that allows it prints the
following, which is shipped as {open}`dump-example.txt` so you can
read it here:

```
Stack dump for PID 16, thread 16 (main thread, has GIL, on CPU; most recent call last):
  File "gazette/report.py", line 69, in <module>
    main(*sys.argv[1:])
  File "gazette/report.py", line 62, in main
    counts = count_words(articles)
  File "gazette/report.py", line 36, in count_words
    return {word: words.count(word) for word in unique}
```

The header names the process and the thread, says it is the main
thread, that it holds the GIL and is on the CPU, and that the most
recent call is last, as a traceback is. Then the frames, ending on
line 36 of `count_words`, where the first workshop found the time.
One sample, read as a story.

What to do about the refusal is an administrator's decision, and the
sixth workshop of **Tachyon on real applications** goes through the
options: `ptrace_scope` 0 for a machine used for profiling, the
capability on a dedicated profiler binary, or, with no change at all,
starting the service under `run` in the first place so that the
profiler is its parent. Everything else in these workshops uses `run`,
and works here.
````

```{quiz}
:id: who-may-read
question: On a Linux machine with the default `ptrace_scope` of 1, which processes may the profiler read?
options:
  - { text: "Any process of the same user", explanation: "That is `ptrace_scope` 0. At 1 the same user is not enough." }
  - { text: "Only processes it started itself, its descendants", correct: true }
  - { text: "None: reading another process always needs root", explanation: "Root can read anything, but a parent may always read its child, which is why `run` needs no privilege at all." }
  - { text: "Any Python process, since the profiler is part of Python", explanation: "The kernel does not know or care that the reader is Python. The rule is about the relationship between the two processes." }
explanation: "At the usual setting a process may read its descendants and nothing else, so `run`, where the profiler is the parent, always works, and `attach` and `dump` work only where the setting is relaxed or the profiler has the capability."
```
