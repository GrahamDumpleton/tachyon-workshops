"""Send requests to the gazette's web site, as its readers would.

Eight readers each ask for one page after another, three articles
for every search, until the time is up or the server stops
answering. Then the number of requests of each kind is printed, with
how long they took.

    python load.py 8083             until the server stops
    python load.py 8083 10          for ten seconds
    python load.py 8083 10 search   searches only
"""

import random
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request

READERS = 8
KINDS = ["article", "article", "article", "search"]
WORDS = ["council", "city", "report", "plan", "week", "local", "people", "year"]


def path_for(kind, rng):
    if kind == "article":
        return f"/article/{rng.randrange(1, 2001)}"
    return f"/search?q={rng.choice(WORDS)}"


def reader(number, base, kinds, deadline, timings, stopped):
    rng = random.Random(number)
    while not stopped.is_set() and time.monotonic() < deadline:
        kind = rng.choice(kinds)
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(base + path_for(kind, rng), timeout=30) as reply:
                reply.read()
        except urllib.error.HTTPError:
            pass
        except OSError:
            stopped.set()
            return
        timings[kind].append(time.perf_counter() - started)


def main(port, seconds=None, only=None):
    base = f"http://127.0.0.1:{port}"
    kinds = [only] if only else KINDS
    try:
        urllib.request.urlopen(base + "/health", timeout=5).close()
    except OSError:
        sys.exit(f"Nothing answers on port {port}. Start the server, then run this again straight away.")
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
