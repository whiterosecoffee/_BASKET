"""Qualification only: call the pinned production helper, never replace it."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from orchestration import component_conformance as cc
from jsonschema import ValidationError

HERE = Path(__file__).resolve().parent
CORPUS = json.loads((HERE / 'corpus.json').read_text())
PINS = json.loads((HERE / 'source-pins.json').read_text())


def source_hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
            for p in PINS['sha256']}


def invoke(exchange):
    cc.check_exchange(exchange['manifest'], exchange['call'], exchange['result'],
                      {k: v.encode('utf-8') for k, v in exchange['artifacts_utf8'].items()},
                      expected_input_sha256=exchange['expected_input_sha256'],
                      dependency_inventory=exchange.get('dependency_inventory'))


def observe(exchange):
    try:
        invoke(exchange)
    except (cc.ConformanceError, ValidationError) as exc:
        return {'outcome': 'reject', 'error_type': type(exc).__name__,
                'message': str(exc).splitlines()[0]}
    return {'outcome': 'accept', 'error_type': None, 'message': None}


class PortQualification(unittest.TestCase):
    def test_pinned_implementation_and_contract_bytes(self):
        self.assertEqual(source_hashes(), PINS['sha256'])
        self.assertEqual(Path(cc.__file__).resolve(), ROOT / 'orchestration/component_conformance.py')

    def test_repeat_is_deterministic_without_mutation(self):
        before = copy.deepcopy(CORPUS)
        hashes = source_hashes()
        first = [observe(c['exchange']) for c in CORPUS['cases']]
        second = [observe(c['exchange']) for c in CORPUS['cases']]
        self.assertEqual(first, second)
        self.assertEqual(CORPUS, before)
        self.assertEqual(source_hashes(), hashes)
        self.assertEqual(hashes, PINS['sha256'])

    def test_corpus_identifiers_and_declared_coverage(self):
        ids = [c['id'] for c in CORPUS['cases']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 22)
        self.assertEqual(sum(c['expected'] == 'unsupported_rejection' for c in CORPUS['cases']), 0)
        self.assertTrue(all(c['contract_mapping'] for c in CORPUS['cases']))

    def test_valid_exchange_has_independent_input_fingerprint(self):
        exchange = CORPUS['cases'][0]['exchange']
        encoded = json.dumps(exchange['call']['inputs'], sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode()
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), exchange['expected_input_sha256'])


def case_test(case):
    def check(self):
        exchange = copy.deepcopy(case['exchange'])
        if case['expected'] == 'accept':
            self.assertIsNone(invoke(exchange))
        else:
            error = {'ConformanceError': cc.ConformanceError,
                     'ValidationError': ValidationError}[case['error_type']]
            with self.assertRaises(error) as caught:
                invoke(exchange)
            if case['error_contains']:
                self.assertIn(case['error_contains'], str(caught.exception))
    if case['expected'] == 'unsupported_rejection':
        check = unittest.expectedFailure(check)
    return check


for case in CORPUS['cases']:
    setattr(PortQualification, 'test_' + case['id'], case_test(case))

if __name__ == '__main__':
    unittest.main()
