import copy
import hashlib
import json
from pathlib import Path
import unittest
from orchestration.conversation_closeout.versions.qc_intake import (
    QUEUE, digest, enqueue, pending, request_id, validate_request,
    validate_index, validate_receipt, verify_artifacts)


def sample(issue=178):
    task = {'schema': 'basket.worker_task@1', 'task_id': f'B00-{issue}',
            'spark_id': 'B00', 'issue': {'number': issue, 'url': f'https://github.com/whiterosecoffee/_BASKET/issues/{issue}'},
            'branch': {'name': f'work/{issue}-qc', 'base': 'main'},
            'objective': 'Preserve and review closeout evidence',
            'write_paths': ['orchestration/conversation_closeout/versions/**'],
            'acceptance': [{'id': 'A1', 'criterion': 'Source and obligations preserved', 'evidence_class': 'source'}],
            'dependencies': [], 'claimed_at': None, 'state': 'review'}
    artifacts = [{'path': 'orchestration/conversation_closeout/versions/' + path,
                  'revision': 'a' * 40, 'sha256': hashlib.sha256(b'example').hexdigest(), 'role': role}
                 for path, role in [('primary.md', 'primary'), ('handoff.md', 'handoff')]]
    value = {'task': task, 'source_pr': 179, 'artifacts': artifacts, 'item_ids': ['O1', 'K1'],
             'review_kind': 'closeout_semantic'}
    value['request_id'] = request_id(value)
    return value


def index(*requests):
    return {'schema': 'basket.closeout_qc_index@1', 'canonical_queue': QUEUE, 'requests': list(requests)}


def receipt(request, outcome='accepted'):
    return {'request_id': request['request_id'], 'reviewer': 'independent test fixture',
            'outcome': outcome, 'item_dispositions': {key: {'state': 'transfer',
                'reason': 'Reviewed; implementation remains with existing owner',
                'destination': QUEUE} for key in request['item_ids']},
            'evidence_urls': ['https://github.com/whiterosecoffee/_BASKET/pull/179'],
            'limitations': ['Synthetic unit fixture; no source authentication'],
            'next_action': 'B00 reconciles existing work'}


class QcIntakeTests(unittest.TestCase):
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
        result = pending(index(a, b), [receipt(a)], [178])
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
        self.assertTrue(verify_artifacts(x, lambda path, revision: b'example'))
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
        self.assertEqual(pending(index(x), [r], [178])['ordered_intake'], [])
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
        with self.assertRaises(ValueError): pending(index(x), [receipt(x), receipt(x, 'blocked')], [178])
        with self.assertRaises(ValueError): pending(index(x), [], [178, 178])


if __name__ == '__main__': unittest.main()
