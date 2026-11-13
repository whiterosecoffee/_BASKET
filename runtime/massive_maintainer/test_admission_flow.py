"""Request -> real admission -> fake transport -> local consumption.

Permit references are synthetic owner attestations, not authenticated authority.
No require_admission or fetch_day mock is used in these integration fixtures.
"""
import contextlib
import io
import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from runtime.massive_maintainer import maintain as m
from runtime.massive_maintainer import test_admission as fixtures
from runtime.massive_maintainer import test_freshness_contract as freshness

class AdmissionFlowTests(unittest.TestCase):
    admit=fixtures.AdmissionTests.admit
    def setUp(self):
        fixtures.AdmissionTests.setUp(self)
        self.args.dates=''
        self.t=int(datetime(2026,11,11,15,tzinfo=m.UTC).timestamp())*1000
        self.clock=datetime.fromtimestamp((self.t+180000)/1000,m.UTC).isoformat()
        self.enterContext(patch.object(m,'now',return_value=self.clock))
        self.pointer=self.root/'pointer.json';m.atomic(self.pointer,m.encode({'schema':m.SCHEMA,'root':str(self.root)}))
        self.coverage={'session':'RTH','start_t':self.t,'end_t':self.t+120000,'completion':'all_minutes_present','timezone':'America/New_York','adjustment':'split_adjusted'}
        key=self.root/'key';key.write_text('SYNTHETIC_ONLY');self.args.key_file=str(key)
    def demand(self):
        return m.resolve(self.pointer,'NVDA',self.day,self.t+120000,coverage=self.coverage)
    def run_quiet(self):
        with contextlib.redirect_stdout(io.StringIO()):m.run(self.args)
    def accepted(self):
        request=self.demand();self.admit()
        ref=m.encode({'results':{'ticker':'NVDA','market':'stocks','locale':'us','currency_name':'usd','cik':'fixture-cik'}})
        bars=m.encode({'status':'OK','ticker':'NVDA','adjusted':True,'results':[{'t':self.t+i*60000,'o':1,'h':2,'l':1,'c':1,'v':'3.125'} for i in range(3)]})
        responses=iter([ref,bars])
        with patch('urllib.request.urlopen',side_effect=lambda *a,**kw:io.BytesIO(next(responses))) as transport,patch('time.sleep'):
            self.run_quiet();self.assertEqual(transport.call_count,2)
        self.assertTrue((self.root/'fulfilled'/Path(request['request']).name).exists())
        self.assertEqual(self.demand()['status'],'qualified_current')
    def test_accepted_absent_range_without_authorization_mock(self):
        self.accepted()
        self.assertEqual(m.read(self.root/'progress.json')['provider_calls'],2)
    def test_unapproved_request_zero_transport_and_durable_block(self):
        self.demand()
        with patch('urllib.request.urlopen') as transport:self.run_quiet();transport.assert_not_called()
        self.assertEqual(m.read(self.root/'progress.json')['results'][0]['status'],'blocked')
    def test_existing_date_refresh_stays_blocked(self):
        self.accepted()
        index=m.read(self.root/'index.json');index['partitions']['NVDA/'+self.day]['fetched_at']='2000-01-01T00:00:00+00:00'
        m.atomic(self.root/'index.json',m.encode(index));before=(self.root/'index.json').read_bytes()
        self.assertEqual(self.demand()['status'],'refresh_required');self.admit()
        with patch('urllib.request.urlopen') as transport:self.run_quiet();transport.assert_not_called()
        self.assertEqual((self.root/'index.json').read_bytes(),before)
        self.assertTrue(any(r['status']=='blocked' for r in m.read(self.root/'progress.json')['results']))
    def test_invalid_freshness_requests_quarantined_without_transport(self):
        for i,value in enumerate(freshness.FreshnessContractTests.invalid):
            m.atomic(self.root/'requests'/(str(i)+'.json'),m.encode({'ticker':'NVDA','date':self.day,'required_through':self.t,'max_age_seconds':value}))
        with patch('urllib.request.urlopen') as transport:self.run_quiet();transport.assert_not_called()
        results=m.read(self.root/'progress.json')['results']
        self.assertEqual(len(results),len(freshness.FreshnessContractTests.invalid))
        self.assertTrue(all(r['status']=='quarantined' and r['contract_error']=='invalid_freshness_budget' for r in results))
