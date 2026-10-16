#!/usr/bin/env python3
"""Compute time-to-data freshness without assuming the provider is live."""
import json, argparse
from datetime import datetime,timezone
def parse(s):return datetime.fromisoformat(s.replace("Z","+00:00"))
def assess(observation,now):
    if observation.get("value") is None:return "unavailable"
    if observation.get("freshness_status") in ("conflicted","unavailable"):return observation["freshness_status"]
    t=parse(observation["observed_at"])
    if t>now:return "conflicted"
    if (now-t).total_seconds()>observation["ttd_seconds"]:return "stale"
    return observation.get("freshness_status","fresh")
def main():
    p=argparse.ArgumentParser();p.add_argument("json_path");p.add_argument("--as-of");a=p.parse_args()
    now=parse(a.as_of) if a.as_of else datetime.now(timezone.utc)
    data=json.load(open(a.json_path))
    items=data if isinstance(data,list) else [data]
    for item in items:print(json.dumps({"entity_id":item["entity_id"],"field":item["field"],"status":assess(item,now),"as_of":now.isoformat()}))
if __name__=="__main__":main()
