"""B01 independent acceptance for the pure #180 MRIE review adapter.

Fixtures are controlled synthetic metadata. A dispatcher double is injected;
these tests do not establish a live scan, source verification or delivery.
"""
import copy
import datetime as dt
from pathlib import Path
import tempfile
import unittest

from orchestration.mrie_watch.watch import canonical_bytes, load_dispatcher, reconcile

AS_OF = '2026-11-04T12:00:00Z'


class DispatcherDouble:
    @staticmethod
    def instant(value):
        if not isinstance(value, str):
            raise ValueError('Timestamp string required')
        result = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None:
            raise ValueError('Timezone required')
        return result.astimezone(dt.timezone.utc)

    @staticmethod
    def compile_plan(entities, coverage, as_of, candidates=()):
        return {'schema': 'SYNTHETIC_DISPATCHER_RESULT', 'canonical_count': len(entities),
                'unregistered_candidates': sorted(set(candidates) - set(entities)),
                'coverage': copy.deepcopy(coverage), 'live_verified': False}


def proposal(**changes):
    row = {'event_id': 'synthetic-nvda-event', 'revision': 'r1',
           'content_hash': 'a' * 64,
           'source_url': 'https://nvidianews.nvidia.com/news/synthetic-test-only',
           'available_at': '2026-11-03T10:00:00Z',
           'published_at': '2026-11-03T10:00:00Z',
           'effective_at': '2026-11-03T00:00:00Z',
           'ingested_at': '2026-11-03T11:00:00Z',
           'classification': 'issuer_claim', 'status': 'announced',
           'affected_tickers': ['NVDA'], 'material': True, 'backfill': False}
    row.update(changes)
    return row


class MrieWatchIndependentAcceptance(unittest.TestCase):
    def setUp(self):
        self.manifest = {'count': 2, 'records': [
            {'symbol': 'NVDA', 'instrument_type': 'equity_or_depositary_receipt'},
            {'symbol': 'SPY', 'instrument_type': 'index'}]}
        self.entities = {'NVDA': {'id': 'NVDA', 'type': 'public_equity'}}
        self.scans = [{'source_id': 'synthetic-official-nvda', 'status': 'success'}]

    def run_review(self, proposals=(), scans=None, previous=()):
        return reconcile(DispatcherDouble, self.manifest, self.entities, {}, AS_OF,
                         self.scans if scans is None else scans, list(proposals), previous)

    def test_missing_scans_are_incomplete_not_no_news(self):
        r = self.run_review(scans=[])
        self.assertEqual(r['scan_state'], 'incomplete')
        self.assertIn('SOURCE_COVERAGE_UNKNOWN', [e['code'] for e in r['errors']])
        self.assertFalse(r['operational_ready'])

    def test_source_outage_preserves_gap_and_suppresses_candidate(self):
        for state in ('failed', 'partial', 'unknown', 'not_run'):
            r = self.run_review([proposal()], scans=[{'source_id': 'synthetic-official-nvda', 'status': state}])
            self.assertEqual(r['scan_state'], 'incomplete')
            self.assertTrue(r['errors'])
            self.assertFalse(r['decisions'][0]['notification_candidate'])

    def test_success_without_source_identity_is_not_complete(self):
        r = self.run_review([proposal()], scans=[{'status': 'success'}])
        self.assertEqual(r['scan_state'], 'incomplete')
        self.assertFalse(r['decisions'][0]['notification_candidate'])

    def test_no_delivery_or_persistence_claim_from_proposal(self):
        r = self.run_review([proposal()])
        self.assertFalse(r['operational_ready'])
        self.assertFalse(r['checkpoint_advanced'])
        self.assertEqual(r['library_status'], 'NOT_VERIFIED')
        self.assertFalse(r['coverage']['live_verified'])
        decision = r['decisions'][0]
        self.assertFalse(decision['notify'])
        self.assertEqual(decision['delivery_status'], 'NOT_SENT')
        self.assertEqual(decision['persistence_status'], 'NOT_WRITTEN')
        self.assertTrue(any('B03' in gate for gate in r['gates']))

    def test_input_snapshots_unchanged_and_repeat_deterministic(self):
        rows = [proposal()]
        before = copy.deepcopy((self.manifest, self.entities, self.scans, rows))
        a = self.run_review(rows)
        b = self.run_review(rows)
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))
        self.assertEqual((self.manifest, self.entities, self.scans, rows), before)

    def test_identical_batch_item_is_deduplicated(self):
        r = self.run_review([proposal(), proposal()])
        self.assertEqual([d['state'] for d in r['decisions']], ['new_event_proposal', 'duplicate'])
        self.assertEqual(sum(d['notification_candidate'] for d in r['decisions']), 1)

    def test_accepted_payload_is_duplicate_even_if_new_revision_label(self):
        baseline = [{'event_id': 'synthetic-nvda-event', 'revision': 'r1', 'content_hash': 'a' * 64}]
        r = self.run_review([proposal(revision='r2')], previous=baseline)
        self.assertEqual(r['decisions'][0]['state'], 'duplicate')
        self.assertFalse(r['decisions'][0]['notification_candidate'])

    def test_changed_accepted_payload_requires_new_revision(self):
        baseline = [{'event_id': 'synthetic-nvda-event', 'revision': 'r1', 'content_hash': 'a' * 64}]
        conflict = self.run_review([proposal(content_hash='b' * 64)], previous=baseline)
        self.assertEqual(conflict['decisions'][0]['state'], 'conflicting_revision_review')
        self.assertFalse(conflict['decisions'][0]['notification_candidate'])
        revised = self.run_review([proposal(revision='r2', content_hash='b' * 64)], previous=baseline)
        self.assertEqual(revised['decisions'][0]['state'], 'revision_proposal')

    def test_conflicting_batch_never_leaves_an_actionable_first_row(self):
        r = self.run_review([proposal(), proposal(content_hash='b' * 64)])
        self.assertFalse(any(d.get('notification_candidate', False) for d in r['decisions']))
        self.assertTrue(any(d['state'] == 'conflicting_revision_review' for d in r['decisions']))

    def test_declared_backfill_is_not_fresh_alert(self):
        r = self.run_review([proposal(backfill=True, published_at='2024-01-01T00:00:00Z',
                                      effective_at='2023-12-31T00:00:00Z')])
        self.assertEqual(r['decisions'][0]['state'], 'backfill_proposal')
        self.assertFalse(r['decisions'][0]['notification_candidate'])

    def test_unregistered_issuer_is_review_not_admission(self):
        r = self.run_review([proposal(affected_tickers=['NVDA', 'UNKNOWN'])])
        self.assertEqual(r['decisions'][0]['state'], 'identity_review_required')
        self.assertFalse(r['decisions'][0]['notification_candidate'])
        self.assertNotIn('UNKNOWN', self.entities)

    def test_uncertain_classifications_require_review(self):
        for classification in ('inference', 'scenario', 'unknown'):
            r = self.run_review([proposal(classification=classification)])
            self.assertEqual(r['decisions'][0]['state'], 'review_required')
            self.assertFalse(r['decisions'][0]['notification_candidate'])

    def test_point_in_time_failures_require_review(self):
        for changes in ({'available_at': '2027-01-01T00:00:00Z'},
                        {'ingested_at': '2026-11-02T00:00:00Z'},
                        {'ingested_at': '2027-01-01T00:00:00Z'},
                        {'available_at': '2026-11-03T10:00:00'}):
            r = self.run_review([proposal(**changes)])
            self.assertEqual(r['decisions'][0]['state'], 'review_required')

    def test_malformed_evidence_is_review_not_unhandled_exception(self):
        for changes in ({'source_url': 123}, {'source_url': None}, {'revision': 2},
                        {'content_hash': 'bad'}, {'material': 'yes'}, {'affected_tickers': []}):
            r = self.run_review([proposal(**changes)])
            self.assertEqual(r['decisions'][0]['state'], 'review_required')

    def test_nonissuer_scope_is_explicitly_excluded(self):
        r = self.run_review()
        scope = {x['symbol']: x for x in r['scope']}
        self.assertEqual(scope['SPY']['state'], 'excluded_nonissuer')

    def test_future_publication_is_not_current_evidence(self):
        r = self.run_review([proposal(published_at='2027-01-01T00:00:00Z')])
        self.assertEqual(r['decisions'][0]['state'], 'review_required')
        self.assertFalse(r['decisions'][0].get('notification_candidate', False))
        # Announced future effectiveness is a distinct, valid economic timestamp.
        future_event = self.run_review([proposal(effective_at='2027-01-01T00:00:00Z')])
        self.assertEqual(future_event['decisions'][0]['state'], 'new_event_proposal')

    def test_nonstring_event_identity_is_quarantined_without_crash(self):
        for identity in (123, ['bad-id'], {'bad': 'id'}):
            r = self.run_review([proposal(event_id=identity)])
            self.assertEqual(r['decisions'][0]['state'], 'review_required')
            self.assertFalse(r['decisions'][0].get('notification_candidate', False))

    def test_backfill_classification_must_be_explicit(self):
        row = proposal()
        del row['backfill']
        r = self.run_review([row])
        self.assertEqual(r['decisions'][0]['state'], 'review_required')
        self.assertFalse(r['decisions'][0].get('notification_candidate', False))

    def test_unsupported_dispatch_symbol_is_preserved_without_admission(self):
        self.manifest['records'].append({'symbol': 'CL=F', 'instrument_type': 'futures_contract'})
        self.manifest['count'] += 1
        r = self.run_review()
        self.assertIn('CL=F', r['unsupported_dispatch_symbols'])
        self.assertEqual(next(s for s in r['scope'] if s['symbol']=='CL=F')['state'], 'excluded_nonissuer')
        self.assertNotIn('CL=F', r['coverage']['unregistered_candidates'])

    def test_manifest_duplicate_identity_is_rejected(self):
        self.manifest['records'].append(copy.deepcopy(self.manifest['records'][0]))
        self.manifest['count'] += 1
        with self.assertRaises(ValueError):
            self.run_review()

    def test_conflicting_accepted_baselines_are_rejected(self):
        old = {'event_id': 'synthetic-nvda-event', 'revision': 'r1', 'content_hash': 'a' * 64}
        with self.assertRaises(ValueError):
            self.run_review([proposal()], previous=[old, dict(old, content_hash='b' * 64)])

    def test_changed_dispatcher_is_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'changed_dispatcher.py'
            sentinel = Path(tmp) / 'executed'
            path.write_text('from pathlib import Path\nPath(' + repr(str(sentinel)) + ').write_text("bad")\n')
            with self.assertRaises(ValueError):
                load_dispatcher(path)
            self.assertFalse(sentinel.exists())


if __name__ == '__main__':
    unittest.main()
