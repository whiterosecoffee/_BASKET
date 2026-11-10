"""Offline CSV-to-daily staging candidate; no canonical ingestion or live feed.

Replaces the old monthly writer. Outputs immutable capture shards in an external
staging directory. A changed capture, revision or older-gap fill must use a new
staging generation and B02 review; no existing JSONL is silently rewritten.
"""
import argparse
import csv
import json
import re
import tempfile
from pathlib import Path
from datetime import datetime
from prepare_daily_shards import ET, digest, prepare


def capture(source, output, month):
    source, output = Path(source), Path(output)
    repository = Path(__file__).resolve().parents[3]
    if output.resolve().is_relative_to(repository):
        raise ValueError('External staging required; canonical adoption belongs to B02')
    if not re.fullmatch(r'\d{4}-\d{2}', month):
        raise ValueError('Expected YYYY-MM month')
    datetime.strptime(month, '%Y-%m')
    marker = output / 'capture.manifest.json'
    identity = {'month': month, 'source_csv_sha256': digest(source.read_bytes())}
    if marker.exists():
        if json.loads(marker.read_text()) != identity:
            raise ValueError('Changed capture requires a new staging generation')
    elif output.exists() and any(output.iterdir()):
        raise ValueError('Unidentified nonempty staging directory; use a new generation')
    rows = {}
    count = duplicates = 0
    with source.open(newline='') as f:
        for r in csv.DictReader(f):
            count += 1
            if r['ticker'] != 'CRWV':
                raise ValueError('Wrong ticker')
            row = [int(r['t'])] + [float(r[k]) for k in ('o', 'h', 'l', 'c', 'v', 'vw')] + [int(r['n'])]
            if datetime.fromtimestamp(row[0] / 1000, ET).strftime('%Y-%m') != month:
                raise ValueError('Out-of-month observation')
            if row[0] in rows:
                if rows[row[0]] != row:
                    raise ValueError('Conflicting source duplicate')
                duplicates += 1
            rows[row[0]] = row
    if count >= 50000:
        raise ValueError('Potential truncated capture: require pagination evidence')
    payload = ''.join(json.dumps(rows[t], separators=(',', ':'), allow_nan=False) + '\n' for t in sorted(rows)).encode()
    # prepare validates numeric/OHLC/time invariants and preflights every output
    # collision before publishing files. Source capture hash is retained.
    with tempfile.TemporaryDirectory() as folder:
        staged = Path(folder) / (month + '.1m.jsonl')
        staged.write_bytes(payload)
        staged.with_suffix('.meta.json').write_text(json.dumps({
            'sha256': digest(payload), 'source': 'Massive', 'adjusted': True,
            'recorded_at': None, 'historical_first_available_at': None, 'source_retrieved_at': None,
            'captures': [{'sha256': digest(source.read_bytes()), 'records': count, 'retrieved_at': None}]
        }))
        result = prepare(staged, output)
    if not marker.exists():
        with marker.open('x') as f:
            f.write(json.dumps(identity, indent=2) + '\n')
    result.update({'duplicate_source_rows': duplicates, 'source_csv_sha256': digest(source.read_bytes()),
                   'replay_policy': 'identical_capture_only; changed_capture_requires_new_staging_generation'})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True)
    parser.add_argument('--output', required=True, help='External staging directory, never canonical root')
    parser.add_argument('--month', default='2026-10')
    args = parser.parse_args()
    source = Path(args.source_dir) / ('CRWV-' + args.month + '-minute-source.csv')
    print(json.dumps(capture(source, args.output, args.month), indent=2))
