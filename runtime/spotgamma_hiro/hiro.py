"""Licensed user-export SpotGamma HIRO ingestion; offline, append-only."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

FIELDS = ("ticker", "hiro_usd", "range_30d_low_usd", "range_30d_high_usd")
OPTIONAL = ("spotgamma_price_usd", "hedge_wall", "key_gamma_strike", "key_delta_strike", "call_wall", "put_wall")
def normalize(raw):
    if not isinstance(raw, dict) or any(k not in raw for k in FIELDS):
        raise ValueError("missing required HIRO fields")
    ticker = raw["ticker"]
    if not isinstance(ticker, str) or not ticker.isupper() or not ticker.replace(".","").isalnum():
        raise ValueError("invalid ticker")
    for k in FIELDS[1:]:
        if type(raw[k]) not in (int,float):
            raise ValueError("invalid numeric field: "+k)
    if raw["range_30d_low_usd"] > raw["hiro_usd"] or raw["hiro_usd"] > raw["range_30d_high_usd"]:
        raise ValueError("HIRO outside reported range")
    for k in OPTIONAL:
        if raw.get(k) is not None and type(raw[k]) not in (int,float):
            raise ValueError("invalid optional numeric: "+k)
    stamp = raw.get("observed_at")
    if stamp is not None:
        from datetime import datetime, timezone
        dt=datetime.fromisoformat(stamp.replace("Z","+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("observed_at must contain UTC offset")
        stamp=dt.astimezone(timezone.utc).isoformat().replace("+00:00","Z")
    entry={"schema":"basket.spotgamma_hiro@1","source":"SpotGamma Alpha","ticker":ticker,
           **{k:raw[k] for k in FIELDS[1:]},
           **{k:raw.get(k) for k in OPTIONAL},
           "observed_at":stamp,"status":"historical_unknown_capture" if stamp is None else "timestamped_unverified_entitlement",
           "actionable":False}
    canonical=json.dumps(entry,sort_keys=True,separators=(",",":"),allow_nan=False)
    entry["record_id"]=hashlib.sha256(canonical.encode()).hexdigest()
    return entry

def ingest(source, destination):
    source=Path(source); destination=Path(destination)
    entries=[normalize(json.loads(line)) for line in source.read_text().splitlines() if line.strip()]
    destination.parent.mkdir(parents=True,exist_ok=True)
    existing=set()
    if destination.exists():
        for line in destination.read_text().splitlines():
            if line.strip():
                existing.add(json.loads(line)["record_id"])
    count=0
    with destination.open("a") as f:
        for entry in entries:
            if entry["record_id"] not in existing:
                f.write(json.dumps(entry,sort_keys=True,allow_nan=False)+"\n")
                existing.add(entry["record_id"]); count+=1
    return count

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("source");parser.add_argument("destination")
    args=parser.parse_args()
    print(json.dumps({"appended":ingest(args.source,args.destination),"live_feed":False}))
