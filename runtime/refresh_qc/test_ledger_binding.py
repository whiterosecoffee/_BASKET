import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from ledger_binding import bind_evidence, BindingError

class LedgerBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.values = {
            'plan': {'plan': {'TEST': {'symbol':'TEST', 'ranges': [{'from':'2026-10-08','to':'2026-10-08'}], 'needed':['2026-10-08'], 'kind_by_session':{'2026-10-08':'missing'}}}},
            'done': {'rows':1,'statuses':[200],'ok':True},
            'request_ledger': [{'ticker':'TEST','symbol':'TEST','from':'2026-10-08','to':'2026-10-08','rows':1,'pages':1,'status':200,'at':'2026-10-09T00:00:00Z'}],
            'apply_ledger': [{'ticker':'TEST','round':'raw_r3','staged_rows':1,'applied':True,'status':'applied','sha256_after':hashlib.sha256(b'legacy output').hexdigest()}],
            'capture': [{'ticker':'TEST','t':1791468000000,'class':'bar','grain':'1min','vol':1.25}],
        }
        self.manifest={'ticker':'TEST','round':'raw_r3','artifacts':{}}
        for name in self.values:
            self.replace(name, self.values[name])
        for name in ('fetch_plan.py','fetch_run.py','verify_apply.py','ticker_jsonl_tool.py'):
            self.bytes(name,b'# synthetic script')
        self.bytes('output',b'legacy output')

    def bytes(self,name,data):
        p=self.root/name
        p.write_bytes(data)
        self.manifest['artifacts'][name]={'path':str(p),'sha256':hashlib.sha256(data).hexdigest()}

    def replace(self,name,value):
        data=('\n'.join(json.dumps(r) for r in value) if isinstance(value,list) else json.dumps(value)).encode()
        self.bytes(name,data)

    def assertBlocked(self, reason):
        with self.assertRaisesRegex(BindingError,reason):
            bind_evidence(self.manifest)

    def test_correlates_without_authority_and_replays(self):
        before={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.root.iterdir()}
        receipt=bind_evidence(self.manifest)
        self.assertEqual(receipt,bind_evidence(self.manifest))
        self.assertFalse(receipt['canonical_eligible'])
        self.assertFalse(receipt['historical_capture_hash_bound'])
        self.assertEqual(receipt['fractional_volume_rows'],1)
        self.assertNotIn(str(self.root),json.dumps(receipt))
        self.assertEqual(before,{p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.root.iterdir()})

    def test_stale_capture_pin(self):
        (self.root/'capture').write_bytes(b'changed')
        self.assertBlocked('artifact_hash_mismatch:capture')

    def test_stale_output_pin(self):
        (self.root/'output').write_bytes(b'changed')
        self.assertBlocked('artifact_hash_mismatch:output')

    def test_repin_cannot_bypass_apply_output(self):
        self.bytes('output',b'changed')
        self.assertBlocked('apply_output_binding_mismatch')

    def test_ambiguous_request(self):
        self.replace('request_ledger',self.values['request_ledger']*2)
        self.assertBlocked('missing_or_ambiguous')

    def test_count_mismatch(self):
        v=copy.deepcopy(self.values['done']);v['rows']=2
        self.replace('done',v)
        self.assertBlocked('row_count_mismatch')

    def test_duplicate_timestamp(self):
        self.replace('capture',self.values['capture']*2)
        self.assertBlocked('duplicate_capture_timestamp')

    def test_wrong_ticker(self):
        v=copy.deepcopy(self.values['capture']);v[0]['ticker']='OTHER'
        self.replace('capture',v)
        self.assertBlocked('capture_identity_or_grain')

    def test_nonfinite_rejected(self):
        self.bytes('capture',b'{"vol":NaN}')
        self.assertBlocked('invalid_json')

    def test_duplicate_key_rejected(self):
        self.bytes('done',b'{"rows":1,"rows":2}')
        self.assertBlocked('invalid_json')

    def test_missing_artifact(self):
        del self.manifest['artifacts']['fetch_run.py']
        self.assertBlocked('artifact_set_mismatch')

    def test_out_of_plan(self):
        v=copy.deepcopy(self.values['capture']);v[0]['t']+=86400000
        self.replace('capture',v)
        self.assertBlocked('capture_outside_plan')

    def test_boolean_count(self):
        v=copy.deepcopy(self.values['done']);v['rows']=True
        self.replace('done',v)
        self.assertBlocked('row_count_mismatch')

    def test_failed_marker(self):
        v=copy.deepcopy(self.values['done']);v['ok']=False
        self.replace('done',v)
        self.assertBlocked('unsuccessful_fetch_evidence')

    def test_scalar_ledger_rejected(self):
        self.bytes('request_ledger',b'null')
        self.assertBlocked('non_object_json_record')

    def test_nonobject_manifest_sanitized(self):
        with self.assertRaisesRegex(BindingError,'invalid_or_unreadable_artifact'):
            bind_evidence([])

    def test_unsafe_timestamp_rejected(self):
        v=copy.deepcopy(self.values['request_ledger']);v[0]['at']={'private':'secret'}
        self.replace('request_ledger',v)
        self.assertBlocked('invalid_request_timestamp')

    def test_unbounded_volume_rejected(self):
        data=json.dumps(self.values['capture'][0]).replace('1.25','1e999999999')
        self.bytes('capture',data.encode())
        self.assertBlocked('unsupported_volume_precision')

    def test_float_status_rejected(self):
        v=copy.deepcopy(self.values['request_ledger']);v[0]['status']=200.0
        self.replace('request_ledger',v)
        self.assertBlocked('unsuccessful_fetch_evidence')

    def test_invalid_date_rejected(self):
        v=copy.deepcopy(self.values['plan']);v['plan']['TEST']['ranges'][0]['from']='not-a-date'
        self.replace('plan',v)
        self.assertBlocked('invalid_or_unreadable_artifact')

    def test_wrong_provider_symbol(self):
        v=copy.deepcopy(self.values['request_ledger']);v[0]['symbol']='OTHER'
        self.replace('request_ledger',v)
        self.assertBlocked('provider_symbol_mismatch')

if __name__=='__main__':
    unittest.main()
