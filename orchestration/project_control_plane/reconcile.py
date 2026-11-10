"""Fail-closed GitHub issue/PR control-plane reconciliation.

Input is a dated snapshot exported with GitHub CLI; output is advisory and never
substitutes for live GitHub objects. No network requests or side effects.
"""
import fnmatch
import json
import sys
from pathlib import Path


def _scope_overlap(a, b):
    """Conservatively recognize nested globs, treating uncertainty as conflict."""
    if a == b or a in ("**", "*") or b in ("**", "*"):
        return True
    def prefix(p):
        parts = p.split("/")
        fixed = []
        for part in parts:
            if any(c in part for c in "*?["):
                break
            fixed.append(part)
        return "/".join(fixed)
    ap, bp = prefix(a), prefix(b)
    if not ap or not bp:
        return True
    if ap == bp or ap.startswith(bp + "/") or bp.startswith(ap + "/"):
        return True
    # Exact filename against other glob.
    if not any(c in a for c in "*?[") and fnmatch.fnmatch(a, b):
        return True
    if not any(c in b for c in "*?[") and fnmatch.fnmatch(b, a):
        return True
    return False


def reconcile(snapshot):
    """Derive states from verified claims, without claiming missing evidence passes."""
    items = snapshot.get("issues", [])
    prs = snapshot.get("pull_requests", [])
    results = []
    collisions = []
    claims = []
    for issue in items:
        if issue.get("state") != "OPEN":
            continue
        number = issue["number"]
        task = issue.get("task") or {}
        branch = task.get("branch")
        scopes = task.get("write_paths") or []
        status = "Claimed" if branch and scopes and task.get("worker") else "Backlog"
        related = [p for p in prs if p.get("headRefName") == branch and branch]
        pr = related[0] if len(related) == 1 else None
        if len(related) > 1:
            status = "Blocked"
        if pr:
            status = "Draft PR" if pr.get("isDraft") else "Review"
            head = pr.get("headRefOid")
            checks = pr.get("checks") or []
            current_checks = [c for c in checks if c.get("head_sha") == head]
            if not head or not current_checks:
                validation = "unverified"
            elif any(c.get("conclusion") in ("FAILURE", "CANCELLED", "TIMED_OUT") for c in current_checks):
                validation = "failed"
            elif all(c.get("conclusion") == "SUCCESS" for c in current_checks):
                validation = "head_passed_not_integrated"
            else:
                validation = "pending"
        else:
            validation = "unverified"
        if task.get("blocked_by"):
            status = "Blocked"
        results.append({"issue": number, "status": status, "branch": branch,
                        "pr": pr.get("number") if pr else None, "validation": validation,
                        "blocked_by": task.get("blocked_by", []),
                        "next_action": task.get("next_action", "verify task claim and evidence")})
        if branch and scopes:
            claims.append((number, scopes))
    for i, (n, scopes) in enumerate(claims):
        for m, other in claims[i+1:]:
            if any(_scope_overlap(a, b) for a in scopes for b in other):
                collisions.append({"issues": [n, m], "reason": "overlapping or ambiguous write scopes"})
    # PR changed files independently checked against all *other* claimed paths.
    for pr in prs:
        paths = pr.get("changedFiles") or []
        for n, scopes in claims:
            if pr.get("headRefName") == next((x.get("branch") for x in results if x["issue"] == n), None):
                continue
            if any(_scope_overlap(path, scope) for path in paths for scope in scopes):
                collisions.append({"issues": [n], "pr": pr.get("number"),
                                   "reason": "PR changed file overlaps another task claim"})
    return {"schema": "basket.project_reconciliation@1", "source_as_of": snapshot.get("as_of"),
            "source": "github_export", "items": results, "collisions": collisions,
            "summary": {"issues": len(results), "prs": len(prs), "collision_flags": len(collisions)},
            "project_state": "unverified"}


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python reconcile.py snapshot.json report.json")
    src = json.loads(Path(sys.argv[1]).read_text())
    report = reconcile(src)
    Path(sys.argv[2]).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if report["collisions"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
