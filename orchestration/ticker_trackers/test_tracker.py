import copy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from orchestration.ticker_trackers.tracker import Tracker, dashboard, config


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / 'tracker.sqlite')
        self.now = '2026-10-26T14:00:00Z'
        self.tracker = Tracker(self.path, lambda: self.now)

    def tearDown(self):
        self.tracker.close()
        self.temp.cleanup()

    def item(self, **changes):
        value = {'schema':'basket.ticker_panel@1', 'ticker':'ORCL', 'panel':'market',
                 'effective_at':self.now, 'observed_at':self.now, 'available_at':self.now,
                 'expires_at':'2026-10-26T15:00:00Z', 'classification':'source_fact',
                 'verification':'verified', 'sources':[{'url':'https://example.com/fixture', 'label':'SYNTHETIC TEST ONLY'}],
                 'data':{'last_usd':100}, 'method_version':'synthetic-test-1', 'supersedes':None, 'input_revisions':[]}
        value.update(changes)
        return value

    def panel(self, name='market', **kwargs):
        return next(p for p in self.tracker.snapshot(**kwargs)['panels'] if p['id'] == name)

    def test_missing_and_policy_coverage(self):
        snapshot = self.tracker.snapshot()
        self.assertEqual(len(snapshot['refresh_work']), 8)
        self.assertTrue(all(p['current_data'] is None for p in snapshot['panels']))
        self.assertEqual(set(config()['benchmarks']), {'QQQ','NVDA','IBM','HYG','IEF','USO'})
        self.assertAlmostEqual(sum(config()['baseline']['weights'].values()), 1)

    def test_idempotent_durable_immutable(self):
        item = self.item()
        rid = self.tracker.append(item)
        self.assertEqual(rid, self.tracker.append(item))
        self.assertEqual(len(self.tracker.all()), 1)
        other = Tracker(self.path, lambda:self.now)
        self.assertEqual(other.all()[0]['revision_id'],rid)
        other.close()
        for sql in ('DELETE FROM revisions', "UPDATE revisions SET payload='{}'"):
            with self.assertRaises(sqlite3.IntegrityError):
                self.tracker.db.execute(sql)

    def test_correction_and_point_in_time(self):
        original = self.tracker.append(self.item())
        self.now = '2026-10-26T14:01:00Z'
        correction = self.item(supersedes=original, data={'last_usd':101})
        self.tracker.append(correction)
        self.assertEqual(self.panel()['current_data']['last_usd'],101)
        self.assertEqual(self.panel(as_of='2026-10-26T14:00:30Z')['current_data']['last_usd'],100)
        self.assertEqual(self.panel()['changes'], [{'field':'last_usd','before':100,'after':101}])
        with self.assertRaises(ValueError):
            self.tracker.append(self.item(supersedes=original,data={'last_usd':102}))

    def test_late_ingestion_not_backdated_into_replay(self):
        item = self.item()
        self.now = '2026-10-26T14:01:00Z'
        self.tracker.append(item)
        self.assertEqual(self.panel(as_of='2026-10-26T14:00:30Z')['status'],'missing')

    def test_ttl_caps_publisher_expiry(self):
        self.tracker.append(self.item())
        self.now = '2026-10-26T14:02:00Z'
        self.assertEqual(self.panel()['status'],'stale')
        self.assertIsNone(self.panel()['current_data'])
        self.assertIsNotNone(self.panel()['latest'])

    def test_unverified_correction_suppresses_old_verified_signal(self):
        rid = self.tracker.append(self.item())
        self.now = '2026-10-26T14:00:30Z'
        self.tracker.append(self.item(supersedes=rid,verification='disputed'))
        self.assertEqual(self.panel()['status'],'disputed')
        self.assertIsNone(self.panel()['current_data'])

    def test_dependency_staleness_and_supersession(self):
        rid = self.tracker.append(self.item())
        self.tracker.append(self.item(panel='traversal', classification='derived', input_revisions=[rid], data={'regime':'balance'}))
        self.assertEqual(self.panel('traversal')['status'],'current')
        self.now = '2026-10-26T14:02:00Z'
        self.assertEqual(self.panel('traversal')['status'],'dependency_invalid')
        self.now = '2026-10-26T14:01:00Z'
        self.tracker.append(self.item(supersedes=rid))
        self.assertEqual(self.panel('traversal')['status'],'dependency_invalid')

    def test_reject_invalid_inputs_without_partial_write(self):
        cases = [dict(observed_at='2026-10-26T14:00:00'), dict(available_at='2026-10-27T00:00:00Z'),
                 dict(expires_at=self.now),dict(panel='unknown'),dict(data={'x':float('nan')}),
                 dict(input_revisions=['missing']),dict(sources=[]),dict(ingested_at=self.now),
                 dict(sources=[{'url':'javascript:alert(1)','label':'bad'}]),dict(supersedes='missing')]
        for case in cases:
            with self.subTest(case=case), self.assertRaises((ValueError,TypeError)):
                self.tracker.append(self.item(**case))
        self.assertEqual(self.tracker.all(),[])

    def test_scenario_and_future_effective_not_current(self):
        self.tracker.append(self.item(classification='scenario'))
        self.assertEqual(self.panel()['status'],'scenario')
        self.now='2026-10-26T14:01:00Z'
        self.tracker.append(self.item(effective_at='2026-10-27T14:00:00Z'))
        self.assertEqual(self.panel()['status'],'future_effective')

    def test_html_escapes_provider_payload(self):
        self.tracker.append(self.item(data={'note':'<script>alert(1)</script>'}))
        page = dashboard(self.tracker.snapshot())
        self.assertNotIn('<script>',page)
        self.assertIn('&lt;script&gt;',page)
        self.assertIn('not a live feed',page)
        self.assertIn('Refresh queue',page)

    def test_cli_init_snapshot_refresh_html(self):
        for command in ('init','snapshot','refresh','html','history'):
            result = subprocess.run([sys.executable,'-m','orchestration.ticker_trackers.tracker','--db',self.path,command],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            if command in ('snapshot','refresh','history'):
                json.loads(result.stdout)


if __name__ == '__main__':
    unittest.main()
