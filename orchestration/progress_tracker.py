#!/usr/bin/env python3
"""Read-only progress/queue projection from GitHub evidence; never a second ledger."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("progress_planner", ROOT / "orchestration/planner.py")
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


def validate_contract(value, schema_name):
    schema = planner.load(ROOT / "schemas" / schema_name)
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value))
    if errors:
        raise ValueError(schema_name + ": " + errors[0].message)


def checklist(issue):
    """Ignore historical details and code examples; preserve explicit item identity."""
    items, seen = [], {}
    details, fence = 0, None
    for line in (issue.get("body") or "").splitlines():
        stripped = line.strip()
        if fence:
            if stripped.startswith(fence):
                fence = None
            continue
        if stripped.startswith(("```", "~~~")):
            fence = stripped[:3]
            continue
        opened = len(re.findall(r"<details(?:\s[^>]*)?>", line, re.I))
        closed = len(re.findall(r"</details\s*>", line, re.I))
        hidden = details > 0 or opened > 0
        details = max(0, details + opened - closed)
        if hidden:
            continue
        match = re.match(r"^\s*[-*+]\s+\[([ xX])\]\s+(.+)$", line)
        if not match:
            continue
        title = match.group(2).strip()
        plain = title.replace("**", "").replace("`", "")
        explicit = re.match(r"^([A-Z]+-\d+|[A-Z]+\d+(?:\.\d+)*)(?:\s|[—:])", plain)
        key = explicit.group(1) if explicit else hashlib.sha256(title.encode()).hexdigest()[:16]
        identity = "%s:%s" % (issue["number"], key)
        item = {"id": identity, "title": title, "checked": match.group(1).lower() == "x",
                "source_url": issue["url"], "issue_number": issue["number"],
                "identity_basis": "explicit_id" if explicit else "text_hash",
                "acceptance": "NOT_VERIFIED"}
        if identity in seen:
            if seen[identity] != item:
                raise ValueError("conflicting checklist identity: " + identity)
            continue
        seen[identity] = item
        items.append(item)
    return items


def build_report(queue, library, registry, evidence, active_ids=None, token_budget=None,
                 focus_issue=None):
    validate_contract(queue, "task-queue.v1.json")
    validate_contract(library, "worker-library.v1.json")
    validate_contract(evidence, "worker-evidence.v1.json")
    plan = planner.run_plan(queue, library, registry, evidence, active_ids, token_budget)
    issues = evidence["issues"]
    errors, progress = [], []
    for issue in issues:
        if focus_issue is not None and issue["number"] != focus_issue:
            continue
        try:
            progress.extend(checklist(issue))
        except ValueError as exc:
            errors.append({"issue_number": issue["number"], "code": "CHECKLIST_CONFLICT",
                           "message": str(exc), "source_url": issue["url"]})
    if focus_issue is not None and not any(i["number"] == focus_issue for i in issues):
        errors.append({"issue_number": focus_issue, "code": "ISSUE_NOT_OBSERVED",
                       "message": "Requested issue is absent from this evidence snapshot"})
    claimed = {t["issue_number"] for t in queue["tasks"] if t["issue_number"] is not None}
    unplanned = [{"number": i["number"], "title": i.get("title", ""), "url": i["url"]}
                 for i in issues if i["state"] == "open" and i["number"] not in claimed]
    prs = {p["number"]: p for p in evidence["pull_requests"]}
    work = []
    for entry in plan["ordered_tasks"]:
        row = dict(entry)
        pr = prs.get(row["pr_number"])
        row["integration_review_eligible"] = bool(pr and not pr["draft"] and
            not pr["merged"] and row["branch_ci_pass"] and not row["blocking_dependencies"])
        row["acceptance"] = "NOT_VERIFIED"
        row["required_reviews"] = "UNKNOWN"
        row["integration_ready"] = False
        row["warnings"] = list(row["warnings"])
        if pr and pr["draft"]:
            row["warnings"].append("Draft PR: CI does not establish integration readiness")
        if row["state"].startswith("integrated_"):
            row["warnings"].append("Legacy planner phase is not independent acceptance or deployment proof")
        work.append(row)
    report = {"schema": "basket.progress_report@1",
            "report_kind": "github_progress_projection", "repository": evidence["repository"],
            "main_commit": evidence["main_commit"], "observed_at": evidence["observed_at"],
            "capture_mode": evidence.get("capture_mode", "unknown"),
            "source_fetched_this_invocation": False, "side_effects_executed": [],
            "focus_issue": focus_issue, "checklist": progress,
            "checklist_counts": {"checked": sum(i["checked"] for i in progress),
                                 "open": sum(not i["checked"] for i in progress)},
            "checklist_completion_is_verified_acceptance": False,
            "unplanned_open_issues": sorted(unplanned, key=lambda i: i["number"]),
            "ordered_tasks": work, "next_orchestrator_action": plan["next_orchestrator_action"],
            "next_new_worker": plan["next_new_worker"],
            "declared_token_budget": token_budget, "actual_remaining_quota": None,
            "errors": errors}
    validate_contract(report, "progress-report.v1.json")
    return report


def markdown(report):
    counts = report["checklist_counts"]
    lines = ["# _BASKET operational progress", "",
             "Source: %s; observed: %s; main: `%s`." %
             (report["capture_mode"], report["observed_at"], report["main_commit"]),
             "Checklist: %d recorded checked, %d open. Checked is not accepted completion." %
             (counts["checked"], counts["open"]),
             "Open issues absent from the configured plan: %d. Actual remaining quota: UNKNOWN." %
             len(report["unplanned_open_issues"]), "",
             "| Task | Evidence phase | Exact-head checks | Resource gate |",
             "|---|---|---|---|"]
    for row in report["ordered_tasks"]:
        checks = ", ".join(c["workflow"] + ": " + c["result"] for c in row["checks"]) or "NOT_RUN"
        lines.append("| %s | %s | %s | %s |" %
                     (row["id"], row["state"], checks.replace("|", "\\|"), row["resource_gate"]))
    if report["checklist"]:
        lines.extend(["", "## Source checklist"])
        lines.extend("- [%s] %s: %s" % ("x" if i["checked"] else " ", i["id"], i["title"])
                     for i in report["checklist"])
    for error in report["errors"]:
        lines.append("ERROR %s: %s" % (error["code"], error["message"]))
    lines.extend(["", "Read-only projection; no issue mutation, worker launch, merge or deployment."])
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queue", default=str(ROOT / "orchestration/planner/queue.json"))
    ap.add_argument("--library", default=str(ROOT / "orchestration/planner/worker-library.json"))
    ap.add_argument("--catalog", default=str(ROOT / "orchestration/sparks.json"))
    ap.add_argument("--evidence", default=str(ROOT / "orchestration/examples/github-evidence-2026-10-16.json"))
    ap.add_argument("--live-github", action="store_true")
    ap.add_argument("--discover-open", action="store_true")
    ap.add_argument("--active", action="append", default=None)
    ap.add_argument("--token-budget", type=int, default=None)
    ap.add_argument("--focus-issue", type=int, default=None)
    ap.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = ap.parse_args()
    try:
        queue, library, catalog = map(planner.load, (args.queue, args.library, args.catalog))
        if args.discover_open and not args.live_github:
            raise ValueError("--discover-open requires --live-github")
        if args.live_github:
            import os
            from github_snapshot import collect, fetch_json
            evidence = collect(queue, lambda path: fetch_json(path, os.environ.get("GITHUB_TOKEN")),
                               args.discover_open)
        else:
            evidence = planner.load(args.evidence)
        report = build_report(queue, library, catalog, evidence, args.active,
                              args.token_budget, args.focus_issue)
        report["source_fetched_this_invocation"] = args.live_github
        print(json.dumps(report, indent=2) if args.format == "json" else markdown(report), end="\n")
        return 1 if report["errors"] else 0
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        error = {"schema": "basket.progress_report@1", "result": "error", "code": "PROGRESS_UNAVAILABLE",
                          "message": str(exc), "source_error_code": getattr(exc, "code", None),
                          "retry_after": getattr(exc, "retry_after", None),
                          "side_effects_executed": []}
        validate_contract(error, "progress-report.v1.json")
        print(json.dumps(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
