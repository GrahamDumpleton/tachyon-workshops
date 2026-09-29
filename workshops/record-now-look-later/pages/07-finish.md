---
title: Finish
requires: [quiz:which-format]
---

# Finish

One recording, six views, and the program ran once. These are the
formats the profiler writes, with what each is for and what it
leaves out. All but the last two you have now made.

- **`--pstats`**, the default: the table, or with `-o` a file for
  the `pstats` module. For the first answer, and for tools that read
  pstats. It has no paths, only functions.

- **`--collapsed`**: one line of text per stack, with a count. For
  another flame graph tool to draw, or for `grep`. It is not for
  reading at a glance.

- **`--flamegraph`**: one HTML file with every call path drawn. For
  when you know the symptom and want the path. It has no order in
  time.

- **`--heatmap`**: a directory of HTML, the source with the samples
  painted on. For when you know the file and want the line. It shows
  one file at a time.

- **`--gecko`**: JSON for the Firefox Profiler. For the order of
  events and the states of the threads. It needs that tool to be
  read.

- **`--jsonl`**: JSON Lines, the counts for each frame. For a script
  or a build to read. It has frames and not stacks, so no paths.

- **`--binary`**: the samples themselves, compact. For the run that
  cannot be repeated and the view not yet chosen. It cannot be
  looked at until it is replayed.

- **`--diff-flamegraph`**: a flame graph of what changed between two
  profiles. It needs a binary recording from before the change.

The last is the subject of **Did the fix work?**, later in these
workshops, and it is one more reason to record: the comparison needs
a binary file of the run before the change. There is also a live
view, `--live`, which writes nothing and is the last of these
workshops.

```{quiz}
:id: which-format
question: A job in production is slow tonight and will not be by morning. You may profile it for thirty seconds and the person who knows the code is asleep. Which output do you ask for?
options:
  - { text: "`--flamegraph`, since a picture is the easiest thing to send", explanation: "It is, and if the question tomorrow is which line, or what changed since last week, the picture cannot answer and the run cannot be repeated." }
  - { text: "`--binary`, since it keeps the samples and any view can be made from it later", correct: true }
  - { text: "`--pstats`, since every tool reads it", explanation: "A pstats file has the counts per function and has lost the stacks, so no flame graph can be drawn from it afterwards." }
  - { text: "All of them, one run after another", explanation: "Each run would be a different thirty seconds of a job that is changing. One recording replayed into each format gives views that agree." }
explanation: "Record in binary when the run cannot be repeated or the profile is for someone else. Every other format can be made from the recording, and none of them can be turned back into it."
```

Next in these workshops is **Waiting or working?**, the first of
four on choosing what the profiler measures. Press Finish to go
there.
