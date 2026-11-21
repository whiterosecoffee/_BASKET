"""Entirely fabricated fixtures; no source, command or receipt is executed."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from .core import criterion_digest, digest, evaluate, persist, subject_digest
from .synthetic_adapter import FIELDS, SCHEMA, evaluate_synthetic, load_json, normalize

REVISION = 'a' * 40


def fixture(accepted=False):
    state = json.loads(Path(__file__).with_name('objectives-status.example.json').read_text())
    state['objectives'] = state['objectives'][:1]
    node = state['objectives'][0]
    node.update(status='accepted' if accepted else 'pending', artifact_revisions=[REVISION], evidence=['test-1', 'accept-1'])
    node['acceptance'][0]['evidence'] = ['accept-1']
    subject = subject_digest(state)
    sources = [dict(id='fixture-source', identity='synthetic://review-fixture', revision='b' * 40)]
    pins = dict(subject_digest=subject, revision=REVISION, sources=deepcopy(sources))
    common = dict(source_id='fixture-source', subject_digest=subject, revision=REVISION, observed_at=100)
    values = dict(state['claim'], online=True, single_writer=True, active=False, approval_pending=False,
                  handoff_requested=False, checkpoint_due=False)
    observations = [dict(common, id='observe-' + field, field=field, availability='available', value=values[field]) for field in sorted(FIELDS)]
    receipts = [
        dict(common, id='test-1', kind='test', payload=dict(objective='handoff', command='synthetic test description; never executed', executed=True,
             result='pass', tests=1, failures=0, errors=0, skipped=0)),
        dict(common, id='accept-1', kind='acceptance', payload=dict(objective='handoff', criterion='A1',
             criterion_digest=criterion_digest(node['acceptance'][0]), result='pass', reviewer='synthetic-reviewer', artifact='synthetic://artifact')),
    ]
    envelope = dict(schema=SCHEMA, mode='synthetic', wake_id='synthetic-wake', subject_digest=subject,
                    revision=REVISION, sources=sources, observations=observations, receipts=receipts)
    return state, envelope, pins


class SyntheticAdapterTests(unittest.TestCase):
    def test_normalization_replay_provenance_and_no_mutation(self):
        state, envelope, pins = fixture()
        before = deepcopy((state, envelope, pins))
        result = evaluate_synthetic(state, envelope, pins, now=100)
        self.assertEqual(result, evaluate_synthetic(state, envelope, pins, now=100))
        self.assertEqual(result['simulated_decision']['action'], 'continue')
        self.assertFalse(result['execution_authorized'])
        self.assertFalse(result['evidence_truth_verified'])
        receipt = result['receipts']['accept-1']
        self.assertEqual(receipt['source'], 'synthetic://review-fixture')
        self.assertEqual(receipt['subject_digest'], subject_digest(state))
        self.assertEqual(receipt['revision'], REVISION)
        self.assertEqual(receipt['observed_at'], 100)
        self.assertEqual((state, envelope, pins), before)
        result['observation']['scope'].append('mutated-output-only')
        self.assertEqual((state, envelope, pins), before)

    def test_synthetic_acceptance_is_not_real_acceptance(self):
        result = evaluate_synthetic(*fixture(accepted=True), now=100)
        self.assertEqual(result['simulated_decision']['action'], 'no-change')
        self.assertEqual(result['simulated_decision']['acceptance'], 'not_established')
        self.assertFalse(result['evidence_truth_verified'])

    def test_unknown_and_unavailable_are_not_false(self):
        for availability in ('unknown', 'unavailable'):
            state, envelope, pins = fixture()
            row = next(r for r in envelope['observations'] if r['field'] == 'online')
            row.update(availability=availability, value=None)
            packet = evaluate_synthetic(state, envelope, pins, now=100)
            self.assertEqual(packet['availability']['online'], availability)
            self.assertIsNone(packet['observation'])
            self.assertEqual(packet['receipts'], {})
            self.assertEqual(packet['simulated_decision']['action'], 'blocked')
        row.update(availability='available', value=False)
        packet = evaluate_synthetic(state, envelope, pins, now=100)
        self.assertIs(packet['observation']['online'], False)
        self.assertEqual(packet['simulated_decision']['reason'], 'workstation offline; park')

    def test_missing_required_records_and_fields(self):
        for key in fixture()[1]:
            state, envelope, pins = fixture()
            del envelope[key]
            with self.subTest(key=key), self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)
        for array in ('observations', 'receipts', 'sources'):
            state, envelope, pins = fixture()
            envelope[array].pop()
            with self.subTest(array=array), self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)

    def test_duplicate_ids_fields_and_sources(self):
        for array in ('observations', 'receipts', 'sources'):
            for fresh_id in (False, True):
                state, envelope, pins = fixture()
                extra = deepcopy(envelope[array][0])
                if fresh_id:
                    extra['id'] = 'different-id'
                envelope[array].append(extra)
                with self.subTest(array=array, fresh_id=fresh_id), self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)

    def test_freshness_rejects_stale_future_unknown_and_bad_clocks(self):
        for array in ('observations', 'receipts'):
            for stamp in (-201, 101, None, True, '100', float('nan'), float('inf')):
                state, envelope, pins = fixture()
                envelope[array][0]['observed_at'] = stamp
                with self.subTest(array=array, stamp=stamp), self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)
        for now in (None, True, '100', float('inf')):
            with self.assertRaises(ValueError): normalize(*fixture(),now=now)
        for max_age in (0, -1, True, float('nan')):
            with self.assertRaises(ValueError): normalize(*fixture(),now=100,max_age=max_age)

    def test_subject_revision_and_source_mismatch(self):
        for location in ('envelope', 'observations', 'receipts', 'pins'):
            for key in ('revision', 'subject_digest'):
                state, envelope, pins = fixture()
                target = pins if location == 'pins' else envelope if location == 'envelope' else envelope[location][0]
                target[key] = 'c' * (40 if key == 'revision' else 64)
                with self.subTest(location=location,key=key), self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)
        for key in ('identity', 'revision'):
            state, envelope, pins = fixture()
            envelope['sources'][0][key] = 'synthetic://different'
            with self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)

    def test_malformed_or_unsupported_observations(self):
        for value in ('true', 'false', 0, 1, None, [], {}, [True]):
            state, envelope, pins = fixture()
            row = next(r for r in envelope['observations'] if r['field'] == 'online')
            row['value'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)
        for change in ({'field':'dispatch_now'}, {'source_id':'unknown'}, {'availability':'inferred'}, {'extra':True}):
            state, envelope, pins = fixture()
            envelope['observations'][0].update(change)
            with self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)
        state, envelope, pins = fixture()
        next(r for r in envelope['observations'] if r['field'] == 'host')['value'] = 'wrong-host'
        with self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)

    def test_test_receipts_require_executed_pass_without_skips(self):
        for change in ({'executed':1}, {'executed':False}, {'result':'pending'}, {'tests':0}, {'tests':True}, {'failures':1}, {'errors':1}, {'skipped':1}):
            state, envelope, pins = fixture()
            envelope['receipts'][0]['payload'].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)

    def test_acceptance_is_bound_and_unsupported_receipts_reject(self):
        for change in ({'criterion':'A2'}, {'criterion_digest':'0'*64}, {'objective':'other'}, {'result':'fail'}, {'reviewer':''}, {'artifact':''}):
            state, envelope, pins = fixture(accepted=True)
            envelope['receipts'][1]['payload'].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)
        for kind in ('session-start', 'dimension', 'dispatch', 'unknown'):
            state, envelope, pins = fixture()
            envelope['receipts'][1]['kind'] = kind
            with self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)

    def test_rejection_does_not_mutate_inputs(self):
        state, envelope, pins = fixture(accepted=True)
        envelope['receipts'][1]['revision'] = 'f'*40
        before = deepcopy((state,envelope,pins))
        with self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)
        self.assertEqual((state,envelope,pins),before)

    def test_strict_json_decoding(self):
        for text in ('{"online":true,"online":false}', '{"number":NaN}', '{"number":Infinity}'):
            with self.assertRaises(ValueError): load_json(text)
        self.assertEqual(load_json(json.dumps(fixture()[1])),fixture()[1])

    def test_oldest_receipt_bounds_packet_freshness(self):
        state, envelope, pins = fixture()
        envelope['receipts'][0]['observed_at'] = -200
        packet = normalize(state,envelope,pins,now=100)
        self.assertEqual(packet['observation']['verified_at'], -200)
        self.assertEqual(evaluate(state,packet['observation'],packet['receipts'],now=101)['action'],'blocked')
        with self.assertRaises(ValueError): normalize(state,envelope,pins,now=101)

    def test_pinned_source_cannot_use_mutable_revision_alias(self):
        state, envelope, pins = fixture()
        for sources in (envelope['sources'],pins['sources']):
            sources[0]['revision'] = 'main'
        with self.assertRaises(ValueError): normalize(state,envelope,pins,now=100)

    def test_adapter_replay_with_existing_atomic_writer(self):
        state, envelope, pins = fixture()
        packet = normalize(state,envelope,pins,now=100)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'status.json'
            path.write_text(json.dumps(state))
            def update(s):
                s['revision'] += 1
                return s
            saved = persist(path,digest(state),update,packet['receipts'],packet['observation'],now=100)
            replay = evaluate_synthetic(saved,envelope,pins,now=100)
            self.assertEqual(replay['simulated_decision']['action'],'no-change')
            before = path.read_bytes()
            persist(path,digest(saved),lambda s:self.fail('duplicate callback'),replay['receipts'],replay['observation'],now=100)
            self.assertEqual(path.read_bytes(),before)
