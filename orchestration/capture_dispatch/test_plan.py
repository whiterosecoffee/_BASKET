import json
import tempfile
import unittest
from pathlib import Path
from plan import compile_plan, discover

NOW = '2026-10-18T03:00:00Z'

class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.entities = {t: {'id': t, 'type': 'public_equity'} for t in ('MU', 'NVDA', 'CRWV', 'LITE', 'AAOI', 'SFTBY')}

    def test_full_fanout_and_idempotency(self):
        first = compile_plan(self.entities, {}, NOW)
        self.assertEqual(len(first['tasks']), 42)
        self.assertEqual(first, compile_plan(self.entities, {}, NOW))
        self.assertEqual(len({t['task_key'] for t in first['tasks']}), 42)

    def test_fresh_stale_future_and_unverified(self):
        record = {'observed_at': '2026-10-18T01:00:00Z', 'first_available_at': '2026-10-18T01:00:00Z',
                  'expires_at': '2026-10-18T04:00:00Z', 'record_ids': ['r1'], 'source_ids': ['s1']}
        def status(r):
            result = compile_plan(self.entities, {'MU': {'market': r}}, NOW)
            return next(x['status'] for x in result['coverage'] if x['ticker'] == 'MU' and x['capability'] == 'market')
        self.assertEqual(status(record), 'fresh')
        self.assertEqual(status(dict(record, expires_at=NOW)), 'stale')
        self.assertEqual(status(dict(record, first_available_at='2026-10-19T01:00:00Z')), 'invalid_time')
        self.assertEqual(status(dict(record, source_ids=[])), 'unverified')

    def test_private_and_candidate(self):
        self.entities['OPENAI'] = {'id': 'OPENAI', 'type': 'private_company'}
        result = compile_plan(self.entities, {}, NOW, ['MU', 'TTMI'])
        self.assertEqual(result['unregistered_candidates'], ['TTMI'])
        self.assertFalse(any(t['ticker'] == 'OPENAI' and t['capability'] == 'market' for t in result['tasks']))

    def test_blocked_and_naive_time(self):
        result = compile_plan(self.entities, {'MU': {'market': {'status': 'blocked'}}}, NOW)
        task = next(t for t in result['tasks'] if t['task_key'] == 'capture:MU:market')
        self.assertEqual(task['action'], 'resolve_gap')
        with self.assertRaises(ValueError):
            compile_plan(self.entities, {}, '2026-10-18T03:00:00')

    def test_discovery_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                discover(root)
            path = Path(root) / 'MU'
            path.mkdir()
            (path / 'entity.json').write_text(json.dumps(self.entities['MU']))
            self.assertEqual(set(discover(root)), {'MU'})
            (path / 'entity.json').write_text(json.dumps(dict(self.entities['MU'], id='NVDA')))
            with self.assertRaises(ValueError):
                discover(root)

    def test_malformed_coverage_cannot_appear_fresh(self):
        for coverage in ([], {'MU': []}, {'MU': {'market': []}}):
            with self.assertRaises(ValueError):
                compile_plan(self.entities, coverage, NOW)
        for field, bad in [('record_ids', 'r1'), ('source_ids', [None]), ('observed_at', 123)]:
            record = {'observed_at': '2026-10-18T01:00:00Z', 'first_available_at': '2026-10-18T01:00:00Z',
                      'expires_at': '2026-10-18T04:00:00Z', 'record_ids': ['r1'], 'source_ids': ['s1']}
            record[field] = bad
            result = compile_plan(self.entities, {'MU': {'market': record}}, NOW)
            row = next(r for r in result['coverage'] if r['ticker'] == 'MU' and r['capability'] == 'market')
            self.assertEqual(row['status'], 'unverified')

    def test_invalid_candidates_and_empty_universe(self):
        for candidates in ('MU', ['../MU'], [None]):
            with self.assertRaises(ValueError):
                compile_plan(self.entities, {}, NOW, candidates)
        with self.assertRaises(ValueError):
            compile_plan({}, {}, NOW)

if __name__ == '__main__':
    unittest.main()
