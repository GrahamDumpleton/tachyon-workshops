"""Print the hottest lines in a profile the sampling profiler wrote as JSONL.

Usage: python hottest.py profile.jsonl
"""

import json
import sys
from pathlib import Path


def main(path, count=10):
    strings, frames, entries, total = {}, {}, [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record["type"] == "string_table":
                strings.update((s["str_id"], s["value"]) for s in record["strings"])
            elif record["type"] == "frame_table":
                frames.update((frame["frame_id"], frame) for frame in record["frames"])
            elif record["type"] == "agg":
                entries.extend(record["entries"])
                total = record["samples_total"]
    entries.sort(key=lambda entry: entry["self"], reverse=True)
    for entry in entries[:count]:
        frame = frames[entry["frame_id"]]
        where = f"{Path(strings[frame['path_str_id']]).name}:{frame['line']}"
        print(f"{entry['self'] / total:6.1%}  {where:<18} {strings[frame['func_str_id']]}")


if __name__ == "__main__":
    main(*sys.argv[1:])
