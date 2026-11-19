import copy
import unittest
from pathlib import Path
from unittest.mock import patch
from orchestration.clean_templates import lifecycle as lc, receiver as rv, temporal as tp


class ReceiverSanitizerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = lc.read('receiver.examples.json')
        self.select('low-risk-historical')
        self.now = self.fixture['evaluation_time']

    def select(self, name):
        self.value = copy.deepcopy(self.fixture['examples'][name])
        self.expected_request = copy.deepcopy(self.value['temporal']['request'])
        self.expected_policy = copy.deepcopy(self.value['policy'])
        self.retained_claims = copy.deepcopy(self.value['claims'])

    def check(self):
        result = rv.evaluate(self.value, expected_request=self.expected_request,
            expected_policy=self.expected_policy, retained_claims=self.retained_claims, now=self.now)
        self.assertFalse(result['execution_authorized'])
        self.assertFalse(result['evidence_authenticated'])
        return result

    def reject(self, error=None):
        result = self.check()
        self.assertFalse(result['valid'], result)
        self.assertFalse(result['consumer_usable'])
        self.assertNotEqual(result['consumer_acceptance'], 'accepted')
        if error:
            self.assertIn(error, result['errors'])
        return result

    def test_bound_receiver_and_risk_examples_pass(self):
        for name in self.fixture['examples']:
            self.select(name)
            result = self.check()
            self.assertTrue(result['valid'], result['errors'])
            self.assertTrue(result['receiver_acknowledged'])
            self.assertTrue(result['consumer_usable'])
            self.assertEqual(result['consumer_acceptance'], 'accepted')
            self.assertEqual(result['state'], 'review')
            self.assertFalse(result['quarantine'])

    def test_dispatch_and_producer_success_without_receiver_do_not_count(self):
        self.value['receiver'] = None
        result = self.reject('MISSING_RECEIVER_ACKNOWLEDGMENT')
        self.assertFalse(result['receiver_acknowledged'])

    def test_receiver_request_artifact_and_policy_bindings_reject_stale(self):
        original = copy.deepcopy(self.value)
        for key in ('request_sha256', 'artifact_sha256', 'policy_sha256'):
            self.value = copy.deepcopy(original)
            self.value['receiver'][key] = '0' * 64
            self.reject('STALE_RECEIVER_BINDING')

    def test_wrong_consumer_or_purpose_receipt_rejects(self):
        self.value['receiver']['consumer'] = 'other-consumer'
        self.reject('RECEIVER_OR_PURPOSE_MISMATCH')
        self.select('low-risk-historical')
        self.value['receiver']['purpose'] = 'current'
        self.reject('RECEIVER_OR_PURPOSE_MISMATCH')

    def test_readback_content_mismatch_is_quarantined(self):
        self.value['receiver']['readback_content']['revision_id'] = 'other-revision'
        self.assertTrue(self.reject('READBACK_NOT_VERIFIED')['quarantine'])

    def test_missing_failed_and_unknown_readback_do_not_pass(self):
        del self.value['receiver']['readback_result']
        self.reject()
        for status in ('fail', 'unknown'):
            self.select('low-risk-historical')
            self.value['receiver']['readback_result'] = status
            result = self.reject('READBACK_NOT_VERIFIED')
            if status == 'unknown':
                self.assertIn('receiver_readback', result['unknowns'])

    def test_readback_acknowledgment_is_not_consumer_acceptance(self):
        for status in ('pending', 'rejected'):
            self.value['receiver']['acceptance'] = status
            result = self.reject('CONSUMER_ACCEPTANCE_PENDING_OR_REJECTED')
            self.assertTrue(result['receiver_acknowledged'])

    def test_producer_artifact_cannot_be_its_own_receiver_receipt(self):
        self.value['receiver']['evidence'] = copy.deepcopy(self.value['temporal']['generation']['artifact'])
        self.reject('RECEIVER_EVIDENCE_MUST_BE_DISTINCT')

    def test_assertion_cannot_be_promoted_to_verified(self):
        self.value['claims'][0]['status'] = 'verified'
        result = self.reject('ASSERTION_PROMOTED_TO_VERIFICATION')
        self.assertIn('CLAIM_PROVENANCE_CHANGED', result['errors'])

    def test_origin_relabel_cannot_replace_retained_claim(self):
        self.value['claims'][0].update(origin='independently_verified_evidence', status='verified')
        self.reject('CLAIM_PROVENANCE_CHANGED')

    def test_producer_observation_cannot_claim_independent_verification(self):
        self.value['claims'][1]['status'] = 'verified'
        self.reject('ASSERTION_PROMOTED_TO_VERIFICATION')

    def test_user_assertion_cannot_pass_mandatory_sanitizer_gate(self):
        self.value['checks'][0]['origin'] = 'user_assertion'
        self.reject('ASSERTION_CANNOT_PASS_SANITIZER_CHECK')

    def test_placement_does_not_establish_current_freshness(self):
        self.select('high-risk-current')
        self.now = '2030-01-01T00:03:00Z'
        self.value['placement']['artifact_present'] = True
        self.reject('temporal: LATEST_WATERMARK_STALE')

    def test_placement_does_not_establish_coverage_or_semantic_validity(self):
        for gate in ('coverage', 'semantic_validity'):
            self.select('high-risk-current')
            next(c for c in self.value['checks'] if c['id'] == gate)['result'] = 'unknown'
            result = self.reject('CHECK_NOT_PASSED:' + gate)
            self.assertIn(gate, result['unknowns'])
            self.assertTrue(result['quarantine'])

    def test_mandatory_integrity_provenance_privacy_never_optional(self):
        for gate in sorted(rv.MANDATORY):
            self.select('low-risk-historical')
            self.value['checks'] = [c for c in self.value['checks'] if c['id'] != gate]
            self.assertTrue(self.reject('MISSING_CHECK:' + gate)['quarantine'])

    def test_high_risk_minimum_cannot_be_omitted_even_in_supplied_policy(self):
        self.select('high-risk-current')
        self.value['policy']['required_domain_checks'] = ['semantic_validity']
        self.expected_policy = copy.deepcopy(self.value['policy'])
        self.reject('RISK_CHECKS_OMITTED')

    def test_missing_high_risk_check_rejects(self):
        self.select('high-risk-current')
        self.value['checks'] = [c for c in self.value['checks'] if c['id'] != 'independent_review']
        self.reject('MISSING_CHECK:independent_review')

    def test_high_risk_independent_review_requires_distinct_origin_and_evidence(self):
        self.select('high-risk-current')
        gate = next(c for c in self.value['checks'] if c['id'] == 'independent_review')
        gate['origin'] = 'producer_observation'
        self.reject('INDEPENDENT_REVIEW_REQUIRED')
        gate['origin'] = 'independently_verified_evidence'
        gate['evidence'] = copy.deepcopy(self.value['checks'][0]['evidence'])
        self.reject('INDEPENDENT_EVIDENCE_MUST_BE_DISTINCT')

    def test_risk_downgrade_rejects_against_expected_policy(self):
        self.select('high-risk-current')
        self.value['policy']['risk'] = 'low'
        self.reject('RISK_POLICY_CHANGED')

    def test_private_destination_cannot_be_relabelled(self):
        self.value['placement'].update(requires_private=False, destination_visibility='public')
        result = self.reject('PRIVATE_DESTINATION_REQUIRED')
        self.assertIn('PRIVACY_POLICY_MISMATCH', result['errors'])

    def test_stale_or_duplicate_sanitizer_checks_reject(self):
        self.value['checks'][0]['artifact_sha256'] = '0' * 64
        self.reject('STALE_SANITIZER_EVIDENCE')
        self.select('low-risk-historical')
        self.value['checks'].append(copy.deepcopy(self.value['checks'][0]))
        self.reject('DUPLICATE_SANITIZER_CHECK')

    def test_known_failed_gate_cannot_be_averaged_into_acceptance(self):
        self.value['checks'][0]['result'] = 'fail'
        result = self.reject('CHECK_NOT_PASSED:' + self.value['checks'][0]['id'])
        self.assertTrue(result['receiver_acknowledged'])
        self.assertTrue(result['quarantine'])

    def test_repeat_preserves_inputs_and_claim_origin(self):
        before = copy.deepcopy((self.value, self.expected_request, self.expected_policy, self.retained_claims))
        result = self.check()
        self.assertEqual(result, self.check())
        result['claims'][0]['origin'] = 'mutated-return'
        self.assertEqual((self.value, self.expected_request, self.expected_policy, self.retained_claims), before)

    def test_historical_receipt_does_not_expire_by_event_age(self):
        self.now = '2099-01-01T00:00:00Z'
        self.assertTrue(self.check()['valid'])

    def test_no_file_readback_network_dispatch_or_write_is_claimed(self):
        original = Path.open
        def guarded(path, mode='r', *args, **kwargs):
            self.assertEqual(path, lc.ROOT / 'lifecycle.schema.json')
            self.assertEqual(mode, 'r')
            return original(path, mode, *args, **kwargs)
        with patch.object(Path, 'open', guarded), \
                patch('socket.socket', side_effect=AssertionError('network')), \
                patch('subprocess.run', side_effect=AssertionError('dispatch')):
            self.assertTrue(self.check()['valid'])

    def test_malformed_packet_and_invalid_clock_reject(self):
        self.now = '2030-02-30T00:00:00Z'
        self.reject('temporal: INVALID_NOW')
        for value in (None, {}, []):
            self.value = value
            self.reject()

    def test_qc_supplement_provider_adjustment_unknown_is_retained_and_blocks_use(self):
        self.select('high-risk-current')
        check = copy.deepcopy(self.value['checks'][0])
        check.update(id='provider_adjustment_verification', result='unknown')
        self.value['checks'].append(check)
        result = self.check()
        self.assertIn('provider_adjustment_verification', result['unknowns'])
        self.assertFalse(result['consumer_usable'])

    def test_qc_supplement_opaque_independent_receipt_without_record_rejects(self):
        self.select('high-risk-current')
        gate = next(c for c in self.value['checks'] if c['id'] == 'independent_review')
        gate['evidence'] = {'ref': 'fixture://no-runner-or-version-record', 'sha256': 'a' * 64}
        self.reject()

    def test_qc_supplement_missing_raw_transform_audit_preservation_rejects(self):
        self.select('high-risk-current')
        self.value.pop('pipeline', None)
        self.reject()

    def rehash_pipeline(self):
        pipeline = self.value['pipeline']
        for stage in ('transform', 'audit'):
            pipeline[stage]['record']['policy_sha256'] = tp.digest(self.value['policy'])
        pipeline['audit']['record']['results'] = [
            {'id': c['id'], 'result': c['result']} for c in self.value['checks']]
        for stage in ('transform', 'audit', 'preservation'):
            pipeline[stage]['artifact']['sha256'] = tp.digest(pipeline[stage]['record'])
        for check in self.value['checks']:
            check.update(policy_sha256=tp.digest(self.value['policy']), pipeline_sha256=tp.digest(pipeline))
            if check['id'] == 'independent_review':
                check['evidence'] = copy.deepcopy(pipeline['audit']['artifact'])
        self.value['receiver'].update(policy_sha256=tp.digest(self.value['policy']), pipeline_sha256=tp.digest(pipeline))

    def add_adjustment_unknown(self):
        check = copy.deepcopy(self.value['checks'][0])
        check.update(id='provider_adjustment_verification', result='unknown')
        self.value['checks'].append(check)
        self.rehash_pipeline()

    def test_exact_raw_output_versions_roles_and_preservation_positive(self):
        self.select('high-risk-current')
        p = self.value['pipeline']
        self.assertNotEqual(p['raw_input']['artifact']['sha256'], p['normalized_output']['sha256'])
        self.assertNotEqual(p['transform']['record']['actor'], p['audit']['record']['actor'])
        result = self.check()
        self.assertTrue(result['valid'], result['errors'])
        self.assertEqual(result['use_status'], 'qualified')
        self.assertEqual(result['unknowns'], [])

    def test_missing_each_pipeline_record_is_mandatory(self):
        original = copy.deepcopy(self.value)
        for stage in ('raw_input', 'normalized_output', 'transform', 'audit', 'preservation'):
            self.value = copy.deepcopy(original)
            del self.value['pipeline'][stage]
            self.reject()

    def test_missing_schema_sanitizer_runner_configuration_version_rejects(self):
        original = copy.deepcopy(self.value)
        for key in self.value['policy']['processing_contract']:
            self.value = copy.deepcopy(original)
            del self.value['policy']['processing_contract'][key]
            self.reject()

    def test_version_or_exact_assessed_scope_mismatch_rejects_even_rehashed(self):
        original = copy.deepcopy(self.value)
        for stage in ('transform', 'audit'):
            for key in ('schema_version', 'sanitizer_revision', 'runner_version', 'configuration_sha256'):
                with self.subTest(stage=stage, key=key):
                    self.value = copy.deepcopy(original)
                    old = self.value['pipeline'][stage]['record'][key]
                    self.value['pipeline'][stage]['record'][key] = 'b' * len(old)
                    self.rehash_pipeline()
                    self.reject('TRANSFORM_AUDIT_LINEAGE_OR_VERSION_MISMATCH')
        self.value = original
        self.value['pipeline']['audit']['record']['scope']['coverage_sha256'] = '0' * 64
        self.rehash_pipeline()
        self.reject('TRANSFORM_AUDIT_LINEAGE_OR_VERSION_MISMATCH')

    def test_raw_input_tampering_and_wrong_transform_input_reject(self):
        self.value['pipeline']['raw_input']['content'] += 'tampered'
        self.reject('RAW_INPUT_INTEGRITY_MISMATCH')
        self.select('low-risk-historical')
        self.value['pipeline']['transform']['record']['raw_input_sha256'] = '0' * 64
        self.rehash_pipeline()
        self.reject('TRANSFORM_AUDIT_LINEAGE_OR_VERSION_MISMATCH')

    def test_normalized_output_binding_and_record_hash_reject(self):
        self.value['pipeline']['normalized_output']['sha256'] = '0' * 64
        self.reject('RAW_NORMALIZED_ARTIFACT_BINDING_MISMATCH')
        self.select('low-risk-historical')
        self.value['pipeline']['audit']['artifact']['sha256'] = '0' * 64
        self.reject('PIPELINE_RECORD_HASH_MISMATCH')

    def test_standardizer_cannot_declare_itself_independent_auditor(self):
        self.value['pipeline']['audit']['record']['actor'] = self.value['pipeline']['transform']['record']['actor']
        self.rehash_pipeline()
        self.reject('STANDARDIZER_CANNOT_BE_INDEPENDENT_AUDITOR')

    def test_original_change_or_same_output_destination_rejects(self):
        self.value['pipeline']['preservation']['record']['after_sha256'] = '0' * 64
        self.rehash_pipeline()
        self.reject('ORIGINALS_PRESERVATION_MISMATCH')
        self.select('low-risk-historical')
        record = self.value['pipeline']['preservation']['record']
        record['normalized_destination'] = record['original_destination']
        self.rehash_pipeline()
        self.reject('ORIGINALS_PRESERVATION_MISMATCH')

    def test_all_unknowns_retained_with_complete_audit_binding(self):
        self.add_adjustment_unknown()
        result = self.reject('UNRESOLVED_UNKNOWN:provider_adjustment_verification')
        self.assertEqual(result['unknowns'], ['provider_adjustment_verification'])
        self.assertTrue(result['quarantine'])

    def test_optional_unknown_requires_explicit_purpose_specific_conditional_policy(self):
        self.value['policy']['allowed_unknowns'] = ['provider_adjustment_verification']
        self.expected_policy = copy.deepcopy(self.value['policy'])
        self.add_adjustment_unknown()
        result = self.check()
        self.assertTrue(result['valid'], result['errors'])
        self.assertEqual(result['use_status'], 'conditional')
        self.assertEqual(result['unknowns'], ['provider_adjustment_verification'])
        self.assertFalse(result['consumer_usable'])
        self.assertEqual(result['consumer_acceptance'], 'pending')

    def test_mandatory_unknown_cannot_be_waived_by_conditional_policy(self):
        self.value['policy']['allowed_unknowns'] = ['integrity']
        self.expected_policy = copy.deepcopy(self.value['policy'])
        next(c for c in self.value['checks'] if c['id'] == 'integrity')['result'] = 'unknown'
        self.rehash_pipeline()
        self.reject('UNRESOLVED_UNKNOWN:integrity')

    def test_optional_failed_check_cannot_disappear(self):
        self.add_adjustment_unknown()
        self.value['checks'][-1]['result'] = 'fail'
        self.rehash_pipeline()
        result = self.reject('FAILED_CHECK:provider_adjustment_verification')
        self.assertIn('provider_adjustment_verification', result['failures'])

    def test_raw_whitespace_is_part_of_exact_original_byte_hash(self):
        self.value['pipeline']['raw_input']['content'] += '\n'
        self.reject('RAW_INPUT_INTEGRITY_MISMATCH')

    def test_auditor_only_unknown_is_retained_even_if_check_list_omits_it(self):
        self.value['pipeline']['audit']['record']['results'].append(
            {'id': 'provider_adjustment_verification', 'result': 'unknown'})
        result = self.reject('AUDIT_RESULTS_MISMATCH')
        self.assertIn('provider_adjustment_verification', result['unknowns'])
