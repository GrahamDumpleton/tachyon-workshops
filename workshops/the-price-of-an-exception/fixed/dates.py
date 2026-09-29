"""Report how long the gazette's articles take to reach print, by desk.

Usage: python gazette/dates.py [data/filings.csv.gz]

Every filing of an article carries four dates: written, filed,
published and last revised. The desk that filed it writes them its
own way: the newsroom as 2026-03-14, the archive as 14/03/2026 and
the wire agencies as 14 March 2026.
"""

import csv
import gzip
import sys
import time
from datetime import datetime


def load_filings(path):
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_date(text):
    if "-" in text:
        layout = "%Y-%m-%d"
    elif "/" in text:
        layout = "%d/%m/%Y"
    else:
        layout = "%d %B %Y"
    return datetime.strptime(text, layout)


def days_between(filings):
    to_print = {}
    to_settle = {}
    for filing in filings:
        written = parse_date(filing["written"])
        filed = parse_date(filing["filed"])
        published = parse_date(filing["published"])
        revised = parse_date(filing["revised"])
        desk = filing["desk"]
        to_print.setdefault(desk, []).append((published - written).days + (published - filed).days)
        to_settle.setdefault(desk, []).append((revised - published).days)
    return {
        desk: (sum(to_print[desk]) / len(to_print[desk]) / 2, sum(to_settle[desk]) / len(to_settle[desk]))
        for desk in to_print
    }


def main(path="data/filings.csv.gz"):
    started = time.perf_counter()
    filings = load_filings(path)
    desks = days_between(filings)
    print(f"{len(filings)} filings from {len(desks)} desks")
    for desk, (to_print, to_settle) in sorted(desks.items()):
        print(f"  {desk:<10} {to_print:4.1f} days to print, {to_settle:4.1f} more to the last revision")
    print(f"Dates parsed in {time.perf_counter() - started:.1f} seconds")


if __name__ == "__main__":
    main(*sys.argv[1:])
