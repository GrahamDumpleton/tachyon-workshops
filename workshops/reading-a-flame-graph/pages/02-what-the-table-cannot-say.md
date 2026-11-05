---
title: What the table cannot say
requires: [quiz:who-calls-it]
---

# What the table cannot say

Run the renderer under the profiler with the table trimmed to ten
rows, as the first workshop taught.

```{execute}
:id: profile-table
:session: shell
:title: Profile the page renderer, ten rows
:wait: prompt
python -m profiling.sampling run -l 10 --no-summary gazette/pages.py
```

The program takes a second or two to render its pages, depending on
the machine, and the table is clear about where: `format_date`, on
its two lines, has around three quarters of the direct samples, and
the `_strptime` rows below it are the standard library's date
parser that `format_date` calls. The error rate can be high on this
program, as much as forty percent on some machines and runs,
because parsing a date builds and tears down a dozen frames in a
few microseconds; the third of these workshops explains what that
costs and what it does not, and the table is still sound.

So `format_date` is expensive. But `format_date` is called from two
places: from `summary`, once per article rendered, and from
`render_archive`, which uses it to work out which day each article
belongs to. Which caller is responsible for the time? The table
cannot say. Its rows are functions, not paths, and the row for
`format_date` adds up every call from everywhere. Look at the two
callers in {open}`gazette/pages.py` and predict.

```{quiz}
:id: who-calls-it
question: Most of the time in `format_date` is spent on calls from which function?
options:
  - { text: "`summary`, since every one of the three hundred pages is made of summaries", explanation: "Plausible, and wrong: `summary` calls `format_date` once per article on a page, about six thousand times in all, which is a fraction of a second. The flame graph on the next pages shows this." }
  - { text: "`render_archive`, which calls it for every article for every day", correct: true }
  - { text: "`render_index`, which sorts the articles by date", explanation: "`render_index` sorts by the ISO string and never calls `format_date` itself; only its hundred summaries do." }
  - { text: "The calls are spread evenly, since the function costs the same wherever it is called from", explanation: "The cost per call is the same. The number of calls is not: a loop that calls it once per article for each of 271 days calls it half a million times." }
explanation: "`render_archive` finds each day's articles with a comprehension that calls `format_date` on every article, for every day: 271 days times 2,000 articles. `summary` calls it about 6,000 times. The next page draws the difference."
```
