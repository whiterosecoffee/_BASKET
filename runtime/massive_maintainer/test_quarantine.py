"""Rejected responses keep raw evidence and never replace accepted snapshots."""
import io
import json
import unittest
from unittest.mock import patch
from runtime.massive_maintainer import test_maintain as fixtures
from runtime.massive_maintainer import maintain as m

class QuarantineTests(unittest.TestCase):
    setUp=fixtures.MaintenanceTests.setUp
    def publish(self):
        identity={'cik':'synthetic-cik','composite_figi':None,'share_class_figi':None,'primary_exchange':None,'type':None}
        return m.promote(self.root,'NVDA',self.day,[self.row],self.ev,{'instrument_identity':identity},expected_head=m.partition_head(self.root,'NVDA',self.day))
    def transport(self,items):
        queue=iter(items)
        def send(*args,**kw):
            item=next(queue)
            if isinstance(item,Exception):raise item
            return io.BytesIO(item)
        return patch('urllib.request.urlopen',side_effect=send)
    def raw(self,rows=None,**overrides):
        body={'status':'OK','ticker':'NVDA','adjusted':True,'results':rows if rows is not None else [self.row]}
        body.update(overrides);return m.encode(body)
    def ref(self,**changes):
        ref={'ticker':'NVDA','market':'stocks','locale':'us','currency_name':'usd','cik':'synthetic-cik'};ref.update(changes)
        return m.encode({'results':ref})
    def rejected(self,responses):
        key=self.root/'key';key.write_text('FAKE_SECRET')
        with self.transport(responses),patch('time.sleep'):
            with self.assertRaises((ValueError,RuntimeError,TypeError,KeyError,AttributeError)):
                m.fetch_day(m.Massive(self.root,key),'NVDA',self.day)
        receipts=[json.loads(p.read_bytes()) for p in (self.root/'quarantine').glob('response-*.json')]
        self.assertTrue(receipts)
        last_raw=next(x for x in reversed(responses) if isinstance(x,bytes))
        self.assertIn(m.digest(last_raw),[r['sha256'] for x in receipts for r in x['raw']])
        for receipt in receipts:
            for raw in receipt['raw']:
                self.assertEqual(m.digest((self.root/raw['path']).read_bytes()),raw['sha256'])
        return receipts
    def test_invalid_ohlc_retains_index_and_original_generation(self):
        old=self.publish();before=(self.root/'index.json').read_bytes();bad=self.raw([dict(self.row,h=0)])
        receipts=self.rejected([self.ref(),bad])
        self.assertEqual((self.root/'index.json').read_bytes(),before)
        self.assertTrue((self.root/old['path']).exists())
        self.assertEqual((self.root/'raw'/(m.digest(bad)+'.json')).read_bytes(),bad)
        self.assertIn(m.digest(bad),[r['sha256'] for x in receipts for r in x['raw']])
    def test_parse_failure_bound_to_raw(self):
        bad=b'{broken'
        self.rejected([self.ref(),bad]);self.assertFalse((self.root/'index.json').exists())
    def test_reference_and_aggregate_identity_schema_failures(self):
        for responses in ([self.ref(ticker='AAOI')],[b'[]'],[self.ref(),self.raw(ticker='AAOI')],[self.ref(),b'[]'],[self.ref(),self.raw(results='invalid')]):
            with self.subTest(responses=responses):self.rejected(responses)
        self.assertFalse((self.root/'index.json').exists())
    def test_second_page_failure_preserves_first_page_evidence(self):
        old=self.publish();before=(self.root/'index.json').read_bytes()
        page=self.raw(next_url='https://api.massive.com/next')
        receipts=self.rejected([self.ref(),page,RuntimeError('synthetic failure')])
        self.assertIn(m.digest(page),[r['sha256'] for x in receipts for r in x['raw']])
        self.assertEqual((self.root/'index.json').read_bytes(),before)
        self.assertTrue((self.root/old['path']).exists())
    def test_repeat_has_identical_disposition_and_keeps_raw(self):
        bad=self.raw([dict(self.row,h=0)]);inputs=[self.ref(),bad]
        self.rejected(inputs)
        before={p.name:p.read_bytes() for p in (self.root/'quarantine').glob('response-*.json')}
        self.rejected(inputs)
        after={p.name:p.read_bytes() for p in (self.root/'quarantine').glob('response-*.json')}
        self.assertEqual(before,after)
    def test_second_page_parse_failure_binds_both_pages(self):
        page=self.raw(next_url='https://api.massive.com/next');bad=b'not JSON'
        receipts=self.rejected([self.ref(),page,bad])
        hashes={r['sha256'] for x in receipts for r in x['raw']}
        self.assertTrue({m.digest(page),m.digest(bad)}<=hashes)

    def test_missing_row_field_and_invalid_pagination_shape(self):
        row=dict(self.row);del row['h']
        for body in (self.raw([row]),self.raw(next_url=0)):
            with self.subTest(body=body):self.rejected([self.ref(),body])
        self.assertFalse((self.root/'index.json').exists())
