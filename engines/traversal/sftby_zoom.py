#!/usr/bin/env python3
"""SFTBY traversal in USD: historical 200-session view and intraday zoom.
Read-only deterministic report; source bars and FX are preserved independently.
"""
import json, argparse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
def load(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def stats(b):
    low=min(x[3] for x in b); high=max(x[2] for x in b)
    return {"bars":len(b),"low_usd":low,"high_usd":high,"last_usd":b[-1][4],"range_position":(b[-1][4]-low)/(high-low) if high>low else None,"total_volume":sum(x[5] for x in b)}
def main():
    p=argparse.ArgumentParser();p.add_argument("--ticker",default="SFTBY");p.add_argument("--date",default=None);a=p.parse_args()
    d=load(ROOT/"tickers"/a.ticker/"history.jsonl")
    result={"ticker":a.ticker,"currency":"USD","as_of_daily":datetime.fromtimestamp(d[-1][0]/1000,timezone.utc).isoformat(),"daily":{str(n):stats(d[-n:]) for n in (5,20,60,200) if len(d)>=n}}
    if a.date:
        path=ROOT/"tickers"/a.ticker/"intraday"/f"{a.date}.5m.jsonl"
        bars=load(path)
        result["intraday"]={"date":a.date,"timeframe":"5m","partial_session":True,"as_of_bar_start_utc":datetime.fromtimestamp(bars[-1][0]/1000,timezone.utc).isoformat(),"observed":stats(bars),"last_vs_previous_daily_close":bars[-1][4]/d[-1][4]-1,"windows":{str(n):stats(bars[-n:]) for n in (5,12,24,48,78) if len(bars)>=n}}
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
