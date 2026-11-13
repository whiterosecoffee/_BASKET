"""Date-specific identity controls using fake responses only."""
import io
import json
import unittest
from unittest.mock import patch
from runtime.massive_maintainer import test_quarantine as fixtures
from runtime.massive_maintainer import maintain as m

class IdentityTests(unittest.TestCase):
    setUp=fixtures.QuarantineTests.setUp
    transport=fixtures.QuarantineTests.transport
    raw=fixtures.QuarantineTests.raw
    ref=fixtures.QuarantineTests.ref
    def fetch(self,reference):
        key=self.root/'key';key.write_text('FAKE_KEY')
        with self.transport([reference,self.raw()]) as net,patch('time.sleep'):
            result=m.fetch_day(m.Massive(self.root,key),'NVDA',self.day)
        return result,net
    def test_historical_query_and_stable_repeat(self):
        result,net=self.fetch(self.ref())
        self.assertIn('date='+self.day,net.call_args_list[0].args[0].full_url)
        self.assertEqual(result['reference']['reference_date'],self.day)
        again,net=self.fetch(self.ref());self.assertEqual(again['sha256'],result['sha256'])
    def test_changed_cik_retained_without_overwrite(self):
        result,_=self.fetch(self.ref());before=(self.root/'index.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'identity continuity'):self.fetch(self.ref(cik='other-cik'))
        self.assertEqual((self.root/'index.json').read_bytes(),before)
        self.assertTrue((self.root/result['path']).exists())
        conflict=self.ref(cik='other-cik');self.assertEqual((self.root/'raw'/(m.digest(conflict)+'.json')).read_bytes(),conflict)
        self.assertTrue(list((self.root/'quarantine').glob('response-*.json')))
    def test_missing_identity_rejects(self):
        with self.assertRaisesRegex(ValueError,'identity unavailable'):self.fetch(self.ref(cik=None))
        self.assertFalse((self.root/'index.json').exists())
    def test_existing_unknown_identity_blocks(self):
        m.promote(self.root,'NVDA',self.day,[self.row],self.ev,{},expected_head=m.partition_head(self.root,'NVDA',self.day))
        before=(self.root/'index.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'identity continuity'):self.fetch(self.ref())
        self.assertEqual((self.root/'index.json').read_bytes(),before)
