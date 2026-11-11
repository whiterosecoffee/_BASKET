"""Bounded reference only: no network client, durable root or existing FETCH import."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / 'objects.json'


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def instant(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timezone required')
    return dt.astimezone(timezone.utc)


def strict_load(data):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError('duplicate JSON key')
            result[k] = v
        return result
    return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def qualify(capture):
    if set(capture) != {'format', 'source_mode', 'provider', 'endpoint', 'params', 'ticker', 'session', 'captured_at', 'rows'}:
        raise ValueError('capture fields')
    if capture['format'] != 'basket.data_capture@1' or capture['provider'] != 'massive':
        raise ValueError('source identity')
    if capture['source_mode'] not in ('connector_projection', 'synthetic'):
        raise ValueError('source mode')
    ticker, day = capture['ticker'], capture['session']
    if not isinstance(ticker, str) or not re.fullmatch(r'[A-Z][A-Z0-9.]{0,15}', ticker):
        raise ValueError('ticker')
    if not isinstance(day, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', day):
        raise ValueError('session')
    datetime.strptime(day, '%Y-%m-%d')
    endpoint = f'/v2/aggs/ticker/{ticker}/range/1/minute/{day}/{day}'
    if capture['endpoint'] != endpoint or capture['params'] != {'adjusted': True, 'sort': 'asc', 'limit': 50000}:
        raise ValueError('endpoint/basis mismatch')
    if type(capture['params']['adjusted']) is not bool:
        raise ValueError('adjustment type')
    captured = instant(capture['captured_at'])
    if not isinstance(capture['rows'], list) or not capture['rows']:
        raise ValueError('no source rows')
    return captured


def sanitize(capture):
    captured = qualify(capture)
    unique = {}
    duplicates = 0
    for row in capture['rows']:
        if not isinstance(row, dict) or set(row) != {'t', 'o', 'h', 'l', 'c', 'v', 'vw', 'n'}:
            raise ValueError('bar fields')
        if type(row['t']) is not int or row['t'] % 60000 or type(row['n']) is not int or row['n'] < 0:
            raise ValueError('grain/count')
        for field in ('o', 'h', 'l', 'c', 'v', 'vw'):
            if type(row[field]) not in (int, float) or not math.isfinite(row[field]):
                raise ValueError('non-finite/non-numeric bar')
        if min(row[x] for x in ('o', 'h', 'l', 'c', 'vw')) <= 0 or row['v'] < 0:
            raise ValueError('invalid price/volume')
        if not row['l'] <= min(row['o'], row['c']) <= max(row['o'], row['c']) <= row['h']:
            raise ValueError('OHLC order')
        dt = datetime.fromtimestamp(row['t'] / 1000, timezone.utc)
        if dt.astimezone(ZoneInfo('America/New_York')).date().isoformat() != capture['session']:
            raise ValueError('mixed session')
        if row['t'] / 1000 + 60 > captured.timestamp():
            raise ValueError('bar unavailable at capture')
        if row['t'] in unique:
            if encoded(row) != encoded(unique[row['t']]):
                raise ValueError('conflicting duplicate')
            duplicates += 1
        unique[row['t']] = row
    rows = [unique[t] for t in sorted(unique)]
    return rows, duplicates


def build(capture_bytes):
    capture = strict_load(capture_bytes)
    rows, duplicates = sanitize(capture)
    partition = b''.join(encoded(row) for row in rows)
    manifest = {
        'format': 'basket.verified_partition@1', 'source_mode': capture['source_mode'],
        'provider': 'massive', 'ticker': capture['ticker'], 'session': capture['session'],
        'grain': '1m', 'currency': 'USD', 'adjusted': True,
        'volume': 'provider_shares_fractional_preserved', 'timezone': 'America/New_York',
        'coverage': 'observed_bars_only_not_complete_session_certification',
        'available_at': capture['captured_at'], 'historical_first_available_at': None,
        'source_sha256': digest(capture_bytes), 'partition_sha256': digest(partition),
        'contract_sha256': digest(CONTRACT.read_bytes()), 'rows': len(rows),
        'duplicates_removed': duplicates, 'verification': 'reference_checks_passed',
    }
    return {'capture.json': capture_bytes, 'bars.jsonl': partition, 'receipt.json': encoded(manifest)}


def safe_files(directory):
    directory = Path(directory)
    if directory.is_symlink() or any(p.is_symlink() for p in directory.parents):
        raise ValueError('symlink directory')
    if {p.name for p in directory.iterdir()} != {'capture.json', 'bars.jsonl', 'receipt.json'}:
        raise ValueError('incomplete/unexpected artifact set')
    for name in ('capture.json', 'bars.jsonl', 'receipt.json'):
        if not (directory / name).is_file() or (directory / name).is_symlink():
            raise ValueError('unsafe artifact')
    return directory


def verify(directory):
    directory = safe_files(directory)
    expected = build((directory / 'capture.json').read_bytes())
    for name, data in expected.items():
        if (directory / name).read_bytes() != data:
            raise ValueError('changed source, partition, contract or receipt: ' + name)
    return strict_load(expected['receipt.json'])


def write_capture(capture_path, root):
    files = build(Path(capture_path).read_bytes())  # No writes until all rows qualify.
    receipt = strict_load(files['receipt.json'])
    root = Path(root).absolute()
    if root.is_symlink() or any(p.is_symlink() for p in root.parents):
        raise ValueError('symlink root')
    root.mkdir(parents=True, exist_ok=True)
    name = receipt['ticker'] + '.' + receipt['session'] + '.1m.adjusted'
    destination = root / name
    if destination.exists() or destination.is_symlink():
        verify(destination)
        if any((destination / name).read_bytes() != data for name, data in files.items()):
            raise ValueError('existing partition differs; explicit revision required')
        return destination, 'unchanged'
    temporary = Path(tempfile.mkdtemp(prefix='.staging-', dir=root))
    try:
        for name, data in files.items():
            with (temporary / name).open('xb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        verify(temporary)
        # A nonempty existing target cannot be replaced by rename. Single writer proof only.
        temporary.rename(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination, 'created'


def read_verified(directory, *, ticker, session, as_of, expected_source_sha256, allow_synthetic=False):
    manifest = verify(directory)
    if manifest['ticker'] != ticker or manifest['session'] != session:
        raise ValueError('consumer identity mismatch')
    if manifest['source_sha256'] != expected_source_sha256:
        raise ValueError('consumer source pin mismatch')
    if manifest['source_mode'] == 'synthetic' and not allow_synthetic:
        raise ValueError('synthetic forbidden')
    if instant(manifest['available_at']) > instant(as_of):
        raise ValueError('not available as of requested time')
    # Re-read and hash the exact returned bytes rather than trusting a previous read.
    data = (Path(directory) / 'bars.jsonl').read_bytes()
    if digest(data) != manifest['partition_sha256']:
        raise ValueError('partition changed during read')
    return [strict_load(line) for line in data.splitlines()], manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--capture', required=True)
    p.add_argument('--root', required=True, help='Explicit isolated test root, not automatic canonical storage')
    args = p.parse_args()
    destination, disposition = write_capture(args.capture, args.root)
    print(json.dumps({'directory': str(destination), 'disposition': disposition, 'receipt': verify(destination)}, sort_keys=True))


if __name__ == '__main__':
    main()
