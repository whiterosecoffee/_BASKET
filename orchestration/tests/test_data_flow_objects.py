"""Discover the owned data-flow suite through the existing shared CI command.

No workflow edits, network calls, raw provider data or global import aliases.
"""
import importlib.util
from pathlib import Path
import sys
import unittest
import uuid


REQUIRED_FLOW_TESTS = (
    'test_template_definitions_and_bindings',
    'test_capture_schema',
    'test_end_to_end_and_fractional_volume',
    'test_separate_process_consumer',
    'test_repeat_unchanged',
    'test_exact_duplicates_collapse_and_order',
    'test_conflicting_duplicate_no_write',
    'test_numeric_representation_duplicates_reject_in_both_orders',
    'test_changed_capture_cannot_replace',
    'test_semantic_negatives',
    'test_nonstandard_json_rejected',
    'test_mutation_rejected',
    'test_stale_contract_rejected',
    'test_schema_and_transform_identity_changes_rejected',
    'test_consumer_boundary_rejections',
    'test_incomplete_artifacts_rejected',
    'test_symlink_rejected',
    'test_interrupted_write_no_published_partition',
)

def cases(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from cases(case)
        else:
            yield case


def load_owned_suite(loader, directory):
    directory = Path(directory)
    namespace = '_basket_data_flow_' + uuid.uuid4().hex
    try:
        spec = importlib.util.spec_from_file_location(namespace, directory / '__init__.py',
                                                      submodule_search_locations=[str(directory)])
        package = importlib.util.module_from_spec(spec)
        sys.modules[namespace] = package
        spec.loader.exec_module(package)
        suite = unittest.TestSuite()
        for path in sorted(directory.glob('test_*.py')):
            name = namespace + '.' + path.stem
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            suite.addTests(loader.loadTestsFromModule(module))
        if suite.countTestCases() < 17:
            raise RuntimeError('Expected at least 17 data-flow tests')
        for case in cases(suite):
            method = getattr(case, case._testMethodName)
            if getattr(type(case), '__unittest_skip__', False) or getattr(method, '__unittest_skip__', False):
                raise RuntimeError('Skipped data-flow test cannot satisfy verification')
        actual = {case._testMethodName for case in cases(suite)
                  if type(case).__module__ == namespace + '.test_flow'
                  and type(case).__name__ == 'FlowTests'}
        missing = set(REQUIRED_FLOW_TESTS) - actual
        if missing:
            raise RuntimeError('Missing required flow tests: ' + ', '.join(sorted(missing)))
        return suite
    finally:
        # Test methods retain their loaded module references; no aliases leak to other suites.
        for name in list(sys.modules):
            if name == namespace or name.startswith(namespace + '.'):
                del sys.modules[name]


def load_tests(loader, tests, pattern):
    return load_owned_suite(loader, Path(__file__).resolve().parents[1] / 'data_flow_objects')
