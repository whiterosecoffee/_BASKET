#!/usr/bin/env python3
"""B00 execution-loop controller: pure deterministic action/QC plan, no writes.

Run from repo root:
python orchestration/execution_loop.py --evidence orchestration/examples/github-evidence-2026-10-16.json
Requires jsonschema for the existing worker protocol evaluator (not for planner).
No GitHub mutations, merges, remote worker launches or background scheduling.
"""
from __future__ import annotations
import argparse
import json
import shlex
from pathlib import Path
import importlib.util
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def imported(name, relpath):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


planner = imported("basket_planner", "orchestration/planner.py")
QC = (
    ("Q0", "Claim identity, issue and one permitted branch"),
    ("Q1", "Static schemas, owner scope and dependency checks"),
    ("Q2", "Behavioral unit tests and adversarial negative tests"),
    ("Q3", "Source provenance, temporal availability and currency/TTD"),
    ("Q4", "All mandatory independent checks passed at exact PR SHA"),
    ("Q5", "Reviewed and explicitly authorized integration"),
    ("Q6", "Main CI and dependent replay after authorized merge"),
)


def reconcile(queue, library, registry, evidence, active_ids=None):
    plan = planner.run_plan(queue, library, registry, evidence, active_ids)
    actions = []
    for item in plan["ordered_tasks"]:
        if item["state"] in ("integrated_main_ci_verified",):
            phase, action, owner = "accepted", "Verify downstream acceptance and release only by explicit authorization.", "B00"
        elif item["state"] == "integrated_main_ci_unverified":
            phase, action, owner = "post_merge_qc", "Verify all required checks and actual main-commit CI, then advance dependents.", "B01"
        elif item["state"] == "review_ready_ci_green":
            phase, action, owner = "approval_review", "Review PR diff, test scope, evidence and mandatory checks; obtain explicit merge authorization.", "B00"
        elif item["state"] == "review_required_checks_pending":
            phase, action, owner = "qc_rework", "Run missing exact-head mandatory CI and record failed/skipped tests.", item["spark_id"]
        elif item["state"] == "resume_incomplete":
            phase, action, owner = "qc_rework", "Return failing or unverified domain acceptance criteria to the SAME worker task; run domain checks.", item["spark_id"]
        elif item["state"] == "ready_new_worker":
            if plan["worker_slots_remaining"] is None:
                phase, action, owner = "capacity_unknown", "Confirm active code-writing workers before dispatch.", "B00"
            elif plan["worker_slots_remaining"] <= 0:
                phase, action, owner = "capacity_full", "Finish or pause a current writer before starting a new conversation.", "B00"
            elif item["id"] != plan["next_new_worker"]:
                phase, action, owner = "queued_for_slot", "Preserve priority order; do not dispatch until a worker slot is available.", "B00"
            else:
                phase, action, owner = "dispatch_ready", "Start exactly one new domain conversation using the task recipe and claim a unique issue/branch.", "B00"
        elif item["state"] in ("blocked_upstream", "evidence_unavailable"):
            phase, action, owner = "blocked", "Collect missing evidence or satisfy explicit dependency gates; do not infer completion.", "B00"
        else:
            phase, action, owner = "unverified", "Verify task claim and current GitHub evidence before any transition.", "B00"
        actions.append({
            "task_id": item["id"], "spark_id": item["spark_id"],
            "state_from_evidence": item["state"], "qc_phase": phase,
            "next_action": action, "action_owner": owner,
            "blocking_dependencies": item["blocking_dependencies"],
            "required_gates": [g[0] for g in QC],
            "merge_authorized": False,
            "automatic_issue_creation": False,
        })
    return {
        "schema": "basket.execution_review@1",
        "queue_version": plan["queue_version"],
        "source_evidence_observed_at": plan["source_evidence_observed_at"],
        "source_fetched_this_invocation": False,
        "worker_slots_remaining": plan["worker_slots_remaining"],
        "next_orchestrator_action": plan["next_orchestrator_action"],
        "next_new_worker": plan["next_new_worker"],
        "qc_gate_definitions": [{"id": gate, "criterion": meaning} for gate, meaning in QC],
        "actions": actions,
        "side_effects_executed": [],
        "approval_required_for_merge": True
    }



# Explicit policy: a priority score never grants mutation permission.
DECISION_CLASS = {
    "accepted": "automatic_safe",
    "post_merge_qc": "requires_evidence",
    "approval_review": "requires_authorization",
    "qc_rework": "requires_owner",
    "dispatch_ready": "requires_owner",
    "capacity_unknown": "requires_evidence",
    "capacity_full": "requires_owner",
    "queued_for_slot": "requires_owner",
    "blocked": "requires_evidence",
    "unverified": "requires_evidence",
}
SAFE_LOCAL_CHECKS = (
    ("planner_structure", "python orchestration/validate_planner.py"),
    ("orchestration_unit_tests",
     "python -m unittest discover -s orchestration/tests -p 'test_*.py' -v"),
    ("worker_scope", "python orchestration/validate_worker_scopes.py"),
    ("worker_attempts", "python orchestration/validate_worker_attempts.py"),
)


def decide_next(review, *, fresh_evidence=False):
    """Pure next-step decision. Never executes commands or mutates GitHub."""
    decisions = []
    for item in review["actions"]:
        category = DECISION_CLASS[item["qc_phase"]]
        if not fresh_evidence and category == "automatic_safe":
            category = "requires_evidence"
        decisions.append({
            "task_id": item["task_id"],
            "decision_class": category,
            "reason": item["next_action"],
            "blockers": item["blocking_dependencies"],
        })
    selected = next((x for x in decisions
                     if x["decision_class"] == "automatic_safe"), None)
    if selected is None:
        selected = next((x for x in decisions
                         if x["decision_class"] != "requires_authorization"
                         and not x["blockers"]), None)
    return {
        "schema": "basket.execution_decision@1",
        "queue_version": review["queue_version"],
        "fresh_evidence_confirmed": bool(fresh_evidence),
        "selected": selected,
        "ordered_decisions": decisions,
        "safe_local_checks": [{"id": key, "command": cmd}
                              for key, cmd in SAFE_LOCAL_CHECKS],
        "checks_executed": [],
        "side_effects_executed": [],
        "automatic_merge": False,
        "automatic_release": False,
        "automatic_trade": False,
        "automatic_worker_launch": False,
    }




def run_safe_checks(*, runner=None, check_ids=None, timeout_seconds=120):
    """Execute only hardcoded repo-local validators, recording every outcome.

    A failing validator does not prevent independent validators from running.
    The caller controls when this bounded, opt-in operation is invoked.
    """
    allowed = {name: command for name, command in SAFE_LOCAL_CHECKS}
    selected = list(allowed) if check_ids is None else list(check_ids)
    if len(selected) != len(set(selected)) or any(x not in allowed for x in selected):
        raise ValueError("unknown or repeated safe check")
    if not 1 <= timeout_seconds <= 600:
        raise ValueError("timeout must be between 1 and 600 seconds")
    if runner is None:
        def runner(argv, **kwargs):
            return subprocess.run(argv, **kwargs)
    results = []
    for name in selected:
        command = allowed[name]
        # Never run a shell or execute arbitrary commands from queue/issue text.
        argv = ([sys.executable] + shlex.split(command)[1:])
        start = time.monotonic()
        try:
            proc = runner(argv, cwd=str(ROOT), capture_output=True,
                          text=True, timeout=timeout_seconds, check=False)
            status = "passed" if proc.returncode == 0 else "failed"
            code = proc.returncode
            output = (proc.stdout or "")[-3000:]
            error = (proc.stderr or "")[-3000:]
        except subprocess.TimeoutExpired:
            status, code, output, error = "timeout", None, "", "validator timed out"
        except OSError as exc:
            status, code, output, error = "unavailable", None, "", str(exc)
        results.append({
            "id": name, "status": status, "exit_code": code,
            "duration_seconds": round(time.monotonic() - start, 3),
            "stdout_tail": output, "stderr_tail": error,
        })
    return {
        "schema": "basket.local_check_result@1",
        "results": results,
        "all_passed": all(x["status"] == "passed" for x in results),
        "checks_executed": [x["id"] for x in results],
        "mutating_actions_executed": [],
    }



def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queue", default=str(ROOT / "orchestration/planner/queue.json"))
    ap.add_argument("--library", default=str(ROOT / "orchestration/planner/worker-library.json"))
    ap.add_argument("--registry", default=str(ROOT / "orchestration/sparks.json"))
    ap.add_argument("--evidence", default=str(ROOT / "orchestration/examples/github-evidence-2026-10-16.json"))
    ap.add_argument("--active", action="append", default=None)
    ap.add_argument("--run-safe-checks", action="store_true",
                    help="Opt-in: execute fixed local validators and record outcomes")
    args = ap.parse_args()
    q, l, r, e = (planner.load(p) for p in
                  (args.queue, args.library, args.registry, args.evidence))
    review = reconcile(q, l, r, e, args.active)
    result = {"review": review, "decision": decide_next(review)}
    if args.run_safe_checks:
        result["local_checks"] = run_safe_checks()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
