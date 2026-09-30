---
title: The files
requires: [quiz:why-three-files]
---

# The files

A heatmap is a page per source file and an index that lists them.
Open the index in JupyterLab's HTML viewer. It opens beside
`gazette/report.py`, above the terminal, so the program, the page
and these instructions are all in view.

```{file-open}
:id: open-index
:title: Open heatmap/index.html in the HTML viewer
:path: heatmap/index.html
:factory: HTML Viewer
:area: desk
```

```{hint}
:title: If the page has no colours and nothing responds
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the heatmap's buttons are scripts. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar. Nothing in the file reaches the network.
```

The cards at the top are the run: the number of files profiled, the
total number of samples (the page calls them snapshots), the duration
in seconds, the samples taken each second, and the error rate and
missed samples, which for this program are close to nothing.

Below them, under **Profiled Files**, the files are sorted into
groups by where they come from. **Project Files** is your own code,
and it is open, showing the `gazette` folder. **Standard Library** is
closed. Click the `gazette` folder and then the **Standard Library**
heading to open them.

Your program is one file, `gazette.report`, with a bar beside it
as long as a bar gets. The standard library has two, `json` and
`json.decoder`, with a handful of samples and bars too short to see:
the profiler saw them on the stack while `load_articles` was parsing
the articles, and that took a few milliseconds of nearly two seconds.
Where a program uses packages it has installed, they get a group of
their own. The grouping is the first thing the heatmap tells you:
whether the time is in code you can change.

The count against a file is larger than the number of samples, about
three times as large for `gazette.report`. It is the sum of the counts
against the file's lines, and one sample counts towards every line of
the file that was on the stack: the line that called `main`, the line
of `main` that called `count_words`, and the line of `count_words`
that was running. Use it to compare one file with another and not as
a number of samples.

```{quiz}
:id: why-three-files
question: The program is one file. Why does the heatmap list three?
options:
  - { text: "The profiler profiles itself as well as the program", explanation: "The profiler is a separate process and none of its own code is in the profile." }
  - { text: "Standard library functions the program called were on the stack when samples were taken, so their files have lines with samples too", correct: true }
  - { text: "Every module the program imports is listed, whether or not it ran", explanation: "The program imports `string`, `sys` and `time` too, and none of them is listed. A file appears only if a sample found one of its lines on the stack." }
  - { text: "The heatmap always includes two files of examples", explanation: "Everything in the heatmap came from this run." }
explanation: "A file is in the heatmap if any sample had one of its lines on the stack. Parsing the articles ran code in `json/__init__.py` and `json/decoder.py` for a few milliseconds, long enough to be seen."
```

```{hint}
:title: Why the links on the page do nothing here
In a browser, each file name in the index is a link to that file's
page. JupyterLab's HTML viewer shows a copy of the file held in
memory, which has no address for a link to be relative to, so
following one from here fails with an error from the server. These
pages open each heatmap page with an action of its own instead. To
browse a heatmap by its links, download the directory and open
`index.html` in a browser.
```
