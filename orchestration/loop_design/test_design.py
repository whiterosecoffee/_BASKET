"""Offline design conformance model, not a production controller or effect executor."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = json.loads((HERE / 'contract.json').read_text())


def select(options, gates):
    """Return an eligible proposal only. This model never dispatches or writes."""
    for gate in CONTRACT['selection']['hard_gates']:
        if gates.get(gate) is not True:
            return {'state': 'blocked', 'reason': gate, 'chosen': None}
    rejected, eligible = [], []
    for option in options:
        failed = [g for g in CONTRACT['selection']['candidate_gates'] if option.get(g) is not True]
        if failed:
            rejected.append({'task_id': option.get('task_id'), 'reasons': failed})
        else:
            eligible.append(option)
    if not eligible:
        return {'state': 'no_op', 'chosen': None, 'rejected': rejected,
                'evidence': [], 'next_action': 'Resolve blocked candidate gates or await a new eligible delta.'}
    keys = ('benefit', 'risk', 'effort')
    if any(any(type(o.get(k)) not in (int, float) or not 0 <= o[k] <= 5 for k in keys) for o in eligible):
        return {'state': 'blocked', 'reason': 'unknown_or_invalid_ranking', 'chosen': None}
    ids = [o.get('task_id') for o in eligible]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        return {'state': 'blocked', 'reason': 'invalid_identity', 'chosen': None}
    if any(not isinstance(o.get('evidence'), list) or not o['evidence']
           or any(not isinstance(e, str) or not e for e in o['evidence']) for o in eligible):
        return {'state': 'blocked', 'reason': 'missing_evidence', 'chosen': None}
    ranked = sorted(eligible, key=lambda o: (-o['benefit'], o['risk'], o['effort'], o['task_id']))
    return {'state': 'proposal', 'chosen': ranked[0]['task_id'],
            'rejected': rejected + [{'task_id': o['task_id'], 'reasons': ['lower_rank_or_stable_tie']} for o in ranked[1:]],
            'evidence': ranked[0]['evidence'], 'next_action': 'Revalidate selected scope and authority before a bounded action.'}


def recover(readback, attempt, authorized, fence_current):
    if type(attempt) is not int or attempt < 0 or type(authorized) is not bool or type(fence_current) is not bool:
        return 'blocked_invalid_input'
    if not fence_current:
        return 'blocked_stale_fence'
    if readback == 'matching':
        return 'confirmed_no_repeat'
    if readback == 'absent' and authorized and attempt < CONTRACT['cadence']['budget']['max_same_failure_retries']:
        return 'retry_proposal'
    return 'blocked'


def review(producer, reviewer, candidate, tested, reviewed, required_suites, receipts):
    if not (producer and reviewer and producer != reviewer and candidate
            and candidate == tested == reviewed and required_suites):
        return False
    if len(set(required_suites)) != len(required_suites):
        return False
    for suite in required_suites:
        matches = [r for r in receipts if r.get('suite') == suite]
        if len(matches) != 1:
            return False
        receipt = matches[0]
        if not (receipt.get('revision') == candidate and receipt.get('status') == 'pass'
                and type(receipt.get('count')) is int and receipt['count'] > 0):
            return False
    return True


class DesignTests(unittest.TestCase):
    def test_source_pins(self):
        for source in CONTRACT['sources']:
            # Default hosted checkout is shallow. Unchanged working-tree bytes
            # may prove the pinned content hash without pretending history exists.
            probe = subprocess.run(['git', 'cat-file', '-e', source['commit'] + '^{commit}'], cwd=ROOT, capture_output=True)
            if probe.returncode == 0:
                content = subprocess.check_output(['git', 'show', source['commit'] + ':' + source['path']], cwd=ROOT)
            else:
                content = (ROOT / source['path']).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), source['sha256'])

    def test_roles_and_ports(self):
        self.assertEqual({r['id'] for r in CONTRACT['roles']}, {'audit', 'advance', 'review', 'outer'})
        outputs = {p for r in CONTRACT['roles'] for p in r['outputs']}
        for role in CONTRACT['roles']:
            for port in role['inputs']:
                self.assertIn(port, set(CONTRACT['ports']) | outputs)
            self.assertTrue(role['outputs'] and role['trigger'])

    def test_boundary(self):
        self.assertTrue(CONTRACT['authority']['spec_is_not_scheduler'])
        self.assertIsNone(CONTRACT['authority']['configured_schedule'])
        self.assertEqual(CONTRACT['scope'], ['orchestration/loop_design/**', 'orchestration/tests/test_loop_design_bridge.py'])
        self.assertFalse(CONTRACT['review']['acceptance_is_merge_authorization'])

    def test_claim_schema(self):
        jsonschema.validate(json.loads((HERE / 'claim.json').read_text()), json.loads((ROOT / 'schemas/worker-task.v1.json').read_text()))

    def test_score_arithmetic(self):
        score = json.loads((HERE / 'scorecard.json').read_text())
        self.assertEqual(len(score['dimensions']), 10)
        for label in ['before', 'after']:
            self.assertEqual(sum(d[label] for d in score['dimensions']), score[label + '_total'])
        self.assertIsNone(score['operational_health'])
        self.assertIsNone(score['real_cycle_efficiency_gain'])

    def test_every_gate_fails_closed(self):
        gates = dict.fromkeys(CONTRACT['selection']['hard_gates'], True)
        for gate in gates:
            for bad in [False, None, 'true', 1]:
                changed = dict(gates, **{gate: bad})
                self.assertEqual(select([{'task_id': 'B00-1', 'benefit': 5, 'risk': 0, 'effort': 0}], changed)['state'], 'blocked')

    def test_selection(self):
        gates = dict.fromkeys(CONTRACT['selection']['hard_gates'], True)
        a = dict(task_id='B00-2', benefit=3, risk=1, effort=2, evidence=['synthetic'], **dict.fromkeys(CONTRACT['selection']['candidate_gates'], True))
        b = dict(a, task_id='B00-1')
        self.assertEqual(select([a, b], gates)['chosen'], 'B00-1')
        self.assertEqual(select([b, a], gates)['chosen'], 'B00-1')
        self.assertEqual(select([], gates)['state'], 'no_op')
        for value in [None, True, -1, 6, float('nan'), float('inf')]:
            self.assertEqual(select([dict(a, benefit=value)], gates)['state'], 'blocked')
        self.assertEqual(select([a, a], gates)['state'], 'blocked')
        for gate in CONTRACT['selection']['candidate_gates']:
            result = select([dict(a, benefit=5, **{gate: False}), b], gates)
            self.assertEqual(result['chosen'], 'B00-1')
            self.assertIn(gate, result['rejected'][0]['reasons'])
        self.assertEqual(select([dict(a, evidence=[])], gates)['reason'], 'missing_evidence')

    def test_recovery(self):
        self.assertEqual(recover('matching', 1, False, True), 'confirmed_no_repeat')
        self.assertEqual(recover('absent', 0, True, True), 'retry_proposal')
        for value in ['unavailable', 'conflicting', 'unknown']:
            self.assertEqual(recover(value, 0, True, True), 'blocked')
        self.assertEqual(recover('absent', 1, True, True), 'blocked')
        self.assertEqual(recover('absent', 0, False, True), 'blocked')
        self.assertEqual(recover('matching', 0, True, False), 'blocked_stale_fence')
        for args in [('absent', -1, True, True), ('absent', 0, 'false', True), ('matching', 0, True, 'true'), ('absent', True, True, True)]:
            self.assertEqual(recover(*args), 'blocked_invalid_input')

    def test_review(self):
        receipt = {'suite': 'domain', 'revision': 'head', 'status': 'pass', 'count': 1}
        def check(**changes):
            args = dict(producer='owner', reviewer='reviewer', candidate='head', tested='head',
                        reviewed='head', required_suites=['domain'], receipts=[receipt])
            args.update(changes)
            return review(**args)
        self.assertTrue(check())
        for statuses in ['fail', 'skipped', 'not_run']:
            self.assertFalse(check(receipts=[dict(receipt, status=statuses)]))
        for count in [0, -1, None, True]:
            self.assertFalse(check(receipts=[dict(receipt, count=count)]))
        for change in [dict(reviewer='owner'), dict(tested='old'), dict(reviewed='old'),
                       dict(required_suites=[]), dict(required_suites=['domain', 'missing']),
                       dict(receipts=[]), dict(receipts=[receipt, receipt]),
                       dict(receipts=[dict(receipt, revision='old')])]:
            self.assertFalse(check(**change))

    def test_checkpoint_schema(self):
        schema = json.loads((HERE / 'checkpoint.schema.json').read_text())
        checkpoint = {key: 'example' for key in ['task_id', 'run_id', 'input_digest', 'source_revision', 'owner', 'action_key', 'expected_target_revision', 'next_action']}
        checkpoint.update(scope=['orchestration/loop_design/**'], fence=1, attempt=0, stage='effect_uncertain', receipt=None)
        jsonschema.validate(checkpoint, schema)
        for key in schema['required']:
            invalid = dict(checkpoint)
            del invalid[key]
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(invalid, schema)
        for patch in [{'fence': -1}, {'attempt': -1}, {'stage': 'done'}, {'scope': []}, {'secret': 'forbidden'}, {'stage': 'accepted'}, {'stage': 'effect_confirmed'}, {'stage': 'reviewed'}]:
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(dict(checkpoint, **patch), schema)


if __name__ == '__main__':
    unittest.main()
