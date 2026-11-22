#!/usr/bin/env python3
"""Validate orchestration/planner/agent-routing.json against sparks.json. Stdlib only."""
from __future__ import annotations
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def validate(routing: dict, registry: dict) -> list[str]:
    errors = []
    tools = routing.get("tools", {})
    defaults = routing.get("spark_defaults", {})
    for tool, spec in tools.items():
        if not spec.get("strengths") or not spec.get("entrypoint"):
            errors.append("tool %s needs strengths and entrypoint" % tool)
        elif not (ROOT / spec["entrypoint"]).exists():
            errors.append("tool %s entrypoint missing: %s" % (tool, spec["entrypoint"]))
    ids = {s["id"] for s in registry.get("sparks", [])}
    for sid in sorted(ids - set(defaults)):
        errors.append("%s: no default tool" % sid)
    for sid in sorted(set(defaults) - ids):
        errors.append("%s: routing for unknown spark" % sid)
    for sid, tool in defaults.items():
        if tool not in tools:
            errors.append("%s: unknown tool %s" % (sid, tool))
        elif tool == "human":
            errors.append("%s: human is not a default drafting tool" % sid)
    if not {"merge", "tag", "release"} <= set(routing.get("human_only_actions", [])):
        errors.append("merge, tag and release must stay human-only")
    return errors


def main() -> int:
    routing = json.loads((ROOT / "orchestration/planner/agent-routing.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "orchestration/sparks.json").read_text(encoding="utf-8"))
    errors = validate(routing, registry)
    for e in errors:
        print("ERROR:", e)
    print("agent routing OK" if not errors else "agent routing FAILED")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
