"""Purpose-specific timestamp truth, current recency, and as-of evidence."""
import unittest
from datetime import datetime,timedelta
from unittest.mock import patch
from runtime.massive_maintainer import maintain as m
from runtime.massive_maintainer import test_eligibility as fixtures

class PurposeTests(unittest.TestCase):
    setUp=fixtures.EligibilityTests.setUp
    coverage=fixtures.EligibilityTests.coverage
    publish=fixtures.EligibilityTests.publish
    def historical(self,purpose='historical_interval',as_of=None):
        return m.resolve(self.pointer,'NVDA',self.day,self.t+120000,coverage=self.coverage(),purpose=purpose,as_of=as_of)
    def test_historical_stable_as_clock_advances_without_refresh(self):
        self.publish()
        for year in (2027,2037):
            with patch.object(m,'now',return_value=datetime(year,1,1,tzinfo=m.UTC).isoformat()):
                self.assertEqual(m.resolve(self.pointer,'NVDA',self.day,purpose='historical')['status'],'qualified_historical')
                self.assertEqual(self.historical()['status'],'qualified_historical')
        self.assertFalse((self.root/'requests').exists())
    def test_historical_has_no_recency_policy(self):
        self.publish()
        self.assertEqual(m.resolve(self.pointer,'NVDA',self.day,purpose='historical',max_age_seconds=None)['status'],'qualified_historical')
        self.assertEqual(m.resolve(self.pointer,'NVDA',self.day,self.t+120000,purpose='historical_interval',max_age_seconds=float('inf'),coverage=self.coverage())['status'],'qualified_historical')
    def test_asof_known_vintage_and_correction_lookahead(self):
        vintage=datetime.fromtimestamp((self.t+180000)/1000,m.UTC)
        self.ev=[{'fetched_at':vintage.isoformat(),'sha256':'fixture'}];self.publish()
        cutoff=(vintage+timedelta(minutes=1)).isoformat()
        self.assertEqual(self.historical('as_of',cutoff)['status'],'qualified_as_of')
        before=m.partition_head(self.root,'NVDA',self.day)
        self.ev=[{'fetched_at':(vintage+timedelta(days=1)).isoformat(),'sha256':'new-fixture'}]
        self.publish(rows=[dict(self.row,t=self.t+i*60000,c=2) for i in range(3)])
        result=self.historical('as_of',cutoff)
        self.assertEqual(result['reason'],'vintage_after_as_of')
        self.assertNotEqual(m.partition_head(self.root,'NVDA',self.day),before)
    def test_asof_unknown_vintage_and_event_lookahead_reject(self):
        self.publish()
        cutoff=datetime.fromtimestamp((self.t+60000)/1000,m.UTC).isoformat()
        self.assertEqual(self.historical('as_of',cutoff)['reason'],'event_after_as_of')
        idx=m.read(self.root/'index.json');idx['partitions']['NVDA/'+self.day]['raw'][0].pop('fetched_at');m.atomic(self.root/'index.json',m.encode(idx))
        self.assertEqual(self.historical('as_of','2040-01-01T00:00:00+00:00')['reason'],'vintage_availability_unknown')
    def test_delayed_historical_complete_but_latest_refuses(self):
        self.publish('DELAYED')
        self.assertEqual(self.historical()['status'],'qualified_historical')
        self.assertEqual(m.resolve(self.pointer,'NVDA',self.day,self.t+120000,coverage=self.coverage(),purpose='latest_complete')['reason'],'source_delayed')
    def test_sparse_historical_scope_and_wrong_ticker_reject(self):
        self.publish(rows=[self.row,dict(self.row,t=self.t+120000)])
        self.assertEqual(self.historical()['reason'],'coverage_unresolved')
        self.assertEqual(m.resolve(self.pointer,'AAOI',self.day,purpose='historical')['reason'],'missing')
    def test_latest_still_rejects_infinity_and_unknown_purpose(self):
        with self.assertRaises(m.FreshnessContractError):m.resolve(self.pointer,'NVDA',self.day,self.t,coverage=self.coverage(),purpose='latest_complete',max_age_seconds=float('inf'))
        with self.assertRaises(ValueError):m.resolve(self.pointer,'NVDA',self.day,purpose='invented')

    def test_exchange_local_date_and_ticker_mapping(self):
        stamp=int(datetime(2026,11,11,0,30,tzinfo=m.UTC).timestamp())*1000
        exchange_day='2026-11-10'
        self.assertEqual(m.date_of(stamp),exchange_day)
        m.promote(self.root,'NVDA',exchange_day,[dict(self.row,t=stamp)],self.ev,{},expected_head=None)
        result=m.resolve(self.pointer,'NVDA',exchange_day,purpose='historical')
        self.assertEqual(result['status'],'qualified_historical')
        self.assertEqual(m.resolve(self.pointer,'NVDA','2026-11-11',purpose='historical')['reason'],'missing')
        self.assertEqual(m.resolve(self.pointer,'AAOI',exchange_day,purpose='historical')['reason'],'missing')
    def test_historical_fulfilment_never_expires_by_clock(self):
        self.publish()
        request={'ticker':'NVDA','date':self.day,'purpose':'historical_interval','required_through':self.t+120000,'coverage':self.coverage(),'max_age_seconds':None}
        with patch.object(m,'now',return_value='2040-01-01T00:00:00+00:00'):
            self.assertTrue(m.fulfilled_request_is_current(self.root,request))
