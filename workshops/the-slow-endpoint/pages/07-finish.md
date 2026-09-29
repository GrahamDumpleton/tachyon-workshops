---
title: Finish
requires: [verify:server-stopped, quiz:like-with-like]
---

# Finish

Both servers stopped when their twenty seconds were up. Make sure
of it before leaving.

```{verify}
:id: server-stopped
:label: Nothing is left listening on the port
:trigger: page-enter
:substrate: shell
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$SERVER_PORT/health', timeout=2)" 2>/dev/null && { echo "The site still answers on port $SERVER_PORT. Wait for its twenty seconds to end, or click in the server terminal and press Ctrl-C, then check again"; exit 1; } || echo "Nothing is listening on port $SERVER_PORT"
```

The order you worked in is the order to keep.

1. **Record before changing anything**, under a load you can
   repeat, in the binary format.

2. **Flame graph** for the view, **heatmap** for the line. Both
   come from the recording, so the server is run once.

3. **Change one thing.**

4. **Record again, the same way**, and compare: what the readers
   saw, the tables for the amounts, the differential flame graph
   for which functions changed their share.

Then do it again for the next widest box, with the second recording
as the new baseline. On this site that is `front_page`, whose query
sorts every article in the database to find the newest twenty.

```{quiz}
:id: like-with-like
question: "A colleague records a baseline with `load.py` on Monday. On Friday, after a fix, they record again with a load generator that sends requests as fast as the server will answer, and the differential flame graph is red nearly everywhere. What went wrong?"
options:
  - { text: "Nothing: the fix made most of the application slower", explanation: "It may have, and this comparison cannot say, since more than the fix differs between the two recordings." }
  - { text: "The baseline is too old to compare with", explanation: "A recording does not go stale. It is a fair baseline for as long as the second recording is made the same way." }
  - { text: "The two recordings were made under different loads, so the difference between them is not the fix alone", correct: true }
  - { text: "They should have compared two flame graphs by eye", explanation: "The differential flame graph does that comparison for you. It needs two recordings that differ in one thing." }
explanation: "A server answering as fast as it can is doing more work in the same time, in every view, and that shows as red. Same load, same duration, same options to the profiler: then what differs is the change you made."
```

Next in these workshops is **An async service that stalls**, where
the slow part is not slow itself and makes everything else wait.
Press Finish to go there.
