"""Independent B01 acceptance checks. Upstream defects remain real CI failures."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def read(path):
    return json.loads((ROOT / path).read_text())


class WorkerQC(unittest.TestCase):
    def setUp(self):
        self.loop = module('independent_loop', 'orchestration/execution_loop.py')
        self.wp = module('independent_protocol', 'orchestration/worker_protocol.py')
        self.av = module('independent_attempts', 'orchestration/validate_worker_attempts.py')
        self.q = read('orchestration/planner/queue.json')
        self.lib = read('orchestration/planner/worker-library.json')
        self.reg = read('orchestration/sparks.json')
        self.ev = read('orchestration/examples/github-evidence-2026-10-16.json')
        self.task = read('orchestration/examples/B05.task.json')
        self.report = read('orchestration/examples/B05.resolution.json')

    def test_historical_fixture_never_claims_live_or_integrated(self):
        out = self.wp.evidence_check(self.task, self.report, self.ev, self.reg)
        self.assertEqual(out['errors'], [])
        self.assertEqual(out['b00_evidence_phase'], 'component_verified_review_pending')
        plan = self.loop.reconcile(self.q, self.lib, self.reg, self.ev)
        self.assertFalse(plan['source_fetched_this_invocation'])
        self.assertEqual(plan['side_effects_executed'], [])
        self.assertIsNone(plan['next_new_worker'])

    def test_missing_mandatory_workflow_cannot_verify_component(self):
        self.report['checks'] = []
        out = self.wp.evidence_check(self.task, self.report, self.ev, self.reg)
        self.assertTrue(out['errors'], 'Missing mandatory CI is only a warning; CLI exits zero')

    def test_stale_head_cannot_return_verified_phase(self):
        self.report['pr']['head_sha'] = '0' * 40
        next(p for p in self.ev['pull_requests'] if p['number'] == 10)['head_sha'] = '0' * 40
        out = self.wp.evidence_check(self.task, self.report, self.ev, self.reg)
        self.assertTrue(out['errors'])
        self.assertNotEqual(out['b00_evidence_phase'], 'component_verified_review_pending')

    def test_owner_breach_cannot_return_verified_phase(self):
        path = 'schemas/relationships.v1.json'
        self.report['changed_paths'].append(path)
        next(p for p in self.ev['pull_requests'] if p['number'] == 10)['changed_paths'].append(path)
        out = self.wp.evidence_check(self.task, self.report, self.ev, self.reg)
        self.assertTrue(out['errors'])
        self.assertNotEqual(out['b00_evidence_phase'], 'component_verified_review_pending',
                            'Errors must prevent a verified phase')

    def test_duplicate_queue_tasks_rejected(self):
        self.q['tasks'].append(copy.deepcopy(self.q['tasks'][0]))
        with self.assertRaises(ValueError):
            self.loop.reconcile(self.q, self.lib, self.reg, self.ev, [])

    def test_one_slot_dispatches_only_highest_priority(self):
        # Simulation only: make prerequisites merged to expose multiple ready jobs.
        for p in self.ev['pull_requests']:
            if p['number'] in (2, 10, 13):
                p.update(merged=True, draft=False, state='closed')
        out = self.loop.reconcile(self.q, self.lib, self.reg, self.ev, ['T-004', 'T-005'])
        self.assertEqual(out['worker_slots_remaining'], 1)
        dispatched = [a['task_id'] for a in out['actions'] if a['qc_phase'] == 'dispatch_ready']
        self.assertEqual(dispatched, ['T-009'])
        self.assertTrue(any(a['qc_phase'] == 'queued_for_slot' for a in out['actions']))

    def test_full_capacity_dispatches_nothing(self):
        out = self.loop.reconcile(self.q, self.lib, self.reg, self.ev, ['T-004', 'T-005', 'T-006'])
        self.assertEqual(out['worker_slots_remaining'], 0)
        self.assertIsNone(out['next_new_worker'])
        self.assertFalse(any(a['qc_phase'] == 'dispatch_ready' for a in out['actions']))

    def test_active_task_never_redispatched(self):
        active = ['T-004', 'T-006']
        out = self.loop.reconcile(self.q, self.lib, self.reg, self.ev, active)
        self.assertNotIn(out['next_new_worker'], active)

    def test_self_retry_rejected(self):
        ledger = read('orchestration/planner/attempts/T-001.json')
        ledger['attempts'][1]['retry_of'] = ledger['attempts'][1]['attempt_id']
        ledger['lessons'] = []  # Isolate lineage from the independent lesson gate.
        scopes = read('orchestration/planner/worker-scopes.json')
        self.assertTrue(self.av.evaluate(ledger, scopes), 'Self retry was accepted')

    def test_fabricated_efficiency_rejected(self):
        ledger = read('orchestration/planner/attempts/T-001.json')
        ledger['evaluation']['measured_time_seconds'] = 1
        self.assertTrue(self.av.evaluate(ledger, read('orchestration/planner/worker-scopes.json')))


if __name__ == '__main__':
    unittest.main()
