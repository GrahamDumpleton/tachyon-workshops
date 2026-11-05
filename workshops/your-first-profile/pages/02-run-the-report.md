---
title: Run the report
requires: [quiz:which-is-slow]
---

# Run the report

Before profiling anything, run the program as it is, so you have a
time to compare against and know what it prints. The terminal below
the editor is where every command in this workshop runs; each one
arrives when you click it.

```{execute}
:id: run-report
:session: shell
:title: Run the report without a profiler
:wait: prompt
python gazette/report.py
```

The report lists the ten most common words and the articles in each
section, and its last line says how long it took: about a second and
a half where this page was written, and two or three times that on a
slower machine or a busy shared server. Whatever yours says, it is
your own time that the rest of the workshop is measured against. Two
thousand short articles is not much text.
Something in those four functions is doing more work than the text
deserves, and the question is which.

Reading the code, you might guess. `load_articles` parses a megabyte
and a half of JSON. `count_words` walks every word of every article.
`most_common` sorts a dictionary of counts. `render` formats a few
dozen lines. Make your guess before the profiler answers, because the
point of a profiler is how often the guess is wrong.

```{quiz}
:id: which-is-slow
question: Which function do you expect to take most of the report's time?
options:
  - { text: "`load_articles`, parsing the JSON", explanation: "Parsing a megabyte and a half of JSON takes a few milliseconds; the `json` module is C code and fast." }
  - { text: "`most_common`, sorting the counts", explanation: "There are about a thousand distinct words to sort, which takes a fraction of a millisecond." }
  - { text: "`count_words`, counting every word", correct: true }
  - { text: "`render`, formatting the report", explanation: "Formatting a few dozen lines is the cheapest thing the program does." }
explanation: "`count_words` is the one. Any answer is fine here: the profiler is about to say for certain, and the next pages read what it says."
```
