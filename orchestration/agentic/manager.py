"""_BASKET evidence-gated project manager. B00-owned; no implicit remote writes."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

REPO = "whiterosecoffee/_BASKET"
EVENT_SCHEMA = "basket.agentic_event@1"
PRIORITIES = {"P0": 3, "P1": 2, "P2": 1}
UTC = dt.timezone.utc

class GuardError(ValueError):
    """A missing or contradictory prerequisite; never silently proceed."""

def utc(value):
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("timezone required")
        return parsed.astimezone(UTC)
    except (AttributeError, ValueError) as error:
        raise GuardError("invalid or timezone-free timestamp") from error

def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def evidence_check(evidence, now, max_age_seconds=900):
    if evidence.get("repository") != REPO or evidence.get("schema") != "basket.github_evidence@1":
        raise GuardError("wrong repository or evidence contract")
    if evidence.get("capture_mode") != "live_connector":
        raise GuardError("historical fixture cannot authorize operations")
    age = (now.astimezone(UTC) - utc(evidence.get("observed_at"))).total_seconds()
    if age < -60 or age > max_age_seconds:
        raise GuardError("GitHub snapshot expired or future dated")
    if not re.fullmatch("[a-f0-9]{40}", str(evidence.get("main_commit", ""))):
        raise GuardError("missing main commit")
    if any(not isinstance(evidence.get(key), list) for key in ("issues", "pull_requests", "workflow_runs")):
        raise GuardError("incomplete GitHub inventory")
    for pr in evidence["pull_requests"]:
        if not isinstance(pr.get("number"), int) or not isinstance(pr.get("changed_paths"), list):
            raise GuardError("PR missing complete changed-file inventory")
        if not re.fullmatch("[a-f0-9]{40}", str(pr.get("head_sha", ""))):
            raise GuardError("PR head SHA missing")
        if pr.get("state") not in ("open", "closed") or type(pr.get("merged")) is not bool:
            raise GuardError("PR status unknown")
    if len({p["number"] for p in evidence["pull_requests"]}) != len(evidence["pull_requests"]):
        raise GuardError("duplicate pull request in snapshot")

def validate_queue(queue):
    if not 1 <= queue.get("active_worker_limit", 0) <= 20:
        raise GuardError("invalid worker limit")
    tasks = queue.get("tasks")
    if not isinstance(tasks, list):
        raise GuardError("missing tasks")
    by_id = {}
    for task in tasks:
        tid = task.get("id")
        if tid in by_id or not re.fullmatch("T-[0-9]{3,}", str(tid)):
            raise GuardError("duplicated or invalid task ID")
        if task.get("priority") not in PRIORITIES:
            raise GuardError("invalid priority")
        if task.get("mode") not in ("orchestrator_review", "resume_existing_worker", "launch_new_worker"):
            raise GuardError("invalid task mode")
        if not isinstance(task.get("acceptance"), list) or not task["acceptance"]:
            raise GuardError("acceptance criteria required")
        if not isinstance(task.get("depends_on"), list) or not isinstance(task.get("write_scope"), list):
            raise GuardError("scope/dependency required")
        by_id[tid] = task
    busy, done = set(), set()
    def visit(tid):
        if tid in busy:
            raise GuardError("dependency cycle")
        if tid in done:
            return
        busy.add(tid)
        for dep in by_id[tid]["depends_on"]:
            if dep.get("task_id") not in by_id or dep.get("gate") not in ("merged", "issue_exists", "ci_passed_on_head"):
                raise GuardError("unknown dependency or gate")
            visit(dep["task_id"])
        busy.remove(tid)
        done.add(tid)
    for tid in by_id:
        visit(tid)
    return by_id

def path_matches(pattern, path):
    if not isinstance(pattern, str) or ".." in pattern or "\\" in pattern:
        raise GuardError("invalid path scope")
    result, pos = [], 0
    while pos < len(pattern):
        if pattern.startswith("**/", pos):
            result.append("(?:.*/)?")
            pos += 3
        elif pattern.startswith("**", pos):
            result.append(".*")
            pos += 2
        elif pattern[pos] == "*":
            result.append("[^/]*")
            pos += 1
        else:
            result.append(re.escape(pattern[pos]))
            pos += 1
    return re.fullmatch("".join(result), path) is not None

def collisions(scope, evidence, own_pr=None):
    return [{"pr": p["number"], "path": path}
            for p in evidence["pull_requests"]
            if p["state"] == "open" and not p["merged"] and p["number"] != own_pr
            for path in p["changed_paths"] if any(path_matches(pattern, path) for pattern in scope)]

def event_check(events, now):
    valid_types = {"lease_granted", "lease_heartbeat", "lease_released", "lease_expired_verified",
                   "capacity_reconciled", "attempt_started", "attempt_passed", "attempt_failed",
                   "acceptance_verified", "deliverable_registered", "deliverable_superseded",
                   "handoff_requested", "evidence_checked"}
    previous, ids = dt.datetime(1970, 1, 1, tzinfo=UTC), set()
    for ev in events:
        if ev.get("schema") != EVENT_SCHEMA or ev.get("type") not in valid_types:
            raise GuardError("unknown journal event")
        if not ev.get("event_id") or ev["event_id"] in ids:
            raise GuardError("duplicated journal ID")
        ids.add(ev["event_id"])
        at = utc(ev.get("at"))
        if at < previous or at > now + dt.timedelta(seconds=60):
            raise GuardError("out-of-order or future journal event")
        previous = at
        if not isinstance(ev.get("task_id"), str):
            raise GuardError("event must name task")
        if ev["type"] in ("lease_granted", "lease_heartbeat"):
            if not isinstance(ev.get("issue"), int) or not str(ev.get("branch", "")).startswith("work/%d-" % ev["issue"]):
                raise GuardError("lease requires unique worker issue and branch")
            if utc(ev.get("expires_at")) <= at:
                raise GuardError("lease expiration must follow heartbeat")
        if ev["type"] == "capacity_reconciled":
            if not isinstance(ev.get("verified_active_task_ids"), list) or not ev.get("source_url") or not ev.get("verified_by"):
                raise GuardError("capacity requires verifiable attestation")
        if ev["type"] in ("attempt_started", "attempt_passed", "attempt_failed"):
            if not re.fullmatch("ATT-[a-zA-Z0-9_.-]+", str(ev.get("attempt_id", ""))):
                raise GuardError("immutable attempt ID required")
            if not ev.get("step_id"):
                raise GuardError("attempt requires step_id")
            if ev["type"] != "attempt_started" and not ev.get("result_url"):
                raise GuardError("attempt resolution needs external result evidence")
        if ev["type"] == "acceptance_verified":
            if not ev.get("criterion_id") or not ev.get("source_url") or not ev.get("independent_reviewer"):
                raise GuardError("acceptance needs independently sourced evidence")
            if not re.fullmatch("[a-f0-9]{40}", str(ev.get("head_sha", ""))):
                raise GuardError("acceptance requires exact PR SHA")
        if ev["type"] in ("deliverable_registered", "deliverable_superseded"):
            if not re.fullmatch("D-[a-zA-Z0-9_.-]+", str(ev.get("deliverable_id", ""))):
                raise GuardError("stable deliverable ID required")
            if ev["type"] == "deliverable_registered":
                if not ev.get("artifact_path") or not ev.get("source_url") or not re.fullmatch("[a-f0-9]{40}", str(ev.get("head_sha", ""))):
                    raise GuardError("deliverable requires artifact, URL and pinned SHA")

def append_event(path, event, now):
    """Fsynced append-only local ledger. Distributed writes require B08 transactions."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    previous = load_events(target)
    event_check(previous + [event], now)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())

def load_events(path):
    target = Path(path)
    return [json.loads(line) for line in target.read_text().splitlines() if line.strip()] if target.exists() else []

def attempts(events, task_id):
    """Validate retry ancestry; never erase failed attempts or claim invented efficiency."""
    starts, outcomes, order = {}, {}, []
    for ev in events:
        if ev["task_id"] != task_id or ev["type"] not in ("attempt_started","attempt_failed","attempt_passed"):
            continue
        aid = ev["attempt_id"]
        if ev["type"] == "attempt_started":
            if aid in starts:
                raise GuardError("attempt started twice")
            parent = ev.get("retry_of")
            if not parent and any(x["step_id"] == ev["step_id"] for x in starts.values()):
                raise GuardError("repeated step requires retry_of")
            if parent:
                if parent not in starts or outcomes.get(parent,{}).get("type") != "attempt_failed":
                    raise GuardError("retry must name earlier failed attempt")
                if starts[parent]["step_id"] != ev["step_id"]:
                    raise GuardError("retry cannot change step identity")
            starts[aid] = ev
            order.append(aid)
        else:
            if aid not in starts or aid in outcomes:
                raise GuardError("resolution requires one existing unresolved attempt")
            if ev["step_id"] != starts[aid]["step_id"]:
                raise GuardError("attempt resolution step mismatch")
            outcomes[aid] = ev
    unresolved = [aid for aid in order if aid not in outcomes]
    failed = [aid for aid in order if outcomes.get(aid,{}).get("type")=="attempt_failed"]
    last = order[-1] if order else None
    return {"attempts":len(order),"failures":len(failed),
            "pending":unresolved,
            "last_attempt":last,
            "last_result":outcomes[last]["type"] if last in outcomes else None,
            "retry_required":bool(last and outcomes.get(last,{}).get("type")=="attempt_failed")}

def lease_state(events, task_ids, now):
    leases, claim = {}, None
    for event in events:
        tid = event["task_id"]
        if tid not in task_ids and tid != "__controller__":
            raise GuardError("event for unknown task")
        if event["type"] in ("lease_granted", "lease_heartbeat"):
            leases[tid] = event
        elif event["type"] in ("lease_released", "lease_expired_verified"):
            leases.pop(tid, None)
        elif event["type"] == "capacity_reconciled":
            claim = event
    active = {tid: ev for tid, ev in leases.items() if utc(ev["expires_at"]) > now}
    expired = sorted(set(leases) - set(active))
    trusted = bool(claim and not expired and (now - utc(claim["at"])).total_seconds() <= 900
                   and set(claim["verified_active_task_ids"]) == set(active))
    return active, expired, trusted

def ci_green(evidence, sha):
    return any(run.get("head_sha") == sha and run.get("name") == "Validate BASKET data"
               and run.get("conclusion") == "success" for run in evidence["workflow_runs"])

def acceptance(task, pr, evidence, events):
    wanted = {"A%d" % (i+1) for i in range(len(task["acceptance"]))}
    got = {ev["criterion_id"] for ev in events if ev["type"] == "acceptance_verified"
           and ev["task_id"] == task["id"] and pr and ev.get("head_sha") == pr["head_sha"]}
    head_ok = bool(pr and ci_green(evidence, pr["head_sha"]))
    complete = bool(pr and head_ok and wanted.issubset(got))
    return {"required": len(wanted), "verified": len(wanted & got), "missing": sorted(wanted-got),
            "head_ci": head_ok, "component_verified": complete,
            "integrated": bool(complete and pr["merged"] and ci_green(evidence, evidence["main_commit"]))}

def deliverables(events, task_id, pr):
    found = {}
    for ev in events:
        if ev["task_id"] != task_id or ev["type"] not in ("deliverable_registered", "deliverable_superseded"):
            continue
        key = ev["deliverable_id"]
        if ev["type"] == "deliverable_registered":
            if key in found:
                raise GuardError("duplicate deliverable registration")
            found[key] = {"artifact_path": ev["artifact_path"], "source_url": ev["source_url"],
                          "head_sha": ev["head_sha"], "registered_at": ev["at"], "superseded": False,
                          "matches_pr_head": bool(pr and pr["head_sha"] == ev["head_sha"])}
        else:
            if key not in found or found[key]["superseded"]:
                raise GuardError("invalid deliverable supersession")
            found[key]["superseded"] = True
    return found

def evaluate(queue, evidence, events, now, max_age_seconds=900):
    tasks = validate_queue(queue)
    evidence_check(evidence, now, max_age_seconds=max_age_seconds)
    event_check(events, now)
    active, expired, reconciled = lease_state(events, set(tasks), now)
    issues = {i["number"]: i for i in evidence["issues"]}
    prs = {p["number"]: p for p in evidence["pull_requests"]}
    children = {tid: [] for tid in tasks}
    for task in tasks.values():
        for d in task["depends_on"]:
            children[d["task_id"]].append(task["id"])
    def downstream(tid):
        seen, pending = set(), list(children[tid])
        while pending:
            item = pending.pop()
            if item not in seen:
                seen.add(item); pending.extend(children[item])
        return len(seen)
    output = []
    for task in tasks.values():
        pr = prs.get(task.get("pr_number"))
        issue = issues.get(task.get("issue_number"))
        blocked = []
        for dep in task["depends_on"]:
            predecessor = tasks[dep["task_id"]]
            prior_pr = prs.get(predecessor.get("pr_number"))
            prior_issue = issues.get(predecessor.get("issue_number"))
            met = (bool(prior_issue) if dep["gate"] == "issue_exists" else
                   bool(prior_pr and prior_pr["merged"]) if dep["gate"] == "merged" else
                   bool(prior_pr and ci_green(evidence, prior_pr["head_sha"])))
            if not met:
                blocked.append("dependency:%s:%s" % (dep["task_id"], dep["gate"]))
        if task.get("pr_number") is not None and not pr:
            blocked.append("missing_pr")
        if task.get("issue_number") is not None and not issue:
            blocked.append("missing_issue")
        overlaps = collisions(task["write_scope"], evidence, own_pr=task.get("pr_number"))
        if overlaps and task["mode"] == "launch_new_worker":
            blocked.append("write_collision")
        quality = acceptance(task, pr, evidence, events)
        attempt_history = attempts(events, task["id"])
        if pr and pr["merged"]:
            state, decision, action = ("integrated" if quality["integrated"] else "merged_unverified",
                                       "requires_evidence", "verify_main_and_acceptance")
        elif blocked:
            state, decision, action = "blocked", "requires_evidence", "resolve_blocker"
        elif attempt_history["retry_required"]:
            state, decision, action = "failed_retry_required", "requires_owner", "retry_original_step"
        elif task["id"] in active:
            state, decision, action = "active", "automatic_safe", "verify_heartbeat"
        elif task["mode"] == "orchestrator_review":
            state, decision, action = "review_ready", "automatic_safe", "run_allowlisted_validations"
        elif task["mode"] == "resume_existing_worker":
            state, decision, action = "resume_ready", "requires_owner", "resume_original_worker"
        else:
            state = "launch_eligible"
            if reconciled and len(active) < queue["active_worker_limit"]:
                decision, action = "requires_owner", "claim_unique_worker_issue_branch"
            else:
                decision, action = "requires_evidence", "reconcile_worker_capacity"
        score = 100*PRIORITIES[task["priority"]] + 10*task["impact"] - 3*task["effort"] + 6*downstream(task["id"])
        output.append({"task_id": task["id"], "owner": task["spark_id"], "state": state,
                       "classification": decision, "next_action": action, "priority_score": score,
                       "issue_number": task.get("issue_number"), "pr_number": task.get("pr_number"),
                       "blockers": blocked, "scope_collisions": overlaps, "acceptance": quality,
                       "deliverables": deliverables(events, task["id"], pr),
                       "attempt_history": attempt_history})
    output.sort(key=lambda item: (item["state"] in ("blocked", "merged_unverified", "integrated"),
                                  -item["priority_score"], item["task_id"]))
    report = {"schema": "basket.agentic_decision@1", "repository": REPO, "queue_version": queue.get("queue_version"),
              "evaluated_at": now.isoformat(), "source_at": evidence["observed_at"],
              "main_sha": evidence["main_commit"], "evidence_digest": fingerprint(evidence),
              "queue_digest": fingerprint(queue), "event_ledger_digest":fingerprint(events),
              "policy_version":"agentic-manager@0.1.0",
              "active_workers": len(active) if reconciled else None, "capacity_reconciled": reconciled,
              "expired_unverified_leases": expired, "worker_limit": queue["active_worker_limit"],
              "decisions": output, "no_autonomous_merges_or_worker_creation": True}
    report["decision_id"] = fingerprint(report)
    return report

def run_safe_checks(root, names, timeout=90):
    """Only predetermined B00 validation scripts may be executed; never task-provided shell."""
    scripts = {"planner":"orchestration/validate_planner.py",
               "goals":"orchestration/validate_goals.py",
               "scopes":"orchestration/validate_worker_scopes.py",
               "attempts":"orchestration/validate_worker_attempts.py",
               "versions":"orchestration/validate_versions.py",
               "sparks":"orchestration/validate_sparks.py"}
    root = Path(root).resolve()
    results = []
    for name in names:
        if name not in scripts:
            raise GuardError("not allowlisted: " + str(name))
        path = (root/scripts[name]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            results.append({"check":name, "status":"unavailable", "reason":"missing script"})
            continue
        try:
            run = subprocess.run(["python", str(path)], cwd=root, capture_output=True, text=True,
                                 timeout=timeout, check=False)
            results.append({"check":name, "status":"pass" if run.returncode == 0 else "fail",
                            "exit_code":run.returncode, "stderr_tail":run.stderr[-1000:]})
        except subprocess.TimeoutExpired:
            results.append({"check":name, "status":"timeout"})
    return results
