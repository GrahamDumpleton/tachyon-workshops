---
title: Who may read a process?
requires: [verify:probe-ran, verify:server-up, quiz:who-may-read]
---

# Who may read a process?

A process's memory holds whatever the program holds: passwords,
keys, other people's data. A program that can read another's memory
can take all of it. So operating systems are careful about who may,
and being the same user is often not enough.

- **On Linux** the kernel's Yama module decides, by a setting called
  `ptrace_scope`. At 0, a process may read any process of the same
  user. At 1, which is what most distributions ship, it may read
  only its own descendants, the processes it started and those they
  started. At 2 and 3 it is stricter still. Root, and a program
  given the capability `CAP_SYS_PTRACE`, may read anything.

- **On macOS** reading another process needs root, or a program
  signed with a debugger's entitlement.

- **On Windows** it needs an administrator's privilege.

This is why `run` works everywhere: the profiler starts the
program, so the program is its descendant. And it is why `attach`
often does not: a service started by the system, or by another
shell, is nobody's descendant but theirs.

In a container the kernel is the host's. Docker Desktop's kernel has
no Yama module at all, so inside a container there the answer is
yes. On a Linux server, or in a container on one, it is usually no.

## Ask the machine

The way to find out what a machine allows is to try. The action
below starts a small Python program in the background, one that
the profiler did not start, runs `dump` against it, and keeps only
whether that worked: `yes` or `no`. The answer is stored for the
rest of the workshop, and the pages that follow show you the path
that suits it.

```{execute-capture}
:id: probe-attach
:title: Find out whether the profiler may read a process it did not start
:capture: can_attach
python -c "import time; time.sleep(5)" & pid=$!; sleep 0.5; if python -m profiling.sampling dump $pid >/dev/null 2>&1; then echo yes; else echo no; fi; kill $pid; wait $pid 2>/dev/null; true
```

```{verify}
:id: probe-ran
:label: The machine has answered
:trigger: after:probe-attach
:substrate: shell
test "$CAN_ATTACH" = yes -o "$CAN_ATTACH" = no && echo "This machine answers: $CAN_ATTACH" || { echo "No answer yet: run the action above"; exit 1; }
```

````{when} can_attach == "yes"
On this machine the answer is **yes**. The profiler may read a
process of yours that it did not start, which is so where
`ptrace_scope` is 0 and in a container on Docker Desktop. The next
pages read a web site for real.
````

````{when} can_attach == "no"
On this machine the answer is **no**, which is the usual answer on a
Linux machine. Nothing is wrong with the profiler or the web site.
The next pages show what the commands print where they are allowed,
from a machine where they were, and the page after those is about
what can be done here.
````

## A server, started the ordinary way

Whatever the answer, start the web site, with nothing around it.
It runs in the terminal on the left until the last page of the
workshop stops it.

```{execute}
:id: start-server
:session: server
:title: Start the web site
:wait: 3s
python -m flask --app gazette.web run --port {{ server_port }}
```

```{verify}
:id: server-up
:label: The site answers, and has written its process number
:trigger: after:start-server
:substrate: shell
python -c "import urllib.request; from pathlib import Path; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=5).read().decode(); assert 'ok' in body; pid = Path('gazette.pid').read_text().strip(); assert Path('/proc', pid).exists(), 'gazette.pid names a process that is not running'; print('The site answers, and is process', pid)" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT; start the web site with the action above. If it stopped at once with 'Address already in use', see the hint"; exit 1; }
```

```{hint}
:title: If the port is already in use
The server stops at once with "Address already in use" when something
else on the machine has port {{ server_port }}. Click the gear button
in the header of this panel to open the Variables dialog, change
`server_port` to another number, such as 8096, and run the action
again. The commands on every page use the number you set.
```

```{quiz}
:id: who-may-read
question: "A service was started by the system when the machine came up, and runs as the user `web`. You log in as `web`, on a Linux machine with `ptrace_scope` at 1, and run `attach` with the service's process number. What happens?"
options:
  - { text: "It works, since the service and the profiler are the same user", explanation: "That is enough at `ptrace_scope` 0. At 1, being the same user is not." }
  - { text: "It is refused, since the service is not a descendant of the profiler", correct: true }
  - { text: "It works, but only the main thread can be read", explanation: "Permission is for the process as a whole. Either all of its memory can be read or none." }
  - { text: "It is refused, since a service can never be profiled while it runs", explanation: "It can, by a process that is allowed to read it: root, a program with the capability, or any process of the same user where the setting is 0." }
explanation: "At the usual setting a process may read its descendants and nothing else. Your shell did not start the service, so nothing you start from it is the service's ancestor."
```
