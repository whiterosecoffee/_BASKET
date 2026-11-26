"""Read-only qualification probes, never a worker/controller implementation."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from orchestration.agentic import manager
from orchestration import worker_protocol

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODEL = json.loads((HERE / 'scenarios.json').read_text())


def observe(case):
    data = copy.deepcopy(case['inputs'])
    now = manager.utc(MODEL['now'])
    try:
        if case['helper'] == 'attempts':
            manager.event_check(data, now)
            return manager.attempts(data, 'synthetic-recovery')
        if case['helper'] == 'event_check':
            manager.event_check(data, now)
            return {'accepted': True}
        if case['helper'] == 'evidence_check':
            manager.evidence_check(data, now)
            return {'accepted': True}
        if case['helper'] == 'lease_state':
            manager.event_check(data, now)
            active, expired, trusted = manager.lease_state(data, {'synthetic-recovery'}, now)
            return dict(active=active, expired=expired, trusted=trusted)
        raise AssertionError('unknown probe helper')
    except manager.GuardError as error:
        return {'error': str(error)}


class RecoveryQualification(unittest.TestCase):
    def test_pinned_source_bytes(self):
        for source in MODEL['sources']:
            self.assertEqual(hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest(), source['sha256'])

    def test_scenario_coverage_and_labels(self):
        ids = [c['id'] for c in MODEL['scenarios']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 15)
        for case in MODEL['scenarios']:
            self.assertEqual(case['classification'], 'simulated_scenario')
            self.assertTrue(case['expected_transition'])
            self.assertTrue(case['source']['symbol'])
            self.assertEqual(case['source']['commit'], MODEL['base_commit'])
        gaps = {c['id'] for c in MODEL['scenarios'] if c['implementation_gap']}
        self.assertIn('uncertain_write_mislabeled_failure', gaps)
        self.assertIn('newer_user_steering', gaps)

    def test_protocol_stale_head_rejected(self):
        # Existing dated public examples are offline evidence, never live authorization.
        read = worker_protocol.read
        examples = ROOT / 'orchestration/examples'
        task = read(examples / 'B05.task.json')
        report = read(examples / 'B05.resolution.json')
        evidence = read(examples / 'github-evidence-2026-10-16.json')
        catalog = read(ROOT / 'orchestration/sparks.json')
        original = copy.deepcopy(evidence)
        control = worker_protocol.evidence_check(task, report, evidence, catalog)
        self.assertEqual(control['b00_evidence_phase'], 'component_verified_review_pending')
        next(pr for pr in evidence['pull_requests'] if pr['number'] == report['pr']['number'])['head_sha'] = 'a' * 40
        result = worker_protocol.evidence_check(task, report, evidence, catalog)
        self.assertEqual(result['b00_evidence_phase'], 'evidence_invalid')
        self.assertTrue(result['errors'])
        self.assertNotEqual(evidence, original)

    def test_latest_failure_overrides_prior_success(self):
        runs = [{'id': 1, 'name': 'Validate BASKET data', 'head_sha': 'a'*40,
                 'status': 'completed', 'conclusion': 'success', 'url': 'https://example.invalid/1'}]
        self.assertTrue(manager.ci_green({'workflow_runs': runs}, 'a'*40))
        runs.append(dict(runs[0], id=2, conclusion='failure', url='https://example.invalid/2'))
        self.assertFalse(manager.ci_green({'workflow_runs': runs}, 'a'*40))
        self.assertFalse(manager.ci_green({'workflow_runs': list(reversed(runs))}, 'a'*40))


def scenario_test(case):
    def test(self):
        before = copy.deepcopy(case)
        actual = observe(case)
        for key, expected in case['expected_helper'].items():
            self.assertEqual(actual.get(key), expected, (case['id'], actual))
        self.assertEqual(observe(case), actual, 'unchanged replay must be deterministic')
        self.assertEqual(case, before, 'input corpus must remain unchanged')
    return test


for case in MODEL['scenarios']:
    setattr(RecoveryQualification, 'test_case_' + case['id'], scenario_test(case))

if __name__ == '__main__':
    unittest.main()
