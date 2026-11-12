"""Regression cases supplied by independent review of the first increment."""
import json
from pathlib import Path
import tempfile
import unittest
from .core import digest, evaluate, persist, subject_digest, validate


class ReviewRegressionTests(unittest.TestCase):
    def setUp(self):
        self.s = json.loads(Path(__file__).with_name('objectives-status.example.json').read_text())
        self.o = dict(self.s['claim'], online=True, verified_at=100,
                      single_writer=True, wake_id='review-wake', active=False,
                      approval_pending=False, handoff_requested=False, checkpoint_due=False)

    def test_callback_omits_wake_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'status.json'
            path.write_text(json.dumps(self.s))
            def update(s):
                s['revision'] += 1
                return s
            saved = persist(path, digest(self.s), update, {}, self.o, now=100)
            self.assertEqual(evaluate(saved, self.o, {}, now=100)['action'], 'no-change')
            before = path.read_bytes()
            self.assertEqual(persist(path, digest(saved), lambda s: self.fail('duplicate callback'), {}, self.o, now=100), saved)
            self.assertEqual(path.read_bytes(), before)

    def test_unreceipted_dimension_promotion(self):
        for key, status in [('execution', 'operational'), ('acceptance', 'accepted')]:
            with self.subTest(dimension=key):
                self.s['dimensions'][key] = status
                with self.assertRaises(ValueError):
                    validate(self.s, {})

    def test_changed_condition_reuses_old_receipt(self):
        row = self.s['objectives'][0]
        self.s['objectives'] = [row]
        row.update(status='accepted', evidence=['r'], artifact_revisions=['v1'])
        gate = row['acceptance'][0]
        gate['evidence'] = ['r']
        receipt = dict(kind='acceptance', source='independent-review', revision='v1',
                       objective=row['id'], criterion=gate['id'],
                       criterion_digest=digest({'id':gate['id'], 'condition':gate['condition']}))
        validate(self.s, {'r':receipt})
        gate['condition'] = 'Different, stronger acceptance requirement'
        with self.assertRaises(ValueError):
            validate(self.s, {'r':receipt})

    def test_typed_promotion_without_receipt_cannot_persist(self):
        for name, status in [('execution', 'operational'), ('acceptance', 'accepted')]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/'status.json'
                path.write_text(json.dumps(self.s))
                original = path.read_bytes()
                def update(s):
                    s['revision'] += 1
                    s['dimensions'][name] = {'status':status, 'evidence':[]}
                    return s
                with self.assertRaisesRegex(ValueError, 'dimension receipt required'):
                    persist(path, digest(self.s), update, {}, self.o, now=100)
                self.assertEqual(path.read_bytes(), original)

    def test_dimension_receipt_is_bound_and_cannot_cross_dimensions(self):
        self.s['objectives'][0]['artifact_revisions'] = ['v1']
        self.s['dimensions']['execution'] = {'status':'executed','evidence':['run']}
        receipt = dict(kind='dimension', dimension='execution', status='executed',
                       source='independent-runner',revision='v1',subject_digest=subject_digest(self.s))
        validate(self.s, {'run':receipt})
        for change in ({'kind':'session-start'}, {'dimension':'publication'}, {'revision':'old'}, {'status':'operational'}, {'subject_digest':'wrong'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate(self.s, {'run':dict(receipt, **change)})
        self.s['objectives'][0]['next_action'] = 'Changed task'
        with self.assertRaises(ValueError): validate(self.s, {'run':receipt})

    def test_overall_acceptance_requires_objective_gates(self):
        self.s['objectives'][0]['artifact_revisions'] = ['v1']
        self.s['dimensions']['acceptance'] = {'status':'accepted','evidence':['a']}
        r = dict(kind='dimension',dimension='acceptance',status='accepted',source='review',revision='v1',subject_digest=subject_digest(self.s))
        with self.assertRaisesRegex(ValueError, 'all objectives'):
            validate(self.s, {'a':r})

    def test_callback_cannot_rewrite_criterion_or_invent_wakes(self):
        for attack in ('criterion', 'wake'):
            with self.subTest(attack=attack), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/'status.json'
                path.write_text(json.dumps(self.s))
                original = path.read_bytes()
                def update(s):
                    s['revision'] += 1
                    if attack == 'criterion':
                        s['objectives'][0]['acceptance'][0]['condition'] = 'Easier condition'
                    else:
                        s['processed_wakes'].append('unobserved-wake')
                    return s
                with self.assertRaises(ValueError): persist(path,digest(self.s),update,{},self.o,now=100)
                self.assertEqual(path.read_bytes(), original)

    def test_old_schema_is_rejected(self):
        self.s['schema'] = 'basket.handoff_objectives@0.1-draft'
        with self.assertRaisesRegex(ValueError, 'unknown schema'): validate(self.s, {})
