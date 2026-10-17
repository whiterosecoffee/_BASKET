#!/usr/bin/env python3
"""Validate B00 planner schema, composable capabilities, DAG and exclusive ownership.

Requires jsonschema>=4.23.
Run: python orchestration/validate_planner.py
This reads checked-in proposals only. It cannot verify live GitHub issue status.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("basket_plan", ROOT / "orchestration/planner.py")
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


def main():
    objects = [
        ("worker-library.v1.json", "orchestration/planner/worker-library.json"),
        ("task-queue.v1.json", "orchestration/planner/queue.json"),
    ]
    errors = []
    for schema_path, payload_path in objects:
        schema = planner.load(ROOT / "schemas" / schema_path)
        payload = planner.load(ROOT / payload_path)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors.extend("%s: %s" % (payload_path, e.message) for e in
                      validator.iter_errors(payload))
    if not errors:
        queue = planner.load(ROOT / "orchestration/planner/queue.json")
        library = planner.load(ROOT / "orchestration/planner/worker-library.json")
        registry = planner.load(ROOT / "orchestration/sparks.json")
        errors.extend(planner.validate_plan(queue, library, registry))
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 1
    print(json.dumps({
        "status": "pass",
        "queue_version": queue["queue_version"],
        "library_version": library["library_version"],
        "task_count": len(queue["tasks"]),
        "profiles": len(library["profiles"]),
        "capabilities": len(library["capabilities"]),
        "recipes": len(library["recipes"]),
        "source": "checked-in proposal; GitHub state must be fetched separately",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
