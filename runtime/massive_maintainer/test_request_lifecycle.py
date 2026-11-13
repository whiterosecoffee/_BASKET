"""Offline request replay regressions; no live stores or credentials."""
import contextlib
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from runtime.massive_maintainer import test_maintain as fixtures
from runtime.massive_maintainer import maintain as m

class RequestLifecycleTests(unittest.TestCase):
    def setUp(self):
        fixtures.MaintenanceTests.setUp(self)
        from datetime import datetime
        self.clock=datetime.fromtimestamp((self.t+120000)/1000,m.UTC).isoformat()
        self.enterContext(patch.object(m,'now',return_value=self.clock))
        self.ev=[{'fetched_at':self.clock,'sha256':'fixture'}]
        self.coverage={'start_t':self.t,'end_t':self.t,'session':'RTH','completion':'all_minutes_present','timezone':'America/New_York','adjustment':'split_adjusted'}
    def publish(self):
        return m.promote(self.root,'NVDA',self.day,[self.row],self.ev,{},source_status='OK',pagination_complete=True,expected_head=m.partition_head(self.root,'NVDA',self.day))
    rewrite_index=fixtures.MaintenanceTests.rewrite_index
    def run_requests(self):
        legacy=self.root/'empty-legacy'; legacy.mkdir(exist_ok=True)
        args=SimpleNamespace(root=str(self.root),legacy=str(legacy),key_file='unused',
                             ticker='NVDA',dates='',audit_batch=0,history_batch=0)
        with patch.object(m,'require_admission',return_value='isolated-lifecycle-gate'), contextlib.redirect_stdout(io.StringIO()):
            m.run(args)

    def age(self):
        self.rewrite_index(lambda index: index['partitions']['NVDA/'+self.day].update(
            fetched_at='2000-01-01T00:00:00+00:00'))

    def test_same_fulfilled_request_reopens_after_expiry(self):
        self.publish(); self.age()
        request=m.resolve(self.pointer,'NVDA',self.day,self.t,coverage=self.coverage)
        def fetch(*args): return self.publish()
        with patch.object(m,'fetch_day',side_effect=fetch) as fetcher:
            self.run_requests()
            self.assertEqual(fetcher.call_count,1)
            self.run_requests()
            self.assertEqual(fetcher.call_count,1,'fresh fulfilment must coalesce')
            self.age()
            repeated=m.resolve(self.pointer,'NVDA',self.day,self.t,coverage=self.coverage)
            self.assertEqual(request['request'],repeated['request'])
            self.run_requests()
            self.assertEqual(fetcher.call_count,2,'expired fulfilment must reopen')
            self.run_requests()
            self.assertEqual(fetcher.call_count,2,'successful replay must coalesce')

    def test_consumer_age_requirement_persisted(self):
        request=m.resolve(self.pointer,'NVDA',self.day,self.t,max_age_seconds=5)
        self.assertEqual(m.read(Path(request['request']))['max_age_seconds'],5)

    def test_corrupt_fulfilled_snapshot_does_not_trigger_acquisition(self):
        request=m.resolve(self.pointer,'NVDA',self.day,self.t,coverage=self.coverage)
        result=self.publish()
        m.atomic(self.root/'fulfilled'/Path(request['request']).name,m.encode({'result':result['sha256']}))
        (self.root/result['path']).write_bytes(b'corrupt')
        with patch.object(m,'fetch_day',side_effect=AssertionError('must not fetch')) as fetcher:
            self.run_requests()
            self.assertEqual(m.read(self.root/'progress.json')['results'][0]['status'],'quarantined')
            fetcher.assert_not_called()
