"""Offline qualification adapter only; calls existing checks, never authorizes writes."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def verify_sources(manifest=None):
    manifest = load("sources.json") if manifest is None else manifest
    actual = {}
    for path, expected in manifest["sha256"].items():
        resolved = (ROOT / path).resolve()
        if not resolved.is_relative_to(ROOT):
            raise ValueError("Source path escapes checkout")
        actual[path] = hashlib.sha256(resolved.read_bytes()).hexdigest()
        if actual[path] != expected:
            raise ValueError("Pinned source mismatch: " + path)
    return actual


def observe(case):
    # Verify before importing or invoking published implementations.
    verify_sources()
    from orchestration.agentic import manager
    from orchestration import worker_protocol, validate_sparks
    args = copy.deepcopy(case["arguments"])
    operation = case["operation"]
    try:
        if operation == "worker":
            for name, key in (("task", "task"), ("resolution", "report"), ("evidence", "github")):
                errors = worker_protocol.validate_schema(args[key], name)
                if errors:
                    raise ValueError("Invalid qualification fixture: " + repr(errors))
            raw = worker_protocol.evidence_check(**args)
            return {"errors": raw["errors"], "phase": raw["b00_evidence_phase"],
                    "merge_authorized": raw["merge_authorized"], "blockers": raw["worker_blockers"]}
        if operation == "collisions":
            return manager.collisions(**args)
        if operation == "intersect":
            return validate_sparks.intersect(**args)
        if operation == "subset":
            return worker_protocol.declared_subset(**args)
        if operation in ("events", "snapshot", "leases"):
            args["now"] = manager.utc(args["now"])
        if operation == "events":
            return manager.event_check(**args)
        if operation == "snapshot":
            return manager.evidence_check(**args)
        if operation == "leases":
            return list(manager.lease_state(**args))
        if operation == "attempts":
            return manager.attempts(**args)
    except manager.GuardError as error:
        return {"error": str(error)}
    raise ValueError("Unknown qualification operation: " + str(operation))


def replay(corpus=None):
    corpus = load("cases.json") if corpus is None else corpus
    before = verify_sources()
    original = copy.deepcopy(corpus)
    results = []
    for case in corpus["cases"]:
        actual = observe(case)
        repeat = observe(case)
        results.append({"id": case["id"], "operation": case["operation"],
                        "expected_disposition": case["expected_disposition"],
                        "expected_observation": case["expected_observation"],
                        "observed": actual, "matches_observation": actual == case["expected_observation"],
                        "deterministic": actual == repeat,
                        "policy_enforcement": "explicit_gap" if case["gap"] else "bounded_check_only",
                        "gap": case["gap"]})
    unchanged = corpus == original and before == verify_sources()
    return {"classification": "executed_offline_synthetic_not_operational",
            "source_commit": load("sources.json")["base_commit"],
            "source_sha256": before, "cases_executed": len(results),
            "observation_mismatches": sum(not r["matches_observation"] for r in results),
            "explicit_gaps": sum(r["policy_enforcement"] == "explicit_gap" for r in results),
            "unchanged_sources_and_inputs": unchanged, "results": results}


if __name__ == "__main__":
    result = replay()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["unchanged_sources_and_inputs"] and not result["observation_mismatches"]
                     and all(r["deterministic"] for r in result["results"]) else 1)
