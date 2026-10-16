#!/usr/bin/env python3
"""Deterministic GitHub-evidence-backed task planner. No remote calls or side effects.

Run:
  python orchestration/planner.py
  python orchestration/planner.py --active T-004 --active T-005 --next-worker

Evidence JSON is an immutable, dated observation. NEVER interpret it as live.
Task/library configuration is editable on B00's branch; actual issue/PR state is GitHub.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANNER = ROOT / "orchestration" / "planner"
REPO = "whiterosecoffee/_BASKET"
PRIORITY = {"P0": 3, "P1": 2, "P2": 1}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def path_matches(pattern, path):
    """Match GitHub-relative POSIX paths; * does not cross directories."""
    pieces = []
    for part in pattern.split("/"):
        if part == "**":
            pieces.append(".*")
        else:
            pieces.append(re.escape(part).replace(r"\*", "[^/]*"))
    return re.fullmatch("/".join(pieces), path) is not None


def scope_subset(submitted, allowed):
    if submitted in allowed:
        return True
    if "*" not in submitted:
        return any(path_matches(p, submitted) for p in allowed)
    if submitted.endswith("/**"):
        root = submitted[:-3]
        return any(p.endswith("/**") and
                   (root == p[:-3] or root.startswith(p[:-3] + "/"))
                   for p in allowed)
    return False


def validate_plan(queue, library, registry):
    errors = []
    sparks = {s["id"]: s for s in registry["sparks"]}
    caps = {c["id"]: c for c in library["capabilities"]}
    profiles = {p["id"]: p for p in library["profiles"]}
    recipes = {r["id"]: r for r in library["recipes"]}
    tasks = queue["tasks"]
    ids = [t["id"] for t in tasks]
    if len(ids) != len(set(ids)):
        errors.append("duplicate task IDs")
    for group, values in (("capability", library["capabilities"]),
                          ("profile", library["profiles"]),
                          ("recipe", library["recipes"])):
        names = [v["id"] for v in values]
        if len(names) != len(set(names)):
            errors.append("duplicate " + group + " IDs")
    for p in library["profiles"]:
        for c in p["capabilities"]:
            if c not in caps:
                errors.append("profile %s missing capability %s" % (p["id"], c))
    for recipe in library["recipes"]:
        for step in recipe["steps"]:
            if step["capability"] not in caps:
                errors.append("recipe %s missing capability %s" %
                              (recipe["id"], step["capability"]))
    by_id = {t["id"]: t for t in tasks}
    for t in tasks:
        if t["spark_id"] not in sparks:
            errors.append(t["id"] + " unknown owner")
            continue
        owner = sparks[t["spark_id"]]["write_paths"]
        for w in t["write_scope"]:
            if not scope_subset(w, owner):
                errors.append(t["id"] + " claims other domain: " + w)
        if t["mode"] == "orchestrator_review" and t["spark_id"] != "B00":
            errors.append(t["id"] + " only B00 can run orchestrator review")
        if t["mode"] == "launch_new_worker" and (t["issue_number"] or t["pr_number"]):
            errors.append(t["id"] + " new worker cannot preassign issue or PR")
        if t["mode"] != "launch_new_worker" and t["issue_number"] is None:
            errors.append(t["id"] + " existing/review task missing issue")
        if t["pr_number"] is not None and t["issue_number"] is None:
            errors.append(t["id"] + " PR without issue")
        cover = set()
        for profile_id in t["profiles"]:
            if profile_id not in profiles:
                errors.append(t["id"] + " missing profile " + profile_id)
            else:
                cover.update(profiles[profile_id]["capabilities"])
        for c in t["capabilities"]:
            if c not in caps or c not in cover:
                errors.append(t["id"] + " capability not provided: " + c)
        if t["recipe"] not in recipes:
            errors.append(t["id"] + " missing recipe")
        else:
            for step in recipes[t["recipe"]]["steps"]:
                if step["capability"] not in t["capabilities"]:
                    errors.append(t["id"] + " missing recipe step " +
                                  step["capability"])
        for d in t["depends_on"]:
            if d["task_id"] not in by_id:
                errors.append(t["id"] + " unknown task dependency " + d["task_id"])
            if d["task_id"] == t["id"]:
                errors.append(t["id"] + " self-dependency")
    visiting, finished = set(), set()
    def walk(tid):
        if tid in visiting:
            errors.append("dependency cycle at " + tid)
            return
        if tid in finished or tid not in by_id:
            return
        visiting.add(tid)
        for d in by_id[tid]["depends_on"]:
            walk(d["task_id"])
        visiting.remove(tid)
        finished.add(tid)
    for tid in ids:
        walk(tid)
    return sorted(set(errors))


def evidence_maps(evidence):
    return ({x["number"]: x for x in evidence["issues"]},
            {x["number"]: x for x in evidence["pull_requests"]},
            {x["url"]: x for x in evidence["workflow_runs"]})


def head_ci_green(pr, runs, workflow_name="Validate BASKET data"):
    return any(r["head_sha"] == pr["head_sha"] and
               r["conclusion"] == "success" and
               r["name"] == workflow_name for r in runs.values())


def run_plan(queue, library, registry, evidence, active_ids=None):
    """Return reproducible queue; status is derived, never asserted as live."""
    errors = validate_plan(queue, library, registry)
    if errors:
        raise ValueError("; ".join(errors))
    if evidence["repository"] != REPO:
        raise ValueError("evidence repository mismatch")
    tasks = queue["tasks"]
    issues, prs, runs = evidence_maps(evidence)
    by_id = {t["id"]: t for t in tasks}
    active_unknown = active_ids is None
    active = set(active_ids or ())
    if len(active) != len(tuple(active_ids or ())) or not active.issubset(by_id):
        raise ValueError("active tasks must be unique known task IDs")
    if any(by_id[tid]["mode"] == "orchestrator_review" for tid in active):
        raise ValueError("B00 orchestrator review does not count as a worker slot")

    def dependency(task):
        blockers = []
        for d in task["depends_on"]:
            source = by_id[d["task_id"]]
            issue = issues.get(source["issue_number"])
            pr = prs.get(source["pr_number"])
            good = {"issue_exists": bool(issue),
                    "merged": bool(pr and pr["merged"]),
                    "ci_passed_on_head": bool(pr and head_ci_green(pr, runs))}[d["gate"]]
            if not good:
                blockers.append(d["task_id"] + ":" + d["gate"])
        return blockers

    children = {t["id"]: set() for t in tasks}
    for t in tasks:
        for dep in t["depends_on"]:
            children[dep["task_id"]].add(t["id"])
    def downstream(task_id):
        seen, pending = set(), list(children[task_id])
        while pending:
            n = pending.pop()
            if n not in seen:
                seen.add(n)
                pending += list(children[n])
        return len(seen)

    entries = []
    for t in tasks:
        issue = issues.get(t["issue_number"])
        pr = prs.get(t["pr_number"])
        warnings = []
        if t["issue_number"] and not issue:
            warnings.append("GitHub evidence missing claimed worker issue")
        if t["pr_number"] and not pr:
            warnings.append("GitHub evidence missing claimed worker PR")
        gate_blocks = dependency(t)
        branch_ci = bool(pr and head_ci_green(pr, runs))
        if pr and pr["merged"]:
            state = "integrated_main_ci_unverified"
            if any(run["head_sha"] == evidence["main_commit"] and
                   run["name"] == "Validate BASKET data" and
                   run["conclusion"] == "success" for run in runs.values()):
                state = "integrated_main_ci_verified"
        elif gate_blocks:
            state = "blocked_upstream"
        elif t["mode"] == "orchestrator_review":
            state = "review_ready_ci_green" if branch_ci else "review_required_checks_pending"
        elif t["mode"] == "resume_existing_worker" and issue:
            state = "resume_incomplete"
        elif t["mode"] == "launch_new_worker":
            state = "ready_new_worker"
        else:
            state = "unverified_claim"
        readiness = state in ("review_ready_ci_green",
                              "review_required_checks_pending",
                              "resume_incomplete", "ready_new_worker")
        impact = t["impact"]
        effort = t["effort"]
        # Decision ordering only; NEVER probability, investment edge, or completion metric.
        score = PRIORITY[t["priority"]] * 100 + impact * 10 - effort * 3 + downstream(t["id"]) * 6
        entries.append({"id": t["id"], "spark_id": t["spark_id"],
                        "title": t["title"], "mode": t["mode"],
                        "priority": t["priority"], "state": state,
                        "ready_for_action": readiness,
                        "blocking_dependencies": gate_blocks,
                        "branch_ci_pass": branch_ci,
                        "score_for_ordering_only": score,
                        "issue_number": t["issue_number"],
                        "pr_number": t["pr_number"],
                        "capabilities": t["capabilities"],
                        "composed_profiles": t["profiles"],
                        "warnings": warnings})
    entries.sort(key=lambda e: (not e["ready_for_action"],
                                -e["score_for_ordering_only"], e["id"]))
    slots = None if active_unknown else max(0, queue["active_worker_limit"] - len(active))
    new_launches = [e for e in entries if e["state"] == "ready_new_worker"]
    proposed = new_launches[0]["id"] if new_launches and slots is not None and slots > 0 else None
    return {
        "schema": "basket.planner_decision@1",
        "source_evidence_observed_at": evidence["observed_at"],
        "source_is_live": False,
        "source_fetched_this_invocation": False,
        "active_worker_count_known": not active_unknown,
        "queue_version": queue["queue_version"],
        "library_version": library["library_version"],
        "active_worker_limit": queue["active_worker_limit"],
        "active_worker_tasks_supplied": sorted(active),
        "worker_slots_remaining": slots,
        "next_new_worker": proposed,
        "next_orchestrator_action": next((
            e["id"] for e in entries
            if e["mode"] == "orchestrator_review" and e["ready_for_action"]), None),
        "ordered_tasks": entries,
        "no_automatic_issue_or_branch_creation": True,
        "no_automatic_merge": True,
    }


def render_next_worker(queue, task_id):
    task = next(t for t in queue["tasks"] if t["id"] == task_id)
    return (
        "Launch _BASKET Spark %s — %s. I am a NEW conversation. "
        "Read AGENTS.md, orchestration/sparks.json and WORKER_PROTOCOL.md "
        "from main if PR #2 merged, else READ provisional documents from "
        "work/1-conversation-sparks-orchestration. Verify live GitHub issues, "
        "branch owners, PR changed paths and dependencies. "
        "Create ONE NEW issue and ONE UNIQUE work/<issue>-<slug> branch FROM "
        "latest main, never reuse an existing worker branch. "
        "Task ID %s. Objective: %s "
        "Compose reusable profiles %s and capabilities %s within the "
        "sole write scope: %s. "
        "Acceptance: %s. "
        "Post a basket.worker_task@1 claim and basket.worker_resolution@1 "
        "payload with exact CI SHA, verified vs missing tests, blockers, "
        "handoffs and one next action. Commit, test, open draft PR. "
        "Never merge without explicit authorization."
        % (task["spark_id"], task["title"], task_id, task["objective"],
           ", ".join(task["profiles"]), ", ".join(task["capabilities"]),
           ", ".join(task["write_scope"]), "; ".join(task["acceptance"]))
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", default=str(PLANNER / "queue.json"))
    parser.add_argument("--library", default=str(PLANNER / "worker-library.json"))
    parser.add_argument("--catalog", default=str(ROOT / "orchestration/sparks.json"))
    parser.add_argument("--evidence", default=str(ROOT / "orchestration/examples/github-evidence-2026-10-16.json"))
    parser.add_argument("--active", action="append", default=None,
                        help="Confirmed currently code-writing worker task ID")
    parser.add_argument("--assume-none-active", action="store_true",
                        help="Explicitly declare zero active code-writing workers")
    parser.add_argument("--live-github", action="store_true",
                        help="Fetch fresh read-only GitHub issue/PR/CI evidence; never substitute cached status")
    parser.add_argument("--next-worker", action="store_true", help="Also print next new worker launch prompt")
    args = parser.parse_args()
    queue, library, catalog = map(load, (args.queue, args.library, args.catalog))
    if args.live_github:
        from github_snapshot import EvidenceUnavailable, collect, fetch_json
        import os
        try:
            evidence = collect(queue, lambda path: fetch_json(path, os.environ.get("GITHUB_TOKEN")))
        except EvidenceUnavailable as exc:
            parser.error(str(exc))
    else:
        evidence = load(args.evidence)
    if args.assume_none_active and args.active:
        parser.error("--assume-none-active conflicts with --active")
    active_ids = [] if args.assume_none_active else args.active
    result = run_plan(queue, library, catalog, evidence, active_ids)
    result["source_fetched_this_invocation"] = args.live_github
    print(json.dumps(result, indent=2))
    if args.next_worker and result["next_new_worker"]:
        print("\nNEXT NEW WORKER PROMPT:\n" +
              render_next_worker(queue, result["next_new_worker"]))


if __name__ == "__main__":
    main()
