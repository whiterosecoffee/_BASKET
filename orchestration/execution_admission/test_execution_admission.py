"""Synthetic contract cases plus sanitized real preflight rejection fixtures."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from preflight import evaluate, fingerprint, REQUEST_SCHEMA, RECEIPT_SCHEMA
from jsonschema import Draft202012Validator

NOW = '2026-11-12T12:00:00Z'


def specimen():
    """Synthetic eligible case; no live ownership or authorization claim."""
    identity = dict(task_id='B00-999', owner='fixture-worker', spark='B00',
                    branch='work/999-admission-fixture', head='a'*40, worktree='fixture-worktree')
    r = dict(schema='basket.execution_request@1', policy_version='fixture-policy@1',
             identity=identity, purpose='Exercise admission contract',
             manifest=dict(path='orchestration/example/README.md', sha256='b'*64),
             owned_folders=['orchestration/example'], allowed_writes=['orchestration/example/result.json'],
             authority=dict(source='fixture-controller', inherited_from='B00', scope=['orchestration/example']),
             executor=dict(host='WORKSTATION-A', os='Windows', resources=['python']),
             inputs=[dict(id='input', schema='fixture@1', sha256='c'*64, max_age_seconds=60)],
             prerequisites=['approval'], acceptance_tests=['negative and repeat'],
             permitted_effects=['local_artifact'],
             recovery=dict(idempotency_key='fixture-1', strategy='reconcile then retry', uncertain_effects_action='reconcile_before_retry'),
             lifecycle=dict(mode='new', previous_owner=None, transfer_ref=None), fallback='park_only')
    o = dict(evidence_kind='executor_observation', collector='fixture-collector', observed_at=NOW,
             identity=copy.deepcopy(identity), host='Workstation-A', os='Windows', isolated_worktree=True,
             purpose_present=True, manifest_sha256='b'*64, ownership_complete=True, ownership=[],
             writers_complete=True, writers=[], resources=[dict(id='python', confirmed=True)],
             inputs=[dict(id='input', readable=True, schema='fixture@1', schema_valid=True, sha256='c'*64, observed_at=NOW)],
             prerequisites=[dict(id='approval', confirmed=True)], prior_effects='none',
             prior_idempotency_key=None, continuation=None, transfer=None, online=True)
    t = dict(policy_version='fixture-policy@1', request_sha256=fingerprint(r), identity=copy.deepcopy(identity),
             authority_source='fixture-controller', authority_parent='B00', allowed_scope=['orchestration/example'],
             effects=['local_artifact'], host='WORKSTATION-A', os='Windows', collector='fixture-collector',
             max_evidence_age_seconds=60, task_registered=True, new_identity_confirmed=True,
             continuation_binding=None)
    return r, o, t


def continuation_proof(identity):
    return dict(identity=copy.deepcopy(identity), session_id='session-1', lease_id='lease-1',
                lease_confirmed=True, lease_expires_at='2026-11-12T12:01:00Z')


def continuation_specimen():
    r, o, t = specimen()
    r['lifecycle']['mode'] = 'continuation'
    o['continuation'] = continuation_proof(r['identity'])
    t['continuation_binding'] = dict(session_id='session-1', lease_id='lease-1')
    writer = {k: r['identity'][k] for k in ('task_id','owner','branch','worktree')}
    writer.update(active=True, **t['continuation_binding'])
    o['writers'] = [writer]
    t['request_sha256'] = fingerprint(r)
    return r, o, t


class AdmissionTests(unittest.TestCase):
    def run_case(self, triplet):
        return evaluate(*triplet, now=NOW)

    def assertRejected(self, triplet, reason):
        receipt = self.run_case(triplet)
        self.assertEqual(receipt['decision'], 'rejected')
        self.assertIn(reason, receipt['reasons'])
        self.assertFalse(receipt['execution_authorized'])

    def test_schema_definitions_valid(self):
        Draft202012Validator.check_schema(REQUEST_SCHEMA)
        Draft202012Validator.check_schema(RECEIPT_SCHEMA)

    def test_receipt_cannot_claim_contradictory_next_action(self):
        receipt = self.run_case(specimen())
        receipt['decision'] = 'parked'
        self.assertFalse(Draft202012Validator(RECEIPT_SCHEMA).is_valid(receipt))

    def test_eligible_repeat_and_immutable_inputs(self):
        values = specimen()
        before = copy.deepcopy(values)
        first = self.run_case(values)
        self.assertEqual(first['decision'], 'eligible')
        self.assertEqual(first, self.run_case(values))
        self.assertEqual(values, before)
        self.assertFalse(first['execution_authorized'])
        self.assertFalse(first['evidence_truth_verified'])

    def test_no_io_during_evaluation(self):
        with patch('builtins.open', side_effect=AssertionError('unexpected IO')), patch('socket.socket', side_effect=AssertionError('network')):
            self.assertEqual(self.run_case(specimen())['decision'], 'eligible')

    def test_every_top_level_field_required(self):
        for i in range(3):
            for key in specimen()[i]:
                with self.subTest(contract=i, key=key):
                    values = specimen()
                    del values[i][key]
                    self.assertIn('schema:', ' '.join(self.run_case(values)['reasons']))

    def test_unknown_fields_rejected(self):
        for i in range(3):
            values = specimen()
            values[i]['trust_me'] = True
            self.assertEqual(self.run_case(values)['decision'], 'rejected')

    def test_wrong_host_and_branch(self):
        for i, key, value, reason in [(1,'host','CLOUD','executor_mismatch'),
                                     (1,'os','Linux','executor_mismatch')]:
            values = specimen()
            values[i][key] = value
            self.assertRejected(values, reason)
        values = specimen()
        values[1]['identity']['branch'] = 'main'
        self.assertRejected(values, 'identity_mismatch')

    def test_declared_host_cannot_override_trusted_pin(self):
        values = specimen()
        values[0]['executor']['host'] = values[1]['host'] = 'CLOUD'
        self.assertRejected(values, 'executor_mismatch')

    def test_identity_and_worktree_pins(self):
        for key in specimen()[0]['identity']:
            values = specimen()
            values[1]['identity'][key] = 'b'*40 if key == 'head' else 'other'
            self.assertRejected(values, 'identity_mismatch')

    def test_main_even_if_all_declarations_agree(self):
        values = specimen()
        for v in values:
            v['identity']['branch'] = 'main'
        self.assertRejected(values, 'unscoped_branch')

    def test_missing_purpose_manifest_or_isolation(self):
        for key, value, reason in [('purpose_present',False,'purpose_or_manifest_missing'),
                                  ('manifest_sha256','d'*64,'purpose_or_manifest_missing'),
                                  ('isolated_worktree',False,'worktree_not_isolated')]:
            values = specimen()
            values[1][key] = value
            self.assertRejected(values, reason)

    def test_stale_future_and_invalid_timestamps(self):
        for time in ['2026-11-12T11:58:59Z', '2026-11-12T12:00:01Z']:
            values = specimen()
            values[1]['observed_at'] = time
            self.assertRejected(values, 'evidence_stale_or_future')
        values = specimen()
        values[1]['observed_at'] = '2026-11-12T12:00:00'
        self.assertRejected(values, 'schema:observation')

    def test_input_readability_schema_integrity_freshness(self):
        for key, value, reason in [('readable',False,'input_unreadable'),
                                  ('schema_valid',False,'input_schema_mismatch'),
                                  ('schema','wrong','input_schema_mismatch'),
                                  ('sha256','d'*64,'input_integrity_mismatch'),
                                  ('observed_at','2026-11-12T11:00:00Z','input_stale_or_future')]:
            values = specimen()
            values[1]['inputs'][0][key] = value
            self.assertRejected(values, reason)
        values = specimen()
        values[1]['inputs'] = []
        self.assertRejected(values, 'input_unreadable')

    def test_resources_and_prerequisites(self):
        for key, reason in [('resources','resource_unconfirmed'),('prerequisites','prerequisite_unconfirmed')]:
            for replacement in [[], [dict(id='python' if key=='resources' else 'approval', confirmed=False)]]:
                values = specimen()
                values[1][key] = replacement
                self.assertRejected(values, reason)

    def test_overlapping_parent_child_and_case_alias(self):
        for path in ['orchestration', 'orchestration/example/file', 'Orchestration/EXAMPLE']:
            values = specimen()
            values[1]['ownership'] = [dict(task_id='other',owner='other',branch='work/888-other',worktree='other',paths=[path])]
            self.assertRejected(values, 'ownership_overlap')

    def test_sibling_is_disjoint(self):
        values = specimen()
        values[1]['ownership'] = [dict(task_id='other',owner='other',branch='work/888-other',worktree='other',paths=['orchestration/example2'])]
        self.assertEqual(self.run_case(values)['decision'], 'eligible')

    def test_scope_and_unsupported_paths(self):
        for path in ['../escape','/absolute','C:/private','orchestration/**','orchestration//example','orchestration/example.','orchestration\\example']:
            values = specimen()
            values[0]['allowed_writes'] = [path]
            self.assertRejected(values, 'unsupported_path')
        values = specimen()
        values[0]['allowed_writes'] = ['runtime/file.py']
        self.assertRejected(values, 'scope_escalation')

    def test_effects_authority_and_policy(self):
        values = specimen()
        values[0]['permitted_effects'] = ['deploy']
        self.assertRejected(values, 'effect_not_permitted')
        values = specimen()
        values[0]['authority']['inherited_from'] = 'B02'
        self.assertRejected(values, 'authority_mismatch')
        values = specimen()
        values[0]['policy_version'] = 'other'
        self.assertRejected(values, 'policy_mismatch')

    def test_incomplete_inventory(self):
        for key in ['ownership_complete','writers_complete']:
            values = specimen()
            values[1][key] = False
            self.assertRejected(values, 'incomplete_writer_inventory')

    def test_competing_writer_same_task_different_worktree(self):
        values = specimen()
        writer = {k:values[0]['identity'][k] for k in ('task_id','owner','branch','worktree')}
        writer.update(active=True, worktree='other', session_id='session-1', lease_id='lease-1')
        values[1]['writers'] = [writer]
        self.assertRejected(values, 'competing_writer')

    def test_new_launch_rejects_identical_active_writer(self):
        values = specimen()
        writer = {k: values[0]['identity'][k] for k in ('task_id','owner','branch','worktree')}
        writer.update(active=True, session_id='session-1', lease_id='lease-1')
        values[1]['writers'] = [writer]
        self.assertRejected(values, 'competing_writer')

    def test_transfer_rejects_conflicting_continuation(self):
        values = specimen()
        values[0]['lifecycle'] = dict(mode='transfer',previous_owner='old-owner',transfer_ref='fixture-transfer')
        values[1]['transfer'] = dict(previous_owner='old-owner',ref='fixture-transfer',stopped=True,confirmed=True)
        values[1]['continuation'] = continuation_proof(values[0]['identity'])
        values[1]['continuation']['identity']['owner'] = 'conflicting-owner'
        values[2]['request_sha256'] = fingerprint(values[0])
        self.assertRejected(values, 'unexpected_lifecycle_evidence')

    def test_uncertain_or_completed_effects_cannot_repeat(self):
        for state, reason in [('uncertain','prior_effects_uncertain'),('confirmed_complete','already_completed_reconcile_only')]:
            values = specimen()
            values[1]['prior_effects'] = state
            self.assertRejected(values, reason)

    def test_idempotency_binding(self):
        values = specimen()
        values[1]['prior_idempotency_key'] = 'different'
        self.assertRejected(values, 'idempotency_key_mismatch')

    def test_continuation_retains_identity(self):
        values = continuation_specimen()
        self.assertEqual(self.run_case(values)['decision'], 'eligible')
        values[1]['continuation']['identity']['owner'] = 'other'
        self.assertRejected(values, 'continuation_ownership_changed')

    def test_transfer_requires_record_and_stopped_writer(self):
        values = specimen()
        values[0]['lifecycle'] = dict(mode='transfer',previous_owner='old-owner',transfer_ref='fixture-transfer')
        values[1]['transfer'] = dict(previous_owner='old-owner',ref='fixture-transfer',stopped=True,confirmed=True)
        values[2]['request_sha256'] = fingerprint(values[0])
        self.assertEqual(self.run_case(values)['decision'], 'eligible')
        for key in ['stopped','confirmed']:
            bad = copy.deepcopy(values)
            bad[1]['transfer'][key] = False
            self.assertRejected(bad, 'transfer_not_confirmed_stopped')

    def test_offline_only_parks_even_with_invalid_evidence(self):
        values = specimen()
        values[1]['online'] = False
        values[1]['host'] = 'WRONG'
        receipt = self.run_case(values)
        self.assertEqual(receipt['decision'], 'parked')
        self.assertEqual(receipt['permitted_next'], 'park_only')
        self.assertIn('executor_mismatch', receipt['reasons'])

    def test_request_and_observation_bound_into_receipt(self):
        values = specimen()
        receipt = self.run_case(values)
        self.assertEqual(receipt['request_sha256'], fingerprint(values[0]))
        self.assertEqual(receipt['observation_sha256'], fingerprint(values[1]))
        self.assertNotIn('WORKSTATION-A', json.dumps(receipt))

    def test_registry_and_new_task_proof_required(self):
        for key, reason in [('task_registered','task_unregistered'), ('new_identity_confirmed','new_identity_unconfirmed')]:
            values = specimen()
            values[2][key] = False
            self.assertRejected(values, reason)

    def test_worker_cannot_omit_controller_required_inputs(self):
        values = specimen()
        values[0]['inputs'] = []
        values[0]['prerequisites'] = []
        self.assertRejected(values, 'request_not_controller_approved')

    def test_manifest_must_be_owned(self):
        values = specimen()
        values[0]['manifest']['path'] = 'other/task.json'
        self.assertRejected(values, 'manifest_outside_owned_folder')

    def test_duplicate_evidence_ids_are_not_last_writer_wins(self):
        for key in ['resources','prerequisites','inputs']:
            values = specimen()
            other = copy.deepcopy(values[1][key][0])
            other['readable' if key == 'inputs' else 'confirmed'] = False
            values[1][key].append(other)
            self.assertRejected(values, 'duplicate_evidence_id')

    def test_collector_pin_required(self):
        values = specimen()
        values[1]['collector'] = 'worker-self-declaration'
        self.assertRejected(values, 'collector_mismatch')

    def test_freshness_boundary_and_bad_calendar_date(self):
        values = specimen()
        values[1]['observed_at'] = '2026-11-12T11:59:00Z'
        self.assertEqual(self.run_case(values)['decision'], 'eligible')
        values[1]['observed_at'] = '2026-02-30T12:00:00Z'
        self.assertRejected(values, 'schema:observation')

    def test_continuation_without_evidence_rejected(self):
        values = specimen()
        values[0]['lifecycle']['mode'] = 'continuation'
        self.assertRejected(values, 'continuation_ownership_changed')

    def test_transfer_without_record_rejected(self):
        values = specimen()
        values[0]['lifecycle']['mode'] = 'transfer'
        self.assertRejected(values, 'transfer_not_confirmed_stopped')

    def test_new_task_cannot_smuggle_transfer_evidence(self):
        values = specimen()
        values[1]['transfer'] = dict(previous_owner='old',ref='record',stopped=True,confirmed=True)
        self.assertRejected(values, 'unexpected_lifecycle_evidence')

    def test_real_workstation_and_data_continuation_remain_blocked(self):
        fixtures = json.loads((Path(__file__).parent/'observed_fixtures.json').read_text())
        for case in fixtures['cases']:
            values = specimen()
            for v in values:
                v['identity'].update(case['identity'])
            values[0]['lifecycle']['mode'] = case['mode']
            if case['mode'] == 'continuation':
                values[1]['continuation'] = continuation_proof(values[0]['identity'])
            values[1]['writers_complete'] = False
            values[2]['task_registered'] = case['task_registered']
            receipt = self.run_case(values)
            self.assertEqual(receipt['decision'], 'rejected')
            self.assertIn('incomplete_writer_inventory', receipt['reasons'])

    def test_continuation_requires_unique_bound_session_and_lease(self):
        for target in ('proof', 'writer'):
            for key in ('session_id', 'lease_id'):
                with self.subTest(target=target, key=key):
                    values = continuation_specimen()
                    entry = values[1]['continuation'] if target == 'proof' else values[1]['writers'][0]
                    entry[key] = 'other'
                    self.assertRejected(values, 'continuation_lease_unconfirmed' if target == 'proof' else 'continuation_writer_binding_mismatch')

    def test_continuation_rejects_missing_unconfirmed_or_expired_lease(self):
        for key, value in [('lease_confirmed',False), ('lease_expires_at',NOW),
                           ('lease_expires_at','2026-11-12T11:59:59Z')]:
            values = continuation_specimen()
            values[1]['continuation'][key] = value
            self.assertRejected(values, 'continuation_lease_unconfirmed')
        values = continuation_specimen()
        values[2]['continuation_binding'] = None
        self.assertRejected(values, 'continuation_lease_unconfirmed')

    def test_continuation_rejects_absent_or_multiple_active_sessions(self):
        values = continuation_specimen()
        values[1]['writers'] = []
        self.assertRejected(values, 'continuation_writer_missing_or_multiple')
        values = continuation_specimen()
        other = copy.deepcopy(values[1]['writers'][0])
        other['session_id'] = 'second-session'
        values[1]['writers'].append(other)
        self.assertRejected(values, 'competing_writer')

    def test_continuation_repeat_is_immutable(self):
        values = continuation_specimen()
        original = copy.deepcopy(values)
        first = self.run_case(values)
        self.assertEqual(first['decision'], 'eligible')
        self.assertEqual(first, self.run_case(values))
        self.assertEqual(values, original)

    def test_continuation_lease_fields_cannot_be_omitted(self):
        for key in ('session_id','lease_id','lease_confirmed','lease_expires_at'):
            values = continuation_specimen()
            del values[1]['continuation'][key]
            self.assertRejected(values, 'schema:observation')
        for key in ('session_id','lease_id'):
            values = continuation_specimen()
            del values[1]['writers'][0][key]
            self.assertRejected(values, 'schema:observation')

    def test_new_launch_rejects_continuation_binding(self):
        values = specimen()
        values[2]['continuation_binding'] = dict(session_id='session-1',lease_id='lease-1')
        self.assertRejected(values, 'unexpected_continuation_binding')

    def test_transfer_rejects_matching_continuation_too(self):
        values = specimen()
        values[0]['lifecycle'] = dict(mode='transfer',previous_owner='old-owner',transfer_ref='fixture-transfer')
        values[1]['transfer'] = dict(previous_owner='old-owner',ref='fixture-transfer',stopped=True,confirmed=True)
        values[1]['continuation'] = continuation_proof(values[0]['identity'])
        values[2]['request_sha256'] = fingerprint(values[0])
        self.assertRejected(values, 'unexpected_lifecycle_evidence')

    def test_transfer_rejects_any_active_writer(self):
        values = continuation_specimen()
        values[0]['lifecycle'] = dict(mode='transfer',previous_owner='old-owner',transfer_ref='fixture-transfer')
        values[1]['continuation'] = None
        values[2]['continuation_binding'] = None
        values[1]['transfer'] = dict(previous_owner='old-owner',ref='fixture-transfer',stopped=True,confirmed=True)
        values[2]['request_sha256'] = fingerprint(values[0])
        self.assertRejected(values, 'competing_writer')


if __name__ == '__main__':
    unittest.main()
