---
title: A slow server
requires: [verify:server-up]
---

# A slow server

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
`server_port` to another number, such as 8072, and run the action
again. The commands on every page use the number you set.
```

```{verify}
:id: server-up
:label: The feed server answers
:trigger: after:start-server
:substrate: shell
python -c "import urllib.request; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/feeds/0.xml', timeout=5).read(); assert b'<rss' in body; print('The server sent feed 0,', len(body), 'bytes')" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT; start the server with the action above"; exit 1; }
```

Now run the feed reader against it, in the terminal on the left, with
no profiler.

```{execute}
:id: run-feeds
:session: shell
:title: Read the feeds
:wait: prompt
python gazette/feeds.py {{ server_port }}
```

Four seconds and a little more, to fetch twenty pages and merge two
thousand items into fifteen hundred or so. Where does that time go?
You know there is a fifth of a second of waiting in each of twenty
requests, which is four seconds on any machine, since a wait takes
as long on a slow machine as on a quick one. The little more is the
program's own work, and that does depend on the machine: half a
second where this page was written, and two or three times that on
a busy shared server. A colleague who had not read the server would
know none of this, and would see only a program that fetches, parses
and merges and is slow. The profiler is how they find out.
