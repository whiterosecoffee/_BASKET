"""B00 adapter unit tests picked up by the existing independent B01 workflow.

No workflow changes, live model calls or external dependency fetching in CI.
"""
import importlib.util
from pathlib import Path
import unittest


def load_tests(loader, tests, pattern):
    directory = Path(__file__).resolve().parents[1] / "worker_bridge"
    suite = unittest.TestSuite()
    for path in sorted(directory.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location("worker_bridge_" + path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(loader.loadTestsFromModule(module))
    if suite.countTestCases() == 0:
        raise RuntimeError("No worker bridge tests discovered")
    return suite
