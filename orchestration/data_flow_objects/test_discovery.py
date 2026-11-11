"""Synthetic discovery failures must fail the shared suite, never silently pass."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('data_flow_bridge_under_test',
    Path(__file__).resolve().parents[1] / 'tests/test_data_flow_objects.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class DiscoveryTests(unittest.TestCase):
    def make(self, body=None):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        root=Path(tmp.name);(root/'__init__.py').write_text('')
        if body is not None:(root/'test_fixture.py').write_text(body)
        return root

    def test_missing_suite_rejected(self):
        with self.assertRaises(FileNotFoundError):
            bridge.load_owned_suite(unittest.TestLoader(),self.make()/'missing')

    def test_empty_suite_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'at least 17'):
            bridge.load_owned_suite(unittest.TestLoader(),self.make())

    def test_short_suite_rejected(self):
        body='import unittest\nclass T(unittest.TestCase):\n def test_one(self): pass\n'
        with self.assertRaisesRegex(RuntimeError,'at least 17'):
            bridge.load_owned_suite(unittest.TestLoader(),self.make(body))

    def test_skipped_suite_rejected(self):
        body='import unittest\n@unittest.skip("missing dependency")\nclass T(unittest.TestCase):\n'+''.join(f' def test_{i}(self): pass\n' for i in range(17))
        with self.assertRaisesRegex(RuntimeError,'Skipped'):
            bridge.load_owned_suite(unittest.TestLoader(),self.make(body))

    def test_failed_import_rejected_and_namespace_cleaned(self):
        before=set(sys.modules)
        with self.assertRaisesRegex(RuntimeError,'broken source'):
            bridge.load_owned_suite(unittest.TestLoader(),self.make('raise RuntimeError("broken source")'))
        self.assertFalse(any(n.startswith('_basket_data_flow_') for n in set(sys.modules)-before))

    def test_extra_tests_cannot_replace_original_flow_tests(self):
        body='import unittest\nclass T(unittest.TestCase):\n'+''.join(f' def test_{i}(self): pass\n' for i in range(22))
        with self.assertRaisesRegex(RuntimeError,'Missing required flow tests'):
            bridge.load_owned_suite(unittest.TestLoader(),self.make(body))
