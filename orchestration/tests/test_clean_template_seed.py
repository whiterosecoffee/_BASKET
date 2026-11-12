"""Bridge the owned clean-seed suite into the existing hosted discovery root."""
import importlib.util
from pathlib import Path


def load_tests(loader, tests, pattern):
    source = Path(__file__).resolve().parents[1] / "clean_templates" / "tests" / "test_seed.py"
    spec = importlib.util.spec_from_file_location("basket_clean_seed_tests", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return loader.loadTestsFromModule(module)
