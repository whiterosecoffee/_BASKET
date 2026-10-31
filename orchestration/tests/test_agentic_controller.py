"""Discover B00 controller tests through the existing independent B01 workflow.

No live requests, source fetching, workflow changes or controller copies.
An empty, failed-import or skipped source suite cannot masquerade as verification.
"""
import importlib.util
from pathlib import Path
import unittest


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def load_tests(loader, tests, pattern):
    directory = Path(__file__).resolve().parents[1] / "agentic/tests"
    suite = unittest.TestSuite()
    for path in sorted(directory.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location("agentic_" + path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(loader.loadTestsFromModule(module))
    if not suite.countTestCases():
        raise RuntimeError("No agentic controller tests discovered")
    for case in cases(suite):
        method = getattr(case, case._testMethodName)
        if getattr(type(case), "__unittest_skip__", False) or getattr(method, "__unittest_skip__", False):
            raise RuntimeError("Skipped controller test cannot satisfy independent verification")
    return suite
