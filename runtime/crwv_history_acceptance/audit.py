"""Read-only, exact-source acceptance audit for PR122; never promotes data."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York')
SOURCE_SHA = '827dd1ee9e9239c5761013c05f320b30e795c84c'
RESEARCH = 'research/CRWV/market-research-2026-10-29'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def inspect(raw, day=None):
    if not raw or not raw.endswith(b'\n'):
        raise ValueError('empty or truncated input')
    rows = [json.loads(line) for line in raw.splitlines()]
    previous = -1
    dates = set()
    for r in rows:
        if not isinstance(r, list) or len(r) != 8:
            raise ValueError('eight fields required')
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in r):
            raise ValueError('invalid numeric field')
        t, o, h, l, c, v, vw, n = r
        if not isinstance(t, int) or t % 60000 or t <= previous:
            raise ValueError('unordered, duplicate or non-minute timestamp')
        if not (0 < l <= min(o, c) <= max(o, c) <= h and vw > 0 and v >= 0 and n >= 0 and int(n) == n):
            raise ValueError('invalid observation')
        dates.add(datetime.fromtimestamp(t / 1000, ET).date().isoformat())
        previous = t
    if day is not None and dates != {day}:
        raise ValueError('mixed or wrong session date')
    local = [datetime.fromtimestamp(r[0] / 1000, ET) for r in rows]
    return {'sha256': digest(raw), 'records': len(rows), 'dates': sorted(dates),
            'first_bar_start': local[0].isoformat(), 'last_bar_start': local[-1].isoformat(),
            'coverage_end_exclusive': datetime.fromtimestamp((rows[-1][0] + 60000) / 1000, ET).isoformat(),
            'regular_session_bars': sum(570 <= t.hour * 60 + t.minute < 960 for t in local),
            'vwap_outside_ohlc': sum(not r[3] <= r[6] <= r[2] for r in rows)}


def verify_meta(meta, info, day=None):
    for key, value in [('entity_id', 'CRWV'), ('source', 'Massive'), ('currency', 'USD'),
                       ('timezone', 'America/New_York'), ('timeframe', '1m'), ('adjusted', True),
                       ('records', info['records']), ('sha256', info['sha256']),
                       ('as_of_last_bar', info['coverage_end_exclusive'])]:
        if meta.get(key) != value:
            raise ValueError('metadata mismatch: ' + key)
    if day and meta.get('session_date') != day:
        raise ValueError('metadata session mismatch')
    if 'vwap_outside_ohlc' in meta and meta['vwap_outside_ohlc'] != info['vwap_outside_ohlc']:
        raise ValueError('anomalies not preserved')
    if 'regular_session_bars' in meta and meta['regular_session_bars'] != info['regular_session_bars']:
        raise ValueError('regular-session count mismatch')


def run(root):
    root = Path(root).resolve()
    head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if head != SOURCE_SHA:
        raise ValueError('source head differs; review and repin before acceptance')
    # Confirm working bytes match the pinned commit, not merely its HEAD label.
    paths = sorted((root / RESEARCH).glob('*')) + sorted((root / 'tickers/CRWV/intraday').glob('*'))
    inventory = []
    for path in paths:
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        committed = subprocess.check_output(['git', '-C', str(root), 'show', f'{head}:{relative}'])
        raw = path.read_bytes()
        if raw != committed:
            raise ValueError('dirty source: ' + relative)
        inventory.append({'path': relative, 'sha256': digest(raw)})
    folder = root / 'tickers/CRWV/intraday'
    source = folder / '2026-10.1m.jsonl'
    original = source.read_bytes()
    info = inspect(original)
    verify_meta(json.loads(source.with_suffix('.meta.json').read_text()), info)
    if (info['records'], len(info['dates']), info['vwap_outside_ohlc']) != (19186, 22, 2374):
        raise ValueError('October anchor mismatch')
    spec = importlib.util.spec_from_file_location('candidate_splitter', root / RESEARCH / 'prepare_daily_shards.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected = json.loads((root / RESEARCH / 'daily-shard-preparation.json').read_text())
    expected = {row['name']: row for row in expected['shards']}
    shards = []
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / 'stage'
        module.prepare(source, stage)
        before = {p.name: p.read_bytes() for p in stage.iterdir()}
        replay = module.prepare(source, stage)
        after = {p.name: p.read_bytes() for p in stage.iterdir()}
        if before != after or replay['added_files'] or replay['added_metadata_files']:
            raise ValueError('replay changes bytes')
        files = sorted(stage.glob('*.jsonl'))
        if set(p.name for p in files) != set(expected) or b''.join(p.read_bytes() for p in files) != original:
            raise ValueError('partition set or reassembly mismatch')
        for p in files:
            item = inspect(p.read_bytes(), p.name[:10])
            meta = json.loads(p.with_suffix('.meta.json').read_text())
            verify_meta(meta, item, p.name[:10])
            if meta['source_capture_sha256'] != digest(original):
                raise ValueError('lost source lineage')
            for key in ('sha256', 'records'):
                if item[key] != expected[p.name][key]:
                    raise ValueError('published manifest mismatch')
            if meta['historical_first_available_at'] is not None or meta['source_retrieved_at'] is not None:
                raise ValueError('invented source availability')
            shards.append({'file': p.name, **item})
    november = []
    for day, count in [('2026-11-02', 918), ('2026-11-03', 921), ('2026-11-04', 819)]:
        p = folder / (day + '.1m.jsonl')
        item = inspect(p.read_bytes(), day)
        meta = json.loads(p.with_suffix('.meta.json').read_text())
        verify_meta(meta, item, day)
        if item['records'] != count or meta['available_at'] is not None:
            raise ValueError('November count or availability mismatch')
        if day == '2026-11-04' and (meta['status'] != 'partial_extended_session' or item['coverage_end_exclusive'] != '2026-11-04T17:43:00-05:00'):
            raise ValueError('partial snapshot misrepresented')
        november.append({'file': p.name, **item})
    if source.read_bytes() != original:
        raise ValueError('source modified')
    return {'schema': 'crwv.acceptance_audit@1', 'source_head': head,
            'result': 'historical_bytes_verified_canonical_adoption_pending',
            'source_inventory': inventory, 'october': info, 'daily_partitions': shards,
            'november': november, 'total_records': info['records'] + sum(i['records'] for i in november),
            'replay_changed_files': 0, 'source_unchanged': True,
            'unknowns': ['Original Massive transport CSV unavailable to this audit; its recorded hash is not independent source retrieval proof.',
                         'Historical first availability unknown: no point-in-time tradability acceptance.',
                         'No provider entitlement, current-use TTD, live process, atomic production writer or restart proof.'],
            'canonical_adoption': False, 'b01_independent_ci': 'not_run'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.source_root), indent=2))
