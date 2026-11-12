"""Synthetic contract qualification of exact PR242 reference, not integration.

Supply a separately materialized reference directory. No provider data is read.
All captures/partitions are generated under TemporaryDirectory and then removed.
"""
import argparse
import hashlib
import types
import os
import py_compile
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from volume_guard import verify_volume_preservation, VolumeError

REFERENCE_REVISION = 'd103a99486589aa4aee24d4fa978532f1b288ac1'
PINS = {
    'flow.py': 'f43d7b6357a5548c8c47195ca6ec5ea9e823b9add25792d9998847857b475821',
    'objects.json': '6a1a347e962ba44d4e76656cb33795288ed1deaa862d10de79b2c512f4b57afd',
    'capture.schema.json': 'bc8f7ac55276c5dbd0985d43a8bdab6d9f15822ab15601a2e378c901eb45b93f',
}

def load_reference(root):
    root = Path(root)
    verified = {}
    for name, digest in PINS.items():
        data = (root / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('reference_pin_mismatch')
        verified[name] = data
    module = types.ModuleType('qualified_reference_242')
    module.__file__ = str((root / 'flow.py').resolve())
    # Execute the exact hashed bytes, never re-open source or use cached .pyc.
    exec(compile(verified['flow.py'], module.__file__, 'exec'), module.__dict__)

    return module


def suite_for(flow):
    class ReferenceQualification(unittest.TestCase):
        def setUp(self):
            self.temp = tempfile.TemporaryDirectory(prefix='basket207-synthetic-')
            self.addCleanup(self.temp.cleanup)
            self.root = Path(self.temp.name)
            self.capture_path = self.root / 'synthetic-capture.json'
            self.capture = {
                'format':'basket.data_capture@1', 'source_mode':'synthetic',
                'provider':'massive', 'endpoint':'/v2/aggs/ticker/TEST/range/1/minute/2026-10-08/2026-10-08',
                'params':{'adjusted':True,'sort':'asc','limit':50000},
                'ticker':'TEST','session':'2026-10-08','captured_at':'2026-10-09T00:00:00Z',
                'rows':[{'t':1791468000000,'o':2,'h':3,'l':1,'c':2,'v':1.25,'vw':2,'n':2}],
            }

        def write(self):
            self.capture_path.write_bytes(flow.encoded(self.capture))
            return flow.write_capture(self.capture_path, self.root/'artifacts')

        def read(self,directory,source_hash=None):
            return flow.read_verified(directory,ticker='TEST',session='2026-10-08',as_of='2026-10-09T00:00:00Z',expected_source_sha256=source_hash or flow.digest(self.capture_path.read_bytes()),allow_synthetic=True)

        def snapshot(self,directory):
            return {p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in directory.iterdir()}

        def test_loader_ignores_timestamp_valid_cached_bytecode(self):
            bundle=self.root/'cached-bundle';bundle.mkdir()
            original=Path(flow.__file__)
            for name in PINS:
                (bundle/name).write_bytes((original.parent/name).read_bytes())
            target=bundle/'flow.py';trusted=target.read_bytes()
            poison=b"raise RuntimeError('cached bytecode executed')\n"
            poison+=b'#'*(len(trusted)-len(poison))
            target.write_bytes(poison)
            timestamp=target.stat().st_mtime_ns
            py_compile.compile(str(target),doraise=True)
            target.write_bytes(trusted)
            os.utime(target,ns=(timestamp,timestamp))
            loaded=load_reference(bundle)
            self.assertTrue(callable(loaded.build))

        def test_create_read_and_identical_replay(self):
            directory,status=self.write();self.assertEqual(status,'created')
            before=self.snapshot(directory)
            rows,receipt=self.read(directory)
            self.assertEqual(rows[0]['v'],1.25)
            self.assertEqual(flow.write_capture(self.capture_path,self.root/'artifacts')[1],'unchanged')
            self.assertEqual(before,self.snapshot(directory))
            self.assertEqual(receipt['source_mode'],'synthetic')

        def test_changed_capture_rejects_without_generation(self):
            directory,_=self.write();before=self.snapshot(directory)
            self.capture['rows'][0]['v']=1.5
            with self.assertRaisesRegex(ValueError,'existing partition differs'):
                self.write()
            self.assertEqual(before,self.snapshot(directory))

        def test_wrong_source_pin_rejected(self):
            directory,_=self.write()
            with self.assertRaisesRegex(ValueError,'consumer source pin mismatch'):
                self.read(directory,'0'*64)

        def test_changed_reader_cannot_read_old_receipt(self):
            directory,_=self.write();before=self.snapshot(directory)
            old=flow.TRANSFORM
            replacement=self.root/'changed-reader.py'
            replacement.write_bytes(old.read_bytes()+b'\n# synthetic revision\n')
            self.addCleanup(setattr,flow,'TRANSFORM',old)
            flow.TRANSFORM=replacement
            with self.assertRaisesRegex(ValueError,'changed source, partition, contract, schema, transform or receipt'):
                self.read(directory)
            self.assertEqual(before,self.snapshot(directory))

        def test_guard_exposes_reference_precision_loss(self):
            exact='1.250000000000000000000000000001'
            capture=flow.encoded(self.capture).replace(b'"v":1.25',b'"v":'+exact.encode())
            self.assertIn(exact.encode(),capture)
            artifacts=flow.build(capture)
            row=json.loads(artifacts['bars.jsonl'])
            identity={'ticker':'TEST','t':1791468000000,'class':'bar','grain':'1min'}
            candidate=dict(identity,vol=row['v'])
            source=(json.dumps(identity)[:-1]+',"vol":'+exact+'}\n').encode()
            with self.assertRaisesRegex(VolumeError,'volume_changed'):
                verify_volume_preservation(source,json.dumps(candidate).encode(),source_unit='shares',candidate_unit='shares')
            self.assertEqual(row['v'],1.25)

        def test_asof_and_synthetic_admission_remain_closed(self):
            directory,_=self.write()
            kwargs=dict(ticker='TEST',session='2026-10-08',expected_source_sha256=flow.digest(self.capture_path.read_bytes()))
            with self.assertRaisesRegex(ValueError,'synthetic forbidden'):
                flow.read_verified(directory,as_of='2026-10-09T00:00:00Z',**kwargs)
            with self.assertRaisesRegex(ValueError,'not available as of'):
                flow.read_verified(directory,as_of='2026-10-08T23:59:59Z',allow_synthetic=True,**kwargs)

    return unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceQualification)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-directory',required=True)
    args=parser.parse_args()
    try:
        flow=load_reference(args.reference_directory)
    except (OSError, ValueError):
        print(json.dumps({'status':'blocked','reason':'reference_missing_or_pin_mismatch'}))
        return 2
    suite=suite_for(flow)
    names=[test.id().split('.')[-1] for test in suite]
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    # Deliberately omit traceback/local paths from the portable evidence receipt.
    try:
        pins_unchanged=all(hashlib.sha256((Path(args.reference_directory)/name).read_bytes()).hexdigest()==digest for name,digest in PINS.items())
    except OSError:
        pins_unchanged=False
    if not pins_unchanged:
        print(json.dumps({'status':'blocked','reason':'reference_changed_during_qualification'}))
        return 2
    receipt={'reference_revision':REFERENCE_REVISION,'reference_sha256':PINS,'synthetic_only':True,'tests_run':result.testsRun,'tests':names,'failures':len(result.failures),'errors':len(result.errors),'status':'passed' if result.wasSuccessful() else 'failed','canonical_eligible':False,'conclusions':['Single capture read/replay qualified synthetically','Changed captures rejected; append-only generations not implemented','Changed reader rejects historical receipt; revision dispatch not implemented','High-precision volume loss detected by receiving guard','No source-data or production-FETCH execution']}
    if not result.wasSuccessful():
        receipt['conclusions']=['Qualification failed; no acceptance conclusions']
    print(json.dumps(receipt,sort_keys=True,indent=2))
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':
    raise SystemExit(main())
