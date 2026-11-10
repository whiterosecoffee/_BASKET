"""Negative checks for #64; isolated from B13 source/provider access."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('b01_openai_gate', Path(__file__).with_name('openai_gate.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class OpenAIGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fixture(self, body):
        (self.root / 'test_probe.py').write_text(body)
        return gate.bounded_suite(self.root, 'test_probe.py')

    def test_empty_source_suite_rejected(self):
        self.assertNotEqual(self.fixture('# no cases'), 0)

    def test_skipped_source_suite_rejected(self):
        self.assertNotEqual(self.fixture('import unittest\nclass T(unittest.TestCase):\n @unittest.skip("missing")\n def test_x(self): pass\n'), 0)

    def test_expected_failure_rejected(self):
        self.assertNotEqual(self.fixture('import unittest\nclass T(unittest.TestCase):\n @unittest.expectedFailure\n def test_x(self): self.fail()\n'), 0)

    def test_passing_and_failing_suites(self):
        self.assertEqual(self.fixture('import unittest\nclass T(unittest.TestCase):\n def test_x(self): pass\n'), 0)
        self.assertNotEqual(self.fixture('import unittest\nclass T(unittest.TestCase):\n def test_x(self): self.fail("probe")\n'), 0)

    def test_timeout_does_not_retry(self):
        with patch.object(gate.subprocess, 'run', side_effect=subprocess.TimeoutExpired('probe', 120)) as mocked:
            self.assertEqual(gate.bounded_suite(self.root, 'test_probe.py'), 1)
        self.assertEqual(mocked.call_count, 1)

    def test_hash_order_stability_and_revision_invalidation(self):
        self.assertEqual(gate.digest({'a': 1, 'b': 2}), gate.digest({'b': 2, 'a': 1}))
        self.assertNotEqual(gate.digest({'revision': 1}), gate.digest({'revision': 2}))

    def test_mutation_addition_and_removal_rejected(self):
        p = self.root / 'input.json'
        p.write_text('{}')
        before = gate.files(self.root)
        gate.verify(before, gate.files(self.root))
        p.write_text('{"revised":true}')
        with self.assertRaises(ValueError): gate.verify(before, gate.files(self.root))
        p.write_text('{}')
        other = self.root / 'extra.json'
        other.write_text('{}')
        with self.assertRaises(ValueError): gate.verify(before, gate.files(self.root))
        p.unlink()
        with self.assertRaises(ValueError): gate.verify(before, gate.files(self.root))

    def test_symlinks_and_empty_inputs_rejected(self):
        with self.assertRaises(ValueError): gate.files(self.root)
        (self.root / 'link').symlink_to(self.root)
        with self.assertRaises(ValueError): gate.files(self.root)

    def test_stale_revision_rejected_before_tests(self):
        with patch.object(gate.subprocess, 'check_output', return_value='a' * 40):
            with self.assertRaisesRegex(ValueError, 'stale'):
                gate.snapshot(self.root, self.root, 'b' * 40, 'b' * 40)

    def test_failure_evidence_is_written(self):
        report = self.root / 'report.json'
        with patch.object(gate.subprocess, 'check_output', return_value='a' * 40):
            status = gate.main(['snapshot', '--source', str(self.root), '--acceptance', str(self.root), '--source-sha', 'b' * 40, '--acceptance-sha', 'b' * 40, '--output', str(report)])
        self.assertEqual(status, 1)
        self.assertIn('stale source revision', report.read_text())
