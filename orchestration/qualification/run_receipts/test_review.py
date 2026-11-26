"""Qualify PR256 review findings without authenticating synthetic assertions."""
import copy
import unittest
from validate import HERE, read_json, validate


class ReviewQualification(unittest.TestCase):
    def setUp(self):
        self.receipt = read_json(HERE / 'specimen.json')
        self.approval = copy.deepcopy(self.receipt)
        self.approval['outcome_state'] = 'awaiting_approval'
        self.approval['blocker'] = {
            'reason': 'Synthetic artifact publication awaits permission',
            'action': 'Publish synthetic artifact to synthetic destination',
            'approval_authority': 'synthetic-project-owner',
            'unblock_condition': 'Explicit approval for the named action and destination is recorded',
        }

    def test_approval_requires_resume_details(self):
        self.assertTrue(validate(self.approval)['valid'])
        null_blocker = copy.deepcopy(self.approval)
        null_blocker['blocker'] = None
        self.assertFalse(validate(null_blocker)['valid'])
        for field in ['reason', 'action', 'approval_authority', 'unblock_condition']:
            for replacement in [None, '', ' ']:
                with self.subTest(field=field, replacement=replacement):
                    receipt = copy.deepcopy(self.approval)
                    if replacement is None:
                        del receipt['blocker'][field]
                    else:
                        receipt['blocker'][field] = replacement
                    self.assertFalse(validate(receipt)['valid'])

    def test_approval_record_does_not_grant_authorization(self):
        result = validate(self.approval)
        self.assertTrue(result['valid'])
        self.assertFalse(result['claims_verified'])
        self.assertEqual(self.approval['outcome_state'], 'awaiting_approval')

    def test_non_git_monitoring_requires_checked_identity(self):
        receipt = copy.deepcopy(self.receipt)
        receipt['subject_revision'] = None
        receipt['sources'][0].update(revision=None, watermark='synthetic-loop:cursor-4')
        before = copy.deepcopy(receipt)
        result = validate(receipt)
        self.assertTrue(result['valid'], result)
        self.assertEqual(validate(receipt), result)
        self.assertEqual(receipt, before)
        self.assertFalse(result['claims_verified'])
        receipt['sources'][0]['watermark'] = None
        self.assertFalse(validate(receipt)['valid'])

    def test_null_subject_is_not_a_general_evidence_escape(self):
        receipt = copy.deepcopy(self.receipt)
        receipt['subject_revision'] = None
        for state in ['ready', 'working', 'awaiting_evidence', 'awaiting_approval', 'blocked', 'tested', 'accepted']:
            with self.subTest(state=state):
                receipt['outcome_state'] = state
                self.assertFalse(validate(receipt)['valid'])
        corpus = read_json(HERE / 'cases.json')['cases']
        for name in ['tested-local', 'accepted', 'published', 'CI-verified']:
            with self.subTest(case=name):
                receipt = copy.deepcopy(next(c['receipts'] for c in corpus if c['name'] == name))
                receipt.update(subject_revision=None, outcome_state='monitoring_only')
                self.assertFalse(validate(receipt)['valid'])
                for item in receipt['evidence']:
                    item['revision'] = None
                self.assertFalse(validate(receipt)['valid'])

    def test_cross_loop_source_identities_need_not_match_subject(self):
        receipt = copy.deepcopy(self.receipt)
        receipt['sources'].extend([
            {'source_id':'synthetic-loop-b', 'checked_at':receipt['checked_at'], 'revision':'b'*40, 'watermark':None},
            {'source_id':'synthetic-non-git-loop', 'checked_at':receipt['checked_at'], 'revision':None, 'watermark':'synthetic-cursor-8'},
        ])
        self.assertTrue(validate(receipt)['valid'])

    def test_multiple_subjects_use_separate_receipts_not_mixed_evidence(self):
        corpus = read_json(HERE / 'cases.json')['cases']
        first = copy.deepcopy(next(c['receipts'] for c in corpus if c['name']=='tested-local'))
        second = copy.deepcopy(first)
        second.update(run_id='synthetic-other-loop-001',subject_revision='b'*40)
        second['sources'][0]['revision']='b'*40
        second['evidence'][0]['revision']='b'*40
        self.assertTrue(validate([first,second])['valid'])
        mixed = copy.deepcopy(first)
        foreign = copy.deepcopy(second['evidence'][0])
        foreign['id']='foreign-test'
        mixed['evidence'].append(foreign)
        self.assertFalse(validate(mixed)['valid'])
