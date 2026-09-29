---
title: A second change
requires: [verify:changed, verify:change-compared, quiz:which-baseline]
---

# A second change

Someone now tidies `hardest`. It used to collect every article's
score and sort the list once at the end. The new version keeps the
list in order as it goes, by sorting it each time a score is added.
The report it prints is the same.

```{file-write}
:id: write-change
:title: Replace report.py with the version that keeps the scores sorted
:path: gazette/report.py
:from: regressed/report.py
:open: true
```

```{verify}
:id: changed
:label: hardest sorts the scores inside its loop
:trigger: after:write-change
:substrate: shell
grep -q "scores = sorted(scores)" gazette/report.py && echo "hardest sorts the scores each time one is added" || { echo "gazette/report.py is not the changed version; run the action above"; exit 1; }
```

Record it, and compare it with the recording made just before this
change, `fixed.bin`, not with the first baseline.

```{execute}
:id: record-second
:session: shell
:title: Record the changed program
:wait: prompt
python -m profiling.sampling run -r 10khz --binary -o second.bin gazette/report.py
```

```{execute}
:id: compare-second
:session: shell
:title: Compare it with the fixed program
:wait: prompt
python -m profiling.sampling replay --diff-flamegraph fixed.bin -o diff2.html second.bin
```

```{command}
:id: open-diff2
:title: Open diff2.html in the HTML viewer
:command: docmanager:open
{ "path": "{{ workspace }}/diff2.html", "factory": "HTML Viewer" }
```

This is the picture the tool is for. `hardest` is red, and it is
wide at the bottom of its stack: there is a box for line 78, the
new `sorted`, with nothing beneath it. Its tooltip says about two
milliseconds before and twenty-five or so now, more than ten times
as much. `count_words` is grey. Nobody touched it, and it shows.

`reading_ease` and `syllables` are pale blue, and nobody touched
them either. It is the scaling again, in the other direction and
much milder: the run is half as long again as it was, so everything
that stayed the same has a somewhat smaller share. With two runs
of nearly the same length the effect is small enough to see past.
Against the first baseline it would not have been, since `hardest`
would have been one more red box among the red boxes of the last
page.

The change cost about a twentieth of a second, a third of the
program's time, in a report whose output did not change by a
character. No test would have caught it.

```{verify}
:id: change-compared
:label: The changed program is recorded and compared with the fixed one
:trigger: after:compare-second
:substrate: shell
test -s second.bin || { echo "No second.bin yet: run the command above that records the changed program"; exit 1; }
test -s diff2.html || { echo "No diff2.html yet: run the command above that compares second.bin with fixed.bin"; exit 1; }
grep -q "baseline_samples" diff2.html || { echo "diff2.html is not a differential flame graph; was it written with --diff-flamegraph fixed.bin?"; exit 1; }
grep -q hardest diff2.html && echo "diff2.html compares the changed program with the fixed one, and holds hardest" || { echo "diff2.html does not name hardest; was the program gazette/report.py?"; exit 1; }
```

```{quiz}
:id: which-baseline
question: A service has been made quicker in three steps over a month, and a profile was recorded after each. A fourth change has just gone in. Which recording should its profile be compared with?
options:
  - { text: "The first, from before any of the changes, since it is the original baseline", explanation: "That compares four changes at once, and the runs are so unlike in length that the scaling colours everything." }
  - { text: "The one recorded after the third step, since the only difference from it is the change being judged", correct: true }
  - { text: "Any of them: the differential flame graph allows for the difference in length", explanation: "It allows for it by comparing shares, which is what makes a comparison between very different runs hard to read." }
explanation: "Compare each change with the profile made just before it, recorded the same way. Then what is coloured is what the change did."
```
