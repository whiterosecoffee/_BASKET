import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from qualify import load_manifest, run


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root/'source'
        (self.source/'fixture').mkdir(parents=True)
        self.manifest = self.root/'manifest.json'
        self.counter = 0

    def prepare(self, body='', minimum=1):
        (self.source/'fixture/__init__.py').write_text('')
        (self.source/'fixture/test_sample.py').write_text(
            'import unittest\nclass Sample(unittest.TestCase):\n    def test_sample(self):\n' +
            (body or '        self.assertEqual(2+2,4)\n'))
        files = {}
        for path in self.source.rglob('*'):
            if path.is_file():
                data = path.read_bytes()
                files[path.relative_to(self.source).as_posix()] = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        value = dict(schema='basket.component_export_review@0.1-draft',source_revision='a'*40,
                     component='fixture',files=files,modules=['fixture.test_sample'],minimum=minimum)
        self.manifest.write_text(json.dumps(value))
        return value

    def execute(self, **kwargs):
        self.counter += 1
        return run(self.source,self.manifest,self.root/('evidence-'+str(self.counter)),**kwargs)

    def test_real_execution_and_distinct_claim_dimensions(self):
        self.prepare()
        packet = self.execute()
        self.assertTrue(packet['passed'])
        self.assertEqual(packet['tests']['run'],1)
        self.assertTrue(packet['inputs_unchanged'])
        self.assertFalse(packet['semantic_acceptance'])
        self.assertFalse(packet['integrated'])
        self.assertFalse(packet['operational'])

    def test_changed_missing_extra_and_symlink_inputs_fail(self):
        for case in ('changed','missing','extra','symlink'):
            with self.subTest(case=case):
                self.prepare()
                path = self.source/'fixture/test_sample.py'
                if case == 'changed': path.write_text('raise RuntimeError("never execute")')
                elif case == 'missing': path.unlink()
                elif case == 'extra': (self.source/'extra.py').write_text('')
                else:
                    path.unlink();path.symlink_to(self.manifest)
                packet = self.execute()
                self.assertFalse(packet['passed'])
                self.assertNotIn('tests',packet)
                if path.is_symlink(): path.unlink()
                extra = self.source/'extra.py'
                if extra.exists(): extra.unlink()

    def test_skip_failure_and_reduced_discovery_fail(self):
        for body, minimum in [('        self.skipTest("not evidence")\n',1),
                              ('        self.fail("real failure")\n',1),('',2)]:
            with self.subTest(body=body,minimum=minimum):
                self.prepare(body,minimum)
                packet = self.execute()
                self.assertFalse(packet['passed'])
                self.assertFalse(packet['tests']['passed'])

    def test_source_mutation_fails_after_successful_suite(self):
        self.prepare('        from pathlib import Path\n        Path(__file__).write_text("mutated")\n')
        packet = self.execute()
        self.assertFalse(packet['passed'])
        self.assertTrue(packet['tests']['passed'])
        self.assertIn('mismatch',packet['error'])

    def test_timeout_is_a_failure_with_evidence(self):
        self.prepare('        import time\n        time.sleep(2)\n')
        packet = self.execute(timeout=0.05)
        self.assertFalse(packet['passed'])
        self.assertIn('timed out',packet['error'])

    def test_manifest_rejects_invalid_pins_modules_and_paths(self):
        for field, value in [('source_revision','main'),('minimum',True),
                             ('modules',[{}]),('modules',['untracked.test']),
                             ('component','../fixture')]:
            with self.subTest(field=field):
                manifest = self.prepare();manifest[field]=value
                self.manifest.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):load_manifest(self.manifest)

    def test_existing_evidence_and_inside_source_output_rejected(self):
        self.prepare()
        self.execute()
        with self.assertRaises(FileExistsError):
            run(self.source,self.manifest,self.root/'evidence-1')
        with self.assertRaises(ValueError):
            run(self.source,self.manifest,self.source/'evidence')


if __name__ == '__main__':
    unittest.main()
