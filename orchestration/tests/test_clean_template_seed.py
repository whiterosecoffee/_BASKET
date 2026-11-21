"""Bridge owned clean-template tests into existing hosted discovery."""
import importlib.util
from pathlib import Path
import unittest


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    root = Path(__file__).resolve().parents[1] / "clean_templates" / "tests"
    for source in sorted(root.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location("basket_clean_" + source.stem, source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(loader.loadTestsFromModule(module))
    return suite
