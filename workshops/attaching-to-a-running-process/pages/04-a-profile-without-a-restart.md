---
title: A profile without a restart
requires: [verify:profile-to-read, verify:never-restarted]
---

# A profile without a restart

`attach` is `run` with a process number where the program would
be. It takes the options you know: `-d` for how long, `-a` for every
thread, `--mode`, and any of the formats.

```
python -m profiling.sampling attach -a -d 15 --flamegraph -o attached.html $(cat gazette.pid)
```

There is one difference worth a moment. With `run`, `-d` ends the
program when the time is up. With `attach` it ends the profiler, and
the program carries on. Without `-d`, `attach` samples until the
program ends, or until you stop the profiler with Ctrl-C, which
writes the profile and leaves the program running.

````{when} can_attach == "yes"
Send requests for twenty seconds, and while they arrive, attach for
fifteen. Click the first action, then the second.

```{execute}
:id: load-for-attach
:session: client
:title: Send requests for twenty seconds
:wait: 1s
python load.py {{ server_port }} 20
```

```{execute}
:id: attach-server
:session: shell
:title: Attach to the running web site, for fifteen seconds
:wait: prompt
python -m profiling.sampling attach -a -d 15 --flamegraph -o attached.html $(cat gazette.pid)
```

```{command}
:id: open-attached
:title: Open attached.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/attached.html", "factory": "HTML Viewer" }
```
````

````{when} can_attach == "no"
On this machine the command is refused, and what the profiler says
when it is refused is worth reading once with a clear head. It is
shipped as {open}`attach-refused.txt`.

The first paragraph is the finding: the profiler could not read the
process's memory. The rest is three ways to be allowed to, and every
one of them is a change to the security of the machine: a
container started with more privilege, the command run as root, the
kernel's setting turned off. **Do none of them here**, and do none
of them on a machine that is not yours to decide for. The next page
is about making that decision properly.

A flame graph made by this command, of this web site under the same
load, on a machine that allowed it, is shipped with the workshop.

```{command}
:id: open-example
:title: Open attached-example.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/attached-example.html", "factory": "HTML Viewer" }
```
````

````{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar. If the tab is blank though the file is trusted,
close the tab and click the action again.
````

```{verify}
:id: profile-to-read
:label: There is a profile of the running web site to read
:trigger: action
import os
from pathlib import Path

answer = os.environ.get("CAN_ATTACH", "")
assert answer in ("yes", "no"), "The machine has not been asked yet: go back to the second page and run the action under 'Ask the machine'"
name = "attached.html" if answer == "yes" else "attached-example.html"
file = Path(name)
if answer == "yes":
    assert file.exists(), "No attached.html yet: send the requests, then attach, with the two actions above"
else:
    assert file.exists(), "attached-example.html is missing; restart the workshop to get it back"
text = file.read_text(encoding="utf-8", errors="replace")
missing = [word for word in ("serve_forever", "dispatch_request", "search") if word not in text]
assert not missing, (
    f"{name} has no " + ", ".join(missing) + " in it, so the site served no requests while the profiler was attached. "
    "Send the requests, then attach straight after"
)
if answer == "yes":
    print("attached.html is a profile of the running web site, made without restarting it")
else:
    print("This machine does not allow attaching; attached-example.html is a profile made where it was allowed")
```

## Reading it

It is the flame graph of a Flask application under load, and if you
have seen one made with `run` there is nothing new in it: a tower
for the main thread, waiting in `select`, a tower for the request
threads, with Werkzeug and Flask above the views, and `search` the
widest of the views. That is the point. A profile made by attaching
is an ordinary profile.

What differs is what is *not* in it. A profile made with `run`
begins when the program does, so it has the program starting up:
the imports, the database being opened. This one began in the
middle of the program's life, and has only what the program did in
those fifteen seconds.

## The server never knew

```{verify}
:id: never-restarted
:label: The web site is the same process it was, and still answers
:trigger: action
:substrate: shell
python -c "import urllib.request; from pathlib import Path; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=5).read().decode(); assert 'ok' in body; pid = Path('gazette.pid').read_text().strip(); assert Path('/proc', pid).exists(); print('The site still answers, and is still process', pid)" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT. The web site should still be running in the terminal on the left: start it from the second page"; exit 1; }
```

The web site was started once, on the second page, and has the
process number it had then. Whatever has been read from it since,
it served every request it was sent, and nothing in its log says
that anyone looked.
