import copy
import tempfile
import unittest
from pathlib import Path
from engines.valuation.orcl_bridge.example import fixture
from orchestration.ticker_trackers.tracker import Tracker, dashboard
from orchestration.ticker_trackers.publish_valuation import publish


class ValuationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.now='2026-10-26T14:00:00Z'
        self.tracker=Tracker(str(Path(self.temp.name)/'orcl.sqlite'),lambda:self.now)
        self.bundle=fixture(self.now)

    def tearDown(self):
        self.tracker.close();self.temp.cleanup()

    def seed(self):
        target=self.bundle['companies']['ORCL']
        data={'market':{'last_usd':target['quote']['data']['price']},
              'financing':{'balance':target['balance']['data']},
              'fundamentals':{'data_mode':'synthetic','forecast':target['forecast']['data'],
                 'peers':{k:v for k,v in self.bundle['companies'].items() if k!='ORCL'},
                 'peer_weights':self.bundle['peer_weights'],'scenarios':self.bundle['scenarios']}}
        for panel,payload in data.items():
            envelope={'schema':'basket.ticker_panel@1','ticker':'ORCL','panel':panel,'effective_at':self.now,
                'observed_at':self.now,'available_at':self.now,'expires_at':'2026-10-26T15:00:00Z',
                'classification':'source_fact','verification':'verified',
                'sources':[{'url':'https://example.com/synthetic-only','label':'SYNTHETIC TEST'}],
                'data':payload,'method_version':'synthetic-test-1','supersedes':None,'input_revisions':[]}
            self.tracker.append(envelope)

    def panel(self):
        return next(p for p in self.tracker.snapshot()['panels'] if p['id']=='valuation')

    def test_source_panels_to_engine_to_ledger_to_dashboard(self):
        self.seed(); result=publish(self.tracker)
        self.assertEqual(result['status'],'published_conditional')
        self.assertFalse(result['eligible'])
        panel=self.panel()
        self.assertEqual(panel['status'],'synthetic')
        self.assertIsNone(panel['current_data'])
        self.assertAlmostEqual(panel['conditional_data']['target']['stats']['eps'],2.24)
        self.assertIn('SYNTHETIC DEMONSTRATION',dashboard(self.tracker.snapshot()))
        self.assertIn('valuation',[r['panel'] for r in self.tracker.snapshot()['refresh_work']])
        self.assertEqual(publish(self.tracker)['status'],'unchanged')

    def test_expiry_hides_conditional_output(self):
        self.seed();publish(self.tracker)
        self.now='2026-10-26T14:02:00Z'
        self.assertEqual(self.panel()['status'],'stale')
        self.assertIsNone(self.panel()['conditional_data'])
        self.assertEqual(publish(self.tracker)['status'],'blocked')

    def test_correction_invalidates_then_recomputes(self):
        self.seed();publish(self.tracker)
        market=next(r for r in self.tracker.all() if r['panel']=='market')
        old=market.pop('revision_id');market.pop('ingested_at')
        self.now='2026-10-26T14:00:30Z'
        market.update(supersedes=old,observed_at=self.now,available_at=self.now,effective_at=self.now)
        market['data']['last_usd']=55
        self.tracker.append(market)
        self.assertEqual(self.panel()['status'],'dependency_invalid')
        self.assertIsNone(self.panel()['conditional_data'])
        self.assertEqual(publish(self.tracker)['status'],'published_conditional')
        self.assertEqual(self.panel()['conditional_data']['target']['quote']['price'],55)
        self.assertEqual(self.panel()['revision_count'],2)

    def test_missing_upstream_does_not_publish(self):
        self.assertEqual(publish(self.tracker)['status'],'blocked')
        self.assertEqual(self.tracker.all(),[])


if __name__=='__main__':unittest.main()
