"""GitHub-native discovery adapter; composes the existing worker protocol evaluator.

No claims, launches, merges, task creation, closures or releases are performed.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

from api import API, Blocked, Project

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestration"))
from worker_protocol import validate_schema, evidence_check, permitted, declared_subset

REPO = "whiterosecoffee/_BASKET"
BASE = "/repos/" + REPO


def payloads(body, schema):
    found = []
    for match in re.finditer(r"```(?:json)?\s*\n(.*?)```", body or "", re.S):
        try:
            obj = json.loads(match[1])
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("schema") == schema:
            found.append(obj)
    return found


def overlap(a, b):
    """Conservative uncertainty flag, including wildcard subtrees and char classes."""
    def prefix(p):
        return re.split(r"[*?\[]", p, 1)[0].rstrip("/")
    ap, bp = prefix(a), prefix(b)
    if not ap or not bp:
        return True
    return (ap == bp or ap.startswith(bp + "/") or bp.startswith(ap + "/") or
            permitted(a, [b]) or permitted(b, [a]))


def collect(api):
    """Complete open-work snapshot, native blockers, current PR files and workflow runs.

    An endpoint failure aborts collection; no stale cache is substituted.
    """
    main = api.call(BASE + "/branches/main")["commit"]["sha"]
    rows = api.rest_pages(BASE + "/issues?state=open")
    issues = [r for r in rows if "pull_request" not in r]
    prs = api.rest_pages(BASE + "/pulls?state=open")
    branches = api.rest_pages(BASE + "/branches")
    for issue in issues:
        issue["comments_data"] = api.rest_pages(BASE + f'/issues/{issue["number"]}/comments')
        issue["native_blockers"] = api.rest_pages(BASE + f'/issues/{issue["number"]}/dependencies/blocked_by')
    for pr in prs:
        pr["files"] = api.rest_pages(BASE + f'/pulls/{pr["number"]}/files')
        pr["checks"] = api.rest_pages(BASE + f'/commits/{pr["head"]["sha"]}/check-runs', "check_runs")
        pr["statuses"] = api.rest_pages(BASE + f'/commits/{pr["head"]["sha"]}/statuses')
        pr["runs"] = api.rest_pages(BASE + f'/actions/runs?head_sha={pr["head"]["sha"]}', "workflow_runs")
    # Detect concurrent head/main movement, rather than publish a mixed snapshot.
    for pr in prs:
        fresh = api.call(BASE + f'/pulls/{pr["number"]}')
        if fresh["head"]["sha"] != pr["head"]["sha"] or fresh["state"] != "open":
            raise Blocked("snapshot_changed", "collect", "PR moved during collection; retry")
    if api.call(BASE + "/branches/main")["commit"]["sha"] != main:
        raise Blocked("snapshot_changed", "collect", "Main moved during collection; retry")
    return {"as_of": datetime.now(timezone.utc).isoformat(), "main_commit": main,
            "issues": issues, "pull_requests": prs, "branches": branches,
            "main_runs": api.rest_pages(BASE + f"/actions/runs?branch=main&head_sha={main}", "workflow_runs")}


def check_state(pr):
    """Latest attempts only; successful old commits and skipped jobs never pass."""
    head = pr["head"]["sha"]
    latest = {}
    for row in sorted(pr.get("checks", []), key=lambda x: x.get("id", 0)):
        if row.get("head_sha") == head:
            latest["check:" + row["name"]] = row.get("conclusion") if row.get("status") == "completed" else "pending"
    # Commit statuses endpoint is newest first.
    for row in pr.get("statuses", []):
        latest.setdefault("status:" + row["context"], row["state"])
    for row in sorted(pr.get("runs", []), key=lambda x: (x.get("id", 0), x.get("run_attempt", 0))):
        if row.get("head_sha") == head:
            latest["workflow:" + str(row["workflow_id"])] = row.get("conclusion") if row.get("status") == "completed" else "pending"
    values = set(latest.values())
    if values & {"failure", "error", "cancelled", "timed_out", "action_required", "startup_failure"}:
        return "failed"
    return "head_passed_not_integrated" if values == {"success"} else "unverified"


def reconcile(snapshot, catalog, now=None):
    """Enrich live identities with validated claims. Unknown evidence stays unknown.

    This adapter never assigns READY automatically and never completes an open PR.
    Existing worker_protocol.evidence_check remains the resolution authority.
    """
    now = now or datetime.now(timezone.utc)
    sparks = {s["id"]: s for s in catalog["sparks"]}
    records, claims, findings = [], {}, []
    branch_names = {b["name"] for b in snapshot.get("branches", [])}
    prs = snapshot["pull_requests"]
    for issue in snapshot["issues"]:
        number = issue["number"]
        bodies = [issue.get("body")] + [c.get("body") for c in issue.get("comments_data", [])]
        tasks = [t for body in bodies for t in payloads(body, "basket.worker_task@1")]
        # Repeated identical registration is safe; differing claims require B00 review.
        unique = {json.dumps(t, sort_keys=True): t for t in tasks}
        task = next(iter(unique.values())) if len(unique) == 1 else None
        errors = []
        if len(unique) > 1:
            errors.append("ambiguous_task_claim")
        if task:
            errors.extend(validate_schema(task, "task"))
            if not errors:
                if task["issue"] != {"number": number, "url": issue["html_url"]}:
                    errors.append("issue_identity_mismatch")
                if task["task_id"] != f'{task["spark_id"]}-{number}':
                    errors.append("task_identity_mismatch")
                if not task["branch"]["name"].startswith(f"work/{number}-"):
                    errors.append("branch_issue_mismatch")
                if task["branch"]["name"] not in branch_names:
                    errors.append("branch_not_found")
                spark = sparks.get(task["spark_id"])
                if not spark or any(not declared_subset(p, spark["write_paths"]) for p in task["write_paths"]):
                    errors.append("invalid_spark_or_scope")
        branch = task.get("branch", {}).get("name") if task and not errors else None
        related = [p for p in prs if (p["head"]["ref"] == branch if branch else
                                     p["head"]["ref"].startswith(f"work/{number}-"))]
        blocked = {b["number"] for b in issue.get("native_blockers", []) if b.get("state") != "closed"}
        if task and not errors:
            # Resolution of a dependency is not inferred from closure. Missing integration
            # evidence is intentionally blocking; native issue state is advisory only.
            blocked.update(d["issue_number"] for d in task["dependencies"] if d["blocks_completion"])
            claims[number] = task
        if len(related) > 1:
            errors.append("ambiguous_pr_association")
        pr = related[0] if len(related) == 1 else None
        fields = {"Status": "BACKLOG", "Validation": "unverified", "Acceptance": "not_verified"}
        if branch:
            fields.update({"Status": "CLAIMED", "Branch": branch, "Spark ID": task["spark_id"],
                           "Domain": sparks[task["spark_id"]]["title"],
                           "Worker": ", ".join(a["login"] for a in issue.get("assignees", [])) or "unassigned"})
            # A valid claim without an assigned GitHub owner must not look executable.
            if fields["Worker"] == "unassigned":
                errors.append("owner_missing")
        if pr:
            fields["Status"] = "DRAFT_PR" if pr["draft"] else "REVIEW"
            fields["Branch"] = pr["head"]["ref"]
            fields["Validation"] = check_state(pr)
            changed = {p for f in pr.get("files", []) for p in
                       (f["filename"], f.get("previous_filename")) if p}
            if branch and any(not permitted(p, task["write_paths"]) for p in changed):
                errors.append("changed_file_outside_scope")
            if not task:
                errors.append("missing_valid_worker_claim")
            if pr["base"]["ref"] != "main":
                errors.append("pr_base_not_main")
            updated = datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00"))
            if (now - updated).days >= 14:
                findings.append({"issue": number, "pr": pr["number"], "code": "stale_pr", "url": pr["html_url"]})
        if blocked or errors:
            fields["Status"] = "BLOCKED"
        records.append({"node_id": issue["node_id"], "issue": number, "url": issue["html_url"],
                        "pr": pr["number"] if pr else None, "blocked_by": sorted(blocked),
                        "fields": fields, "errors": errors,
                        "category": "Blocked" if blocked or errors else "In progress" if pr or branch else "Planned"})
    for n, task in claims.items():
        for m, other in claims.items():
            if n < m and any(overlap(a, b) for a in task["write_paths"] for b in other["write_paths"]):
                findings.append({"issues": [n, m], "code": "declared_scope_collision"})
        for pr in prs:
            if pr["head"]["ref"] != task["branch"]["name"] and any(
                    overlap(path, p) for f in pr.get("files", []) for path in
                    (f["filename"], f.get("previous_filename")) if path for p in task["write_paths"]):
                findings.append({"issues": [n], "pr": pr["number"], "code": "actual_pr_scope_collision"})
    collisions = {n for f in findings if "collision" in f["code"] for n in f["issues"]}
    for r in records:
        if r["issue"] in collisions:
            r["fields"]["Status"] = "BLOCKED"
            r["errors"].append("ownership_collision_requires_B00")
    # Native PR items are imported once, without duplicating dependency/PR text fields.
    for pr in prs:
        records.append({"node_id": pr["node_id"], "url": pr["html_url"], "pr": pr["number"],
                        "fields": {"Status": "DRAFT_PR" if pr["draft"] else "REVIEW",
                                   "Validation": check_state(pr)}, "category": "In progress"})
    return {"schema": "basket.project_sync@1", "source_as_of": snapshot["as_of"],
            "main_commit": snapshot["main_commit"], "records": records, "findings": findings,
            "summary": {"issues": len(snapshot["issues"]), "prs": len(prs),
                        "categories": dict(Counter(r["category"] for r in records))},
            "merge_authorized": False, "executor_connected": False}


def resolution_gate(task, resolution, evidence, catalog, integration_proof=None):
    """Future handoff interface: only exact, schema-valid GitHub evidence is evaluated."""
    errors = (validate_schema(task, "task") + validate_schema(resolution, "resolution") +
              validate_schema(evidence, "evidence"))
    if errors:
        return {"status": "BLOCKED", "errors": errors}
    result = evidence_check(task, resolution, evidence, catalog)
    # evaluator phase alone doesn't prove all acceptance: require reported integrated
    # disposition plus no unresolved criteria; main must be separately verified.
    proof = integration_proof or {}
    required = proof.get("required_workflows", [])
    latest = {}
    for run in sorted(evidence["workflow_runs"], key=lambda r: r["id"]):
        if run["head_sha"] == evidence["main_commit"]:
            latest[run["name"]] = run["conclusion"]
    main_verified = (proof.get("main_sha") == evidence["main_commit"] and
                     proof.get("ancestry_status") in ("ahead", "identical") and
                     bool(re.fullmatch(r"[a-f0-9]{40}", proof.get("merged_commit_sha", ""))) and
                     proof.get("compare_url", "").startswith("https://github.com/" + REPO + "/compare/") and
                     bool(required) and all(latest.get(n) == "success" for n in required))
    complete = (main_verified and not result["errors"] and not result["mandatory_acceptance_unresolved"] and
                not any(b["blocking"] for b in resolution["blockers"]) and
                not resolution["pr"]["draft"] and
                resolution["disposition"] == "integrated" and
                result["b00_evidence_phase"] == "integrated_main_ci_verified")
    return {"status": "COMPLETE" if complete else "INTEGRATION_VERIFICATION", "evidence": result}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot", type=Path, help="Historical/API export; never used for live mutations")
    p.add_argument("--apply", action="store_true", help="Explicitly apply additive Project mutations")
    p.add_argument("--create-project", action="store_true")
    p.add_argument("--owner", default="whiterosecoffee")
    p.add_argument("--owner-kind", choices=["user", "organization"], default="user")
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    if args.snapshot and args.apply:
        p.error("Historical exports cannot authorize live Project updates")
    api = API()
    report = {"blocked": [], "dry_run": not args.apply}
    try:
        snapshot = json.loads(args.snapshot.read_text()) if args.snapshot else collect(api)
        catalog = json.loads((ROOT / "orchestration/sparks.json").read_text())
        report.update(reconcile(snapshot, catalog))
        project = Project(api, args.owner, args.owner_kind, args.apply)
        try:
            board = project.discover(args.create_project)
            report["project"] = board
            if board:
                fields, incompatible = project.ensure_fields(board)
                report["incompatible_fields"] = incompatible
                # Field incompatibility must be resolved before any item state writes.
                if incompatible:
                    raise Blocked("field_configuration_blocked", "sync", "Existing options/types require B00 review")
                report["blocked"].extend(project.sync(board, report["records"], fields))
        finally:
            report["operations"] = project.operations
    except Blocked as exc:
        report["blocked"].append(exc.result)
    except (KeyError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        report["blocked"].append({"code": "invalid_or_unavailable_evidence", "detail": type(exc).__name__})
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report.get(k) for k in ("summary", "project", "blocked", "dry_run")}))
    return 2 if report["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
