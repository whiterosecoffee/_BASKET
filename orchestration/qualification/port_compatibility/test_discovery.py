"""Adversarial probes for the shared-discovery bridge; no domain replicas."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('port_bridge', ROOT / 'orchestration/tests/test_port_compatibility_qualification.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def fake():
    cls = type('PortQualification', (unittest.TestCase,), {n: lambda self: None for n in b.REQUIRED})
    cls.__module__ = 'port_qualification_test_ports'
    return list(b.cases(unittest.defaultTestLoader.loadTestsFromTestCase(cls)))


class DiscoveryTests(unittest.TestCase):
    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as d, self.assertRaises(RuntimeError):
            b.build_suite(unittest.TestLoader(), Path(d))

    def test_empty_source(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'test_ports.py').write_text('import unittest\n')
            with self.assertRaises(RuntimeError):
                b.build_suite(unittest.TestLoader(), Path(d))

    def test_missing_identity(self):
        with self.assertRaises(RuntimeError):
            b.checked_suite(unittest.TestSuite(fake()[1:]))

    def test_duplicate_identity(self):
        a = fake()
        with self.assertRaises(RuntimeError):
            b.checked_suite(unittest.TestSuite(a + [a[0]]))

    def test_skip_marker(self):
        a = fake()
        type(a[0]).__unittest_skip__ = True
        with self.assertRaises(RuntimeError):
            b.checked_suite(unittest.TestSuite(a))

    def test_expected_failure_marker(self):
        a = fake()
        getattr(type(a[0]), a[0]._testMethodName).__unittest_expecting_failure__ = True
        with self.assertRaises(RuntimeError):
            b.checked_suite(unittest.TestSuite(a))

    def test_runtime_skip(self):
        class Skip(unittest.TestCase):
            def runTest(self): self.skipTest('probe')
        with self.assertRaises(RuntimeError):
            b.StrictSuite([Skip()]).run(unittest.TestResult())

    def test_runtime_expected_failure(self):
        class Expected(unittest.TestCase):
            def run(self, result):
                result.startTest(self)
                try: raise AssertionError('probe')
                except AssertionError: result.addExpectedFailure(self, sys.exc_info())
                result.stopTest(self)
        with self.assertRaises(RuntimeError):
            b.StrictSuite([Expected()]).run(unittest.TestResult())

    def test_actual_discovery_once_and_import_path_preserved(self):
        before = sys.path[:]
        suite = b.load_tests(unittest.TestLoader(), None, None)
        ids = [c.id() for c in b.cases(suite)]
        self.assertEqual(26, len(ids))
        self.assertEqual(26, len(set(ids)))
        self.assertEqual(before, sys.path)
