"""Semantic profile checks; underlying lifecycle regressions remain in their suite."""
import copy
import unittest
from pathlib import Path
from unittest.mock import patch
from orchestration.clean_templates import lifecycle as lc, semantic as sm


class SemanticTemplateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = lc.read('semantic.examples.json')
        self.prior = self.fixture['prior']
        self.value = copy.deepcopy(self.fixture['examples']['planned-child'])

    def check(self):
        result = sm.evaluate(self.value, prior=self.prior,
                             now=self.fixture['evaluation_time'],
                             expected_revision=self.fixture['expected_revision'])
        self.assertFalse(result['execution_authorized'])
        self.assertEqual(result['new_executions'], [])
        return result

    def reject(self, error=None):
        result = self.check()
        self.assertFalse(result['valid'], result)
        if error:
            self.assertIn(error, result['errors'])
        return result

    def test_valid_planned_child_and_all_examples(self):
        for name, value in self.fixture['examples'].items():
            with self.subTest(name=name):
                self.value = value
                self.assertTrue(self.check()['valid'], self.check()['errors'])
                child = value['planned_children'][0]
                self.assertIsNone(child['branch'])
                self.assertIsNone(child['running_worker'])

    def test_ghost_promotion_to_branch_or_worker_is_rejected(self):
        for key in ('branch', 'running_worker'):
            with self.subTest(key=key):
                self.value['planned_children'][0][key] = 'asserted-live'
                self.reject()
                self.value['planned_children'][0][key] = None

    def test_child_requires_intended_owner_acceptance_and_parent(self):
        saved = copy.deepcopy(self.value)
        for key in ('intended_owner', 'acceptance', 'parent_task_id'):
            self.value = copy.deepcopy(saved)
            del self.value['planned_children'][0][key]
            self.reject()
        self.value = saved
        self.value['planned_children'][0]['parent_task_id'] = 'different'
        self.reject('CHILD_PARENT_MISMATCH')

    def test_one_active_objective_and_matching_owner(self):
        saved = copy.deepcopy(self.value)
        self.value['active_objectives'] *= 2
        self.reject()
        self.value = saved
        self.value['active_objectives'][0]['owner_session'] = 'other'
        self.reject('ACTIVE_OBJECTIVE_OWNER_MISMATCH')

    def test_purpose_outcomes_and_non_goals_are_required(self):
        saved = copy.deepcopy(self.value)
        for key in ('purpose', 'outcomes', 'non_goals'):
            self.value = copy.deepcopy(saved)
            del self.value['active_objectives'][0][key]
            self.reject()
        self.value = saved
        self.value['active_objectives'][0]['outcomes'] = ['A999']
        self.reject('OUTCOMES_MUST_BIND_TASK_CRITERIA')

    def test_later_correction_retains_original_lineage_and_source(self):
        self.value = self.fixture['examples']['retained-correction']
        self.assertTrue(self.check()['valid'])
        self.assertEqual(self.value['intake'][:-1], self.prior['intake'])
        self.value['intake'][0]['source']['sha256'] = '0' * 64
        self.reject('PRIOR_INTAKE_MUST_BE_RETAINED')

    def test_removed_predecessor_or_forward_correction_rejects(self):
        self.value = self.fixture['examples']['retained-correction']
        del self.value['intake'][0]
        self.reject('CORRECTION_REQUIRES_RETAINED_PREDECESSOR')

    def test_unapproved_question_and_idea_remain_noncommitments(self):
        saved = copy.deepcopy(self.value)
        for index in (0, 1):
            self.value = copy.deepcopy(saved)
            self.value['active_objectives'][0]['intake_id'] = self.value['intake'][index]['id']
            self.reject('QUESTION_OR_IDEA_IS_NOT_ACTIVE_COMMITMENT')
            self.value['intake'][index]['kind'] = 'commitment'
            self.reject('COMMITMENT_REQUIRES_EXPLICIT_APPROVAL')

    def test_explicit_approved_append_preserves_question(self):
        entry = copy.deepcopy(self.value['intake'][2])
        entry.update(id='approved-followup', supersedes='question-1')
        self.value['intake'].append(entry)
        self.value['active_objectives'][0]['intake_id'] = entry['id']
        self.assertTrue(self.check()['valid'])
        self.assertEqual(self.value['intake'][0]['kind'], 'question')

    def test_wrong_head_rejects_against_supplied_expected_revision(self):
        self.fixture['expected_revision'] = 'f' * 40
        self.reject('EXPECTED_HEAD_MISMATCH')

    def test_replay_request_change_requires_owner_reconciliation(self):
        from orchestration import component_conformance as cc
        life = self.value['lifecycle']
        life['request']['request_id'] += '-new'
        digest = cc.digest(cc.canonical(life['request']))
        life['acknowledgment']['request_sha256'] = digest
        life['outcome']['receipt']['request_sha256'] = digest
        self.reject('REPLAY_REQUEST_CHANGED_REQUIRES_OWNER_RECONCILIATION')

    def test_duplicate_wake_preserves_effects_without_execution(self):
        self.value = self.fixture['examples']['duplicate-wake']
        result = self.check()
        self.assertTrue(result['valid'])
        self.assertEqual(result['action'], 'reuse_existing_evidence')
        self.assertEqual(result['known_effects'], self.prior['known_effects'])

    def test_uncertain_retry_is_reconciliation_even_if_later_flag_cleared(self):
        self.value = self.fixture['examples']['uncertain-replay']
        self.assertEqual(self.check()['action'], 'reconcile_uncertain_effect')
        self.prior['wake']['uncertain_effect'] = True
        self.value['wake']['uncertain_effect'] = False
        self.assertEqual(self.check()['action'], 'reconcile_uncertain_effect')

    def test_replay_cannot_delete_or_rewrite_known_effects(self):
        self.value['known_effects'] = []
        result = self.reject('PRIOR_KNOWN_EFFECTS_MUST_BE_RETAINED')
        self.assertEqual(result['known_effects'], self.prior['known_effects'])

    def test_repeat_deterministic_and_inputs_and_returned_effects_isolated(self):
        before = copy.deepcopy((self.value, self.prior))
        first = self.check()
        self.assertEqual(first, self.check())
        first['known_effects'][0]['id'] = 'mutated-return'
        self.assertEqual((self.value, self.prior), before)

    def test_worker_resolution_is_reused_and_bound(self):
        self.value['resolution']['task_id'] = 'B00-999'
        self.reject('RESOLUTION_TASK_MISMATCH')
        self.value['resolution'] = {}
        self.reject()

    def test_malformed_profile_rejects_without_exception(self):
        for value in (None, [], {}, {'profile': 'wrong'}):
            self.value = value
            result = self.reject()
            self.assertEqual(result['known_effects'], self.prior['known_effects'])

    def test_no_network_dispatch_archive_or_output_write(self):
        original = Path.open
        allowed = {lc.ROOT / 'lifecycle.schema.json',
                   sm.wp.ROOT / 'schemas/worker-task.v1.json',
                   sm.wp.ROOT / 'schemas/worker-resolution.v1.json'}
        def guarded(path, mode='r', *args, **kwargs):
            self.assertIn(path, allowed)
            self.assertEqual(mode, 'r')
            return original(path, mode, *args, **kwargs)
        with patch.object(Path, 'open', guarded), \
                patch('socket.socket', side_effect=AssertionError('network')), \
                patch('subprocess.run', side_effect=AssertionError('dispatch')):
            self.assertTrue(self.check()['valid'])

    def test_data_example_uses_canonical_tasks_with_distinct_scoped_owners(self):
        data = lc.read('semantic.data-example.json')
        consumers = data['consumers']
        self.assertEqual(len(consumers), 2)
        self.assertEqual(len({c['task']['branch']['name'] for c in consumers}), 2)
        self.assertEqual(len({c['accountable_owner'] for c in consumers}), 2)
        self.assertEqual(len({tuple(c['task']['write_paths']) for c in consumers}), 2)
        for consumer in consumers:
            self.assertEqual(sm.wp.validate_schema(consumer['task'], 'task'), [])
            self.assertTrue(consumer['synthetic'])
            self.assertEqual(consumer['request_target'], '_FETCH')
            self.assertEqual(consumer['maintenance_owner'], '_FETCH')
            self.assertEqual(consumer['access'], 'read_only')

    def test_fetch_master_and_massive_dependency_keep_request_provider_neutral(self):
        import json
        data = lc.read('semantic.data-example.json')
        self.assertEqual(data['master_class'], '_FETCH')
        self.assertFalse(data['execution_authorized'])
        adapter = data['dependency_metadata']['adapters'][0]
        self.assertEqual((adapter['id'], adapter['kind'], adapter['parent']),
                         ('Massive', 'source_adapter', '_FETCH'))
        request = lc.read('lifecycle.examples.json')['examples']['market-readonly']['request']
        self.assertNotIn('Massive', json.dumps(request))
        self.assertEqual(request['operation'], 'consume')

    def test_fetch_product_capabilities_are_separate_from_verified_maturity(self):
        data = lc.read('semantic.data-example.json')
        self.assertEqual(set(data['intended_capabilities']), {
            'ongoing_live_source_acquisition', 'standardization', 'sanitization',
            'persistence_to_requester_authorized_local_repository_store'})
        maturity = data['verified_maturity']
        self.assertEqual(maturity['evidence_scope'], 'local_synthetic_template_checks_only')
        self.assertFalse(maturity['live_operation_verified'])
        self.assertEqual(maturity['governing_adoption_verified'], 0)
        self.assertFalse(data['execution_authorized'])
        adoption = lc.read('semantic.adoption.json')['data_architecture']
        self.assertEqual(adoption['verified_maturity']['live_operation_verified'], False)
        self.assertIn('Ongoing live source acquisition', adoption['intended_scope'])

    def test_requester_private_store_and_conflict_policy_remain_explicit(self):
        data = lc.read('semantic.data-example.json')
        for consumer in data['consumers']:
            store = consumer['authorized_store']
            self.assertEqual(store['accountable_owner'], consumer['accountable_owner'])
            self.assertEqual(store['destination'], 'requesting_component_local_repository_store')
            self.assertTrue(store['private'])
            self.assertEqual(store['persistence_writer'], '_FETCH')
            self.assertEqual(store['authorization'], 'explicit_requester_scoped_destination_authorization_required')
            self.assertEqual(store['publication'], 'none')
            self.assertEqual(consumer['access'], 'read_only')
        self.assertIn('quarantine', data['data_policy']['conflicts'])
        self.assertIn('lineage', data['data_policy']['provenance'])
        self.assertIn('separate later read-only', data['data_policy']['consumer_use'])
