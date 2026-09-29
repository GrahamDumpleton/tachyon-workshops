"""Checksum every subscriber's copy of the archive, on four threads.

Usage: python gazette/checksums.py [threads] [data/articles.json]

Each subscriber's copy of the archive is stamped with their number,
and the SHA-256 of the stamped copy is what they check their download
against.
"""

import hashlib
import sys
import threading
import time

SUBSCRIBERS = 6000


def load_archive(path):
    with open(path, "rb") as f:
        return f.read()


def checksum(subscriber, archive):
    digest = hashlib.sha256(f"subscriber {subscriber}\n".encode("ascii"))
    digest.update(archive)
    return digest.hexdigest()


def worker(subscribers, archive, checksums):
    for subscriber in subscribers:
        checksums[subscriber] = checksum(subscriber, archive)


def main(threads="4", path="data/articles.json"):
    count = int(threads)
    started = time.perf_counter()
    archive = load_archive(path)
    checksums = {}
    subscribers = range(SUBSCRIBERS)
    workers = [
        threading.Thread(target=worker, args=(subscribers[n::count], archive, checksums), name=f"worker-{n}")
        for n in range(count)
    ]
    for thread in workers:
        thread.start()
    for thread in workers:
        thread.join()
    print(f"Made {len(checksums)} checksums of {len(archive) / 1e6:.1f} MB on {count} {"thread" if count == 1 else "threads"} "
          f"in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
