"""Compose the source audit with existing main traversal; no new data reader/store."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from collections import defaultdict
from datetime import datetime
from audit import ET, run

MAIN = '74d913e8913d630d85451344689e093aeea07efc'


def probe(source_root, source_sha, consumer_root):
    source_root, consumer_root = Path(source_root).resolve(), Path(consumer_root).resolve()
    audited = run(source_root, source_sha)
    head = subprocess.check_output(['git', '-C', str(consumer_root), 'rev-parse', 'HEAD'], text=True).strip()
    if head != MAIN:
        raise ValueError('consumer requires reviewed main revision')
    relative = 'engines/traversal/metrics.py'
    path = consumer_root / relative
    raw = path.read_bytes()
    committed = subprocess.check_output(['git', '-C', str(consumer_root), 'show', f'{head}:{relative}'])
    if raw != committed:
        raise ValueError('dirty consumer implementation')
    spec = importlib.util.spec_from_file_location('reviewed_metrics', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    groups = defaultdict(list)
    for source in sorted((source_root / 'tickers/CRWV/intraday').glob('*.jsonl')):
        for line in source.read_bytes().splitlines(keepends=True):
            row = json.loads(line)
            day = datetime.fromtimestamp(row[0] / 1000, ET).date().isoformat()
            groups[day].append((line, row))
    results = []
    for day, entries in sorted(groups.items()):
        # Known Oct1-Nov4 dates only; not a general exchange-calendar adapter.
        regular = [r for _, r in entries if 570 <= datetime.fromtimestamp(r[0] / 1000, ET).hour * 60
                   + datetime.fromtimestamp(r[0] / 1000, ET).minute < 960]
        cutoff = regular[-1][0] + 60000
        first = module.evaluate('CRWV', regular, interval_minutes=1, as_of=cutoff)
        if first != module.evaluate('CRWV', regular, interval_minutes=1, as_of=cutoff):
            raise ValueError('consumer replay differs')
        try:
            module.evaluate('CRWV', regular, interval_minutes=1, as_of=cutoff - 1)
        except ValueError:
            pass
        else:
            raise ValueError('consumer accepted an incomplete last bar')
        # Omit an interior minute in the final five; five-minute result must be unavailable.
        gapped = regular[:-3] + regular[-2:]
        if module.evaluate('CRWV', gapped, interval_minutes=1, as_of=cutoff)['windows']['5m'] is not None:
            raise ValueError('consumer accepted incomplete horizon')
        results.append({'session_date': day, 'daily_sha256': hashlib.sha256(b''.join(l for l, _ in entries)).hexdigest(),
                        'regular_observations': len(regular), 'horizon_available': {k: v is not None for k, v in first['windows'].items()},
                        'repeat_identical': True, 'future_bar_rejected': True, 'missing_minute_returns_null': True})
    if len(results) != 25:
        raise ValueError('unexpected date set')
    return {'schema': 'crwv.consumer_probe@1', 'source_head': source_sha, 'consumer_head': head,
            'consumer_path': relative, 'consumer_sha256': hashlib.sha256(raw).hexdigest(),
            'source_records_verified': audited['total_records'], 'sessions': results,
            'result': 'explicit_input_descriptive_consumer_verified', 'canonical_discovery': False,
            'historical_availability_verified': False, 'b01_acceptance': False,
            'limits': ['RTH filtering is bounded to these dates, not a general early-close calendar.',
                       'Observed VWAP anomalies remain; this is compatibility, not economic volume qualification.',
                       'Arithmetic completion cutoff does not establish historical first availability.',
                       'No source records persisted or canonical writer/reader selection changed.']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', required=True)
    p.add_argument('--expected-source', required=True)
    p.add_argument('--consumer-root', required=True)
    a = p.parse_args()
    print(json.dumps(probe(a.source_root, a.expected_source, a.consumer_root), indent=2))
