"""Single-writer filesystem inbox for licensed SpotGamma user exports; no API implied."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from hiro import ingest

def freshness(record, *, now=None, ttd_seconds=120):
    stamp=record.get("observed_at")
    if not stamp: return "unknown_capture_time"
    try:
        observed=datetime.fromisoformat(stamp.replace("Z","+00:00"))
        if observed.tzinfo is None or observed.utcoffset() is None: return "invalid_capture_time"
        age=((now or datetime.now(timezone.utc))-observed.astimezone(timezone.utc)).total_seconds()
        if age < -10: return "future_capture_time"
        return "within_ttd" if age <= ttd_seconds else "expired"
    except (ValueError,TypeError): return "invalid_capture_time"

def scan(inbox,out,*,ttd_seconds=120,now=None):
    inbox,out=Path(inbox),Path(out)
    inbox.mkdir(parents=True,exist_ok=True)
    before=out.read_text().count("\n") if out.exists() else 0
    errors={}
    for source in sorted(inbox.glob("*.jsonl")):
        if source.resolve()==out.resolve(): continue
        try: ingest(source,out)
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc: errors[source.name]=str(exc)
    rows=[json.loads(s) for s in out.read_text().splitlines() if s.strip()] if out.exists() else []
    latest={}
    for row in rows:
        t=row["ticker"]
        if t not in latest or (row.get("observed_at") or "")>(latest[t].get("observed_at") or ""):latest[t]=row
    return {"schema":"basket.hiro_health@1","source":"SpotGamma Alpha user-export",
        "live_provider_connected":False,"tracked":len(latest),"appended":len(rows)-before,"errors":errors,
        "symbols":{t:{"hiro_usd":r["hiro_usd"],"observed_at":r.get("observed_at"),
            "freshness":freshness(r,now=now,ttd_seconds=ttd_seconds),"actionable":False}
            for t,r in sorted(latest.items())}}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inbox",required=True);p.add_argument("--output",required=True)
    p.add_argument("--status",required=True);p.add_argument("--interval",type=int,default=5)
    p.add_argument("--ttd",type=int,default=120);p.add_argument("--once",action="store_true")
    args=p.parse_args()
    if args.interval<1 or args.ttd<1:p.error("interval and ttd must be positive")
    while True:
        health=scan(args.inbox,args.output,ttd_seconds=args.ttd)
        target=Path(args.status);target.parent.mkdir(parents=True,exist_ok=True)
        temp=target.with_suffix(target.suffix+".tmp")
        temp.write_text(json.dumps(health,indent=2,sort_keys=True)+"\n")
        temp.replace(target)
        if args.once:
            print(json.dumps(health,sort_keys=True));break
        time.sleep(args.interval)

if __name__=="__main__":main()
