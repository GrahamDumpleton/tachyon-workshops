---
title: The shape of a server
requires: [quiz:read-the-server]
---

# The shape of a server

Open the flame graph. It opens beside `gazette/web.py`, above the
terminals, so the program, the picture and this page are all in
view.

```{file-open}
:id: open-wall
:title: Open wall.html in the HTML viewer
:path: wall.html
:factory: HTML Viewer
:area: desk
```

````{hint}
:title: If the graph is blank
JupyterLab does not run the scripts in an HTML file until it is
trusted, and the flame graph is drawn by a script. On Binder, in a
codespace and in the workshops' container the viewer trusts HTML files
by default; on your own JupyterLab click the **Trust HTML** button in
the viewer's toolbar. If the tab is blank though the file is trusted,
close the tab and click the action again.
````

A script's flame graph has one tower, with the script at the top.
This one has two, side by side, because the program had two kinds of
thread and `-a` sampled them all. Which of the two is the wider
depends on how busy the server was kept, so find each by the name in
its top box.

## The main thread

One tower starts at `_run_module_as_main`, which is `-m flask` being
run, and goes down through Flask's command line and Werkzeug's
`run_simple` to `serve_forever` and, at the bottom, `select`. That
is the *accept loop*: the main thread asks the operating system to
wake it when a connection arrives, and sleeps until one does. Nearly
all of the tower is that one box at the bottom. This is what a
server with `-a` left out would have shown, and all it would have
shown.

## The requests

The other tower starts at `Thread._bootstrap`, the first frame of
any thread that Python starts. Every request thread begins with
the same frames, so the profiler has laid them all over one another,
and the tower is every request of the twenty seconds added together.
Read it downward and it is the life of a request in three layers.

- **The standard library's servers.** `process_request_thread` and
  `finish_request` from `socketserver`, then `handle` and
  `handle_one_request` from `http.server`: a thread is started for
  the connection, and the request is read from it.

- **Werkzeug and Flask.** `run_wsgi` and `execute` are Werkzeug, the
  library beneath Flask that speaks HTTP. `Flask.__call__`,
  `wsgi_app`, `full_dispatch_request` and `dispatch_request` are
  Flask, working out which view the address belongs to.

- **The application.** Below `dispatch_request` the tower divides
  into the views of {open}`gazette/web.py`: `search`, `front_page`,
  `article` and `health`.

The boxes of the first two layers are all nearly as wide as the
tower. Each is wide because of what is below it, and has next to no
time of its own: the framework costs little here. The slivers that
leave the tower on its right-hand edge on the way down are what it
does cost, reading the request, writing the log line, sending the
reply.

The application's layer is where the width is shared out, and it is
not shared evenly. The boxes are labelled with a line as well as a
function, so a view has a box for each of its lines that was
sampled, and `search (gazette.web:101)` is far wider than every
other box of the layer put together. The **Hotspots** list in the
sidebar says the same with numbers.

## One thread at a time

The sidebar has a **Thread Filter**, which draws the graph of one
thread. Open it and the list is thousands of entries long, since
the development server started a thread for each request and each
lived for a few milliseconds. The first in the list is the main
thread. Any other is one request, a few samples if it has any, and
which request is a matter of luck. On this server the threads added
together are the picture worth reading.

```{quiz}
:id: read-the-server
question: "`load.py` sent one search in every ten requests. Why is `search` so much the widest of the views?"
options:
  - { text: "The profiler samples the slowest thread more often than the others", explanation: "It reads every thread at every sample, a thousand times a second, whatever the thread is doing." }
  - { text: "The width of a box is time, not the number of calls, and a search takes many times as long as any other request", correct: true }
  - { text: "The other requests were served by the main thread, in the other tower", explanation: "The main thread only accepts connections. Every request, of every kind, was served by a thread of its own." }
  - { text: "`search` is the last view in the file, so the others are drawn inside it", explanation: "Boxes are drawn beneath the function that called them. The views are side by side under `dispatch_request` because Flask called each of them." }
explanation: "A sample lands in whatever is running when it is taken, so a function's width is the time spent in it. The table `load.py` printed has the two numbers to multiply: a tenth of the requests, each taking many times as long as an article."
```
