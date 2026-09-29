---
title: Welcome
requires: [verify:env-ready]
---

# The price of an exception

Python programmers are taught to ask forgiveness, not permission: try
the thing, and handle the exception if it fails, in place of testing
first whether it will work. It is good advice. It rests on an
assumption, though, which is that failing is unusual. Code written
this way has a quick path for the usual case and a slower one for the
exception, and nobody minds the slower one because it is hardly ever
taken.

Then the data changes, and the unusual case is two thirds of the
input. Nothing breaks and every answer is still right. The program
is slower than it was, and an ordinary profile shows the time in the
same functions as before. What would help is a profile of only the
time spent handling exceptions, and the profiler has a mode for that.

## The program

{open}`gazette/dates.py` is open in the editor. Every filing of an
article carries four dates, and the desk that filed it writes them
its own way: the newsroom as `2026-03-14`, the archive as
`14/03/2026` and the wire agencies as `14 March 2026`. The program
reads fifty thousand filings and reports, for each desk, how long its
articles take to reach print.

Read `parse_date`. It tries the newsroom's format, and if that raises
`ValueError` it tries the archive's, and if that raises too it uses
the wire agencies'. When it was written nearly every filing came from
the newsroom.

## The environment

Create the workshop's environment, which installs nothing and makes
the `python` in the terminal Python 3.15, the one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15 and has the profiler
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling')"
```

## The data

The filings are a compressed CSV file. Look at the first few.

```{execute}
:id: show-filings
:session: shell
:title: The first filings in the file
:wait: prompt
gzip -dc data/filings.csv.gz | head -n 6
```

Most of the lines you see are from the `wire` desk. Across the whole
file two thirds are, a fifth are from the newsroom, and the rest from
the archive.
