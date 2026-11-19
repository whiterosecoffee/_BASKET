#!/usr/bin/env python3
"""Detect more than one open issue/PR claiming the same spark. Offline, stdlib only.

A claim is a spark ID in a leading "[Bxx...]" title tag or a "spark:Bxx" label.
[HANDOFF X->Y] issues claim nothing for the sender; the receiver is Y only when
it picks the work up, so handoff titles are ignored. Output is evidence for B00,
not a capacity count.
Usage: python orchestration/spark_claims.py issues.json  (list of {number,title,labels,state})
"""
from __future__ import annotations
import json
import re
import sys

TAG = re.compile(r"^\s*\[(B\d{2})(?:[^\]]*)\]")
LABEL = re.compile(r"^spark:(B\d{2})$")


def claimed_spark(item: dict) -> str | None:
    title = item.get("title", "")
    if title.upper().lstrip("[ ").startswith("HANDOFF"):
        return None
    for label in item.get("labels", []):
        name = label.get("name", "") if isinstance(label, dict) else str(label)
        match = LABEL.match(name)
        if match:
            return match.group(1)
    match = TAG.match(title)
    return match.group(1) if match else None


def find_conflicts(items: list[dict]) -> dict[str, list[int]]:
    claims: dict[str, list[int]] = {}
    for item in items:
        if str(item.get("state", "open")).lower() != "open":
            continue
        spark = claimed_spark(item)
        if spark:
            claims.setdefault(spark, []).append(item["number"])
    return {s: sorted(n) for s, n in claims.items() if len(n) > 1}


def main(argv: list[str]) -> int:
    items = json.load(open(argv[1], encoding="utf-8"))
    conflicts = find_conflicts(items)
    for spark, numbers in sorted(conflicts.items()):
        print("%s claimed by open items: %s" % (spark, ", ".join("#%d" % n for n in numbers)))
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
