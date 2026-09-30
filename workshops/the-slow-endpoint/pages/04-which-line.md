---
title: Which line?
requires: [verify:heatmap-written, quiz:what-is-wrong]
---

# Which line?

A heatmap is the source of the program with the samples written
beside each line. Make one from the same recording.

```{execute}
:id: replay-heatmap
:session: client
:title: Make a heatmap from the baseline
:wait: prompt
python -m profiling.sampling replay --heatmap -o heatmap baseline.bin
```

A heatmap is a directory, with a page for every source file that
had a sample: a hundred or so here, nearly all of them Flask,
Werkzeug and the standard library. The pages are numbered, and the
number a file gets depends on how many samples it had, so the page
for `web.py` is not the same one on every machine. Find it by its
title, and copy it to a name of its own.

```{execute}
:id: copy-heatmap
:session: client
:title: Copy the page for web.py to heatmap-web.html
:wait: prompt
cp "$(grep -l 'gazette/web.py - Heatmap' heatmap/file_*.html)" heatmap-web.html
```

```{verify}
:id: heatmap-written
:label: heatmap-web.html is the heatmap of web.py
:trigger: after:copy-heatmap
:substrate: shell
python -c "from pathlib import Path; f = Path('heatmap-web.html'); assert f.exists(), 'No heatmap-web.html yet: run the two commands above, in order'; t = f.read_text(encoding='utf-8', errors='replace'); assert 'gazette/web.py' in t and 'def search' in t, 'heatmap-web.html is not the page for gazette/web.py; run the two commands above again'; print('heatmap-web.html is the heatmap of gazette/web.py')"
```

```{file-open}
:id: open-heatmap
:title: Open heatmap-web.html in the HTML viewer
:path: heatmap-web.html
:factory: HTML Viewer
:area: desk
```

Scroll down to `search`, near line 95. Each line has two numbers.
**Self** is the samples taken while that line itself was running,
and **Total** adds the samples of whatever the line called. The
colour runs from blue, for few, to red, for the most in the file.

One line is red, line 101, and the line above it is the next
warmest:

```python
    for mention in db.execute(MENTIONS, (word,)).fetchall():
        row = db.execute(ARTICLE, (mention["article_id"],)).fetchone()
        found.append(row)
```

Compare it with the views above it in the file. `front_page` and
`article` each have one line with samples worth the name, and it is
the line that runs their query. They run one query for a request.
Look at the two statements at the top of the file, `MENTIONS` and
`ARTICLE`, and then at what `search` does with them.

```{quiz}
:id: what-is-wrong
question: "The readers search for words such as \"council\", which about a thousand of the two thousand articles mention. How many queries does one such search run?"
options:
  - { text: "One, which joins the words to the articles", explanation: "That is what it should do. `MENTIONS` reads the `words` table alone, and gives back the numbers of the articles, not the articles." }
  - { text: "Two, one for the words and one for the articles", explanation: "There are two statements, and the second is inside the `for` loop, so it runs once for each article the first one found." }
  - { text: "About a thousand and one: one to find the articles, and one more for each of them", correct: true }
  - { text: "Twenty, one for each article on the page of results", explanation: "Only twenty are shown. All of them are fetched first, and then sorted, and the newest twenty kept." }
explanation: "One query finds which articles mention the word, and the loop then asks for each article with a query of its own. Each is quick, and a thousand of them are not. This is the commonest mistake in code that talks to a database, and it has a name: the N+1 query."
```

The loop also explains why the page gets slower as the gazette
grows, and why a search for a rare word is quick. Nobody would find
it by testing with ten articles.
