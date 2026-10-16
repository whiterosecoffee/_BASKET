#!/usr/bin/env python3
"""Local JSONL TTD ingestion runtime. Stdlib only. No provider access implied.
Input adapters must print a JSON observation on stdout; a failure does not refresh validity.
Usage:
 python runtime/ttd.py status --config runtime/feeds.json
 python runtime/ttd.py ingest --config runtime/feeds.json --feed JPYUSD_1M --input sample.json
 python runtime/ttd.py run --config runtime/feeds.json --feed JPYUSD_1M --command 'python adapters/fx.py'
"""
import argparse, datetime as dt, json, os, pathlib, subprocess, sys, time, hashlib
UTC=dt.timezone.utc
def utcnow(): return dt.datetime.now(UTC)
def iso(t): return t.astimezone(UTC).isoformat().replace("+00:00","Z")
def parse(s):
    t=dt.datetime.fromisoformat(s.replace("Z","+00:00"))
    if t.tzinfo is None: raise ValueError("timezone required")
    return t.astimezone(UTC)
def config(path):
    p=pathlib.Path(path).resolve()
    return p, json.loads(p.read_text())
def target(base, feed):
    p=(base.parent.parent/feed["path"]).resolve()
    if not p.is_relative_to(base.parent.parent): raise ValueError("unsafe path")
    return p
def last(path):
    if not path.exists(): return None
    result=None
    with path.open() as f:
        for line in f:
            if line.strip(): result=json.loads(line)
    return result
def expiry(obs):
    t=parse(obs["observed_at"])+dt.timedelta(seconds=int(obs["ttd_seconds"]))
    for dep in obs.get("dependency_expires_at",[]):
        d=parse(dep)
        if d<t: t=d
    if "calculation_ttd_seconds" in obs:
        d=parse(obs["computed_at"])+dt.timedelta(seconds=int(obs["calculation_ttd_seconds"]))
        if d<t:t=d
    return t
def status(obs,now=None):
    now=now or utcnow()
    if obs is None:return "unavailable"
    if obs.get("state") in ("unavailable","error","invalidated"):return obs["state"]
    if parse(obs["observed_at"])>now+dt.timedelta(seconds=10):return "invalidated"
    return "alive" if now<expiry(obs) else "dead"
def append(path,obs):
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(obs,sort_keys=True,separators=(",",":"))+"\n"
    # Exclusive advisory file lock on Unix; single-writer process required on Windows.
    with path.open("a",encoding="utf-8") as f:
        try:
            import fcntl
            fcntl.flock(f,fcntl.LOCK_EX)
        except ImportError: pass
        f.write(payload);f.flush();os.fsync(f.fileno())
def ingest(cfg_path,cfg,feed_id,raw):
    feed=next((f for f in cfg["feeds"] if f["id"]==feed_id),None)
    if feed is None:raise ValueError("unknown feed")
    if raw.get("entity_id")!=feed["entity_id"]:raise ValueError("entity mismatch")
    if "observed_at" not in raw or "source" not in raw:raise ValueError("source and observed_at required")
    now=utcnow();observed=parse(raw["observed_at"])
    if observed>now+dt.timedelta(seconds=10):raise ValueError("future observation")
    if "value" not in raw:raise ValueError("value required")
    deps=[]
    for dep_id in feed.get("depends_on",[]):
        dep=next(f for f in cfg["feeds"] if f["id"]==dep_id)
        d=last(target(cfg_path,dep))
        if status(d,now)!="alive":raise ValueError("dependency dead: "+dep_id)
        deps.append(iso(expiry(d)))
    obs={**raw,"feed_id":feed_id,"ingested_at":iso(now),"ttd_seconds":feed["ttd_seconds"],"dependency_expires_at":deps,"state":"valid"}
    if feed["kind"]=="computed_nav":
        if "computed_at" not in raw:raise ValueError("computed_at required")
        obs["calculation_ttd_seconds"]=feed["ttd_seconds"]
    obs["expires_at"]=iso(expiry(obs))
    obs["record_id"]=hashlib.sha256(json.dumps({k:v for k,v in obs.items() if k not in ("ingested_at","record_id")},sort_keys=True).encode()).hexdigest()
    path=target(cfg_path,feed)
    previous=last(path)
    if previous and previous.get("record_id")==obs["record_id"]:return obs,False
    append(path,obs)
    return obs,True
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    for action in ("status","ingest","run"):
        s=sub.add_parser(action);s.add_argument("--config",default="runtime/feeds.json")
        if action!="status":s.add_argument("--feed",required=True)
        if action=="ingest":s.add_argument("--input",required=True)
        if action=="run":
            s.add_argument("--command",required=True,help="trusted local adapter command")
            s.add_argument("--once",action="store_true")
    a=p.parse_args();cp,cfg=config(a.config)
    if a.action=="status":
        for f in cfg["feeds"]:
            o=last(target(cp,f));print(json.dumps({"feed":f["id"],"status":status(o),"expires_at":o.get("expires_at") if o else None,"enabled":f["enabled"]}))
    elif a.action=="ingest":
        o,w=ingest(cp,cfg,a.feed,json.loads(pathlib.Path(a.input).read_text()))
        print(json.dumps({"record_id":o["record_id"],"written":w,"status":status(o),"expires_at":o["expires_at"]}))
    else:
        feed=next(f for f in cfg["feeds"] if f["id"]==a.feed)
        if not feed["enabled"]:raise ValueError("feed disabled; configure source and enable explicitly")
        while True:
            try:
                result=subprocess.run(a.command,shell=True,capture_output=True,text=True,timeout=max(5,feed["interval_seconds"]))
                if result.returncode:raise RuntimeError(result.stderr[:500])
                obs,w=ingest(cp,cfg,a.feed,json.loads(result.stdout))
                print(json.dumps({"feed":a.feed,"written":w,"status":status(obs),"expires_at":obs["expires_at"]}),flush=True)
            except Exception as exc:
                print(json.dumps({"feed":a.feed,"error":str(exc),"status":"not_refreshed"}),file=sys.stderr,flush=True)
            if a.once:break
            time.sleep(feed["interval_seconds"])
if __name__=="__main__":main()
