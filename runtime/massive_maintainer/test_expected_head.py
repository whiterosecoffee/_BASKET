"""Expected-head publication controls on disposable single-writer stores."""
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from runtime.massive_maintainer import maintain as m
from runtime.massive_maintainer import test_maintain as fixtures

class ExpectedHeadTests(unittest.TestCase):
    setUp=fixtures.MaintenanceTests.setUp
    def publish(self,expected,change=False):
        rows=[dict(self.row,c=2)] if change else [self.row]
        return m.promote(self.root,'NVDA',self.day,rows,self.ev,{},expected_head=expected)
    def test_first_replacement_and_current_head_noop(self):
        first=self.publish(None);second=self.publish(first['sha256'],True)
        self.assertEqual(second['supersedes'],first['sha256'])
        before=(self.root/'index.json').read_bytes()
        same=self.publish(second['sha256'],True)
        self.assertEqual(same['outcome'],'unchanged');self.assertEqual((self.root/'index.json').read_bytes(),before)
    def test_missing_and_malformed_expectations(self):
        with self.assertRaisesRegex(ValueError,'expected head'):
            m.promote(self.root,'NVDA',self.day,[self.row],self.ev,{})
        for value in ('',True,[],{},'invalid'):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError,'expected head'):self.publish(value)
        self.assertFalse((self.root/'index.json').exists())
    def test_stale_or_absence_cannot_overwrite(self):
        first=self.publish(None);second=self.publish(first['sha256'],True);before=(self.root/'index.json').read_bytes()
        for stale in (None,first['sha256'],'0'*64):
            with self.subTest(stale=stale):
                with self.assertRaisesRegex(ValueError,'expected head'):self.publish(stale)
                self.assertEqual((self.root/'index.json').read_bytes(),before)
    def test_concurrent_claim_cannot_enter_owned_writer(self):
        with m.writer(self.root):
            with ThreadPoolExecutor(max_workers=1) as pool:
                with self.assertRaises(FileExistsError):pool.submit(self.publish,None).result()
        self.assertFalse((self.root/'index.json').exists())
    def test_index_rechecked_after_staging(self):
        first=self.publish(None);original=m.immutable;injected=[]
        def mutate(path,data):
            result=original(path,data)
            if path.parent.name=='receipts' and not injected:
                index=m.read(self.root/'index.json');index['external_change']='injected'
                m.atomic(self.root/'index.json',m.encode(index));injected.append((self.root/'index.json').read_bytes())
            return result
        with patch.object(m,'immutable',side_effect=mutate):
            with self.assertRaisesRegex(ValueError,'index changed'):self.publish(first['sha256'],True)
        self.assertEqual((self.root/'index.json').read_bytes(),injected[0])
    def test_crash_before_index_and_restart(self):
        first=self.publish(None);before=(self.root/'index.json').read_bytes();original=m.atomic
        def crash(path,data):
            if path.name=='index.json':raise RuntimeError('synthetic crash')
            return original(path,data)
        with patch.object(m,'atomic',side_effect=crash):
            with self.assertRaises(RuntimeError):self.publish(first['sha256'],True)
        self.assertEqual((self.root/'index.json').read_bytes(),before)
        self.assertFalse((self.root/'WRITER.lock').exists())
        result=self.publish(first['sha256'],True);self.assertEqual(result['supersedes'],first['sha256'])
        # A retry after success re-resolves the current head; stale expectations never waive CAS.
        self.assertEqual(self.publish(result['sha256'],True)['outcome'],'unchanged')
