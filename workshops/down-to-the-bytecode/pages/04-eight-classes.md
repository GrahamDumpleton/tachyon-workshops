---
title: Eight classes
requires: [quiz:what-changes, verify:slower, verify:attribute-loads]
---

# Eight classes

Now the other way of making the articles: an instance of `Business`
for an article in the business section, of `Sport` for one in sport,
eight classes in all. They have the same attributes, set by the same
`__init__`, and `score` is the same function, not a character
changed. Run the program both ways, without the profiler. The
`| tee` keeps a copy of each run's output for the check below.

```{execute}
:id: time-one-class
:session: shell
:title: Score articles of one class
:wait: prompt
python gazette/scores.py one-class | tee one-class.txt
```

```{execute}
:id: time-by-section
:session: shell
:title: Score articles of eight classes
:wait: prompt
python gazette/scores.py by-section | tee by-section.txt
```

```{verify}
:id: slower
:label: Both forms of the program ran
:trigger: after:time-by-section
import re
from pathlib import Path

def seconds(path, how):
    file = Path(path)
    assert file.exists(), f"No {path} yet: run the command above that scores articles of {how}"
    text = file.read_text(encoding="utf-8")
    found = re.search(r"Scored \d+ articles of (\d+) class.*\n.*computed in ([\d.]+) seconds", text)
    assert found, f"{path} does not say how long the scoring took; did the program fail?"
    return int(found.group(1)), float(found.group(2))

classes, one = seconds("one-class.txt", "one class")
assert classes == 1, f"one-class.txt is a run with {classes} classes; run the first command as it is written"
classes, eight = seconds("by-section.txt", "eight classes")
assert classes == 8, f"by-section.txt is a run with {classes} classes; run the second command as it is written"
print(f"One class: {one} seconds. Eight classes: {eight} seconds")
```

The second run takes about a third longer, for the same work on the
same data. The source cannot say why, and nor can a profile by
line, which would show the same lines in much the same proportions.

```{quiz}
:id: what-changes
question: "The function `score` reads `article.section`, `article.words`, `article.age` and `article.length`. With articles of eight classes arriving in no order, what becomes of the instructions that load them?"
options:
  - { text: "They are never specialised, and appear as plain `LOAD_ATTR`", explanation: "They are specialised, for whichever class the interpreter saw when it looked. The trouble comes after." }
  - { text: "They are specialised for one class, and for an article of any other the check fails and the load is done the general way", correct: true }
  - { text: "The interpreter makes eight copies of `score`, one for each class", explanation: "It keeps one copy of the bytecode, with one specialised instruction at each place, and that instruction expects one class." }
explanation: "A specialised `LOAD_ATTR` checks the object's class before anything else. Seven articles in eight fail the check, and for those the instruction costs the check and then the general lookup."
```

```{execute}
:id: profile-by-section
:session: shell
:title: Record a heatmap with opcodes, with eight classes
:wait: prompt
python -m profiling.sampling run --opcodes --heatmap -o heatmap-by-section gazette/scores.py by-section
```

Put the two heatmap pages one above the other: the first action
makes room by shrinking the terminal, the second brings back the
page from the first heatmap, and the third opens the new one beneath
it. They cannot be tabs in one place, because the viewer loads a
page again each time its tab comes to the front, and a panel you
opened in one would be closed by looking at the other.

```{layout}
:id: make-room
:title: Make room for two pages
:name: compare
```

```{file-open}
:id: open-one-class
:title: Bring back the heatmap of scores.py with one class
:path: heatmap/file_0000.html
:factory: HTML Viewer
:area: desk
```

```{file-open}
:id: open-by-section
:title: Open the heatmap with eight classes below it
:path: heatmap-by-section/file_0000.html
:factory: HTML Viewer
:area: bottom
```

Both pages are called `file_0000.html`: the one above is from
`heatmap`, one class, and the one below from `heatmap-by-section`,
eight. Open the panel on line 91 in each and compare them. The instructions
are the same, under the same names, with the same badges, and the
heading still says nine tenths specialised. What differs is the
samples. `CONTAINS_OP_SET` has about as many as before.
`LOAD_ATTR_INSTANCE_VALUE` had a few dozen and now has several
hundred, several times as many, and the same is true of the
attribute loads on lines 89, 93 and 94.

The profiler reads the instruction that is in the bytecode, and the
instruction in the bytecode is the specialised one. It cannot see
that the check inside it failed. It can see that the program is
spending several times as long there, and that is the extra third
of a second.

So the badge says what the interpreter chose, and the samples say
whether the choice is paying. An instruction that is specialised and
costly beside its neighbours is worth a second look.

What to do about it is an ordinary decision about design. Here the
eight classes differ in one attribute that nothing in the scoring
uses, and one class with a `desk` field would do. Where the classes
are needed, the loop could take its articles a section at a time, so
that each run of calls meets one class.

```{verify}
:id: attribute-loads
:label: With eight classes the attribute loads take several times the samples
:trigger: after:profile-by-section
import html
import json
import re
from pathlib import Path

def attribute_loads(directory, how):
    page = Path(directory) / "file_0000.html"
    assert page.exists(), f"No {page} yet: run the command above that records a heatmap {how}"
    text = page.read_text(encoding="utf-8")
    assert "scores.py" in text, f"{page} is not the page for scores.py; was the program gazette/scores.py?"
    loads = tests = 0
    for packed in re.findall(r"data-bytecode='(.*?)'", text, re.S):
        for instruction in json.loads(html.unescape(packed)):
            if instruction["opname"].startswith("LOAD_ATTR"):
                loads += instruction["samples"]
            elif instruction["opname"].startswith("CONTAINS_OP"):
                tests += instruction["samples"]
    assert tests, f"{page} has no instructions in it; was the heatmap written with --opcodes?"
    return 100 * loads / tests

one = attribute_loads("heatmap", "on the second page of this workshop")
eight = attribute_loads("heatmap-by-section", "with eight classes")
assert eight > one * 1.5, (
    f"For every hundred samples on the test of a word, the attribute loads have {one:.0f} with one class "
    f"and {eight:.0f} with eight; expected a good deal more with eight. "
    "Was the second heatmap recorded with by-section?"
)
print(f"For every hundred samples on the test of a word, the attribute loads have {one:.0f} "
      f"with one class and {eight:.0f} with eight")
```
