#!/usr/bin/env python3
"""Read-only GitHub snapshot provider for B00 planner; no writes, tokens or merges.

Run:
  python orchestration/github_snapshot.py > /tmp/basket-evidence.json
Requires network access; optional GITHUB_TOKEN for public/private repo access.
Endpoint failures fail closed; never silently use a stale snapshot.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"
REPO = "whiterosecoffee/_BASKET"


class EvidenceUnavailable(RuntimeError):
    def __init__(self, message, code="EVIDENCE_UNAVAILABLE", retry_after=None):
        super().__init__(message)
        self.code = code
        self.retry_after = retry_after


def fetch_json(path, token=None):
    if not path.startswith("/repos/whiterosecoffee/_BASKET/"):
        raise EvidenceUnavailable("Unapproved GitHub API path")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "BASKET-B00-readonly-evidence",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urlopen(Request(API + path, headers=headers), timeout=15) as reply:
            return json.loads(reply.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        code = getattr(exc, "code", "network")
        response_headers = getattr(exc, "headers", None) or {}
        if code == 429 or (code == 403 and response_headers.get("X-RateLimit-Remaining") == "0"):
            raise EvidenceUnavailable("GitHub rate limit reached; no cached fallback",
                                      code="RATE_LIMITED",
                                      retry_after=response_headers.get("Retry-After") or
                                      response_headers.get("X-RateLimit-Reset")) from None
        raise EvidenceUnavailable("GitHub evidence unavailable for %s (%s); no cached fallback"
                                  % (path, code)) from None


def paged(fetch, endpoint, max_pages=10):
    result = []
    for page in range(1, max_pages + 1):
        rows = fetch(endpoint + ("&" if "?" in endpoint else "?") +
                     "per_page=100&page=%d" % page)
        if not isinstance(rows, list):
            raise EvidenceUnavailable("Invalid paginated GitHub response")
        result.extend(rows)
        if len(rows) < 100:
            return result
    raise EvidenceUnavailable("GitHub pagination exceeded safe limit; incomplete evidence")


def workflow_pages(fetch, endpoint, max_pages=10):
    """Paginate workflow envelopes; incomplete or malformed evidence is explicit."""
    result = []
    for page in range(1, max_pages + 1):
        row = fetch(endpoint + ("&" if "?" in endpoint else "?") +
                    "per_page=100&page=%d" % page)
        if not isinstance(row, dict) or not isinstance(row.get("workflow_runs"), list):
            raise EvidenceUnavailable("Missing or malformed workflow run response")
        rows = row["workflow_runs"]
        result.extend(rows)
        if len(rows) < 100:
            return result
    raise EvidenceUnavailable("Workflow pagination exceeded safe limit; incomplete evidence")


def collect(queue, fetch, discover_open=False):
    """Pure provider logic; inject fixture fetcher for offline tests."""
    path = "/repos/" + REPO
    main = fetch(path + "/branches/main")["commit"]["sha"]
    issue_ids = {n for task in queue["tasks"]
                        for n in ([task["issue_number"]] +
                                  task.get("source_handoff_issues", []))
                        if n is not None}
    pr_ids = {t["pr_number"] for t in queue["tasks"]
              if t["pr_number"] is not None}
    if discover_open:
        issue_ids.update(x["number"] for x in paged(fetch, path + "/issues?state=open")
                         if "pull_request" not in x)
        pr_ids.update(x["number"] for x in paged(fetch, path + "/pulls?state=open"))
    issues = []
    for number in sorted(issue_ids):
        row = fetch(path + "/issues/%d" % number)
        if "pull_request" in row or row["number"] != number:
            raise EvidenceUnavailable("Wrong GitHub issue response for %d" % number)
        issues.append({"number": number, "url": row["html_url"],
                       "state": row["state"], "title": row["title"],
                       "body": row.get("body") or ""})
    prs = []
    for number in sorted(pr_ids):
        row = fetch(path + "/pulls/%d" % number)
        if row.get("number", number) != number:
            raise EvidenceUnavailable("Wrong GitHub PR response for %d" % number)
        files = paged(fetch, path + "/pulls/%d/files" % number)
        prs.append({
            "number": number, "url": row["html_url"],
            "head_branch": row["head"]["ref"],
            "head_sha": row["head"]["sha"],
            "base_branch": row["base"]["ref"],
            "state": row["state"],
            "draft": bool(row["draft"]),
            "merged": bool(row.get("merged_at")),
            "merge_commit_sha": row.get("merge_commit_sha") if row.get("merged_at") else None,
            "changed_paths": sorted(set(f["filename"] for f in files)),
        })
    relevant_sha = {main, *(r["head_sha"] for r in prs)}
    runs = {}
    for sha in sorted(relevant_sha):
        for row in workflow_pages(fetch, path + "/actions/runs?head_sha=" + sha):
            if row.get("head_sha") != sha:
                continue
            conclusion = row.get("conclusion") or "pending"
            runs[row["id"]] = {
                "id": row["id"], "url": row["html_url"],
                "head_sha": row["head_sha"], "run_attempt": row.get("run_attempt", 1),
                "conclusion": conclusion, "name": row["name"],
            }
    return {
        "schema": "basket.github_evidence@1",
        "capture_mode": "live_connector",
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository": REPO,
        "main_commit": main,
        "issues": issues,
        "pull_requests": prs,
        "workflow_runs": sorted(runs.values(), key=lambda r: r["id"]),
    }


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--queue", default=str(ROOT / "orchestration/planner/queue.json"))
    args.add_argument("--discover-open", action="store_true",
                      help="Also discover all open issues/PRs, including work absent from the planned queue")
    config = args.parse_args()
    queue = json.loads(Path(config.queue).read_text(encoding="utf-8"))
    token = os.environ.get("GITHUB_TOKEN")
    try:
        evidence = collect(queue, lambda endpoint: fetch_json(endpoint, token=token), config.discover_open)
    except EvidenceUnavailable as exc:
        raise SystemExit("ERROR: " + str(exc)) from None
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
