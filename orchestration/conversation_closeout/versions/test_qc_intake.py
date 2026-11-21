import copy
import hashlib
import json
from pathlib import Path
import unittest
from orchestration.conversation_closeout.versions.qc_intake import (
    QUEUE, digest, enqueue, pending, request_id, validate_request,
    validate_index, validate_receipt, verify_artifacts, reconcile_inventory)


def sample(issue=178):
    task = {'schema': 'basket.worker_task@1', 'task_id': f'B00-{issue}',
            'spark_id': 'B00', 'issue': {'number': issue, 'url': f'https://github.com/whiterosecoffee/_BASKET/issues/{issue}'},
            'branch': {'name': f'work/{issue}-qc', 'base': 'main'},
            'objective': 'Preserve and review closeout evidence',
            'write_paths': ['orchestration/conversation_closeout/versions/**'],
            'acceptance': [{'id': 'A1', 'criterion': 'Source and obligations preserved', 'evidence_class': 'source'}],
            'dependencies': [], 'claimed_at': None, 'state': 'review'}
    artifacts = [{'path': 'orchestration/conversation_closeout/versions/' + path,
                  'revision': 'a' * 40, 'sha256': hashlib.sha256(b'O1: source obligation\nK1: source knowledge\n' if role == 'handoff' else b'example').hexdigest(), 'role': role}
                 for path, role in [('primary.md', 'primary'), ('handoff.md', 'handoff')]]
    value = {'task': task, 'source_pr': 179, 'artifacts': artifacts, 'item_ids': ['O1', 'K1'],
             'review_kind': 'closeout_semantic'}
    value['request_id'] = request_id(value)
    return value


def index(*requests):
    return {'schema': 'basket.closeout_qc_index@1', 'canonical_queue': QUEUE, 'requests': list(requests)}


def source_reader(path, revision):
    return b'O1: source obligation\nK1: source knowledge\n' if path.endswith('handoff.md') else b'example'


def archive_inputs(*requests):
    return {'read_bytes': source_reader, 'source_items': {r['request_id']: {
        'O1': [QUEUE], 'K1': [QUEUE]} for r in requests}}


def receipt(request, outcome='accepted'):
    return {'request_id': request['request_id'], 'reviewer': 'independent test fixture',
            'outcome': outcome, 'item_dispositions': {key: {'state': 'transfer',
                'reason': 'Reviewed; implementation remains with existing owner',
                'destination': QUEUE} for key in request['item_ids']},
            'evidence_urls': ['https://github.com/whiterosecoffee/_BASKET/pull/179'],
            'limitations': ['Synthetic unit fixture; no source authentication'],
            'next_action': 'B00 reconciles existing work'}


class QcIntakeTests(unittest.TestCase):
    def test_intact_inventory_advances_to_semantic_review(self):
        x = sample()
        review = reconcile_inventory(x, source_reader, {'O1': [QUEUE], 'K1': [QUEUE]})
        self.assertEqual(review['outcome'], 'review')
        self.assertFalse(review['missing_item_ids'])
        # Reconciliation does not itself accept or archive the source.
        self.assertEqual(pending(index(x), [], [178])['ordered_intake'], [x])

    def test_archive_fails_closed_without_source_review(self):
        x = sample()
        for outcome in ('accepted', 'superseded'):
            with self.subTest(outcome=outcome), self.assertRaisesRegex(ValueError, 'source inventory'):
                pending(index(x), [receipt(x, outcome)], [178])

    def test_omitted_from_request_and_handoff_still_requires_source_disposition(self):
        x = sample()
        source = {'O1': [QUEUE], 'K1': [QUEUE], 'R1': [QUEUE]}
        review = reconcile_inventory(x, source_reader, source)
        self.assertEqual(review['outcome'], 'rework')
        self.assertEqual(review['missing_item_ids'], ['R1'])
        self.assertEqual(review['missing_handoff_ids'], ['R1'])

    def test_unanchored_handoff_and_duplicate_ids_need_rework(self):
        x = sample()
        self.assertEqual(reconcile_inventory(x, source_reader, {'O1': [QUEUE]})[
            'unanchored_item_ids'], ['K1'])
        data = b'O1: obligation\nK1: knowledge\nK1: duplicate\n'
        next(a for a in x['artifacts'] if a['role'] == 'handoff')['sha256'] = hashlib.sha256(data).hexdigest()
        x['request_id'] = request_id(x)
        read_bytes = lambda path, revision: data if path.endswith('handoff.md') else b'example'
        review = reconcile_inventory(x, read_bytes, {'O1': [QUEUE], 'K1': [QUEUE]})
        self.assertEqual(review['outcome'], 'rework')
        self.assertEqual(review['duplicate_handoff_ids'], ['K1'])

    def test_reconciliation_checks_pinned_bytes_and_source_references(self):
        x = sample()
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            reconcile_inventory(x, lambda path, revision: b'wrong', {'O1': [QUEUE]})
        for source in ({}, {'O1': []}, {'O1': ['invented']}):
            with self.subTest(source=source), self.assertRaises(ValueError):
                reconcile_inventory(x, source_reader, source)

    def test_real_handoff_intact_and_k5_omission_pair(self):
        # Pin real handoff text; primary bytes are synthetic to isolate inventory.
        here = Path(__file__).parent
        handoff = (here / 'QC_HANDOFF.md').read_bytes()
        expected = ['O1', 'O2', 'O3', 'O4', 'O5', 'K1', 'K2', 'K3', 'K4', 'K5',
                    'R1', 'R2', 'R3', 'R4']
        request = copy.deepcopy(json.loads((here / 'QC_QUEUE.json').read_text())['requests'][0])
        request['item_ids'] = expected[:]
        for artifact in request['artifacts']:
            data = handoff if artifact['role'] == 'handoff' else b'example'
            artifact['sha256'] = hashlib.sha256(data).hexdigest()
        request['request_id'] = request_id(request)
        source = {item: [QUEUE] for item in expected}
        read_bytes = lambda path, revision: handoff if path.endswith('QC_HANDOFF.md') else b'example'
        intact = reconcile_inventory(request, read_bytes, source)
        self.assertEqual(intact['outcome'], 'review')
        self.assertEqual(intact['missing_item_ids'], [])
        request['item_ids'].remove('K5')
        request['request_id'] = request_id(request)
        result = pending(index(request), [receipt(request)], [178], read_bytes=read_bytes,
                         source_items={request['request_id']: source})
        self.assertEqual(result['archived_request_ids'], [])
        review = result['inventory_reviews'][request['request_id']]
        self.assertEqual(review['outcome'], 'rework')
        self.assertEqual(review['missing_item_ids'], ['K5'])
        self.assertEqual(review['missing_handoff_ids'], [])
        self.assertEqual(review['unanchored_item_ids'], [])

    def test_original_ten_item_intact_and_nine_item_omission_pair(self):
        expected = ['O1', 'O2', 'O3', 'O4', 'O5', 'K1', 'K2', 'K3', 'K4', 'K5']
        handoff = ('\n'.join(item + ': bounded original inventory' for item in expected) + '\n').encode()
        request = sample()
        request['item_ids'] = expected[:]
        next(a for a in request['artifacts'] if a['role'] == 'handoff')['sha256'] = hashlib.sha256(handoff).hexdigest()
        request['request_id'] = request_id(request)
        source = {item: [QUEUE] for item in expected}
        reader = lambda path, revision: handoff if path.endswith('handoff.md') else b'example'
        self.assertEqual(reconcile_inventory(request, reader, source)['outcome'], 'review')
        request['item_ids'].remove('K5'); request['request_id'] = request_id(request)
        result = pending(index(request), [receipt(request)], [178], read_bytes=reader,
                         source_items={request['request_id']: source})
        self.assertEqual(result['archived_request_ids'], [])
        self.assertEqual(result['inventory_reviews'][request['request_id']]['missing_item_ids'], ['K5'])

    def test_replay_no_duplicate(self):
        request = sample(); first = enqueue(index(), request)
        self.assertEqual(enqueue(first, request), first)
        self.assertEqual(len(first['requests']), 1)

    def test_set_order_does_not_duplicate_intake(self):
        a = sample(); b = copy.deepcopy(a)
        b['artifacts'].reverse(); b['item_ids'].reverse()
        b['request_id'] = request_id(b)
        self.assertEqual(a['request_id'], b['request_id'])
        self.assertEqual(enqueue(index(a), b), index(a))

    def test_issue_url_must_match_number(self):
        x = sample(); x['task']['issue']['url'] = QUEUE; x['request_id'] = request_id(x)
        with self.assertRaisesRegex(ValueError, 'issue URL'): validate_request(x)

    def test_changed_input_is_new_review(self):
        a = sample(); b = copy.deepcopy(a); b['artifacts'][0]['revision'] = 'b' * 40
        b['request_id'] = request_id(b)
        self.assertNotEqual(a['request_id'], b['request_id'])
        result = pending(index(a, b), [receipt(a)], [178], **archive_inputs(a))
        self.assertEqual(result['ordered_intake'], [b])

    def test_primary_and_handoff_required(self):
        for role in ('primary', 'handoff'):
            x = sample(); x['artifacts'] = [a for a in x['artifacts'] if a['role'] != role]
            x['request_id'] = request_id(x)
            with self.assertRaises(ValueError): validate_request(x)

    def test_owner_paths_and_traversal_rejected(self):
        for path in ('../secret', '/etc/passwd', '.github/workflows/qc.yml',
                     'orchestration//file', 'orchestration/../file'):
            x = sample(); x['artifacts'][0]['path'] = path; x['request_id'] = request_id(x)
            with self.subTest(path=path), self.assertRaises(ValueError): validate_request(x)
        x = sample(); x['task']['write_paths'] = ['.github/workflows/**']; x['request_id'] = request_id(x)
        with self.assertRaisesRegex(ValueError, 'another spark'): validate_request(x)

    def test_wrong_worker_and_unpinned_source_rejected(self):
        for field, value in [('task_id', 'B02-178'), ('schema', 'invented@1')]:
            x = sample(); x['task'][field] = value; x['request_id'] = request_id(x)
            with self.assertRaises(ValueError): validate_request(x)
        x = sample(); x['artifacts'][0]['revision'] = 'main'; x['request_id'] = request_id(x)
        with self.assertRaises(ValueError): validate_request(x)

    def test_source_readback_and_tamper(self):
        x = sample()
        self.assertTrue(verify_artifacts(x, source_reader))
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            verify_artifacts(x, lambda path, revision: b'changed')
        x['source_pr'] = 170
        with self.assertRaisesRegex(ValueError, 'digest mismatch'): validate_request(x)

    def test_priority_is_canonical_not_arrival(self):
        a, b, c = sample(178), sample(103), sample(106)
        result = pending(index(a, b, c), [], [103, 178])
        self.assertEqual(result['ordered_intake'], [b, a])
        self.assertEqual(result['needs_priority'], [c])

    def test_archive_does_not_close_implementation(self):
        x = sample(); r = receipt(x)
        self.assertEqual(pending(index(x), [r], [178], **archive_inputs(x))['ordered_intake'], [])
        self.assertEqual(x['task']['state'], 'review')
        for state in ('rework', 'blocked'):
            self.assertEqual(pending(index(x), [receipt(x, state)], [178])['ordered_intake'], [x])

    def test_receipt_requires_full_inventory_and_revision(self):
        x = sample(); r = receipt(x); del r['item_dispositions']['K1']
        with self.assertRaises(ValueError): validate_receipt(r, x)
        r = receipt(x); r['request_id'] = '0' * 64
        with self.assertRaises(ValueError): validate_receipt(r, x)
        r = receipt(x); r['evidence_urls'] = []
        with self.assertRaises(ValueError): validate_receipt(r, x)

    def test_duplicate_index_and_conflicting_receipts_fail(self):
        x = sample()
        with self.assertRaises(ValueError): validate_index(index(x, x))
        with self.assertRaises(ValueError): pending(index(x), [receipt(x), receipt(x, 'blocked')], [178], **archive_inputs(x))
        with self.assertRaises(ValueError): pending(index(x), [], [178, 178])


if __name__ == '__main__': unittest.main()
