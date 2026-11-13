import copy
import unittest
from pathlib import Path
from unittest.mock import patch
from orchestration.clean_templates import lifecycle as lc, temporal as tp


class TemporalTemplateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = lc.read('temporal.examples.json')
        self.select('historical-as-of')
        self.now = self.fixture['evaluation_time']

    def select(self, name):
        self.value = copy.deepcopy(self.fixture['examples'][name])
        self.expected = copy.deepcopy(self.value['request'])

    def check(self):
        result = tp.evaluate(self.value, expected_request=self.expected, now=self.now)
        self.assertFalse(result['execution_authorized'])
        return result

    def reject(self, error=None):
        result = self.check()
        self.assertFalse(result['valid'], result)
        self.assertFalse(result['acceptance_current'])
        if error:
            self.assertIn(error, result['errors'])
        return result

    def rebind(self, acceptance=True):
        content = self.value['generation']['content']
        self.value['generation']['artifact']['sha256'] = tp.digest(content)
        self.value['request']['input_revision'] = tp.digest(content)
        self.expected = copy.deepcopy(self.value['request'])
        if acceptance:
            self.value['acceptance'] = {'request_sha256': tp.digest(self.expected),
                'generation_sha256': tp.digest(content), 'revision_view_sha256': tp.digest([])}

    def correction(self, available='2020-01-03T12:00:00Z', status='resolved'):
        return {'supersedes_generation': 'history-g1', 'replacement_generation': 'history-g2',
                'available_at': available, 'status': status,
                'evidence': {'ref': 'fixture://correction', 'sha256': '7'*64}}

    def test_all_explicit_options_pass(self):
        for name in self.fixture['examples']:
            with self.subTest(name=name):
                self.select(name)
                self.assertTrue(self.check()['valid'], self.check()['errors'])

    def test_historical_old_data_remains_valid_as_clock_advances(self):
        for clock in ('2030-01-01T00:00:00Z', '2040-01-01T00:00:00Z', '2099-01-01T00:00:00Z'):
            self.now = clock
            result = self.check()
            self.assertTrue(result['valid'], result['errors'])
            self.assertTrue(result['acceptance_current'])
            self.assertTrue(result['cache_refresh_due'])
            self.assertIsNone(result['owner_refresh_request'])

    def test_missing_historical_range_rejects(self):
        self.value['generation']['content']['coverage'][0]['start'] = '2020-01-02T15:30:00Z'
        self.rebind()
        self.reject('MISSING_HISTORICAL_RANGE')

    def test_missing_provenance_rejects(self):
        del self.value['generation']['content']['provenance']
        self.reject()

    def test_unknown_coverage_is_not_no_trade(self):
        self.value['generation']['content']['coverage'][0]['status'] = 'unknown'
        self.rebind()
        self.reject('UNKNOWN_COVERAGE')
        self.select('historical-no-trade')
        self.assertTrue(self.check()['valid'])

    def test_unresolved_conflicting_revision_rejects(self):
        self.value['corrections'] = [self.correction(status='conflicting')]
        self.reject('CONFLICTING_REVISION')

    def test_visible_correction_invalidates_old_generation_and_acceptance(self):
        self.value['corrections'] = [self.correction()]
        result = self.reject('PINNED_GENERATION_SUPERSEDED')
        self.assertIn('STALE_ACCEPTANCE', result['errors'])

    def test_post_cutoff_correction_does_not_leak_into_as_of_view(self):
        self.value['corrections'] = [self.correction(available='2021-01-01T00:00:00Z')]
        result = self.check()
        self.assertTrue(result['valid'], result['errors'])
        self.assertTrue(result['acceptance_current'])
        self.assertNotIn('replacement_generation', result)

    def test_strict_policy_invalidates_on_post_cutoff_known_correction(self):
        self.select('historical-strict-correction')
        self.value['corrections'] = [self.correction(available='2021-01-01T00:00:00Z')]
        self.reject('PINNED_GENERATION_SUPERSEDED')

    def test_corrected_generation_requires_new_acceptance(self):
        c = self.value['generation']['content']
        c.update(generation_id='history-g2', revision_id='revision-2')
        self.value['request']['historical']['pinned_generation'] = 'history-g2'
        self.rebind(acceptance=False)
        self.reject('STALE_ACCEPTANCE')
        self.rebind()
        self.assertTrue(self.check()['valid'])

    def test_forward_looking_revision_rejects(self):
        self.value['generation']['content']['available_at'] = '2020-01-05T00:00:00Z'
        self.rebind()
        self.reject('REVISION_AFTER_AS_OF')

    def test_as_of_cutoff_is_bound_to_expected_request(self):
        self.value['request']['historical']['as_of'] = '2020-02-01T00:00:00Z'
        self.value['acceptance']['request_sha256'] = tp.digest(self.value['request'])
        self.reject('REQUEST_OR_AS_OF_CHANGED')

    def test_session_and_basis_mismatches_reject(self):
        for field, code in [('session', 'SESSION_MISMATCH'), ('adjustment_basis', 'ADJUSTMENT_BASIS_MISMATCH')]:
            self.select('historical-as-of')
            self.value['generation']['content'][field] = 'different'
            self.rebind()
            self.reject(code)

    def test_entitlement_not_bypassed_by_historical_mode(self):
        self.value['entitlement']['granted'] = False
        self.reject('ENTITLEMENT_REQUIRED')
        self.value['entitlement']['granted'] = True
        self.value['entitlement']['allowed_purposes'] = ['current']
        self.reject('ENTITLEMENT_REQUIRED')

    def test_historical_integrity_tampering_rejects(self):
        self.value['generation']['content']['revision_id'] = 'tampered'
        self.reject('GENERATION_INTEGRITY_MISMATCH')

    def test_current_stale_watermark_requests_only_bounded_owner_refresh(self):
        self.select('current')
        self.now = '2030-01-01T00:03:00Z'
        result = self.reject('LATEST_WATERMARK_STALE')
        self.assertEqual(result['owner_refresh_request']['owner'], '_FETCH')
        self.assertFalse(result['owner_refresh_request']['execution_authorized'])
        self.value['refresh_attempts_used'] = 1
        self.assertIsNone(self.check()['owner_refresh_request'])
        self.value['refresh_attempts_used'] = 0
        self.now = '2030-01-01T00:10:00Z'
        self.assertIsNone(self.check()['owner_refresh_request'])

    def test_source_observation_age_is_separate_from_retrieval(self):
        self.select('current')
        self.value['request']['current']['max_observation_age_seconds'] = 30
        self.value['observation']['retrieved_at'] = '2030-01-01T00:01:00Z'
        self.now = '2030-01-01T00:01:00Z'
        self.rebind()
        self.reject('SOURCE_OBSERVATION_STALE')

    def test_current_last_successful_generation_must_match(self):
        self.select('current')
        self.value['observation']['last_successful_generation'] = 'other'
        self.reject('LAST_SUCCESSFUL_GENERATION_MISMATCH')

    def test_policy_not_inferred_from_event_dates(self):
        self.value['request']['purpose'] = 'current'
        self.expected = copy.deepcopy(self.value['request'])
        self.reject('EXPLICIT_PURPOSE_POLICY_REQUIRED')

    def test_repeat_deterministic_nonmutating_and_lowercase_clock(self):
        before = copy.deepcopy((self.value, self.expected))
        result = self.check()
        self.assertEqual(result, self.check())
        self.now = self.now.lower()
        self.assertEqual(result, self.check())
        self.assertEqual((self.value, self.expected), before)

    def test_no_archive_network_dispatch_or_write(self):
        original = Path.open
        def guarded(path, mode='r', *args, **kwargs):
            self.assertEqual(path, lc.ROOT / 'lifecycle.schema.json')
            self.assertEqual(mode, 'r')
            return original(path, mode, *args, **kwargs)
        with patch.object(Path, 'open', guarded), \
                patch('socket.socket', side_effect=AssertionError('network')), \
                patch('subprocess.run', side_effect=AssertionError('dispatch')):
            self.assertTrue(self.check()['valid'])

    def test_malformed_packets_and_clock_reject(self):
        self.now = 'bad-clock'
        self.reject('INVALID_NOW')
        self.now = self.fixture['evaluation_time']
        for value in (None, [], {}, {'synthetic': True}):
            self.value = value
            self.reject()

    def test_pinned_generation_mismatch_rejects(self):
        self.value['request']['historical']['pinned_generation'] = 'other-generation'
        self.expected = copy.deepcopy(self.value['request'])
        self.reject('PINNED_GENERATION_MISMATCH')

    def test_future_event_or_coverage_cannot_hide_in_historical_generation(self):
        self.value['generation']['content']['coverage'][0]['end'] = '2020-01-05T00:00:00Z'
        self.rebind()
        self.reject('COVERAGE_AFTER_AS_OF')
        self.select('historical-as-of')
        self.value['generation']['content']['event_watermark'] = '2020-01-05T00:00:00Z'
        self.rebind()
        self.reject('REVISION_AFTER_AS_OF')

    def test_integrity_failure_cannot_become_refresh_proposal(self):
        self.select('current')
        self.now = '2030-01-01T00:03:00Z'
        self.value['generation']['content']['revision_id'] = 'tampered'
        self.assertIsNone(self.reject('GENERATION_INTEGRITY_MISMATCH')['owner_refresh_request'])

    def test_current_watermark_requires_known_coverage(self):
        self.select('current')
        self.value['generation']['content']['coverage'][0]['start'] = '2029-12-31T23:59:30Z'
        self.rebind()
        self.reject('LATEST_WATERMARK_NOT_COVERED')
