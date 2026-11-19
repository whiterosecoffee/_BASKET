"""Discover scoped B00 loop tests in the existing shared CI, fail closed."""
import importlib.util
from pathlib import Path
import unittest

REQUIRED = {
    'test_source_pins', 'test_roles_and_ports', 'test_boundary', 'test_claim_schema',
    'test_score_arithmetic', 'test_every_gate_fails_closed', 'test_selection',
    'test_recovery', 'test_review', 'test_checkpoint_schema',
}


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


class NoSkippedSuite(unittest.TestSuite):
    def run(self, result, debug=False):
        before = len(result.skipped)
        expected_before = len(result.expectedFailures)
        super().run(result, debug)
        if len(result.skipped) > before:
            raise RuntimeError('Skipped loop tests cannot satisfy acceptance')
        if len(result.expectedFailures) > expected_before:
            raise RuntimeError('Expected-failure loop tests cannot satisfy acceptance')
        return result


def build_suite(loader, directory):
    suite = NoSkippedSuite()
    found = set()
    for path in sorted(directory.glob('test_*.py')):
        spec = importlib.util.spec_from_file_location('loop_design_' + path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded = loader.loadTestsFromModule(module)
        for case in cases(loaded):
            method = getattr(case, case._testMethodName)
            if getattr(type(case), '__unittest_skip__', False) or getattr(method, '__unittest_skip__', False):
                raise RuntimeError('Skipped loop test cannot satisfy acceptance')
            if getattr(case, '__unittest_expecting_failure__', False) or getattr(method, '__unittest_expecting_failure__', False):
                raise RuntimeError('Expected-failure loop test cannot satisfy acceptance')
            if path.name == 'test_design.py' and type(case).__name__ == 'DesignTests':
                found.add(case._testMethodName)
        suite.addTests(loaded)
    if not REQUIRED <= found:
        raise RuntimeError('Missing required loop tests: ' + ', '.join(sorted(REQUIRED - found)))
    return suite


def load_tests(loader, tests, pattern):
    return build_suite(loader, Path(__file__).resolve().parents[1] / 'loop_design')
