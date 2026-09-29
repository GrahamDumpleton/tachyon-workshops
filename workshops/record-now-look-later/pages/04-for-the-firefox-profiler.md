---
title: For the Firefox Profiler
requires: [verify:gecko-written]
---

# For the Firefox Profiler

Every view so far adds the samples up, and adding up throws away the
order they came in. A flame graph of a program that was quick for
ten seconds and then slow for two looks the same as one that was
slow first. When the question is "what happened, and when", the
profile has to go to a tool with a timeline, and the one the profiler
writes for is the [Firefox Profiler](https://profiler.firefox.com), a
web application built for profiling Firefox that reads profiles from
anything. Its format is named after Gecko, the browser's engine.

```{execute}
:id: replay-gecko
:session: shell
:title: Replay the recording as a gecko profile
:wait: prompt
python -m profiling.sampling replay --gecko -o profile.json report.bin
```

The file is JSON, written as one long line. JupyterLab can show it
as a tree.

```{command}
:id: open-gecko
:title: Open profile.json as a tree
:command: docmanager:open
{ "path": "{{ workspace }}/profile.json", "factory": "JSON" }
```

Click the arrows to open a branch. Three things are worth finding.

- `threads` has one item, the main thread, and inside it `samples`
  has three lists of the same length: `stack`, which stack each
  sample saw, `time`, when it was taken in milliseconds from the
  start, and `eventDelay`. This is the difference from every other
  format: the samples are kept one by one, in order, with their
  times.

- `markers`, also inside the thread, are intervals rather than
  instants. The profiler writes one whenever the thread's state
  changes: whether it holds the GIL, whether it is on a processor,
  whether it is running Python or native code, whether an exception
  is being handled, and when the garbage collector runs. Later
  workshops measure each of these one at a time with `--mode`; the
  gecko format records them all at once, which is why `--gecko` and
  `--mode` cannot be used together.

- `shared`, at the top level, has `stringArray`, the names of the
  functions and files, which everything else refers to by number.

To look at it properly, open <https://profiler.firefox.com> in a
browser, in Firefox or any other, and load the file. The site's code
runs in your browser and the profile is not uploaded anywhere, so it
can be done with a profile you may not share. There you get the
samples along a timeline with the markers as coloured bands beneath,
a call tree, and a flame graph of any span of time you select. That
is for later and for a profile with more of a story than this one,
which does one thing from start to finish.

```{verify}
:id: gecko-written
:label: profile.json is a gecko profile with one thread of samples
:trigger: after:replay-gecko
import json
from pathlib import Path

assert Path("profile.json").exists(), "No profile.json yet: run the replay --gecko command above"
profile = json.loads(Path("profile.json").read_text(encoding="utf-8"))
assert "threads" in profile and profile["threads"], "profile.json has no threads; was it written by replay --gecko?"
samples = profile["threads"][0]["samples"]["length"]
assert samples > 100, f"The thread holds only {samples} samples; was report.bin recorded from the whole run?"
print(f"profile.json holds {len(profile['threads'])} thread with {samples} samples, each with its time")
```
