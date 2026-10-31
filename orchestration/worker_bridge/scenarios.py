"""Injected collision/clock/recovery tests against the exact existing controller.

These cases are deliberately synthetic tests, never live claims or host restarts.
"""
import copy
import datetime as dt
import json
from pathlib import Path

from .bridge import (ROOT, UTC, Blocked, assert_fence, digest, git, load_controller, prepare)


def demonstrate(controller, task, issue, library, catalog, evidence, events, root, now):
    tid = f'T-{task["issue"]["number"]:03d}'
    token = next(e["event_id"] for e in reversed(events) if e["type"] == "lease_granted")
    def run(source=evidence):
        return prepare(controller, task, issue, library, catalog, source, events, token,
                       ["contract_governance", "implementation"], root, now, "contract_engineer",
                       attempt_id=controller.attempts(events, tid)["last_attempt"])
    original = digest(evidence)
    baseline = run()
    cases = []
    actual = copy.deepcopy(evidence)
    actual["pull_requests"].append({"number": 999999, "url": "https://github.com/example/synthetic/999999",
                                   "state": "open", "draft": True, "merged": False,
                                   "head_sha": "a" * 40, "head_branch": "test-only-fixture", "base_branch": "main",
                                   "changed_paths": ["orchestration/worker_bridge/collision-fixture.py"]})
    declared = copy.deepcopy(evidence)
    declared["declared_claims"].append({"issue": 999999, "write_paths": ["orchestration/worker_bridge/**"]})
    for name, source, expected in [("actual_pr_collision", actual, "actual_pr_collision"),
                                   ("declared_scope_collision", declared, "declared_collision")]:
        try:
            run(source)
        except Blocked as exc:
            assert exc.code == expected, str(exc)
            cases.append({"case": name, "result": "pass", "rejected_with": exc.code})
        else:
            raise AssertionError("Collision was not rejected")
        restored = run()
        assert restored["assignment_sha256"] == baseline["assignment_sha256"]
        cases.append({"case": name + "_recovery", "result": "pass",
                      "action": "Remove only injected fixture; original owner/source remains unchanged"})
    # Simulated loss/restart: owner acknowledges the prior lease, then issues a
    # replacement event ID. This is not evidence of a real hosted worker restart.
    replacement = copy.deepcopy(events)
    stamp = now.isoformat()
    replacement.append({"schema": controller.EVENT_SCHEMA, "event_id": "TEST-release", "task_id": tid,
                        "type": "lease_released", "at": stamp, "verified_by": "test-only owner acknowledgement"})
    replacement.append({"schema": controller.EVENT_SCHEMA, "event_id": "TEST-new-fence", "task_id": tid,
                        "type": "lease_granted", "at": stamp, "issue": task["issue"]["number"],
                        "branch": task["branch"]["name"], "expires_at": (now+dt.timedelta(minutes=5)).isoformat()})
    try:
        assert_fence(controller, replacement, tid, token, now)
    except Blocked as exc:
        assert exc.code == "stale_fence"
        cases.append({"case": "stale_fencing_token", "result": "pass", "rejected_with": exc.code})
    else:
        raise AssertionError("Old fence accepted")
    assert_fence(controller, replacement, tid, "TEST-new-fence", now)
    cases.append({"case": "owner_acknowledged_test_recovery", "result": "pass"})
    try:
        assert_fence(controller, replacement, tid, "TEST-new-fence", now+dt.timedelta(minutes=6))
    except Blocked as exc:
        assert exc.code == "lease_expired"
        cases.append({"case": "expired_lease", "result": "pass", "simulated_clock": True})
    else:
        raise AssertionError("Expired lease accepted")
    drift = json.loads((ROOT / "orchestration/worker_bridge/controller-lock.json").read_text())
    drift["files"]["orchestration/agentic/manager.py"] = "0" * 64
    try:
        # root is the worker checkout; use the separately pinned dependency path.
        load_controller(Path(controller.__file__).resolve().parents[2], drift)
    except Blocked as exc:
        assert exc.code == "controller_fingerprint"
        cases.append({"case": "source_fingerprint_drift", "result": "pass", "rejected_with": exc.code})
    else:
        raise AssertionError("Source drift accepted")
    assert original == digest(evidence)
    return {"classification": "synthetic_negative_tests_not_live_ownership_or_host_recovery",
            "controller_sha": git(Path(controller.__file__).resolve().parents[2], "rev-parse", "HEAD"),
            "source_evidence_sha256": original, "cases": cases, "case_count": len(cases)}
