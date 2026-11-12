import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from validate import HERE, SCHEMA, VALIDATOR, canonical, read_json, validate


class ReceiptQualification(unittest.TestCase):
    def setUp(self):
        self.specimen = read_json(HERE / 'specimen.json')

    def test_schema_and_corpus(self):
        VALIDATOR.check_schema(SCHEMA)
        corpus = read_json(HERE / 'cases.json')
        self.assertIs(corpus['synthetic'], True)
        self.assertEqual(len(corpus['cases']), 46)
        for case in corpus['cases']:
            with self.subTest(case=case['name']):
                result = validate(case['receipts'])
                self.assertIs(result['valid'], case['expected_valid'], result)
                self.assertFalse(result['claims_verified'])
                self.assertEqual(result['validation_scope'], 'structural_only')

    def test_every_required_field_rejects_when_missing(self):
        for field in SCHEMA['required']:
            with self.subTest(field=field):
                receipt = copy.deepcopy(self.specimen)
                del receipt[field]
                self.assertFalse(validate(receipt)['valid'])

    def test_repeat_and_no_input_mutation(self):
        for case in read_json(HERE / 'cases.json')['cases']:
            with self.subTest(case=case['name']):
                before = canonical(case['receipts'])
                first = validate(case['receipts'])
                self.assertEqual(first, validate(case['receipts']))
                self.assertEqual(before, canonical(case['receipts']))

    def test_duplicate_key_and_non_json_number_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.json'
            for value in ['{"run_id":"a","run_id":"b"}', '{"x":NaN}', '{"x":Infinity}']:
                path.write_text(value)
                with self.assertRaises(ValueError):
                    read_json(path)
                result = self.cli(path)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(json.loads(result.stdout)['valid'])

    def cli(self, path, script=HERE / 'validate.py'):
        return subprocess.run([sys.executable, '-B', str(script), str(path)], text=True,
                              capture_output=True, check=False, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})

    def test_cli_repeat_same_bytes_and_input_hash(self):
        path = HERE / 'specimen.json'
        before = path.read_bytes()
        first, second = self.cli(path), self.cli(path)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, '')
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(json.loads(first.stdout)['input_sha256'], hashlib.sha256(before).hexdigest())

    def test_cli_negative_and_missing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rejected.json'
            receipt = copy.deepcopy(self.specimen)
            receipt['outcome_state'] = 'accepted'
            path.write_text(json.dumps(receipt))
            result = self.cli(path)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)['valid'])
            result = self.cli(Path(directory) / 'missing.json')
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)['valid'])

    def test_standalone_copy_no_repo_or_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ['validate.py', 'receipt.schema.json', 'specimen.json']:
                shutil.copyfile(HERE / name, target / name)
            result = self.cli(target / 'specimen.json', target / 'validate.py')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(json.loads(result.stdout)['claims_verified'])

    def test_network_is_unnecessary(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')):
            self.assertTrue(validate(self.specimen)['valid'])

    def test_key_order_is_not_conflict(self):
        reordered = dict(reversed(list(self.specimen.items())))
        result = validate([self.specimen, reordered])
        self.assertTrue(result['valid'])
        self.assertEqual(result['receipt_count'], 2)
        self.assertEqual(result['unique_run_count'], 1)

    def test_structural_success_does_not_authenticate_claim(self):
        case = next(c for c in read_json(HERE / 'cases.json')['cases'] if c['name'] == 'CI-verified')
        self.assertIn('example.invalid', case['receipts']['evidence'][0]['artifact'])
        result = validate(case['receipts'])
        self.assertTrue(result['valid'])
        self.assertFalse(result['claims_verified'])


if __name__ == '__main__':
    unittest.main()
