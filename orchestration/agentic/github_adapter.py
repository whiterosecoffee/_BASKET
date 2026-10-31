"""Complete read-only GitHub inventory for B00 worker scheduling.

Queue-linked PRs alone cannot detect collisions. This adapter inventories all open
PR changed files, plus merged PRs referenced by the queue; it never writes GitHub.
"""
from __future__ import annotations

import datetime as dt
from .manager import GuardError, REPO, UTC

def pages(fetch, endpoint, max_pages=20):
    rows = []
    for page in range(1, max_pages + 1):
        response = fetch(endpoint + ("&" if "?" in endpoint else "?") +
                         "per_page=100&page=%d" % page)
        if not isinstance(response, list):
            raise GuardError("GitHub pagination incomplete")
        rows.extend(response)
        if len(response) < 100:
            return rows
    raise GuardError("GitHub pagination maximum reached; fail closed")

def collect(queue, fetch, now):
    prefix = "/repos/" + REPO
    main = fetch(prefix + "/branches/main")["commit"]["sha"]
    prs = {p["number"]:p for p in pages(fetch, prefix + "/pulls?state=open")}
    for number in sorted({t["pr_number"] for t in queue["tasks"] if t.get("pr_number")}):
        if number not in prs:
            prs[number] = fetch(prefix + "/pulls/%d" % number)
    pr_rows = []
    for number, raw in sorted(prs.items()):
        if raw["number"] != number:
            raise GuardError("mismatched PR identity")
        files = pages(fetch, prefix + "/pulls/%d/files" % number)
        if any("filename" not in f for f in files):
            raise GuardError("PR filename unavailable")
        pr_rows.append({"number":number, "url":raw["html_url"], "state":raw["state"],
                        "draft":bool(raw["draft"]), "merged":bool(raw.get("merged_at")),
                        "head_sha":raw["head"]["sha"], "head_branch":raw["head"]["ref"],
                        "base_branch":raw["base"]["ref"],
                        "changed_paths":sorted(set(f["filename"] for f in files))})
    issues = {i["number"]:i for i in pages(fetch, prefix + "/issues?state=open")
              if "pull_request" not in i}
    required = {n for task in queue["tasks"] for n in
                [task.get("issue_number"), *task.get("source_handoff_issues", [])]
                if n is not None}
    for n in sorted(required - set(issues)):
        record = fetch(prefix + "/issues/%d" % n)
        if record["number"] != n or "pull_request" in record:
            raise GuardError("mismatched GitHub issue identity")
        issues[n] = record
    issue_rows = [{"number": n, "state": x["state"], "url": x["html_url"],
                   "title": x.get("title","")} for n,x in sorted(issues.items())]
    data = fetch(prefix + "/actions/runs?per_page=100")
    if not isinstance(data, dict) or not isinstance(data.get("workflow_runs"),list):
        raise GuardError("GitHub workflow response missing")
    shas = {main, *(p["head_sha"] for p in pr_rows)}
    runs = [{"id":r["id"], "url":r.get("html_url"), "name":r["name"],
             "head_sha":r["head_sha"], "conclusion":r.get("conclusion") or "pending"}
            for r in data["workflow_runs"] if r.get("head_sha") in shas]
    return {"schema":"basket.github_evidence@1","capture_mode":"live_connector",
            "repository":REPO,"observed_at":now.astimezone(UTC).isoformat(),
            "main_commit":main,"issues":issue_rows,"pull_requests":pr_rows,
            "workflow_runs":runs}
