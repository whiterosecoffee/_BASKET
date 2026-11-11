"""Negative checks for the discovery adapter; temporary synthetic suites only."""
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

BRIDGE = Path(__file__).resolve().parents[1] / 'tests/test_loop_design_bridge.py'
spec = importlib.util.spec_from_file_location('loop_bridge_for_negatives', BRIDGE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class DiscoveryTests(unittest.TestCase):
    def fixture(self, directory, change='', extra=''):
        text = 'import unittest\nclass DesignTests(unittest.TestCase):\n'
        for name in sorted(bridge.REQUIRED):
            text += f'    def {name}(self):\n        pass\n'
        if change:
            text = text.replace('    def test_recovery(self):\n        pass', change)
        (directory / 'test_design.py').write_text(text)
        if extra:
            (directory / 'test_extra.py').write_text(extra)

    def test_empty_or_missing_required_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, 'Missing required'):
                bridge.build_suite(unittest.TestLoader(), root)
            self.fixture(root)
            p = root / 'test_design.py'
            p.write_text(p.read_text().replace('def test_recovery', 'def removed_recovery'))
            with self.assertRaisesRegex(RuntimeError, 'test_recovery'):
                bridge.build_suite(unittest.TestLoader(), root)

    def test_static_skip_and_expected_failure_rejected(self):
        for decorator in ["@unittest.skip('synthetic')", '@unittest.expectedFailure']:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root, f'    {decorator}\n    def test_recovery(self):\n        pass')
                with self.assertRaises(RuntimeError):
                    bridge.build_suite(unittest.TestLoader(), root)

    def test_class_expected_failure_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            p = root / 'test_design.py'
            p.write_text(p.read_text().replace('class DesignTests', '@unittest.expectedFailure\nclass DesignTests'))
            with self.assertRaisesRegex(RuntimeError, 'Expected-failure'):
                bridge.build_suite(unittest.TestLoader(), root)

    def test_runtime_skip_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, "    def test_recovery(self):\n        self.skipTest('synthetic')")
            suite = bridge.build_suite(unittest.TestLoader(), root)
            with self.assertRaisesRegex(RuntimeError, 'Skipped loop'):
                suite.run(unittest.TestResult())

    def test_failure_and_import_error_propagate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, '    def test_recovery(self):\n        self.fail("intentional regression")')
            result = unittest.TextTestRunner(stream=io.StringIO()).run(bridge.build_suite(unittest.TestLoader(), root))
            self.assertEqual(len(result.failures), 1)
            self.assertFalse(result.wasSuccessful())
            (root / 'test_design.py').write_text('raise ImportError("synthetic missing dependency")')
            with self.assertRaises(ImportError):
                bridge.build_suite(unittest.TestLoader(), root)

    def test_additional_tests_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, extra='import unittest\nclass Extra(unittest.TestCase):\n    def test_new(self): pass\n')
            suite = bridge.build_suite(unittest.TestLoader(), root)
            self.assertEqual(suite.countTestCases(), 11)
            self.assertTrue(unittest.TextTestRunner(stream=io.StringIO()).run(suite).wasSuccessful())
