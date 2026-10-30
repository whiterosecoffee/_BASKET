"""Validate Massive CSV captures and append missing minute records without revisions.

Uses the repository's existing market.intraday@1 positional layout. CSV is a
transport from Massive MCP, not a second quote adapter. Conflicting existing
observations fail closed; an owner-audited revision is required to replace them.
"""
import argparse, csv, hashlib, json, math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York')
FIELDS = ['timestamp_ms','open','high','low','close','volume','vwap','transactions']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(row):
    assert len(row) == 8 and isinstance(row[0], int) and row[0] % 60000 == 0
    assert all(isinstance(v, (int,float)) and math.isfinite(v) for v in row)
    t,o,h,l,c,v,vw,n = row
    assert min(o,h,l,c,vw) > 0 and v >= 0 and n >= 0 and int(n) == n
    assert l <= min(o,c) <= max(o,c) <= h, ('OHLC', row)

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',required=True);p.add_argument('--root',required=True)
    p.add_argument('--month',default='2026-10');a=p.parse_args();root=Path(a.root);sources=sorted(Path(a.source_dir).glob(f'CRWV-{a.month}-minute-source.csv'))
    assert len(sources)==1, 'Expected one monthly capture'
    folder=root/'tickers/CRWV/intraday';folder.mkdir(parents=True,exist_ok=True)
    target=folder/(a.month+'.1m.jsonl');existing={}
    if target.exists():
        for line in target.open():
            row=json.loads(line);validate(row);assert row[0] not in existing;existing[row[0]]=row
    incoming={};duplicates=0;capture_manifest=[]
    for source in sources:
        count=0
        for r in csv.DictReader(source.open()):
            assert r['ticker']=='CRWV'
            row=[int(r['t'])]+[float(r[k]) for k in ('o','h','l','c','v','vw')]+[int(r['n'])]
            validate(row);count+=1
            if row[0] in incoming:
                assert row == incoming[row[0]], 'Conflicting source duplicate'
                duplicates+=1
            incoming[row[0]]=row
        assert count < 50000, 'Potential truncated capture requires pagination'
        capture_manifest.append({'month':source.name[5:12],'records':count,'sha256':sha(source),'retrieved_at':None})
    for t,row in existing.items():
        if t in incoming: assert row==incoming[t], 'Source revision: do not overwrite'
    merged=dict(existing);merged.update(incoming);rows=[merged[t] for t in sorted(merged)]
    added=len(merged)-len(existing)
    # An initial historical backfill is sorted; subsequent captures must append
    # at the tail. Older gaps need an explicit backfill/revision generation.
    if existing:
        last_existing=max(existing)
        assert not any(t < last_existing and t not in existing for t in incoming), 'Older gap requires explicit backfill generation'
    if added:
        mode='a' if existing else 'w'
        with target.open(mode) as f:
            for row in rows:
                if row[0] not in existing:f.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n')
    dates=defaultdict(list);sessions=Counter();vwap_outside=0
    for r in rows:
        dt=datetime.fromtimestamp(r[0]/1000,ET);minute=dt.hour*60+dt.minute
        dates[dt.date().isoformat()].append(r)
        sessions['premarket' if minute<570 else 'regular' if minute<960 else 'afterhours']+=1
        vwap_outside+=not (r[3]<=r[6]<=r[2])
    metadata={'schema':'market.intraday@1','entity_id':'CRWV','source':'Massive','timeframe':'1m','fields':FIELDS,'currency':'USD','timezone':'America/New_York','timestamp_semantics':'UTC epoch milliseconds at minute start','adjusted':True,'start':datetime.fromtimestamp(rows[0][0]/1000,ET).isoformat(),'as_of_last_bar':datetime.fromtimestamp((rows[-1][0]+60000)/1000,ET).isoformat(),'records':len(rows),'sessions':len(dates),'session_record_counts':dict(sessions),'sha256':sha(target),'recorded_at':datetime.now(timezone.utc).isoformat(),'historical_first_available_at':None,'source_retrieved_at':None,'feed_status':'historical aggregates; current tail latency measured separately; realtime entitlement not inferred','status':'historical_backfill_with_partial_latest_session','captures':capture_manifest,'notes':['One-minute OHLCV aggregates, not individual trade ticks.','No missing minute is fabricated; absence can mean no qualifying trades or a source gap.','Existing daily history.jsonl is preserved unchanged.','VWAP outside reported OHLC is retained and flagged, not corrected.','Source request exact retrieval instants were not exposed by MCP; recorded_at is local materialization time.']}
    mp=folder/(a.month+'.1m.meta.json')
    if added or not mp.exists():mp.write_text(json.dumps(metadata,indent=2)+'\n')
    summary={'total_records':len(rows),'added':added,'duplicate_source_rows':duplicates,'sessions':len(dates),'first':metadata['start'],'cutoff':metadata['as_of_last_bar'],'vwap_outside_ohlc':vwap_outside,'sha256':sha(target),'unique_timestamps':len(merged)==len(rows),'strict_order':all(b[0]>a[0] for a,b in zip(rows,rows[1:]))}
    print(json.dumps(summary))

if __name__=='__main__':main()
