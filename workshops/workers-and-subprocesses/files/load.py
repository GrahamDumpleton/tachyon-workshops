"""Send requests to the gazette's web site, as its readers would.

Four readers each ask for a page fifty times a second, a mixture of
the front page, articles and searches, until the time is up or the
server stops answering. Then the number of requests of each kind is
printed, with how long they took. The pace is fixed, so a server
that answers more quickly is sent the same requests and no more.

    python load.py 8081            until the server stops
    python load.py 8081 10         for ten seconds
    python load.py 8081 10 search  searches only
"""

import random
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request

READERS = 4
PACE = 0.02
WORDS = ["council", "city", "report", "plan", "week", "local", "people", "year"]
KINDS = ["front"] * 3 + ["article"] * 5 + ["search", "health"]


def path_for(kind, rng):
    if kind == "front":
        return "/"
    if kind == "article":
        return f"/article/{rng.randrange(1, 2001)}"
    if kind == "search":
        return f"/search?q={rng.choice(WORDS)}"
    return "/health"


def reader(number, base, kinds, deadline, timings, stopped):
    rng = random.Random(number)
    due = time.monotonic()
    while not stopped.is_set() and due < deadline:
        time.sleep(max(0.0, due - time.monotonic()))
        due += PACE
        kind = rng.choice(kinds)
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(base + path_for(kind, rng), timeout=10) as reply:
                reply.read()
        except urllib.error.HTTPError:
            pass
        except OSError:
            stopped.set()
            return
        timings[kind].append(time.perf_counter() - started)


def main(port, seconds=None, only=None):
    base = f"http://127.0.0.1:{port}"
    try:
        urllib.request.urlopen(base + "/health", timeout=5).close()
    except OSError:
        sys.exit(f"Nothing answers on port {port}. Start the server, then run this again straight away.")
    kinds = [only] if only else KINDS
    deadline = time.monotonic() + (float(seconds) if seconds else 3600)
    timings = {kind: [] for kind in dict.fromkeys(kinds)}
    stopped = threading.Event()
    started = time.monotonic()
    threads = [
        threading.Thread(target=reader, args=(n, base, kinds, deadline, timings, stopped))
        for n in range(READERS)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    elapsed = time.monotonic() - started
    total = sum(len(times) for times in timings.values())
    if stopped.is_set():
        print(f"The server stopped answering after {elapsed:.1f} seconds.")
    print(f"{total} requests in {elapsed:.1f} seconds from {READERS} readers")
    print(f"{'page':<10}{'requests':>10}{'median':>12}{'slowest':>12}")
    for kind, times in timings.items():
        if times:
            print(
                f"{kind:<10}{len(times):>10}"
                f"{statistics.median(times) * 1000:>9.1f} ms"
                f"{max(times) * 1000:>9.1f} ms"
            )


if __name__ == "__main__":
    main(*sys.argv[1:])
