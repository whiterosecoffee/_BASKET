#!/usr/bin/env python3
"""Validate independent BASKET ticker stores and daily historical bars."""
import json, pathlib, sys
from datetime import datetime, timezone
from jsonschema import Draft202012Validator
root=pathlib.Path(__file__).resolve().parents[1]
schemas={k:json.loads((root/"schemas"/f"{k}.v1.json").read_text()) for k in ("entity","events","relationships")}
daily=json.loads((root/"schemas/history/market.daily.v1.json").read_text())
errors=[]
for folder in sorted((root/"tickers").iterdir()):
 if not folder.is_dir(): continue
 for kind in ("entity","events","relationships"):
  p=folder/f"{kind}.json"
  try:
   data=json.loads(p.read_text())
   Draft202012Validator(schemas[kind]).validate(data)
   if (data.get("id") or data.get("entity_id"))!=folder.name: raise ValueError("entity mismatch")
  except Exception as exc: errors.append(f"{p}: {exc}")
 p=folder/"history.jsonl"
 if not p.exists(): errors.append(f"{p}: missing");continue
 if json.loads((folder/"entity.json").read_text()).get("type")!="public_equity":
  print(f"{folder.name}: private/non-public history (daily OHLCV not required)")
  continue
 prev=-1; count=0
 for i,line in enumerate(p.read_text().splitlines(),1):
  try:
   bar=json.loads(line); Draft202012Validator(daily).validate(bar)
   ts,o,h,l,c,v,*_=bar
   if not (ts>prev and h>=max(o,l,c) and l<=min(o,h,c)): raise ValueError("time order or OHLC inconsistency")
   prev=ts;count+=1
  except Exception as exc: errors.append(f"{p}:{i}: {exc}")
 if count<200:errors.append(f"{p}: only {count} daily bars")
 meta=folder/"history.meta.json"
 try:
  m=json.loads(meta.read_text())
  if m["records"]!=count or m["entity_id"]!=folder.name:raise ValueError("metadata mismatch")
 except Exception as exc:errors.append(f"{meta}: {exc}")
 print(f"{folder.name}: {count} bars")
if errors:
 print("\n".join(errors),file=sys.stderr);sys.exit(1)
print("Validation passed")
