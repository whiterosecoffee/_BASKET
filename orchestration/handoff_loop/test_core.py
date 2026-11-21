import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from .core import criterion_digest, digest, evaluate, persist, validate


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.s = json.loads(Path(__file__).with_name('objectives-status.example.json').read_text())
        self.o = dict(self.s['claim'], online=True, verified_at=100, single_writer=True, wake_id='wake-1', active=False, approval_pending=False, handoff_requested=False, checkpoint_due=False)

    def run_decision(self, **values):
        self.o.update(values)
        return evaluate(self.s, self.o, {}, now=100)['action']

    def test_continue_has_no_execution_claim(self):
        result = evaluate(self.s, self.o, {}, now=100)
        self.assertEqual(result['action'], 'continue')
        self.assertEqual(result['execution'], 'not_attempted')
        self.assertEqual(result['acceptance'], 'not_established')

    def test_coalesce(self):
        self.assertEqual(self.run_decision(active=True), 'coalesce')

    def test_duplicate_wake(self):
        self.s['processed_wakes'] = ['wake-1']
        self.assertEqual(self.run_decision(), 'no-change')

    def test_pending_approval(self):
        self.assertEqual(self.run_decision(approval_pending=True), 'blocked')

    def test_unchanged_blocker(self):
        self.s['blocker_fingerprint'] = 'same'
        self.assertEqual(self.run_decision(blocker_fingerprint='same'), 'no-change')
        self.assertEqual(self.run_decision(blocker_fingerprint='new'), 'blocked')

    def test_unknown_stale_wrong_host_and_offline(self):
        for delta in ({'verified_at': -300}, {'verified_at': 101}, {'host': 'other'}, {'owner': None}, {'single_writer': False}, {'online': False}):
            with self.subTest(delta=delta):
                o = dict(self.o, **delta)
                self.assertEqual(evaluate(self.s, o, {}, now=100)['action'], 'blocked')

    def test_checkpoint(self):
        self.assertEqual(self.run_decision(checkpoint_due=True), 'request checkpoint')

    def test_transfer_requires_all_ack_fields(self):
        self.o['handoff_requested'] = True
        ack = dict(owner='replacement',branch=self.s['claim']['branch'],scope=self.s['claim']['scope'],data_access=True,outstanding_task=self.s['next_action'])
        for missing in ack:
            partial = dict(ack)
            del partial[missing]
            self.assertEqual(self.run_decision(transfer=dict(old_writer_retired=True,replacement_ack=partial)), 'request checkpoint')
        self.assertEqual(self.run_decision(transfer=dict(old_writer_retired=False,replacement_ack=ack)), 'request checkpoint')
        self.assertEqual(self.run_decision(transfer=dict(old_writer_retired=True,replacement_ack=ack)), 'handoff-ready')

    def test_duplicate_and_unknown_references(self):
        self.s['objectives'].append(self.s['objectives'][0])
        with self.assertRaises(ValueError): validate(self.s, {})
        self.s['objectives'].pop()
        self.s['objectives'][0]['depends_on'] = ['missing']
        with self.assertRaises(ValueError): validate(self.s, {})

    def test_cycles(self):
        self.s['objectives'][0]['parent'] = 'handoff.evaluator'
        with self.assertRaises(ValueError): validate(self.s, {})
        self.s['objectives'][0]['parent'] = None
        self.s['objectives'][1]['depends_on'] = ['handoff']
        with self.assertRaises(ValueError): validate(self.s, {})

    def test_fabricated_stale_and_session_start_evidence(self):
        row = self.s['objectives'][0]
        row['evidence'] = ['r']
        row['artifact_revisions'] = ['v1']
        with self.assertRaises(ValueError): validate(self.s, {})
        for kind, revision in [('session-start', 'v1'), ('test', 'v0')]:
            with self.assertRaises(ValueError): validate(self.s, {'r': dict(kind=kind,source='test',revision=revision)})

    def test_parent_acceptance_gate_and_receipt_binding(self):
        row = self.s['objectives'][0]
        row.update(status='accepted', evidence=['r'], artifact_revisions=['v1'])
        row['acceptance'][0]['evidence'] = ['r']
        receipt = dict(kind='acceptance',source='independent-review',revision='v1',objective='handoff',criterion='A1',criterion_digest=criterion_digest(row['acceptance'][0]))
        with self.assertRaises(ValueError): validate(self.s, {'r':receipt})
        self.s['objectives'].pop()
        validate(self.s, {'r':receipt})
        receipt['objective'] = 'other'
        with self.assertRaises(ValueError): validate(self.s, {'r':receipt})

    def test_atomic_cas_replay_and_interruption(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'objectives-status.json'
            path.write_text(json.dumps(self.s))
            original = path.read_bytes()
            def update(s):
                s['revision'] += 1
                s['processed_wakes'].append('wake-1')
                return s
            with patch('orchestration.handoff_loop.core.os.replace', side_effect=OSError('interrupted')):
                with self.assertRaises(OSError): persist(path, digest(self.s), update, {}, self.o, now=100)
            self.assertEqual(path.read_bytes(), original)
            self.assertFalse(path.with_suffix('.json.lock').exists())
            saved = persist(path, digest(self.s), update, {}, self.o, now=100)
            self.assertEqual(evaluate(saved,self.o,{},now=100)['action'], 'no-change')
            self.assertEqual(persist(path,digest(saved),lambda s: self.fail('duplicate must not update'),{},self.o,now=100), saved)
            with self.assertRaises(ValueError): persist(path, digest(self.s), update, {}, self.o, now=100)
            path.with_suffix('.json.lock').touch()
            with self.assertRaises(FileExistsError): persist(path, digest(saved), update, {}, self.o, now=100)
            self.assertEqual(json.loads(path.read_text()), saved)

    def test_write_rejects_bad_owner_and_transfer(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'status.json'
            path.write_text(json.dumps(self.s))
            with self.assertRaises(ValueError): persist(path,digest(self.s),lambda s:s,{},dict(self.o,owner='other'),now=100)
            def steal(s):
                s['revision'] += 1
                s['claim']['owner'] = 'other'
                return s
            with self.assertRaises(ValueError): persist(path,digest(self.s),steal,{},self.o,now=100)

    def test_unknown_activity_and_blocked_objectives(self):
        del self.o['active']
        self.assertEqual(self.run_decision(), 'blocked')
        self.o['active'] = False
        for row in self.s['objectives']:
            row['status'] = 'blocked'
            row['blockers'] = ['dependency unavailable']
        self.assertEqual(self.run_decision(), 'blocked')

    def test_snapshot_cannot_drop_objective_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'status.json'
            path.write_text(json.dumps(self.s))
            def drop(s):
                s['revision'] += 1
                s['objectives'].pop()
                return s
            with self.assertRaises(ValueError): persist(path,digest(self.s),drop,{},self.o,now=100)


if __name__ == '__main__':
    unittest.main()
