"""Emit reproducible JSON observations and honest unittest counts to stdout."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import unittest
import test_ports as q


def main():
    before = q.source_hashes()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(q.PortQualification)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        'scope': 'synthetic portable exchange qualification; no domain execution',
        'base_commit': q.PINS['base_commit'],
        'python': platform.python_version(),
        'jsonschema': importlib.metadata.version('jsonschema'),
        'tests_run': result.testsRun,
        'passes': result.testsRun - sum(map(len, [result.failures, result.errors, result.skipped,
                                                result.expectedFailures, result.unexpectedSuccesses])),
        'failures': len(result.failures), 'errors': len(result.errors),
        'skips': len(result.skipped),
        'expected_failures': [t.id() for t, _ in result.expectedFailures],
        'unexpected_successes': [t.id() for t in result.unexpectedSuccesses],
        'source_hashes_before': before, 'source_hashes_after': q.source_hashes(),
        'corpus_sha256': hashlib.sha256((q.HERE / 'corpus.json').read_bytes()).hexdigest(),
        'cases': [dict(id=c['id'], expectation=c['expected'], actual=q.observe(c['exchange']))
                  for c in q.CORPUS['cases']],
        'acceptance': 'bounded_supported_exchange_cases_only',
        'unsupported': ['Dependency version ranges are not resolved/enforced by check_exchange.'],
        'hosted_focused_coverage': False,
        'independent_acceptance': 'pending owner #105',
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
