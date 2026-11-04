import unittest
from orchestration.mrie_watch.watch import canonical_bytes, reconcile


class Dispatcher:
    from datetime import datetime
    @staticmethod
    def instant(value):
        from datetime import datetime
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None:
            raise ValueError('Timezone required')
        return result
    @staticmethod
    def compile_plan(entities, coverage, as_of, candidates):
        return {'canonical_count': len(entities), 'unregistered_candidates': sorted(set(candidates)-set(entities))}


class WatchTests(unittest.TestCase):
    def run_watch(self, proposals=(), previous=(), scans=()):
        return reconcile(Dispatcher, {'count': 1, 'records': [{'symbol': 'NVDA', 'instrument_type': 'equity_or_depositary_receipt'}]},
                         {'NVDA': {'id': 'NVDA', 'type': 'public_equity'}}, {},
                         '2026-11-04T06:00:00Z', scans, proposals, previous)

    def event(self, **changes):
        p = dict(event_id='event1', revision='1', content_hash='a'*64,
                 source_url='https://www.sec.gov/Archives/example',
                 available_at='2026-11-02T12:00:00Z', published_at=None,
                 effective_at=None, ingested_at='2026-11-04T05:00:00Z',
                 classification='issuer_claim', status='signed_definitive',
                 affected_tickers=['NVDA'], material=True, backfill=False)
        p.update(changes)
        return p

    def test_deterministic_no_mutations(self):
        self.assertEqual(canonical_bytes(self.run_watch()), canonical_bytes(self.run_watch()))
        self.assertFalse(self.run_watch()['checkpoint_advanced'])
        self.assertFalse(self.run_watch()['operational_ready'])

    def test_missing_source_not_no_news(self):
        self.assertEqual(self.run_watch()['scan_state'], 'incomplete')

    def test_owner_accepted_duplicate(self):
        event = self.event()
        d = self.run_watch([event], [event])['decisions'][0]
        self.assertEqual(d['state'], 'duplicate')
        self.assertFalse(d['notify'])

    def test_revision_requires_new_revision_identity(self):
        d = self.run_watch([self.event(content_hash='b'*64)], [self.event()])['decisions'][0]
        self.assertEqual(d['state'], 'conflicting_revision_review')

    def test_backfill_not_fresh(self):
        d = self.run_watch([self.event(backfill=True)])['decisions'][0]
        self.assertEqual(d['state'], 'backfill_proposal')
        self.assertFalse(d['notification_candidate'])

    def test_future_evidence_rejected(self):
        d = self.run_watch([self.event(available_at='2027-01-01T00:00:00Z')])['decisions'][0]
        self.assertEqual(d['error'], 'POINT_IN_TIME_VIOLATION')

    def test_unregistered_issuer_not_admitted(self):
        d = self.run_watch([self.event(affected_tickers=['LITE'])])['decisions'][0]
        self.assertEqual(d['state'], 'identity_review_required')

    def test_failed_scan_suppresses_candidate(self):
        d = self.run_watch([self.event()], scans=[{'source_id':'sec', 'status':'failure'}])['decisions'][0]
        self.assertFalse(d['notification_candidate'])

    def test_duplicate_scope_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_SCOPE_MANIFEST'):
            reconcile(Dispatcher, {'count':2,'records':[{'symbol':'X'},{'symbol':'X'}]}, {}, {}, '2026-11-04T06:00:00Z', [], [])
