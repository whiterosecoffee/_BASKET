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
from pathlib import Path
import importlib.util

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
            else:
                phase, action, owner = "dispatch_ready", "Start one new domain conversation using task recipe, then claim issue and unique branch.", "B00"
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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queue", default=str(ROOT / "orchestration/planner/queue.json"))
    ap.add_argument("--library", default=str(ROOT / "orchestration/planner/worker-library.json"))
    ap.add_argument("--registry", default=str(ROOT / "orchestration/sparks.json"))
    ap.add_argument("--evidence", default=str(ROOT / "orchestration/examples/github-evidence-2026-10-16.json"))
    ap.add_argument("--active", action="append", default=None)
    args = ap.parse_args()
    q, l, r, e = (planner.load(p) for p in
                  (args.queue, args.library, args.registry, args.evidence))
    print(json.dumps(reconcile(q, l, r, e, args.active), indent=2))


if __name__ == "__main__":
    main()
