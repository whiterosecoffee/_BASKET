"""Bounded synthetic qualification; no production validator or schema registry."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

from jsonschema import Draft7Validator, Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry
from referencing.exceptions import Unresolvable

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from orchestration import component_conformance as existing

HERE = Path(__file__).resolve().parent
CORPUS = json.loads((HERE / 'corpus.json').read_text())


class Interoperability(unittest.TestCase):
    def test_pinned_existing_sources(self):
        for path, digest in CORPUS['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)

    def test_canonical_dialects(self):
        paths = sorted((ROOT / 'schemas').glob('*.json'))
        self.assertEqual(len(paths), 15)
        for path in paths:
            schema = json.loads(path.read_text())
            self.assertEqual(schema['$schema'], CORPUS['dialects']['2020-12'])
            Draft202012Validator.check_schema(schema)


def case_test(case):
    def test(self):
        schema, value = copy.deepcopy(case['schema']), copy.deepcopy(case['instance'])
        before = copy.deepcopy((schema, value))
        # Network attempts fail the test, even if reference failure was expected.
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')) as net:
            outcome = 'valid'
            try:
                if case['mode'] == 'existing_profile':
                    Draft202012Validator.check_schema(schema)
                    existing._local_schema(schema)
                    existing._validate(value, schema)
                else:
                    cls = {'draft7': Draft7Validator, 'draft2020': Draft202012Validator}[case['mode']]
                    cls.check_schema(schema)
                    cls(schema, registry=Registry()).validate(value)
            except existing.ConformanceError:
                outcome = 'profile_rejected'
            except SchemaError:
                outcome = 'schema_rejected'
            except ValidationError:
                outcome = 'instance_rejected'
            except Unresolvable:
                outcome = 'unresolved_reference'
            self.assertEqual(outcome, case['expected'], case['id'])
            net.assert_not_called()
        self.assertEqual((schema, value), before, 'Schema/instance must not be coerced or mutated')
    return test


for case in CORPUS['cases']:
    setattr(Interoperability, 'test_' + case['id'], case_test(case))

if __name__ == '__main__':
    unittest.main(verbosity=2)
