import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import jsonschema
import flow
import consumer


def sample():
    t = int(datetime(2026, 11, 10, 15, 0, tzinfo=timezone.utc).timestamp() * 1000)
    return {'format':'basket.data_capture@1','provider':'massive','source_mode':'synthetic',
            'endpoint':'/v2/aggs/ticker/NVDA/range/1/minute/2026-11-10/2026-11-10',
            'params':{'adjusted':True,'sort':'asc','limit':50000},'ticker':'NVDA',
            'session':'2026-11-10','captured_at':'2026-11-11T00:00:00Z',
            'rows':[{'t':t,'o':2.0,'h':3.0,'l':1.0,'c':2.5,'v':12.345678,'vw':2.2,'n':4}]}


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root/'input.json'
        self.capture = sample()

    def write(self):
        self.source.write_bytes(flow.encoded(self.capture))
        return flow.write_capture(self.source,self.root/'store')[0]

    def request(self):
        return dict(ticker='NVDA', session='2026-11-10',as_of='2026-11-11T00:00:00Z',expected_source_sha256=flow.digest(self.source.read_bytes()), allow_synthetic=True)

    def test_template_definitions_and_bindings(self):
        obj=json.loads(flow.CONTRACT.read_text())
        self.assertEqual(set(obj['flow']),set(obj['definitions']))
        for instance in obj['instances']:
            self.assertIn(instance['definition'],obj['definitions'])
            self.assertIn(instance['parent'],obj['compositions'])
        self.assertIsNone(obj['bindings']['durable_local_authoritative_root'])

    def test_capture_schema(self):
        schema=json.loads((flow.HERE/'capture.schema.json').read_text())
        jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(self.capture)
        self.capture['unexpected']=True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.capture,schema)

    def test_end_to_end_and_fractional_volume(self):
        path=self.write()
        rows,receipt=flow.read_verified(path,**self.request())
        self.assertEqual(rows[0]['v'],12.345678)
        self.assertEqual(receipt['rows'],1)
        self.assertEqual(consumer.summary(path,**self.request())['fractional_volume_rows'],1)

    def test_separate_process_consumer(self):
        path=self.write()
        r=subprocess.run([sys.executable,str(flow.HERE/'consumer.py'),str(path),'--ticker','NVDA','--session','2026-11-10','--as-of','2026-11-11T00:00:00Z','--expected-source-sha256',flow.digest(self.source.read_bytes()),'--allow-synthetic'],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(r.stdout)['rows'],1)

    def test_repeat_unchanged(self):
        path=self.write()
        before={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in path.iterdir()}
        _,state=flow.write_capture(self.source,self.root/'store')
        self.assertEqual(state,'unchanged')
        self.assertEqual(before,{p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in path.iterdir()})

    def test_exact_duplicates_collapse_and_order(self):
        second=copy.deepcopy(self.capture['rows'][0]);second['t']+=60000
        self.capture['rows']=[second,self.capture['rows'][0],second]
        path=self.write();rows,m=flow.read_verified(path,**self.request())
        self.assertEqual(len(rows),2);self.assertLess(rows[0]['t'],rows[1]['t']);self.assertEqual(m['duplicates_removed'],1)

    def test_conflicting_duplicate_no_write(self):
        row=copy.deepcopy(self.capture['rows'][0]);row['v']+=1;self.capture['rows'].append(row)
        with self.assertRaises(ValueError):self.write()
        self.assertFalse((self.root/'store').exists())

    def test_numeric_representation_duplicates_reject_in_both_orders(self):
        original=self.capture['rows'][0]
        changed=copy.deepcopy(original);changed['o']=2
        for rows in ([original,changed],[changed,original]):
            with self.subTest(rows=rows):
                self.capture['rows']=rows
                with self.assertRaises(ValueError):flow.build(flow.encoded(self.capture))

    def test_changed_capture_cannot_replace(self):
        path=self.write();before=(path/'capture.json').read_bytes();self.capture['rows'][0]['v']+=1
        with self.assertRaises(ValueError):self.write()
        self.assertEqual(before,(path/'capture.json').read_bytes())

    def test_semantic_negatives(self):
        cases=[('mixed day',lambda c:c['rows'][0].update(t=c['rows'][0]['t']+86400000)),
               ('grain',lambda c:c['rows'][0].update(t=c['rows'][0]['t']+1)),
               ('basis',lambda c:c['params'].update(adjusted=False)),
               ('bool basis',lambda c:c['params'].update(adjusted=1)),
               ('ticker path',lambda c:c.update(ticker='../NVDA')),
               ('wrong endpoint',lambda c:c.update(endpoint='/v3/trades/NVDA')),
               ('negative volume',lambda c:c['rows'][0].update(v=-1)),
               ('bad OHLC',lambda c:c['rows'][0].update(l=4)),
               ('numeric string',lambda c:c['rows'][0].update(o='2')),
               ('bool numeric',lambda c:c['rows'][0].update(v=True)),
               ('fraction count',lambda c:c['rows'][0].update(n=1.5)),
               ('empty',lambda c:c.update(rows=[])),
               ('unknown field',lambda c:c['rows'][0].update(extra=1)),
               ('future bar',lambda c:c.update(captured_at='2026-11-10T15:00:30Z')),
               ('naive capture',lambda c:c.update(captured_at='2026-11-11T00:00:00'))]
        for name,change in cases:
            with self.subTest(name=name):
                c=sample();change(c)
                with self.assertRaises(ValueError):flow.build(flow.encoded(c))

    def test_nonstandard_json_rejected(self):
        for payload in (b'{"x":NaN}',b'{"x":1,"x":2}',b'{"x":Infinity}'):
            with self.assertRaises(ValueError):flow.strict_load(payload)

    def test_mutation_rejected(self):
        path=self.write()
        for name in ('capture.json','bars.jsonl','receipt.json'):
            with self.subTest(name=name):
                p=path/name;original=p.read_bytes();p.write_bytes(original+b' ')
                with self.assertRaises(ValueError):flow.verify(path)
                p.write_bytes(original)

    def test_stale_contract_rejected(self):
        path=self.write();other=self.root/'contract.json';other.write_text('{}')
        with patch.object(flow,'CONTRACT',other):
            with self.assertRaises(ValueError):flow.verify(path)

    def test_consumer_boundary_rejections(self):
        path=self.write()
        for updates in ({'ticker':'SPY'},{'session':'2026-11-09'},{'as_of':'2026-11-10T23:59:59Z'},{'expected_source_sha256':'0'*64},{'allow_synthetic':False}):
            with self.subTest(updates=updates):
                with self.assertRaises(ValueError):flow.read_verified(path,**(self.request()|updates))

    def test_incomplete_artifacts_rejected(self):
        path=self.write();(path/'receipt.json').unlink()
        with self.assertRaises(ValueError):flow.verify(path)
        with self.assertRaises(ValueError):flow.write_capture(self.source,self.root/'store')

    def test_symlink_rejected(self):
        path=self.write();link=self.root/'link';link.symlink_to(path,target_is_directory=True)
        with self.assertRaises(ValueError):flow.verify(link)
        with self.assertRaises(ValueError):flow.write_capture(self.source,link)

    def test_interrupted_write_no_published_partition(self):
        self.source.write_bytes(flow.encoded(self.capture))
        with patch.object(flow.os,'fsync',side_effect=OSError('simulated interruption')):
            with self.assertRaises(OSError):flow.write_capture(self.source,self.root/'store')
        self.assertEqual(list((self.root/'store').iterdir()),[])


if __name__=='__main__':unittest.main()
