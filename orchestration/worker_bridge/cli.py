"""Run one explicit existing-profile assignment; no scheduler or automatic claims."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys

from .bridge import (ROOT, Blocked, UTC, assert_changed_scope, assert_fence,
                     collect_live, digest, load_controller, prepare, publication_inputs_unchanged, run_codex)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--controller-root", type=Path, required=True)
    p.add_argument("--task", type=Path, default=ROOT / "orchestration/worker_bridge/task.json")
    p.add_argument("--lease-comment-id", type=int, required=True)
    p.add_argument("--lease-id", required=True)
    p.add_argument("--profile", required=True)
    p.add_argument("--capability", action="append", required=True)
    p.add_argument("--attempt-id", required=True)
    p.add_argument("--instruction", type=Path, required=True)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--write", action="store_true", help="Explicit workspace-write; default agent is read-only")
    p.add_argument("--own-pr", type=int)
    args = p.parse_args()
    import re
    if not re.fullmatch(r"ATT-[A-Za-z0-9_.-]+", args.attempt_id):
        p.error("attempt ID must be immutable and path-safe")
    try:
        controller = load_controller(args.controller_root, json.loads((ROOT / "orchestration/worker_bridge/controller-lock.json").read_text()))
        task = json.loads(args.task.read_text())
        evidence, issue, events = collect_live(controller, task, args.lease_comment_id, dt.datetime.now(UTC), args.own_pr)
        prepared = prepare(controller, task, issue,
                           json.loads((ROOT / "orchestration/planner/worker-library.json").read_text()),
                           json.loads((ROOT / "orchestration/sparks.json").read_text()),
                           evidence, events, args.lease_id, args.capability, ROOT, dt.datetime.now(UTC),
                           args.profile, args.own_pr, args.attempt_id)
        assert_changed_scope(ROOT, task)
        if not args.execute:
            print(json.dumps(prepared, indent=2))
            return 0
        output = ROOT / "orchestration/worker_bridge/evidence" / args.attempt_id
        result = run_codex(ROOT, prepared, args.instruction.read_text(), output,
                           controller, events, dt.datetime.now(UTC), read_only=not args.write)
        # Preserve genuine failed invocation evidence too; success must survive a
        # second live ownership/lease check before it can be published as accepted.
        fresh_evidence, fresh_issue, fresh_events = collect_live(controller, task, args.lease_comment_id,
                                                                dt.datetime.now(UTC), args.own_pr)
        refreshed = prepare(controller, task, fresh_issue,
                json.loads((ROOT / "orchestration/planner/worker-library.json").read_text()),
                json.loads((ROOT / "orchestration/sparks.json").read_text()), fresh_evidence,
                fresh_events, args.lease_id, args.capability, ROOT, dt.datetime.now(UTC), args.profile, args.own_pr, args.attempt_id)
        publication_inputs_unchanged(prepared, refreshed)
        result["changed_paths"] = assert_changed_scope(ROOT, task)
        result["postflight_evidence_sha256"] = digest(fresh_evidence)
        (output / "publication-check.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "executed" else 2
    except (Blocked, ValueError, OSError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
