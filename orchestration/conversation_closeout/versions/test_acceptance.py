"""Frozen-output regression checks, NOT a semantic evaluator or LLM runner.

Run: python -m unittest discover -s orchestration/conversation_closeout/versions -p 'test_*.py' -v
Annotations were reviewed manually; exact anchors deliberately reject paraphrases.
"""
import hashlib
import json
from pathlib import Path
import re
import unittest

HERE = Path(__file__).parent


def audit(output, required, forbidden=()):
    """Test-only oracle for these frozen examples; no external authenticity claim."""
    blocks = re.findall(r'^```(?:text)?\n(.*?)^```\s*$', output, re.M | re.S)
    if len(blocks) != 1:
        return ['one complete block required']
    block = blocks[0]
    failures = []
    if not re.search(r'^(?:Receiver:|To:?) B00\b', block, re.M):
        failures.append('B00 recipient')
    for item in required:
        if item not in block:
            failures.append('missing: ' + item)
    for item in forbidden:
        if item in block:
            failures.append('forbidden: ' + item)
    return failures


class AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((HERE / 'acceptance_cases.json').read_text())['cases']

    def test_preserved_v2_blob(self):
        raw = (HERE / 'HANDOFF_PROMPT.v2-source.md').read_bytes()
        self.assertEqual(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(),
                         'f3e6c4b8a656b27feeed4ea32b86792faa1a7be2')

    def test_frozen_v3_outputs(self):
        self.assertEqual({c['kind'] for c in self.cases}, {'routine', 'research', 'implementation'})
        for case in self.cases:
            with self.subTest(case=case['id']):
                self.assertFalse(audit(case['v3_output'], case['required'], case['forbidden']))

    def test_version_specific_baseline(self):
        for case in self.cases:
            with self.subTest(case=case['id']):
                if case['kind'] == 'routine':
                    self.assertNotIn('```', case['v2_output'])
                    self.assertTrue(case['v2_output'].rstrip().endswith('Ready to Archive'))
                    self.assertTrue(audit(case['v2_output'], case['required']))
                else:
                    self.assertFalse(audit(case['v2_output'], case['shared_required']))

    def test_each_material_omission_detected_inside_copy(self):
        for case in self.cases:
            for anchor in case['required']:
                with self.subTest(case=case['id'], anchor=anchor):
                    mutated = case['v3_output'].replace(anchor, '[omitted]')
                    # Moving knowledge outside the block must not rescue it.
                    self.assertTrue(audit(anchor + '\n' + mutated, case['required']))

    def test_wrong_recipient_and_duplicate_handoff_rejected(self):
        for case in self.cases:
            self.assertTrue(audit(case['v3_output'].replace('B00', 'B02', 1), case['required']))
            self.assertTrue(audit(case['v3_output'] + '\n' + case['v3_output'], case['required']))

    def test_false_authority_evidence_and_duplicate_work_rejected(self):
        for case in self.cases:
            for forbidden in case['forbidden']:
                with self.subTest(case=case['id'], forbidden=forbidden):
                    mutated = case['v3_output'].replace('\n```', '\n' + forbidden + '\n```', 1)
                    self.assertTrue(audit(mutated, case['required'], case['forbidden']))

    def test_candidate_compatibility_and_actionability_clauses(self):
        # Source-contract smoke check only; paired examples carry behavioral review.
        text = (HERE / 'HANDOFF_PROMPT.v3-candidate.md').read_text()
        for phrase in ['COMPATIBILITY AND RETRIEVAL', 'does not read transcripts',
                       'prerequisite-ordered', 'exact known', 'no material delta']:
            self.assertIn(phrase, text)


if __name__ == '__main__':
    unittest.main()
