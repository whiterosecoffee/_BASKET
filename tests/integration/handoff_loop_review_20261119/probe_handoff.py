"""Independent consumer probes; execute against a separate verified export."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest


class ConsumerProbes(unittest.TestCase):
    def setUp(self):
        from orchestration.handoff_loop import core
        self.core = core
        self.state = json.loads(Path(core.__file__).with_name('objectives-status.example.json').read_text())
        self.observation = dict(self.state['claim'], online=True, verified_at=100,
            single_writer=True, wake_id='independent-review-wake', active=False,
            approval_pending=False, handoff_requested=False, checkpoint_due=False)

    def test_continue_is_only_a_decision(self):
        result = self.core.evaluate(self.state, self.observation, {}, now=100)
        self.assertEqual(result['action'], 'continue')
        self.assertEqual(result['execution'], 'not_attempted')
        self.assertEqual(result['acceptance'], 'not_established')

    def test_omitted_wake_is_consumed_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'state.json'
            path.write_text(json.dumps(self.state))
            def update(state):
                state['revision'] += 1
                return state
            saved = self.core.persist(path, self.core.digest(self.state), update, {}, self.observation, now=100)
            before = path.read_bytes()
            self.core.persist(path, self.core.digest(saved), lambda s: self.fail('duplicate executed update'), {}, self.observation, now=100)
            self.assertEqual(path.read_bytes(), before)

    def test_success_dimension_cannot_be_self_asserted(self):
        self.state['dimensions']['publication'] = {'status':'published', 'evidence':[]}
        with self.assertRaises(ValueError):
            self.core.validate(self.state, {})

    def test_criterion_cannot_be_weakened_during_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'state.json'
            path.write_text(json.dumps(self.state))
            before = path.read_bytes()
            def weaken(state):
                state['revision'] += 1
                state['objectives'][0]['acceptance'][0]['condition'] = 'Easier'
                return state
            with self.assertRaises(ValueError):
                self.core.persist(path, self.core.digest(self.state), weaken, {}, self.observation, now=100)
            self.assertEqual(path.read_bytes(), before)

    def test_live_boundary_cannot_be_enabled_by_caller_flags(self):
        from orchestration.handoff_loop.trigger_bridge import admit_live_trigger
        result = admit_live_trigger('/nonexistent/never-open.json', {'verified':True,'authenticated':True})
        self.assertEqual(result['status'], 'blocked')
        self.assertFalse(result['checkpoint_written'])
        self.assertFalse(result['dispatch_authorized'])

    def test_boolean_timestamp_cannot_establish_freshness(self):
        # A JSON boolean is not an observation epoch. Keep failure visible.
        observation = dict(self.observation, verified_at=True)
        self.assertEqual(self.core.evaluate(self.state, observation, {}, now=100)['action'], 'blocked')


if __name__ == '__main__':
    source = Path(sys.argv.pop(1)).resolve()
    sys.path.insert(0, str(source))
    unittest.main(verbosity=2)
