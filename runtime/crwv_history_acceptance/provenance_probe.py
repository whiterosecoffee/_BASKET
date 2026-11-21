"""Replay preserved private transport CSVs; emit metadata only, never adopt data."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import zipfile
from audit import RESEARCH, digest, inspect, run

CAPTURES = {
    '2026-10': ('CRWV-2026-10-minute-source.csv', '4e5cee44828b552ff54f79d9a88fdd8d5d0bc1c1d9c8653228ec1ac630c29852'),
    '2026-11': ('CRWV-nov4-source.csv', '4bf12d43a25bc4129844129921e340e60514858bbb8902e7cdb754a5670a6e5b'),
}


def probe(root, source_sha, archive):
    root = Path(root).resolve()
    audit = run(root, source_sha)
    research = root / RESEARCH
    sys.path.insert(0, str(research))
    spec = importlib.util.spec_from_file_location('source_backfill', research / 'backfill_minutes.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results = []
    with zipfile.ZipFile(archive) as z, tempfile.TemporaryDirectory() as temp:
        for month, (name, expected_hash) in CAPTURES.items():
            matches = [n for n in z.namelist() if n == name or n.endswith('/' + name)]
            if len(matches) != 1:
                raise ValueError('missing or ambiguous capture: ' + name)
            raw = z.read(matches[0])
            if digest(raw) != expected_hash:
                raise ValueError('transport capture hash mismatch: ' + name)
            csv = Path(temp) / name
            csv.write_bytes(raw)
            stage = Path(temp) / month
            first = module.capture(csv, stage, month)
            before = {p.name: p.read_bytes() for p in stage.iterdir()}
            replay = module.capture(csv, stage, month)
            if before != {p.name: p.read_bytes() for p in stage.iterdir()}:
                raise ValueError('transport replay mutated outputs')
            expected = audit['daily_partitions'] if month == '2026-10' else audit['november']
            if set(p.name for p in stage.glob('*.jsonl')) != {x['file'] for x in expected}:
                raise ValueError('partition set mismatch')
            for item in expected:
                actual = inspect((stage / item['file']).read_bytes(), item['file'][:10])
                if any(actual[k] != item[k] for k in actual):
                    raise ValueError('CSV replay differs from candidate: ' + item['file'])
            results.append({'source_csv': name, 'sha256': expected_hash,
                            'records': sum(x['records'] for x in expected),
                            'daily_partitions': len(expected), 'duplicate_rows': first['duplicate_source_rows'],
                            'candidate_daily_bytes_match': True, 'replay_unchanged': True,
                            'replay_added_files': replay['added_files']})
    return {'schema': 'crwv.transport_provenance@1', 'source_head': source_sha,
            'archive_sha256': digest(Path(archive).read_bytes()), 'captures': results,
            'total_records': audit['total_records'], 'source_unchanged': True,
            'limitations': ['Preserved CSV identity and deterministic conversion verified; vendor truth and original retrieval time remain unverified.',
                           'Temporary staging only; no canonical write, writer activation or independent B01 acceptance.']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', required=True)
    p.add_argument('--expected-source', required=True)
    p.add_argument('--archive', required=True)
    a = p.parse_args()
    print(json.dumps(probe(a.source_root, a.expected_source, a.archive), indent=2))
