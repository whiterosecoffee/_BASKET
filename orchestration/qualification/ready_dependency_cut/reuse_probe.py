"""Read-only second consumer of PR256's pinned in-memory API; no validator replica."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

REVISION = "2f395d475abace7fe58afbb9f0c5fa3d596c25e2"
PREFIX = "orchestration/qualification/run_receipts/"
PINS = {
    "validate.py": "3af3b3323c2f4f6dfc8503cb370639deb61727ed218356ea254292ca21f847c2",
    "receipt.schema.json": "bb47ef1f80e028f503e190c5870d7345e463853f3c34c1c67b81702658f32258",
}


def load_validator(repo):
    # Only immutable Git objects are read; never import the other owner's worktree.
    files = {}
    for name, expected in PINS.items():
        raw = subprocess.check_output(
            ["git", "-C", str(repo), "show", REVISION + ":" + PREFIX + name])
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("source hash mismatch: " + name)
        files[name] = raw.decode("utf-8")
    # Initialize dependencies before substituting this one schema read.
    from jsonschema import Draft202012Validator  # noqa: F401
    original = Path.read_text
    virtual = Path("/virtual/ready-dependency-cut-consumer")

    def read(path, *args, **kwargs):
        if path == virtual / "receipt.schema.json":
            return files["receipt.schema.json"]
        return original(path, *args, **kwargs)

    namespace = {"__file__": str(virtual / "validate.py"), "__name__": "pinned_receipt_consumer"}
    with patch.object(Path, "read_text", read):
        exec(compile(files["validate.py"], namespace["__file__"], "exec"), namespace)
    return namespace["validate"]


def exercise(validate):
    base = {
        "schema": "run_receipt.qualification@1",
        "run_id": "synthetic-second-consumer-252",
        "checked_at": "2026-11-19T00:00:00Z",
        "subject_revision": "a" * 40,
        "sources": [{"source_id": "synthetic-design-proposal",
                     "checked_at": "2026-11-19T00:00:00Z",
                     "revision": "a" * 40, "watermark": None}],
        "new_deltas": [], "outcome_state": "monitoring_only",
        "owner": "synthetic-design-review-consumer", "evidence": [],
        "test_evidence": [], "acceptance_evidence": [],
        "next_action": "Obtain independent exact-revision review.",
        "blocker": None, "recheck_condition": "New attributable review receipt",
    }
    results = []

    def check(name, value, expected):
        before = copy.deepcopy(value)
        verdict = validate(value)
        checks = {
            "expected_verdict": verdict["valid"] is expected,
            "no_truth_promotion": verdict["claims_verified"] is False,
            "structural_only": verdict["validation_scope"] == "structural_only",
            "input_unchanged": value == before,
            "deterministic_repeat": verdict == validate(value),
        }
        results.append({"id": name, "expected_valid": expected,
                        "checks": checks, "passed": all(checks.values())})

    check("monitoring", base, True)
    for state in ("tested", "accepted"):
        value = copy.deepcopy(base)
        value["outcome_state"] = state
        check(state + "-without-evidence", value, False)
    value = copy.deepcopy(base)
    value["outcome_state"] = "awaiting_approval"
    check("approval-without-authority", value, False)
    value["blocker"] = {"reason": "Synthetic gate", "action": "Synthetic adoption",
                        "unblock_condition": "Explicit scoped approval",
                        "approval_authority": "synthetic-owner"}
    check("explicit-approval-blocker", value, True)
    value = copy.deepcopy(base)
    value["next_action"] = "Different action"
    check("conflicting-duplicate", [base, value], False)
    check("identical-duplicate", [base, copy.deepcopy(base)], True)
    value = copy.deepcopy(base)
    value["outcome_state"] = "accepted"
    value["acceptance_evidence"] = ["review"]
    value["evidence"] = [{
        "id": "review", "kind": "acceptance", "tier": "published",
        "execution": "manual_review", "result": "pass", "revision": "b" * 40,
        "artifact": "https://example.invalid/review", "criterion": "Synthetic criterion",
        "reviewer": "synthetic-reviewer",
    }]
    check("foreign-revision", value, False)
    value["evidence"][0]["revision"] = base["subject_revision"]
    check("well-shaped-fiction-remains-unverified", value, True)
    return {
        "source_revision": REVISION, "source_sha256": PINS,
        "input_kind": "synthetic", "execution": "local_in_memory_api",
        "case_count": len(results), "passed": sum(r["passed"] for r in results),
        "failed": sum(not r["passed"] for r in results),
        "cases": results, "independent_acceptance": False, "operational": False,
        "limits": ["Exact-path schema read supplied in memory; CLI not exercised.",
                   "Structural assertions do not authenticate any receipt.",
                   "No other-owner worktree bytes, unpublished candidate, network, or writes used."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", required=True,
                        help="Existing Git checkout containing the published source revision")
    args = parser.parse_args()
    result = exercise(load_validator(args.source_repo))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
