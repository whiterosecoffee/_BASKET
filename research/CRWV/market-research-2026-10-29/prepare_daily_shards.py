"""Losslessly stage a monthly capture for B02 review; never change its source.

Output must be an external staging directory. Canonical adoption and removal of
the monthly file require B02 acceptance. Unknown availability stays unknown.
"""
import argparse
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare(source, output):
    source, output = Path(source), Path(output)
    if output.resolve().is_relative_to(source.parent.resolve()):
        raise ValueError('Use external staging; canonical directory is read-only')
    raw = source.read_bytes()
    if not raw or not raw.endswith(b'\n'):
        raise ValueError('Empty or incomplete source')
    groups = defaultdict(list)
    previous = -1
    anomalies = 0
    for line in raw.splitlines(keepends=True):
        r = json.loads(line)
        if not isinstance(r, list) or len(r) != 8:
            raise ValueError('Expected eight-field bar')
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in r):
            raise ValueError('Non-finite or non-numeric field')
        t, o, h, l, c, v, vw, n = r
        if not isinstance(t, int) or t % 60000 or t <= previous:
            raise ValueError('Timestamps must be unique, ordered minute starts')
        if not (0 < l <= min(o, c) <= max(o, c) <= h and vw > 0 and v >= 0 and n >= 0 and int(n) == n):
            raise ValueError('Invalid OHLC, price, volume or count')
        day = datetime.fromtimestamp(t / 1000, ET).date().isoformat()
        groups[day].append(line)
        anomalies += not l <= vw <= h
        previous = t
    files = {day + '.1m.jsonl': b''.join(lines) for day, lines in sorted(groups.items())}
    if b''.join(files.values()) != raw:
        raise ValueError('Reassembly differs from source')
    # Preflight every collision before writing any shard; replay is byte stable.
    for name, data in files.items():
        p = output / name
        if p.exists() and p.read_bytes() != data:
            raise ValueError('Conflicting staged file: ' + name)
    output.mkdir(parents=True, exist_ok=True)
    added = 0
    for name, data in files.items():
        p = output / name
        if not p.exists():
            with p.open('xb') as f:
                f.write(data)
            added += 1
    return {'source_sha256': digest(raw), 'records': sum(map(len, groups.values())),
            'day_count': len(groups), 'added_files': added,
            'byte_identical_reassembly': True, 'vwap_outside_ohlc': anomalies,
            'historical_first_available_at': None, 'source_retrieved_at': None,
            'status': 'staging_only_pending_B02_acceptance',
            'shards': [{'name': name, 'records': len(groups[name[:10]]),
                        'bytes': len(data), 'sha256': digest(data)} for name, data in files.items()]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.output), indent=2))
