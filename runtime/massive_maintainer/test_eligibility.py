"""Explicit current-consumer scope, separate from historical returned bars."""
import unittest
from datetime import datetime,timedelta
from unittest.mock import patch
from runtime.massive_maintainer import maintain as m
from runtime.massive_maintainer import test_maintain as fixtures

class EligibilityTests(unittest.TestCase):
    setUp=fixtures.MaintenanceTests.setUp
    def coverage(self):
        return {'session':'RTH','start_t':self.t,'end_t':self.t+120000,
                'completion':'all_minutes_present','timezone':'America/New_York','adjustment':'split_adjusted'}
    def publish(self,status='OK',rows=None):
        return m.promote(self.root,'NVDA',self.day,rows or [dict(self.row,t=self.t+i*60000) for i in range(3)],self.ev,{},source_status=status,pagination_complete=True,expected_head=m.partition_head(self.root,'NVDA',self.day))
    def resolve(self,coverage=True):
        return m.resolve(self.pointer,'NVDA',self.day,self.t+120000,coverage=self.coverage() if coverage else None)
    def test_complete_declared_scope_positive(self):
        clock=datetime.fromtimestamp((self.t+240000)/1000,m.UTC).isoformat()
        with patch.object(m,'now',return_value=clock):
            self.ev=[{'fetched_at':clock,'sha256':'fixture'}];self.publish()
            self.assertEqual(self.resolve()['status'],'qualified_current')
    def test_sparse_delayed_and_unknown_never_current(self):
        for status in ('DELAYED','unknown','OK'):
            with self.subTest(status=status):
                self.publish(status,[self.row,dict(self.row,t=self.t+120000)])
                self.assertNotEqual(self.resolve()['status'],'qualified_current')
                self.assertEqual(m.resolve(self.pointer,'NVDA',self.day)['status'],'qualified_historical')
    def test_missing_scope_not_current(self):
        self.publish();self.assertEqual(self.resolve(False)['reason'],'coverage_unknown')
    def test_refetch_does_not_refresh_observation_age(self):
        self.publish();self.assertEqual(self.resolve()['reason'],'stale_observation')
    def test_wrong_session_and_unknown_no_trade_are_not_fabricated(self):
        self.publish(rows=[self.row,dict(self.row,t=self.t+120000)])
        cov=self.coverage();cov['session']='PRE'
        self.assertEqual(m.resolve(self.pointer,'NVDA',self.day,self.t+120000,coverage=cov)['reason'],'coverage_unknown')
        self.assertEqual(self.resolve()['reason'],'coverage_unresolved')

    def test_fulfilment_uses_same_coverage_gate(self):
        self.publish('DELAYED')
        request={'ticker':'NVDA','date':self.day,'required_through':self.t+120000,'max_age_seconds':1200,'coverage':self.coverage()}
        self.assertFalse(m.fulfilled_request_is_current(self.root,request))
        self.publish('OK');request['coverage']=None
        self.assertFalse(m.fulfilled_request_is_current(self.root,request))
