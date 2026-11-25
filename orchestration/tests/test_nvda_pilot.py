"""Component checks for source freeze semantics; B01 tests are independently owned."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from orchestration.nvda_pilot.store import Pilot, PilotError, canonical, digest, freeze, sha
from runtime.ticker_data import TickerStore

ROOT = Path(__file__).resolve().parents[2]


def package(root):
    root.mkdir(parents=True)
    store = TickerStore(root)
    store.path = root / 'observations.jsonl'
    obs = json.loads((ROOT / 'runtime/fixtures/nvda/revenue.json').read_text())
    assert store.put(obs)['status'] == 'created'
    reports = root / 'reports'
    reports.mkdir()
    p = reports / 'synthetic.md'
    p.write_text('# Explicitly synthetic document for testing only\n')
    doc = {'entity_id': 'NVDA', 'local_file': p.name, 'retrieved_at': '2026-11-01T01:50:29Z',
           'source_url': 'https://example.invalid/nvda', 'content_sha256': sha(p)}
    (reports / 'manifest.jsonl').write_text(json.dumps(doc) + '\n')
    return root


class FreezeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = package(self.base / 'source')

    def test_snapshot_contains_source_hashes_and_is_stable(self):
        before = {str(p): sha(p) for p in self.source.rglob('*') if p.is_file()}
        a = freeze(self.source, '2026-11-04T00:00:00Z')
        self.assertEqual(a, freeze(self.source, '2026-11-04T00:00:00Z'))
        self.assertEqual(before, {str(p): sha(p) for p in self.source.rglob('*') if p.is_file()})
        self.assertEqual(a['manifest_id'], digest({k: v for k, v in a.items() if k != 'manifest_id'}))

    def test_duplicate_file_identity_is_rejected(self):
        m = freeze(self.source, '2026-11-04T00:00:00Z')
        m['files'].append(copy.deepcopy(m['files'][0]))
        m['manifest_id'] = digest({k: v for k, v in m.items() if k != 'manifest_id'})
        with self.assertRaises(PilotError):
            Pilot(self.base / 'target').stage(self.source, m)

    def test_wrong_document_identity_is_not_normalized(self):
        p = self.source / 'reports/manifest.jsonl'
        row = json.loads(p.read_text()); row['entity_id'] = 'OTHER'
        p.write_text(json.dumps(row) + '\n')
        with self.assertRaises(PilotError):
            freeze(self.source, '2026-11-04T00:00:00Z')

    def test_report_availability_requires_timestamp(self):
        p = self.source / 'reports/manifest.jsonl'
        row = json.loads(p.read_text()); row['retrieved_at'] = '2020-01-01'
        p.write_text(json.dumps(row) + '\n')
        with self.assertRaises(PilotError):
            freeze(self.source, '2026-11-04T00:00:00Z')

    def test_manifest_content_tampering_rejected(self):
        m = freeze(self.source, '2026-11-04T00:00:00Z')
        m['frozen_at'] = '2020-01-01T00:00:00Z'
        with self.assertRaises(PilotError):
            Pilot(self.base / 'target').stage(self.source, m)

    def test_extra_file_rejected_after_freeze(self):
        m = freeze(self.source, '2026-11-04T00:00:00Z')
        (self.source / 'extra.txt').write_text('unexpected')
        with self.assertRaises(PilotError):
            Pilot(self.base / 'target').stage(self.source, m)

    def test_raw_source_fingerprint_mismatch_rejected(self):
        (self.source / 'source').mkdir()
        (self.source / 'source/massive.csv').write_text('unrelated source')
        store = TickerStore(self.source); store.path = self.source / 'observations.jsonl'
        market = json.loads((ROOT / 'runtime/fixtures/nvda/revenue.json').read_text())
        market.update(kind='market_bar', source_record_id='synthetic-minute', source_fingerprint='a'*64,
                      value={'interval':'1m','adjustment_basis':'unadjusted','open':100,'high':101,'low':99,'close':100,'volume':10})
        self.assertEqual(store.put(market)['status'], 'created')
        with self.assertRaises(PilotError) as error:
            freeze(self.source, '2026-11-04T00:00:00Z')
        self.assertEqual(error.exception.code, 'SOURCE_MISMATCH')

    def test_cli_failure_is_structured(self):
        r = subprocess.run([sys.executable, '-m', 'orchestration.nvda_pilot.cli', '--root', str(self.base / 'target'),
                            'report', '--as-of', '2026-11-04T00:00:00Z'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)['code'], 'BLOCKED_CANONICAL_DATA')

    def test_identical_activation_retry_is_safe(self):
        m = freeze(self.source, '2026-11-04T00:00:00Z'); pilot = Pilot(self.base / 'target')
        pilot.stage(self.source, m); pilot.activate(m['manifest_id'])
        self.assertEqual(pilot.activate(m['manifest_id'])['status'], 'unchanged')


if __name__ == '__main__':
    unittest.main()
