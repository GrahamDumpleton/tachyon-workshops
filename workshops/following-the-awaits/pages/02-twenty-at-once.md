---
title: Twenty at once
requires: [verify:server-up, verify:both-ran]
---

# Twenty at once

Start the feed server. It runs in the terminal on the right, called
`server`, and stays running until the last page of the workshop stops
it. It listens on this machine only, on port {{ server_port }}.

```{execute}
:id: start-server
:session: server
:title: Start the feed server
:wait: 3s
python slow_server.py {{ server_port }}
```

```{hint}
:title: If the port is already in use
The server stops at once with "Address already in use" when something
else on the machine has port {{ server_port }}. Click the gear button
in the header of this panel to open the Variables dialog, change
`server_port` to another number, such as 8082, and run the action
again. The commands on every page use the number you set.
```

```{verify}
:id: server-up
:label: The feed server answers
:trigger: after:start-server
:substrate: shell
python -c "import urllib.request; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/feeds/0.xml', timeout=5).read(); assert b'<rss' in body; print('The server sent feed 0,', len(body), 'bytes')" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT; start the server with the action above"; exit 1; }
```

Read the feeds one after another first, with the program that does
not use `asyncio`, and then at once with the one that does. Neither
is being profiled. The `| tee` at the end of each command belongs to
the shell: it prints the program's output as usual and keeps a copy
in a file, which the check below reads.

```{execute}
:id: run-feeds
:session: shell
:title: Read the feeds one after another
:wait: prompt
python gazette/feeds.py {{ server_port }} | tee one-by-one.txt
```

```{execute}
:id: run-crawl
:session: shell
:title: Read the feeds at once
:wait: prompt
python gazette/crawl.py {{ server_port }} | tee at-once.txt
```

The same fifteen hundred or so items both times, in about four and a
half seconds and then in about one and a half. Twenty waits of a
fifth of a second are four seconds when they are made in turn. Made
four at a time they are five rounds, one second. The half second
left over in both is work: parsing the pages and merging the items.

So `asyncio` has done what it is for, and the question now is the
one to ask of any program: where does the second and a half go?

```{verify}
:id: both-ran
:label: Both programs read the feeds, and the asyncio one was quicker
:trigger: after:run-crawl
import re
from pathlib import Path

def seconds(path, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the command above that reads the feeds {command}"
    found = re.search(r"Feeds read in ([\d.]+) seconds", file.read_text(encoding="utf-8"))
    assert found, f"{path} does not say how long the feeds took; did the program fail? Check that the server is running"
    return float(found.group(1))

in_turn = seconds("one-by-one.txt", "one after another")
at_once = seconds("at-once.txt", "at once")
assert at_once < in_turn, f"Reading the feeds at once took {at_once} seconds and in turn {in_turn}; expected at once to be quicker"
print(f"One after another: {in_turn} seconds. At once: {at_once} seconds")
```
