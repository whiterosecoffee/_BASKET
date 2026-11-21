"""Expose portable qualification to shared discovery without copying tests."""
import importlib.util
from pathlib import Path
import sys
import unittest

REQUIRED = frozenset(['test_component_version_mismatch', 'test_corpus_identifiers_and_declared_coverage', 'test_declared_dependency_without_resolution', 'test_dependency_compatible', 'test_dependency_exact', 'test_dependency_incompatible', 'test_dependency_malformed_constraint', 'test_dependency_malformed_inventory', 'test_dependency_unavailable', 'test_dependency_unsupported_syntax', 'test_incompatible_schema_identity_input', 'test_incompatible_schema_identity_output', 'test_incompatible_schema_version_input', 'test_incompatible_schema_version_output', 'test_missing_required_input', 'test_missing_required_output', 'test_pinned_implementation_and_contract_bytes', 'test_repeat_is_deterministic_without_mutation', 'test_stale_pinned_source_input', 'test_stale_pinned_source_output', 'test_unexpected_payload_input', 'test_unexpected_payload_output', 'test_valid_exchange', 'test_valid_exchange_has_independent_input_fingerprint', 'test_wrong_named_input', 'test_wrong_named_output'])


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


class StrictSuite(unittest.TestSuite):
    def run(self, result, debug=False):
        before = len(result.skipped), len(result.expectedFailures)
        super().run(result, debug)
        if before != (len(result.skipped), len(result.expectedFailures)):
            raise RuntimeError('Skipped or expected-failure qualification')
        return result


def checked_suite(suite):
    found = list(cases(suite))
    ids = [c.id() for c in found]
    required = {'port_qualification_test_ports.PortQualification.' + n for n in REQUIRED}
    if not found or len(ids) != len(set(ids)) or not required <= set(ids):
        raise RuntimeError('Empty, duplicate or missing required qualification identities')
    for case in found:
        method = getattr(case, case._testMethodName)
        if any(getattr(obj, flag, False) for obj in (case, type(case), method)
               for flag in ('__unittest_skip__', '__unittest_expecting_failure__')):
            raise RuntimeError('Skipped or expected-failure qualification')
    return StrictSuite(found)


def build_suite(loader, directory):
    path = directory / 'test_ports.py'
    if not path.is_file():
        raise RuntimeError('Missing portable qualification suite')
    spec = importlib.util.spec_from_file_location('port_qualification_test_ports', path)
    module = importlib.util.module_from_spec(spec)
    original = sys.path[:]
    try:
        spec.loader.exec_module(module)
        loaded = loader.loadTestsFromModule(module)
    finally:
        sys.path[:] = original
    return checked_suite(loaded)


def load_tests(loader, tests, pattern):
    return build_suite(loader, Path(__file__).resolve().parents[1] / 'qualification/port_compatibility')
