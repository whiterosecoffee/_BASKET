"""Actual local consumer acceptance with network denied; produces private receipt."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch
from .maintain import resolve,read,atomic,encode,now

def main():
    p=argparse.ArgumentParser(); p.add_argument('--pointer',required=True)
    p.add_argument('--day',required=True); args=p.parse_args()
    with patch('urllib.request.urlopen',side_effect=AssertionError('independent Massive call')) as network:
        result=resolve(args.pointer,'NVDA',args.day)
        assert result['status']=='qualified_historical'
        rows=[json.loads(line) for line in Path(result['path']).read_bytes().splitlines()]
        assert len(rows)==result['rows']
        assert {r['ticker'] for r in rows}=={'NVDA'}
        assert {r['session_date'] for r in rows}=={args.day}
        current=resolve(args.pointer,'NVDA',args.day,result['last_t'])
        stale=resolve(args.pointer,'NVDA',args.day,result['last_t']+60000)
        assert stale['status']=='refresh_required'
        network.assert_not_called()
    receipt={'at':now(),'consumer':'_Ticker NVDA acceptance example','rows_read':len(rows),
             'day':args.day,'sha256':result['sha256'],'independent_network_calls':network.call_count,
             'historical':result['status'],'current_at_last_observation':current['status'],
             'beyond_last_observation':stale['status'],
             'all_workers_integrated':False}
    root=Path(read(Path(args.pointer))['root'])
    atomic(root/'consumer-acceptance.json',encode(receipt))
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
