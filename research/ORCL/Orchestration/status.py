#!/usr/bin/env python3
"""Read-only ORCL vector status and drift report.

No writes, no merges, no stored tokens. Restricted to whiterosecoffee/_BASKET.
Fails closed: any API failure aborts instead of reporting stale state.

Run:  python research/ORCL/Orchestration/status.py [--json] [--no-collisions]
Auth: uses `gh api` when the GitHub CLI is installed, else GITHUB_TOKEN from the environment.
Exit: 0 = no hard flags, 2 = at least one hard flag, 3 = evidence unavailable.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "vectors.json"
PREFIX = "/repos/whiterosecoffee/_BASKET/"
API = "https://api.github.com"
HARD_FLAGS = {"BRANCH_MISSING", "SCOPE_VIOLATION", "COLLISION", "MISSING_FILE", "FILES_TRUNCATED", "TREE_TRUNCATED"}


class EvidenceUnavailable(RuntimeError):
    pass


def load_registry(path=REGISTRY):
    reg = json.loads(Path(path).read_text())
    if reg.get("schema") != "basket.orcl_vector_registry@1":
        raise ValueError("Unexpected registry schema")
    return reg


def matches(pattern, path):
    """Exact path, or a prefix pattern ending in /** (same convention as sparks.json)."""
    if pattern.endswith("/**"):
        return path.startswith(pattern[:-2])
    return path == pattern


def any_match(patterns, path):
    return any(matches(p, path) for p in patterns)


def fetch(path, token=None):
    """GET a repository-scoped GitHub REST path. Read-only. Fails closed."""
    if not path.startswith(PREFIX):
        raise EvidenceUnavailable("Unapproved GitHub API path")
    if shutil.which("gh") and not token:
        done = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
        if done.returncode != 0:
            raise EvidenceUnavailable(f"gh api failed for {path}: {done.stderr.strip()[:200]}")
        try:
            return json.loads(done.stdout)
        except json.JSONDecodeError as exc:
            raise EvidenceUnavailable(f"Invalid JSON for {path}") from exc
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "BASKET-ORCL-readonly-status",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urlopen(Request(API + path, headers=headers), timeout=20) as reply:
            return json.loads(reply.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EvidenceUnavailable(f"GitHub request failed for {path}: {exc}") from exc


def vector_flags(vset, ownership_status, branch_info, compare, prs, tree_paths, tree_truncated, other_pr_files):
    """Pure function: turn fetched GitHub facts into flags. No I/O."""
    flags = []
    if ownership_status != "ratified":
        flags.append("UNRATIFIED")
    if branch_info is None or compare is None:
        return flags + ["BRANCH_MISSING"]
    if not prs:
        flags.append("NO_PR")
    if compare.get("ahead_by", 0) > 0:
        flags.append("UNMERGED")
    if compare.get("behind_by", 0) > 0:
        flags.append("DRIFT")
    changed = [f["filename"] for f in compare.get("files", [])]
    if len(changed) >= 300:
        flags.append("FILES_TRUNCATED")
    outside = [p for p in changed if not any_match(vset["write_paths"], p)]
    if outside:
        flags.append("SCOPE_VIOLATION")
    if tree_truncated:
        flags.append("TREE_TRUNCATED")
    else:
        expected = [f"{vset['folder']}/{name}" for name in vset["files"]]
        if any(p not in tree_paths for p in expected):
            flags.append("MISSING_FILE")
    for number, files in sorted(other_pr_files.items()):
        if any(any_match(vset["write_paths"], f) for f in files):
            flags.append(f"COLLISION:#{number}")
    return flags


def missing_files(vset, tree_paths):
    return [f"{vset['folder']}/{n}" for n in vset["files"] if f"{vset['folder']}/{n}" not in tree_paths]


def collect(reg, token=None, collisions=True):
    base = reg["base"]
    open_prs = fetch(f"{PREFIX}pulls?state=open&per_page=100", token) if collisions else []
    out = []
    for vset in reg["vector_sets"]:
        branch = vset["branch"]
        q = quote(branch, safe="/")
        try:
            branch_info = fetch(f"{PREFIX}branches/{q}", token)
        except EvidenceUnavailable as exc:
            if "404" in str(exc) or "Not Found" in str(exc):
                branch_info = None
            else:
                raise
        compare = tree_paths = None
        tree_truncated = False
        prs = []
        other = {}
        if branch_info:
            compare = fetch(f"{PREFIX}compare/{base}...{q}", token)
            sha = branch_info["commit"]["sha"]
            tree = fetch(f"{PREFIX}git/trees/{sha}?recursive=1", token)
            tree_truncated = bool(tree.get("truncated"))
            tree_paths = {t["path"] for t in tree.get("tree", [])}
            head = quote(f"whiterosecoffee:{branch}", safe=":/")
            prs = fetch(f"{PREFIX}pulls?head={head}&state=all&per_page=10", token)
            for pr in open_prs:
                if pr["head"]["ref"] == branch:
                    continue
                files = fetch(f"{PREFIX}pulls/{pr['number']}/files?per_page=100", token)
                other[pr["number"]] = [f["filename"] for f in files]
        flags = vector_flags(vset, reg["ownership"]["status"], branch_info, compare, prs, tree_paths or set(), tree_truncated, other)
        out.append({
            "id": vset["id"],
            "title": vset["title"],
            "issue": vset["issue"],
            "branch": branch,
            "head_sha": branch_info["commit"]["sha"] if branch_info else None,
            "ahead_by": compare.get("ahead_by") if compare else None,
            "behind_by": compare.get("behind_by") if compare else None,
            "pull_requests": [{"number": p["number"], "state": p["state"], "draft": p.get("draft"), "merged": bool(p.get("merged_at"))} for p in prs],
            "missing_files": missing_files(vset, tree_paths) if tree_paths is not None and not tree_truncated else [],
            "flags": flags,
        })
    return out


def render(results, generated_at):
    lines = [f"ORCL vector status, generated {generated_at} (live GitHub read; stale after the next push or merge)"]
    for r in results:
        pr = ", ".join(f"#{p['number']} {p['state']}{' draft' if p['draft'] else ''}{' merged' if p['merged'] else ''}" for p in r["pull_requests"]) or "no PR"
        sha = (r["head_sha"] or "none")[:7]
        lines.append(f"- {r['id']} {r['title']} (issue #{r['issue']})")
        lines.append(f"  {r['branch']} @ {sha}; ahead {r['ahead_by']} behind {r['behind_by']}; {pr}")
        lines.append("  flags: " + (", ".join(r["flags"]) or "none"))
        if r["missing_files"]:
            lines.append("  missing: " + ", ".join(r["missing_files"]))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--no-collisions", action="store_true", help="skip the per-PR changed-file scan")
    args = parser.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN")
    try:
        results = collect(load_registry(), token=token, collisions=not args.no_collisions)
    except EvidenceUnavailable as exc:
        print(f"EVIDENCE UNAVAILABLE (fail closed): {exc}", file=sys.stderr)
        return 3
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    if args.json:
        print(json.dumps({"generated_at": generated_at, "results": results}, indent=2))
    else:
        print(render(results, generated_at))
    hard = any(f.split(":")[0] in HARD_FLAGS for r in results for f in r["flags"])
    return 2 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
