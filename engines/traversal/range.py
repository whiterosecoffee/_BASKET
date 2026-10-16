#!/usr/bin/env python3
"""Reproducible multi-horizon range traversal from per-ticker JSONL.
No forecast probability or investment advice is implied.
"""
import argparse, json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]

def read_bars(path):
    bars=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not bars: raise ValueError("Empty bar history")
    if any(len(b)!=8 for b in bars): raise ValueError("Invalid bar shape")
    if any(bars[i][0]>=bars[i+1][0] for i in range(len(bars)-1)): raise ValueError("Unsorted or duplicate bars")
    return bars

def traverse(bars, windows=(5,20,60,200)):
    result={"observations":len(bars),"latest_timestamp":datetime.fromtimestamp(bars[-1][0]/1000,timezone.utc).isoformat(),"last_close":bars[-1][4],"windows":{}}
    for n in windows:
        if len(bars)<n: continue
        segment=bars[-n:]
        low=min(b[3] for b in segment);high=max(b[2] for b in segment)
        position=(segment[-1][4]-low)/(high-low) if high>low else None
        prior=bars[-n-1][4] if len(bars)>n else None
        result["windows"][str(n)]={"low":low,"high":high,"position":position,"return_from_prior_close":segment[-1][4]/prior-1 if prior else None,"volume_sum":sum(b[5] for b in segment)}
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("ticker")
    p.add_argument("--intraday-date",default=None)
    args=p.parse_args()
    ticker=args.ticker.upper()
    folder=ROOT/"tickers"/ticker
    daily=read_bars(folder/"history.jsonl")
    result={"ticker":ticker,"daily":traverse(daily)}
    if args.intraday_date:
        path=folder/"intraday"/f"{args.intraday_date}.5m.jsonl"
        intra=read_bars(path)
        result["intraday"]={"session_date":args.intraday_date,"partial_session":True,**traverse(intra,(5,12,24,48,78))}
        result["intraday"]["gap_from_prior_daily_close"]=intra[-1][4]/daily[-1][4]-1
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
