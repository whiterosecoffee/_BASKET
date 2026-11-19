"""Offline source/gate revision review. Matching evidence never establishes integration."""
import argparse
import hashlib
import json
import re

SHA = re.compile(r"^[0-9a-f]{40}$")
FIELDS = {"source_head", "gate_head", "run_head", "executed_source",
          "conclusion", "run_url", "source_binding"}


def assess(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError("exact evidence fields required")
    for key in ("source_head", "gate_head", "run_head", "executed_source"):
        if not isinstance(record[key], str) or not SHA.fullmatch(record[key]):
            raise ValueError("full immutable revision required: " + key)
    if record["conclusion"] not in ("success", "failure", "cancelled", "skipped", "pending"):
        raise ValueError("unknown conclusion")
    if record["source_binding"] not in ("immutable_dependency", "reviewed_checkout"):
        raise ValueError("unknown source binding")
    if not isinstance(record["run_url"], str) or not re.fullmatch(
        r"https://github\.com/whiterosecoffee/_BASKET/actions/runs/[1-9][0-9]*",
        record["run_url"]
    ):
        raise ValueError("repository run URL required")
    blockers = []
    if record["conclusion"] != "success":
        blockers.append("run_not_successful")
    if record["run_head"] != record["gate_head"]:
        blockers.append("stale_gate_run")
    if record["executed_source"] != record["source_head"]:
        blockers.append("stale_source_execution")
    if record["source_binding"] == "reviewed_checkout" and record["executed_source"] != record["run_head"]:
        blockers.append("checkout_not_run_revision")
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {
        "component_evidence_matches": not blockers,
        "reviewed_source_exercised": not blockers and record["source_binding"] == "reviewed_checkout",
        "integration_verified": False,
        "blockers": blockers,
        "dependency_fingerprint": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence")
    args = parser.parse_args()
    try:
        with open(args.evidence, encoding="utf-8") as stream:
            result = assess(json.load(stream))
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if result["component_evidence_matches"] else 1
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
