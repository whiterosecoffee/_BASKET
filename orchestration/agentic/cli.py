"""CLI: run fresh evidence-gated scheduling; optionally invoke safe local B00 validators."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from .manager import GuardError, evaluate, load_events, run_safe_checks
from .github_adapter import collect

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--queue", type=Path, required=True)
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument("--live-github", action="store_true")
    source.add_argument("--evidence", type=Path)
    p.add_argument("--events", type=Path)
    p.add_argument("--decision-log", type=Path)
    p.add_argument("--check", action="append", default=[])
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--max-evidence-age", type=int, default=900)
    args=p.parse_args()
    try:
        now=dt.datetime.now(dt.timezone.utc)
        queue=json.loads(args.queue.read_text(encoding="utf-8"))
        if args.live_github:
            token=os.environ.get("GITHUB_TOKEN")
            if not token:
                raise GuardError("GITHUB_TOKEN required for live inventory; no stale fallback")
            def fetch(path):
                if not path.startswith("/repos/whiterosecoffee/_BASKET/"):
                    raise GuardError("unapproved Github REST path")
                req=Request("https://api.github.com"+path,
                            headers={"Authorization":"Bearer "+token,
                                     "Accept":"application/vnd.github+json",
                                     "X-GitHub-Api-Version":"2022-11-28",
                                     "User-Agent":"basket-agentic-readonly"})
                with urlopen(req,timeout=15) as response:
                    return json.loads(response.read().decode("utf-8"))
            evidence=collect(queue,fetch,now)
        else:
            evidence=json.loads(args.evidence.read_text(encoding="utf-8"))
        report=evaluate(queue,evidence,load_events(args.events) if args.events else [],
                        now,max_age_seconds=args.max_evidence_age)
        if args.check:
            report["local_checks"]=run_safe_checks(args.root,args.check)
        if args.decision_log:
            args.decision_log.parent.mkdir(parents=True,exist_ok=True)
            with args.decision_log.open("a",encoding="utf-8") as out:
                out.write(json.dumps(report,sort_keys=True)+"\n")
                out.flush();os.fsync(out.fileno())
        print(json.dumps(report,indent=2))
        return 0 if all(c["status"]=="pass" for c in report.get("local_checks",[])) else 2
    except (GuardError,OSError,ValueError,TimeoutError) as error:
        print(json.dumps({"status":"fail_closed","error":str(error)}),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
