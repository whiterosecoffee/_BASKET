"""Finite execution adapter for existing #32 policy and #78 assignments.

No scheduler, shared lease store, task schema, implicit claim or remote writes.
GitHub hosts authorization/evidence; B08 remains the persistent-runtime owner.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestration"))
import worker_protocol as protocol
from validate_sparks import intersect

UTC = dt.timezone.utc
REPO = "whiterosecoffee/_BASKET"


class Blocked(ValueError):
    def __init__(self, code, detail):
        self.code, self.detail = code, detail
        super().__init__(f"{code}: {detail}")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def load_controller(root, lock):
    """Load the owner's exact dependency, never copy or silently use another head."""
    root = Path(root).resolve()
    if git(root, "rev-parse", "HEAD") != lock["controller_commit"]:
        raise Blocked("controller_revision", "Dependency checkout differs from pinned commit")
    for relative, expected in lock["files"].items():
        p = root / relative
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise Blocked("controller_fingerprint", relative)
    path = root / "orchestration/agentic/manager.py"
    package = types.ModuleType("basket_owner_controller")
    package.__path__ = [str(path.parent)]
    sys.modules[package.__name__] = package
    spec = importlib.util.spec_from_file_location("basket_owner_controller.manager", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    adapter_spec = importlib.util.spec_from_file_location("basket_owner_controller.github_adapter", path.parent / "github_adapter.py")
    adapter = importlib.util.module_from_spec(adapter_spec)
    sys.modules[adapter_spec.name] = adapter
    adapter_spec.loader.exec_module(adapter)
    module.github_collect = adapter.collect
    return module


def fetch_github(endpoint):
    if not endpoint.startswith("/repos/" + REPO + "/"):
        raise Blocked("github_endpoint", "Only repository evidence endpoints are supported")
    try:
        result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        raise Blocked("github_timeout", "Evidence read timed out; no cached fallback") from None
    if result.returncode:
        raise Blocked("github_unavailable", "Authenticated GitHub read failed; no cached fallback")
    return json.loads(result.stdout)


def collect_live(controller, task, lease_comment_id, now, own_pr=None):
    """Reuse #32's complete PR inventory provider, augment with issue-held claims."""
    base = "/repos/" + REPO
    queue = {"tasks": [{"issue_number": task["issue"]["number"], "pr_number": own_pr}]}
    evidence = controller.github_collect(queue, fetch_github, now)
    issue = fetch_github(base + f'/issues/{task["issue"]["number"]}')
    # Use the owner's pagination implementation as well as its main collector.
    from basket_owner_controller.github_adapter import pages
    issue["comments_data"] = pages(fetch_github, base + f'/issues/{issue["number"]}/comments')
    issue["native_blockers"] = pages(fetch_github, base + f'/issues/{issue["number"]}/dependencies/blocked_by')
    declared = []
    for row in evidence["issues"]:
        raw = issue if row["number"] == issue["number"] else fetch_github(base + f'/issues/{row["number"]}')
        if raw is not issue:
            raw["comments_data"] = pages(fetch_github, base + f'/issues/{row["number"]}/comments')
        for claim in claims_from_issue(raw):
            paths = claim.get("write_paths")
            if isinstance(paths, list) and all(isinstance(p, str) for p in paths):
                declared.append({"issue": row["number"], "write_paths": paths})
    evidence["declared_claims"] = declared
    comment = fetch_github(base + f"/issues/comments/{lease_comment_id}")
    if (comment["user"]["login"] != "whiterosecoffee" or
            comment["issue_url"] != f'https://api.github.com/repos/{REPO}/issues/{issue["number"]}'):
        raise Blocked("lease_authority", "Lease must be explicitly issued by repository owner on this issue")
    blocks = re.findall(r"```json\s*\n(.*?)```", comment["body"], flags=re.S)
    if len(blocks) != 1:
        raise Blocked("lease_authority", "One unambiguous controller-event array required")
    events = json.loads(blocks[0])
    if not isinstance(events, list):
        raise Blocked("lease_authority", "Expected existing controller events, not a new assignment schema")
    # Detect main/PR movement during capture. Comments are historical authorization;
    # their current edit timestamp and content are part of the captured fingerprint.
    if fetch_github(base + "/branches/main")["commit"]["sha"] != evidence["main_commit"]:
        raise Blocked("snapshot_changed", "Main changed during capture")
    fresh = pages(fetch_github, base + "/pulls?state=open")
    heads = {p["number"]: p["head"]["sha"] for p in fresh}
    if heads != {p["number"]: p["head_sha"] for p in evidence["pull_requests"] if p["state"] == "open"}:
        raise Blocked("snapshot_changed", "Open PR inventory changed during capture")
    repositories = {p["number"]: (p["head"].get("repo") or {}).get("full_name") for p in fresh}
    for pr in evidence["pull_requests"]:
        pr["head_repository"] = repositories.get(pr["number"])
    evidence["lease_comment_sha256"] = digest(comment)
    return evidence, issue, events


def match_profile(library, required, requested=None):
    """Choose from the existing library; stable order, least excess capabilities."""
    known = {c["id"] for c in library["capabilities"]}
    required = set(required)
    if not required or not required <= known:
        raise Blocked("capability_unknown", "Required capabilities must be nonempty and registered")
    eligible = [p for p in library["profiles"] if required <= set(p["capabilities"])
                and (requested is None or p["id"] == requested)]
    if not eligible:
        raise Blocked("profile_ineligible", str(requested))
    return min(eligible, key=lambda p: (len(set(p["capabilities"]) - required), p["id"]))


def claims_from_issue(issue):
    claims = []
    for body in [issue.get("body", ""), *[c.get("body", "") for c in issue.get("comments_data", [])]]:
        for text in re.findall(r"```(?:json)?\s*\n(.*?)```", body or "", flags=re.S):
            try:
                obj = json.loads(text)
            except ValueError:
                continue
            if isinstance(obj, dict) and obj.get("schema") == "basket.worker_task@1":
                claims.append(obj)
    return claims


def assert_fence(controller, events, task_id, lease_id, now):
    controller.event_check(events, now)
    active, expired, _ = controller.lease_state(events, {task_id}, now)
    current = active.get(task_id)
    if not current or task_id in expired:
        raise Blocked("lease_expired", "No active owner-issued lease; no automatic takeover")
    if current["event_id"] != lease_id:
        raise Blocked("stale_fence", "Assignment no longer holds the current lease event ID")
    return current


def assert_attempt(controller, events, task_id, attempt_id):
    history = controller.attempts(events, task_id)
    if (not attempt_id or history["last_attempt"] != attempt_id or
            attempt_id not in history["pending"]):
        raise Blocked("attempt_unregistered", "Invocation must name the latest authorized pending owner-ledger attempt")
    return history


def own_pr_exemption(task, evidence, own_pr, head_sha):
    matching = [p for p in evidence["pull_requests"] if p["state"] == "open" and
                p.get("head_branch") == task["branch"]["name"]]
    if len(matching) > 1:
        raise Blocked("pr_ambiguous", "Multiple PRs use this task branch")
    if own_pr is None:
        if matching:
            raise Blocked("pr_association_required", "Explicitly bind the observed task PR before excluding its paths")
        return None
    if (len(matching) != 1 or matching[0]["number"] != own_pr or matching[0].get("merged") or
            matching[0].get("base_branch") != "main" or matching[0].get("head_sha") != head_sha or
            matching[0].get("head_repository") != REPO):
        raise Blocked("pr_identity", "PR exemption must match task branch, repository, base and exact checkout head")
    return own_pr


def publication_inputs_unchanged(before, after):
    fields = ("task", "library", "catalog", "profile", "required_capabilities", "controller_lock", "policy", "checkout_head")
    a, b = before["assignment"], after["assignment"]
    if (a["base_commit_sha"] != b["base_commit_sha"] or
            a["execution"] != b["execution"] or
            any(a["input_manifest"][k] != b["input_manifest"][k] for k in fields)):
        raise Blocked("source_drift", "Stable dispatch inputs changed; old execution cannot authorize publication")


def owned_output_directory(root, output):
    root = Path(root).resolve()
    expected = root / "orchestration/worker_bridge/evidence"
    output = Path(output).absolute()
    if not output.is_relative_to(expected):
        raise Blocked("log_scope", "Output must remain within the owned evidence subtree")
    for path in (output, *output.parents):
        if path == root:
            break
        if path.is_symlink():
            raise Blocked("log_scope", "Symlinked log ancestry is forbidden")
    if not expected.resolve().is_relative_to(root) or not output.resolve().is_relative_to(expected.resolve()):
        raise Blocked("log_scope", "Resolved log path escapes the checkout")
    return output


def prepare(controller, task, issue, library, catalog, evidence, events, lease_id,
            capabilities, root, now, profile_id=None, own_pr=None, attempt_id=None):
    errors = protocol.validate_schema(task, "task")
    if errors:
        raise Blocked("invalid_task", "; ".join(errors))
    number = task["issue"]["number"]
    if issue["number"] != number or issue.get("state") != "open" or issue["html_url"] != task["issue"]["url"]:
        raise Blocked("issue_identity", "Live issue does not match open worker task")
    claims = {digest(c): c for c in claims_from_issue(issue)}
    if set(claims) != {digest(task)}:
        raise Blocked("claim_ambiguous", "GitHub must hold one exact authoritative task claim")
    if task["task_id"] != f'{task["spark_id"]}-{number}' or not task["branch"]["name"].startswith(f"work/{number}-"):
        raise Blocked("task_identity", "Issue/task/branch mismatch")
    if git(root, "branch", "--show-current") != task["branch"]["name"]:
        raise Blocked("branch_identity", "Checkout is not the assignment branch")
    if subprocess.run(["git", "merge-base", "--is-ancestor", evidence["main_commit"], "HEAD"], cwd=root).returncode:
        raise Blocked("base_identity", "Observed main is not an ancestor of this checkout")
    sparks = {s["id"]: s for s in catalog["sparks"]}
    spark = sparks.get(task["spark_id"])
    if not spark or any(not protocol.declared_subset(p, spark["write_paths"]) for p in task["write_paths"]):
        raise Blocked("scope_invalid", "Task exceeds registered spark scope")
    if any(d["blocks_completion"] for d in task["dependencies"]) or issue.get("native_blockers"):
        raise Blocked("dependency_unresolved", "Explicit dependency requires owner resolution")
    # Include raw scopes of legacy/malformed claims conservatively, without treating
    # malformed records as a valid assignment. Actual PR files are separately checked.
    for other in evidence.get("declared_claims", []):
        if other["issue"] == number:
            continue
        for a in task["write_paths"]:
            for b in other["write_paths"]:
                if intersect(a, b):
                    raise Blocked("declared_collision", f'Issue {other["issue"]}: {b}')
    # Controller consumes its existing evidence contract; extra collector metadata
    # is deliberately excluded rather than creating another evidence schema.
    source = {k: evidence[k] for k in ("schema", "capture_mode", "repository", "observed_at",
                                     "main_commit", "issues", "pull_requests", "workflow_runs")}
    controller.evidence_check(source, now)
    tid = f"T-{number:03d}"
    lease = assert_fence(controller, events, tid, lease_id, now)
    if lease["issue"] != number or lease["branch"] != task["branch"]["name"]:
        raise Blocked("lease_identity", "Lease names another issue/branch")
    assert_attempt(controller, events, tid, attempt_id)
    own_pr = own_pr_exemption(task, source, own_pr, git(root, "rev-parse", "HEAD"))
    if controller.collisions(task["write_paths"], source, own_pr):
        raise Blocked("actual_pr_collision", "Another open PR owns an intersecting changed file")
    # A single ephemeral issue projection is an input to the existing controller,
    # not a new stored queue or scheduler. No global capacity is fabricated.
    projection = dict(id=tid, spark_id=task["spark_id"], mode="launch_new_worker",
                      issue_number=number, pr_number=own_pr, priority="P0", impact=1, effort=1,
                      write_scope=task["write_paths"], depends_on=[], acceptance=task["acceptance"])
    decision = controller.evaluate({"queue_version": "1.0.0", "active_worker_limit": 3,
                                   "tasks": [projection]}, source, events, now)["decisions"][0]
    if decision["blockers"] or decision["attempt_history"]["retry_required"]:
        raise Blocked("controller_blocked", str(decision))
    profile = match_profile(library, capabilities, profile_id)
    lock = json.loads((ROOT / "orchestration/worker_bridge/controller-lock.json").read_text())
    # Verify actual mounted code on every prepare, including postflight.
    if git(Path(controller.__file__).resolve().parents[2], "rev-parse", "HEAD") != lock["controller_commit"]:
        raise Blocked("controller_revision", "Mounted dependency moved during dispatch")
    for relative, expected in lock["files"].items():
        file = Path(controller.__file__).resolve().parents[2] / relative
        if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise Blocked("controller_fingerprint", relative)
    policy = {n: hashlib.sha256((ROOT / "orchestration/worker_bridge" / n).read_bytes()).hexdigest()
              for n in ("bridge.py", "cli.py")}
    manifest = {"task": digest(task), "library": digest(library), "catalog": digest(catalog),
                "profile": digest(profile), "required_capabilities": digest(sorted(set(capabilities))),
                "controller_lock": digest(lock), "policy": digest(policy),
                "checkout_head": digest(git(root, "rev-parse", "HEAD")),
                "evidence": controller.fingerprint(source), "events": controller.fingerprint(events)}
    assignment = {"schema": "basket.agent_assignment@1", "task_id": task["task_id"],
                  "source_issue": number, "spark_id": task["spark_id"], "repository": REPO,
                  "branch": task["branch"]["name"], "base_commit_sha": source["main_commit"],
                  "exclusive_write_paths": task["write_paths"], "read_paths": ["AGENTS.md", "orchestration/WORKER_PROTOCOL.md"],
                  "dependencies": task["dependencies"], "input_manifest": manifest,
                  "acceptance": task["acceptance"], "execution": {"mode": "human_started", "provider": "codex",
                  "lease_id": lease_id, "expires_at": lease["expires_at"], "may_commit": False, "may_merge": False},
                  "return_schema": "basket.worker_resolution@1"}
    assignment["execution"]["attempt_id"] = attempt_id
    return {"profile": profile, "assignment": assignment, "controller_decision": decision,
            "assignment_sha256": digest(assignment)}


def changed_paths(root):
    """Include committed, staged, unstaged, untracked and renamed source paths."""
    # Compare all tracked changes against current main, then include untracked output.
    names = set(git(root, "diff", "--no-renames", "--name-only", "origin/main").splitlines())
    names.update(git(root, "ls-files", "--others", "--exclude-standard").splitlines())
    return sorted(names)


def assert_changed_scope(root, task):
    paths = changed_paths(root)
    bad = [p for p in paths if not protocol.permitted(p, task["write_paths"]) or (Path(root) / p).is_symlink()]
    if bad:
        raise Blocked("changed_scope", str(bad))
    return paths


def run_codex(root, prepared, instruction, output_dir, controller, events, now,
              read_only=False, timeout=240):
    """One explicit finite invocation. Never retry model calls or commit/merge here.

    The outer host must refresh GitHub state before invocation and publication.
    Post-flight scope rejection blocks publication; it is not an OS path ACL.
    """
    task_id = f'T-{prepared["assignment"]["source_issue"]:03d}'
    token = prepared["assignment"]["execution"]["lease_id"]
    if not read_only and "implementation" not in prepared["profile"]["capabilities"]:
        raise Blocked("execution_permission", "Read-only profile cannot request a write-capable model sandbox")
    output_dir = owned_output_directory(root, output_dir)
    assert_fence(controller, events, task_id, token, now)
    assert_attempt(controller, events, task_id, prepared["assignment"]["execution"].get("attempt_id"))
    output_dir.mkdir(parents=True, exist_ok=False)
    prompt = ("You are an authorized bounded worker instance for the existing issue/branch, not a new conversation allocation. "
              "Do not create issues/branches, commit, push, merge, change credentials, inspect secret files, or modify other domains. "
              "Do not delegate. Read AGENTS.md. Honor the attached assignment and narrower instruction. "
              "Never claim tests executed unless actually run.\n" + json.dumps(prepared, indent=2) + "\n" + instruction)
    (output_dir / "prompt.txt").write_text(prompt)
    argv = ["codex", "exec", "--ephemeral", "--json", "--sandbox", "read-only" if read_only else "workspace-write",
            "--cd", str(Path(root).resolve()), "--output-last-message", str(output_dir / "final.txt"), "-"]
    started = dt.datetime.now(UTC)
    begin = time.monotonic()
    status = "failed"
    try:
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run(argv, input=prompt, capture_output=True, text=True, cwd=root,
                                timeout=timeout, env=environment)
        (output_dir / "events.jsonl").write_text(result.stdout)
        (output_dir / "stderr.txt").write_text(result.stderr)
        exit_code = result.returncode
        # CLI success alone is insufficient: retain native completion event evidence.
        native = [json.loads(line) for line in result.stdout.splitlines() if line.strip().startswith("{")]
        finished = any(e.get("type") == "turn.completed" for e in native)
        status = "executed" if exit_code == 0 and finished else "failed"
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        (output_dir / "stderr.txt").write_text("Bounded invocation timed out; no automatic retry.\n")
        data = exc.stdout or b""
        (output_dir / "events.jsonl").write_text(data.decode(errors="replace") if isinstance(data, bytes) else data)
        status = "timeout"
    report = {"provider": "codex", "profile": prepared["profile"]["id"], "status": status,
              "argv": argv, "exit_code": exit_code, "started_at": started.isoformat(),
              "finished_at": dt.datetime.now(UTC).isoformat(), "duration_seconds": round(time.monotonic()-begin, 3),
              "assignment_sha256": prepared["assignment_sha256"], "lease_id": token,
              "persistent_runtime": False, "model_call_retried": False}
    for filename in ("prompt.txt", "events.jsonl", "stderr.txt", "final.txt"):
        path = output_dir / filename
        if path.exists():
            report[filename + "_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output_dir / "invocation.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
