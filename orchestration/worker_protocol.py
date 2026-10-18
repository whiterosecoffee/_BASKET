#!/usr/bin/env python3
"""Offline worker-claim evaluator: GitHub snapshot is evidence, reports are assertions.

No network calls, no merges, no automated issue closure. Requires jsonschema>=4.23.
Run: python orchestration/worker_protocol.py --task ... --resolution ... --evidence ...
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REPO = "whiterosecoffee/_BASKET"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def path_pattern(pattern):
    """GitHub repo relative POSIX path; single * may not cross '/'."""
    chunks = pattern.split("/")
    result = []
    for i, c in enumerate(chunks):
        if c == "**":
            result.append(".*" if i == len(chunks) - 1 else "(?:[^/]+/)*")
        else:
            result.append(re.escape(c).replace(r"\*", "[^/]*"))
            if i != len(chunks) - 1:
                result.append("/")
    return re.compile("^" + "".join(result) + "$")


def permitted(path, patterns):
    return any(path_pattern(p).fullmatch(path) for p in patterns)


def declared_subset(claimed, owned):
    """Conservative check: a claimed glob must be within an owned subtree."""
    if claimed in owned:
        return True
    if "*" not in claimed:
        return permitted(claimed, owned)
    if claimed.endswith("/**"):
        root = claimed[:-3]
        return any(p.endswith("/**") and (
            root == p[:-3] or root.startswith(p[:-3] + "/")) for p in owned)
    return any(p == claimed for p in owned)


def validate_schema(obj, name):
    schema = read(ROOT / "schemas" / ("worker-" + name + ".v1.json"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return ["%s: %s" % (name, e.message) for e in validator.iter_errors(obj)]


def evidence_check(task, report, github, spark_catalog):
    errors, warnings = [], []
    issues = {x["number"]: x for x in github["issues"]}
    prs = {x["number"]: x for x in github["pull_requests"]}
    runs = {x["url"]: x for x in github["workflow_runs"]}
    sparks = {x["id"]: x for x in spark_catalog["sparks"]}

    issue = task["issue"]["number"]
    if task["task_id"] != "%s-%d" % (task["spark_id"], issue):
        errors.append("task ID must equal spark ID + worker issue number")
    if not task["branch"]["name"].startswith("work/%d-" % issue):
        errors.append("worker branch must be named from its new issue")
    if task["spark_id"] not in sparks:
        errors.append("unknown spark ID")
    else:
        owned = sparks[task["spark_id"]]["write_paths"]
        for path in task["write_paths"]:
            if not declared_subset(path, owned):
                errors.append("task path outside spark ownership: " + path)
    if issues.get(issue, {}).get("url") != task["issue"]["url"]:
        errors.append("worker issue not verified in GitHub evidence")
    for key in ("task_id", "spark_id", "issue", "branch"):
        if task[key] != report[key]:
            errors.append("task/resolution mismatch: " + key)

    if report["pr"] is None:
        if report["changed_paths"]:
            warnings.append("changed paths reported without a PR; no PR path verification")
        pr = None
    else:
        pr = prs.get(report["pr"]["number"])
        if pr is None:
            errors.append("PR number missing from GitHub evidence")
        else:
            expected = report["pr"]
            for key, other in (("url", expected["url"]),
                               ("head_branch", task["branch"]["name"]),
                               ("head_sha", expected["head_sha"]),
                               ("state", expected["state"]),
                               ("draft", expected["draft"]),
                               ("merged", expected["merged"])):
                if pr[key] != other:
                    errors.append("GitHub PR metadata mismatch: " + key)
            if pr["base_branch"] != "main":
                errors.append("PR base must be main")
            if set(report["changed_paths"]) != set(pr["changed_paths"]):
                errors.append("reported changed paths differ from GitHub PR")
            for path in pr["changed_paths"]:
                if not permitted(path, task["write_paths"]):
                    errors.append("PR touches a path outside task claim: " + path)
                if task["spark_id"] in sparks and not permitted(
                        path, sparks[task["spark_id"]]["write_paths"]):
                    errors.append("PR touches path owned by another spark: " + path)
    ci_passes = 0
    for check in report["checks"]:
        if check["result"] == "pass" and not check["evidence_urls"]:
            errors.append("pass without evidence URL: " + check["id"])
        if check["result"] == "pass" and check["execution"] == "not_executed":
            errors.append("not_executed check cannot pass: " + check["id"])
        if check["kind"] == "workflow" and check["result"] == "pass":
            confirmed = False
            for url in check["evidence_urls"]:
                run = runs.get(url)
                if run and run["conclusion"] == "success" and (
                        pr is None or run["head_sha"] == pr["head_sha"]):
                    confirmed = True
            if not confirmed:
                errors.append("workflow success not verified at PR head: " + check["id"])
            else:
                ci_passes += 1
        if check["result"] in ("skipped", "not_run"):
            warnings.append("check not executed: " + check["id"])
    required = {a["id"] for a in task["acceptance"] if a.get("mandatory", True)}
    known = {a["id"] for a in task["acceptance"]}
    findings = {a["id"]: a for a in report["acceptance"]}
    if len(findings) != len(report["acceptance"]):
        errors.append("duplicate acceptance IDs in resolution")
    if not set(findings).issubset(known):
        errors.append("unknown acceptance ID in resolution")
    passed = {k for k, v in findings.items()
              if v["result"] == "pass" and v["evidence_urls"]}
    outstanding = sorted(required - passed)
    if outstanding and report["disposition"] in (
            "component_verified", "ready_for_integration", "integrated"):
        errors.append("cannot claim component readiness; mandatory acceptance unresolved: "
                      + ",".join(outstanding))
    if report["disposition"] in (
            "component_verified", "ready_for_integration", "integrated") and ci_passes == 0:
        errors.append("component evidence lacks confirmed passing PR-head CI")
    if report["disposition"] == "integrated" and not (pr and pr["merged"]):
        errors.append("integrated report requires PR merged in GitHub evidence")

    # Merge alone does not assert a functioning release. CI on the main commit is separate.
    main_ci = [run for run in github["workflow_runs"]
               if run["head_sha"] == github["main_commit"]
               and run["name"] == "Validate BASKET data"
               and run["conclusion"] == "success"]
    if errors:
        # An invalid record can never appear in a verified phase. A failed
        # ownership check or stale/missing CI overrides apparent readiness.
        phase = "evidence_invalid"
    elif pr and pr["merged"] and main_ci:
        phase = "integrated_main_ci_verified"
    elif pr and pr["merged"]:
        phase = "integrated_main_ci_unverified"
    elif pr and ci_passes and not outstanding:
        phase = "component_verified_review_pending"
    elif pr:
        phase = "draft_or_pr_active_incomplete"
    else:
        phase = "claimed_or_building_no_pr"
    if github["main_commit"] == (pr or {}).get("head_sha") and not (pr or {}).get("merged"):
        warnings.append("head equals main but no merged PR evidence; do not infer integration")
    next_action = ("Request explicit PR merge approval; verify integrated main CI afterward."
                   if phase == "component_verified_review_pending"
                   else "Address unresolved checks and dependencies without treating branch work as integrated.")
    return {
        "task_id": task["task_id"],
        "spark_id": task["spark_id"],
        "observed_at": github["observed_at"],
        "worker_reported_disposition": report["disposition"],
        "b00_evidence_phase": phase,
        "checks_passed_on_pr_head": ci_passes,
        "mandatory_acceptance_unresolved": outstanding,
        "worker_blockers": report["blockers"],
        "errors": errors,
        "warnings": warnings,
        "recommendation": next_action,
        "merge_authorized": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--task", required=True)
    p.add_argument("--resolution", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--catalog", default=str(ROOT / "orchestration/sparks.json"))
    args = p.parse_args()
    task, report, evidence, catalog = map(
        read, (args.task, args.resolution, args.evidence, args.catalog))
    failures = (validate_schema(task, "task")
                + validate_schema(report, "resolution")
                + validate_schema(evidence, "evidence"))
    if failures:
        print(json.dumps({"result": "invalid_schema", "errors": failures}, indent=2))
        return 1
    result = evidence_check(task, report, evidence, catalog)
    print(json.dumps(result, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
