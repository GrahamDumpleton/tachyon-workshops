---
title: Where it is refused
requires: [quiz:which-arrangement]
---

# Where it is refused

Sooner or later you will want a profile of a service on a machine
that says no. The profiler's own message offers three ways round,
and they are not equal. Each is a decision about the machine's
security, to be made by whoever answers for the machine, ahead of
the day it is needed.

## Changing who may read

- **Run the profiler as root.** It works, and it is the bluntest
  answer: the whole of Python, and whatever the profiler imports,
  runs with every privilege, for the sake of one permission.

- **Set `ptrace_scope` to 0.** Every process may then read every
  other process of the same user, for good, and not the profiler
  alone. That undoes a protection the distribution chose to have. It
  is reasonable on a machine that exists for profiling and
  debugging, and hard to defend on one that holds secrets.

- **Give one program the capability.** `CAP_SYS_PTRACE` can be
  granted to a particular copy of the Python interpreter, kept for
  profiling and runnable only by the people who profile. It is the
  narrowest of the three, and it still makes a program that can read
  any process on the machine.

- **In a container**, the same choices are made when the container
  is started, by whoever starts it.

None of these is done in these workshops, and none should be done
on a shared machine because a message suggested it.

## Changing nothing

There are two arrangements that need no permission at all, because
they keep the program a descendant of the profiler.

- **Start the service under `run`.** A service that is started as
  `python -m profiling.sampling run ...` can be sampled from its
  first moment. With `-d` the profiler stops the service when the
  time is up, so this suits a profile taken on purpose, a release
  tried under load before it goes out, more than a service left
  running.

- **Reproduce it where you may.** A service that misbehaves in
  production, started again on a machine of your own with the same
  requests sent to it, can be profiled any way you like. The
  recording can be made on one machine and read on another, which
  is the subject of the next of these workshops.

```{quiz}
:id: which-arrangement
question: A team wants to be able to profile its services in production when something goes wrong, on Linux machines with `ptrace_scope` at 1. Which arrangement gives them that with the least exposure?
options:
  - { text: "Set `ptrace_scope` to 0 on the production machines", explanation: "That lets every process read every other process of its user, all the time, to allow something done a few times a year." }
  - { text: "Give the team `sudo`, and run the profiler as root when needed", explanation: "It works, and it runs a whole interpreter as root on a production machine. There is a narrower way." }
  - { text: "Keep a copy of the interpreter with `CAP_SYS_PTRACE` for profiling, runnable by the team alone, and decide that before it is needed", correct: true }
  - { text: "Restart the service under `run` when something goes wrong", explanation: "The restart destroys the state that was going wrong, which is what attaching is meant to avoid." }
explanation: "The capability gives one program one permission, and file permissions say who may run that program. It is still a decision for whoever answers for the machines, and it is far better made calmly beforehand than at three in the morning."
```
