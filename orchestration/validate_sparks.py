#!/usr/bin/env python3
"""Offline _BASKET spark registry validation. Stdlib only.

CI integration belongs to B01; this script is a B00-owned orchestration invariant.
Usage: python orchestration/validate_sparks.py
"""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "orchestration" / "sparks.json"


def glob_pattern(path: str) -> re.Pattern[str]:
    parts = path.split("/")
    out = []
    for i, part in enumerate(parts):
        if part == "**":
            out.append(r"(?:[^/]+/)*" if i < len(parts)-1 else r".*")
            continue
        piece = re.escape(part).replace(r"\*", "[^/]*")
        out.append(piece)
        if i < len(parts)-1:
            out.append("/")
    return re.compile("^" + "".join(out) + "$")


def witness(path: str, deep: bool = False) -> str:
    chunks = []
    for p in path.split("/"):
        if p == "**":
            chunks.extend(["folder", "child"] if deep else ["folder"])
        elif "*" in p:
            chunks.append(p.replace("*", "sample"))
        else:
            chunks.append(p)
    return "/".join(chunks)


def intersect(a: str, b: str) -> bool:
    if a == b:
        return True
    r1, r2 = glob_pattern(a), glob_pattern(b)
    for s in (witness(a), witness(a, True), witness(b), witness(b, True)):
        if r1.fullmatch(s) and r2.fullmatch(s):
            return True
    if a.endswith("/**") and b.startswith(a[:-3] + "/"):
        return True
    if b.endswith("/**") and a.startswith(b[:-3] + "/"):
        return True
    return False


def validate(registry: dict) -> list[str]:
    errors: list[str] = []
    sparks = registry.get("sparks", [])
    ids = [s.get("id") for s in sparks]
    if len(ids) != len(set(ids)):
        errors.append("duplicate spark IDs")
    known = set(ids)
    for s in sparks:
        sid = s.get("id", "?")
        if not s.get("write_paths"):
            errors.append(f"{sid}: empty write paths")
        if not "Create a NEW GitHub issue" in s.get("launch_prompt", ""):
            errors.append(f"{sid}: launch prompt does not enforce a new issue")
        if "work/<issue-number>-<objective-slug>" not in s.get("launch_prompt", ""):
            errors.append(f"{sid}: launch prompt does not enforce issue-scoped branch")
        for dep in s.get("dependencies", []):
            if dep not in known:
                errors.append(f"{sid}: missing dependency {dep}")
        if sid in s.get("dependencies", []):
            errors.append(f"{sid}: self dependency")
    ownership = [(s["id"], p) for s in sparks for p in s["write_paths"]]
    for i, (owner, path) in enumerate(ownership):
        for other, opath in ownership[i+1:]:
            if owner != other and intersect(path, opath):
                errors.append(f"overlapping write ownership {owner}:{path} vs {other}:{opath}")
    graph = {s["id"]: s.get("dependencies", []) for s in sparks}
    gray, black = set(), set()
    def visit(v: str) -> None:
        if v in gray:
            errors.append(f"dependency cycle at {v}")
            return
        if v in black:
            return
        gray.add(v)
        for nxt in graph.get(v, []):
            if nxt in graph:
                visit(nxt)
        gray.remove(v)
        black.add(v)
    for id_ in ids:
        visit(id_)
    return errors


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    failures = validate(registry)
    if failures:
        for e in failures:
            print("ERROR:", e, file=sys.stderr)
        return 1
    print(f"Validated {len(registry['sparks'])} sparks / "
          f"{sum(len(x['write_paths']) for x in registry['sparks'])} write patterns; "
          "no overlapping owners or dependency cycles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
