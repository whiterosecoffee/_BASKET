#!/usr/bin/env python3
"""Require every agent entry point to be a byte-identical copy of AGENT_INSTRUCTIONS.md."""
from __future__ import annotations
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANONICAL = "orchestration/AGENT_INSTRUCTIONS.md"
COPIES = ["CLAUDE.md", ".github/copilot-instructions.md"]


def validate(root: pathlib.Path = ROOT) -> list[str]:
    errors = []
    canon = root / CANONICAL
    if not canon.exists():
        return ["missing " + CANONICAL]
    text = canon.read_bytes()
    for rel in COPIES:
        path = root / rel
        if not path.exists():
            errors.append("missing " + rel)
        elif path.read_bytes() != text:
            errors.append("%s differs from %s" % (rel, CANONICAL))
    return errors


def main() -> int:
    errors = validate()
    for e in errors:
        print("ERROR:", e)
    print("agent entry points OK" if not errors else "agent entry points FAILED")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
