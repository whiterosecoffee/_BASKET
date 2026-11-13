"""Offline owner-admission boundary; all paths are disposable."""
import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime,timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from runtime.massive_maintainer import maintain as m

class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.legacy=self.root/'legacy'; self.legacy.mkdir()
        self.day='2026-11-11'
        self.args=SimpleNamespace(root=str(self.root),legacy=str(self.legacy),key_file='unused',ticker='NVDA',dates=self.day,audit_batch=0,history_batch=0,admission_file=None)
        self.enterContext(patch('urllib.request.urlopen',side_effect=AssertionError('network forbidden')))
    def admit(self):
        records=m.inventory(self.root,self.legacy)
        payload={'schema':'basket.massive.admission@1','owner':m.OWNER,'source':'Massive',
                 'ticker':'NVDA','date':self.day,'grain':'1m','adjustment':'split_adjusted',
                 'purpose':'acquire_absent_day','authorization_ref':'synthetic-owner-approval',
                 'entitlement_ref':'synthetic-entitlement-evidence',
                 'expires_at':(datetime.now(m.UTC)+timedelta(minutes=5)).isoformat(),
                 'legacy_root':str(self.legacy.resolve()),'inventory_sha256':m.digest(m.encode(records)),
                 'index_sha256':m.digest((self.root/'index.json').read_bytes()) if (self.root/'index.json').exists() else None}
        path=self.root/'admission.json'; m.atomic(path,m.encode(payload)); self.args.admission_file=str(path)
        return path
    def run_fake(self):
        with patch.object(m,'fetch_day',return_value={'last_t':0,'sha256':'synthetic'}) as fetcher:
            with contextlib.redirect_stdout(io.StringIO()): m.run(self.args)
        receipt=m.read(self.root/'progress.json')
        self.assertTrue(list((self.root/'runs').glob('*.json')))
        return fetcher.call_count,receipt
    def test_explicit_date_without_admission(self):
        calls,receipt=self.run_fake(); self.assertEqual(calls,0)
        self.assertEqual(receipt['results'][0]['status'],'blocked')
    def test_default_dates_without_admission(self):
        self.args.dates=','.join([(datetime.now(m.ET).date()-timedelta(days=1)).isoformat(),datetime.now(m.ET).date().isoformat()])
        calls,receipt=self.run_fake(); self.assertEqual(calls,0); self.assertEqual(len(receipt['results']),2)
    def test_existing_legacy_no_index_even_with_admission(self):
        raw=b'{"t":0}\n'; path=self.legacy/'NVDA.jsonl';path.write_bytes(raw)
        self.admit(); calls,receipt=self.run_fake();self.assertEqual(calls,0)
        self.assertEqual(path.read_bytes(),raw)
    def test_malformed_request_quarantined_valid_plan_continues(self):
        self.admit();p=self.root/'requests'/'partial.json';p.parent.mkdir();p.write_bytes(b'{')
        calls,receipt=self.run_fake();self.assertEqual(calls,1)
        self.assertTrue(list((self.root/'quarantine').glob('request-*.json')))
        self.assertEqual(p.read_bytes(),b'{')
    def test_valid_bounded_absent_day(self):
        self.admit();calls,receipt=self.run_fake();self.assertEqual(calls,1)
    def test_changed_inventory_or_wrong_date_or_expiry_blocks(self):
        for field,value in [('inventory_sha256','wrong'),('date','2026-11-10'),('expires_at','2000-01-01T00:00:00+00:00'),('entitlement_ref','')]:
            with self.subTest(field=field):
                p=self.admit();body=m.read(p);body[field]=value;m.atomic(p,m.encode(body))
                calls,receipt=self.run_fake();self.assertEqual(calls,0)
    def test_new_local_file_invalidates_admission(self):
        self.admit();(self.legacy/'NVDA.jsonl').write_bytes(b'{}\n')
        calls,receipt=self.run_fake();self.assertEqual(calls,0)
    def test_invalid_request_shape_quarantined(self):
        self.args.dates='';p=self.root/'requests'/'bad.json';p.parent.mkdir();p.write_text('[]')
        calls,receipt=self.run_fake();self.assertEqual(calls,0)
        self.assertTrue(list((self.root/'quarantine').glob('request-*.json')))

    def test_missing_inventory_root_blocks(self):
        self.admit();self.legacy.rmdir()
        calls,receipt=self.run_fake();self.assertEqual(calls,0)
    def test_existing_indexed_date_blocks(self):
        m.atomic(self.root/'index.json',m.encode({'schema':m.SCHEMA,'source':'Massive','partitions':{'NVDA/'+self.day:{}}}))
        self.admit();calls,receipt=self.run_fake();self.assertEqual(calls,0)
    def test_actual_cli_defaults_block(self):
        argv=['maintain','--root',str(self.root),'--legacy',str(self.legacy),'--key-file','unused','--audit-batch','0','--history-batch','0']
        with patch('sys.argv',argv), patch.object(m,'fetch_day') as fetcher, contextlib.redirect_stdout(io.StringIO()):
            m.main()
        fetcher.assert_not_called()
        self.assertEqual(len(m.read(self.root/'progress.json')['results']),2)
