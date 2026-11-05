---
title: Watch it stall
requires: [verify:index-up, verify:server-up, quiz:predict-the-search, verify:search-slowed, verify:server-stopped]
---

# Watch it stall

See the complaint before looking for its cause. Start the index
service first. It runs in the terminal on the right, called `index`,
until the last page of the workshop stops it.

```{execute}
:id: start-index
:session: index
:title: Start the index service
:wait: 3s
python index_server.py {{ upstream_port }}
```

```{verify}
:id: index-up
:label: The index service answers
:trigger: after:start-index
:substrate: shell
python -c "import urllib.request, json; answer = json.load(urllib.request.urlopen('http://127.0.0.1:$UPSTREAM_PORT/lookup?q=council', timeout=5)); assert answer['count'] > 0; print('The index service found', answer['count'], 'articles that mention council')" 2>/dev/null || { echo "Nothing answers on port $UPSTREAM_PORT; start the index service with the action above"; exit 1; }
```

Then the web site, in the terminal on the left, with no profiler
yet.

```{execute}
:id: start-plain
:session: server
:title: Start the web site
:wait: 3s
python -m uvicorn gazette.asgi:app --port {{ server_port }}
```

```{verify}
:id: server-up
:label: The web site answers
:trigger: after:start-plain
:substrate: shell
python -c "import urllib.request; body = urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=5).read().decode(); assert 'ok' in body; print('The site answered its health check:', body.strip())" 2>/dev/null || { echo "Nothing answers on port $SERVER_PORT; start the web site with the action above"; exit 1; }
```

```{hint}
:title: If a port is already in use
A server stops at once with "Address already in use" when something
else on the machine has its port. Click the gear button in the
header of this panel to open the Variables dialog, change
`server_port` or `upstream_port` to another number, and run the
actions again. The commands on every page use the numbers you set.
If you change `upstream_port` after the terminals are open, close
the `server` terminal and run its action again, so that the web
site learns the new number.
```

## Searches alone

Send searches and nothing else, for five seconds.

```{execute}
:id: load-alone
:session: client
:title: Send searches only, for five seconds
:wait: prompt
python load.py {{ server_port }} 5 search | tee alone.txt
```

The median is a little over fifty milliseconds, which is the
twentieth of a second the index service takes and a few thousandths
for everything else. It is much the same on any machine, since
nearly all of it is the wait. Eight searches are in hand at any moment, and
none of them slows another, because all eight are waiting. This is
an asyncio service doing what it is good at.

## Searches, and articles

Now the ordinary mixture, three articles for every search. The
searches are the same as before, and the index service is no busier
than it was.

```{quiz}
:id: predict-the-search
question: What will the median time of a search be, now that articles are being read as well?
options:
  - { text: "The same, a little over fifty milliseconds, since a search does nothing it did not do before", explanation: "A search does the same work. It does not get the same turns: whenever it is ready to go on, the loop may be busy with an article." }
  - { text: "Less, since there are fewer searches to wait for", explanation: "Searches never waited for each other. They wait for the index service, which answers each in its own time." }
  - { text: "A good deal longer, though a search does nothing different", correct: true }
  - { text: "Searches will fail, since the service can only do one thing at a time", explanation: "Nothing fails. Every request is answered, some later than they might have been." }
explanation: "A search needs the loop several times: to read the request, to send the question to the index service, to read the answer, to reply. Each time, it has to wait until the loop is free, and with articles being rendered the loop is often not."
```

```{execute}
:id: load-together
:session: client
:title: Send articles and searches, for five seconds
:wait: prompt
python load.py {{ server_port }} 5 | tee together.txt
```

In the run this page was written from, a search went from 55
milliseconds to 111. Yours will differ, and the direction will not:
on a slower machine the second figure is larger still, since what
the search is kept waiting by is computing, which takes longer
there.

```{verify}
:id: search-slowed
:label: A search takes longer when articles are being read
:trigger: after:load-together
import re
from pathlib import Path

def median(path, page, command):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the {command}, which writes it"
    row = re.search(rf"^{page}\s+(\d+)\s+([\d.]+) ms", file.read_text(encoding="utf-8"), re.M)
    assert row, f"{path} has no row for {page}; was the web site running when load.py was run? Start it and run the command again"
    return float(row.group(2))

alone = median("alone.txt", "search", "first load.py command above")
together = median("together.txt", "search", "second load.py command above")
assert together > alone * 1.2, (
    f"A search took {alone:.0f} ms alone and {together:.0f} ms with articles being read; expected it to take a good deal longer. "
    "Run the two load.py commands again, in order"
)
print(f"A search took {alone:.0f} ms alone and {together:.0f} ms with articles being read")
```

Stop the web site. It will be started again under the profiler.

```{interrupt}
:id: stop-plain
:session: server
:title: Stop the web site
```

```{verify}
:id: server-stopped
:label: The web site has stopped
:trigger: after:stop-plain
:substrate: shell
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=2)" 2>/dev/null && { echo "The site still answers on port $SERVER_PORT; stop it with the action above"; exit 1; } || echo "Nothing is listening on port $SERVER_PORT"
```
