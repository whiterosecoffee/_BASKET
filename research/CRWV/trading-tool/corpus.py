"""Read pinned PR69 source corpus without copying or importing its implementation."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

PIN = '6d82bccacaaba9855ef6bd27c64d72eb0514c8c9'
PATTERN_HASH = 'd9949861839f7844801845c10c8b1f3dd54159afe017262ca9ecc9d445e2580c'
HASHES = {'CRWV-minute-bars.csv': 'ade323e63835e590f025d1211390d771c3905b2d5063fc3fd13c7db0a35256dd',
          'CRWV-daily-bars.csv': '75fc88dd5223ccfd2538f1092bea1dacc9420e2684265e1913812f15f9143c3e'}


def csv_bars(path):
    with Path(path).open() as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    for row in rows:
        row['t'] = int(row['t'])
    return rows


def load(root):
    root = Path(root)
    manifest = json.loads((root/'manifest.json').read_text())
    for name, expected in HASHES.items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('pinned corpus hash mismatch: '+name)
    pattern_file = root/'CRWV.range-patterns.jsonl'
    expected = PATTERN_HASH
    if manifest['files']['CRWV.range-patterns.jsonl'] != expected:
        raise ValueError('pinned manifest pattern hash mismatch')
    if hashlib.sha256(pattern_file.read_bytes()).hexdigest() != expected:
        raise ValueError('pattern file hash mismatch')
    minutes = csv_bars(root/'CRWV-minute-bars.csv')
    return {'ticker': 'CRWV', 'currency': 'USD', 'bars': minutes,
            'daily': csv_bars(root/'CRWV-daily-bars.csv'), 'profiles': minutes,
            'patterns': [json.loads(s) for s in pattern_file.read_text().splitlines() if s],
            'source': {'source_id': 'PR69@'+PIN, 'provider': 'Massive',
                       'source_commit': PIN, 'observation_kind': 'historical',
                       'entitlement': 'historical aggregates observed; realtime not established',
                       'retrieved_at': None, 'ingested_at': manifest['ingested_at'],
                       'available_at': None, 'adjustment': 'split-adjusted',
                       'file_hashes': dict(HASHES, **{'CRWV.range-patterns.jsonl': expected})}}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--source', required=True); p.add_argument('--out', required=True)
    a = p.parse_args(); Path(a.out).write_text(json.dumps(load(a.source), allow_nan=False))
