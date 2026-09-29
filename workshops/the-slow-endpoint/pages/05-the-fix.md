---
title: The fix
requires: [verify:fix-written, verify:fixed-recorded]
---

# The fix

The view wants the twenty newest articles that mention a word, and
how many mention it. The database can work out both. It can find
the articles through the index of words, sort them and stop at
twenty, in one query, where the view fetched a thousand articles to
throw away all but twenty.

```{file-write}
:id: write-fix
:title: Replace web.py with the fixed version
:path: gazette/web.py
:from: fixed/web.py
:open: true
```

Two things have changed in {open}`gazette/web.py`. Near the top,
`MENTIONS` now counts, and there is a new statement, `MENTIONING`,
which joins the `words` table to the `articles` table:

```sql
SELECT a.id, a.title, a.author, a.section, a.date, a.body
  FROM words AS w JOIN articles AS a ON a.id = w.article_id
  WHERE w.word = ? ORDER BY a.date DESC, a.id DESC LIMIT 20
```

And `search` has lost its loop:

```python
    count = db.execute(MENTIONS, (word,)).fetchone()[0]
    newest = db.execute(MENTIONING, (word,)).fetchall()
```

Two queries for a search, whatever the word.

```{verify}
:id: fix-written
:label: web.py has the fixed search
:trigger: after:write-fix
:substrate: shell
python -c "from pathlib import Path; t = Path('gazette/web.py').read_text(encoding='utf-8'); assert 'JOIN articles' in t and 'for mention in' not in t, 'gazette/web.py still has the loop in search: click the action above to replace it'; print('gazette/web.py has one query where the loop was')"
```

## Record it again, the same way

A comparison is only as good as the two things compared. Everything
but the fix must be the same: the same options to the profiler, the
same twenty seconds, and the same load, which is why `load.py` keeps
to a pace. Had it sent requests as fast as the server could answer,
the fixed server would have been sent more of them, and the second
recording would be of a busier server.

As before, click the first action, and the second as soon as the
first has a tick.

```{execute}
:id: start-fixed
:session: server
:title: Start the fixed server under the profiler
:wait: 3s
python -m profiling.sampling run -a -d 20 --binary -o fixed.bin -m flask --app gazette.web run --port {{ server_port }}
```

```{execute}
:id: load-fixed
:session: client
:title: Send the same requests
:wait: prompt
python load.py {{ server_port }} | tee load-after.txt
```

```{verify}
:id: fixed-recorded
:label: fixed.bin is recorded, of the fixed server
:trigger: after:load-fixed
:substrate: shell
:timeout: 40s
python - <<'CHECK'
import sys, time
from pathlib import Path

if "JOIN articles" not in Path("gazette/web.py").read_text(encoding="utf-8"):
    sys.exit("gazette/web.py still has the loop in search. Replace it with the first action on this page, then record again")
file = Path("fixed.bin")
for _ in range(25):
    if file.exists() and file.stat().st_size > 0:
        break
    time.sleep(1)
else:
    sys.exit("No fixed.bin yet. The profiler writes it when its twenty seconds are up: start the server, then send the requests")
time.sleep(1)
load = Path("load-after.txt")
if not load.exists() or "search" not in load.read_text(encoding="utf-8"):
    sys.exit("fixed.bin is written, but load.py sent no requests while it was recorded. Start the server again, and send the requests straight after")
if not Path("baseline.bin").exists():
    sys.exit("fixed.bin is recorded, but there is no baseline.bin to compare it with. Restart the workshop to begin again")
print(f"fixed.bin is recorded, {file.stat().st_size // 1024} KB of samples")
CHECK
```
